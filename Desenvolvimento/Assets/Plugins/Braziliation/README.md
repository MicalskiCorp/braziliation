# Braziliation.Game.Core – Plugin Setup

This folder must contain the compiled DLL of the `Braziliation.Game.Core` project
so that Unity's `Assembly-CSharp` can reference the service and domain types.

## How to build and deploy

```powershell
# From the repository root:
dotnet build src/Braziliation.Game.Core/Braziliation.Game.Core.csproj -c Release

Copy-Item src/Braziliation.Game.Core/bin/Release/net8.0/Braziliation.Game.Core.dll `
          Assets/Plugins/Braziliation/Braziliation.Game.Core.dll -Force
```

After copying, Unity will reimport the DLL automatically.

## Types provided to Unity scripts

| Namespace | Key types |
|---|---|
| `Braziliation.SaveSystem` | `SaveGameService`, `SaveSlot`, `ISaveStorage` |
| `Braziliation.Settings` | `SettingsService`, `GameSettings`, `ISettingsStorage` |
| `Braziliation.Storage` | `IStorageProvider`, `FileStorageProvider`, `StorageProviderSaveAdapter`, `StorageProviderSettingsAdapter` |

## Notes

- Rebuild the DLL whenever `src/Braziliation.Game.Core/` changes.
- The DLL targets `net8.0`; Unity 6 is compatible.
- Add a CI step to automate the copy on merge to `main`.
