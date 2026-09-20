# Braziliation.Game.Core — plugin do Unity

Esta pasta recebe a DLL compilada do projeto `Braziliation.Game.Core` para que o
`Assembly-CSharp` do Unity enxergue os serviços e tipos de domínio.

> **O conteúdo desta pasta é saída de build e não é versionado** — só este README é.
> Num clone novo a pasta chega vazia; o primeiro `dotnet build` do core a preenche.

## Primeiro uso num clone

```bash
dotnet build Desenvolvimento/src/Braziliation.Game.Core/Braziliation.Game.Core.csproj
```

O target `CopyToUnityPlugins` (em `Braziliation.Game.Core.csproj`) roda depois de cada
build e copia para cá a DLL do core mais as dependências NuGet que o runtime do Unity 6
não fornece. Não é preciso copiar nada à mão. Abra o Unity só depois disso — sem a DLL,
o projeto não compila.

## Por que não é versionado

O compilador emite bytes diferentes a cada troca de versão do SDK. Com a DLL no git,
qualquer `dotnet build` ou `dotnet test` local — inclusive o do pre-commit — deixava o
working tree sujo com uma modificação que ninguém pediu. Os `.meta` saíram junto: nada no
projeto referencia esses assets por GUID, e um `.meta` sem asset é o que o `meta-check`
reprova.

## O que é copiado

| Arquivo | Por quê |
|---|---|
| `Braziliation.Game.Core.dll` | O core em si (`netstandard2.1`, C# 10) |
| `System.Text.Json.dll` | O Unity 6 traz a v6.0.0; o core precisa da v8.0.0 |
| `System.Text.Encodings.Web.dll` | Dependência direta de `System.Text.Json` 8.x |
| `System.Runtime.CompilerServices.Unsafe.dll` | Exigida por `Encodings.Web` 8.x |
| `Microsoft.Bcl.AsyncInterfaces.dll` | Ausente no Mono; necessária para iteradores assíncronos |

Ficam de fora as que o BCL do Unity 6 já fornece: `System.Memory`, `System.Buffers`,
`System.Numerics.Vectors` e `System.Threading.Tasks.Extensions`.

## Tipos oferecidos aos scripts do Unity

| Namespace | Tipos principais |
|---|---|
| `Braziliation.SaveSystem` | `SaveGameService`, `SaveSlot`, `ISaveStorage`, `SaveLoadResult` |
| `Braziliation.Settings` | `SettingsService`, `GameSettings`, `ISettingsStorage` |
| `Braziliation.Storage` | `IStorageProvider`, `FileStorageProvider`, `StorageProviderSaveAdapter`, `StorageProviderSettingsAdapter` |
| `Braziliation.Build` | `BuildState`, `HybridSynergyResolver` |
| `Braziliation.Crafting` | `CraftingService`, `CraftingRecipe`, `ItemComponent`, `ReceptacleData` |
| `Braziliation.Enemies` | `EnemyBrain`, `EnemyBehaviorProfile`, `EnemySenses` |

## Notas

- O hook `PostToolUse` recompila o core sozinho quando um `.cs` de
  `src/Braziliation.Game.Core/` é editado numa sessão do Claude Code.
- Em CI o target não roda (`Condition="'$(CI)' != 'true'"`): lá não existe Editor para
  alimentar, e os testes referenciam o projeto direto, não esta pasta.
