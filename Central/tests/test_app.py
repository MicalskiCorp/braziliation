"""Rotas e proteção da Central (ADR-012, invariante 8)."""
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from central import filas
from central.app import criar_app
from central.fontes import renderizar_md
from tests.apoio import BLOCO, PY, SessaoFalsa, apagar, esperar, repo_temporario

TOKEN = "token-de-teste"
TODO = "Design/Criativo/TODO.md"


class ProtecaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estado = Path(tempfile.mkdtemp())
        cls.app = criar_app(estado=cls.estado, hosts_extra=("testserver",), token=TOKEN, observar=False)
        cls.c = TestClient(cls.app)

    @classmethod
    def tearDownClass(cls):
        apagar(cls.estado)

    def test_host_estranho_e_recusado(self):
        self.assertEqual(self.c.get("/", headers={"host": "braziliation.evil.com"}).status_code, 403)

    def test_acao_sem_token_e_recusada(self):
        self.assertEqual(self.c.post("/conversa", data={"mensagem": "oi"}).status_code, 403)
        r = self.c.post("/conversa", data={"mensagem": "oi"}, headers={"x-central-token": "errado"})
        self.assertEqual(r.status_code, 403)

    def test_origem_de_outro_site_e_recusada(self):
        r = self.c.post("/conversa", data={"mensagem": "oi"},
                        headers={"x-central-token": TOKEN, "origin": "https://evil.com"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.c.get("/", headers={"sec-fetch-site": "cross-site"}).status_code, 403)

    def test_csp_sem_script_inline(self):
        csp = self.c.get("/").headers["content-security-policy"]
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("unsafe-inline", csp.split("script-src", 1)[1].split(";")[0])

    def test_todas_as_paginas_abrem(self):
        urls = ["/", "/execucoes", "/conversa", "/tokens", "/saude", "/doc?c=Design/Criativo/TODO.md", "/doc?c=Design"]
        urls += [f"/fila/{f['id']}" for f in filas.registro()]
        for url in urls:
            self.assertEqual(self.c.get(url).status_code, 200, url)

    def test_caminho_fora_do_projeto(self):
        self.assertEqual(self.c.get("/arquivo?c=../../Windows/win.ini").status_code, 403)
        self.assertIn("fora do projeto", self.c.get("/doc?c=../../").text)

    def test_markdown_nao_vira_html(self):
        html = renderizar_md("<script>alert(1)</script> [x](javascript:alert(1)) [y](Historia/a.md)", TODO)
        self.assertNotIn("<script>", html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn('href="/doc?c=Design/Criativo/Historia/a.md"', html)


class ExecutarPeloPainelTest(unittest.TestCase):
    def setUp(self):
        self.raiz = repo_temporario()
        self.estado = Path(tempfile.mkdtemp())
        SessaoFalsa.roteiro, SessaoFalsa.criadas = [], []
        self.app = criar_app(raiz=self.raiz, estado=self.estado, fabrica=SessaoFalsa, hosts_extra=("testserver",),
                             token=TOKEN, observar=False)
        self.ger = self.app.state.ger
        self.ger._checagens_para = lambda ex: {"eco": [PY, "-c", "print('ok')"]}
        self.c = TestClient(self.app)
        self.h = {"x-central-token": TOKEN}

    def tearDown(self):
        for ex in self.ger.ativas():
            try:
                self.ger.descartar(ex.id)
            except Exception:
                pass
        apagar(self.raiz)
        apagar(self.estado)

    def test_selecionar_executar_conversar_validar_commitar(self):
        f = filas.por_id(filas.carregar(self.raiz), "cri-lendas")
        alvo = f.abertos[0]

        def pergunta(s):
            s.texto("Qual nome para a ficha?")
            s.fim()

        def termina(s):
            arq = s.cwd / TODO
            arq.write_text(arq.read_text(encoding="utf-8").replace("| Alta | ❌ Não iniciado |", "| Alta | 🔨 Em andamento |"),
                           encoding="utf-8", newline="\n")
            s.texto("Feito." + BLOCO)
            s.fim()

        SessaoFalsa.roteiro = [pergunta, termina]
        r = self.c.post("/fila/cri-lendas/executar", data={"itens": [alvo["id"]]}, headers=self.h)
        self.assertTrue(r.json()["ok"], r.json())
        ex_id = r.json()["ir"].rsplit("/", 1)[1]
        self.assertTrue(esperar(lambda: self.ger.obter(ex_id).estado == "aguardando-voce"))
        self.assertIn("Qual nome para a ficha?", self.c.get(f"/execucao/{ex_id}").text)
        r = self.c.post(f"/execucao/{ex_id}/mensagem", data={"texto": "Bruxas da Ilha"}, headers=self.h)
        self.assertTrue(r.json()["ok"], r.json())
        self.assertTrue(esperar(lambda: self.ger.obter(ex_id).estado == "aguardando-validacao"))
        self.assertIn("🔨 Em andamento", self.c.get(f"/execucao/{ex_id}/validacao").text)
        sem_revisao = self.c.post(f"/execucao/{ex_id}/commit", data={"mensagem": "docs: x", "arquivos": [TODO]},
                                  headers=self.h)
        self.assertFalse(sem_revisao.json()["ok"])
        r = self.c.post(f"/execucao/{ex_id}/commit", data={"mensagem": "docs: lenda", "revisei": "1",
                                                           "arquivos": [TODO]}, headers=self.h)
        self.assertTrue(r.json()["ok"], r.json())
        self.assertEqual(self.ger.obter(ex_id).estado, "commitada")
        self.assertIn("🔨 Em andamento", (self.raiz / TODO).read_text(encoding="utf-8"))

    def test_item_ja_em_execucao_e_recusado(self):
        SessaoFalsa.roteiro = [lambda s: (s.texto("?"), s.fim())]
        f = filas.por_id(filas.carregar(self.raiz), "cri-lendas")
        ids = [f.abertos[0]["id"]]
        self.assertTrue(self.c.post("/fila/cri-lendas/executar", data={"itens": ids}, headers=self.h).json()["ok"])
        r = self.c.post("/fila/cri-lendas/executar", data={"itens": ids, "confirmado": "1"}, headers=self.h).json()
        self.assertFalse(r["ok"])
        self.assertIn("já está na execução", r["erro"])

    def test_edicao_rapida_vai_para_validacao_sem_tocar_a_arvore(self):
        f = filas.por_id(filas.carregar(self.raiz), "cri-lendas")
        alvo = f.abertos[1]
        r = self.c.post(f"/fila/cri-lendas/item/{alvo['id']}/prioridade", data={"valor": "Baixa"}, headers=self.h).json()
        self.assertTrue(r["ok"], r)
        self.assertIn("/validacao", r["ir"])
        self.assertIn("Ficha: Dragão | [`c.md`](c.md) | Média", (self.raiz / TODO).read_text(encoding="utf-8"))

    def test_estado_ao_vivo_por_consulta_curta(self):
        SessaoFalsa.roteiro = [lambda s: (s.texto("Qual nome?"), s.fim())]
        f = filas.por_id(filas.carregar(self.raiz), "cri-lendas")
        antes = self.c.get("/vivo").json()
        r = self.c.post("/fila/cri-lendas/executar", data={"itens": [f.abertos[0]["id"]]}, headers=self.h).json()
        ex_id = r["ir"].rsplit("/", 1)[1]
        self.assertTrue(esperar(lambda: self.ger.obter(ex_id).estado == "aguardando-voce"))
        depois = self.c.get("/vivo").json()
        self.assertNotEqual(antes["v"], depois["v"])
        self.assertEqual(depois["atencao"], 1)
        d = self.c.get(f"/execucao/{ex_id}/novidades?desde=0").json()
        self.assertEqual(d["estado"]["estado"], "aguardando-voce")
        self.assertTrue(any("Qual nome?" in e["html"] for e in d["entradas"]))
        fim = d["entradas"][-1]["i"] + 1
        self.assertEqual(self.c.get(f"/execucao/{ex_id}/novidades?desde={fim}").json()["entradas"], [])
        self.assertEqual(self.c.get("/execucao/nao-existe/novidades").status_code, 404)

    def test_validacao_durante_o_commit_nao_oferece_commit_nem_descarte(self):
        SessaoFalsa.roteiro = [lambda s: (s.texto("Feito." + BLOCO), s.fim())]
        f = filas.por_id(filas.carregar(self.raiz), "cri-lendas")
        r = self.c.post("/fila/cri-lendas/executar", data={"itens": [f.abertos[0]["id"]]}, headers=self.h).json()
        ex_id = r["ir"].rsplit("/", 1)[1]
        self.assertTrue(esperar(lambda: self.ger.obter(ex_id).estado == "aguardando-validacao"))
        ex = self.ger.obter(ex_id)
        ex.estado, ex.mensagem = "commitando", "Commit em andamento (o pre-commit roda os testes)…"
        html = self.c.get(f"/execucao/{ex_id}/validacao").text
        self.assertIn("atualiza sozinha", html)
        self.assertNotIn('id="form-commit"', html)
        self.assertNotIn("Descartar a execução", html)
        self.assertNotIn("Rodar as checagens de novo", html)
        r = self.c.post(f"/execucao/{ex_id}/commit", data={"mensagem": "docs: x", "revisei": "1", "arquivos": [TODO]},
                        headers=self.h).json()
        self.assertFalse(r["ok"])
        self.assertIn("já está em andamento", r["erro"])
        ex.estado = "aguardando-validacao"


if __name__ == "__main__":
    unittest.main()
