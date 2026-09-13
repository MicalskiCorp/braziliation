# Pipeline de IA para Sprites e Assets

Este roteiro define como usar IA sem perder a identidade visual do Braziliation. A IA deve acelerar conceito, variação e iteração; o sprite final ainda precisa de curadoria e acabamento manual.

> **Escopo deste guia (2026-07-24):** dono das Etapas 1-2 do fluxo em 5 etapas (ideia → **concept art aprovado**) para assets orgânicos (personagens, criaturas, bosses) — ver [`pipeline-sprites-programaticos.md`](pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas). A partir de concept art aprovado, as Etapas 3-5 (especificação → spec JSON → sprite) são regidas por aquele guia, mesmo quando o acabamento final é manual no Aseprite (passos 7-11 abaixo continuam válidos como uma das formas de executar essas etapas — a outra é a spec JSON programática). Nenhum dos dois guias descreve "o processo inteiro" sozinho.

## Objetivo

Gerar assets 2D/pixel art consistentes com:

- 640x360 de leitura final.
- 32 PPU.
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
- **Sempre incluir `nude, naked, bare skin, exposed breasts, nsfw` no prompt negativo de qualquer personagem humanoide**, e nunca simplificar a descrição de roupa a ponto de deixar só adjetivo solto ("translúcido") sem substantivo de peça de roupa concreta (corte/cós/mangas/comprimento) — incidente real em 2026-07-25 (ver `ContextPacks/chr-blumenau-edith-gaertner/lotes.md`, lote 6): um prompt simplificado sem descrição de vestido gerou personagem sem roupa, ainda mais grave por ser baseada em pessoa histórica real. Nunca promover/reusar saída assim — arquivar com a anotação e descartar de vez do fluxo de aprovação.

## Fluxo Operacional

### Mudança de fluxo (2026-07-26): concept de cena antes de sprite isolado

Decisão do usuário durante o teste-âncora da Edith Gaertner (7 lotes de sprite isolado — ver `Design/ArteFonte/IA/ContextPacks/chr-blumenau-edith-gaertner/lotes.md`): o concept art da Etapa 2 passa a ser de **cena completa** — personagem posicionado no cenário, como o concept do Minhocão (`Design/ArteConceitual/Monstros/Minhocão.png`) — e não mais o sprite isolado direto. O sprite de produção (isolado, frames de animação) vira uma etapa **posterior à aprovação do concept de cena**.

1. **Concept de cena (novo Passo 2):** gerar com a stack local (ComfyUI + SDXL + LoRA `pixel-art-xl` — ver `IA/Models/comfyui-setup.md`) a cena inteira: personagem no ambiente, iluminação, mood. Referências visuais reais do local e da pessoa (`ReferenciasVisuais/`) entram aqui como base de descrição e/ou img2img. Aprovação segue a convenção de `ArteConceitual/index.md` (concept.png + concept.md).
2. **Sprites de produção (Etapas 3-5, após aprovação):** extrair/derivar do concept aprovado os sprites isolados com frames de animação (idle/walk/etc.), animáveis via código. **Rota free atual:** `pixelize.py` + pixel pass e frames manuais no Aseprite (onion skin, tags). Ferramentas de IA especializadas nesta etapa (animação por esqueleto) existem mas são pagas — pesquisa completa com preços em `IA/Models/pesquisa-ferramentas-2026-07.md`; decisão vigente é **só free/local**.

O roteiro numerado abaixo continua válido — a mudança é o *conteúdo* do que se gera na Etapa 2 (cena, não sprite isolado) e a formalização de que sprite/animação vem depois da aprovação do concept.

### Roteiro Recomendado

Este é o fluxo que deve ser usado para cada asset novo:

