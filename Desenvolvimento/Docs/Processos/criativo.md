# Criativo

> Camada 2 · Design · Fonte canônica: [`game-creative.md`](../../../.claude/agents/game-creative.md) · skills [`gerir-todo`](../../../.claude/skills/gerir-todo/SKILL.md), [`nova-cidade`](../../../.claude/skills/nova-cidade/SKILL.md), [`fechar-decisao`](../../../.claude/skills/fechar-decisao/SKILL.md), [`handoff`](../../../.claude/skills/handoff/SKILL.md). Este manual resume; em divergência, vale a fonte.

Dono **@GameCreative** · Pasta **Design/Criativo/** · TODO **Design/Criativo/TODO.md** · Operações **skill gerir-todo** (pré-carregada) · Sai por **## Handoffs do @GameCreative** no TODO de Dev

Transforma folclore e ideias em material estruturado — cidades, lendas mapeadas, personagens, arcos — que alimenta monstros, mapas e NPCs. Usa a pesquisa aprovada como base factual e não pesquisa na web nem toca fontes do engine. Sete modos: os artefatos distintos continuam separados; o que era o mesmo procedimento com dois nomes foi unido.

## Passo 0

- Ler `Design/Criativo/TODO.md` e ver se o pedido já é pendência.
- Ler `Design/Pesquisa/index.md` para achar pesquisa aprovada sobre o tema.
- Se houver handoff, ler o briefing de `Design/Pesquisa/Handoffs/`.

## Passo Final

- TODO pela skill `gerir-todo`: concluído → "Concluído" com data; novo → seção certa com ❌; parcial → 🔨.
- Item pronto para virar feature → skill `handoff` (C10).

## Gatilho → modo

- `Catalogar lenda:` · `Mapear:` → C1
- `Registrar ideia:` → C2 · `Brainstorm:` → C3
- `Novo arco:` → C4 · `Novo personagem:` → C5
- `Nova cidade:` · `Novo estado:` → C6
- `Varredura criativa` → C7 · `TODOs: …` → C8

## C1 — Lenda: catalogar e mapear

**Quem:** @GameCreative · Modo 1
**Aciona:** `@GameCreative Catalogar lenda: Curupira` · `@GameCreative Mapear: Curupira → monstro`

1. Ler `Lendas/catalogo.md`; se a lenda não estiver, adicionar (nome, origem, categoria, ❌). Pedido só de catalogar termina aqui.
2. Mapear: linha em `Lendas/mapeamento.md` (lenda, elemento, tipo, arco, 🔨).
3. Reinterpretação dieselpunk no arquivo da categoria: `por-categoria/criaturas.md`, `lugares.md` ou `personagens.md`.
4. Status no catálogo → 🔨; monstro novo abre concept art (C8, `concept-art`).

- **Pergunta ao usuário:** Arco e reinterpretação dieselpunk
- **Unificou:** "Catalogar" e "Mapear" — o mapear já catalogava

## C2 — Registrar ideia

**Quem:** @GameCreative · Modo 2
**Aciona:** `@GameCreative Registrar ideia: boss que persegue pelo rastro de combustível`

1. Ler `Ideias/pool.md`.
2. Calcular o próximo número sequencial.
3. Adicionar: ideia, tag, prioridade, 💡 Nova.
4. Apontar lenda, feature ou mecânica relacionada e sugerir o próximo passo.

- **Escreve:** `Ideias/pool.md`
- **Mantido separado:** Uso avulso frequente; o brainstorm só termina chamando este modo

## C3 — Brainstorm

**Quem:** @GameCreative · Modo 3
**Aciona:** `@GameCreative Brainstorm: monstros para a região amazônica`

1. Criar `Brainstorm/sessoes/AAAA-MM-DD-{tema}.md` com cabeçalho e as seções *Ideias Brutas*, *Ideias Selecionadas*, *Próximos Passos*.
2. Registrar a sessão em `Brainstorm/index.md`.
3. Conduzir: perguntas, conexões com lendas, arcos e mecânicas; handoff de brainstorm da Pesquisa entra como base factual.
4. Ao fechar, registrar as ideias aprovadas (C2).

- **Entrada comum:** P4 tipo brainstorm
- **Exemplo real:** `sessoes/2026-04-26-blumenau.md`

## C4 — Novo arco narrativo

**Quem:** @GameCreative · Modo 4
**Aciona:** `@GameCreative Novo arco: A Floresta Que Respira`

1. Ler `Historia/arcos.md`.
2. Pedir o que faltar: conflito, cenário, antagonista, lendas ativas, resolução.
3. Adicionar a linha do arco.
4. Sugerir lendas do catálogo que se encaixam.

- **Pendente:** Meta-arco "A Rede Esquecida"

## C5 — Novo personagem

**Quem:** @GameCreative · Modo 5
**Aciona:** `@GameCreative Novo personagem: Saci, o Correio`

1. Ler `Historia/personagens/index.md`.
2. Criar `Historia/personagens/{Nome}.md` pelo `ModelPersonagem.md`, com Aparência detalhada o bastante para servir de matriz do concept art.
3. Atualizar o índice; garantir a lenda no catálogo (C1).
4. Abrir a pendência de concept art (`gerir-todo` → `concept-art`), que abre também a linha em `indices/assets.md`.

- **Próximo:** A2 na camada de Arte

## C6 — Nova cidade ou estado

**Quem:** @GameCreative · Modo 6 · skill `nova-cidade`
**Aciona:** `@GameCreative Nova cidade: Chapecó — Santa Catarina` · `@GameCreative Novo estado: Rio Grande do Sul`

1. Estrutura pela skill: template `ModelCidade.md`, índices do estado e de cidades, paleta proposta; estado novo cria `index.md`, `ideias.md`, `cidades/index.md` e sai de "Planejados".
2. Pedir nome real, nome no jogo e Punk Genre; para estado, as primeiras cidades.
3. Preencher Características com o que o usuário der.
4. Monstros, Lugares e Easter Eggs a partir da pesquisa aprovada; lacuna → sugestão de `@Historiador Pesquisar`.
5. Catalogar lendas novas (C1) e abrir concept art de cada criatura.
6. Pastas em `Assets/Art/Environments/{Cidade}/` → pendência do @UnityDeveloper.

- **Gate:** Sem direção de paleta, só a base do palette-guide
- **Unificou:** "Nova cidade" e "Novo estado", que repetiam os passos da skill — a estrutura mora na skill, o conteúdo no agente

## C7 — Varredura criativa

**Quem:** @GameCreative · Modo 7 · `gerir-todo` → `varredura`
**Aciona:** `@GameCreative Varredura criativa` — sem confirmar passo a passo

1. Marcadores abertos (`{TODO}`, `*(a definir)*`…).
2. Lendas ❌ sem mapeamento; ideias 💡 paradas.
3. Arcos e personagens sem lenda; cidades 📋 vazias.
4. Personagens e criaturas com Aparência sem concept art pendente nem aprovado.
5. Comparar com o TODO e devolver a lista para o usuário decidir.

- **Unificou:** A varredura do agente e a do antigo `BackLog.md`
- **Script:** `py .claude/skills/gerir-todo/todo.py varredura criativo` faz as checagens e marca o que já está no TODO

## C8 — TODO criativo

**Quem:** @GameCreative · skill `gerir-todo` (pré-carregada)
**Aciona:** `TODOs: listar` · `adicionar` · `concluído` · `executar: {item}`

1. **listar** — resumo por seção, destacando Alta ❌ e bloqueios.
2. **adicionar** — seção pela tabela de roteamento (História, Lendas, Cidades, Estados, Ideias, Crafting & Build).
3. **concept-art** — linha na tabela de concept art + linha em `indices/assets.md`.
4. **executar** — identificar o tipo e rodar o modo (C1–C6, ou C9 para decisão); ao fim, **concluído**.

- **Fora do escopo:** Concept art pendente é da Arte — sugerir @SpriteArtist
- **Substituiu:** `Design/BackLog/BackLog.md`

## C9 — Fechar decisão de design (DDR)

**Quem:** @GameCreative + @TechLead · skill `fechar-decisao`
**Aciona:** "fechar decisão", "definir a arma/inimigo/premissa" — a premissa vem antes de todas

1. Escolher a pendência Alta de design que desbloqueia mais outras.
2. Juntar só o contexto que restringe: premissa, cidade, game-vision, `Mechanics/`, código do core, assets prontos.
3. Escrever `GDD/Decisoes/DDR-{NNN}-{slug}.md`: problema, 2 ou 3 opções, recomendação, números provisórios, status Proposta.
4. Apresentar e pedir aprovação, outra opção ou ajuste.
5. Aprovado: aplicar onde a decisão mora, baixar a pendência pela regra de cada TODO e fazer o handoff (ex.: inimigo base → I4).

- **Gate:** Nunca aprovar sozinho · uma decisão por execução
- **Estado hoje:** Nenhum DDR; 9 decisões bloqueiam a demo

## C10 — Handoff para a Documentação

**Quem:** @GameCreative · skill `handoff`

1. Confirmar que o item está completo (lenda mapeada, personagem, arco, cidade).
2. Linha em `## Handoffs do @GameCreative`: `Criar feature: {Nome} | Design/Criativo/{arquivo} | Alta | ❌`.
3. Avisar o usuário para acionar o @GameArchitect.

- **Exemplo real:** As 7 features de Blumenau (2026-05-17)
- **Próximo:** D1

---

[← Manual de processos](index.md)
