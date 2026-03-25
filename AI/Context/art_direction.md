# Art Direction – Braziliation

## Visual style

- **Pixel art** – Hand-drawn or tool-generated pixel art; no high-res textures or vector art in-game.
- **SNES-era inspiration** – Resolution and palette constraints similar to 16-bit consoles. Clear read at 320×180 reference (16 PPU).
- **Restricted palette** – Cohesive color palette; avoid “rainbow” or clashing hues. Define key palettes per environment (e.g. wasteland, jungle, industrial).
- **Dieselpunk** – Industrial, mechanical, oily, rusty. Gears, pipes, steam, improvised tech. Brazilian flavor in architecture and props (e.g. favela meets factory).

## Technical constraints

- **Reference resolution:** 320×180 (from CameraScaler).
- **PPU:** 16 (pixels per unit). All sprites and tiles must align to this.
- **Pipeline:** URP 2D. No 3D models for core gameplay; 2D sprites and tilemaps.
- **Animation:** Sprite-based (e.g. 2D Animation, Aseprite). Keep frame counts reasonable for performance and clarity.

## Audio direction

- **Music:** Mood that fits dieselpunk + Brazilian identity. Can be chiptune, industrial, or hybrid; avoid generic “epic orchestral.”
- **SFX:** Punchy, readable. Hits, jumps, and UI should feel satisfying at low volume. Consider limited channels (SNES-style) for authenticity if desired.
- **Language:** Portuguese (BR) for dialogue and UI is preferred; document any localization approach in GDD.

## References for AI

- When proposing assets or descriptions, stay within **pixel art** and **dieselpunk**.
- New areas or characters should fit **Docs/Lore/** and the established world.
- For implementation details (import settings, atlases), align with **Docs/Architecture/** and Unity project settings.
