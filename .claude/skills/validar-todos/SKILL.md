---
name: validar-todos
description: Audita se os TODOs marcados como concluídos no Braziliation estão de fato implementados, testados e documentados; varre TODOs inline não rastreados e mapeia gaps da milestone. Use quando o usuário pedir para auditar projeto, validar TODOs, verificar cobertura de testes ou "o que falta para a demo".
context: fork
agent: agent-architect
---

# Skill: validar-todos

Protocolo canônico do **Papel 3 (Auditoria)** do `@AgentArchitect` — roda num fork desse agente, que também a pré-carrega. Objetivo: o estado real do código corresponde ao que os TODOs dizem, e nenhum ponto incompleto fica sem registro.

## A — Contexto

Ler: `Desenvolvimento/Docs/TODO.md`, `Docs/Roadmap/roadmap.md`, `Docs/Roadmap/backlog.md`, `Docs/Architecture/Sistemas/index.md` (cada ficha lista seus scripts) e `.claude/state/unity-validar.json`. Código e testes **não** são lidos em bloco: `Glob` lista, `Grep` acha (`// TODO`, classe, teste) e só então o arquivo é aberto.

## B — Itens dados como concluídos

Para cada item ✅ no backlog, no roadmap ou num TODO:

- o `.cs` existe e compila?
- há teste cobrindo o comportamento principal?
- está integrado (`GameServiceLocator`, Inspector) ou há pendência de wiring registrada?
- há `// TODO` ou `// TODO-DESIGN` sem rastreio?

Aprovado só com as quatro respostas satisfeitas; senão, parcial ou reprovado.

## C — Cobertura de testes

"Todo `*Service.cs` tem `{Nome}Tests.cs`" já é teste (`ConventionGuardTests`) — não conferir à mão. Julgar o resto em `src/Braziliation.Game.Core/`: todo modelo com lógica (`BuildState`, `HybridSynergyResolver`…) tem teste; modelo só de dados (`SaveSlot`, `SlotData`) é opcional. O CI roda `Tests/Braziliation.Game.Tests/` direto; o lado Unity é validado pela skill `unity-validar`.

Saída: `Classe | Tem teste? | Arquivo de teste | Gap`.

## D — Gaps da milestone

Comparar o estado real com a fase atual do `roadmap.md`. Item da milestone sem TODO → criar na seção da área. Classificar:

| Categoria | Critério | Urgência |
|-----------|---------|----------|
| Bloqueador de demo | Sem isso a demo não é jogável | Crítico |
| Funcionalidade incompleta | Marcada ✅ com partes faltando | Alta |
| Cobertura ausente | Classe testável sem teste | Alta |
| CI desincronizado | Checagem que roda local mas não no CI (ou o inverso) | Alta |
| TODO inline não rastreado | `// TODO` sem entrada no TODO | Média |
| Design pendente bloqueador | `TODO-DESIGN` que bloqueia gameplay | Média |
| Documentação desatualizada | Status no backlog ou TODO diverge do código | Baixa |

## E — Retroalimentação obrigatória

`py .claude/skills/validar-todos/todos_inline.py` lista todos os `// TODO` e `// TODO-DESIGN` do código já classificados: rastreado pelo arquivo, rastreado pelo domínio (a ficha ou mecânica do sistema é citada no TODO) ou **NÃO**. Só os "NÃO" pedem decisão; os que forem pendência real ganham entrada pela skill `gerir-todo`:
`| {ponto faltante, extraído do comentário} | {arquivo} | @{agente} | {prioridade} | ❌ Não iniciado |`

## F — Relatório

```
## Relatório de Auditoria — {data}

### Resumo
- TODOs verificados: {N} ✅ aprovados / {N} ⚠️ parciais / {N} ❌ reprovados
- Classes sem teste: {lista}
- Checagens fora do CI: {lista}
- TODOs inline não rastreados: {N}
- Gaps bloqueadores de demo: {lista}

### Ações geradas
- {N} TODOs novos · {N} status corrigidos · {N} TODOs inline agora rastreados

### Próxima ação recomendada
@{Agente}: {comando exato}
```

## Regras

- A auditoria **escreve TODOs e corrige status**; não implementa nem corrige código.
- Nenhum ponto faltante encontrado fica sem registro.
