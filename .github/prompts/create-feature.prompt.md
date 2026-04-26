---
description: "Criar uma nova feature no Braziliation: definir design, documentação necessária e implementação. Use com @TechLead para features que tocam estrutura, ou @GameplayEngineer / @UnityDeveloper para implementação direta."
argument-hint: "Nome da feature (ex: 'Double Jump', 'Sistema de Inventário', 'Checkpoint')"
agent: agent
tools: [read, edit, search, todo]
---
Crie a feature abaixo para o projeto Braziliation. Preencha todos os campos antes de enviar.

**Nome:** [Nome curto da feature]

**Resumo:** [1–2 frases: o que o jogador vê/faz]

**Origem:** [Seção do GDD / Docs/Mechanics / nenhuma — descreva se nenhuma]

**Escopo:**
- [ ] Comportamento visível ao jogador
- [ ] Novo sistema (ex: inventário, save)
- [ ] Novos assets (arte, áudio)
- [ ] Apenas UI
- [ ] Outro: ___

**Restrições:**
- [ex: "deve funcionar com o input map existente", "sem novas cenas"]

**Critérios de aceite (quando está pronto?):**
1.
2.
3.

---

Ao processar este prompt:
1. Confirme quais docs criar/atualizar (`Docs/GDD/`, `Docs/Mechanics/`, `Docs/Architecture/`).
2. Proponha ou implemente a mudança (arquivos, components, ScriptableObjects).
3. Aponte qualquer tech debt ou trabalho de follow-up para `Desenvolvimento/Docs/Tech/tech_debt.md`.
4. Se a feature introduzir novos limites de sistema, sugira ADR em `Desenvolvimento/Docs/Architecture/architecture_decisions.md`.

**Agentes por escopo:**
- Estrutura / limites: `@Architect`
- Mecânica de gameplay: `@GameplayEngineer`
- Setup Unity / Input / câmera: `@UnityEngineer`
- UI / ServiceLocator / MonoBehaviours: `@UnityDeveloper`
- Sistemas C# puros: `@SystemsDeveloper`
