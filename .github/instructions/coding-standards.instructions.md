---
description: "Padrões de código C# do Braziliation: namespaces, convenções Unity, lifecycle, prefabs, ScriptableObjects e Git. Aplicado automaticamente a todos os arquivos .cs do projeto."
applyTo: "Desenvolvimento/Assets/**/*.cs"
---
# Coding Standards – Braziliation

## Language and engine

- **Language:** C#
- **Engine:** Unity 6 (6000.2), URP 2D
- **Input:** com.unity.inputsystem (New Input System)
- **Target:** PC; port SNES (EverDrive) por build configuration

## Namespaces

Namespace raiz: `Braziliation`. Subnamespaces espelham pastas em `Assets/Scripts/`:

| Pasta | Namespace |
|-------|-----------|
| `Core/` | `Braziliation.Core` |
| `Player/` | `Braziliation.Player` |
| `Enemies/` | `Braziliation.Enemies` |
| `Combat/` | `Braziliation.Combat` |
| `Inventory/` | `Braziliation.Inventory` |
| `World/` | `Braziliation.World` |
| `UI/` | `Braziliation.UI` |
| `Utils/` | `Braziliation.Utils` |

## Script layout

- **Uma responsabilidade por script.** Sem god classes.
- **Nomes:** PascalCase para types e membros públicos; camelCase para campos privados. MonoBehaviours com sufixo descritivo (`PlayerController`, `EnemyPatrol`).
- **Inspector:** Use `[Header]`, `[Tooltip]`, `[Range]` onde útil. Serialize apenas o que designers precisam ajustar. Use `[SerializeField]` — nunca `public` para campos Unity.
- **Lifecycle:** `FixedUpdate` para física; sem lógica pesada em `Update`. Use events/coroutines para lógica adiada ou pontual.

## Unity conventions

- **Pixel Perfect:** Respeite 320×180 e 16 PPU. Nenhum scaling arbitrário que quebre alinhamento de pixel.
- **Physics 2D:** Use `Rigidbody2D` e `Collider2D`; configure layers e matrix em Project Settings.
- **Prefabs:** Um prefab por entidade lógica (player, tipo de inimigo, projétil). Variants para tuning.
- **ScriptableObjects:** Para dados em tempo de design (stats, definições de item, wave configs). Estado de runtime fica em components.
- **Business logic:** Zero em MonoBehaviours de UI — eles apenas chamam serviços. Toda lógica vive em `Braziliation.Game.Core` (C# puro).

## Pure C# systems (`src/Braziliation.Game.Core/`)

- Zero dependência de `UnityEngine.*` ou `UnityEditor.*`.
- Serviços recebem todas as dependências via construtor (sem estado estático).
- Caminhos de arquivo nunca hardcoded — sempre injetados na construção.
- Serialização com `System.Text.Json` + `SaveJsonOptions.Default`.

## Git and workflow

- Siga `Docs/Tech/DevelopmentRules.md`: nomenclatura de branches, formato de commit `tipo(scope): descrição`, PR e CI.
- Não remova nem reestruture `Assets/`, `Packages/`, `ProjectSettings/` além do combinado.
