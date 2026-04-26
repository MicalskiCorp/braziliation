# Índice de Sistemas — Braziliation

> Mapeamento de scripts por sistema. Atualizar ao criar ou mover arquivos-fonte.
> Metodologia: [`../motor/como-indexar.md`](../motor/como-indexar.md)

## Core

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `GameServiceLocator.cs` | `Assets/Scripts/Core/GameServiceLocator.cs` | Service locator global |
| `GameInitializer.cs` | `Assets/Scripts/Core/GameInitializer.cs` | Inicialização do jogo |
| `CameraScaler.cs` | `Assets/Scripts/Core/CameraScaler.cs` | Escala da câmera por resolução |

## UI

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `MenuController.cs` | `Assets/Scripts/UI/MenuController.cs` | Controle do menu principal |
| `SaveSlotsView.cs` | `Assets/Scripts/UI/SaveSlotsView.cs` | Tela de slots de save |
| `SaveSlotEntryView.cs` | `Assets/Scripts/UI/SaveSlotEntryView.cs` | Entrada individual de slot |
| `SettingsView.cs` | `Assets/Scripts/UI/SettingsView.cs` | Tela de configurações |

## SaveSystem

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `ISaveStorage.cs` | `src/Braziliation.Game.Core/SaveSystem/ISaveStorage.cs` | Interface do armazenamento de save |
| `SaveGameService.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveGameService.cs` | Serviço principal de save/load |
| `SaveSlot.cs` | `src/Braziliation.Game.Core/SaveSystem/SaveSlot.cs` | Modelo de slot de save |

## Serialization

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `SaveJsonOptions.cs` | `src/Braziliation.Game.Core/Serialization/SaveJsonOptions.cs` | Opções de serialização JSON |

## Settings

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `ISettingsStorage.cs` | `src/Braziliation.Game.Core/Settings/ISettingsStorage.cs` | Interface de armazenamento de settings |
| `SettingsService.cs` | `src/Braziliation.Game.Core/Settings/SettingsService.cs` | Serviço de configurações do jogo |
| `GameSettings.cs` | `src/Braziliation.Game.Core/Settings/GameSettings.cs` | Modelo de configurações |

## Storage

| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| `IStorageProvider.cs` | `src/Braziliation.Game.Core/Storage/IStorageProvider.cs` | Interface do provider de armazenamento |
| `FileStorageProvider.cs` | `src/Braziliation.Game.Core/Storage/FileStorageProvider.cs` | Provider de armazenamento em arquivo |
| `StorageProviderSaveAdapter.cs` | `src/Braziliation.Game.Core/Storage/StorageProviderSaveAdapter.cs` | Adapter de storage para SaveSystem |
| `StorageProviderSettingsAdapter.cs` | `src/Braziliation.Game.Core/Storage/StorageProviderSettingsAdapter.cs` | Adapter de storage para Settings |
