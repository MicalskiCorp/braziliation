# Architecture Decision Records (ADRs) – Braziliation

This file records **significant architecture and structure decisions** so future work and AI agents stay consistent.

Format per entry:
- **Title:** Short name
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Deprecated
- **Context:** What problem or option we faced
- **Decision:** What we chose
- **Consequences:** Trade-offs, follow-ups

---

## ADR-001: Unity 6 + URP 2D + 320×180 @ 16 PPU

- **Date:** (fill when accepted)
- **Status:** Accepted
- **Context:** Need stable resolution and pixel-perfect rendering for SNES-style pixel art.
- **Decision:** Use Unity 6, URP 2D, reference resolution 320×180, 16 pixels per unit. CameraScaler and GameInitializer enforce this.
- **Consequences:** All art and tiles must be authored for 16 PPU; scaling handled by pipeline. Documented in `.github/instructions/art-direction.instructions.md`.

---

## ADR-002: Input System (com.unity.inputsystem)

- **Date:** (fill when accepted)
- **Status:** Accepted
- **Context:** Modern input with actions and rebinding; replace legacy Input Manager.
- **Decision:** Use com.unity.inputsystem; single Input Actions asset (e.g. InputSystem_Actions.inputactions) for player and UI.
- **Consequences:** All player and UI input goes through action maps; no direct Input.GetKey in gameplay code.

---

## ADR-003: Recommended Assets/Scripts layout

- **Date:** (fill when accepted)
- **Status:** Proposed
- **Context:** Scalable structure for Core, Player, Enemies, Combat, Inventory, World, UI, Utils.
- **Decision:** Document and adopt folder layout under Assets/Scripts/ as in Docs/Architecture/AssetsStructure.md. Namespaces match folders.
- **Consequences:** New scripts go in the correct subfolder; existing Core, Tools, UI can be merged into this layout over time.

---

*(Add new ADRs below. Keep entries short and link to Docs/Architecture or code when relevant.)*
