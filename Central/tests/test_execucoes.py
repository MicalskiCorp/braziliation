"""Ciclo das execuções num repositório git temporário, com o agente falso (ADR-012)."""
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from central import filas, gitops
from central.execucoes import Bloqueio, Gerenciador
from central.fontes import todo_md
from tests.apoio import BLOCO, PY, SessaoFalsa, apagar, esperar, git, pedir_permissao, repo_temporario

TODO = "Design/Criativo/TODO.md"


def fila(fid="cri-lendas", secao="Lendas", isolamento="worktree"):
    return filas.Fila(id=fid, camada="Criativo", nome=secao, fonte={"todo": "criativo", "secao": secao},
                      agente="game-creative", isolamento=isolamento)


def itens(raiz, secao="Lendas"):
    doc = todo_md.ler(raiz / TODO)
    return [{"id": i.id, "titulo": i.titulo} for i in doc.itens(so_abertos=True) if i.secao == secao]


def troca_no_todo(antes, depois):
    def passo(s):
        arq = s.cwd / TODO
        arq.write_text(arq.read_text(encoding="utf-8").replace(antes, depois), encoding="utf-8", newline="\n")
        s.texto("Feito." + BLOCO)
        s.fim()
    return passo


def junta_as_versoes(linha_final):
    """O agente falso troca o bloco de conflito inteiro pela linha combinada."""
    def passo(s):
        arq = s.cwd / TODO
        saida, dentro = [], False
        for l in arq.read_text(encoding="utf-8").splitlines():
            if l.startswith("<<<<<<<"):
                dentro = True
                continue
            if dentro and l.startswith(">>>>>>>"):
                dentro = False
                saida.append(linha_final)
                continue
            if not dentro:
                saida.append(l)
        arq.write_text("\n".join(saida) + "\n", encoding="utf-8", newline="\n")
        s.texto("Juntei as duas versões." + BLOCO)
        s.fim()
    return passo


class Base(unittest.TestCase):
    def setUp(self):
        self.raiz = repo_temporario()
        self.estado = Path(tempfile.mkdtemp(prefix="central-estado-"))
        SessaoFalsa.roteiro, SessaoFalsa.criadas = [], []
        self.ger = Gerenciador(raiz=self.raiz, estado=self.estado, fabrica=SessaoFalsa, max_paralelo=3, zelador=False)
        self.ger._checagens_para = lambda ex: {"eco": [PY, "-c", "print('ok')"]}

    def tearDown(self):
        for ex in self.ger.ativas():
            try:
                self.ger.descartar(ex.id)
            except Exception:
                pass
        apagar(self.raiz)
        apagar(self.estado)

    def criar(self, f, its, **kw):
        ex, avisos = self.ger.criar(f, its, "game-creative", "faça", confirmado=True, **kw)
        return ex

    def ate(self, ex, estado, limite=30):
        ok = esperar(lambda: self.ger.obter(ex.id).estado == estado, limite)
        self.assertTrue(ok, f"esperava {estado}, está {self.ger.obter(ex.id).estado}: {self.ger.obter(ex.id).mensagem}")


