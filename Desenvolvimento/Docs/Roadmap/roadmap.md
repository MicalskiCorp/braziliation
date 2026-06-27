# Roadmap – Braziliation

High-level roadmap for technical and content work. Update as priorities change. Link to external tools (e.g. ClickUp) if used.

## Phase: Foundation (current)

- [x] Unity 6 + URP 2D + Pixel Perfect (320×180, 16 PPU)
- [x] GameInitializer, CameraScaler
- [x] Input System setup
- [x] Recommended Assets/Scripts structure adopted (see Docs/Architecture/AssetsStructure.md)
- [x] Core player movement (run, jump) and basic collision
- [x] Basic combat (health, damage, one weapon type)
- [x] One playable level (blockout + placeholders)

Status note (2026-05-31): a base da demo foi consolidada com cena fixa em Assets/Scenes/DemoGameplay.unity e bootstrap de runtime/editor.

## Phase: Gameplay loop

- [ ] Full player moveset per GDD (dash, interact, etc.)
- [ ] 2–3 enemy types with distinct behaviors
- [ ] Checkpoints / respawn
- [ ] Basic UI (HUD, main menu, pause)
- [ ] First pass at feel (juice, feedback, sound)

## Phase: Content and polish

- [ ] Multiple levels or areas
- [ ] Inventory/items if in scope
- [ ] Lore and narrative hooks in-world
- [ ] Balance and difficulty tuning
- [ ] Performance and platform checks (e.g. target build)

## Phase: Release prep

- [ ] Save system (if required)
- [ ] Options (audio, controls)
- [ ] Credits and legal
- [ ] Build pipeline and versioning (see scripts/update_version.ps1)

---

*Update this file when committing to a new phase or when the solo dev or Tech Lead reprioritizes. Link to Docs/GDD/ for feature details.*
