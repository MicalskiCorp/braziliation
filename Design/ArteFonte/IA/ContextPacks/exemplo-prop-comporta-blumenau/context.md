# Context Pack — Prop Comporta de Blumenau

## 1. Identificação

- Asset: prop_blumenau_floodgate_lever
- Tipo: prop/interactable
- Região/cidade: Blumenau — Die Unterwelt
- Feature/sistema associado: Sistema Hídrico de Die Unterwelt
- Caminho final previsto: `Desenvolvimento/Assets/Art/Environments/Blumenau/Props/prop_blumenau_floodgate_lever.png`
- Data: 2026-06-27

## 2. Contexto Criativo

- Referência principal em `Design/Criativo/`: `Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`
- Resumo do papel no jogo: alavanca mecânica usada para abrir/fechar comportas durante ciclos de cheia.
- Emoção/sensação desejada: objeto pesado, antigo, funcional e perigoso; tecnologia improvisada que ainda aguenta pressão da água.
- Materiais principais: latão envelhecido, ferro escuro, madeira úmida, lama seca e marcas de enchente.
- Elementos obrigatórios: alavanca legível, base metálica, engrenagem parcial, madeira ou suporte gasto.
- Elementos proibidos: visual limpo demais, sci-fi moderno, neon, fantasia medieval genérica.

## 3. Contexto Visual do Projeto

Braziliation é um jogo de plataforma/ação 2D em pixel art, leitura SNES-era, 320x180, 16 PPU, paleta restrita, pós-apocalipse brasileiro e estética dieselpunk/clockpunk regional.

## 4. Contexto Regional

Blumenau em Braziliation é clockpunk, com arquitetura enxaimel, engrenagens, força hidráulica, cheias do rio Itajaí-Açu, madeira úmida, latão envelhecido, ferro escurecido, clero militarizado e marcas de enchente.

## 5. Restrições Técnicas

- Canvas/tamanho final: 32x32 px
- PPU: 16
- Orientação: side-view
- Fundo: transparente
- Paleta: Blumenau clockpunk/hídrico
- Número máximo aproximado de cores: 12 a 16
- Animações necessárias: idle estático; opcional 3 frames de acionamento
- Pivot/hitbox: base central inferior; área interativa no cabo da alavanca

## 6. Referências Autorizadas

- Sprites âncora: ainda a definir
- Paleta: `Design/GuiasDeArte/palette-guide.md`
- Silhueta própria: desenhar shape simples antes do image-to-image
- Concept próprio: opcional em `Design/ArteConceitual/Props/`
- Referências externas licenciadas/domínio público: apenas mecanismos hidráulicos/engrenagens com licença clara

## 7. Prompt Positivo

```text
[GLOBAL STYLE]
pixel art sprite for a 2D side-scrolling action platformer, SNES-era readability, limited 16 color palette, clear silhouette, Brazilian post-apocalyptic dieselpunk

[REGION]
Blumenau clockpunk district, colonial-german timber architecture influence, flood marks, aged brass gears, dark iron, wet wood, muddy water stains

[ASSET]
32x32 side-view floodgate lever prop, readable silhouette, one interaction point, brass handle, iron base, partial gear mechanism, wet wooden support, heavy old machinery

[TECHNICAL]
orthographic side view, no background, transparent background, readable at 320x180, designed for 16 PPU, no smooth gradients, no painterly rendering, clean pixel clusters
```

## 8. Prompt Negativo

```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, generic fantasy, modern sci-fi, neon, text, watermark, copyrighted character
```

## 9. Configuração da Geração

- Ferramenta: ComfyUI
- Modelo: SDXL/Flux base a definir
- Workflow: text-to-image para thumbnails; image-to-image após silhueta aprovada
- Seed: fixar por lote
- Steps: a definir conforme modelo
- CFG/guidance: médio; evitar exagero de detalhe
- Denoise: baixo em image-to-image com silhueta própria
- ControlNet/IP-Adapter/referências: usar silhueta própria se disponível
- Observações: gerar 6 a 12 variações, escolher 1 ou 2, redesenhar no Aseprite

## 10. Resultado e Decisão

- **Rota executada:** pipeline programático (`pipeline-sprites-programaticos.md`, Opção A) — 2026-07-11
- Fonte: `prop_blumenau_floodgate_lever.spec.json` (neste context pack) + paleta `Design/ArteConceitual/Paletas/blumenau.json`
- Output: `Design/ArteFonte/IA/Outputs/prop_blumenau_floodgate_lever.png` (+ previews e mocks 320×180)
- Selecionado: `Design/ArteFonte/IA/Selected/prop_blumenau_floodgate_lever.png`
- Iterações do ciclo de crítica: 2 (iteração 2 corrigiu o encaixe de ferro que sumia contra fundo grafite em 1x — corpo 3→4 com outline 1)
- Validação: `palette_check.py` APROVADO — 15/16 cores, todas da paleta Blumenau
- Motivo da escolha: silhueta da alavanca legível em 1x no mock 320×180; materiais corretos (latão, ferro, madeira úmida, marca de enchente, lama)
- **Animação (2026-07-11):** acionamento em 3 frames (idle/esquerda → vertical → direita/impacto), engrenagem girando um passo de dente entre frames. Fontes: `_f2.spec.json` e `_f3.spec.json` neste context pack. Sheet: `prop_blumenau_floodgate_lever_activate_sheet.png` (96×32), palette_check APROVADO, exportado para `Assets/Art/Environments/Blumenau/Props/`
- Pendências: paleta Blumenau ainda em `proposta-inicial`; pixel pass manual opcional para polish; slicing (Sprite Mode Multiple, grid 32×32) e Animator no Unity → @UnityDeveloper
- **Roteiro completo de retomada:** `Desenvolvimento/Docs/TODO.md` → seção "Pipeline de Sprites — Roteiro de Continuação" (passos 1–4 = wiring Unity deste asset; 5–6 = paleta e polish; 7–8 = evolução do pipeline)

## 11. Checklist

- [x] Contexto criativo preenchido
- [x] Paleta definida
- [x] Prompt salvo (rota programática: spec JSON é a fonte)
- [x] Seed/modelo/configuração salvos (spec determinística — sem seed)
- [x] Referências autorizadas listadas
- [x] Seleção salva em `Design/ArteFonte/IA/Selected/`
- [ ] Pixel pass feito em Aseprite (opcional — polish futuro)
- [x] Export final salvo em `Desenvolvimento/Assets/Art/Environments/Blumenau/Props/`
- [x] Asset registrado no índice técnico