1. **Escolher a origem criativa:** pegue a feature em `Design/Criativo/` ou `Desenvolvimento/Docs/GDD/Features/`.
1b. **Checar/buscar referência visual de apoio** em `Design/ArteConceitual/ReferenciasVisuais/{tema}/` antes de seguir, quando fizer sentido pro asset (ver Etapa 1b abaixo).
2. **Criar um context pack:** use [`context-pack-template.md`](context-pack-template.md) dentro de `Design/ArteFonte/IA/ContextPacks/{asset}/`.
3. **Definir escala e paleta:** confirme tamanho no [`sprite-scale-guide.md`](sprite-scale-guide.md) e paleta no [`palette-guide.md`](palette-guide.md).
4. **Montar prompt por camadas:** combine visão global, cidade/região, função do asset, restrições técnicas e prompt negativo.
5. **Gerar thumbnails (Etapa 2a — log de lote obrigatório):** faça 6 a 12 variações pequenas em IA, sem tentar finalizar. Toda rodada de geração recebe uma linha em `Design/ArteFonte/IA/ContextPacks/{asset}/lotes.md` (criar se não existir): seed, o que mudou em relação ao lote anterior, e depois do passo 6, o veredito. Não é burocracia extra — é a mesma frase que já se diz ao olhar o resultado, só que escrita, para o histórico de exploração sobreviver a uma limpeza de pasta.
6. **Decidir (Etapa 2b — gate obrigatório):** toda imagem gerada termina em exatamente um lugar, nunca em "descartada sem registro":
   - **Aprovar:** mover para `Design/ArteFonte/IA/Selected/` e seguir para o passo 6b.
   - **Descartar:** mover para `Design/ArteFonte/IA/Rejected/` (arquivo, não deleção — é para isso que a pasta existe).
   - **Iterar:** voltar ao passo 5 com a mudança anotada no `lotes.md` antes de gerar o próximo lote.
   - **Teto de iteração:** no máximo **3 lotes por pedido de ajuste**. Se o terceiro não resolver, parar a difusão e levar o melhor candidato para o pixel pass (passo 7, ou o MCP `aseprite`) — o lote 11 da Edith mostrou que img2img não acrescenta elemento que a imagem-base não tem, e insistir só queima tempo de GPU.
6b. **Pixelizar assistido:** `py pixelize.py candidato.png {regiao}.json --size {canvas do brief}` (ver [`pixelize.py`](../ArteFonte/Ferramentas/pixelize.py)) — downscale por cor dominante + paleta exata do projeto, ponto de partida pro passo 7, não substitui.
7. **Redesenhar no Aseprite:** faça pixel pass manual em tamanho real a partir do resultado do 6b — corrigir bandas de sombra, outline e highlight direcional (ver `style-bible.md#densidade-alvo`), não redesenhar do zero.
8. **Animar se necessário:** use tags do Aseprite e siga [`animation-guide.md`](animation-guide.md).
9. **Exportar para Unity:** salve PNG/spritesheet em `Desenvolvimento/Assets/Art/`.
10. **Validar em cena:** teste em 640x360, 32 PPU, em fundo real ou cena sandbox.
11. **Registrar:** atualize `Desenvolvimento/Docs/Architecture/indices/assets.md`.

Exemplo preenchido: `Design/ArteFonte/IA/ContextPacks/exemplo-prop-comporta-blumenau/context.md`.

## Como Passar Contexto Para a IA

A melhor forma não é mandar um prompt gigante solto. Use um pacote de contexto com partes fixas e partes variáveis.

### Pacote Mínimo

Todo pedido de asset deve ter:

- **Brief:** função, região, tamanho, paleta e caminho final.
- **Contexto do mundo:** dieselpunk brasileiro, pós-apocalipse, pixel art de alta densidade.
- **Contexto regional:** exemplo: Blumenau clockpunk, enxaimel, rio Itajaí-Açu, cheias, engrenagens e clero.
- **Restrições técnicas:** 32 PPU, canvas, sprite side-view, paleta limitada, sem gradiente suave.
- **Referências autorizadas:** sprites próprios, conceitos próprios, silhuetas próprias, paleta do projeto.
- **Prompt negativo:** o que a IA deve evitar.

