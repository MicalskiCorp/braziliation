# Agente: GameArquitetoMarkdown

> **Papel:** Arquiteto da camada de documentação/gerenciamento Markdown do projeto.
> **Arquivo-fonte:** [`GameArquitetoMarkdown.agent.md`](../../../../GameArquitetoMarkdown.agent.md) (raiz do workspace)

## Responsabilidades

- Bootstrap da estrutura `Docs/IA/` e `Docs/estrutura/`
- Criação de features (`Docs/IA/Features/`)
- Criação de sistemas (`Docs/IA/Sistemas/`)
- Criação de mecânicas (`Docs/IA/Mecanicas/`)
- Manutenção de `index.md` em todas as pastas
- Sincronização motor ↔ produto
- Varredura automática de gaps

## Modos de Operação

| Modo | Acionador | Ação |
|------|-----------|------|
| 0 — Bootstrap | `Bootstrap do projeto` | Cria toda a estrutura inicial |
| 1 — Nova Feature | `Nova feature: {Nome}` | Cria pasta + arquivos em `Features/` |
| 2 — Novo Sistema | `Novo sistema: {Nome}` | Cria arquivo em `Sistemas/` |
| 3 — Análise de Arquivo | `Analisar {arquivo.md}` | Diagnóstico de tokens e estrutura |
| 4 — Análise de Pasta | `Analisar {pasta/}` | Mapa de tokens + gaps de index |
| 5 — Sincronização | `Sincronizar camadas` | Motor ↔ produto |
| 6 — Varredura | `Varredura automática` | Detecta e cria stubs para gaps |

## Regras Invioláveis

- Nunca editar fontes do engine (scripts, cenas, prefabs, configs)
- Nunca editar arquivos em `Models/`
- Todo diretório deve ter `index.md` funcional
- Links sempre relativos
