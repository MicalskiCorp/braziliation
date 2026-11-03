# Avaliação das 16 skills — plugin `skill-creator`

> Executado em 2026-11-03 por `@AgentArchitect`. Plugin: `skill-creator` (marketplace
> `claude-plugins-official`), commit em cache `a2e251d9b97b`. Reexecutar quando entrar
> skill nova ou quando o plugin for atualizado.

O "modo Eval" do `skill-creator` tem três níveis de custo bem diferentes. Esta avaliação
cobriu os dois primeiros — determinísticos, sem gasto de modelo. O terceiro depende de
decisão do responsável (ver [Nível 3](#nível-3--o-que-ficou-pendente-de-decisão)).

| Nível | O que mede | Custo | Status |
|-------|------------|-------|--------|
| 1 — validação estrutural | `scripts/quick_validate.py`: frontmatter, nome, limites | zero | ✅ feito |
| 2 — disclosure progressivo e colisão de disparo | métricas do guia do plugin + leitura das cláusulas `Use …` | zero | ✅ feito |
| 3 — benchmark de disparo e eval comportamental | `scripts/run_eval.py`, `improve_description.py` | centenas de chamadas `claude -p` por skill | ⏸ precisa de decisão |

## Nível 1 — validação estrutural: 16/16 válidas

Comando (o `PYTHONUTF8=1` é obrigatório — ver [bug 1](#bugs-do-plugin-encontrados-na-execução)):

```bash
PYTHONUTF8=1 py <plugin>/skills/skill-creator/scripts/quick_validate.py .claude/skills/<skill>/
```

Nenhuma skill tem defeito real de frontmatter. Quatro saem como inválidas, e são **falsos
positivos do validador**, não defeitos nossos:

| Skill | Chave recusada | Por que é legítima |
|-------|----------------|--------------------|
| `hemeroteca-blumenau`, `structure-audit`, `validar-todos` | `context`, `agent` | Skill que roda em fork de um agente — recurso do Claude Code |
| `novo-agente` | `disable-model-invocation` | Skill só invocável por nome, nunca pelo modelo |

O `quick_validate.py` valida contra o esquema de skill do claude.ai/API, que não conhece
essas chaves do Claude Code (ADR-008: Claude Code é o nosso único harness). **Não remover as
chaves para agradar o validador** — são elas que fazem a skill rodar em fork.

## Nível 2 — disclosure progressivo

O guia do plugin pede: metadados ~100 palavras, corpo do `SKILL.md` **abaixo de 500 linhas**,
e o que for grande em `scripts/`, `references/` ou `assets/`. Limites duros do esquema: nome
≤ 64 caracteres, descrição ≤ 1024.

| Métrica | Pior caso do projeto | Limite | Margem |
|---------|---------------------|--------|--------|
| Tamanho da descrição | 522 (`processar-entrevistas`) | 1024 | 49% |
| Linhas do corpo | 142 (`processar-entrevistas`) | 500 | 72% |
| Palavras do corpo | 1636 (`processar-entrevistas`) | — | — |

Nenhuma skill passa de 30% do orçamento de linhas; as 16 somam 8.816 palavras de corpo, e só
uma entra em contexto por vez. As skills de maior peso já externalizam o que é grande em
script (`gerir-todo/todo_md.py`, `meta-check/check_meta_pairs.py`,
`unity-validar/scripts/validar.py`, `validar-todos/todos_inline.py`). **Nada a corrigir.**

Todas as 16 têm cláusula de disparo explícita na descrição (`Use quando …`, e em dois casos
`Use no Passo 0 …` / `Use depois de editar …`, igualmente concretas).

## Nível 2 — colisão de disparo

Disparo de skill é decidido só pelo par nome + descrição. O risco real não é descrição ruim
isolada: é **duas descrições competindo pelo mesmo pedido**. Cruzando as 16 cláusulas `Use …`:

| Par / trio | Pedido ambíguo | Veredito |
|------------|----------------|----------|
| `novo-asset` × `sprite-pipeline` | "cria um sprite de lampião" | ⚠ ambíguo na descrição, **resolvido no roteiro** — ver abaixo |
| `meta-check` × `structure-audit` | "auditar os assets" | 🟡 cinza aceitável — checam coisas diferentes e as duas só reportam |
| `validar-todos` × `structure-audit` | "auditar o projeto" × "auditar estrutura" | ✅ separado na própria cláusula |
| `fechar-decisao` × `novo-inimigo` | "definir o inimigo base" × "criar inimigo" | ✅ `novo-inimigo` nomeia `fechar-decisao` como etapa anterior |
| `fechar-decisao` × `novo-adr` | "decidir X" | ✅ cada uma enumera o seu domínio (design × estrutural) |
| `gerir-todo` × `handoff` | "adicionar pendência" | ✅ "própria camada" × "outra camada", explícito |
| `unity-validar` × `meta-check` | "validar antes de commitar Unity" | ✅ complementares — disparar as duas é o certo |
| `hemeroteca-blumenau` × `processar-entrevistas` | "pesquisar em Blumenau" | ✅ fonte impressa × captura do WhatsApp |

**O caso `novo-asset` × `sprite-pipeline`.** A descrição de `novo-asset` se separa por "*e
ainda não existir brief/context pack para ele*" — uma condição de disco que o modelo não pode
checar antes de disparar. Na prática não causa dano: o passo 3 do `sprite-pipeline` manda criar
ou confirmar o context pack e aponta `novo-asset` quando ele falta, e `novo-asset` termina
registrando a pendência de produção. Os dois caminhos convergem. Mantido como está — mexer na
descrição para "resolver" a ambiguidade trocaria uma convergência que funciona por uma regra
que o modelo teria que adivinhar.

## Defeito de conteúdo encontrado e corrigido

A descrição do `sprite-pipeline` prometia "mock **640x360**" — resolução do ADR-004, que o
**ADR-011 substituiu por 960×540 @ 48 PPU**. O `mock_scene.py` já estava certo (gera 960×540 e
cita o ADR-011); quem ficou para trás foi a descrição da skill e o guia canônico.

É o pior lugar possível para um número velho: a descrição é **metadado sempre em contexto**,
então todo agente com `Skill` em `tools:` lia "640x360" em toda sessão.

Corrigido em três pontos:

- `.claude/skills/sprite-pipeline/SKILL.md` — descrição: `mock 640x360` → `mock 960x540`
- `Design/GuiasDeArte/pipeline-sprites-programaticos.md` passo 6 — "leitura em 640×360 real" → "leitura em 960×540 real (resolução de referência, ADR-011)"
- idem, checklist de crítica visual — "no mock 640×360?" → "no mock 960×540?"

Varredura complementar: nenhuma das 16 skills tem referência de arquivo quebrada e nenhuma
cita ADR substituído.

## Bugs do plugin encontrados na execução

Registrados aqui porque afetam quem reexecutar esta avaliação; não são dívida nossa.

1. **`quick_validate.py` quebra em UTF-8 no Windows.** Lê o `SKILL.md` com `read_text()` sem
   `encoding`, cai em cp1252 e estoura `UnicodeDecodeError` em qualquer skill com travessão ou
   aspas tipográficas — 5 das nossas 16. Contorno: `PYTHONUTF8=1`.
2. **`quick_validate.py` usa o esquema do claude.ai**, não o do Claude Code — recusa `context`,
   `agent` e `disable-model-invocation` (ver Nível 1).
3. **`run_eval.py` dá falso negativo em skill já instalada.** Ele registra um chamariz com nome
   `{skill}-skill-{uuid}` em `.claude/commands/` e só conta disparo se *aquele* nome for chamado.
   Rodando na raiz do projeto, a skill real está na lista junto com o chamariz; quando o modelo
   escolhe a real — o comportamento correto — o script marca "não disparou". Toda taxa de disparo
   medida assim sai pessimista para as nossas 16.

## Nível 3 — o que ficou pendente de decisão

### 3a. Eval comportamental (o "modo Eval" pleno)

Roda cada prompt de teste duas vezes (com skill e baseline) em subagentes que **executam a
skill de verdade**, grada contra asserções e abre um viewer HTML. É desenhado para skill de
saída autocontida (um gráfico, um documento). As nossas **mutam o repositório**: `nova-cidade`
cria árvore de pastas, `gerir-todo` reescreve TODO, `concept-art` enfileira job no ComfyUI,
`novo-adr` numera ADR. Rodar exigiria worktree descartável e ainda assim mexeria em ComfyUI e
em índices.

Recomendação: **não rodar nas 16.** O custo (≈ 16 skills × 3 prompts × 2 configurações ≈ 96
execuções de subagente que escrevem no disco) não se paga. As duas skills onde haveria lógica
de decisão para medir — `gerir-todo` e `validar-todos` — já têm script próprio com teste
(`gerir-todo/tests/test_todo_md.py`).

### 3b. Otimização de descrição (benchmark de disparo)

Mede só o disparo e é **seguro**: o `run_eval.py` mata o processo no primeiro uso de ferramenta,
sem nunca executar o corpo da skill. Custo: 20 queries × 3 repetições × até 5 iterações ≈ 300
chamadas `claude -p` **por skill**, mais uma revisão do conjunto de queries pelo responsável em
HTML. Some-se o falso negativo do bug 3.

Recomendação: rodar **no máximo nas duas do caso ambíguo** (`novo-asset`, `sprite-pipeline`), e
só se a convergência descrita acima falhar em uso real. Nas outras 14 a separação já está
explícita na cláusula de disparo, e o benchmark gastaria para confirmar o que a leitura mostra.

## Veredito

As 16 skills estão estruturalmente sãs, com folga grande de disclosure progressivo e disparo
bem separado. A avaliação valeu por um achado concreto: uma resolução de dois ADRs atrás viva
num metadado sempre em contexto. O nível 3 fica fora até haver sintoma em uso real.
