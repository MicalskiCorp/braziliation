"""Contrato com o stream-json do Claude Code (gravado em 2026-11-03, versão 2.1.316)."""
import json
import unittest
from pathlib import Path
from unittest import mock

from central import config, conversa
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


    def test_compactacao_vira_nota(self):
        ev = {"type": "system", "subtype": "compact_boundary", "compact_metadata": {"trigger": "auto", "pre_tokens": 131400}}
        self.assertEqual(conversa.normalizar(ev), [{"tipo": "nota", "texto": "Contexto compactado (automática): "
                                                                             "131 mil tokens viraram um resumo."}])


class ArgumentosTest(unittest.TestCase):
    def setUp(self):
        # Sem isto o teste rodaria `claude --version` de verdade (ADR-015 lê a versão para ligar o mod).
        trava = mock.patch.object(config, "versao_claude", return_value=(2, 1, 277))
        trava.start()
        self.addCleanup(trava.stop)

    def sessao(self, economia=None):
        return SessaoAgente(Path("."), "historiador", Path("contrato.md"), "teste", lambda ev: None, exe="claude",
                            economia=economia)

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


class EconomiaTest(ArgumentosTest):
    """ADR-015: a janela vale em qualquer versão; o mod só a partir da 2.1.287."""

    def test_versao_sem_mods_roda_sem_o_mod_mas_com_a_janela(self):
        s = self.sessao({"janela": 150000, "execucao": "x1", "fila": "Unity"})
        self.assertFalse(s.mod_ativo)
        self.assertNotIn("--plugin-dir", s.argumentos())
        self.assertEqual(s.variaveis(), {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "150000"})

    def test_versao_com_mods_carrega_o_mod_antes_da_lista_variadica(self):
        with mock.patch.object(config, "versao_claude", return_value=(2, 1, 318)):
            s = self.sessao({"janela": 150000, "execucao": "x1", "fila": "Unity"})
        args = s.argumentos()
        self.assertTrue(s.mod_ativo)
        self.assertEqual(args[args.index("--plugin-dir") + 1], str(config.MOD_ECONOMIA))
        self.assertLess(args.index("--plugin-dir"), args.index("--disallowedTools"))
        self.assertEqual(args[args.index("--disallowedTools") + 1:], PROIBIDAS)
        self.assertEqual(s.variaveis(), {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "150000",
                                         "CENTRAL_EXECUCAO": "x1", "CENTRAL_FILA": "Unity"})

    def test_fila_sem_janela_fica_no_padrao_do_claude_code(self):
        self.assertEqual(self.sessao({"janela": 0}).variaveis(), {})
        self.assertEqual(self.sessao().variaveis(), {})

    def test_central_economia_0_desliga_tudo(self):
        with mock.patch.object(config, "ECONOMIA", False), \
                mock.patch.object(config, "versao_claude", return_value=(2, 1, 318)):
            s = self.sessao({"janela": 150000, "execucao": "x1"})
        self.assertFalse(s.mod_ativo)
        with mock.patch.object(config, "ECONOMIA", False):
            self.assertEqual(s.variaveis(), {})

    def test_o_mod_existe_onde_a_central_aponta(self):
        self.assertTrue((config.MOD_ECONOMIA / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((config.MOD_ECONOMIA / "hooks" / "hooks.json").is_file())


if __name__ == "__main__":
    unittest.main()
