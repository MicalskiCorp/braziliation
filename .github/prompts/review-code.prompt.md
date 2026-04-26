---
description: "Revisar código do Braziliation: edge cases, null safety, alinhamento com padrões, acceptance criteria e tech debt. Use com @QAEngineer para revisão técnica ou @TechLead para direção e standards."
argument-hint: "Arquivo(s) ou feature a revisar (ex: 'PlayerController.cs', 'sistema de dash')"
agent: agent
tools: [read, search, todo]
---
Revise o código abaixo no Braziliation. Preencha todos os campos antes de enviar.

**Escopo:** [Arquivo(s) ou nome do PR/feature]

**Contexto:** [O que este código faz — 1–2 frases]

**Preocupações (opcional):**
- [ex: "Preocupado com null refs no caminho de spawn", "Isso corresponde ao GDD para double jump?"]

---

Ao processar este prompt, verifique:
1. **Edge cases e null safety** — null refs, bounds checks, validação de input.
2. **Alinhamento com padrões** — `.github/instructions/coding-standards.instructions.md` e `Desenvolvimento/Docs/Architecture/`.
3. **Critérios de aceite** — sugira testes ou condições "done when" se for feature nova.
4. **Tech debt** — registre itens em `Desenvolvimento/Docs/Tech/tech_debt.md`.

**O que revisar:**
- **Corretude:** Lógica corresponde ao GDD/Mechanics; sem bugs óbvios.
- **Robustez:** Null checks, bounds checks, input inválido.
- **Convenções:** Namespaces, naming, responsabilidade única.
- **Performance:** Sem lógica pesada em Update; uso correto de physics e events.
- **Documentação:** API pública e parâmetros não-óbvios comentados.

**Agentes:**
- Revisão técnica / edge cases: `@QAEngineer`
- Padrões e direção técnica: `@TechLead`
- Testes automatizados: `@TestEngineer`
