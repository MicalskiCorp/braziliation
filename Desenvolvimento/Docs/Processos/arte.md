# Arte

> Camada lateral · Design · Fonte canônica: [`sprite-artist.md`](../../../.claude/agents/sprite-artist.md) · skills [`concept-art`](../../../.claude/skills/concept-art/SKILL.md), [`novo-asset`](../../../.claude/skills/novo-asset/SKILL.md), [`sprite-pipeline`](../../../.claude/skills/sprite-pipeline/SKILL.md) · guias [`pipeline-ia-sprites.md`](../../../Design/GuiasDeArte/pipeline-ia-sprites.md), [`pipeline-sprites-programaticos.md`](../../../Design/GuiasDeArte/pipeline-sprites-programaticos.md). Este manual resume; em divergência, vale a fonte.

Dono **@SpriteArtist** (executa) + **usuário** (aprova e direciona) · Pastas **ArteConceitual · ArteFonte · GuiasDeArte** · Registro **Docs/Architecture/indices/assets.md**

Todo asset percorre 5 etapas, cada uma acionada manualmente e fechada por um registro: **1** ideia no Criativo → **2** concept art aprovado → **3** especificação de variações → **4** spec JSON → **5** sprite em `Assets/Art/`. Props simples pulam 2 e 3. Restrições do ADR-004: 640×360, 32 PPU, tile 32×32, player ~64 px, até 32 cores por sprite.

| Rota | Técnica | Para | Processo |
|---|---|---|---|
| A — Programática | Spec JSON pixel a pixel → `render_spec.py` | Props mecânicos, ícones, objetos até ~48×48 | A3 |
| B — Procedural | Geradores com seed (`gen_tileset.py`, `gen_map_wfc.py`) | Tiles e mapas em volume | A4 |
| C — Difusão | ComfyUI + SDXL + LoRA, pixel pass manual | Personagens, inimigos, concept de cena | A2 |
| D — Acabamento | Aseprite, import automático no Unity | Toda entrada de asset no Unity | A5 |

## A1 — Novo asset (brief e context pack)

**Quem:** @SpriteArtist · skill `novo-asset`
**Aciona:** Pedido de asset sem brief — nenhum asset começa com "faz um sprite de X"

1. Ler os templates `asset-brief-template.md`, `context-pack-template.md` e, se houver várias ações, `variation-spec-template.md`.
2. Localizar a origem criativa no Criativo ou em `GDD/Features/`; sem origem, avisar.
3. Personagem, inimigo ou boss: exigir concept art aprovado (`concept.md` com `status: aprovado`) e, com múltiplas ações, `variations.md` preenchido.
4. Definir função, região, tamanho (`sprite-scale-guide.md`), paleta, destino com prefixo (`chr_`, `enm_`, `env_`, `prop_`, `ui_`, `vfx_`) e rota.
5. Criar `ContextPacks/{asset}/context.md` (referência: `exemplo-prop-comporta-blumenau/`).
6. Registrar a produção no TODO de Dev.

- **Gate:** Sem concept aprovado, personagem não ganha context pack
- **Próximo:** A2 ou A3

## A2 — Concept art de cena (rota C)

**Quem:** @SpriteArtist + usuário · skill `concept-art`
**Aciona:** Etapa 2 de personagens e criaturas — desde 2026-07-26, concept de **cena completa**, não sprite isolado

1. Pré-voo: a paleta da região existe (mesmo como proposta)?
2. Brief (A1) e referências visuais em `ArteConceitual/ReferenciasVisuais/{tema}/`, com `fontes.md`.
3. Prompt em camadas: visão global, região, função, restrições técnicas, negativo.
4. Gerar 6 a 12 thumbnails com `comfy_batch.py` (texto, ou `--reference-image` com denoise 0,4–0,6); cada lote ganha linha em `lotes.md` com seed e o que mudou.
5. Decidir cada imagem: aprovar → `Selected/`; descartar → `Rejected/`; iterar → novo lote anotado. Teto de 3 lotes por pedido de ajuste.
6. Salvar o concept aprovado em `ArteConceitual/{categoria}/{asset}/concept.png` + `concept.md` com o contexto completo.
7. Depois da aprovação: `pixelize.py` → pixel pass no Aseprite → animação por tags → export → validar em cena 640×360 → registrar.

