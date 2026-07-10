# Guia de Escala de Sprites

## Configuração Base

| Atributo | Valor |
|----------|-------|
| Resolução de referência | 320x180 |
| PPU | 16 |
| Tile base | 16x16 px |
| Unidade Unity | 1 tile = 1 unidade |
| Câmera | Pixel Perfect / URP 2D |

## Tamanhos Recomendados

| Asset | Tamanho Base | Observação |
|-------|--------------|------------|
| Tile comum | 16x16 | Chão, parede, borda, plataforma |
| Prop pequeno | 16x16 | Garrafa, engrenagem pequena, vela, item simples |
| Prop médio | 16x32 ou 32x16 | Alavanca, porta baixa, caixa, cano |
| Prop grande | 32x32 ou 48x32 | Máquina, altar, comporta pequena |
| Player | 24x32 ou 32x32 | Precisa de silhueta limpa e hitbox previsível |
| NPC humano | 24x32 ou 32x32 | Varia por roupa/chapéu/equipamento |
| Inimigo pequeno | 16x16 a 32x24 | Deve ser lido como ameaça em movimento |
| Inimigo médio | 32x32 a 48x32 | Pode ter partes animadas separadas |
| Boss | Múltiplos de 16 | Preferir montagem por partes/prefab |
| UI icon | 16x16 ou 24x24 | Deve ler em escala pequena |

## Regras

- Trabalhe sempre alinhado ao grid de 16 px.
- Evite tamanhos arbitrários quando um múltiplo de 8 ou 16 resolver.
- Defina pivot antes de animar.
- Mantenha chão e sombra de contato estáveis entre frames.
- Exporte spritesheets com padding consistente para evitar bleeding.
