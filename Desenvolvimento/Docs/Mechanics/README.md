# Mechanics – Braziliation

This folder holds **concrete game mechanics**: rules, numbers, and behavior specs that implementation must follow.

## Purpose

- Define **how** systems work (movement, combat, inventory, etc.) in enough detail to implement and tune.
- Serve as the **contract** between design and code; QA and agents use it to verify behavior.
- Complement **GDD** (what the game is) with **Mechanics** (how it plays).

## Suggested files

- `README.md` (this file) – Overview.
- `player_controls.md` – Movement, jump, dash, interact; input mapping references.
- `combat.md` – Damage types, health, knockback, invulnerability, weapon behavior.
- `enemies.md` – General enemy rules (e.g. damage reaction, aggro); per-type details can live in GDD or design docs.
- `world_rules.md` – Hazards, checkpoints, death/respawn, interactables.
- `inventory.md` – (If in scope) Item types, slots, use behavior.

## Usage

- **Gameplay Engineer** implements to match these docs; propose updates when behavior is undefined or wrong.
- **QA Engineer** uses mechanics as acceptance criteria.
- **Tech Lead** and **Architect** keep mechanics aligned with architecture (e.g. who owns damage, who owns respawn).
