# Coding Standards – Braziliation

## Language and engine

- **Language:** C#
- **Engine:** Unity 6 (6000.2), URP 2D
- **Input:** com.unity.inputsystem (Input System)
- **Target:** PC; optional SNES (EverDrive) per build configuration

## Namespaces

- Root namespace: `Braziliation`
- Subnamespaces match folder structure under `Assets/Scripts/`:
  - `Braziliation.Core` – Bootstrap, camera, global init
  - `Braziliation.Player` – Player controller, movement, abilities
  - `Braziliation.Enemies` – Enemy AI and behaviors
  - `Braziliation.Combat` – Damage, health, weapons
  - `Braziliation.Inventory` – Items, equipment
  - `Braziliation.World` – Level logic, hazards, interactables
  - `Braziliation.UI` – Menus, HUD, dialogs
  - `Braziliation.Utils` – Shared utilities, extensions

## Script layout

- **One primary responsibility per script.** No god classes.
- **Names:** PascalCase for types and public members; camelCase for private fields. Suffix MonoBehaviours with clear names (e.g. `PlayerController`, `EnemyPatrol`).
- **Inspector:** Use `[Header]`, `[Tooltip]`, `[Range]` where helpful. Serialize only what designers need to tweak.
- **Lifecycle:** Prefer `FixedUpdate` for physics; avoid heavy work in `Update`. Use events/coroutines for delayed or one-shot logic.

## Unity conventions

- **Pixel Perfect:** Respect 320×180 and 16 PPU. No arbitrary scaling that breaks pixel alignment.
- **Physics 2D:** Use `Rigidbody2D` and `Collider2D`; set layers and matrix in Project Settings.
- **Prefabs:** One prefab per logical entity (e.g. player, enemy type, projectile). Variants for tuning.
- **ScriptableObjects:** Use for design-time data (stats, item definitions, wave configs). Runtime state stays in components.

## Git and workflow

- Follow **Docs/Tech/DevelopmentRules.md**: branch naming, commit format `tipo(scope): descrição`, PR and CI.
- Do not remove or restructure **Assets/**, **Packages/**, **ProjectSettings/** beyond agreed changes.

## References

- **.cursor/rules/unity-csharp.mdc** – Applied to `Assets/**/*.cs`
- **.cursor/rules/braziliation-project.mdc** – Project overview and folder structure
- **Docs/Architecture/** – System boundaries and data flow
