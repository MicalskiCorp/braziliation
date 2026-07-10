# Pipeline de IA para Sprites e Assets

Este roteiro define como usar IA sem perder a identidade visual do Braziliation. A IA deve acelerar conceito, variação e iteração; o sprite final ainda precisa de curadoria e acabamento manual.

## Objetivo

Gerar assets 2D/pixel art consistentes com:

- 320x180 de leitura final.
- 16 PPU.
- Paleta restrita.
- Diesel/clockpunk brasileiro.
- Silhueta clara.
- Estilo próprio do projeto, sem depender do nome de artistas vivos ou de obras protegidas como referência de estilo.

## Ferramentas Sugeridas

| Etapa | Ferramentas |
|-------|-------------|
| Brief e organização | Markdown, VS Code, Copilot |
| Conceito IA | ComfyUI com SDXL/Flux ou ferramenta equivalente |
| Controle de pose/composição | ControlNet, IP-Adapter, image-to-image, silhouettes próprias |
| Pixel pass | Aseprite, LibreSprite ou ferramenta equivalente |
| Paleta | Aseprite palettes, Lospec como estudo, paletas próprias do projeto |
| Unity | Sprite Editor, Pixel Perfect Camera, Sprite Atlas, Presets de importação |

## Stack Recomendada

### Melhor Opção Para o Projeto

Use **ComfyUI + modelo base SDXL/Flux + ControlNet/IP-Adapter + Aseprite**.

Motivo: o Braziliation precisa de consistência visual, não só imagens bonitas. ComfyUI permite montar workflows repetíveis, reaproveitar seed, carregar imagens de referência, fixar etapas e salvar o processo. Aseprite entra como etapa obrigatória para transformar a saída da IA em sprite real de jogo.

### Alternativas por Perfil

| Perfil | Ferramentas | Quando usar |
|--------|-------------|-------------|
| Rápido e simples | Ferramenta online de geração + Aseprite | Ideias iniciais, mood e thumbnails |
| Controle local | ComfyUI + SDXL/Flux + ControlNet/IP-Adapter | Pipeline principal do projeto |
| Pintura/overpaint | Krita + plugin de IA + Aseprite | Refinar concepts e props antes do pixel pass |
| Pixel art manual | Aseprite ou LibreSprite | Sprite final, animação e limpeza |
| Paleta | Aseprite, Lospec, paletas próprias | Criar, comparar e limitar cores |
| Unity final | Unity Sprite Editor, Tile Palette, Sprite Atlas | Importação, slicing, tilemaps e validação em cena |

## Organização na Estrutura do Projeto

```text
Design/ArteFonte/IA/
├── ContextPacks/     # contexto enviado para IA por asset ou lote
├── Outputs/          # todas as gerações brutas
├── Selected/         # variações escolhidas para pixel pass
├── Rejected/         # descartes úteis para auditoria visual
└── Models/           # notas sobre modelos, LoRAs e configurações usadas

Design/ArteFonte/Aseprite/
└── ...               # .aseprite, paletas e spritesheets de trabalho

Design/ArteConceitual/
└── ...               # conceitos aprovados e referências visuais

Desenvolvimento/Assets/Art/
└── ...               # PNG/spritesheet final importado no Unity
```

Regra prática: **IA gera em `ArteFonte/IA`, Aseprite limpa em `ArteFonte/Aseprite`, conceito aprovado fica em `ArteConceitual`, asset final entra em `Assets/Art`.**

## Regra Legal e Criativa

- Treine modelos/LoRAs apenas com arte própria, material licenciado ou domínio público confirmado.
- Não use nomes de artistas vivos como atalho de prompt.
- Não use sprites extraídos de jogos comerciais como dataset.
- Use as artes aprovadas do próprio Braziliation como âncoras de estilo.

## Fluxo Operacional

### Roteiro Recomendado

Este é o fluxo que deve ser usado para cada asset novo:

1. **Escolher a origem criativa:** pegue a feature em `Design/Criativo/` ou `Desenvolvimento/Docs/GDD/Features/`.
2. **Criar um context pack:** use [`context-pack-template.md`](context-pack-template.md) dentro de `Design/ArteFonte/IA/ContextPacks/{asset}/`.
3. **Definir escala e paleta:** confirme tamanho no [`sprite-scale-guide.md`](sprite-scale-guide.md) e paleta no [`palette-guide.md`](palette-guide.md).
4. **Montar prompt por camadas:** combine visão global, cidade/região, função do asset, restrições técnicas e prompt negativo.
5. **Gerar thumbnails:** faça 6 a 12 variações pequenas em IA, sem tentar finalizar.
6. **Selecionar direção:** escolha 1 ou 2 variações e salve em `Design/ArteFonte/IA/Selected/`.
7. **Redesenhar no Aseprite:** faça pixel pass manual em tamanho real, com paleta reduzida.
8. **Animar se necessário:** use tags do Aseprite e siga [`animation-guide.md`](animation-guide.md).
9. **Exportar para Unity:** salve PNG/spritesheet em `Desenvolvimento/Assets/Art/`.
10. **Validar em cena:** teste em 320x180, 16 PPU, em fundo real ou cena sandbox.
11. **Registrar:** atualize `Desenvolvimento/Docs/Architecture/indices/assets.md`.

