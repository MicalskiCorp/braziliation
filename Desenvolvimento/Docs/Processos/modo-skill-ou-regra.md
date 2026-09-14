# Modo, skill ou regra

> Revisão de 13 set 2026 · Fonte canônica: [`processos.md` §11](../Tech/processos.md). Este manual resume; em divergência, vale a fonte.

Cada modo de cada agente foi avaliado contra um critério único, registrado em `Docs/Tech/processos.md` §11. Nada foi unificado só por semelhança de nome: artefatos distintos continuaram separados, e gatilho que só roteia para um agente não virou skill — o agente já é o ponto de entrada, e cada skill a mais põe sua descrição em toda sessão.

| Vira… | Quando | Exemplo |
|---|---|---|
| Modo do agente | Núcleo do agente, dependente das barreiras e ferramentas dele | Pesquisar tema · Nova feature |
| Um modo com parâmetro | Vários gatilhos, mesmo procedimento, saída diferente | "Pesquisar" e "Fontes sobre" · "Listar" e "Compilar estado" |
| Skill | Usado por mais de um agente, com script ou gate próprio, ou longo e raro | `gerir-todo` · `handoff` · `concept-art` |
| Regra por caminho | Vale sempre que alguém toca um tipo de arquivo | Definição de pronto do código · regras de TODO |
| Script (tool) | Parte determinística: parsear, contar, cruzar — o modelo só lê o resultado | `todo.py` · `todos_inline.py` · `check_state.py` |
| Teste | Invariante verificável — vira falha de build, não item de auditoria | Roteador completo · feature no backlog · serviço com teste · paleta com status |
| Hook | Tem de acontecer sozinho num evento | Foto do projeto na sessão · bloquear arquivo congelado · gate do Unity no commit |
| Skill em fork | Só devolve relatório e leria muito texto — isola o contexto; nunca quando há diálogo no meio | `validar-todos` · `structure-audit` · `hemeroteca-blumenau` |

| Camada | Antes | Depois | O que mudou | O que ficou como estava, e por quê |
|---|---|---|---|---|
| Pesquisa | 7 modos | 4 modos | Fontes → dentro de Pesquisar; Listar + Compilar → Consultar acervo; Brainstorm + Handoff + revisão → um Handoff, com o briefing na skill `handoff` | Pesquisar e Armazenar: são o núcleo e dependem das barreiras do Historiador (web, fonte obrigatória, sem escrita no Criativo) |
| Criativo | 10 modos + `BackLog.md` | 7 modos + `gerir-todo` | Catalogar + Mapear; Cidade + Estado (estrutura na skill `nova-cidade`); duas varreduras → uma; TODO → skill | Ideia, Brainstorm, Arco e Personagem: artefatos e templates diferentes |
| Arte | rota C espalhada em 4 docs | skill `concept-art` | Etapa 2 com pré-voo, log de lote, teto de 3 lotes e aprovação vira roteiro executável | Rota B (tiles/WFC): uso raro, bem coberto pelo guia — sem skill |
| Documentação | 6 modos | 4 modos | Análise de arquivo + pasta; Sincronização dentro da Varredura; Passo Final → `gerir-todo` | Feature e Sistema: templates e índices diferentes |
| Implementação | checklist repetida em 4 agentes | regra por caminho | Definição de pronto em `.claude/rules/csharp.md`, carregada ao tocar qualquer `.cs` | TDD continua no @TestEngineer, o dono |
| Orquestração | Papel 3 duplicado no agente e na skill | skill canônica | `validar-todos` passou a ser o protocolo; o agente aponta para ela | Papel 1 (sessão): núcleo do agente |
| Todas — 2ª passada | checagens mecânicas feitas pelo agente | script, teste, hook, fork | Varredura criativa e `// TODO` inline viraram script; roteador, backlog, serviço e paleta viraram teste; arquivo congelado e gate do Unity viraram hook; hemeroteca roda em fork | Handoff, DDR e concept art têm diálogo com o usuário — ficam inline; scaffolding de cidade e ADR são raros e pedem julgamento — sem script |
| Todas | skills situacionais pré-carregadas | só a de toda invocação | Hemeroteca, nova-cidade, fechar-decisao, novo-inimigo, novo-adr, meta-check e novo-asset passam a carregar sob demanda | `gerir-todo`, `sprite-pipeline`, `unity-validar`, `validar-todos` e `structure-audit` seguem pré-carregadas onde são usadas sempre |

---

[← Manual de processos](index.md)
