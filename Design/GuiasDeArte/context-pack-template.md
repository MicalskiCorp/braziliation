# Template de Context Pack para IA

Use este modelo dentro de `Design/ArteFonte/IA/ContextPacks/{nome-do-asset}/context.md`.

```md
# Context Pack — {nome do asset}

## 1. Identificação
- Asset:
- Tipo: personagem | inimigo | boss | prop | tileset | UI | VFX | background
- Região/cidade:
- Feature/sistema associado:
- Caminho final previsto:
- Data:

## 2. Contexto Criativo
- Referência principal em `Design/Criativo/`:
- Resumo do papel no jogo:
- Emoção/sensação desejada:
- Materiais principais:
- Elementos obrigatórios:
- Elementos proibidos:

## 3. Contexto Visual do Projeto
Braziliation é um jogo de plataforma/ação 2D em pixel art, leitura SNES-era, 320x180, 16 PPU, paleta restrita, pós-apocalipse brasileiro e estética dieselpunk/clockpunk regional.

## 4. Contexto Regional
Descrever aqui a região/cidade. Exemplo para Blumenau:

Blumenau em Braziliation é clockpunk, com arquitetura enxaimel, engrenagens, força hidráulica, cheias do rio Itajaí-Açu, madeira úmida, latão envelhecido, ferro escurecido, clero militarizado e marcas de enchente.

## 5. Restrições Técnicas
- Canvas/tamanho final:
- PPU: 16
- Orientação: side-view | front-view | top-down | UI
- Fundo: transparente | cenário | estudo
- Paleta:
- Número máximo aproximado de cores:
- Animações necessárias:
- Pivot/hitbox:

## 6. Referências Autorizadas
- Sprites âncora:
- Paleta:
- Silhueta própria:
- Concept próprio:
- Referências externas licenciadas/domínio público:

## 7. Prompt Positivo
```text
[GLOBAL STYLE]

[REGION]

[ASSET]

[TECHNICAL]
```

## 8. Prompt Negativo
```text
photorealistic, 3D render, vector art, smooth gradient, anti-aliased illustration, high resolution painting, excessive detail, blurry, generic fantasy, modern sci-fi, text, watermark, copyrighted character
```

## 9. Configuração da Geração
- Ferramenta:
- Modelo:
- Workflow:
- Seed:
- Steps:
- CFG/guidance:
- Denoise:
- ControlNet/IP-Adapter/referências:
- Observações:

## 10. Resultado e Decisão
- Outputs salvos em:
- Selecionados:
- Rejeitados:
- Motivo da escolha:
- Ajustes necessários no Aseprite:

## 11. Checklist
- [ ] Contexto criativo preenchido
- [ ] Paleta definida
- [ ] Prompt salvo
- [ ] Seed/modelo/configuração salvos
- [ ] Referências autorizadas listadas
- [ ] Seleção salva em `Design/ArteFonte/IA/Selected/`
- [ ] Pixel pass feito em Aseprite
- [ ] Export final salvo em `Desenvolvimento/Assets/Art/`
- [ ] Asset registrado no índice técnico
```
