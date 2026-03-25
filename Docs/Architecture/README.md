# Architecture – Braziliation

This folder holds **technical architecture** documentation: system boundaries, data flow, and recommended project structure.

## Purpose

- Define **module boundaries**: Core, Player, Enemies, Combat, Inventory, World, UI, Utils.
- Document **data flow** and dependencies (who calls whom, events, interfaces).
- Describe **recommended Unity project structure** (see AssetsStructure.md).
- Support **AI agents** and future developers with a clear “map” of the codebase.

## Suggested files

- `README.md` (this file) – Overview and index.
- `AssetsStructure.md` – Recommended layout under Assets/ and what each folder contains.
- `systems_overview.md` – High-level system map and dependencies.
- `data_flow.md` – Input → Player → Combat → World → UI (to be filled as systems are added).

## Usage

- **Architect** and **Tech Lead** maintain these docs.
- **Unity Engineer** and **Gameplay Engineer** place new code according to AssetsStructure.md and system boundaries.
- **ADR** entries for big structural decisions live in AI/Memory/architecture_decisions.md.
