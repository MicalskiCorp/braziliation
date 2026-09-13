---
name: validar-todos
description: Audita se os TODOs marcados como concluídos no Braziliation estão de fato implementados, testados e documentados; varre TODOs inline não rastreados e mapeia gaps da milestone. Use quando o usuário pedir para auditar projeto, validar TODOs, verificar cobertura de testes ou "o que falta para a demo".
context: fork
agent: agent-architect
---

# Skill: validar-todos

Executa o **Papel 3 (Auditoria)** do `@AgentArchitect` — protocolo canônico completo em `.claude/agents/agent-architect.md` (idêntico em `.github/agents/AgentArchitect.agent.md`), seção "PAPEL 3". Esta skill é o roteiro executável; em divergência, o protocolo canônico manda.

## Roteiro

1. **Contexto** (ler antes de tudo): `Desenvolvimento/Docs/TODO.md`, `Docs/Roadmap/roadmap.md`, `Docs/Roadmap/backlog.md`.
2. **Auditar itens "✅ Concluído"** — para cada um: o arquivo `.cs` existe? tem teste cobrindo o comportamento principal? está integrado (ServiceLocator/Inspector) ou tem TODO de wiring rastreado? tem `// TODO` inline não rastreado?
3. **Cobertura de testes** — varrer `src/Braziliation.Game.Core/`: todo `*Service.cs` e modelo com lógica precisa de teste. O CI roda direto `Desenvolvimento/Tests/Braziliation.Game.Tests/` — não existe cópia paralela de testes para sincronizar (o `RepositoryLayoutTests` impede a volta da pasta antiga). Para o lado Unity, conferir o resultado da skill `unity-validar` (compilação + EditMode).
4. **TODOs inline** — `Grep` por `// TODO` e `// TODO-DESIGN` em `src/` e `Assets/Scripts/`; cada um sem entrada no `TODO.md` gera entrada nova imediatamente (regra de retroalimentação obrigatória).
5. **Gaps de milestone** — comparar estado real com a milestone ativa do roadmap; classificar: Bloqueador de Demo / Funcionalidade Incompleta / Cobertura Ausente / CI Desincronizado / TODO Inline Não Rastreado / Design Pendente / Doc Desatualizada.
6. **Relatório** — usar o formato "Relatório de Auditoria" do protocolo canônico: resumo (aprovados/parciais/reprovados), ações geradas (TODOs criados, status corrigidos) e próxima ação recomendada com agente e comando exato.

## Regras

- Auditoria **escreve TODOs e corrige status**, mas não implementa nem corrige código.
- Nenhum ponto faltante encontrado pode ficar sem registro no `TODO.md`.
