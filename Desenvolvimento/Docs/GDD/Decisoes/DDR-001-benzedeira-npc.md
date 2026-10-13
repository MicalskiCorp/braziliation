# DDR-001 — Benzedeira: NPC de acalanto, garrafadas e benzimentos

> **Status:** Aprovada — 12/10/2026, decidida pelo responsável do projeto (registro feito depois da decisão, não proposta).
> **Origem:** entrevistas do assunto `benzedeira` (`Design/Pesquisa/Entrevistas/Assuntos/benzedeira.md`) e handoff `Design/Pesquisa/Handoffs/2026-10-11-benzedeira.md`.
> **Encadeado com:** [DDR-002 — Monge João Maria](DDR-002-monge-joao-maria-papel.md) (os dois NPCs aliados que ajudam o jogador não se repetem).

## Problema

O jogo não tinha um lugar seguro de recuperação nem um sistema de efeitos temporários pedidos a
NPCs; a cura em NPC já estava atribuída ao Monge João Maria, e a Capa Mística já prometia
"encantamentos" e "bênçãos" pela build. Sem decidir o papel da benzedeira, as entrevistas com
benzedeiras não tinham destino de design, e quatro sistemas (NPCs, crafting, build, checkpoints)
ficavam com sobreposição em aberto.

## Decisão

1. **A benzedeira é um tipo de NPC, com várias pelo mapa.** Uma senhorinha muito tranquila, calma
   e querida — personagem de **acalanto**, o espírito das benzedeiras dos nossos avós. Cada região
   tem a sua, com **um benzimento e uma garrafada próprios** da região. A fala vem das entrevistas,
   com os trejeitos (regra em `.claude/agents/game-creative.md`).
2. **Ponto seguro.** Na benzedeira o jogador **recupera a vida toda**. Onde cada benzedeira fica
   (e se a casa dela é o checkpoint da região) **fica para quando houver mapa** — pendência em
   `Desenvolvimento/Docs/TODO.md`.
3. **Garrafadas — sem mesa de crafting.** O jogador **encontra garrafas vazias pelo mapa** (garrafa
   não se fabrica) e **ingredientes** (derivados de ervas, raízes, itens de medicina). Leva os dois
   à benzedeira, que prepara a garrafada. A mesa de crafting dos receptáculos não participa.
4. **Benzimentos — temporários.** Pedidos à benzedeira, viram efeitos no jogador (ex.: **corpo
   fechado → bônus de defesa**). Cada benzimento tem **duração própria** — uns mais curtos, outros
   mais longos — e **acaba**: precisa ser renovado com uma benzedeira. Benzimentos são pensados
   **contra monstros e bosses específicos**: o jogador vai procurar a benzedeira para o benzimento
   certo antes de uma luta.
5. **Diferença para a Capa das Lendas do Mar.** As bênçãos da Capa são **fixas** — atributos e
   aprimoramentos permanentes da build. O nome "bênçãos" pode mudar (orações, encantamentos…) para
   não se confundir com os benzimentos, que são temporários e pedidos a NPC.
6. **Progressão.** Benzimentos e garrafadas novos se **desbloqueiam** conforme o jogo avança.

## Opções consideradas (histórico)

| Opção | Por que não |
|---|---|
| Garrafadas feitas na mesa de crafting, com garrafa fabricada | Misturaria consumível com o crafting de receptáculos, que é progressão permanente; a garrafa achada no mapa é recompensa de exploração |
| Benzimento permanente, como habilidade da build | Repetiria a Capa Mística e tiraria o motivo de voltar à benzedeira |
| Benzedeira como curadora itinerante | Esse papel era do Monge João Maria; ver DDR-002 |

## Números iniciais *(provisórios — tuning muda o número, não a decisão)*

| Parâmetro | Valor de partida |
|---|---|
| Cura na benzedeira | 100% da vida, sem custo |
| Benzimentos ativos ao mesmo tempo | 1 |
| Corpo fechado | −25% de dano recebido por 10 min de jogo |
| Benzimento contra um tipo de monstro | +30% de dano contra aquele tipo por 5 min |
| Benzimento de quebranto (cura estado negativo) | remove efeitos negativos e dá imunidade a eles por 3 min |
| Garrafada | 1 garrafa vazia + 2 ingredientes → 1 garrafada |
| Garrafas vazias carregadas no início | 3 |
| Desbloqueio | cada região libera 1 benzimento e 1 garrafada novos |

## Onde a decisão foi aplicada

- `Desenvolvimento/Docs/Mechanics/Crafting.md` — garrafadas fora da mesa de crafting.
- `Desenvolvimento/Docs/Mechanics/Build.md` — bênçãos da Capa fixas × benzimentos temporários.
- `Desenvolvimento/Docs/TODO.md` — localização das benzedeiras (quando houver mapa).
- `Design/Criativo/TODO.md` — o handoff da benzedeira aponta para este DDR.

## O que fica aberto

- Localização das benzedeiras e se a casa delas é o checkpoint — depende do mapa.
- Lista de benzimentos e garrafadas por região — vem das entrevistas e da pesquisa "Benzimentos e
  garrafadas por região" (`Design/Pesquisa/TODO.md`).
- Novo nome das bênçãos da Capa.
- Ficha do arquétipo e da primeira benzedeira — `@GameCreative`, pelo handoff.
