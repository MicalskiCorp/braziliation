"""A Central acha git e claude mesmo quando o PATH do Windows não os tem (tarefa agendada)."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

GIT_PADRAO = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "cmd" / "git.exe"


@unittest.skipUnless(sys.platform == "win32" and GIT_PADRAO.exists(), "só no Windows com o Git for Windows padrão")
class PathTest(unittest.TestCase):
    def test_acha_git_sem_ele_no_path(self):
        sistema = os.environ.get("SystemRoot", r"C:\WINDOWS")
        env = {k: v for k, v in os.environ.items() if k.upper() not in ("PATH", "CLAUDE_CODE_GIT_BASH_PATH")}
        env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), sistema, str(Path(sistema) / "System32")])
        codigo = ("import shutil, subprocess; from central import config; "
                  "print(shutil.which('git')); print(subprocess.run(['git', '--version'], capture_output=True).returncode)")
        r = subprocess.run([sys.executable, "-c", codigo], cwd=Path(__file__).resolve().parents[1], env=env,
                           capture_output=True, text=True)
        linhas = r.stdout.strip().splitlines()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(linhas[0].lower().endswith("git.exe"), linhas)
        self.assertEqual(linhas[1], "0")


class AmbienteTest(unittest.TestCase):
    def test_nao_herda_o_repositorio_de_quem_chamou(self):
        # Dentro de um hook o git exporta GIT_INDEX_FILE=.git/index; herdado, ele quebrava o
        # `git worktree add` dos testes rodados pelo pre-commit (2026-11-03).
        from central import config
        antes = {k: os.environ.get(k) for k in ("GIT_INDEX_FILE", "GIT_DIR")}
        os.environ["GIT_INDEX_FILE"], os.environ["GIT_DIR"] = ".git/index", ".git"
        try:
            env = config.ambiente({"X": "1"})
        finally:
            for k, v in antes.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.assertNotIn("GIT_INDEX_FILE", env)
        self.assertNotIn("GIT_DIR", env)
        self.assertEqual(env["X"], "1")
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")


if __name__ == "__main__":
    unittest.main()
