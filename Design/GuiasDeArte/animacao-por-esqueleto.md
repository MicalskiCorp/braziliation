# Animação por esqueleto — Braziliation

> **Personagem = pele + esqueleto + movimentos** (ADR-016). A pele é desenhada UMA vez; esqueleto e movimentos
> são dados; os quadros saem de código. Continuidade por construção (o mesmo desenho em toda pose), uma pose
> custa ~150 caracteres contra ~9.600 de um quadro em spec, e variante (armadura, estágio de receptáculo,
> dano) é só uma pele nova com as mesmas animações. Técnica do Dead Cells (corpo 3D desenhado em pixel) e do
> lookup de pele do Astortion, via o `rig.js` do PixelFX. Ferramentas em
> [`pxfx/esqueleto/`](../ArteFonte/Ferramentas/pxfx/index.md).

## Onde entra no fluxo de 5 etapas

| Etapa | O que muda |
|-------|-----------|
| 1. Ideia | igual |
| 2. Concept | igual (difusão para clima e estilo). Conteúdo nomeado (o gato da Edith, o bambuzal) vira **peça** desenhada, não pedido ao modelo — 12 lotes mostraram que a difusão não obedece a isso |
| 3. Especificação | as ações viram **movimentos** (`anim.json`), não quadros |
| 4. Spec | `{asset}.rig.json` + a **pele** (`{asset}.pele.png`) no context pack |
| 5. Sprite | `py -m pxfx.esqueleto.animar` gera sheet + JSON; retoque só nos quadros de pico |

## Passo a passo

1. **Escolher o modelo de corpo** e escrever `ContextPacks/{asset}/{asset}.rig.json`:

   | Modelo | Para | Ajustes |
   |--------|------|---------|
   | `bipede` | protagonista, Edith, soldados, Cuca, Mapinguari | `medidas` (proporção), `mult_volumes` (cabeça, tronco...) |
   | `bipede` + `variante` | Saci (`"pernas": 1`), Curupira (`"pes_invertidos": true`) | — |
   | `mecanico` | autômatos (chapas, blocos, tinta nas juntas) | engrenagem e detalhe vão na pele |
   | `quadrupede` | Lobisomem, cão | `medidas` do tronco, pernas, pescoço, cauda |
   | `serpente` | Minhocão, Boitatá, cauda da Iara | `segmentos`, `comprimento`, `raio` |

   `"escala": 2.5` = ~96 px de altura (ADR-011). `"regiao": "blumenau"` liga a checagem de paleta.

2. **Animar no manequim primeiro** (blocagem): `py -m pxfx.esqueleto.animar manequim_bipede.rig.json
   <acao>.anim.json` com o rig de `pxfx/esqueleto/modelos/`. Aprovar o MOVIMENTO antes de existir pele.
3. **Gerar o gabarito da pele:** `py -m pxfx.esqueleto.animar {asset}.rig.json --referencia` → `.referencia.png`
   (pose de descanso no manequim), `.partes.png` (uma cor por peça) e `.referencia.json` (origem dos pés).
4. **Pintar a pele POR CIMA do gabarito** — mesmo tamanho, mesma origem — com keys da paleta regional (pixel
   pass no Aseprite via MCP, ou concept aprovado reduzido com `pixelize.py` e retocado). Cada material da pele
   é uma **rampa de 4 degraus aceso → escuro** declarada em `"rampas"` do rig. Cor fora de rampa (olho, emblema,
   botão de latão) é detalhe fixo: segue a peça mas não muda de luz.
5. **Animar com a pele:** apontar `"pele"` e `"pele_origem"` no rig e rodar de novo. A luz de cada pixel anda na
   rampa tantos degraus quanto a pose difere do descanso — nunca sai da paleta.
6. **Retocar os quadros de pico** (antecipação, impacto, smear): PNG do tamanho do quadro em
   `{acao}.retoques/fNN.png`, só com os pixels retocados. Se o quadro base mudar depois, o JSON do sheet lista o
   retoque em `retoques_a_revisar`.
7. **Exportar:** `{nome}_{acao}_sheet.png` + `.json` em `Assets/Art/...`; o Unity fatia pelo JSON e monta o clipe
   com a duração de cada quadro.

## Movimentos (`anim.json`)

```json
{"acao": "ataque", "loop": false, "passo": 12, "respira": false,
 "chaves": [[-0.5, {"crouch": 3, "fx": 12, "fy": -19}], [-0.2, {"fx": -9, "fy": -33, "lean": -4}],
            [0.06, {"fx": 24, "fy": -19, "lean": 5, "ffx": 13}, "snap"], [0.7, {"fx": 12, "fy": -19}]],
 "eventos": [{"t": 0.06, "tipo": "impacto", "congela": 0.14, "tremor": 0.18, "amp": 2}]}
```

- **Pose** em px do boneco de 38 px (o esqueleto multiplica pela escala): `fx, fy` mão da frente, `bx, by` mão
  de trás, `ffx, ffy`/`fbx, fby` pés, `crouch`, `lean`, `turn`, `yaw`, `hx, hy` (cabeça), `x, y` (raiz). Ele
  vira o corpo três-quartos para nós: braço aberto = mão da frente à esquerda (`fx < 0`). Um braço alcança
  ~15 px do ombro e não estica — dê um passo com o corpo.
- **Chegada:** suave (padrão), `"out"` rápido e assenta, `"in"` devagar e acelera, `"line"`, `"snap"` (segura a
  anterior e pula). Membros andam em **degraus de 12 fps** contados de cada chave (desenho segurado); a raiz
  continua suave. Passos iguais em seguida viram um quadro segurado — é a duração por quadro do sheet.
- **O que vende o golpe:** preparação no sentido oposto ao golpe, grande mudança de silhueta no quadro de soltura,
  congelamento no contato (0,03–0,2 s, mais longo para golpe pesado), continuação que passa do ponto.
- **Biblioteca:** as 73 atuações do PixelFX (`esqueleto/biblioteca/atos_pixelfx.json`) servem direto:
  `--biblioteca melee/sword-slash --acao ataque`. Viram ponto de partida, não movimento final.
- **Eventos** vão para o JSON do sheet com o quadro em que caem — é o que o `PlayerCombat` lerá para hit-stop.

## Crítica (o que olhar)

- `_tira.png`: passos CONSECUTIVOS de 12 fps — movimento se julga aqui, nunca em amostra solta.
- `_contact.png`: quadros únicos com a duração de cada um.
- O relatório do `animar` (chão, salto, emenda, cores, paleta, órfãos). AVISO pede olho; FALHA bloqueia export.
- Mínimo de três rodadas de crítica; a régua de leitura é a da [style-bible](style-bible.md).

## Limites conhecidos

- **Rosto e expressão** não saem do esqueleto: cabeça vira detalhe da pele, ou peça trocável.
- **Buraco de origem:** parte escondida no descanso não tem pixel na pele; a busca usa o pixel mais próximo da
  MESMA peça (raio 7 × escala). Pose de referência com membros afastados reduz o problema.
- **Virar de frente/costas** exige pele extra ou quadro manual; esquerda/direita é espelho.
- **Esticar e achatar** (squash & stretch, smear): ossos têm comprimento fixo — use retoque.
- **Armas na mão** (`weapon`, `sa` do original) ainda não foram portadas: pendência no TODO de Desenvolvimento.
