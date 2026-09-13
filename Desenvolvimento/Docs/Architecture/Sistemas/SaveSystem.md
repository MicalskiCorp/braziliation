# Sistema: SaveSystem

> **Responsabilidade:** Gerenciamento de slots de save: criar, carregar, apagar e listar saves do jogador.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `ISaveStorage.cs` | `src/Braziliation.Game.Core/SaveSystem/ISaveStorage.cs` | Contrato de armazenamento de saves |
| `SaveGameService.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveGameService.cs` | Serviço principal: save, load, delete |
| `SaveSlot.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveSlot.cs` | Modelo de dados de um slot de save |
| `SaveLoadResult.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveLoadResult.cs` | Resultado de `LoadDetailed` com `SaveLoadStatus` (ADR-007) |
| `ISaveMigration.cs` | `src/Braziliation.Game.Core/SaveSystem/ISaveMigration.cs` | Contrato de um degrau de migração sobre o JSON bruto |
| `DelegateSaveMigration.cs` | `src/Braziliation.Game.Core/SaveSystem/DelegateSaveMigration.cs` | Degrau de migração a partir de um delegate |
| `SaveMigrations.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveMigrations.cs` | Registro `SaveMigrations.All` aplicado em cadeia |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Storage](Storage.md) | `StorageProviderSaveAdapter.cs` | Persistência em disco via adapter |
| [Serialization](Serialization.md) | `SaveJsonOptions.cs` | Serialização JSON dos dados de save |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar)* | — | — | — |

## Notas de Design

- Usa `ISaveStorage` para desacoplar a lógica de save do provedor físico de armazenamento.
- O `StorageProviderSaveAdapter` faz a ponte entre `IStorageProvider` (Storage) e `ISaveStorage`.
