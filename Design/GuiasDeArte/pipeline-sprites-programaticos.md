# Pipeline Programático de Sprites

Este guia define como gerar sprites pixel art **por código e por agente de IA**, usando a direção de arte do projeto como especificação executável. Complementa o [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md) (geração por difusão/ComfyUI): aquele cobre conceito e arte orgânica; este cobre sprites construídos programaticamente, com validação automática de paleta, escala e leitura.

## Fluxo completo: da ideia ao sprite (5 etapas)

Este pipeline (Opção A) é a etapa final de um fluxo maior, que começa na camada criativa e passa pela concept art antes de virar spec JSON:

| # | Etapa | Onde vive | TODO/registro que fecha a etapa |
|---|-------|-----------|----------------------------------|
| 1 | Ideia/lore do personagem/objeto/cenário | `Design/Criativo/` (MDs existentes por estrutura) | Seção "Concept Art Pendente" em [`Design/Criativo/TODO.md`](../Criativo/TODO.md) |
| 2 | Concept art (motor de IA à escolha) + aprovação do usuário | `Design/ArteConceitual/{categoria}/{asset}/` | Linha "Concept Art" em `Desenvolvimento/Docs/Architecture/indices/assets.md` |
| 3 | Especificação de variações (movimentos, ataques, estados) | Brief/context pack, ou [`variation-spec-template.md`](variation-spec-template.md) para entidades complexas | Linha "Especificado" no mesmo índice |
| 4 | Spec JSON consolidada (este guia, Opção A) | `Design/ArteFonte/IA/ContextPacks/{asset}/{asset}.spec.json` | Linha "Spec JSON" no mesmo índice |
| 5 | Geração do sprite a partir da spec | `Desenvolvimento/Assets/Art/` | Linha "Sprite Gerado" no mesmo índice |

Cada etapa é acionada manualmente pelo usuário lendo o registro da etapa anterior — mesmo modelo reativo do resto do projeto (`AGENTS.md` → "Fluxo entre Camadas"). Nenhuma etapa pula a anterior nem invoca a seguinte sozinha.

## Princípio: cristalização (sem lock-in)

**Nenhuma peça deste pipeline exige um agente ou modelo específico em runtime.** O agente acelera a construção; o entregável é sempre um artefato versionado no repositório:

- Ferramentas são scripts Python puros em `Design/ArteFonte/Ferramentas/` — rodam sozinhos.
- Cada sprite tem uma **spec JSON** (fonte) + PNG (saída) — reproduzível por qualquer operador.
- Paletas são JSON em `Design/ArteConceitual/Paletas/` derivados do [`palette-guide.md`](palette-guide.md).
- O fallback humano é sempre o Aseprite, como já previsto no pipeline de IA.

Qualquer modelo multimodal num harness agêntico (Claude, Copilot, Cursor) executa o mesmo processo; muda a qualidade do resultado, não o processo.

## As 4 Opções de Geração

| Opção | Técnica | Melhor para | Precisa de LLM p/ rodar? |
|-------|---------|-------------|--------------------------|
| **A — Pixel programático** | Agente escreve spec JSON pixel a pixel; `render_spec.py` gera o PNG | Props mecânicos, ícones, objetos até ~48×48 (acima disso, preferir rota C + pixel pass) | Sim (para criar; PNG final não) |
| **B — Procedural** | Geradores paramétricos (tilesets, ferrugem, dithering) | Tiles, variações de cenário em volume | Não (código puro, seed fixa) |
| **C — Difusão** | ComfyUI + SDXL/Flux conforme [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md) | Personagens, inimigos, concepts orgânicos | Não (SD local; LLM só automatiza) |
| **D — Acabamento/Unity** | Scripts Lua Aseprite, import automático, registro | Toda entrada de asset no Unity | Não |

## Pré-requisitos

- Python 3.10+ com Pillow (`pip install pillow`).
- Ferramentas em [`Design/ArteFonte/Ferramentas/`](../ArteFonte/Ferramentas/index.md).
- Paleta da região em `Design/ArteConceitual/Paletas/{regiao}.json` (se não existir, derivar do [`palette-guide.md`](palette-guide.md) e marcar `"status": "proposta-inicial"`).