Exemplo preenchido: `Design/ArteFonte/IA/ContextPacks/exemplo-prop-comporta-blumenau/context.md`.

## Como Passar Contexto Para a IA

A melhor forma não é mandar um prompt gigante solto. Use um pacote de contexto com partes fixas e partes variáveis.

### Pacote Mínimo

Todo pedido de asset deve ter:

- **Brief:** função, região, tamanho, paleta e caminho final.
- **Contexto do mundo:** dieselpunk brasileiro, pós-apocalipse, pixel art SNES-era.
- **Contexto regional:** exemplo: Blumenau clockpunk, enxaimel, rio Itajaí-Açu, cheias, engrenagens e clero.
- **Restrições técnicas:** 16 PPU, canvas, sprite side-view, paleta limitada, sem gradiente suave.
- **Referências autorizadas:** sprites próprios, conceitos próprios, silhuetas próprias, paleta do projeto.
- **Prompt negativo:** o que a IA deve evitar.

### Prompt em Camadas

Monte prompts assim:

```text
[GLOBAL STYLE]
pixel art sprite for a 2D side-scrolling action platformer, SNES-era readability, limited 16 color palette, clear silhouette, Brazilian post-apocalyptic dieselpunk

[REGION]
Blumenau clockpunk district, colonial-german timber architecture influence, flood marks, aged brass gears, dark iron, wet wood, muddy water stains

[ASSET]
32x32 side-view floodgate lever prop, readable silhouette, one interaction point, brass handle, iron base, wet wooden support

[TECHNICAL]
orthographic side view, no background, transparent background, readable at 320x180, designed for 16 PPU, no smooth gradients, no painterly rendering
```

Prompt negativo:

```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, generic fantasy, modern sci-fi, text, watermark, copyrighted character
```

### Configurações Práticas

| Tipo de Asset | Melhor abordagem |
|---------------|------------------|
| Prop pequeno | Text-to-image ou image-to-image com canvas simples; pixel pass obrigatório |
| Personagem | Silhueta própria + image-to-image + ControlNet/IP-Adapter |
| Inimigo | Thumbnail IA para forma geral; redesenho manual para combate e hitbox |
| Tileset | Começar manual no Aseprite; usar IA mais para mood/conceito do material |
| Background | IA pode ajudar mais, mas precisa redução de paleta e ajuste de leitura |
| UI | Melhor fazer manual; IA só para ideias de ornamentação e textura |

### Configurações de Geração

- Comece com canvas maior para conceito, mas finalize manualmente no tamanho real.
- Use seed fixa por lote.
- Salve o prompt, seed, modelo e referências usadas no context pack.
- Use denoise baixo em image-to-image quando a silhueta já estiver aprovada.
- Gere em lote pequeno e compare lado a lado, não uma imagem por vez.
- Nunca aprove sprite direto da IA sem limpeza manual.

### 1. Brief

Crie um brief usando [`asset-brief-template.md`](asset-brief-template.md). Nenhum asset deve começar só com “faz um sprite de X”. O brief fixa função, escala, paleta, região e restrições.

### 2. Referências Autorizadas

Monte uma pasta de trabalho em `Design/ArteFonte/IA/` com:

- Brief do asset.
- Silhueta simples desenhada manualmente, se houver.
- Paleta aprovada.
- Sprites âncora do projeto.
- Referências próprias ou licenciadas.

### 3. Geração de Variações

Use IA para gerar 6 a 12 variações pequenas. Nesta fase, aceite imperfeição; o objetivo é explorar forma, materiais e atmosfera.

Configurações recomendadas:

- Seed fixa por lote para comparações.
- Prompt base fixo por cidade/região.
- Variação controlada apenas em pose, prop, material ou expressão.
- Image-to-image com denoise baixo quando partir de silhueta aprovada.

### 4. Seleção

Escolha 1 ou 2 candidatos usando checklist:

- Silhueta funciona em tamanho pequeno?
- A leitura é dieselpunk brasileiro ou ficou genérica?
- O asset conversa com paleta e materiais da região?
- Dá para transformar em sprite sem redesenhar tudo?

### 5. Pixel Pass Manual

Abra o candidato no Aseprite e redesenhe em resolução real. Não basta reduzir imagem gerada. O pixel pass deve:

- Limpar ruído.
- Reduzir cores.
- Ajustar clusters de pixel.
- Reforçar outline/sombra de contato.
- Alinhar ao grid e ao tamanho previsto.
- Corrigir materiais para a paleta oficial.

### 6. Animação

Para animações, gere ou desenhe keyframes primeiro. Depois interpole manualmente poucos frames. Use tags do Aseprite para exportar spritesheets.

### 7. Export para Unity

Exporte PNG/spritesheet para `Desenvolvimento/Assets/Art/`.

Import settings recomendados:

