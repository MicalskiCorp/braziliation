"""
Copia o corpo (tudo depois do frontmatter) de cada agente Claude para o par Copilot.

Por que existe: cada agente vive em dois formatos com o mesmo prompt. Editar os dois à
mão dobrava o trabalho e o AgentParityTests pegava a divergência só depois. Agora edita-se
o arquivo Claude (.claude/agents/{nome}.md) e este script propaga o corpo.

Preserva do lado Copilot o que é de propósito diferente: frontmatter, BOM UTF-8 e CRLF.

Uso:  py .claude/skills/novo-agente/sync_bodies.py            # sincroniza
      py .claude/skills/novo-agente/sync_bodies.py --check    # só aponta divergências (exit 1)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PARES = {
    "agent-architect": "AgentArchitect",
    "game-architect": "GameArchitect",
    "game-creative": "GameCreative",
    "gameplay-engineer": "GameplayEngineer",
    "historiador": "Historiador",
    "qa-engineer": "QAEngineer",
    "sprite-artist": "SpriteArtist",
    "systems-developer": "SystemsDeveloper",
    "tech-lead": "TechLead",
    "test-engineer": "TestEngineer",
    "unity-developer": "UnityDeveloper",
}
BOM = "﻿"


def dividir(texto: str) -> tuple[str, str]:
    """Separa frontmatter (com os dois '---') do corpo, como o AgentParityTests."""
    partes = texto.split("---", 2)
    if len(partes) < 3:
        raise ValueError("frontmatter ausente")
    return "---" + partes[1] + "---", partes[2]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    so_checar = "--check" in sys.argv
    divergentes = []
    for claude, copilot in PARES.items():
        origem = ROOT / ".claude" / "agents" / f"{claude}.md"
        destino = ROOT / ".github" / "agents" / f"{copilot}.agent.md"

        _, corpo = dividir(origem.read_text(encoding="utf-8").replace("\r\n", "\n"))
        bruto = destino.read_bytes().decode("utf-8")
        tinha_bom = bruto.startswith(BOM)
        crlf = "\r\n" in bruto
        frontmatter, corpo_atual = dividir(bruto.lstrip(BOM).replace("\r\n", "\n"))

        if corpo_atual.strip() == corpo.strip():
            continue
        divergentes.append(copilot)
        if so_checar:
            continue

        novo = frontmatter + corpo
        if crlf:
            novo = novo.replace("\n", "\r\n")
        if tinha_bom:
            novo = BOM + novo
        destino.write_bytes(novo.encode("utf-8"))

    acao = "divergem" if so_checar else "sincronizados"
    print(f"{len(divergentes)} agente(s) {acao}: {', '.join(divergentes) or '—'}")
    return 1 if (so_checar and divergentes) else 0


if __name__ == "__main__":
    sys.exit(main())
