"""Medição de tokens a partir do stream-json (ADR-015)."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from central import tokens
from tests.apoio import apagar


def msg(mid, entrada=0, lido=0, escrito=0, blocos=None, pai=None):
    ev = {"type": "assistant", "message": {"id": mid, "content": blocos or [{"type": "text", "text": "x"}],
                                           "usage": {"input_tokens": entrada, "cache_read_input_tokens": lido,
                                                     "cache_creation_input_tokens": escrito, "output_tokens": 1}}}
    if pai:
        ev["parent_tool_use_id"] = pai
    return json.dumps(ev)


def resultado(lido, escrito, saida, custo, pensamento=0):
    return json.dumps({"type": "result", "subtype": "success", "total_cost_usd": custo,
                       "usage": {"input_tokens": 0, "cache_read_input_tokens": lido,
                                 "cache_creation_input_tokens": escrito, "output_tokens": saida,
                                 "output_tokens_details": {"thinking_tokens": pensamento}}})


INIT = json.dumps({"type": "system", "subtype": "init", "claude_code_version": "2.1.318", "model": "claude-sonnet-5",
                   "plugins": [{"name": "agents-md"}, {"name": tokens.MOD}]})


class AnaliseTest(unittest.TestCase):
    def test_requisicao_e_o_id_da_mensagem_nao_o_evento(self):
        # Cada bloco de uma resposta chega como um evento com o mesmo id e o mesmo usage.
        linhas = [INIT, msg("m1", 2, 0, 20000), msg("m1", 2, 0, 20000), msg("m2", 1, 20000, 500)]
        r = tokens.analisar(linhas)
        self.assertEqual(r["requisicoes"], 2)
        self.assertEqual(r["contexto_inicial"], 20002)
        self.assertEqual(r["contexto_max"], 20501)
        self.assertEqual(r["lidos"], 40503)
        self.assertTrue(r["mod_carregado"])
        self.assertEqual(r["versao"], "2.1.318")

    def test_subagente_fica_fora_da_curva_principal(self):
        r = tokens.analisar([msg("m1", 0, 0, 10000), msg("s1", 0, 0, 90000, pai="toolu_1")])
        self.assertEqual(r["requisicoes"], 1)
        self.assertEqual(r["contexto_max"], 10000)

    def test_turno_fechado_usa_o_usage_do_result(self):
        linhas = [msg("m1", 0, 0, 1000), msg("m2", 0, 1000, 10), resultado(1000, 1010, 300, 0.5, pensamento=120)]
        r = tokens.analisar(linhas)
        self.assertEqual(r["saida"], 300)
        self.assertEqual(r["pensamento"], 120)
        self.assertEqual(r["lidos"], 2010)

    def test_custo_e_acumulado_no_processo(self):
        # Somar os result contava o custo várias vezes (a análise de 2026-11-04 deu US$ 55,85 em vez de 39,94).
        r = tokens.analisar([resultado(1, 0, 0, 1.0), resultado(1, 0, 0, 2.5), resultado(1, 0, 0, 2.5)])
        self.assertEqual(r["custo_usd"], 2.5)

    def test_processo_que_recomeca_a_conta_soma_as_partes(self):
        r = tokens.analisar([resultado(1, 0, 0, 3.0), resultado(1, 0, 0, 0.4), resultado(1, 0, 0, 1.0)])
        self.assertEqual(r["custo_usd"], 4.0)

    def test_compactacao_e_contada(self):
        compacta = json.dumps({"type": "system", "subtype": "compact_boundary",
                               "compact_metadata": {"trigger": "auto", "pre_tokens": 131000}})
        r = tokens.analisar([msg("m1", 0, 0, 131000), compacta, msg("m2", 0, 0, 30000)])
        self.assertEqual(r["compactacoes"], [{"gatilho": "auto", "antes": 131000, "requisicao": 1}])

    def test_maior_resultado_e_o_mais_relido(self):
        # Um resultado grande no começo pesa mais que um maior perto do fim: é relido a cada requisição.
        uso = {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "unity list"}}
        uso2 = {"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": "Cena.unity"}}
        resultado_de = lambda tid, n: json.dumps({"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": tid, "content": "x" * n}]}})
        linhas = [msg("m1", blocos=[uso]), resultado_de("t1", 7000)]
        linhas += [msg(f"m{i}") for i in range(2, 12)]
        linhas += [msg("m12", blocos=[uso2]), resultado_de("t2", 14000), msg("m13")]
        r = tokens.analisar(linhas)
        self.assertEqual(r["maiores"][0]["resumo"], "unity list")
        self.assertEqual(r["maiores"][0]["tokens"], 2000)

    def test_linha_quebrada_nao_derruba(self):
        r = tokens.analisar(["{quebrada", "", "[]", msg("m1", 0, 0, 5)])
        self.assertEqual(r["requisicoes"], 1)


class ResumoTest(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())

    def tearDown(self):
        apagar(self.pasta)

    def test_sem_bruto_nao_ha_resumo(self):
        self.assertIsNone(tokens.resumo(self.pasta))

    def test_arquivo_que_cresce_e_relido(self):
        bruto = self.pasta / "bruto.jsonl"
        bruto.write_text(msg("m1", 0, 0, 100) + "\n", encoding="utf-8")
        self.assertEqual(tokens.resumo(self.pasta)["requisicoes"], 1)
        with bruto.open("a", encoding="utf-8") as f:
            f.write(msg("m2", 0, 100, 5) + "\n")
        self.assertEqual(tokens.resumo(self.pasta)["requisicoes"], 2)


class AgruparTest(unittest.TestCase):
    def test_separa_com_e_sem_janela(self):
        ex = lambda janela: SimpleNamespace(fila_nome="Unity", fila_id="dev-unity", economia={"janela": janela})
        r = lambda lidos: {"lidos": lidos, "requisicoes": 10, "contexto_max": 100, "custo_usd": 1.0, "compactacoes": []}
        g = tokens.agrupar([(ex(0), r(1000)), (ex(0), r(3000)), (ex(150000), r(500))])
        sem = next(x for x in g if not x["janela"])
        com = next(x for x in g if x["janela"])
        self.assertEqual((sem["n"], sem["lidos_medio"]), (2, 2000))
        self.assertEqual((com["n"], com["lidos_medio"], com["janela"]), (1, 500, 150000))

    def test_formato(self):
        self.assertEqual(tokens.fmt(25_290_524), "25,3 M")
        self.assertEqual(tokens.fmt(153_400), "153 mil")
        self.assertEqual(tokens.fmt(950), "950")


if __name__ == "__main__":
    unittest.main()
