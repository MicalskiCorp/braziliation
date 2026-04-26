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