### Prompt em Camadas

Monte prompts assim:

```text
[GLOBAL STYLE]
pixel art sprite for a 2D side-scrolling action platformer, modern metroidvania pixel art readability (Blasphemous-like), limited 32 color palette, clear silhouette, Brazilian post-apocalyptic dieselpunk

[REGION]
Blumenau clockpunk district, colonial-german timber architecture influence, flood marks, aged brass gears, dark iron, wet wood, muddy water stains

[ASSET]
32x32 side-view floodgate lever prop, readable silhouette, one interaction point, brass handle, iron base, wet wooden support

[TECHNICAL]
orthographic side view, no background, transparent background, readable at 640x360, designed for 32 PPU, no smooth gradients, no painterly rendering
```

Prompt negativo:

```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, generic fantasy, modern sci-fi, text, watermark, copyrighted character, nude, naked, bare skin, exposed breasts, nsfw
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

### 0. Pré-voo de região

Antes do primeiro prompt de concept art numa região nova: confirmar que `Design/ArteConceitual/Paletas/{regiao}.json` existe, mesmo que só como `status: proposta-inicial`. Gerar lotes de difusão apontando para uma paleta que não existe queima geração sem nenhuma chance de passar em `palette_check.py` depois.

### 1. Brief

Crie um brief usando [`asset-brief-template.md`](asset-brief-template.md). Nenhum asset deve começar só com “faz um sprite de X”. O brief fixa função, escala, paleta, região e restrições.

### 1b. Referências Visuais (novo — 2026-07-24)

Antes de montar o prompt, verificar `Design/ArteConceitual/ReferenciasVisuais/{tema}/` — repositório de apoio visual pra **qualquer asset**, não só os baseados em pessoa/lugar/fato real: também vale pra referência de material/textura, anatomia, mood ou composição de um elemento fictício. Se já existir pasta útil pro tema, usar; se fizer sentido buscar e não existir, buscar (via `@computador`, skill `hemeroteca-blumenau`, banco de imagem licenciado ou pesquisa direta) e criar — ou registrar em `fontes.md` que a busca não encontrou nada, para não repetir do zero depois. Ver [`ReferenciasVisuais/index.md`](../ArteConceitual/ReferenciasVisuais/index.md) para a estrutura e regra de fontes. Por enquanto isso é só embasamento pra quem escreve o prompt — não está plugado em img2img/IP-Adapter.

Não é obrigatório pra todo asset — props simples já bem descritos em `palette-guide.md`/`style-bible.md` podem não precisar.

### 2. Referências Autorizadas

Monte uma pasta de trabalho em `Design/ArteFonte/IA/` com:

- Brief do asset.
- Referências visuais reais depositadas no Passo 1b, se houver.
- Silhueta simples desenhada manualmente, se houver.
- Paleta aprovada.
- Sprites âncora do projeto.
- Referências próprias ou licenciadas.

### Usando o concept art do Passo 2 como referência (image-to-image)

Quando o asset já passou pelo Passo 2 do fluxo (`Design/ArteConceitual/{categoria}/{asset}/concept.png`, aprovado — ver [`pipeline-sprites-programaticos.md`](pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas)), use-o como imagem inicial em vez de partir só de texto:

- `comfy_batch.py --reference-image Design/ArteConceitual/{categoria}/{asset}/concept.png --denoise 0.4-0.6` monta automaticamente um workflow image-to-image (`workflow-img2img.json`): carrega o concept art, codifica em latente (VAEEncode) e aplica denoise parcial no KSampler — só com nós stock do ComfyUI (sem ControlNet/IP-Adapter, cujos custom nodes/modelos não estão confirmados instalados nesta máquina).
- Denoise baixo (~0.3–0.5) preserva composição/silhueta do concept art; denoise alto (~0.6–0.8) usa o concept mais como sugestão de mood.
- Esse modo gera 1 imagem por submissão (o `EmptyLatentImage` em lote de 6 do modo texto não se aplica aqui) — repita com seeds diferentes para variações.
- **Não testado ponta a ponta** (servidor ComfyUI local não estava rodando ao escrever isto) — faça um dry run antes de usar em produção.
- Se no futuro o projeto instalar ControlNet/IP-Adapter reais, eles dão controle de pose mais forte que o image-to-image simples; até lá, este é o caminho disponível sem novas dependências.

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

Registrar a decisão desta seleção no `lotes.md` do context pack e mover os arquivos para `Selected/`/`Rejected/` conforme a Etapa 2b do roteiro acima — nunca apagar um lote sem essa decisão ficar escrita em algum lugar.

### 4b. Pixelizar assistido (novo — 2026-07-24)

Antes de abrir o Aseprite, rodar [`pixelize.py`](../ArteFonte/Ferramentas/pixelize.py) no candidato aprovado: `py pixelize.py candidato.png {regiao}.json --size {canvas do brief}`. Faz downscale por cor dominante por bloco (não nearest-neighbor cru, que perde a silhueta) e já entrega o resultado na paleta exata do projeto — quem for pro Aseprite corrige bandas de sombra, outline e highlight direcional em cima de um rascunho já paletizado e no tamanho certo, em vez de reconstruir do zero a partir da imagem "pintada". **Isto não é o sprite aprovado** — é insumo pro passo 5, que continua obrigatório.

### 5. Pixel Pass Manual

Abra o candidato (de preferência já passado pelo `pixelize.py`) no Aseprite e redesenhe em resolução real. Não basta reduzir imagem gerada. O pixel pass deve:

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
- Pixels Per Unit: 32
- Filter Mode: Point
- Compression: None
- Mipmap: Off

### 8. Registro

Atualize `Desenvolvimento/Docs/Architecture/indices/assets.md` com o asset aprovado e registre a paleta usada.

## Prompt Base

Use em inglês quando a ferramenta responder melhor, mas mantenha os conceitos do projeto:

```text
pixel art sprite for a 2D side-scrolling action platformer, modern metroidvania pixel art readability (Blasphemous-like), high pixel density, limited 32 color palette, clear silhouette, Brazilian post-apocalyptic dieselpunk, aged brass, dark iron, wet wood, soot, handcrafted machinery, readable at 640x360, orthographic side view, no smooth gradients, no high resolution texture, no painterly rendering
```

Prompt negativo:

```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, realistic skin pores, modern sci-fi, generic fantasy, copyrighted character, text, watermark
```

## Exemplo — Prop de Blumenau

```text
pixel art prop, side view, 32x32 canvas, old clockpunk floodgate mechanism from Blumenau, Brazilian colonial-german timber architecture influence, aged brass gears, dark iron frame, wet wood planks, muddy water stains, limited 32 color palette, strong silhouette, readable at 640x360, modern metroidvania 2D platformer asset
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

- Estudar import settings, 32 PPU, Sprite Editor, Tilemap, Rule Tile, Sprite Atlas e Pixel Perfect Camera.
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
- [ ] Referência visual de apoio checada/buscada em `ReferenciasVisuais/`, quando fazia sentido pro asset (ou busca registrada como sem resultado) — Etapa 1b.
- [ ] Paleta definida.
- [ ] Referências autorizadas.
- [ ] IA usada só para rascunho/variação ou como base controlada.
- [ ] Lote registrado em `lotes.md` e decisão (Selected/Rejected/iterar) explícita — Etapa 2b.
- [ ] Passou por `pixelize.py` antes do Aseprite (Etapa 4b).
- [ ] Pixel pass manual feito — bandas de valor e dithering conforme `style-bible.md#densidade-alvo`.
- [ ] Sprite lê em 640x360.
- [ ] Export com 32 PPU.
- [ ] Asset final em `Desenvolvimento/Assets/Art/`.
- [ ] Índice de assets atualizado.
