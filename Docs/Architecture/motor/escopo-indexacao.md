# Escopo de Indexação — Braziliation

> Define o que é indexado (e o que é ignorado) no projeto Braziliation.

## Incluir no Índice

| Tipo | Localização | Critério |
|------|-------------|----------|
| Scripts Unity (C#) | `Assets/Scripts/**/*.cs` | Todos |
| Código puro (C#) | `src/**/*.cs` | Todos |
| Cenas Unity | `Assets/Scenes/**/*.unity` | Todas |
| Tilemaps | `Assets/Tilemaps/` | Por referência em sistema |
| Prefabs relevantes | `Assets/Art/**/*.prefab` | Quando ligados a sistema documentado |

## Ignorar no Índice

| Tipo | Motivo |
|------|--------|
| `Library/` | Gerado pelo Unity — não é fonte |
| `Temp/` | Cache temporário |
| `Logs/` | Logs de execução |
| `bin/`, `obj/` | Compilação |
| `*.meta` | Gerado automaticamente pelo Unity |
| `packages-lock.json`, `manifest.json` | Gerenciamento de pacotes |

## Sistemas Mapeados

| Sistema | Localização Principal |
|---------|-----------------------|
| Core | `Assets/Scripts/Core/` |
| UI | `Assets/Scripts/UI/` |
| SaveSystem | `src/Braziliation.Game.Core/SaveSystem/` |
| Serialization | `src/Braziliation.Game.Core/Serialization/` |
| Settings | `src/Braziliation.Game.Core/Settings/` |
| Storage | `src/Braziliation.Game.Core/Storage/` |
