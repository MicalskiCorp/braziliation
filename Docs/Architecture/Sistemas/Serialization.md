# Sistema: Serialization

> **Responsabilidade:** Configuração da serialização/desserialização JSON dos dados de jogo.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `SaveJsonOptions.cs` | `src/Braziliation.Game.Core/Serialization/SaveJsonOptions.cs` | Opções centralizadas de `System.Text.Json` para saves |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [SaveSystem](SaveSystem.md) | `SaveGameService.cs` | Consome as opções JSON definidas aqui |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar — ex: indented, camelCase, ignoreNull)* | — | — | — |

## Notas de Design

- Centralizar as `JsonSerializerOptions` evita inconsistências entre serialização e desserialização.
- Alterar aqui afeta todos os saves existentes — considerar migração de dados ao mudar opções.
