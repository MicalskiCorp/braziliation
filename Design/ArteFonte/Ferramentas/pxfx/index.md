# pxfx — motor de pixel art do Braziliation

Port Python do [PixelFX](https://github.com/patch-gg/pixelfx) (MIT, aviso permanente em
[`LICENSE-pixelfx.txt`](LICENSE-pixelfx.txt)), decidido no ADR-016. Efeitos, esqueleto e animação
por código, determinísticos, dentro da paleta. Guias de uso:
[`vfx-guide.md`](../../../GuiasDeArte/vfx-guide.md) e
[`animacao-por-esqueleto.md`](../../../GuiasDeArte/animacao-por-esqueleto.md).

Tudo roda da pasta `Design/ArteFonte/Ferramentas/` com `py -m pxfx.<ferramenta>`. Dependências:
`numpy` e `Pillow`; Node só para a paridade.

## Módulos

| Módulo | Original | O que faz |
|--------|----------|-----------|
| `matematica.py` | `math.js` | easing, aleatório com seed (idêntico bit a bit), ruídos — inclusive os que ladrilham e fecham loop |
| `cor.py` | `color.js` | cores uint32, rampas, `fit`/`at`; `rampa_regional()` monta rampa com keys da paleta da região |
| `pintor.py` | `painter.js` | dois buffers (cor opaca com dither Bayer + luz aditiva), formas, espelho/giro/**escala** |
| `quadro.py` | `fx.js` | quadro, instância de efeito, composição (numpy) |
| `particulas.py` · `simulacao.py` · `formas.py` · `golpe.py` | `particles.js` · `sim.js` · `shapes.js` · `chain.js` | partículas em fórmula fechada e simuladas, detritos, luzes, raios, golpes encadeados |
| `fonte.py` · `ator.py` · `cenario.py` | `font.js` · `actor.js` · `scene.js` | fontes 3×5/5×7, boneco de paridade, fundos de preview |
| `atuacao.py` | `act.js` (dados) | poses no tempo em degraus de 12 fps, `actTiming` |
| `renderizar.py` · `render.py` | `tools/lib/fxlib.mjs` · `render.mjs` | folha de contato, sheet + JSON lateral, GIF |
| `esqueleto/` | `rig.js` + novo | bípede (paridade), mecânico, quadrúpede, serpente; raster, pele, animar, checar |
| `efeitos/<cat>/<nome>.py` | `src/fx/` | os efeitos portados (ver Ondas) |
| `paridade/` | — | compara com o original pixel a pixel |

## Paridade (o que garante o port)

| Checagem | Comando | Resultado em 2026-11-04 |
|----------|---------|--------------------------|
| núcleo inteiro (12 partículas, detritos, luzes, todas as formas, texto, máscara, raios) | `py -m pxfx.paridade nucleo` | 41 quadros, 0,000% px, luz 0 |
| efeitos portados | `py -m pxfx.paridade fire/torch` | 60 quadros, 0,000% px, luz 0 |
| esqueleto: juntas escala 1 e 2,5, `poseAt`, silhueta | `py -m pxfx.paridade.esqueleto` | 1e-14 px · exato · sobreposição média 0,993 |

Tolerância: 0,5% dos pixels de cor e 3 níveis de luz (1 ulp de seno entre V8 e CPython pode virar
pixel de fronteira). Acima disso é bug de port.

## Convenções do port (leia antes de portar um efeito)

- **Nomes da API iguais ao original** (`p.disc`, `ps.spawn`, `glowLine`): o `AUTHORING.md` e as receitas
  continuam valendo. Módulos com nome em português para não colidir com a biblioteca do Python.
- **Objeto literal → `Obj`** (`o.palette`, `None` onde o JS dá `undefined`). Chave com nome de método de
  dict (`clear`, `items`, `get`, `copy`, `update`...) só por `o["clear"]` — `o.clear` devolve o método.
- **Objeto de opções → kwargs**: `bolt(R, x0, y0, x1, y1, jag=0.3)`, `forks(..., count=2, len=14)`.
- **`Math.round` → `jsround`**, `x | 0` → `i32`/`int`, `%` com negativo → `jsmod`/`wrap`.
- **Laço `for (let i = n-1; i >= 0; i--)` com `splice`** → `range` invertido + `del lista[i]`.
- **Escala**: forma cheia escala sozinha; laço de pontos em passo fixo precisa amostrar em `1/p.k`
  (ou `p.passo`) e manter o caminho original quando `p.k == 1`, para a paridade continuar exata.

## Como portar um efeito (uma onda = uma categoria)

1. Portar o `_lib.js` da categoria para `efeitos/<cat>/_lib.py` (crédito ao Hugo Duprez se o original credita).
2. Portar o efeito; `py -m pxfx.paridade <cat>/<nome>` até OK na escala 1.
3. Reescalar: `py -m pxfx.render <cat>/<nome> --escala 2.5`, corrigir os laços de ponto, olhar a folha.
4. Recolorir pela paleta regional (`--regiao blumenau --rampa ...`) e levar à aprovação (vfx-guide).

## Ondas

| Onda | Categorias | Portados |
|------|------------|----------|
| 0 | núcleo | completo (paridade exata) |
| 1 — combate | impacts, melee, projectiles, explosions, fire, spawn, status | `fire/torch` (+ `fire/_lib`) |
| 2 — mundo | water, weather, lightning, scifi, critters, nature, ice | — |
| 3 — sobrenatural | holy, shadow, arcane (redesenhados para as lendas) | — |
| 4 — interface | ui, pickups, transitions | — |
| esqueleto | `moves` e as 73 atuações | atuações extraídas como DADO em `esqueleto/biblioteca/atos_pixelfx.json` |

A fila de cada onda vive em `Desenvolvimento/Docs/TODO.md`. A cópia `../vendor/pixelfx/` sai quando a
última onda fechar.
