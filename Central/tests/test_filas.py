"""O registro de filas cobre os TODOs reais, e os números batem com o parser único."""
import unittest

from central import filas
from central.fontes import todo_md


class RegistroTest(unittest.TestCase):
    def setUp(self):
        self.filas = filas.carregar()

    def test_toda_secao_com_tabela_tem_fila(self):
        self.assertEqual(filas.secoes_sem_fila(self.filas), [],
                         "seção nova num TODO: registre a fila em Central/filas.json")

    def test_toda_fila_de_todo_aponta_para_secao_que_existe(self):
        for f in self.filas:
            if "secao" in f.fonte:
                doc = todo_md.ler_camada(f.fonte["todo"])
                self.assertIn(f.fonte["secao"], doc.nomes_de_secao(), f.id)

    def test_agentes_do_registro_existem(self):
        agentes = {p.stem for p in (todo_md.ROOT / ".claude/agents").glob("*.md")}
        for f in self.filas:
            if f.agente and f.agente != "@responsavel":
                self.assertIn(f.agente, agentes, f.id)

    def test_numeros_iguais_ao_parser(self):
        for camada in todo_md.CAMADAS:
            doc = todo_md.ler_camada(camada)
            esperado = sum(1 for _ in doc.itens(so_abertos=True))
            nas_filas = sum(len(f.abertos) for f in self.filas if f.fonte.get("todo") == camada)
            self.assertEqual(nas_filas, esperado, camada)

    def test_ids_unicos(self):
        ids = [f.id for f in self.filas]
        self.assertEqual(len(ids), len(set(ids)))


class ResponsavelTest(unittest.TestCase):
    def test_mapeamento(self):
        self.assertEqual(filas.agente_do_responsavel("`@UnityDeveloper`"), "unity-developer")
        self.assertEqual(filas.agente_do_responsavel("`@SpriteArtist` + `@UnityDeveloper`"), "sprite-artist")
        self.assertEqual(filas.agente_do_responsavel("Usuário + `@TechLead`"), "tech-lead")
        self.assertEqual(filas.agente_do_responsavel("Usuário"), "tech-lead")


if __name__ == "__main__":
    unittest.main()
