# Braziliation — Documentação Técnica

> Documentação técnica do projeto Braziliation. Engine: Unity 6 (C#) | Gênero: Plataforma 2D Pixel Art | Estilo: Dieselpunk pós-apocalíptico brasileiro
> 🎨 **Camada criativa (lendas, narrativa, brainstorm):** ver [`Design/`](../../Design/index.md)

## Design & Features

| Seção | Descrição | Arquivo |
|-------|-----------|---------|
| GDD | O que o jogo é: features e decisões de design | [`GDD/`](GDD/index.md) |
| Mecânicas | Regras, parâmetros e comportamentos | [`Mechanics/`](Mechanics/index.md) |
| Roadmap | Fases e planejamento | [`Roadmap/roadmap.md`](Roadmap/roadmap.md) |
| Backlog | Features e onde estão documentadas | [`Roadmap/backlog.md`](Roadmap/backlog.md) |

## Arquitetura & Técnico

| Seção | Descrição | Arquivo |
|-------|-----------|---------|
| Sistemas | Ficha de cada sistema — **é o índice de scripts** | [`Architecture/Sistemas/`](Architecture/Sistemas/index.md) |
| Índices | Assets e protocolo de sincronização | [`Architecture/indices/`](Architecture/indices/index.md) |
| ADRs | Decisões de arquitetura | [`Architecture/architecture_decisions.md`](Architecture/architecture_decisions.md) |
| Estrutura de Assets | Layout de `Assets/` | [`Architecture/Assets/AssetsStructure.md`](Architecture/Assets/AssetsStructure.md) |
| Tech | Regras de desenvolvimento, dívida técnica, CI Unity e processos dos agentes | [`Tech/`](Tech/index.md) |

## Manutenção

| Seção | Descrição | Arquivo |
|-------|-----------|---------|
| TODO | Pendências vivas da camada de Desenvolvimento | [`TODO.md`](TODO.md) |
| Arquivo | Histórico de pendências até 2026-09-13 | [`TODO-arquivo.md`](TODO-arquivo.md) |
| Models | Templates reutilizáveis (não editar) | [`Models/`](Models/index.md) |

---

> Nova feature: `@GameArchitect Nova feature: {Nome}` · Novo sistema: `@GameArchitect Novo sistema: {Nome}`
> Calibrar a sessão: no Claude Code o hook `SessionStart` já injeta a foto do projeto; no Copilot use o prompt `/project-context`.
