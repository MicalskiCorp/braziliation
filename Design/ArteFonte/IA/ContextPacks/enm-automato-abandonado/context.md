# Context Pack — Autômato Abandonado (placeholder de inimigo)

> **✅ ADR-011 — re-autoria davinciana concluída (2026-10-05):** o asset foi **redesenhado**,
> não migrado. Saiu a versão frontal simétrica de 32×32/3 frames; entrou um autômato de
> relojoaria em **96×96 @ 48 PPU**, vista lateral, montado por catálogo de peças
> (`montagem.py`). Duas dimensões de variação: **armamento** (lança, escudo-engrenagem,
> sucata) e **liga** (bronze, prata, ferro), esta última pensada como grau de dificuldade —
> só a rampa do metal muda, a silhueta não. O idle de 6 frames é o **maquinismo girando**:
> cada roda avança um período de simetria por ciclo, rodas que engrenam giram em sentidos
> opostos, e a brasa da lente respira. Sem bob: é máquina rígida.
> Caminho percorrido até aqui: 32×32 frontal → lateral em latão (recusada por "fofa") →
> releitura gótica com manto (recusada por não ser davinciana) → esta. As duas recusadas
> ficam registradas em `enm_automato.alt-latao.spec.json` e no histórico do git.
>
> _Histórico:_ **ADR-004 — re-autoria concluída (2026-07-12):** specs 2× (`*.2x.spec.json` via `spec_redetail.py`) são a fonte atual; sheet re-autorado 192×64 (frames 64×64) entregue. Specs 1× = histórico.

## 1. Identificação

- Asset: `enm_automato_idle_sheet` (32×32, 3 frames)
- Rota: **programática (Opção A)** — placeholder; versão final poderá passar pela rota C (difusão) + pixel pass
- Região: Blumenau | Paleta: `blumenau.json` (aprovada 2026-07-11)
- Referência criativa: `Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md` → Monstros
- Data: 2026-07-11

## 2. Brief

"Máquina autônoma sem programação ativa, reage por reflexo a movimento. Corpo todo de metal trabalhado, estilo Da Vinci." Torso de latão arredondado com engrenagem exposta no peito, cabeça cilíndrica com olho de vidro (lente), braços e pernas de hastes de ferro finas. Idle: oscilação sutil de 1px + tique da engrenagem do peito.

> **Nota de design:** o inimigo básico da demo segue como decisão pendente no TODO — este placeholder permite `@GameplayEngineer` implementar AI/estados sem esperar arte final.

## 3. Restrições

32×32, side-view, pivot base central, ~12-16 cores, silhueta de ameaça legível em 1x, sem sci-fi moderno.

## 4. Resultado

- **Entregue 2026-07-12** — `enm_automato_idle_sheet.png` (96×32, 3 frames: engrenagem do peito tica um dente por frame + lente varia o brilho). APROVADO no `palette_check` e no mock 320×180 (silhueta de ameaça clara, latão destaca do fundo por valor).
- Iterações: 2 — a engrenagem do peito lia como painel quadrado; anel de cobre arredondado na iteração 2.
- Destino: `Assets/Art/Enemies/`; cópia em `IA/Selected/`; registro no índice.
- Pendências: decisão de design "inimigo básico da demo" continua aberta no TODO (este asset destrava a implementação de AI/estados como placeholder); animações de patrol/attack quando o design definir o comportamento.

## 5. Frame de ataque — bench de 2026-09-03 e o que fazer com ele

O bench [`bench-modelo-claude-spec-2026-09.md`](../../Models/bench-modelo-claude-spec-2026-09.md)
usou "autorar um frame de ataque do Autômato" como tarefa de comparação entre modelos, e o
resultado do `opus` ficou em `IA/Outputs/bench-spec-automato/opus/`. Ele saiu com um defeito
anotado — quebrou continuidade com o idle (redesenhou a engrenagem do peito, a cabeça e a
silhueta do torso) — e entrou no TODO como "passe de continuidade".

**O passe de continuidade não deve ser feito (achado de 2026-11-04).** O frame de ataque do bench
está ancorado em `enm_automato_idle_f1.2x.spec.json`: a versão frontal simétrica 64×64 de torso de
latão com painel de engrenagem no peito. Essa versão **foi aposentada um mês depois do bench**, na
re-autoria davinciana de 2026-10-05 (ADR-011, topo deste arquivo) — hoje o asset é lateral, 96×96
@ 48 PPU, crânio-gaiola com lente no focinho, gradil de madeira com o maquinismo à vista, montado
por catálogo de peças em `montagem.py`.

Conferido lado a lado (`enm_automato_idle_f1.2x` × `enm_automato_variantes_4x`): não há um pixel em
comum entre as duas leituras. Fazer o passe produziria um frame coerente com um design que não
existe mais — as três correções pedidas (engrenagem do peito, cabeça, torso) são justamente os três
elementos que a re-autoria eliminou.

**Encaminhamento:** o ataque do Autômato nasce junto com dano e morte, quando o inimigo base tiver
o comportamento decidido — e, desde o ADR-016 (2026-11-04), **pelo esqueleto do `pxfx`** (rig
mecânico + `anim.json`, skill `animar-personagem`), não por edição de matriz nem pelo `montagem.py`.
O esqueleto dá continuidade com o idle por construção: a pele é a mesma, só a pose muda.

O resultado do bench fica onde está, como **registro do bench** — é evidência do veredito de
modelo, não candidato a asset. Não promover, não editar.
