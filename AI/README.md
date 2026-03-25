# AI-Assisted Development – Braziliation

This folder supports **AI-assisted development** in Cursor: agent roles, context, prompt templates, and shared memory so that you and AI agents work in a consistent, scalable way.

## Folder structure

| Folder      | Purpose |
|------------|---------|
| **Agents/** | Role definitions (Tech Lead, Architect, Unity Engineer, Gameplay Engineer, QA). Use these to “become” a role in the chat. |
| **Context/** | Game vision, art direction, coding standards. Reference in prompts so the model stays on-theme and on-standards. |
| **Prompts/** | Reusable prompt templates (create feature, refactor, review, design enemy). Copy into Cursor and fill in. |
| **Memory/** | Shared memory: architecture decisions (ADRs), roadmap, tech debt. Update as the project evolves. |

## How to use Cursor agents for this project

1. **Set the role** – At the start of a task, tell Cursor to adopt a role by referencing the right agent file, e.g. “You are the Tech Lead for Braziliation. Follow the role and responsibilities in `AI/Agents/tech_lead.md`.”
2. **Add context** – For design or code tasks, attach or mention `AI/Context/game_vision.md`, `AI/Context/coding_standards.md`, or `Docs/Architecture/AssetsStructure.md` so answers stay aligned with the project.
3. **Use templates** – For features, refactors, or reviews, open the matching file under `AI/Prompts/`, copy the template, fill in the bracketed parts, and paste into the chat.
4. **Keep memory updated** – When you or an agent make a structural decision, add an ADR to `AI/Memory/architecture_decisions.md`. When you notice tech debt, add it to `AI/Memory/tech_debt.md`. Keep `AI/Memory/roadmap.md` in sync with priorities.
5. **One role per thread** – For complex work, use one agent role per conversation (e.g. Architect for structure, then Gameplay Engineer for implementation) to avoid mixed instructions.

## Example prompts: how to call each agent

Use these in Cursor chat. You can @-mention the agent file or paste its path so the model loads the role.

---

### Tech Lead

- *“Act as the Tech Lead for Braziliation. Read `AI/Agents/tech_lead.md` and follow it. I want to add a save system: what should we document first, and where should the code live?”*
- *“You are the Tech Lead (see AI/Agents/tech_lead.md). Review our current Scripts folder structure and suggest how to align it with Docs/Architecture/AssetsStructure.md without breaking existing scenes.”*

---

### Architect

- *“Act as the Architect for Braziliation (AI/Agents/architect.md). Propose a combat system: which components, which interfaces (e.g. IDamageable), and where they live under Assets/Scripts.”*
- *“You are the Architect. We’re adding an inventory. Define the boundaries between Inventory, UI, and World; suggest namespaces and one ADR for AI/Memory/architecture_decisions.md.”*

---

### Unity Engineer

- *“Act as the Unity Engineer (AI/Agents/unity_engineer.md). Implement a simple pause menu that freezes time and shows a panel, using the existing Input System and UI.”*
- *“You are the Unity Engineer. Our pixel camera is 320×180 at 16 PPU. Add a script that keeps the player within the visible play area and suggest where to put it in Assets/Scripts.”*

---

### Gameplay Engineer

- *“Act as the Gameplay Engineer (AI/Agents/gameplay_engineer.md). Implement double jump using the existing input actions and movement script. Follow Docs/Mechanics/player_controls.md if it exists, or propose the rule.”*
- *“You are the Gameplay Engineer. Use the template in AI/Prompts/design_enemy.md to design and implement a basic ‘Crawler’ enemy: patrol, chase, melee contact damage. Reference Docs/Lore for tone.”*

---

### QA Engineer

- *“Act as the QA Engineer (AI/Agents/qa_engineer.md). Review the player movement script in Assets/Scripts/ for edge cases, null safety, and alignment with AI/Context/coding_standards.md.”*
- *“You are the QA Engineer. I added a new weapon. List acceptance criteria and test cases (happy path + edge cases) and suggest one entry for AI/Memory/tech_debt.md if you see debt.”*

---

## Quick reference: when to use which agent

| Need | Prefer |
|------|--------|
| Direction, standards, doc updates | Tech Lead |
| System boundaries, interfaces, ADRs | Architect |
| Unity setup, input, camera, editor tools | Unity Engineer |
| Player, enemies, combat, world logic | Gameplay Engineer |
| Review, test cases, tech debt list | QA Engineer |

For **new features**, start with Tech Lead or Architect if the feature touches structure; then use Gameplay or Unity Engineer for implementation. For **reviews**, use QA Engineer or Tech Lead.
