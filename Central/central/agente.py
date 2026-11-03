"""Uma sessão do Claude Code sem interface, conversando em stream-json.

Protocolo confirmado na versão 2.1.316 (2026-11-03):
- entrada: `{"type":"user","message":{"role":"user","content":"..."}}`, uma por linha; o processo
  segue vivo entre turnos e cada turno termina com um evento `{"type":"result"}`;
- `--permission-prompt-tool stdio` faz o pedido de permissão chegar como
  `{"type":"control_request","request":{"subtype":"can_use_tool",...}}`; a resposta é um
  `control_response` com `{"behavior":"allow","updatedInput":...}` ou `{"behavior":"deny","message":...}`;
- `--disallowedTools "Bash(git commit:*)"` nega sem perguntar;
- `AskUserQuestion` não existe neste modo: o agente pergunta em texto e encerra o turno.

`--permission-mode auto` (confirmado na 2.1.277, 2026-11-03): o classificador libera o rotineiro
sem perguntar, então comando fora da lista de `allow` não vira mais um cartão de permissão; o que
ele barra chega pelo `can_use_tool` como antes. As `PROIBIDAS` continuam negadas — regra de deny
vale acima do modo.
"""
from __future__ import annotations

import json
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Callable

from . import config

# O commit é da validação, e o push é sempre manual pelo VS Code (ADR-012).
PROIBIDAS = [
    "Bash(git commit:*)", "Bash(git push:*)", "Bash(git rebase:*)", "Bash(git merge:*)",
    "Bash(git reset:*)", "Bash(git worktree:*)", "Bash(git stash:*)",
    "PowerShell(git commit:*)", "PowerShell(git push:*)",
    "EnterWorktree", "ExitWorktree", "CronCreate", "RemoteTrigger", "ScheduleWakeup",
]


class SessaoAgente:
    """Processo `claude -p` de uma execução. Eventos chegam por `ao_evento`, numa thread."""

    def __init__(self, cwd: Path, agente: str, contrato: Path, nome: str,
                 ao_evento: Callable[[dict], None], retomar: str | None = None, exe: str | None = None):
        self.cwd = Path(cwd)
        self.agente = agente
        self.contrato = contrato
        self.nome = nome
        self.ao_evento = ao_evento
        self.retomar = retomar
        self.exe = exe or config.claude_exe()
        self.proc: subprocess.Popen | None = None
        self._escrita = threading.Lock()
        self._stderr: list[str] = []

    def argumentos(self) -> list[str]:
        args = [self.exe, "-p", "--verbose",
                "--input-format", "stream-json", "--output-format", "stream-json",
                "--permission-prompt-tool", "stdio", "--permission-mode", "auto",
                "--append-system-prompt-file", str(self.contrato), "-n", self.nome]
        if self.agente:
            args += ["--agent", self.agente]
        if self.retomar:
            args += ["--resume", self.retomar]
        # Variádico: fica por último para não engolir outras opções.
        return args + ["--disallowedTools", *PROIBIDAS]

    def iniciar(self) -> None:
        self.proc = subprocess.Popen(
            self.argumentos(), cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=config.ambiente(), creationflags=config.SEM_JANELA)
        threading.Thread(target=self._ler, daemon=True, name=f"agente-{self.nome}").start()
        threading.Thread(target=self._ler_erro, daemon=True).start()
        self._enviar({"type": "control_request", "request_id": f"init-{uuid.uuid4().hex[:8]}",
                      "request": {"subtype": "initialize"}})

    @property
    def vivo(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def _enviar(self, obj: dict) -> None:
        if not self.vivo:
            raise RuntimeError("o processo do agente não está rodando")
        with self._escrita:
            self.proc.stdin.write((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))
            self.proc.stdin.flush()

    def enviar(self, texto: str) -> None:
        self._enviar({"type": "user", "message": {"role": "user", "content": texto}})

    def responder_permissao(self, request_id: str, permitir: bool, entrada: dict | None = None,
                            mensagem: str = "") -> None:
        resposta = ({"behavior": "allow", "updatedInput": entrada or {}} if permitir
                    else {"behavior": "deny", "message": mensagem or "Negado pelo responsável na Central."})
        self._enviar({"type": "control_response",
                      "response": {"subtype": "success", "request_id": request_id, "response": resposta}})

    def interromper(self) -> None:
        self._enviar({"type": "control_request", "request_id": f"int-{uuid.uuid4().hex[:8]}",
                      "request": {"subtype": "interrupt"}})

    def encerrar(self, espera: float = 10) -> None:
        if self.proc is None:
            return
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
            self.proc.wait(timeout=espera)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.kill()

    def _ler(self) -> None:
        assert self.proc and self.proc.stdout
        for bruta in self.proc.stdout:
            try:
                ev = json.loads(bruta.decode("utf-8", "replace"))
            except ValueError:
                continue
            try:
                self.ao_evento(ev)
            except Exception as erro:  # um evento ruim não derruba a leitura
                self._stderr.append(f"erro ao tratar evento: {erro}")
        codigo = self.proc.wait()
        self.ao_evento({"type": "_fim", "codigo": codigo, "stderr": self._stderr[-15:]})

    def _ler_erro(self) -> None:
        assert self.proc and self.proc.stderr
        for linha in self.proc.stderr:
            self._stderr.append(linha.decode("utf-8", "replace").rstrip())
            del self._stderr[:-50]
