# Game Design Document (GDD) – Braziliation

This folder holds the **Game Design Document** and related design specs for Braziliation.

## Purpose

- Define **vision**, **pillars**, and **target experience** (see also AI/Context/game_vision.md).
- Describe **features**, **modes**, and **content** (levels, characters, items).
- Provide a single source of truth for “what the game is” so implementation and AI agents stay aligned.

## Suggested files

- `vision.md` – High-level pitch, pillars, and target audience.
- `core_loop.md` – Core gameplay loop (e.g. explore → combat → progress → repeat).
- `features.md` – Feature list and priority (MVP vs later).
- `levels.md` – Level/world structure (hub, linear, etc.).
- `characters.md` – Player and key NPCs (brief).
- `content_checklist.md` – Tracks which content is designed vs implemented.

## Usage

- **Gameplay Engineer** and **Tech Lead** should reference GDD when implementing or reviewing features.
- Update GDD when design decisions change; keep AI/Context/game_vision.md in sync for high-level direction.
