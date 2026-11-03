"""Contrato com o stream-json do Claude Code (gravado em 2026-11-03, versão 2.1.316)."""
import json
import unittest
from pathlib import Path

from central import conversa
from central.agente import PROIBIDAS, SessaoAgente

FIXTURE = Path(__file__).parent / "fixtures" / "sessao.jsonl"


def eventos():
    return [json.loads(l) for l in FIXTURE.read_text(encoding="utf-8").splitlines() if l.strip()]


class NormalizarTest(unittest.TestCase):
    def test_sessao_gravada_vira_chat(self):
        entradas = [e for ev in eventos() for e in conversa.normalizar(ev)]
        tipos = [e["tipo"] for e in entradas]
        self.assertEqual(tipos, ["nota", "ferramenta", "permissao", "erro_ferramenta", "agente", "fim_turno"])
        permissao = entradas[2]
        self.assertEqual(permissao["request_id"], "b5f1")
        self.assertEqual(permissao["ferramenta"], "Bash")
        self.assertEqual(permissao["resumo"], "mkdir pastaspike")

    def test_bloco_de_resultado(self):
        texto = [e for ev in eventos() for e in conversa.normalizar(ev) if e["tipo"] == "agente"][0]["texto"]
        resultado = conversa.extrair_resultado(texto)
        self.assertEqual(resultado["itens"][0]["situacao"], "feito")
        self.assertEqual(resultado["commit"], "docs(criativo): ficha das bruxas")
        self.assertEqual(conversa.sem_bloco(texto), "Pronto.")

    def test_sem_bloco_e_bloco_invalido(self):
        self.assertIsNone(conversa.extrair_resultado("Qual opção você prefere?"))
        ruim = conversa.extrair_resultado("```resultado\n{nao é json}\n```")
        self.assertIn("erro", ruim)

    def test_contrato_formata(self):
        texto = conversa.CONTRATO.format(id="x1", fila="Lendas")
        self.assertIn("```resultado", texto)
        self.assertIn("Não faça commit nem push", texto)


class ArgumentosTest(unittest.TestCase):
    def test_commit_e_push_bloqueados_e_sem_pular_hooks(self):
        s = SessaoAgente(Path("."), "historiador", Path("contrato.md"), "teste", lambda ev: None, exe="claude")
        args = s.argumentos()
        self.assertIn("--permission-prompt-tool", args)
        self.assertEqual(args[args.index("--permission-mode") + 1], "auto")
        self.assertNotIn("--bare", args)
        self.assertNotIn("--dangerously-skip-permissions", args)
        self.assertNotIn("bypassPermissions", args)
        self.assertEqual(args[args.index("--disallowedTools") + 1:], PROIBIDAS)
        self.assertIn("Bash(git commit:*)", PROIBIDAS)
        self.assertIn("Bash(git push:*)", PROIBIDAS)
        self.assertEqual(args[args.index("--agent") + 1], "historiador")


if __name__ == "__main__":
    unittest.main()
