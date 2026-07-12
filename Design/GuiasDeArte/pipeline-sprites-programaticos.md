# Pipeline Programático de Sprites

Este guia define como gerar sprites pixel art **por código e por agente de IA**, usando a direção de arte do projeto como especificação executável. Complementa o [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md) (geração por difusão/ComfyUI): aquele cobre conceito e arte orgânica; este cobre sprites construídos programaticamente, com validação automática de paleta, escala e leitura.

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
| **A — Pixel programático** | Agente escreve spec JSON pixel a pixel; `render_spec.py` gera o PNG | Props mecânicos, ícones, objetos 16×16–32×32 | Sim (para criar; PNG final não) |
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
4. **Escrever a spec**: `{asset}.spec.json` dentro do context pack — matriz de chars usando somente keys da paleta.
5. **Renderizar**: `python render_spec.py {asset}.spec.json -o ../../Outputs/{asset}.png`.
6. **Visualizar e criticar** (o coração do ciclo — repetir até aprovar):
   - `python upscale_preview.py {asset}.png -s 8 --grid` → inspecionar ampliado;
   - `python mock_scene.py {asset}.png {paleta}.json` → inspecionar leitura em 320×180 real;
   - criticar contra a checklist abaixo; ajustar a spec e voltar ao passo 5.
7. **Validar paleta**: `python palette_check.py {asset}.png {paleta}.json` deve APROVAR.
8. **Curadoria**: mover PNG aprovado para `Design/ArteFonte/IA/Selected/`; a spec permanece no context pack como fonte.
9. **Export**: copiar para `Desenvolvimento/Assets/Art/{destino}` conforme convenções de nome do `Docs/Architecture/Assets/AssetsStructure.md` — import settings são automáticos (`SpriteImportPostprocessor`).
10. **Registrar**: atualizar `Desenvolvimento/Docs/Architecture/indices/assets.md`.

### Checklist de crítica visual (passo 6)

- [ ] Silhueta reconhecível só pela forma, em 1x, no mock 320×180?
- [ ] Leitura dieselpunk brasileiro (desgaste, remendo, materiais do projeto) ou ficou genérico?
- [ ] Contraste de valor separa o asset do fundo (não saturação)?
- [ ] Highlight apenas nos pontos que guiam o olhar?
- [ ] Sem microdetalhe que desaparece em 1x? Sem pixels órfãos?
- [ ] Clusters de pixel limpos, outline/sombra de contato onde a style-bible pede?
- [ ] Todas as cores pertencem à paleta da região (máx. 16)?

## Animação na rota programática

Quando o brief pede animação (ver contagens em [`animation-guide.md`](animation-guide.md)):

1. **O frame 1 é o idle** — deve funcionar como sprite parado (regra do animation-guide). É o sprite base já aprovado no ciclo.
2. **Uma spec por frame**: `{asset}_f2.spec.json`, `{asset}_f3.spec.json`… no mesmo context pack. Canvas, base e elementos estáticos **idênticos entre frames**; anima apenas o que se move (em pixel art, 1–2 px de deslocamento já são muito).
3. **Cada frame passa pelo ciclo visual** individualmente (preview ampliado + crítica).
4. **Empacotar**: `python sheet_pack.py -o {asset}_{acao}_sheet.png f1.png f2.png f3.png` — nome no padrão do animation-guide (`*_sheet.png`).
5. **Validar o sheet**: `palette_check.py` no sheet final; inspecionar o preview do sheet para conferir a leitura do arco de movimento.
6. **Export e registro** normais (passos 9–10). No Unity, o wiring é automatizado:
   - **Slicing automático**: `Assets/Editor/Art/SheetAutoSlicer.cs` detecta `*_sheet.png` em `Assets/Art/` e aplica `Sprite Mode: Multiple` + grid de frames quadrados (frame = altura do sheet), pivot bottom-center, preservando IDs em reimports;
   - **Clip + Animator**: selecionar o sheet fatiado no Project e rodar `Assets > Braziliation > Criar Animação do Spritesheet` — gera `.anim` (8 fps, sem loop) + `.controller` em `Assets/Animations/World/`;
   - Ligar o Animator ao GameObject/prefab do prop continua sendo wiring de cena do `@UnityDeveloper`.

## Fluxo da Opção B — geradores procedurais

Geradores paramétricos vivem em `Design/ArteFonte/Ferramentas/` com prefixo `gen_` (ex.: `gen_tileset.py`). Regras:

- Parâmetros lidos da paleta JSON da região — nunca cores hardcoded.
- Seed obrigatória e registrada no context pack (reprodutibilidade).
- Saída em `Design/ArteFonte/IA/Outputs/`, mesma curadoria da Opção A.

*(Status: geradores ainda não implementados — ver TODO.md.)*

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
