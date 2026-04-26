---
description: "Direção de arte do Braziliation: pixel art dieselpunk, paleta restrita, resolução 320x180 16 PPU, direção de áudio e referências visuais. Use quando propor ou revisar assets, sprites, tiles, animações ou descrições de arte."
---
# Art Direction – Braziliation

## Visual style

- **Pixel art** — Arte desenhada em pixel; sem texturas hi-res ou arte vetorial no jogo.
- **Inspiração SNES-era** — Restrições de resolução e paleta similares a consoles 16-bit. Leitura clara em 320×180 (16 PPU).
- **Paleta restrita** — Paleta coesa por ambiente; evite "arco-íris" ou tons conflitantes. Defina paletas-chave por ambiente (ex: wasteland, selva, industrial).
- **Dieselpunk brasileiro** — Industrial, mecânico, enferrujado, oleoso. Engrenagens, canos, vapor, tecnologia improvisada. Sabor brasileiro na arquitetura e props (ex: favela meets fábrica).

## Technical constraints

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 320×180 (CameraScaler) |
| PPU (pixels per unit) | 16 |
| Pipeline | URP 2D — apenas sprites e tilemaps; sem modelos 3D no gameplay |
| Tamanho base de sprite | 16×16 a 32×32 px (1 tile = 16×16 @ 16 PPU = 1 unidade Unity) |
| Animação | Sprite-based (2D Animation, Aseprite); contagens de frame razoáveis |
| Paleta máxima por sprite | ~16 cores (estilo SNES) |

## Audio direction

- **Música:** Mood que combina dieselpunk + identidade brasileira. Pode ser chiptune, industrial ou híbrido; evite "épico orquestral" genérico.
- **SFX:** Impactante e legível. Hits, pulos e UI devem se sentir satisfatórios em volume baixo. Considere canais limitados estilo SNES para autenticidade.
- **Idioma:** Português (BR) para diálogo e UI é preferido; documente qualquer abordagem de localização no GDD.

## References for AI

- Ao propor assets ou descrições, mantenha dentro de **pixel art** e **dieselpunk**.
- Novos personagens ou cenários devem se encaixar em `Desenvolvimento/Docs/Lore/` e o mundo estabelecido.
- Para detalhes de implementação (import settings, atlases), alinhe com `Desenvolvimento/Docs/Architecture/` e as configurações do projeto Unity.

## Prompt template para geração de arte

Ao gerar prompts para ferramentas de arte (Midjourney, Stable Diffusion etc.), inclua:
- Paleta restrita (max 16 cores)
- 16 PPU, resolução específica
- Pose e contexto
- Referência cultural brasileira / dieselpunk