class WorktreeTest(Base):
    def test_ciclo_completo_ate_o_commit_no_main(self):
        SessaoFalsa.roteiro = [troca_no_todo("| Alta | ❌ Não iniciado |", "| Alta | 🔨 Em andamento |")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        self.assertTrue(Path(ex.cwd).is_relative_to(self.raiz / ".git" / "central" / "wt"))
        self.assertIn("❌ Não iniciado | \n", (self.raiz / TODO).read_text(encoding="utf-8").replace("❌ Não iniciado |\n", "❌ Não iniciado | \n"))
        arquivos = self.ger.diff(ex.id)
        self.assertEqual([a["caminho"] for a in arquivos], [TODO])
        self.assertIn("🔨 Em andamento", arquivos[0]["patch"])
        esperar(lambda: self.ger.obter(ex.id).checagens.get("eco", {}).get("estado") == "ok")
        r = self.ger.commitar(ex.id, "docs: lenda em andamento", [TODO])
        self.assertTrue(r.ok, r.texto)
        ex = self.ger.obter(ex.id)
        self.assertEqual(ex.estado, "commitada")
        self.assertTrue(ex.integrada)
        self.assertIn("🔨 Em andamento", (self.raiz / TODO).read_text(encoding="utf-8"))
        self.assertFalse(Path(ex.cwd).exists())
        self.assertNotIn(ex.branch, git(self.raiz, "branch").stdout)
        self.assertTrue(gitops.arvore_limpa(self.raiz))

    def test_paralelo_em_secoes_diferentes_se_junta_no_rebase(self):
        SessaoFalsa.roteiro = [troca_no_todo("| Ficha: Bruxas | [`c.md`](c.md) | Alta | ❌", "| Ficha: Bruxas | [`c.md`](c.md) | Alta | 🔨")]
        a = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(a, "aguardando-validacao")
        SessaoFalsa.roteiro = [troca_no_todo("| Primeiras ideias | [`p.md`](p.md) | Baixa | ❌", "| Primeiras ideias | [`p.md`](p.md) | Baixa | 📋")]
        b_fila = fila("cri-ideias", "Ideias")
        _, avisos = self.ger.avaliar(b_fila, itens(self.raiz, "Ideias"))
        self.assertTrue(any("também mexe" in av for av in avisos), avisos)
        b = self.criar(b_fila, itens(self.raiz, "Ideias"))
        self.ate(b, "aguardando-validacao")
        self.assertTrue(self.ger.commitar(a.id, "docs: a", [TODO]).ok)
        r = self.ger.commitar(b.id, "docs: b", [TODO])
        self.assertTrue(r.ok, r.texto)
        texto = (self.raiz / TODO).read_text(encoding="utf-8")
        self.assertIn("| Alta | 🔨", texto)
        self.assertIn("| Baixa | 📋", texto)
        self.assertEqual(self.ger.obter(b.id).estado, "commitada")

    def _duas_execucoes_na_mesma_linha(self):
        SessaoFalsa.roteiro = [troca_no_todo("| Ficha: Dragão | [`c.md`](c.md) | Média |", "| Ficha: Dragão | [`c.md`](c.md) | Alta |")]
        a = self.criar(fila(), itens(self.raiz)[1:2])
        self.ate(a, "aguardando-validacao")
        SessaoFalsa.roteiro = [troca_no_todo("| Ficha: Dragão | [`c.md`](c.md) | Média |", "| Ficha: Dragão | [`c.md`](c.md) | Baixa |")]
        b = self.criar(fila("outra", "Lendas"), [{"id": "outro-id", "titulo": "outro"}])
        self.ate(b, "aguardando-validacao")
        self.assertTrue(self.ger.commitar(a.id, "docs: a", [TODO]).ok)
        return a, b

    def test_mesma_linha_em_duas_execucoes_vira_conflito(self):
        self.ger.resolver_conflitos = False
        a, b = self._duas_execucoes_na_mesma_linha()
        self.ger.commitar(b.id, "docs: b", [TODO])
        b = self.ger.obter(b.id)
        self.assertEqual(b.estado, "conflito")
        self.assertIn(TODO, b.mensagem)
        self.assertEqual(b.conflito, [TODO])
        self.assertIn("| Alta |", (self.raiz / TODO).read_text(encoding="utf-8"))

    def test_conflito_resolvido_pelo_agente_e_aprovado(self):
        a, b = self._duas_execucoes_na_mesma_linha()
        SessaoFalsa.roteiro = [junta_as_versoes("| Ficha: Dragão | [`c.md`](c.md) | Alta | ❌ Não iniciado — prioridade revista |")]
        self.ger.commitar(b.id, "docs: b", [TODO])
        self.ate(b, "aguardando-validacao")
        b = self.ger.obter(b.id)
        self.assertTrue(b.integrar_pendente)
        self.assertIn("deu conflito", SessaoFalsa.criadas[-1].recebidas[0])
        self.assertIn("prioridade revista", "".join(a["patch"] for a in self.ger.diff(b.id)))
        self.assertIn("| Alta |", (self.raiz / TODO).read_text(encoding="utf-8"), "nada entra no main antes da aprovação")
        self.assertNotIn("prioridade revista", (self.raiz / TODO).read_text(encoding="utf-8"))
        with self.assertRaises(Bloqueio):
            self.ger.commitar(b.id, "docs: de novo", [TODO])
        r = self.ger.integrar(b.id)
        self.assertTrue(r.ok, r.texto)
        texto = (self.raiz / TODO).read_text(encoding="utf-8")
        self.assertIn("prioridade revista", texto)
        self.assertNotIn("<<<<<<<", texto)
        self.assertEqual(self.ger.obter(b.id).estado, "commitada")
        self.assertTrue(gitops.arvore_limpa(self.raiz))

    def test_marcador_esquecido_volta_para_o_agente(self):
        a, b = self._duas_execucoes_na_mesma_linha()
        SessaoFalsa.roteiro = [lambda s: (s.texto("Pronto." + BLOCO), s.fim()),
                               junta_as_versoes("| Ficha: Dragão | [`c.md`](c.md) | Alta | ❌ Não iniciado |")]
        self.ger.commitar(b.id, "docs: b", [TODO])
        self.ate(b, "aguardando-validacao")
        recebidas = SessaoFalsa.criadas[-1].recebidas
        self.assertTrue(any("Ainda há marcadores" in m for m in recebidas), recebidas)
        self.assertNotIn("<<<<<<<", (Path(self.ger.obter(b.id).cwd) / TODO).read_text(encoding="utf-8"))

    def test_sobra_de_worktree_e_apagada(self):
        sobra = self.raiz / ".git" / "central" / "wt" / "sobra-antiga" / "obj"
        sobra.mkdir(parents=True)
        (sobra / "x.cs").write_text("// gerado", encoding="utf-8")
        SessaoFalsa.roteiro = [lambda s: (s.texto("?"), s.fim())]
        viva = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(viva, "aguardando-voce")
        self.assertEqual(self.ger.limpar_sobras(), ["sobra-antiga"])
        self.assertTrue(Path(self.ger.obter(viva.id).cwd).exists())

    def test_descartar_apaga_o_worktree(self):
        SessaoFalsa.roteiro = [troca_no_todo("❌ Não iniciado", "🔨")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        self.ger.descartar(ex.id)
        self.assertEqual(self.ger.obter(ex.id).estado, "descartada")
        self.assertFalse(Path(ex.cwd).exists())
        self.assertIn("❌ Não iniciado", (self.raiz / TODO).read_text(encoding="utf-8"))


class RegrasTest(Base):
    def test_mesmo_item_em_duas_execucoes_e_bloqueado(self):
        SessaoFalsa.roteiro = [lambda s: (s.texto("Qual das duas opções?"), s.fim())]
        it = itens(self.raiz)[:1]
        ex = self.criar(fila(), it)
        self.ate(ex, "aguardando-voce")
        with self.assertRaises(Bloqueio):
            self.ger.criar(fila(), it, "game-creative", "de novo", confirmado=True)

    def test_principal_exige_arvore_limpa_e_descarte_devolve_o_estado(self):
        (self.raiz / "LEIA.md").write_text("sujo\n", encoding="utf-8")
        with self.assertRaises(Bloqueio):
            self.criar(fila(isolamento="principal"), itens(self.raiz)[:1])
        git(self.raiz, "checkout", "--", "LEIA.md")

        def passo(s):
            (s.cwd / "novo.md").write_text("arquivo novo\n", encoding="utf-8")
            (s.cwd / "LEIA.md").write_text("mudado\n", encoding="utf-8")
            s.texto("ok" + BLOCO)
            s.fim()
        SessaoFalsa.roteiro = [passo]
        ex = self.criar(fila(isolamento="principal"), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        self.assertEqual(Path(ex.cwd), self.raiz)
        segunda = self.criar(fila("cri-ideias", "Ideias", "principal"), itens(self.raiz, "Ideias"))
        self.assertEqual(self.ger.obter(segunda.id).estado, "na-fila")
        self.ger.descartar(ex.id)
        self.assertFalse((self.raiz / "novo.md").exists())
        self.assertEqual((self.raiz / "LEIA.md").read_text(encoding="utf-8"), "projeto de teste\n")
        self.ate(segunda, "aguardando-validacao")

    def test_pergunta_e_resposta_pelo_chat(self):
        SessaoFalsa.roteiro = [lambda s: (s.texto("Prefere a versão A ou B?"), s.fim()),
                               troca_no_todo("❌ Não iniciado", "🔨 versão B")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-voce")
        self.ger.enviar(ex.id, "B")
        self.ate(ex, "aguardando-validacao")
        tipos = [e["tipo"] for e in self.ger.eventos(ex.id)]
        self.assertIn("voce", tipos)
        self.assertEqual(SessaoFalsa.criadas[-1].recebidas[-1], "B")

    def test_pedido_de_decisao_sem_alteracao_espera_a_resposta(self):
        # Caso real de 2026-11-03: o agente fechou o turno com o bloco de resultado só para pedir
        # decisão, sem mexer em arquivo — e a execução ia para a validação com a sessão fechada.
        pede = ('A, B ou C?\n```resultado\n{"itens": [{"titulo": "x", "situacao": "precisa-decisao", '
                '"resumo": "aguarda"}], "commit": "docs: x"}\n```')
        SessaoFalsa.roteiro = [lambda s: (s.texto(pede), s.fim()),
                               troca_no_todo("❌ Não iniciado", "🔨 versão B")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-voce")
        self.assertTrue(SessaoFalsa.criadas[-1].vivo)
        self.assertEqual(self.ger.obter(ex.id).resultado["itens"][0]["situacao"], "precisa-decisao")
        self.ger.enviar(ex.id, "B")
        self.ate(ex, "aguardando-validacao")

    def test_pedido_de_decisao_com_trabalho_feito_fica_no_chat(self):
        # Caso do print de 2026-11-03: o agente escreveu o dossiê do LoRA e pediu a escolha (1 a 4); a
        # execução ia para a validação e o chat perdia a caixa de resposta.
        pede = ('Escolha 1, 2, 3 ou 4.\n```resultado\n{"itens": [{"titulo": "x", "situacao": "precisa-decisao", '
                '"resumo": "dossiê escrito"}], "commit": "docs: dossie"}\n```')

        def dossie(s):
            arq = s.cwd / TODO
            arq.write_text(arq.read_text(encoding="utf-8").replace("❌ Não iniciado", "⏸ aguardando a escolha", 1),
                           encoding="utf-8", newline="\n")
            s.texto(pede)
            s.fim()

        SessaoFalsa.roteiro = [dossie, troca_no_todo("⏸ aguardando a escolha", "🔨 opção 1")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-voce")
        self.assertTrue(SessaoFalsa.criadas[-1].vivo)
        self.assertEqual(self.ger.obter(ex.id).checagens, {})
        self.ger.enviar(ex.id, "1")
        self.ate(ex, "aguardando-validacao")
        self.assertIn("🔨 opção 1", self.ger.diff(ex.id)[0]["patch"])

    def test_quem_pediu_decisao_pode_ir_para_a_validacao_com_o_que_ja_fez(self):
        pede = ('A ou B?\n```resultado\n{"itens": [{"titulo": "x", "situacao": "precisa-decisao", '
                '"resumo": "parcial"}], "commit": "docs: parcial"}\n```')
        SessaoFalsa.roteiro = [lambda s: (s.texto(pede), s.fim())]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-voce")
        self.ger.finalizar(ex.id)
        self.ate(ex, "aguardando-validacao")
        self.assertEqual(self.ger.obter(ex.id).resultado["commit"], "docs: parcial")

    def test_resposta_na_validacao_retoma_o_agente(self):
        SessaoFalsa.roteiro = [troca_no_todo("❌ Não iniciado", "🔨 primeira versão")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        # A validação fechou a sessão; a resposta abre outra, retomando a mesma conversa.
        SessaoFalsa.roteiro = [troca_no_todo("🔨 primeira versão", "🔨 segunda versão")]
        self.ger.enviar(ex.id, "troque para a segunda versão")
        self.ate(ex, "aguardando-validacao")
        self.assertIn("🔨 segunda versão", self.ger.diff(ex.id)[0]["patch"])
        self.assertEqual(SessaoFalsa.criadas[-1].retomar, "sessao-falsa")

    def test_limite_de_agentes_recusa_sem_registrar_a_mensagem(self):
        SessaoFalsa.roteiro = [troca_no_todo("❌ Não iniciado", "🔨 feito")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        antes = len(self.ger.eventos(ex.id))
        self.ger.max = 0
        with self.assertRaisesRegex(Bloqueio, "limite"):
            self.ger.enviar(ex.id, "mais uma coisa")
        self.assertEqual(self.ger.obter(ex.id).estado, "aguardando-validacao")
        self.assertEqual(len(self.ger.eventos(ex.id)), antes)

    def test_permissao_e_permitir_sempre(self):
        def passo(s):
            pedir_permissao(s, "p1", "py script.py --a")
            s.ao_permitir = lambda s2, ok: (pedir_permissao(s2, "p2", "py script.py --b"),)
        SessaoFalsa.roteiro = [passo]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-voce")
        self.assertEqual(len(self.ger.obter(ex.id).pendentes), 1)
        sessao = SessaoFalsa.criadas[-1]
        self.ger.permissao(ex.id, "p1", "sempre")
        self.assertTrue(esperar(lambda: len(sessao.respostas) == 2))
        self.assertEqual(sessao.respostas, [("p1", True), ("p2", True)])
        self.assertEqual(self.ger.obter(ex.id).pendentes, [])

    def test_edicao_manual_vai_para_a_validacao(self):
        f = fila()
        alvo = itens(self.raiz)[0]

        def aplicar(cwd):
            doc = todo_md.ler(cwd / TODO)
            todo_md.gravar(cwd / TODO, todo_md.mudar_status(doc, alvo["id"], "⏸ aguardando pesquisa"), doc.hash)
        ex = self.ger.edicao_manual(f, alvo, "Status → ⏸", aplicar)
        self.assertEqual(ex.estado, "aguardando-validacao")
        self.assertIn("❌ Não iniciado", (self.raiz / TODO).read_text(encoding="utf-8").split("Bruxas", 1)[1][:80])
        mesma = self.ger.edicao_manual(f, itens(self.raiz)[1], "Prioridade", lambda cwd: None)
        self.assertEqual(mesma.id, ex.id)
        self.assertTrue(self.ger.commitar(ex.id, ex.resultado["commit"], [TODO]).ok)
        self.assertIn("⏸ aguardando pesquisa", (self.raiz / TODO).read_text(encoding="utf-8"))

    def test_falha_ao_iniciar_e_tentar_de_novo(self):
        original = SessaoFalsa.iniciar

        def quebra(s):
            raise FileNotFoundError(2, "O sistema não pode encontrar o arquivo especificado", "git")
        SessaoFalsa.iniciar = quebra
        try:
            ex = self.criar(fila(), itens(self.raiz)[:1])
            self.ate(ex, "erro")
            self.assertIn("programa não encontrado: git", self.ger.obter(ex.id).mensagem)
        finally:
            SessaoFalsa.iniciar = original
        SessaoFalsa.roteiro = [troca_no_todo("❌ Não iniciado", "🔨")]
        self.ger.tentar_de_novo(ex.id)
        self.ate(ex, "aguardando-validacao")
        with self.assertRaises(Bloqueio):
            self.ger.tentar_de_novo(ex.id)

    def test_reinicio_da_central_interrompe_o_que_rodava(self):
        SessaoFalsa.roteiro = [lambda s: None]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "rodando")
        novo = Gerenciador(raiz=self.raiz, estado=self.estado, fabrica=SessaoFalsa, zelador=False)
        self.assertEqual(novo.obter(ex.id).estado, "interrompida")



class AcaoRepetidaTest(Base):
    """Segundo clique (ou outra aba) durante uma ação longa é recusado pelo servidor (2026-11-03)."""

    def pronta_para_commit(self):
        SessaoFalsa.roteiro = [troca_no_todo("| Alta | ❌ Não iniciado |", "| Alta | 🔨 Em andamento |")]
        ex = self.criar(fila(), itens(self.raiz)[:1])
        self.ate(ex, "aguardando-validacao")
        esperar(lambda: self.ger.obter(ex.id).checagens.get("eco", {}).get("estado") == "ok")
        return ex

    def test_commit_duplo_e_recusado_enquanto_o_pre_commit_roda(self):
        ex = self.pronta_para_commit()
        base = git(self.raiz, "rev-parse", "HEAD").stdout.strip()
        liberar, original = threading.Event(), gitops.commitar

        def commit_lento(*args, **kw):
            liberar.wait(20)
            return original(*args, **kw)

        gitops.commitar = commit_lento
        try:
            primeiro = threading.Thread(target=self.ger.commitar, args=(ex.id, "docs: lenda", [TODO]))
            primeiro.start()
            self.ate(ex, "commitando")
            with self.assertRaisesRegex(Bloqueio, "já está em andamento"):
                self.ger.commitar(ex.id, "docs: lenda", [TODO])
            with self.assertRaisesRegex(Bloqueio, "commitando"):
                self.ger.descartar(ex.id)
            with self.assertRaisesRegex(Bloqueio, "commitando"):
                self.ger.preparar_checagens(ex.id)
            liberar.set()
            primeiro.join(30)
        finally:
            gitops.commitar = original
            liberar.set()
        self.ate(ex, "commitada")
        novos = git(self.raiz, "rev-list", f"{base}..HEAD").stdout.split()
        self.assertEqual(len(novos), 1)

    def test_commit_recusado_pelo_pre_commit_volta_para_a_validacao(self):
        ex = self.pronta_para_commit()
        original = gitops.commitar
        gitops.commitar = lambda *a, **k: gitops.Saida(1, "testes falharam")
        try:
            r = self.ger.commitar(ex.id, "docs: lenda", [TODO])
        finally:
            gitops.commitar = original
        self.assertFalse(r.ok)
        self.assertEqual(self.ger.obter(ex.id).estado, "aguardando-validacao")
        self.assertIn("recusou", self.ger.obter(ex.id).mensagem)

    def test_checagem_que_ja_roda_nao_roda_de_novo(self):
        ex = self.pronta_para_commit()
        self.ger.obter(ex.id).checagens["eco"] = {"estado": "rodando", "saida": "", "quando": ""}
        with self.assertRaisesRegex(Bloqueio, "já estão rodando"):
            self.ger.preparar_checagens(ex.id)

    def test_descarte_duplo_e_recusado(self):
        ex = self.pronta_para_commit()
        liberar, original = threading.Event(), gitops.remover_worktree

        def remover_lento(*args, **kw):
            liberar.wait(20)
            return original(*args, **kw)

        gitops.remover_worktree = remover_lento
        try:
            primeiro = threading.Thread(target=self.ger.descartar, args=(ex.id,))
            primeiro.start()
            self.ate(ex, "descartando")
            with self.assertRaisesRegex(Bloqueio, "descartando"):
                self.ger.descartar(ex.id)
            liberar.set()
            primeiro.join(30)
        finally:
            gitops.remover_worktree = original
            liberar.set()
        self.ate(ex, "descartada")

    def test_reinicio_no_meio_do_commit_volta_para_a_validacao(self):
        ex = self.pronta_para_commit()
        with self.ger.trava:
            self.ger.obter(ex.id).estado = "commitando"
            self.ger._salvar(self.ger.obter(ex.id))
        novo = Gerenciador(raiz=self.raiz, estado=self.estado, fabrica=SessaoFalsa, zelador=False)
        self.assertEqual(novo.obter(ex.id).estado, "aguardando-validacao")
        self.assertIn("git log", novo.obter(ex.id).mensagem)


if __name__ == "__main__":
    unittest.main()
