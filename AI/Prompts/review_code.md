# Prompt Template: Review Code

Use this template when asking the **QA Engineer** or **Tech Lead** to review code for correctness, edge cases, and alignment with standards.

## Copy-paste template

```
Role: [QA Engineer | Tech Lead]

Please review the following:

**Scope:** [File(s) or PR/feature name]

**Context:** [What this code does – 1–2 sentences]

**Concerns (optional):**
- [e.g. "Worried about null refs in spawn path", "Does this match GDD for double jump?"]

Please:
1. Check for edge cases, null safety, and input validation.
2. Verify alignment with AI/Context/coding_standards.md and Docs/Architecture.
3. Suggest acceptance criteria or test cases if this is a new feature.
4. Note any items for AI/Memory/tech_debt.md.
```

## What reviewers should look for

- **Correctness:** Logic matches GDD/Mechanics; no obvious bugs.
- **Robustness:** Null checks, bounds checks, invalid input handling.
- **Conventions:** Namespaces, naming, single responsibility.
- **Performance:** No heavy work in Update; appropriate use of physics and events.
- **Documentation:** Public API and non-obvious parameters documented.

Use **AI/Agents/qa_engineer.md** for the QA perspective; use **AI/Agents/tech_lead.md** for technical direction and standards.
