# Protocolo de Comunicação — Código ↔ Fichas ↔ Features

> Regras de sincronização entre o código-fonte, as fichas de sistema (`Docs/Architecture/Sistemas/`) e as features (`Docs/GDD/Features/`).

## Camadas

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Fichas de sistema | `Docs/Architecture/Sistemas/` | Ficha técnica de cada sistema; a seção "Fontes Técnicas" é o índice de scripts |
| Assets | `Docs/Architecture/indices/assets.md` | Assets principais e o backlog das 5 etapas por asset |
| Produto (features) | `Docs/GDD/Features/` | Features navegáveis: design, critérios, fontes técnicas |

## Regras de Sincronização

1. **Script novo** → linha na "Fontes Técnicas" da ficha do sistema (`` `Nome.cs` `` entre crases).
2. **Sistema novo** → `Sistemas/{Sistema}.md` a partir do `ModelSistema.md` + linha em `Sistemas/index.md`.
3. **Script renomeado ou movido** → atualizar a ficha que o lista.
4. **Feature documentada** → linkar as fichas dos sistemas que ela usa.

## Verificação automática

Nada disto depende de lembrar: o `DocsConsistencyTests` (roda no `dotnet test`, no pre-commit e no CI) falha quando

- uma pasta de `src/Braziliation.Game.Core/` não tem ficha nem linha no `Sistemas/index.md`;
- um `.cs` de `src/`, `Assets/Scripts/` ou `Assets/Editor/` não aparece em nenhuma ficha;
- um link relativo de qualquer `.md` aponta para arquivo inexistente.

## Ponto de Contato

O `@GameArchitect` mantém fichas e features sincronizadas. Definição do agente: `.claude/agents/game-architect.md`.
