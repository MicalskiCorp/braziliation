# Braziliation
Jogo plataforma 2D em pixel art (C#) — ambientação dieselpunk pós-apocalíptica brasileira.

## 🧱 Estrutura
- Engine: Unity 6 (6000.2) + URP 2D
- Linguagem: C#
- Estilo: Pixel Art de alta densidade (ADR-004)
- Plataforma alvo: PC (Steam)

## 📂 Pastas principais (dentro de `Desenvolvimento/`)
- `Assets/` → Cenas, arte, áudio, scripts C# (`Assets/Scripts/`), configuração URP
- `Docs/` → GDD, arquitetura, lore, mecânicas, roadmap e docs técnicos
- `scripts/` → `update_version.ps1` (atualiza `VERSION` e o `bundleVersion` do Unity juntos)
- `Packages/` / `ProjectSettings/` → Unity (não mover)
- `Braziliation.slnx` → solution principal (Assembly-CSharp + Core + Tests)
- `Braziliation.CI.slnx` → solution opcional com os testes .NET (útil no IDE)
- **`Tests/Braziliation.Game.Tests/`** → testes xUnit .NET (rodam no CI, sem Unity)
- **`Assets/Tests/EditMode/`** → testes EditMode do Unity (skill `unity-validar`)
- **CI (GitHub Actions)** → `dotnet restore/build/test` no `.csproj` de testes, meta-check e paletas; caminhos prefixados com `Desenvolvimento/` no workflow

> 📁 **Estrutura do repositório:** o projeto Unity vive em `Desenvolvimento/`. A camada criativa (lore, lendas, brainstorm) vive em `Design/Criativo/`. Agents e instructions em `.github/`.

### Limpeza local (logs)
A pasta `Logs/` na raiz é gerada pelo Unity e está no `.gitignore`. Se quiser apagá-la, **feche o editor Unity** e remova `Logs/` manualmente (arquivos podem ficar bloqueados com o projeto aberto).

## ⚙️ Como começar (rápido)
1. Clone o repositório.
2. Instale Git LFS: `git lfs install`
3. Configure o remote: `git remote add origin git@github.com:<org>/Braziliation.git`
4. Push inicial: `git push -u origin main` (commits vão direto no `main` até a v1 — ver `Docs/Tech/DevelopmentRules.md`)

## 🚀 Roadmap
Fases em [`Docs/Roadmap/roadmap.md`](Docs/Roadmap/roadmap.md); pendências vivas em [`Docs/TODO.md`](Docs/TODO.md).

---

## 🤖 Desenvolvimento assistido por IA

O repositório funciona com **Claude Code** e **VS Code Copilot**. Os 11 agentes têm o mesmo corpo nos dois formatos: `.claude/agents/` (Claude Code) e `.github/agents/` (Copilot).

- **Agentes e fluxo entre camadas:** [AGENTS.md](../AGENTS.md) — a lista de agentes vive só lá.
- **Skills, travas automáticas e processos:** [Docs/Tech/processos.md](Docs/Tech/processos.md).
- **Copilot:** instruções em `.github/instructions/` e prompts em `.github/prompts/` (`/project-context` calibra a sessão).
- **Claude Code:** o hook `SessionStart` injeta a foto do projeto; regras por caminho em `.claude/rules/`.
- **Atualizar docs:** decisão de arquitetura → `Docs/Architecture/architecture_decisions.md`; dívida técnica → `Docs/Tech/tech_debt.md`.

> 🎨 **Camada criativa:** `Design/Criativo/` na raiz do repo — gerida por `@GameCreative`.

---

## 📜 Licença e créditos

O código é MIT ([`LICENSE`](LICENSE)). Assets de terceiros mantêm as licenças próprias e estão
listados em [`CREDITS.md`](CREDITS.md) — **todo asset de terceiro que permanecer no projeto precisa
constar lá**, mesmo quando a licença dispensa atribuição.
