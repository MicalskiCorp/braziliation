# Context Pack — chr_blumenau_edith_gaertner

> **Sprite-âncora do processo (2026-07-24)** — não é um pedido de asset normal. Objetivo primário: testar o fluxo orgânico (Rota C) de ponta a ponta pela primeira vez e calibrar a seção "Densidade Alvo" de `style-bible.md` contra um resultado real, antes de qualquer outra arte orgânica. Ver `Design/GuiasDeArte/pipeline-ia-sprites.md` e a análise em memória do projeto sobre por que a rota orgânica nunca completou um ciclo.

## 1. Identificação
- Asset: `chr_blumenau_edith_gaertner`
- Tipo: personagem (NPC espectral, dadora de quest)
- Região/cidade: Blumenau
- Feature/sistema associado: Side-quest SQ-01 — "Os Gatos de Edith", Cemitério dos Gatos
- Caminho final previsto: `Desenvolvimento/Assets/Art/Characters/chr_blumenau_edith_gaertner.png`
- Data: 2026-07-24

## 2. Contexto Criativo
- Referência principal: `Design/Criativo/Historia/personagens/Edith-Gaertner.md`
- Resumo do papel no jogo: figura espectral melancólica (não hostil) no Jardim do Cemitério dos Gatos; dadora da quest dos 41 gatos perdidos.
- Emoção/sensação desejada: melancolia, dignidade decaída — "foi grande e se dobrou" (descrição do próprio doc de lore), não terror.
- Materiais principais: tecido de vestido de época (1920s europeu) desgastado, brilho espectral azul-acinzentado suave.
- Elementos obrigatórios: silhueta feminina, vestido de época europeu gasto, cabelo preso, luz espectral fria (não quente).
- Elementos proibidos: qualquer coisa "assustadora"/hostil (ela é triste, não uma ameaça), roupa moderna, cores quentes/saturadas.

**Simplificação deliberada para este teste:** o lore descreve Edith sentada num banco de raiz de árvore, cercada por 9 gatos espectrais. Para isolar a variável técnica (densidade de pixel art, não composição de cena), este lote testa uma **pose idle em pé**, não a pose sentada canônica. Se a técnica for aprovada, uma segunda rodada replica a pose sentada real antes de qualquer registro como asset final.

## 3. Contexto Visual do Projeto
Braziliation é um jogo de plataforma/ação 2D em pixel art, leitura Blasphemous-like (ADR-004), 640x360, 32 PPU, paleta restrita, pós-apocalipse brasileiro e estética dieselpunk/clockpunk regional.

## 4. Contexto Regional
Blumenau em Braziliation é clockpunk, com arquitetura enxaimel, engrenagens, força hidráulica, cheias do rio Itajaí-Açu, madeira úmida, latão envelhecido, ferro escurecido, clero militarizado e marcas de enchente. Camada específica do Jardim de Edith (`palette-guide.md`): "verde musgo, cinza azulado, brilho espectral pequeno e suave".

## 5. Restrições Técnicas
- Canvas/tamanho final: **64×64** (mínimo do style-bible.md para orgânicos é 48×64; escolhido o teto da faixa "NPC humano" do sprite-scale-guide.md pra maximizar orçamento de detalhe neste teste)
- PPU: 32
- Orientação: side-view
- Fundo: transparente
- Paleta: `Design/ArteConceitual/Paletas/blumenau.json` (aprovada)
- Número máximo aproximado de cores: 32 (max_colors_per_sprite da paleta)
- Animações necessárias: nenhuma neste teste — só o frame idle
- Pivot/hitbox: bottom-center (convenção do projeto)

## 6. Referências Autorizadas
- Referências visuais reais: `Design/ArteConceitual/ReferenciasVisuais/edith-gaertner/` — estrutura criada em 2026-07-24, busca de foto/retrato real ainda pendente (não usada no lote 1)
- Sprites âncora: nenhum ainda — este É o primeiro teste de sprite-âncora orgânico do projeto
- Paleta: Blumenau (aprovada), ênfase nas cores 2 (`#232c33` azul petróleo), 4 (`#4d5a66` ferro azulado), 5 (`#8a949c` highlight frio), E (`#5a6b52` verde acinzentado)
- Silhueta própria: não desenhada ainda
- Concept próprio: nenhum — Passo 2 do fluxo geral (concept art aprovado) ainda não existe pra este asset; este lote É a tentativa do Passo 2
- Referências externas: nenhuma (sem nomes de artista, sem dataset de jogo comercial — só a descrição verbal do estilo Blasphemous/SotN já usada no restante do guia)