- **Gate:** Só o usuário aprova concept · nada vira asset final sem pixel pass · imagem nunca descartada sem registro
- **Regras de prompt:** Sem artista vivo; humanoide leva o negativo de nudez e roupa descrita por peça concreta
- **Em curso:** Edith (lote 12) e Soldado Clérico (6 thumbnails)

## A3 — Sprite programático (rota A)

**Quem:** @SpriteArtist · skill `sprite-pipeline`
**Aciona:** Ciclo gerar → visualizar → criticar → refinar

1. Ler o guia canônico, `style-bible.md` e `sprite-scale-guide.md`; carregar a paleta da região.
2. Confirmar brief, context pack e, se animado, `variations.md` mapeando cada ação para um id.
3. Escrever a spec consolidada `{asset}.spec.json`: silhueta em 1 cor primeiro, depois detalhe; um `output` por frame e `sheets` por animação.
4. `py render_spec.py {spec}` → PNGs e sheets em `IA/Outputs/`.
5. `upscale_preview.py -s 8 --grid` e `mock_scene.py`; abrir as imagens e criticar pela checklist (silhueta em 1×, leitura dieselpunk, contraste de valor, sem pixel órfão, só cores da paleta).
6. Retoque fino opcional pelo MCP `aseprite`, registrado na spec.
7. Gate `palette_check.py` para cada output e sheet.
8. PNG em `Selected/`; export para `Assets/Art/` quando pedido; linha movida para "Assets Registrados" em `assets.md`.

- **Gate:** `palette_check` APROVADO · nunca PNG sem spec versionada

## A4 — Tiles e mapas procedurais (rota B)

**Quem:** @SpriteArtist · `gen_tileset.py` · `gen_map_wfc.py`

1. Gerar tiles pela família (`enxaimel`, `metal`, `agua`) com paleta e seed; `--scale 2` entrega 32×32 com detail pass.
2. Montar o mapa por Wave Function Collapse com um ruleset `rulesets/{regiao}-{cena}.json` — de preferência derivado de um exemplo desenhado (`--learn`).
3. Fixar marcos autorais com `--pin X,Y=tile`.
4. Tratar o aviso de tile órfão como erro de ruleset.
5. Saídas: PNG, `.map.json` (legível), `.unity.json` (máquina) e `.manifest.json` (reprodutibilidade).
6. Preview passa pelo `palette_check.py`; o Unity importa pelo `WfcMapImporter` (A5).

- **Princípio:** A IA escreve o gerador, não é o gerador — o mapa sai de código com seed

## A5 — Entrada no Unity (rota D)

**Quem:** Editor tools · @UnityDeveloper no wiring

1. `SpriteImportPostprocessor` força 32 PPU, Point, sem compressão e sem mipmap em tudo que entra em `Assets/Art/`.
2. `SheetAutoSlicer` fatia `*_sheet.png` em grade quadrada com pivot no centro-inferior, preservando IDs.
3. `Assets > Braziliation > Criar Animação do Spritesheet` gera clip e controller.
4. `Assets > Braziliation > Importar Mapa WFC...` pinta o Tilemap a partir do `.unity.json`.
5. Prefab, animator e cena ficam com o @UnityDeveloper (I5).

- **Gate:** meta-check (todo asset com `.meta`) e `check_art_palettes.py` no pre-commit

## A6 — Nova paleta de região

**Quem:** Usuário (direção) + skill `nova-cidade`

1. Derivar a "Paleta Base Sugerida" do `palette-guide.md`.
2. Adicionar camadas da região só com direção do usuário (materiais, clima, tema).
3. Salvar `ArteConceitual/Paletas/{regiao}.json` com `"status": "proposta-inicial"` e registrar a seção no `palette-guide.md`.
4. Apontar os PNGs da região em `Paletas/regras-assets.json` para o gate em lote.

- **Gate:** Paleta nova sem registro é proibida

## A7 — Registro e rastreio de assets

**Quem:** Quem exporta

1. A linha do asset nasce em "Backlog por Asset" de `indices/assets.md` quando a ideia fecha (C5/C8).
2. Cada etapa concluída marca sua coluna: Concept Art, Especificado, Spec JSON, Sprite Gerado.
3. Exportado, a linha vai para "Assets Registrados", com a paleta usada.
4. Pendências de produção ficam na seção "UI e arte" do TODO de Dev.

- **Terceiros:** Placeholders CC0 (Gothicvania) listados em `CREDITS.md` até a Onda 3 substituí-los

---

[← Manual de processos](index.md)
