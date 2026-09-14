# Direção de Arte e Áudio — Braziliation

> Pixel art dieselpunk, paleta restrita, resolução 640×360 @ 32 PPU (Blasphemous-like, ADR-004), direção de áudio e referências. Movido de `.github/instructions/art-direction.instructions.md` (ADR-008). Detalhe visual: [`style-bible.md`](style-bible.md); regras que o Claude Code carrega nas pastas de arte: `.claude/rules/arte.md`.

## Visual style

- **Pixel art** — Arte desenhada em pixel; sem texturas hi-res ou arte vetorial no jogo.
- **Inspiração Blasphemous-era (ADR-004)** — Densidade de pixel de metroidvanias modernos (Blasphemous, SOTN). Leitura clara em 640×360 (32 PPU); personagem ~17% da altura da tela.
- **Paleta restrita** — Paleta coesa por ambiente; evite "arco-íris" ou tons conflitantes. Defina paletas-chave por ambiente (ex: wasteland, selva, industrial).
- **Dieselpunk brasileiro** — Industrial, mecânico, enferrujado, oleoso. Engrenagens, canos, vapor, tecnologia improvisada. Sabor brasileiro na arquitetura e props (ex: favela meets fábrica).

## Technical constraints

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 640×360 (CameraScaler; escala inteira ×3 → 1080p) — ADR-004 |
| PPU (pixels per unit) | 32 |
| Pipeline | URP 2D — apenas sprites e tilemaps; sem modelos 3D no gameplay |
| Tamanho base de sprite | 32×32 a 64×64 px (1 tile = 32×32 @ 32 PPU = 1 unidade Unity) |
| Animação | Sprite-based (2D Animation, Aseprite); run 8-12 frames, attack 6-10 |
| Paleta máxima por sprite | ~32 cores (base regional de 16 + rampas estendidas conforme necessário) |
| Assets legados (pré-ADR-004) | Upscale ×2 nearest — funcionais, aguardam re-autoria em densidade nova |

## Audio direction

- **Música:** Mood que combina dieselpunk + identidade brasileira. Pode ser chiptune, industrial ou híbrido; evite "épico orquestral" genérico.
- **SFX:** Impactante e legível. Hits, pulos e UI devem se sentir satisfatórios em volume baixo. Considere uma estética retrô de canais limitados para autenticidade.
- **Idioma:** Português (BR) para diálogo e UI é preferido; documente qualquer abordagem de localização no GDD.

## References for AI

- Ao propor assets ou descrições, mantenha dentro de **pixel art** e **dieselpunk**.
- Novos personagens ou cenários devem se encaixar em `Design/Criativo/` (cidades, lendas, personagens) e no mundo estabelecido.
- Para detalhes de implementação (import settings, atlases), alinhe com `Desenvolvimento/Docs/Architecture/` e as configurações do projeto Unity.
- Para concept art e sprites por difusão, siga `pipeline-ia-sprites.md` (skill `concept-art`), `style-bible.md`, `palette-guide.md` e `sprite-scale-guide.md`.
- Para sprites gerados por código/agente (props, tiles, ícones), siga `pipeline-sprites-programaticos.md` (skill `sprite-pipeline`) e use as ferramentas de `Design/ArteFonte/Ferramentas/`.

## Prompt template para geração de arte

Ao gerar prompts para ferramentas de arte (ComfyUI, Stable Diffusion etc.), inclua:
- Paleta restrita da região (`Design/ArteConceitual/Paletas/{regiao}.json`; até ~32 cores por sprite — ADR-004)
- Leitura em 640×360 @ 32 PPU (tile 32×32, player ~64 px de altura)
- Pose e contexto
- Referência cultural brasileira / dieselpunk
