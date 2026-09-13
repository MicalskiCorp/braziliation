# Braziliation

> Jogo plataforma 2D em pixel art (C#) — ambientação **dieselpunk pós-apocalíptica brasileira**.
> Engine: Unity 6 · Linguagem: C# · Estilo: Pixel Art (paleta restrita, 32 PPU)

---

## 📁 Estrutura do repositório

```
Braziliation/                   ← raiz do repositório
├── Desenvolvimento/            ← projeto Unity (engine, código, assets, testes)
│   ├── Assets/                 ← cenas, arte, áudio, scripts C#
│   ├── Docs/                   ← documentação técnica (GDD, arquitetura, roadmap)
│   ├── src/                    ← sistemas C# puros (sem Unity)
│   ├── Tests/                  ← testes xUnit .NET (rodam no CI, sem Unity)
│   ├── scripts/                ← update_version.ps1 (VERSION + bundleVersion do Unity)
│   ├── ProjectSettings/        ← configuração Unity (não mover)
│   ├── Packages/               ← pacotes Unity (não mover)
│   ├── Braziliation.slnx       ← solution principal
│   ├── Braziliation.CI.slnx    ← solution para CI (testes .NET)
│   └── README.md               ← README do projeto Unity
├── Design/                     ← camadas de pesquisa, criativa e de arte
│   ├── Pesquisa/               ← pesquisa histórica e folclórica com fonte (@Historiador)
│   ├── Criativo/               ← cidades por estado, lendas, história, ideias (@GameCreative)
│   ├── ArteConceitual/         ← concept art, referências visuais e paletas
│   ├── ArteFonte/              ← ferramentas de arte, context packs e saídas de IA
│   ├── GuiasDeArte/            ← bíblia visual, paletas, escala e pipelines de sprite
│   └── Models/                 ← templates de documentação criativa
├── .claude/                    ← Claude Code: 11 agentes, 15 skills, hooks, rules, settings
├── .github/                    ← agentes e instruções do Copilot + CI
│   ├── agents/                 ← 11 agentes (formato Copilot)
│   ├── instructions/           ← instruções auto-injetadas pelo Copilot
│   ├── prompts/                ← templates de prompt (/create-feature, etc.)
│   ├── workflows/              ← GitHub Actions (ci.yml, unity-ci.yml)
│   ├── ISSUE_TEMPLATE/         ← templates de issue
│   └── PULL_REQUEST_TEMPLATE.md
├── .githooks/                  ← pre-commit versionado (testes, meta-check, paletas)
├── AGENTS.md                   ← guia canônico de agentes, skills e processos
├── CLAUDE.md                   ← entrada do Claude Code (importa AGENTS.md)
├── .mcp.json                   ← servidores MCP do projeto (aseprite, unity)
├── .gitignore
└── .gitattributes              ← Git LFS para assets binários; LF nos hooks
```

---

## ⚙️ Como começar

```bash
# 1. Clone o repositório
git clone git@github.com:<org>/Braziliation.git
cd Braziliation

# 2. Instale Git LFS
git lfs install
git lfs pull

# 3. Abra o projeto Unity
#    → Aponte o Unity Hub para a pasta  Desenvolvimento/
#    → Unity 6 (6000.2+) com URP 2D

# 4. Abra no VS Code
code .
```

### Pré-requisitos

| Ferramenta | Versão mínima |
|------------|--------------|
| Unity Hub | 3.x |
| Unity | 6000.2+ (URP 2D) |
| .NET SDK | 8.0 (para testes CI) |
| Git LFS | 3.x |
| VS Code | 1.90+ (com extensão GitHub Copilot) |

---

## 🧪 Testes .NET (CI local)

Os testes unitários vivem em `Desenvolvimento/Tests/` (xUnit) e rodam **sem precisar do Unity**:

```bash
cd Desenvolvimento
dotnet test Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj
```

O CI (GitHub Actions) executa esses mesmos comandos automaticamente em push/PR para `main` e `develop`, mais o meta-check e a checagem de paleta.

Antes de commitar, ative o pre-commit uma vez por clone — ele roda as mesmas travas localmente:

```bash
git config core.hooksPath .githooks
```

---

## 🤖 Desenvolvimento assistido por IA (VS Code Copilot)

O repositório usa **VS Code Copilot** com agentes, instructions e prompts customizados em `.github/`.

### Agentes disponíveis

| Agente | Use para |
|--------|----------|
| `@TechLead` | Direção técnica, padrões, routing, interfaces, ADRs |
| `@UnityDeveloper` | Tudo Unity: setup de engine e wiring de runtime |
| `@SystemsDeveloper` | Save, Settings, Storage (C# puro, sem Unity) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArchitect` | Estrutura Markdown, índices, features, sistemas |
| `@GameCreative` | Lendas, brainstorm, personagens, lore |
| `@Historiador` | Pesquisa histórica e folclórica com fonte |
| `@SpriteArtist` | Sprites programáticos, ciclo de crítica visual |
| `@AgentArchitect` | Orquestração, criação e auditoria de agentes |

**Guia completo dos 11 agentes, skills e fluxos:** [AGENTS.md](AGENTS.md)

### Prompts rápidos

| Prompt | Descrição |
|--------|-----------|
| `/project-context` | Carrega todo o contexto do projeto na sessão |
| `/create-feature` | Documenta e implementa uma nova feature |
| `/design-enemy` | Cria estrutura de inimigo (stats, componentes, prefab) |
| `/refactor-system` | Plano de refactor com ADR e tech debt |
| `/review-code` | Revisão de código contra padrões e GDD |

### Como usar

1. **Acionar agente** — Digite `@NomeDoAgente` no chat do Copilot.
2. **Usar template** — Digite `/` no chat e selecione o prompt.
3. **Calibrar sessão** — Use `/project-context` para carregar o contexto completo.

**Guia detalhado:** [AGENTS.md](AGENTS.md)

---

## 🎨 Camada criativa

Lendas, cidades, personagens e brainstorm vivem em `Design/Criativo/` — separados do código Unity, versionados no mesmo repositório. Referências visuais e fontes de arte vivem em `Design/ArteConceitual/`, `Design/ArteFonte/` e `Design/GuiasDeArte/`.

```
Design/Criativo/
├── index.md                ← hub principal
├── Estados/                ← cidades organizadas por estado brasileiro
│   └── SantaCatarina/      ← Florianópolis, Blumenau, Lages, Guabiruba...
├── Lendas/                 ← catálogo de lendas mapeadas para monstros/cenários
├── Historia/               ← premissa, arcos e personagens (personagens/)
├── Ideias/                 ← pool de ideias brutas
├── Brainstorm/             ← sessões de brainstorm
└── TODO.md                 ← pendências da camada criativa
```

Use `@GameCreative` para popular e navegar esta camada.

---

## 📚 Documentação técnica

A documentação técnica do projeto Unity vive em `Desenvolvimento/Docs/`:

| Seção | Descrição |
|-------|-----------|
| [`Docs/GDD/`](Desenvolvimento/Docs/GDD/) | Features documentadas |
| [`Docs/Architecture/`](Desenvolvimento/Docs/Architecture/) | Sistemas, ADRs, índice de scripts |
| [`Docs/Mechanics/`](Desenvolvimento/Docs/Mechanics/) | Regras e mecânicas de gameplay |
| [`Docs/Roadmap/`](Desenvolvimento/Docs/Roadmap/) | Fases e backlog |
| [`Docs/Tech/`](Desenvolvimento/Docs/Tech/) | Tech debt, regras de desenvolvimento |

**Hub técnico:** [Desenvolvimento/Docs/index.md](Desenvolvimento/Docs/index.md)

---

## 🌿 Branches

| Branch | Propósito |
|--------|-----------|
| `main` | Produção / releases estáveis |
| `develop` | Integração contínua |
| `feature/*` | Novas features |
| `fix/*` | Correções |

Consulte as regras completas em `Desenvolvimento/Docs/Tech/DevelopmentRules.md`.
