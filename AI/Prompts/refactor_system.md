# Prompt Template: Refactor System

Use this template when asking an agent to **refactor an existing system** (e.g. player controller, combat, spawners) for clarity, performance, or alignment with architecture.

## Copy-paste template

```
Role: [Tech Lead | Architect | Unity Engineer | Gameplay Engineer]

I want to refactor the following:

**System/area:** [e.g. Player movement, Combat damage flow, Enemy spawner]

**Current location:** [Paths or names of main scripts/assets]

**Goals:**
- [ ] Reduce coupling / clarify boundaries
- [ ] Improve performance
- [ ] Align with Docs/Architecture and recommended Assets structure
- [ ] Prepare for [new feature X]
- [ ] Other: ___

**Non-goals (do not change):**
- [e.g. "Do not change input bindings", "Do not rename public API used by UI"]

**Constraints:**
- [e.g. "No new dependencies", "Keep existing prefabs working"]

Please:
1. Propose a refactor plan (steps, order, risk).
2. List files to create, move, or modify.
3. Suggest an ADR in AI/Memory/architecture_decisions.md if the change is structural.
4. Note any tech debt to add to AI/Memory/tech_debt.md.
```

## Tips

- **Architect** is best for “how should this be split?” and boundary decisions.
- **Tech Lead** is best for “is this refactor worth it?” and doc/ADR updates.
- **Unity/Gameplay Engineer** is best for concrete code and prefab changes.

Check **AI/Memory/tech_debt.md** and **AI/Memory/architecture_decisions.md** before and after the refactor.
