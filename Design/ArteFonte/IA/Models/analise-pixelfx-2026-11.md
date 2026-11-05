# Análise PixelFX → Braziliation (2026-11-04)

> Origem do ADR-016. O que é o [PixelFX](https://github.com/patch-gg/pixelfx), o que se extraiu, como foi
> validado e o que ficou para depois. Uso no dia a dia: [`vfx-guide.md`](../../../GuiasDeArte/vfx-guide.md) e
> [`animacao-por-esqueleto.md`](../../../GuiasDeArte/animacao-por-esqueleto.md).

## O projeto

MIT, publicado em 2026-10-30 pela Patch (4,7 mil estrelas em 5 dias, ~8 commits). 244 efeitos de pixel art
feitos por código (JS, sem dependência em runtime), um boneco 3D desenhado em pixel (técnica do Dead Cells),
atuação com preparação, congelamento no impacto e recuperação (adaptada do Hollow Crown), ferramentas de
crítica (folha de contato, comparação, tira de passos, checagens) e uma skill do Claude Code. Tamanho: núcleo
2.646 linhas, ferramentas 1.025, efeitos 41.224 (91%), galeria 600.

## Por que serve ao Braziliation

Mesma filosofia do pipeline programático (código determinístico + ciclo gerar → olhar → criticar → refinar),
mais avançado nas três frentes que mais doíam:

| Dor registrada | Do PixelFX |
|----------------|------------|
| Ataque do Autômato quebrou a continuidade com o idle (bench 2026-09) | esqueleto: as mesmas peças em toda pose |
| Spec de 96×96 custa ~9.600 caracteres por quadro | pose de ~150 caracteres; 73 atuações prontas como dado |
| Edith: 12 lotes, 73 imagens, 0 aprovadas — difusão ignora conteúdo nomeado e espectral | conteúdo como peça; espectral como efeito sobre o corpo (recolor, dither, aura) |
| `shade()` por faixa horizontal, sem volume; `outline()` uniforme contra a style-bible | 4 tons por normal · luz; contorno seletivo (novo no pxfx) |
| `SheetAnimationTool` em 8 fps fixos | duração por quadro e eventos no JSON lateral |
| Crítica por quadro isolado; sem checagem de movimento | tira de passos consecutivos; checagens de chão, salto, emenda, órfãos |

## O que NÃO veio, e por quê

- **Plugin pelo marketplace:** atualiza de fora sem revisão.
- **Ponte JS ↔ Python:** o pipeline é Python; o motor foi portado inteiro. O JS ficou só como gabarito fixo
  (`Ferramentas/vendor/pixelfx/`, commit `a841596`), removível ao fim do port.
- **Os sheets prontos como arte final:** feitos para um boneco de 38 px (o nosso tem ~96) e com glow em alpha
  parcial; ADR-011 veta ampliar por nearest. Os efeitos voltam em ondas, já reescalados.

## Validação (paridade com o original)

| O quê | Resultado |
|-------|-----------|
| Núcleo inteiro, cenário que exercita a API toda | 41 quadros, 0,000% de pixels diferentes, luz idêntica |
| `fire/torch` (+ `fire/_lib`) | 60 quadros, 0,000%, luz idêntica |
| Juntas do esqueleto, escala 1 e 2,5 | diferença ≤ 3e-14 px em 12 poses de atos reais |
| `poseAt` (todas as chegadas) | idêntico em 175 amostras |
| Silhueta do manequim contra o `posed()` original | sobreposição média 0,993 (mínima 0,918) |
| Escala 2,5 do `fire/torch` | formas cheias escalam sozinhas; laços de ponto pedem passo `1/k` (corrigido no `_lib` do fogo) |
| Pele de teste (paleta Blumenau) num golpe de 18 quadros | 12 cores, 0 fora da paleta; busca de origem ciente da peça eliminou o cinto vazando na coxa |

## Achados do port

- Três armadilhas de linguagem: `Math.round` (meio para cima) ≠ `round()` do Python; `%` com negativo; chave de
  objeto com nome de método de dict (`clear`). Documentadas em `pxfx/index.md`.
- A margem de alcance da cinemática inversa (0,02 px) precisa escalar com o corpo: sem isso o cotovelo se
  desloca 0,32 px na escala 2,5 com o braço esticado.
- Transferência de pele precisa ser ciente da peça: no descanso a pelve cobre o topo da coxa.

## O que ficou para depois (fila no TODO de Desenvolvimento)

Ondas 1–4 dos efeitos (243 restantes); armas na mão do esqueleto; decisão da camada emissiva (glow); hit-stop
no `PlayerCombat` a partir dos eventos; proporções finas do quadrúpede e da serpente por criatura; retirada da
cópia `vendor/` ao fim do port.

Fontes: repositório e `docs/AUTHORING.md` do PixelFX; "Art Design Deep Dive: Using a 3D pipeline for 2D
animation in Dead Cells" (Thomas Vasseur, Game Developer, 2018); técnica de lookup de pele do aarthificial
(Astortion).
