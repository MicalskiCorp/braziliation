# Protocolo de Comunicação — Índice Técnico ↔ Features

> Define as regras de sincronização entre `Docs/Architecture/indices/` (motor) e `Docs/GDD/Features/` + `Docs/Architecture/Sistemas/` (produto).

## Camadas

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Índice técnico | `Docs/Architecture/indices/` | Scripts, assets e cenas mapeados por sistema |
| Produto (features) | `Docs/GDD/Features/` | Features navegáveis: design, critérios, fontes técnicas |
| Sistemas | `Docs/Architecture/Sistemas/` | Ficha técnica de cada sistema do jogo |

## Regras de Sincronização

1. **Novo script criado** → adicionar linha em `indices/sistemas.md` na seção do sistema correspondente.
2. **Novo sistema criado** → criar `Docs/Architecture/Sistemas/{Sistema}.md` e adicionar seção em `indices/sistemas.md`.
3. **Script renomeado/movido** → atualizar `indices/sistemas.md` e `Docs/Architecture/Sistemas/{Sistema}.md` (seção Fontes Técnicas).
4. **Feature documentada** → verificar se sistemas referenciados têm entrada em `indices/sistemas.md`.
5. **Varredura automática (Modo 6)** → detecta gaps automaticamente e cria stubs.

## Verificação de Consistência

Executar periodicamente:

```powershell
# Sistemas em src/ sem seção em indices/sistemas.md
$sistemasNoFonte = Get-ChildItem "src/Braziliation.Game.Core" -Directory | Select-Object -ExpandProperty Name
# Comparar com seções em indices/sistemas.md
```

## Ponto de Contato

O agente `@GameArchitect` é o único responsável por manter ambas as camadas sincronizadas.
Definição do agente: `.github/agents/GameArchitect.agent.md`
