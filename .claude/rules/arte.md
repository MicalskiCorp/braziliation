---
paths:
  - "Design/ArteConceitual/**"
  - "Design/ArteFonte/**"
  - "Design/GuiasDeArte/**"
  - "Desenvolvimento/Assets/Art/**"
---

# Direção de arte — Braziliation

Guia canônico: `Design/GuiasDeArte/style-bible.md` · direção de arte e áudio: `direcao-de-arte.md`. Pipeline: `pipeline-sprites-programaticos.md`
(programático) e `pipeline-ia-sprites.md` (difusão/concept).

## Restrições técnicas (ADR-011)

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 960×540 (escala inteira ×2 → 1080p) |
| PPU | 48 |
| Tile base | 48×48 |
| Sprite típico | 48×48 a 96×96; player ~96 px de altura |
| Paleta máxima por sprite | ~32 cores |
| Animação | run 8-12 frames, attack 6-10 |

Estilo: pixel art dieselpunk brasileiro — industrial, enferrujado, oleoso, tecnologia
improvisada. Silhueta legível em 1× antes de qualquer detalhe.

> **Migração em curso (ADR-011):** a arte anterior ao grid de 48 continua importada a 32 PPU
> para não mudar de tamanho em mundo. A lista viva está em `Assets/Editor/Art/PixelScale.cs`;
> ao re-autorar um asset, apague a linha dele de lá.

## Regras inegociáveis

- **Nada de IA vira asset final sem pixel pass.** A saída de difusão é ponto de partida.
- **Toda geração termina registrada:** `Selected/` ou `Rejected/` — nunca descartada sem
  linha no `lotes.md` do context pack. Seed, modelo e o que mudou entram na linha.
- **`palette_check.py` precisa APROVAR** antes do export para `Assets/Art/`.
- Sem nome de artista vivo no prompt. Sem dataset de jogo comercial.
- **Sem treino de LoRA de estilo próprio até o gate do ADR-014** (≥30 imagens próprias em 48 PPU,
  ≥10 de personagem/inimigo, base decidida, 2 personagens animados). Até lá: prompt fixo, paleta
  travada, img2img e pixel pass. Treino gerenciado em SaaS está descartado.
- Prompt negativo de qualquer humanoide inclui `nude, naked, bare skin, exposed breasts,
  nsfw`, e a roupa é descrita com substantivo de peça concreta — nunca adjetivo solto.
  Isto veio de um incidente real (2026-07-25) com personagem baseada em pessoa histórica.
- Ferramentas rodam com `py`, não `python`.

## Fluxo (5 etapas)

ideia (`Design/Criativo/`) → concept aprovado (`Design/ArteConceitual/`) → especificação
de variações → spec JSON (`ContextPacks/{asset}/{asset}.spec.json`) → sprite
(`Assets/Art/`) → registro em `Docs/Architecture/indices/assets.md`.

Cada etapa é acionada manualmente. Nenhuma pula a anterior. Roteiros executáveis: skill
`concept-art` (etapa 2), `novo-asset` (brief) e `sprite-pipeline` (etapas 4-5).
