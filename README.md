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
├── .claude/                    ← Claude Code: 11 agentes, 16 skills, hooks, rules, settings
├── .github/                    ← plataforma GitHub: CI e templates de issue/PR
│   ├── workflows/              ← GitHub Actions (ci.yml, unity-ci.yml)
│   ├── ISSUE_TEMPLATE/         ← templates de issue
│   └── PULL_REQUEST_TEMPLATE.md
├── .githooks/                  ← pre-commit versionado (testes, meta-check, paletas)
├── AGENTS.md                   ← mapa de agentes, camadas e TODOs (importado pelo CLAUDE.md)
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
#    Os hooks do LFS (post-checkout, post-commit, post-merge, pre-push) são versionados
#    em .githooks/ junto com o pre-commit do projeto — é o pre-push que sobe os objetos
#    LFS, e sem ele um push publica ponteiros sem os binários. Rodar este comando é
#    idempotente: ele reescreve os mesmos arquivos.
git lfs install
git lfs pull

# 3. Compile o core — ANTES de abrir o Unity
#    Assets/Plugins/Braziliation/ é saída de build e não é versionada: num clone novo
#    ela chega vazia, e sem a DLL o projeto Unity não compila.
dotnet build Desenvolvimento/src/Braziliation.Game.Core/Braziliation.Game.Core.csproj

# 4. Abra o projeto Unity
#    → Aponte o Unity Hub para a pasta  Desenvolvimento/
#    → Unity 6 (6000.2+) com URP 2D

# 5. Abra no VS Code
code .
```

### Pré-requisitos

| Ferramenta | Versão mínima |
|------------|--------------|
| Unity Hub | 3.x |
| Unity | 6000.2+ (URP 2D) |
| .NET SDK | 8.0 (para testes CI) |
| Git LFS | 3.x |
| Claude Code | CLI ou extensão do VS Code |

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

## 🤖 Desenvolvimento assistido por IA (Claude Code)

O projeto usa **Claude Code** como único harness de agentes ([ADR-008](Desenvolvimento/Docs/Architecture/architecture_decisions.md)): agentes, skills, hooks e regras vivem em `.claude/`.

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

**Mapa de agentes, camadas e TODOs:** [AGENTS.md](AGENTS.md) · **skills, travas e MCPs:** [processos.md](Desenvolvimento/Docs/Tech/processos.md)

### Como usar

1. **Abrir o Claude Code na raiz do repositório** — a descoberta de `.claude/agents/` e `.claude/skills/` depende do diretório aberto.
2. **Acionar um agente** — pelo pedido em linguagem natural ou com `@agent-{nome}` (ex.: `@agent-historiador`).
3. **Acionar uma skill** — `/{nome}` (ex.: `/fechar-decisao`, `/unity-validar`).
4. **Contexto da sessão** — o hook `SessionStart` injeta a foto do projeto (git, pendências Alta dos TODOs, última validação Unity).

---

## 📘 Manual de processos

Como o projeto funciona, camada por camada: quem executa cada processo, como se aciona, o passo a passo, o que lê e escreve e onde a entrega é travada. Cada processo aponta a fonte canônica (o agente ou a skill que o executa).

| Camada | Área | Processos | Manual |
|--------|------|:---------:|--------|
| Pesquisa | Design | 7 | [pesquisa.md](Desenvolvimento/Docs/Processos/pesquisa.md) |
| Criativo | Design | 10 | [criativo.md](Desenvolvimento/Docs/Processos/criativo.md) |
| Arte | Design (lateral) | 7 | [arte.md](Desenvolvimento/Docs/Processos/arte.md) |
| Documentação | Desenvolvimento | 7 | [documentacao.md](Desenvolvimento/Docs/Processos/documentacao.md) |
| Implementação | Desenvolvimento | 9 | [implementacao.md](Desenvolvimento/Docs/Processos/implementacao.md) |
| Orquestração | Transversal | 5 | [orquestracao.md](Desenvolvimento/Docs/Processos/orquestracao.md) |

**Visão geral, encadeamento das camadas e regras comuns:** [Desenvolvimento/Docs/Processos/index.md](Desenvolvimento/Docs/Processos/index.md) · **Onde cada procedimento mora** (modo, skill, script, teste, hook, regra): [modo-skill-ou-regra.md](Desenvolvimento/Docs/Processos/modo-skill-ou-regra.md)

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
| [`Docs/Tech/`](Desenvolvimento/Docs/Tech/) | Tech debt, regras de desenvolvimento, catálogo de skills e travas |
| [`Docs/Processos/`](Desenvolvimento/Docs/Processos/index.md) | Manual de processos por camada |

**Hub técnico:** [Desenvolvimento/Docs/index.md](Desenvolvimento/Docs/index.md)

---

## 🌿 Branches

**Até a v1:** commits direto no `main`, com o pre-commit ativo (`git config core.hooksPath .githooks`).

**Depois da v1:**

| Branch | Propósito |
|--------|-----------|
| `main` | Produção / releases estáveis |
| `develop` | Integração contínua |
| `feature/*` | Novas features |
| `hotfix/*` · `chore/*` | Correções emergenciais · manutenção técnica |

Regras completas: [`Desenvolvimento/Docs/Tech/DevelopmentRules.md`](Desenvolvimento/Docs/Tech/DevelopmentRules.md).
