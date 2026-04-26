---
description: "Refatorar um sistema existente no Braziliation: reduzir acoplamento, alinhar com arquitetura, melhorar performance ou preparar para nova feature. Use com @Architect para plano estrutural ou @TechLead para priorização."
argument-hint: "Sistema a refatorar (ex: 'PlayerMovement', 'Combat damage flow', 'Enemy spawner')"
agent: agent
tools: [read, edit, search, todo]
---
Refatore o sistema abaixo no Braziliation. Preencha todos os campos antes de enviar.

**Sistema/área:** [ex: movimento do player, fluxo de dano em combate, spawner de inimigos]

**Localização atual:** [Caminhos ou nomes dos scripts/assets principais]

**Objetivos:**
- [ ] Reduzir acoplamento / clarificar limites
- [ ] Melhorar performance
- [ ] Alinhar com `Desenvolvimento/Docs/Architecture/` e estrutura recomendada de Assets
- [ ] Preparar para [nova feature X]
- [ ] Outro: ___

**Não-objetivos (não alterar):**
- [ex: "Não alterar bindings de input", "Não renomear API pública usada pela UI"]

**Restrições:**
- [ex: "Sem novas dependências", "Manter prefabs existentes funcionando"]

---

Ao processar este prompt:
1. Proponha um plano de refactor (passos, ordem, risco).
2. Liste arquivos a criar, mover ou modificar.
3. Se a mudança for estrutural, sugira um ADR em `Desenvolvimento/Docs/Architecture/architecture_decisions.md`.
4. Registre qualquer tech debt identificado em `Desenvolvimento/Docs/Tech/tech_debt.md`.

**Agentes por escopo:**
- `@Architect` — "como deve ser dividido?" e decisões de limite
- `@TechLead` — "vale a pena refatorar?" e atualização de docs/ADR
- `@UnityEngineer` / `@GameplayEngineer` — código concreto e mudanças de prefab