## 7. Prompt Positivo (lote 2 — 2026-07-25, reescrito com base nas referências reais)
```text
[GLOBAL STYLE]
pixel art character reference sheet for a 2D side-scrolling action platformer, modern metroidvania pixel art readability (Blasphemous-like), high pixel density, limited 32 color palette, single isolated character, clear silhouette, Brazilian post-apocalyptic dieselpunk

[ASSET]
translucent ghostly woman NPC, full body, standing idle pose facing sideways, pale spectral blue-white glowing translucent skin and dress, 1920s European day dress with dropped waist and gathered pleated skirt and short cap sleeves, hair center-parted and pulled back low into a simple bun, melancholic dignified expression, soft downcast eyes (not glowing, not menacing), one arm bent holding a small translucent glowing pale-blue spectral cat close against her chest, cat fur pattern still faintly visible through the translucency, faint sparkle particles drifting along the dress, lower hem of the dress dissolving into thin swirling wisps of pale mist instead of visible legs, soft cold blue-grey rim light outline, no weapon, no aggressive pose

[TECHNICAL]
single character only, no scenery, no buildings, no architecture, no landscape, no environment props, plain flat neutral grey backdrop, full body centered in frame, orthographic side view, designed for 32 PPU, no smooth gradients, no painterly rendering, strong readable silhouette, character concept sheet framing
```

Referências usadas (ver `Design/ArteConceitual/ReferenciasVisuais/edith-gaertner/fontes.md`): vestido/cabelo/postura de `Edith Gaertner 1.png`; tratamento translúcido azul + dissolução em névoa de `Espectro 1.jpg`/`Espectro 2.png`; cor/brilho do gato de `Gato Espectral.png`. Referências do Cemitério dos Gatos (local real) **não** entram neste prompt — este lote é o sprite isolado (fundo transparente), cenário fica pra um asset separado de background.

## 8. Prompt Negativo (lote 2)
```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, generic fantasy, modern sci-fi, text, watermark, copyrighted character, modern clothing, colorful, cheerful, saturated colors, horror monster, aggressive pose, weapon, glowing red eyes, background, scenery, buildings, architecture, landscape, city, moon, trees, forest, multiple characters, other people, cropped body, close-up portrait, full scene illustration
```

## 9. Configuração da Geração
- Ferramenta: ComfyUI local (`D:\Tools\ComfyUI`)
- Modelo: `sd_xl_base_1.0.safetensors` (SDXL 1.0)
- Workflow: `workflow-thumbnails.json` (text-to-image, lote de 6, 1024×1024, steps 25, CFG 6.5, sampler euler/normal)
- Seed: `20260725` (lote 2 — lote 1 usou `20260724`)
- Steps: 25 (default do workflow)
- CFG/guidance: 6.5 (default do workflow)
- Denoise: N/A (lote 2 continua text-to-image; decisão de 2026-07-24 foi não plugar img2img/IP-Adapter ainda, só usar referências como embasamento do prompt)
- ControlNet/IP-Adapter/referências: nenhum plugado na geração (não instalado neste ambiente); referências reais usadas manualmente pra escrever o prompt acima — ver `ReferenciasVisuais/edith-gaertner/`
- Observações: primeiro lote de verdade da Etapa 2a (log de lote formal) — ver `lotes.md` nesta mesma pasta.

## 10. Resultado e Decisão
- Outputs salvos em: `Design/ArteFonte/IA/Outputs/chr-blumenau-edith-gaertner/` (vazio após a rejeição — ver abaixo)
- Selecionados: nenhum
- Rejeitados: todas as 12 (2 submissões do lote 1, seed 20260724 — ver `lotes.md`). Arquivos movidos para `Design/ArteFonte/IA/Rejected/chr-blumenau-edith-gaertner/` em 2026-07-25.
- Motivo da escolha: nenhuma imagem isolou a personagem como sprite — todas saíram como ilustração de cena completa (arquitetura + atmosfera), fundo opaco, zero pixel art. Ver diagnóstico completo em `lotes.md`.
- Ajustes necessários no Aseprite: N/A — nenhuma imagem chegou a `Selected/`, `pixelize.py` não foi rodado neste lote.
- Referências visuais reais depositadas em 2026-07-25: `Design/ArteConceitual/ReferenciasVisuais/edith-gaertner/` (7 imagens — figura histórica, tratamento espectral e local real; ver `fontes.md` na pasta) — usadas no lote 2.
- **Lote 2 (seed 20260725): também rejeitado**, mas isolou a personagem com sucesso (fundo liso, sem cenário — confirma o diagnóstico do lote 1). Problemas novos: sem tratamento espectral/translúcido, sem o gato, 4/6 saíram como prancha de turnaround em vez de pose única. Ver diagnóstico completo em `lotes.md`. Arquivos em `Design/ArteFonte/IA/Rejected/chr-blumenau-edith-gaertner-lote2/`.

## 11. Checklist
- [x] Contexto criativo preenchido
- [x] Paleta definida
- [x] Prompt salvo
- [x] Seed/modelo/configuração salvos
- [x] Referências autorizadas listadas
- [ ] Seleção salva em `Design/ArteFonte/IA/Selected/`
- [ ] Pixel pass feito em Aseprite
- [ ] Export final salvo em `Desenvolvimento/Assets/Art/`
- [ ] Asset registrado no índice técnico
