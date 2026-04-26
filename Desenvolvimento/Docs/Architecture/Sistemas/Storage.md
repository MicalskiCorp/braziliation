# Sistema: Storage

> **Responsabilidade:** Abstração de leitura e escrita em disco. Provider e adapters para SaveSystem e Settings.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `IStorageProvider.cs` | `src/Braziliation.Game.Core/Storage/IStorageProvider.cs` | Contrato do provider de armazenamento |
| `FileStorageProvider.cs` | `src/Braziliation.Game.Core/Storage/FileStorageProvider.cs` | Implementação: leitura/escrita em arquivo no disco |
| `StorageProviderSaveAdapter.cs` | `src/Braziliation.Game.Core/Storage/StorageProviderSaveAdapter.cs` | Adapta `IStorageProvider` para `ISaveStorage` |
| `StorageProviderSettingsAdapter.cs` | `src/Braziliation.Game.Core/Storage/StorageProviderSettingsAdapter.cs` | Adapta `IStorageProvider` para `ISettingsStorage` |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [SaveSystem](SaveSystem.md) | via `StorageProviderSaveAdapter` | Fornece persistência física |
| [Settings](Settings.md) | via `StorageProviderSettingsAdapter` | Fornece persistência física |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| Diretório de saves | `string` | *(a documentar)* | Caminho raiz dos arquivos de save |

## Notas de Design

- Padrão Adapter: permite trocar o `IStorageProvider` (ex: memória para testes, arquivo para produção) sem alterar SaveSystem ou Settings.
- O `FileStorageProvider` deve usar `Application.persistentDataPath` no Unity para garantir compatibilidade de plataforma.
