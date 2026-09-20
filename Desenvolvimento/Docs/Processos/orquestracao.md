# Orquestração

> Transversal · Fonte canônica: [`agent-architect.md`](../../../.claude/agents/agent-architect.md) · skills [`validar-todos`](../../../.claude/skills/validar-todos/SKILL.md), [`structure-audit`](../../../.claude/skills/structure-audit/SKILL.md), [`novo-agente`](../../../.claude/skills/novo-agente/SKILL.md) · [`processos.md`](../Tech/processos.md). Este manual resume; em divergência, vale a fonte.

Dono **@AgentArchitect** · Mapa **AGENTS.md** · Detalhe **Docs/Tech/processos.md**

Não produz conteúdo de nenhuma camada: abre sessões, distribui trabalho, audita o que foi dado como pronto e mantém o ecossistema de agentes e as travas automáticas.

## O1 — Sessão de desenvolvimento

**Quem:** @AgentArchitect · Papel 1
**Aciona:** "sessão de desenvolvimento", "próximas tarefas", "distribuir tarefas"

1. Ler o TODO de Dev, o roadmap e a tabela do `AGENTS.md` — sem abrir o corpo dos agentes.
2. Classificar cada pendência: C# puro, mecânica, UI/wiring, testes, QA, documentação, direção técnica, criativo, pesquisa, design pendente.
3. Para cada uma: agente principal, secundários, bloqueadores e ordem de dependência.
4. Emitir um comando por agente (tarefa, referência, dependências, prioridade); todo código testável leva uma tarefa do @TestEngineer antes.
5. Na sessão seguinte, consolidar entregas contra os ADRs e o roadmap.
6. Fechar com "Próxima Ação": situação, próximo passo, agente e comando exato.

- **Não faz:** Não invoca os agentes — o usuário aciona cada um

## O2 — Auditoria de TODOs e cobertura

**Quem:** @AgentArchitect · Papel 3 · skill `validar-todos` (protocolo canônico)
**Aciona:** "auditar projeto", "o que falta para a demo", "cobertura de testes"

1. Contexto: TODO, roadmap, backlog, índice de sistemas, último `unity-validar`; código só por Glob e Grep.
2. Cada item dado como feito: arquivo existe e compila? tem teste? está integrado? tem `// TODO` sem rastreio?
3. Cobertura: todo `*Service.cs` e modelo com lógica precisa de teste.
4. `todos_inline.py` classifica os `// TODO` (arquivo, domínio ou sem rastreio); só os sem rastreio pedem decisão e ganham entrada.
5. Gaps da milestone classificados (bloqueador de demo, incompleto, cobertura, CI, TODO inline, design, doc).
6. Relatório com aprovados, parciais, reprovados, ações geradas e próxima ação.

- **Regra:** Escreve TODO e corrige status; não implementa

## O3 — Auditoria de estrutura

**Quem:** skill `structure-audit` · @AgentArchitect (nível 4) · @GameArchitect (2-3)

1. Nível 1 — `Assets/` × `AssetsStructure.md` e sprites sem registro em `assets.md`.
2. Nível 2 — Design: pastas de `IA/`, guias listados no índice, paletas com status.
3. Nível 3 — Documentação: arquivos listados nos índices, links válidos.
4. Nível 4 — Agentes: wrappers da 1ª camada (o registro no `AGENTS.md` já é teste).
5. Nível 5 — Skills apontam para docs que existem e estão no catálogo.
6. Relatório com gaps por nível; corrigir só após aprovação.

- **Já automático:** Registro de agentes, catálogo, links e índice de scripts são testes

## O4 — Criar ou atualizar agente

**Quem:** @AgentArchitect · Papel 2 · skill `novo-agente`

1. Inventário pela tabela do `AGENTS.md` e as `description:`; ≥50% de sobreposição → estender o existente.
2. Definir limites: o que possui, o que delega.
3. Propor antes de criar; confirmar em sobreposição alta.
4. Escrever `.claude/agents/{nome}.md`; em `skills:` só a skill de toda invocação.
5. `name` igual ao arquivo e `model:` obrigatório.
6. Registrar no `AGENTS.md` (o `AgentDefinitionTests` cobra); wrapper da 1ª camada fora do repositório.

- **Gate:** Nome = arquivo, `model:` e registro no `AGENTS.md` · prompt até 5 mil tokens

## O5 — Travas automáticas

**Quem:** Hooks · pre-commit · CI

1. Início de sessão: `session_snapshot.py` injeta git, pendências Alta dos 3 TODOs e o último `unity-validar`.
2. Antes de escrever: `block_generated_dirs.py` bloqueia `Library/`, `Temp/`, `obj/`, `bin/`, o histórico congelado `TODO-arquivo.md` e a DLL do core.
3. Depois de escrever: `build_game_core.py` recompila o core.
4. Antes do commit: `dotnet test` com as guardas (`DocsConsistency`, `TokenBudget`, `ConventionGuard`, `AgentDefinition`, `GitIgnoreGuard`, `UnityAssetConsistency`, `RepositoryLayout`), meta-check e paletas **contra o índice do git** (`check_clean_checkout.py`) e o gate do Unity (script em stage exige validação OK posterior à edição).
5. No push: CI repete tudo. Os hooks do Git LFS — versionados em `.githooks/` desde 19 set 2026 — sobem os objetos; sem o `pre-push`, um push publica ponteiros sem os binários.

- **Princípio:** Regra que só está escrita envelhece; regra testada, não
- **Ponto cego fechado em 19 set 2026:** trava que olha a árvore de trabalho não vê o que o CI vê. Duas pastas de arte vazias com `.meta` versionado derrubaram o CI por seis dias enquanto o meta-check local aprovava todo commit. Os gates passaram a rodar contra o índice materializado — detalhe em [`processos.md` §8.1](../Tech/processos.md)

---

[← Manual de processos](index.md)
