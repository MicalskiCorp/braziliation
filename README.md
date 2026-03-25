# Braziliation
Jogo plataforma 2D em pixel art (C#) — ambientação dieselpunk pós-apocalíptica brasileira.

## 🧱 Estrutura
- Engine: Unity / MonoGame (C#)
- Linguagem: C#
- Estilo: Pixel Art (paleta restrita para estilo SNES)
- Plataforma alvo: PC / SNES (EverDrive) - dependendo do build target

## 📂 Pastas principais
- `Assets/` → Cenas, arte, áudio, scripts C# (`Assets/Scripts/`), configuração URP
- `AI/` → Agentes, contexto, prompts e memória para desenvolvimento com Cursor
- `Docs/` → GDD, arquitetura, lore, mecânicas e docs técnicos
- `scripts/` → Scripts de setup/versionamento (PowerShell, shell)
- `Packages/` / `ProjectSettings/` → Unity (não mover)
- `Braziliation.sln` → solution gerada/usada com **Assembly-CSharp** (Unity / IDE)
- `Braziliation.CI.sln` → solution opcional com os testes .NET (útil no IDE)
- **`dotnet-tests/Braziliation.Game.Tests/`** → testes .NET para o CI (pasta **fora** de `Tests/` na raiz, que costuma ser Unity ou ficar vazia no Git)
- **CI (GitHub / GitLab)** → `dotnet restore/build/test` nesse `.csproj`; o workflow aceita caminhos antigos (`Tests/…`, `tests/…`) ou `find` como último recurso

### Limpeza local (logs)
A pasta `Logs/` na raiz é gerada pelo Unity e está no `.gitignore`. Se quiser apagá-la, **feche o editor Unity** e remova `Logs/` manualmente (arquivos podem ficar bloqueados com o projeto aberto).

## ⚙️ Como começar (rápido)
1. Clone o repositório.
2. Instale Git LFS: `git lfs install`
3. Configure o remote: `git remote add origin git@github.com:<org>/Braziliation.git`
4. Push inicial: `git push -u origin develop`

## 🚀 Roadmap inicial
Consulte o ClickUp: (link do espaço do projeto)

---

## 🤖 Desenvolvimento assistido por IA (Cursor)

O repositório inclui uma estrutura para **desenvolvimento assistido por agentes de IA** no Cursor, sem alterar a organização Unity (Assets, Packages, ProjectSettings).

### Estrutura AI/

- **AI/Agents/** – Definições de papéis: Tech Lead, Architect, Unity Engineer, Gameplay Engineer, QA Engineer. Use esses arquivos para que o modelo atue como cada papel.
- **AI/Context/** – Visão do jogo, direção de arte, padrões de código. Consulte em prompts para manter respostas alinhadas ao projeto.
- **AI/Prompts/** – Modelos de prompt reutilizáveis: criar feature, refatorar sistema, revisar código, desenhar inimigo.
- **AI/Memory/** – Memória compartilhada: decisões de arquitetura (ADRs), roadmap, tech debt. Atualize conforme o projeto evolui.

### Como usar os agentes no Cursor

1. **Definir o papel** – No início da tarefa, peça ao Cursor que adote um papel citando o arquivo em `AI/Agents/` (ex.: `AI/Agents/tech_lead.md`).
2. **Incluir contexto** – Para tarefas de design ou código, mencione ou anexe `AI/Context/` ou `Docs/Architecture/AssetsStructure.md`.
3. **Usar templates** – Para features, refactors ou reviews, use os arquivos em `AI/Prompts/`, preencha os campos e cole no chat.
4. **Manter a memória** – Decisões estruturais → `AI/Memory/architecture_decisions.md`; tech debt → `AI/Memory/tech_debt.md`; prioridades → `AI/Memory/roadmap.md`.

**Guia completo e exemplos de prompts:** [AI/README.md](AI/README.md)
