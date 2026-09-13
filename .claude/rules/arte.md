---
paths:
  - "Design/**"
  - "Desenvolvimento/Assets/Art/**"
---

# Direção de arte — Braziliation

Guia canônico: `Design/GuiasDeArte/style-bible.md`. Pipeline: `pipeline-sprites-programaticos.md`
(programático) e `pipeline-ia-sprites.md` (difusão/concept).

## Restrições técnicas (ADR-004)

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 640×360 (escala inteira ×3 → 1080p) |
| PPU | 32 |
| Tile base | 32×32 |
| Sprite típico | 32×32 a 64×64; player ~64 px de altura |
| Paleta máxima por sprite | ~32 cores |
| Animação | run 8-12 frames, attack 6-10 |

Estilo: pixel art dieselpunk brasileiro — industrial, enferrujado, oleoso, tecnologia
improvisada. Silhueta legível em 1× antes de qualquer detalhe.

## Regras inegociáveis

- **Nada de IA vira asset final sem pixel pass.** A saída de difusão é ponto de partida.
- **Toda geração termina registrada:** `Selected/` ou `Rejected/` — nunca descartada sem
  linha no `lotes.md` do context pack. Seed, modelo e o que mudou entram na linha.
- **`palette_check.py` precisa APROVAR** antes do export para `Assets/Art/`.
- Sem nome de artista vivo no prompt. Sem dataset de jogo comercial.
- Prompt negativo de qualquer humanoide inclui `nude, naked, bare skin, exposed breasts,
  nsfw`, e a roupa é descrita com substantivo de peça concreta — nunca adjetivo solto.
  Isto veio de um incidente real (2026-07-25) com personagem baseada em pessoa histórica.
- Ferramentas rodam com `py`, não `python`.

## Fluxo (5 etapas)

ideia (`Design/Criativo/`) → concept aprovado (`Design/ArteConceitual/`) → especificação
de variações → spec JSON (`ContextPacks/{asset}/{asset}.spec.json`) → sprite
(`Assets/Art/`) → registro em `Docs/Architecture/indices/assets.md`.

Cada etapa é acionada manualmente. Nenhuma pula a anterior.
