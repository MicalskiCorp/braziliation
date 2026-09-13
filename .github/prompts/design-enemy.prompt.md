---
description: "Desenhar e implementar um novo tipo de inimigo no Braziliation: comportamento, stats, state machine, ScriptableObject e prefab. Use com @GameplayEngineer para implementação ou @TechLead para definir interfaces. No Claude Code, prefira a skill novo-inimigo."
argument-hint: "Nome do inimigo (ex: 'Crawler', 'Brumoso', 'Guardião da Fábrica')"
agent: agent
tools: [read, edit, search, todo]
---
Desenhe e/ou implemente o inimigo abaixo para o Braziliation. Preencha todos os campos.

**Nome:** [Nome do inimigo ou codinome]

**Lore/cenário:** [Onde se encaixa no mundo — referência à cidade em `Design/Criativo/Estados/` ou à lenda em `Design/Criativo/Lendas/`]

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
1. **Inimigo novo é dado, não código:** o motor `EnemyBrain` (`src/Braziliation.Game.Core/Enemies/`) é genérico. Defina um `EnemyBehaviorProfile` (números + `EnemyAggressionStyle`) e crie o `EnemyProfileAsset` correspondente em `Assets/ScriptableObjects/Enemies/`. Só escreva código se o comportamento não couber em nenhum estilo existente — e então proponha o estilo novo ao `@TechLead`.
2. Alinhe com `Desenvolvimento/Docs/Mechanics/InimigosIA.md` e `.github/instructions/art-direction.instructions.md` (pixel art, dieselpunk).
3. Sugira valores para vida, dano e velocidade como ponto de partida para tuning, e registre o perfil na tabela de `InimigosIA.md`.
4. Adicione um caso em `Tests/Braziliation.Game.Tests/EnemyBrainTests.cs` que fixe o comportamento esperado do perfil.
5. Se precisar de interface nova (`IDamageable`, `IEnemy`) ou sistema compartilhado, sinalize para `@TechLead`.
