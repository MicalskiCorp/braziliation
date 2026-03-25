# Prompt Template: Create Feature

Use this template when asking an agent (Tech Lead, Architect, Gameplay Engineer, or Unity Engineer) to **design and/or implement a new feature**.

## Copy-paste template

```
Role: [Tech Lead | Architect | Gameplay Engineer | Unity Engineer]

I want to add the following feature:

**Name:** [Short feature name]

**Summary:** [1–2 sentences: what the player sees/does]

**Source:** [GDD section / Mechanics doc / none – describe if none]

**Scope:**
- [ ] Player-facing behavior
- [ ] New systems (e.g. inventory, save)
- [ ] New assets (art, audio)
- [ ] UI only
- [ ] Other: ___

**Constraints:**
- [Any technical or design constraints, e.g. "must work with existing input map", "no new scenes"]

**Acceptance criteria (when is it done?):**
1. 
2. 
3. 

Please:
1. Confirm which docs to create/update (GDD, Mechanics, Architecture).
2. Propose or implement the change (files, components, ScriptableObjects).
3. Call out any tech debt or follow-up work.
```

## Tips

- **Tech Lead:** Use for cross-cutting features or when you need direction and doc updates.
- **Architect:** Use when the feature introduces new systems or boundaries.
- **Gameplay Engineer:** Use for player mechanics, enemies, combat, items, world logic.
- **Unity Engineer:** Use for engine setup, input, camera, or editor tooling.

Always reference **AI/Context/game_vision.md** and **Docs/GDD/** or **Docs/Mechanics/** when the feature touches design.
