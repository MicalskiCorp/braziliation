"""Testes do parser único dos TODOs (ADR-012). Rodam com a biblioteca padrão:

    py -m unittest discover -s .claude/skills/gerir-todo/tests
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import todo_md  # noqa: E402

CRIATIVO = """# TODO

## Pendências

### Lendas

| Item | Arquivo | Prioridade | Status |
|------|---------|-----------|--------|
| Ficha: Bruxas | [`c.md`](c.md) | Alta | ❌ Não iniciado |
| Ficha: Dragão | [`c.md`](c.md) | Média | ⏸ Bloqueado |

## Handoffs de Pesquisa

| Item | Arquivo | Prioridade | Status |
|------|---------|-----------|--------|
| *(nenhum pendente)* | | | |

---

## Concluído

| Item | Data |
|------|------|
| Bootstrap | 2026-04-25 |
"""

DEV = """# TODO

## Gameplay

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Stagger | `@GameplayEngineer` | Média | ❌ |
| Inventário | `@SystemsDeveloper` + `@GameplayEngineer` | Alta | ⏸ depende |
"""


def doc(texto, nome="Design/Criativo/TODO.md"):
    return todo_md.analisar(texto, todo_md.ROOT / nome)


class LeituraTest(unittest.TestCase):
    def test_itens_por_secao_com_campos_canonicos(self):
        d = doc(CRIATIVO)
        abertos = d.itens(so_abertos=True)
        self.assertEqual([i.titulo for i in abertos], ["Ficha: Bruxas", "Ficha: Dragão"])
        self.assertEqual(abertos[0].secao, "Lendas")
        self.assertEqual(abertos[0].prioridade, "Alta")
        self.assertEqual(abertos[1].status, "⏸")

    def test_placeholder_e_concluido_nao_sao_abertos(self):
        d = doc(CRIATIVO)
        self.assertEqual(len(d.itens()), 4)
        self.assertEqual(len(d.itens(so_abertos=True)), 2)

    def test_id_estavel_entre_leituras(self):
        a = [i.id for i in doc(CRIATIVO).itens()]
        b = [i.id for i in doc(CRIATIVO).itens()]
        self.assertEqual(a, b)

    def test_id_igual_numa_copia_fora_da_raiz(self):
        """A Central lê o mesmo TODO no worktree de uma execução: o id não pode mudar."""
        copia = todo_md.analisar(CRIATIVO, Path("C:/qualquer/wt/123/Design/Criativo/TODO.md"))
        self.assertEqual([i.id for i in copia.itens()], [i.id for i in doc(CRIATIVO).itens()])
        self.assertEqual(copia.relativo, "Design/Criativo/TODO.md")

    def test_status_da_pesquisa_conta_como_aberto(self):
        texto = ("## Pendências de Checagem\n\n| Item | Observação | Prioridade | Status |\n|---|---|---|---|\n"
                 "| A | x | Baixa | 🟡 Confirmação fraca |\n| B | y | Média | 🎙️ Relato oral |\n")
        d = doc(texto, "Design/Pesquisa/TODO.md")
        self.assertEqual([i.status for i in d.itens(so_abertos=True)], ["🟡", "🎙"])

    def test_responsavel_lido_da_coluna(self):
        d = doc(DEV, "Desenvolvimento/Docs/TODO.md")
        self.assertEqual(d.itens()[0].responsavel, "@GameplayEngineer")


class ValidacaoTest(unittest.TestCase):
    def test_arquivo_integro(self):
        self.assertEqual(todo_md.validar(doc(CRIATIVO)), [])

    def test_citacao_no_meio_da_tabela(self):
        quebrado = CRIATIVO.replace("|------|---------|-----------|--------|\n| Ficha: Bruxas",
                                    "|------|---------|-----------|--------|\n> nota\n\n| Ficha: Bruxas", 1)
        problemas = todo_md.validar(doc(quebrado))
        self.assertTrue(any("separadora" in p for p in problemas), problemas)

    def test_concluido_fora_do_lugar(self):
        texto = DEV.replace("| Média | ❌ |", "| Média | ✅ Concluído |")
        problemas = todo_md.validar(doc(texto, "Desenvolvimento/Docs/TODO.md"))
        self.assertTrue(any("a linha sai" in p for p in problemas), problemas)

    def test_sem_status_e_cabecalho_desconhecido(self):
        texto = "## X\n\n| Item | Coisa | Status |\n|---|---|---|\n| A | b | pronto |\n"
        problemas = todo_md.validar(doc(texto))
        self.assertTrue(any("desconhecido" in p for p in problemas))
        self.assertTrue(any("sem status" in p for p in problemas))

    def test_os_tres_todos_do_repositorio_estao_integros(self):
        for camada in todo_md.CAMADAS:
            d = todo_md.ler_camada(camada)
            self.assertEqual(todo_md.validar(d), [], d.relativo)


class EscritaTest(unittest.TestCase):
    def test_mudar_status_e_prioridade(self):
        d = doc(CRIATIVO)
        alvo = d.itens()[0]
        novo = doc(todo_md.mudar_status(d, alvo.id, "🔨 Em andamento"))
        self.assertEqual(novo.item(alvo.id).status, "🔨")
        novo2 = doc(todo_md.mudar_prioridade(novo, alvo.id, "Baixa"))
        self.assertEqual(novo2.item(alvo.id).prioridade, "Baixa")
        with self.assertRaises(ValueError):
            todo_md.mudar_status(d, alvo.id, "feito")

    def test_adicionar_tira_placeholder(self):
        d = doc(CRIATIVO)
        texto = todo_md.adicionar(d, "Handoffs de Pesquisa", {
            "titulo": "Processar: Teatro", "referencia": "h.md", "prioridade": "Alta", "status": "❌ Não iniciado"})
        novo = doc(texto)
        itens = [i for i in novo.itens() if i.secao == "Handoffs de Pesquisa"]
        self.assertEqual([i.titulo for i in itens], ["Processar: Teatro"])
        self.assertEqual(todo_md.validar(novo), [])

    def test_concluir_no_criativo_move_com_data(self):
        d = doc(CRIATIVO)
        alvo = d.itens()[0]
        novo = doc(todo_md.concluir(d, alvo.id, "2026-11-03"))
        concl = [i for i in novo.itens() if i.secao == "Concluído"]
        self.assertEqual(concl[-1].titulo, "Ficha: Bruxas")
        self.assertIn("2026-11-03", concl[-1].campos["data"])
        self.assertEqual(todo_md.validar(novo), [])

    def test_concluir_no_dev_tira_a_linha(self):
        d = doc(DEV, "Desenvolvimento/Docs/TODO.md")
        alvo = d.itens()[0]
        novo = doc(todo_md.concluir(d, alvo.id, "2026-11-03"), "Desenvolvimento/Docs/TODO.md")
        self.assertEqual([i.titulo for i in novo.itens()], ["Inventário"])

    def test_gravar_recusa_arquivo_que_mudou_e_mantem_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "TODO.md"
            caminho.write_bytes(DEV.replace("\n", "\r\n").encode("utf-8"))
            d = todo_md.ler(caminho)
            texto = todo_md.mudar_status(d, d.itens()[0].id, "🔨")
            with self.assertRaises(todo_md.Conflito):
                todo_md.gravar(caminho, texto, "hash-velho")
            todo_md.gravar(caminho, texto, d.hash)
            self.assertIn(b"\r\n", caminho.read_bytes())
            self.assertEqual(todo_md.ler(caminho).itens()[0].status, "🔨")


if __name__ == "__main__":
    unittest.main()