## Fluxo da Opção A — ciclo gerar → visualizar → criticar → refinar

1. **Brief e contexto**: preencher [`asset-brief-template.md`](asset-brief-template.md) e criar context pack em `Design/ArteFonte/IA/ContextPacks/{asset}/` — mesmo fluxo do pipeline de IA.
2. **Escala e paleta**: confirmar tamanho no [`sprite-scale-guide.md`](sprite-scale-guide.md) e paleta JSON da região.
3. **Silhueta primeiro**: rascunhar a spec só com silhueta (1 cor + transparente) e validar a forma antes de detalhar — regra nº 4 da [`style-bible.md`](style-bible.md).
4. **Escrever a spec**: `{asset}.spec.json` dentro do context pack — **spec consolidada**: um único JSON por objeto, com um `output` por frame/variação e, se houver animação, uma entrada em `sheets` listando a sequência (ver [formato completo](#formato-da-spec-consolidada) abaixo). Se o passo 3 gerou uma especificação de variações, cada variação vira um `output` aqui.
5. **Renderizar**: `python render_spec.py {asset}.spec.json` — sem `-o`, renderiza **todos os outputs** (um PNG por id) e monta automaticamente qualquer sheet declarada, tudo em `../../Outputs/`. Para iterar só um frame durante a crítica: `python render_spec.py {asset}.spec.json --only f2 -o ../../Outputs/{asset}_f2.png`.
6. **Visualizar e criticar** (o coração do ciclo — repetir até aprovar):
   - `python upscale_preview.py {asset}.png -s 8 --grid` → inspecionar ampliado (repetir por output relevante);
   - `python mock_scene.py {asset}.png {paleta}.json` → inspecionar leitura em 640×360 real;
   - criticar contra a checklist abaixo; ajustar a spec e voltar ao passo 5.
7. **Validar paleta**: `python palette_check.py {asset}.png {paleta}.json` deve APROVAR (repetir para cada output e para o sheet, se houver).
8. **Curadoria**: mover PNG aprovado para `Design/ArteFonte/IA/Selected/`; a spec permanece no context pack como fonte.
9. **Export**: copiar para `Desenvolvimento/Assets/Art/{destino}` conforme convenções de nome do `Docs/Architecture/Assets/AssetsStructure.md` — import settings são automáticos (`SpriteImportPostprocessor`).
10. **Registrar**: atualizar `Desenvolvimento/Docs/Architecture/indices/assets.md`.

### Checklist de crítica visual (passo 6)

- [ ] Silhueta reconhecível só pela forma, em 1x, no mock 640×360?
- [ ] Leitura dieselpunk brasileiro (desgaste, remendo, materiais do projeto) ou ficou genérico?
- [ ] Contraste de valor separa o asset do fundo (não saturação)?
- [ ] Highlight apenas nos pontos que guiam o olhar?
- [ ] Sem microdetalhe que desaparece em 1x? Sem pixels órfãos?
- [ ] Clusters de pixel limpos, outline/sombra de contato onde a style-bible pede?
- [ ] Todas as cores pertencem à paleta da região (máx. 32 — ADR-004)?

## Formato da spec consolidada

Um JSON por objeto — todos os frames e variações do mesmo asset vivem no mesmo arquivo:

```json
{
  "name": "prop_blumenau_floodgate_lever",
  "size": [32, 32],
  "palette": "../../ArteConceitual/Paletas/blumenau.json",
  "outputs": [
    {"id": "idle", "rows": ["................", "......77........", "..."]},
    {"id": "f2",   "rows": ["...", "..."]},
    {"id": "f3",   "rows": ["...", "..."]}
  ],
  "sheets": {
    "activate": ["idle", "f2", "f3"]
  }
}
```

- Cada entrada em `outputs` é um frame ou uma variação (mesma regra de `rows` de sempre: 1 char por pixel, `.` = transparente, demais chars = key da paleta).
- `id: "idle"` (ou `"default"`) renderiza para `{name}.png`; qualquer outro id renderiza para `{name}_{id}.png` — mesma convenção de nomes de antes, só que a partir de uma fonte única.
- `sheets` é opcional: cada chave vira `{name}_{chave}_sheet.png`, empacotando os outputs listados na ordem dada. Sem `sheets`, o objeto ainda pode representar variações que não são animação (ex.: 4 estados de cor de um marcador), cada uma com seu próprio PNG.
- `render_spec.py` continua lendo o formato legado (`"rows"` no topo, 1 arquivo por frame) para as ~19 specs já entregues antes desta migração — não é necessário reautorar histórico. **Specs novas nascem sempre no formato consolidado.**

## Animação na rota programática

Quando o brief pede animação (ver contagens em [`animation-guide.md`](animation-guide.md)):

1. **O output `idle` é o frame base** — deve funcionar como sprite parado (regra do animation-guide). É o sprite aprovado no ciclo antes de adicionar os demais outputs.
2. **Um `output` por frame** dentro do mesmo `{asset}.spec.json`: `f2`, `f3`… Canvas, base e elementos estáticos **idênticos entre frames**; anima apenas o que se move (em pixel art, 1–2 px de deslocamento já são muito).
3. **Cada output passa pelo ciclo visual** individualmente — use `--only {id}` para renderizar e inspecionar um de cada vez durante a iteração.
4. **Declarar a sequência em `sheets`**: `"sheets": {"{acao}": ["idle", "f2", "f3"]}` — `render_spec.py` monta `{asset}_{acao}_sheet.png` automaticamente ao renderizar a spec inteira (sem precisar rodar `sheet_pack.py` à parte).
5. **Validar o sheet**: `palette_check.py` no sheet final; inspecionar o preview do sheet para conferir a leitura do arco de movimento.
6. **Export e registro** normais (passos 9–10). No Unity, o wiring é automatizado:
   - **Slicing automático**: `Assets/Editor/Art/SheetAutoSlicer.cs` detecta `*_sheet.png` em `Assets/Art/` e aplica `Sprite Mode: Multiple` + grid de frames quadrados (frame = altura do sheet), pivot bottom-center, preservando IDs em reimports;
   - **Clip + Animator**: selecionar o sheet fatiado no Project e rodar `Assets > Braziliation > Criar Animação do Spritesheet` — gera `.anim` (8 fps, sem loop) + `.controller` em `Assets/Animations/World/`;
   - Ligar o Animator ao GameObject/prefab do prop continua sendo wiring de cena do `@UnityDeveloper`.

## Re-autoria de specs 1× (legado pré-ADR-004)

Specs criadas no grid antigo (320x180/16 PPU) são re-autoradas com [`spec_redetail.py`](../ArteFonte/Ferramentas/spec_redetail.py): expansão EPX (suaviza degraus de curvas/diagonais) + textura de material com seed determinística, emitindo **spec 2× versionada** (`{nome}.2x.spec.json`) + PNG. O resultado é ponto de partida — passa pelo ciclo de crítica visual normal e recebe retoques manuais na spec 2×, que vira a fonte atual do asset. Specs novas nascem direto no grid do ADR-004.

## Fluxo da Opção B — geradores procedurais

Geradores paramétricos vivem em `Design/ArteFonte/Ferramentas/` com prefixo `gen_`. Regras:

- Parâmetros lidos da paleta JSON da região — nunca cores hardcoded.
- Seed obrigatória; cada geração grava um `*.manifest.json` ao lado do PNG (gerador, família, seed, paleta) — esse manifest É o registro de reprodutibilidade.
- Saída em `Design/ArteFonte/IA/Outputs/`, mesma curadoria da Opção A.

### Camada de nível: montar os tiles em mapa (WFC)

`gen_tileset.py` gera os **tiles**; [`gen_map_wfc.py`](../ArteFonte/Ferramentas/gen_map_wfc.py) os **monta em mapa** por Wave Function Collapse — o mesmo algoritmo que gera nível em Bad North, Caves of Qud e Townscaper. Regras são declaradas como "o que pode encostar em quê", então o resultado nunca produz parede flutuando na água.

Isto é a aplicação direta do princípio que rege a geração procedural em produção: **a IA escreve o gerador, não é o gerador.** O agente escreve e afina as regras de adjacência; o mapa sai de código puro, com seed, reproduzível sem nenhum modelo.

| Artefato | Onde |
|----------|------|
| Ruleset (vocabulário + gramática) | `Ferramentas/rulesets/{regiao}-{cena}.json` |
| Exemplo desenhado à mão (opcional) | `Ferramentas/rulesets/exemplos/*.json` |
| Saídas | `IA/Outputs/` — `{nome}.png`, `{nome}.map.json`, `{nome}.manifest.json` |

Dois modos de obter a gramática:

- **À mão** — escrever `adjacency` no ruleset. Controle total, mais trabalhoso. Chaves iniciadas por `_` são anotações e são ignoradas pelo parser.
- **`--learn exemplo.json`** — derivar adjacência e pesos de um trecho de mapa desenhado. **É o caminho recomendado**: o desenho *é* a gramática, e ajustar o resultado é editar uma grade de texto em vez de reescrever regras. Se o exemplo tem lâmina d'água plana, o mapa gerado tem; se tem prédio estreito, sai prédio estreito.

`--pin X,Y=tile` fixa uma célula. É o que torna WFC compatível com um jogo autoral: a Igreja Matriz fica onde o designer quer e o WFC preenche o que existe entre os marcos.

O script avisa `AVISO: {tile} nao aceita nada em '{direcao}'` quando um tile ficou órfão — sem ninguém que o aceite naquele lado, ele nunca é colocado e some do mapa em silêncio. Trate o aviso como erro de ruleset.

O gerador emite **dois** JSONs, de propósito: o `.map.json` é a versão legível (dicionários,
grade de strings) e o `.unity.json` é o formato de máquina — só arrays planos de primitivos,
porque o `JsonUtility` do Unity não desserializa dicionário nem array irregular.

No Unity, `Assets > Braziliation > Importar Mapa WFC...` (`Assets/Editor/Art/WfcMapImporter.cs`)
lê o `.unity.json`, fatia os tilesets em grade se preciso, cria um `Tile` por célula da grade em
`{pasta do tileset}/Tiles/` e pinta um Tilemap novo na cena. Reimportar reusa os Tiles existentes
em vez de duplicar. O preview PNG passa por `palette_check.py` como qualquer outro asset.

**Gerador de tiles disponível:** [`gen_tileset.py`](../ArteFonte/Ferramentas/gen_tileset.py) — 3 famílias (`enxaimel`, `metal`, `agua`), layout linhas=tipos × colunas=variações. Desenha em grid 16 e entrega tiles **32×32** via `--scale 2` (default, ADR-004) — o `--scale 2` aplica **detail pass** (EPX + textura fina via `spec_redetail`), não nearest cru; famílias novas podem também ser desenhadas nativamente em 32 (`TILE=32` + `--scale 1`). Ex.: `py gen_tileset.py enxaimel --palette blumenau.json --seed 42 -o out.png`.

## Fluxo das Opções C e D

- **C**: seguir integralmente o [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md). O agente pode montar context packs, prompts em camadas e pós-processar (quantização de paleta com `palette_check.py` como gate).
- **D**: import no Unity é automático via `Assets/Editor/Art/SpriteImportPostprocessor.cs`; scripts Lua para Aseprite entram em `Ferramentas/` quando necessários.

## Como rodar sem agente (operação manual)

Todo o fluxo A é operável por humano: editar a spec JSON em qualquer editor de texto (ou desenhar direto no Aseprite e pular specs), rodar os 4 scripts na ordem dos passos 5–7, e seguir curadoria/export normalmente. A documentação de cada script está em [`Ferramentas/index.md`](../ArteFonte/Ferramentas/index.md).

## Papéis

| Papel | Responsável |
|-------|-------------|
| Executar o pipeline (A/B) e o ciclo de crítica | `@SpriteArtist` (ou skill `sprite-pipeline`) |
| Aprovar direção de arte e exceções de paleta | Usuário/direção de arte |
| Wiring do asset no Unity (prefab, animação, cena) | `@UnityDeveloper` |
| Registro em índices | Quem exporta (passo 10) |
