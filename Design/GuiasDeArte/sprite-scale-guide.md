# Guia de Escala de Sprites

> **ADR-004 (2026-07-12):** upgrade para densidade Blasphemous-like. Valores antigos (320×180 / 16 PPU / tile 16) valem só para assets legados, mantidos via upscale ×2 até re-autoria.

## Configuração Base

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 640x360 (escala inteira ×3 → 1080p) |
| PPU | 32 |
| Tile base | 32x32 px |
| Unidade Unity | 1 tile = 1 unidade |
| Câmera | Pixel Perfect / URP 2D (`CameraScaler`) |

## Tamanhos Recomendados

| Asset | Tamanho Base | Observação |
|-------|--------------|------------|
| Tile comum | 32x32 | Chão, parede, borda, plataforma |
| Prop pequeno | 32x32 | Garrafa, engrenagem pequena, vela, item simples |
| Prop médio | 32x64 ou 64x32 | Alavanca, porta baixa, caixa, cano |
| Prop grande | 64x64 ou 96x64 | Máquina, altar, comporta pequena |
| Player | 48x64 ou 64x64 | ~64px de altura (~17% da tela, proporção Blasphemous) |
| NPC humano | 48x64 ou 64x64 | Varia por roupa/chapéu/equipamento |
| Inimigo pequeno | 32x32 a 64x48 | Deve ser lido como ameaça em movimento |
| Inimigo médio | 64x64 a 96x64 | Pode ter partes animadas separadas |
| Boss | Múltiplos de 32 | Preferir montagem por partes/prefab |
| UI icon | 24x24 ou 32x32 | Deve ler em escala pequena |

## Regras

- Trabalhe sempre alinhado ao grid de 32 px.
- Evite tamanhos arbitrários quando um múltiplo de 16 ou 32 resolver.
- Defina pivot antes de animar.
- Mantenha chão e sombra de contato estáveis entre frames.
- Exporte spritesheets com padding consistente para evitar bleeding.
