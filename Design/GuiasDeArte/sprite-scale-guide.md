# Guia de Escala de Sprites

> **ADR-011 (2026-09-25, substitui o ADR-004):** 960×540 @ 48 PPU, tile 48×48. Toda a arte própria já está no grid de 48; só os placeholders CC0 do Gothicvania seguem a 32 PPU, listados em `Assets/Editor/Art/Escala/PixelScale.cs`.

## Configuração Base

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 960x540 (escala inteira ×2 → 1080p) |
| PPU | 48 |
| Tile base | 48x48 px |
| Unidade Unity | 1 tile = 1 unidade |
| Câmera | Pixel Perfect / URP 2D (`CameraScaler`) |

## Tamanhos Recomendados

| Asset | Tamanho Base | Observação |
|-------|--------------|------------|
| Tile comum | 48x48 | Chão, parede, borda, plataforma |
| Prop pequeno | 48x48 | Garrafa, engrenagem pequena, vela, item simples |
| Prop médio | 48x96 ou 96x48 | Estátua, torre de sinalização, porta baixa, cano |
| Prop grande | 96x96 ou 144x96 | Máquina, altar, alavanca da comporta |
| Player | 72x96 ou 96x96 | ~96px de altura (~17% da tela, proporção Blasphemous) |
| NPC humano | 72x96 ou 96x96 | 72×96 é o mínimo legível da style-bible; varia por roupa/chapéu/equipamento |
| Inimigo pequeno | 48x48 a 96x72 | Deve ser lido como ameaça em movimento |
| Inimigo médio | 96x96 a 144x96 | Pode ter partes animadas separadas |
| Boss | Múltiplos de 48 | Preferir montagem por partes/prefab |
| UI icon | 24x24 ou 48x48 | Deve ler em escala pequena |

## Regras

- Trabalhe sempre alinhado ao grid de 48 px.
- Evite tamanhos arbitrários quando um múltiplo de 24 ou 48 (meio tile ou tile) resolver.
- Defina pivot antes de animar.
- Mantenha chão e sombra de contato estáveis entre frames.
- Exporte spritesheets com padding consistente para evitar bleeding.