- Texture Type: Sprite (2D and UI)
- Sprite Mode: Single ou Multiple conforme spritesheet
- Pixels Per Unit: 16
- Filter Mode: Point
- Compression: None
- Mipmap: Off

### 8. Registro

Atualize `Desenvolvimento/Docs/Architecture/indices/assets.md` com o asset aprovado e registre a paleta usada.

## Prompt Base

Use em inglês quando a ferramenta responder melhor, mas mantenha os conceitos do projeto:

```text
pixel art sprite for a 2D side-scrolling action platformer, SNES-era readability, 16-bit style constraints, limited 16 color palette, clear silhouette, Brazilian post-apocalyptic dieselpunk, aged brass, dark iron, wet wood, soot, handcrafted machinery, readable at 320x180, orthographic side view, no smooth gradients, no high resolution texture, no painterly rendering
```

Prompt negativo:

```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, realistic skin pores, modern sci-fi, generic fantasy, copyrighted character, text, watermark
```

## Exemplo — Prop de Blumenau

```text
pixel art prop, side view, 32x32 canvas, old clockpunk floodgate mechanism from Blumenau, Brazilian colonial-german timber architecture influence, aged brass gears, dark iron frame, wet wood planks, muddy water stains, limited 16 color palette, strong silhouette, readable at 320x180, SNES-era 2D platformer asset
```

## Como Criar Consistência Forte com IA

1. Definir 5 a 10 sprites âncora feitos/retocados manualmente.
2. Usar sempre a mesma paleta por região.
3. Manter prompt base fixo por cidade.
4. Usar ControlNet/silhueta própria para poses e proporção.
5. Treinar LoRA apenas com assets aprovados do próprio projeto quando houver volume suficiente.
6. Fazer pixel pass manual obrigatório antes de entrar no Unity.
7. Revisar assets em lote: personagem + inimigo + prop + tile + background.

## Quando Treinar um LoRA

Treine apenas depois de ter pelo menos 30 a 80 imagens aprovadas do próprio Braziliation, idealmente separadas por categoria:

- Personagens/NPCs.
- Props e máquinas.
- Tiles e cenários.
- VFX/UI.

Antes disso, prefira prompt fixo, paleta fixa, image-to-image e pixel pass manual.

## Trilha de Estudo

### Fase 1 — Fundamentos de Pixel Art

- Estudar clusters, contraste, silhueta, anti-aliasing manual, dithering e limitação de paleta.
- Buscar no YouTube: `AdamCYounis pixel art class`, `Brandon James Greer pixel art beginner`, `Pixel Pete pixel art basics`, `Saultoons pixel art character`.

### Fase 2 — Aseprite e Animação

- Estudar tags, onion skin, timeline, export de spritesheet e paletas.
- Buscar no YouTube: `MortMort Aseprite animation`, `Aseprite sprite sheet export`, `AdamCYounis Aseprite workflow`.

### Fase 3 — Unity 2D Pixel Perfect

- Estudar import settings, 16 PPU, Sprite Editor, Tilemap, Rule Tile, Sprite Atlas e Pixel Perfect Camera.
- Buscar no YouTube: `Unity 2D Pixel Perfect Camera official`, `Unity Tilemap 2D tutorial`, `Unity Sprite Atlas 2D pixel art`.

### Fase 4 — IA Controlada para Game Art

- Estudar Stable Diffusion/ComfyUI, image-to-image, ControlNet, IP-Adapter, seed, denoise e LoRA.
- Buscar no YouTube: `ComfyUI beginner workflow`, `Stable Diffusion img2img game assets`, `ControlNet pose reference workflow`, `Kohya LoRA training basics`.

### Fase 5 — Pipeline Próprio

- Criar sprites âncora do Braziliation.
- Criar paletas por cidade.
- Criar prompts base por região.
- Testar lote pequeno: 1 personagem, 1 inimigo, 1 prop, 1 tile e 1 VFX.
- Revisar tudo junto em uma cena sandbox no Unity.

## Vídeos/Temas Recomendados Para Buscar

| Tema | Busca sugerida |
|------|----------------|
| Fundamentos de pixel art | `AdamCYounis pixel art fundamentals` |
| Personagens em pixel art | `Brandon James Greer character pixel art` |
| Animação no Aseprite | `MortMort Aseprite animation tutorial` |
| Tilesets 2D | `pixel art tileset tutorial 16x16` |
| Unity Tilemap | `Unity 2D Tilemap official tutorial` |
| Pixel Perfect Unity | `Unity Pixel Perfect Camera 2D tutorial` |
| ComfyUI | `ComfyUI beginner guide stable diffusion` |
| ControlNet | `ControlNet img2img workflow game art` |
| LoRA próprio | `Kohya LoRA training own dataset` |

## Checklist Final

- [ ] Brief preenchido.
- [ ] Paleta definida.
- [ ] Referências autorizadas.
- [ ] IA usada só para rascunho/variação ou como base controlada.
- [ ] Pixel pass manual feito.
- [ ] Sprite lê em 320x180.
- [ ] Export com 16 PPU.
- [ ] Asset final em `Desenvolvimento/Assets/Art/`.
- [ ] Índice de assets atualizado.
