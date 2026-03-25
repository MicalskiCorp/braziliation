# Prompt Template: Design Enemy

Use this template when asking the **Gameplay Engineer** or **Architect** to **design and/or implement a new enemy type** for Braziliation.

## Copy-paste template

```
Role: [Gameplay Engineer | Architect]

I want to add a new enemy:

**Name:** [Enemy name or codename]

**Lore/setting:** [Where it fits in the world – reference Docs/Lore/ if possible]

**Behavior (short):**
- Movement: [e.g. patrol, chase, static]
- Attack: [e.g. melee, ranged, contact damage]
- Special: [e.g. spawns minions, buffs others, environmental]

**Feel:**
- [e.g. "Tanky and slow", "Glass cannon", "Annoying hit-and-run"]

**Reference:** [Existing enemy or Doc/Mechanics section – or "none"]

**Constraints:**
- [e.g. "Uses existing IDamageable", "No new input", "Must work with current combat system"]

Please:
1. Propose or implement: components, state machine, ScriptableObject (stats), prefab structure.
2. Align with Docs/Mechanics and AI/Context/art_direction.md (pixel art, dieselpunk).
3. Suggest values for health, damage, speed as starting points for tuning.
4. Call out any new interfaces or shared systems needed (and whether Architect should document them).
```

## Tips

- **Gameplay Engineer** implements behavior and tuning.
- **Architect** defines interfaces (e.g. `IDamageable`, `IEnemy`) and where the enemy fits in the system map.
- Always consider **Docs/Lore/** for tone and naming so enemies feel part of the world.
