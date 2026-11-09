# Pipeline de IA — fundamentos: stack, LoRA e estudo

> Complemento do [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md), o roteiro operacional da rota C (difusão), lido a cada sessão de arte. Aqui fica o que não muda de uma sessão para outra: a escolha de ferramentas, quando treinar LoRA (gate do ADR-014) e a trilha de estudo. Separado do roteiro em 2026-11-09 para ele caber no teto de 5 mil tokens.

## Ferramentas Sugeridas

| Etapa | Ferramentas |
|-------|-------------|
| Brief e organização | Markdown, VS Code, Claude Code |
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

### Gate do projeto (ADR-014, 2026-11-03)

Decisão vigente: **não treinar LoRA de estilo próprio ainda.** O assunto só reabre quando os três
critérios valerem ao mesmo tempo — a contagem oficial é a tabela "Assets Registrados" de
[`indices/assets.md`](../../Desenvolvimento/Docs/Architecture/indices/assets.md):

1. **≥ 30 imagens próprias aprovadas no grid 48 PPU**, das quais **≥ 10 de personagem/inimigo** com pixel pass fechado;
2. **modelo base decidido** — o A/B SDXL × Z-Image resolvido, porque LoRA é treinado *para* uma base (um LoRA de SDXL não serve no Z-Image);
3. **≥ 2 personagens com sheet de animação aprovado**, para o treino ter noção de pose e não só de material.

Quando reabrir, a rota é **treino em GPU alugada por hora** (`kohya_ss`), com os pesos
`.safetensors` guardados junto dos outros LoRAs e **inferência sempre local no ComfyUI**. SaaS de
treino gerenciado (tipo Scenario) está descartado — mensalidade sem relação com uso e pesos não
exportáveis. Comparativo completo em
[`decisao-lora-estilo-proprio.md`](../ArteFonte/IA/Models/decisao-lora-estilo-proprio.md).

## Trilha de Estudo

### Fase 1 — Fundamentos de Pixel Art

- Estudar clusters, contraste, silhueta, anti-aliasing manual, dithering e limitação de paleta.
- Buscar no YouTube: `AdamCYounis pixel art class`, `Brandon James Greer pixel art beginner`, `Pixel Pete pixel art basics`, `Saultoons pixel art character`.

### Fase 2 — Aseprite e Animação

- Estudar tags, onion skin, timeline, export de spritesheet e paletas.
- Buscar no YouTube: `MortMort Aseprite animation`, `Aseprite sprite sheet export`, `AdamCYounis Aseprite workflow`.

### Fase 3 — Unity 2D Pixel Perfect

- Estudar import settings, 48 PPU, Sprite Editor, Tilemap, Rule Tile, Sprite Atlas e Pixel Perfect Camera.
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
