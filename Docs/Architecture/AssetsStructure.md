# Recommended Unity Project Structure – Assets

This document defines the **recommended layout** under `Assets/` for Braziliation. It supports modular gameplay, clear ownership, and AI-assisted development. Existing folders (e.g. Art, Audio, Scenes, Scripts) are preserved; this structure extends and organizes them.

---

## Top-level layout

```
Assets/
├── Art/
├── Audio/
├── Prefabs/
├── Scenes/
├── ScriptableObjects/
├── Scripts/
│   ├── Core/
│   ├── Player/
│   ├── Enemies/
│   ├── Combat/
│   ├── Inventory/
│   ├── World/
│   ├── UI/
│   └── Utils/
├── Settings/          (existing: URP, Renderer2D, scene templates)
├── (other existing)   (e.g. Tilemaps, Sprites, InputSystem_Actions)
```

---

## Folder purposes

### Art/

- **Purpose:** All visual art assets (sprites, tiles, animations, UI art).
- **Contents:** Character sprites, environment tiles, props, VFX sprites, UI graphics. Use subfolders e.g. Characters, Environment, Props, UI (already present). Keep 16 PPU and pixel-art pipeline in mind; see `.github/instructions/art-direction.instructions.md`.

### Audio/

- **Purpose:** Music and sound effects.
- **Contents:** Subfolders such as Music, SFX. Naming and organization should support per-level or per-system use; see `.github/instructions/art-direction.instructions.md` for tone.

### Prefabs/

- **Purpose:** Reusable GameObject compositions.
- **Contents:** Player prefab, enemy prefabs, projectiles, interactables, hazards, UI widgets. One prefab per logical entity; use variants for tuning. Do not store one-off level-specific assemblies here unless they are reused.

### Scenes/

- **Purpose:** Unity scenes (levels, menus, bootstrap).
- **Contents:** Main menu, level scenes, test scenes. Naming should make it clear what each scene is (e.g. Level_01_Industrial, Menu_Main). Keep scene count and dependencies manageable.

### ScriptableObjects/

- **Purpose:** Design-time data assets.
- **Contents:** Stats (e.g. EnemyStats, WeaponStats), item definitions, wave/config data, global settings. Used by scripts at runtime; no scene-specific data here. Organize by domain (Combat, Inventory, Enemies, etc.) if the list grows.

### Scripts/

- **Purpose:** All C# gameplay and engine code. **Namespaces match subfolder names** (e.g. `Braziliation.Player`, `Braziliation.Combat`).

  - **Core/** – Bootstrap and engine-level systems. E.g. GameInitializer, CameraScaler, global settings. No game logic; only startup, camera, and project-wide config. Namespace: `Braziliation.Core`.

  - **Player/** – Player controller and abilities. Movement, jump, dash, interact, and any player-specific state. Namespace: `Braziliation.Player`.

  - **Enemies/** – Enemy AI and behaviors. Per-type scripts (patrol, chase, attack) and shared enemy logic. Namespace: `Braziliation.Enemies`.

  - **Combat/** – Damage, health, weapons, hit reactions. Interfaces such as IDamageable; systems that resolve hits and apply damage. Namespace: `Braziliation.Combat`.

  - **Inventory/** – Items, equipment, and inventory UI logic (if not purely in UI). Item definitions can reference ScriptableObjects. Namespace: `Braziliation.Inventory`.

  - **World/** – Level logic, hazards, interactables, checkpoints, triggers. Environment and level flow, not player or enemy internals. Namespace: `Braziliation.World`.

  - **UI/** – Menus, HUD, dialogs, and UI controllers. Presentation and input wiring for UI; minimal game logic. Namespace: `Braziliation.UI`.

  - **Utils/** – Shared utilities, extensions, and helpers. E.g. math, serialization, debug tools. No domain-specific game logic. Namespace: `Braziliation.Utils`.

Existing Scripts subfolders (e.g. Tools) can remain and be gradually merged into this layout (e.g. Tools → Utils or domain folders) to avoid breaking existing references.

### Settings/

- **Purpose:** (Existing) URP, Renderer2D, scene templates, and other project-wide settings.
- **Contents:** No change required; keep as-is for Unity and pipeline config.

---

## Adopting this structure

- **New scripts:** Place in the appropriate Scripts subfolder and use the matching namespace.
- **Existing scripts:** Move gradually; update namespaces and any references (including in scenes/prefabs).
- **New prefabs:** Store in Prefabs/ with clear names (e.g. Enemy_Crawler, Player).
- **New design-time data:** Use ScriptableObjects/ and reference from scripts.

This structure is the **recommended** layout; it does not require deleting or breaking existing Assets. Merge and rename as needed while keeping the project stable.
