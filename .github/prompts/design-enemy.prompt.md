---
description: "Desenhar e implementar um novo tipo de inimigo no Braziliation: comportamento, stats, state machine, ScriptableObject e prefab. Use com @GameplayEngineer para implementação ou @Architect para definir interfaces."
argument-hint: "Nome do inimigo (ex: 'Crawler', 'Brumoso', 'Guardião da Fábrica')"
agent: agent
tools: [read, edit, search, todo]
---
Desenhe e/ou implemente o inimigo abaixo para o Braziliation. Preencha todos os campos.

**Nome:** [Nome do inimigo ou codinome]

**Lore/cenário:** [Onde se encaixa no mundo — referência a Docs/Lore/ se possível]

**Comportamento:**
- Movimento: [ex: patrol, chase, estático]
- Ataque: [ex: melee, ranged, dano por contato]
- Especial: [ex: spawna minions, buffa outros, ambiental — ou "nenhum"]

**Feel:**
- [ex: "Tanque e lento", "Glass cannon", "Hit-and-run irritante"]

**Referência:** [Inimigo existente ou seção de Docs/Mechanics — ou "nenhuma"]

**Restrições:**
- [ex: "Usa IDamageable existente", "Sem novo input", "Deve funcionar com sistema de combate atual"]

---

Ao processar este prompt:
1. Proponha ou implemente: components, state machine, ScriptableObject de stats, estrutura de prefab.
2. Alinhe com `Desenvolvimento/Docs/Mechanics/` e `.github/instructions/art-direction.instructions.md` (pixel art, dieselpunk).
3. Sugira valores para health, damage, speed como ponto de partida para tuning.
4. Identifique se novas interfaces (`IDamageable`, `IEnemy`) ou sistemas compartilhados são necessários — se sim, sinalize para `@Architect` documentar.
5. Coloque scripts em `Desenvolvimento/Assets/Scripts/Enemies/` com namespace `Braziliation.Enemies`.
