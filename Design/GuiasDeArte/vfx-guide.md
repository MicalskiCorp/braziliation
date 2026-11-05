# Guia de VFX — Braziliation

> Efeitos visuais (fogo, explosão, vapor, faísca, água, raio, impacto, aura) feitos por CÓDIGO no motor
> [`pxfx`](../ArteFonte/Ferramentas/pxfx/index.md) (ADR-016). A régua de qualidade e o método vêm do
> PixelFX e do Hugo Duprez ("código é argila, confie nos olhos, alimente referências"), adaptados à
> [style-bible](style-bible.md): paleta regional, escala de 96 px, dieselpunk brasileiro.

## Regras do Braziliation (valem antes da régua)

- **Escala:** efeito nasce para o personagem de ~96 px (ADR-011). Os efeitos do PixelFX foram feitos para um
  boneco de 38 px: renderize com `--escala 2.5` e corrija os laços de ponto (ver `pxfx/index.md`).
- **Paleta:** a cor do efeito vem de uma rampa da paleta regional (`--regiao blumenau --rampa L,9,W,K` para fogo),
  do escuro ao claro — as rampas por material estão no [`palette-guide.md`](palette-guide.md#rampas-de-blumenau), na ordem
  inversa (aceso → escuro). O buffer de COR do pxfx é opaco com dither Bayer: passa no `palette_check.py`.
- **Brilho e translucidez:** a luz aditiva (`glow`, `light`) e a fumaça translúcida (`disc`, `blend`) geram alpha
  parcial, que o `palette_check` reprova. Até a decisão da camada emissiva (TODO de Desenvolvimento), exporte
  com `--opts '{"light": 0}'` ou troque `disc` por dither, e registre o brilho desejado no brief.
- **Sobrenatural íntimo** (style-bible): brilho pequeno e localizado. A régua abaixo pede "luz em tudo" — no
  Braziliation isso vale para fogo, explosão e máquina; aparição e lenda usam menos luz e mais silhueta.
- **Dieselpunk:** vapor, fuligem, faísca de solda, arco voltaico (`bolt`), óleo, ferrugem. Motivo genérico de
  fantasia (arcano, sagrado) é redesenhado para a lenda ou o clero de Blumenau, nunca usado cru.

## A régua (o que todo efeito precisa fazer)

1. **Linhas e luz, não preenchimento.** Aros de 1 px, anéis, rastros e faíscas; a luz carrega o brilho. Área grande
   de cor saturada chapada quase sempre está errada. Núcleo e borda quentes, meio tingido, cor funda só na sombra.
2. **Luz no lugar certo.** Poça larga e fraca, ponto quente no núcleo, luz em cada faísca, luzes que acendem no
   impacto e morrem, poça no chão enquanto algo queima.
3. **Volumes translúcidos.** Fumaça, vapor e poeira são macios (`SMOKE`, `VAPOUR`, `DUST`), iluminados por cima,
   inchando e afinando. Nunca um xadrez de dither para fumaça.
4. **Movimento real.** Faísca estica com a velocidade, cai e quica. Detrito tomba, quica e assenta. Fogo sobe e
   esfria em fumaça. O que cai levanta poeira. Arrasto: estouro rápido, deriva lenta.
5. **Coreografia em fases.** Antecipação (as coisas se juntando), liberação (1–2 quadros de branco, clarão),
   espalhamento, permanência (brilhos, brasas), quebra, decaimento longo.
6. **Profundidade.** Anel no chão é elipse achatada com a metade de trás atrás do personagem (`band`, `drawBack`).
7. **Tempo.** Ataque rápido, soltura lenta. Efeito grande dura 2–4 s; golpe é curto (0,3–0,8 s) mas tem continuação.
8. **Lê em 1×** com um ponto focal e sem ruído solto dentro das formas.
9. **Original.** Motivo genérico vale; sprite, personagem ou logo de jogo específico não.
10. **Limpo.** Cabe no canvas, termina vazio ou fecha o loop sem emenda, é determinístico (`py -m pxfx.check`).

## Você vê → corrija assim

| Você vê | Corrija |
|---------|---------|
| vira papa em 1× | menos cores, silhueta clara, um ponto focal, formas maiores |
| pixel solto dentro da forma | menos limiar no ruído, quantizar com `at()`, sem ruído em forma pequena |
| flutua, sem soco | entra rápido e assenta devagar (`ease.outQuart`/`outExpo`), 1–2 quadros de branco, menos duração |
| duro, mecânico | varie cada partícula (tamanho, velocidade, atraso, vida), movimento secundário (faísca, fumaça, detrito) |
| lavado | menos brilho (k 0,2–0,5), degraus de borda mais escuros, branco só no núcleo mais quente |
| chapado | luz de um lado: degrau mais claro em cima à esquerda, mais escuro embaixo à direita, base mais escura |
| gradiente suave, cara de vetor | degraus duros de rampa na cor; suavidade só na luz e na fumaça translúcida |
| xadrez onde devia ser fumaça | partículas `SMOKE`/`VAPOUR`/`DUST` ou `p.disc` |
| emenda quando o loop volta | `cycle`, `loopNoise(fase)`, rolagem de `tileNoise` por célula inteira, `sin(fase * TAU * n)` |
| one-shot que some de estalo | deixe encolher, dissolver em dither ou cair antes do fim |
| efeito ótimo num corpo morto | dê atuação: preparação, pose de soltura, congelamento no contato, alvo que reage |
| pontilhado depois de `--escala` | laço de pontos em passo fixo: amostre em `1/p.k` (ver `pxfx/index.md`) |

## O método

1. **Diga em uma linha** com direção de arte: o que é, como se move, rampa, tempo.
2. **Referência primeiro:** `py -m pxfx.render <id>` dos 2–3 efeitos mais próximos já portados (e, para o que
   ainda não foi portado, o original em `vendor/pixelfx/src/fx/`). Se a referência tem mais detalhe, luz ou
   vida no mesmo tamanho de tela, o seu não terminou.
3. **Rascunhos divergentes:** com a direção aberta, 3–5 rascunhos de verdade diferentes, `py -m pxfx.render
   "<cat>/<nome>-*"` e escolha olhando as folhas lado a lado. Mostre os 2–3 melhores ao usuário.
4. **Olhe, julgue, corrija o PIOR problema, renderize de novo.** Mínimo de três rodadas — passar no `check` e no
   `palette_check` não é estar pronto (o bench de 2026-09 mostrou modelos parando aí).
5. **Movimento se julga em passos consecutivos**, não em amostras: `--all` na folha, ou o GIF.
6. **Checagem:** `py -m pxfx.check <id>` até passar limpo; `palette_check.py` no sheet exportado.
7. **Export:** `py -m pxfx.render <id> --escala 2.5 --sheet --nome vfx_<nome>` → `vfx_<nome>_sheet.png` + `.json`
   em `Assets/Art/VFX/`. O `SheetAutoSlicer` lê o JSON (quadro, pivô) e o `SheetAnimationTool` as durações.

Onde vive a régua original: `vendor/pixelfx/docs/AUTHORING.md` (enquanto a cópia existir).
