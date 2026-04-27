# Braziliation

> Jogo plataforma 2D em pixel art (C#) — ambientação **dieselpunk pós-apocalíptica brasileira**.
> Engine: Unity 6 · Linguagem: C# · Estilo: Pixel Art (paleta restrita, 16 PPU)

---

## 📁 Estrutura do repositório

```
Braziliation/                   ← raiz do repositório
├── Desenvolvimento/            ← projeto Unity (engine, código, assets, testes)
│   ├── Assets/                 ← cenas, arte, áudio, scripts C#
│   ├── Docs/                   ← documentação técnica (GDD, arquitetura, roadmap)
│   ├── dotnet-tests/           ← testes .NET para o CI (sem Unity no runner)
│   ├── src/                    ← sistemas C# puros (sem Unity)
│   ├── scripts/                ← scripts de setup/versionamento
│   ├── ProjectSettings/        ← configuração Unity (não mover)
│   ├── Packages/               ← pacotes Unity (não mover)
│   ├── Braziliation.slnx       ← solution principal
│   ├── Braziliation.CI.slnx    ← solution para CI (testes .NET)
│   ├── AGENTS.md               ← guia de agentes de IA para o projeto Unity
│   └── README.md               ← README do projeto Unity
├── Design/                     ← camada criativa (lore, brainstorm, arte conceitual)
│   ├── Criativo/               ← lendas, cidades por estado, ideias, personagens
│   ├── Models/                 ← templates de documentação criativa
│   └── Arts Conceituas/        ← referências visuais para assets
├── .github/                    ← CI/CD + agentes e instruções de IA (VS Code Copilot)
│   ├── agents/                 ← 10 agentes especializados
│   ├── instructions/           ← instruções auto-injetadas pelo Copilot
│   ├── prompts/                ← templates de prompt (/create-feature, etc.)
│   ├── workflows/              ← GitHub Actions (ci.yml)
│   ├── ISSUE_TEMPLATE/         ← templates de issue
│   └── PULL_REQUEST_TEMPLATE.md
├── .vscode/                    ← configurações do VS Code
├── .gitignore
├── .gitattributes              ← Git LFS para assets binários
└── .gitlab-ci.yml              ← CI GitLab (alternativo ao GitHub Actions)
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

Os testes unitários vivem em `Desenvolvimento/dotnet-tests/` e rodam **sem precisar do Unity**:

```bash
cd Desenvolvimento
dotnet restore dotnet-tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj
dotnet test dotnet-tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj --configuration Release
```

O CI (GitHub Actions e GitLab CI) executa esses mesmos comandos automaticamente em push/PR para `main` e `develop`.

---

## 🤖 Desenvolvimento assistido por IA (VS Code Copilot)

O repositório usa **VS Code Copilot** com agentes, instructions e prompts customizados em `.github/`.

### Agentes disponíveis

| Agente | Use para |
|--------|----------|
| `@TechLead` | Direção técnica, padrões, routing |
| `@Architect` | Limites de sistema, interfaces, ADRs |
| `@UnityEngineer` | Setup de engine: URP, Input System, câmera |
| `@UnityDeveloper` | UI controllers, ServiceLocator, MonoBehaviours |
| `@SystemsDeveloper` | Save, Settings, Storage (C# puro, sem Unity) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArchitect` | Estrutura Markdown, índices, features, sistemas |
| `@GameCreative` | Lendas, brainstorm, personagens, lore |

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

**Guia detalhado:** [Desenvolvimento/AGENTS.md](Desenvolvimento/AGENTS.md)

---

## 🎨 Camada criativa

Lendas, cidades, personagens e brainstorm vivem em `Design/Criativo/` — separados do código Unity, versionados no mesmo repositório.

```
Design/Criativo/
├── index.md                ← hub principal
├── Estados/                ← cidades organizadas por estado brasileiro
│   └── SantaCatarina/      ← Florianópolis, Blumenau, Lages, Guabiruba...
├── Lendas/                 ← catálogo de lendas mapeadas para monstros/cenários
├── Personagens/
├── Arcos/
└── Ideias/
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
