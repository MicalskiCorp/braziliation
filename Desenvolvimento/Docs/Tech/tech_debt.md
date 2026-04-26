# Tech Debt – Braziliation

Known technical debt, shortcuts, and follow-up work. Use this so agents and the developer don’t forget and so refactors are prioritized.

Format:
- **Item:** Short description
- **Where:** Path or system
- **Why:** Reason it exists or why it’s debt
- **Fix (optional):** Suggested direction

---

## Current items

*(None yet. Add as you or agents identify debt.)*

**Example:**
- **Item:** Player movement and jump in one large script
- **Where:** Assets/Scripts/Player/PlayerController.cs
- **Why:** Quick prototype; now hard to extend (dash, double jump).
- **Fix:** Split into PlayerMovement, PlayerJump, and optional PlayerAbilities; use same input actions.

---

*QA Engineer and Tech Lead can add items when reviewing code or after refactors. Remove or mark “Done” when addressed.*
