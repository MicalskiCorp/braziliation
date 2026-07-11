# Guias de Arte — Braziliation

Hub dos padrões visuais usados para manter consistência entre arte humana, arte gerada com IA e assets finais do Unity.

## Guias

| Guia | Uso |
|------|-----|
| [`style-bible.md`](style-bible.md) | Bíblia visual: pilares, formas, materiais, leitura e acabamento |
| [`sprite-scale-guide.md`](sprite-scale-guide.md) | Escala, tamanhos de sprite, tile grid e PPU |
| [`palette-guide.md`](palette-guide.md) | Paletas, limites de cor e contraste por região |
| [`animation-guide.md`](animation-guide.md) | Regras de animação, frames, timing e spritesheets |
| [`pipeline-ia-sprites.md`](pipeline-ia-sprites.md) | Roteiro para gerar sprites/assets com IA (difusão/ComfyUI) mantendo estilo |
| [`pipeline-sprites-programaticos.md`](pipeline-sprites-programaticos.md) | Roteiro para gerar sprites por código/agente com validação automática de paleta e leitura |
| [`asset-brief-template.md`](asset-brief-template.md) | Template para pedir asset novo de forma consistente |
| [`context-pack-template.md`](context-pack-template.md) | Template para empacotar contexto, prompt, referências e configurações de IA |

## Ordem de Uso

1. Leia a feature criativa em `Design/Criativo/`.
2. Preencha um brief com `asset-brief-template.md`.
3. Monte um context pack com `context-pack-template.md`.
4. Gere conceito/variações conforme `pipeline-ia-sprites.md` (arte orgânica via difusão) ou `pipeline-sprites-programaticos.md` (props/tiles via código e agente).
5. Faça acabamento manual seguindo escala, paleta e animação.
6. Exporte para `Desenvolvimento/Assets/Art/` e registre no índice técnico.
