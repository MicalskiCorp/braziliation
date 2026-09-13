---
name: concept-art
description: Gera e leva à aprovação o concept art (etapa 2) de um personagem, criatura ou cena do Braziliation pela rota de difusão — pré-voo de paleta, prompt em camadas, lotes no ComfyUI com log, gate de decisão e registro em concept.md. Use quando o usuário pedir concept art ou thumbnails, "gerar no ComfyUI", ou quando um item de "Concept Art Pendente" for executado.
---

# Skill: concept-art

Roteiro executável da **etapa 2** do fluxo de 5 etapas, para personagens, criaturas e cenas (rota C). Guia canônico, com racional, stack e trilha de estudo: `Design/GuiasDeArte/pipeline-ia-sprites.md` — em divergência, o guia manda. Desde 2026-07-26 o concept é de **cena completa** (personagem no ambiente), não sprite isolado. Sprites de produção vêm depois da aprovação (`pixelize.py` + pixel pass; props pela skill `sprite-pipeline`).

## Roteiro

1. **Origem e pendência.** Linha do asset em "Concept Art Pendente" de `Design/Criativo/TODO.md` e o texto de lore/Aparência na origem criativa. Sem origem, parar — conceito é do `@GameCreative`.
2. **Pré-voo de região.** `Design/ArteConceitual/Paletas/{regiao}.json` existe (mesmo como `proposta-inicial`)? Sem paleta, registrar a pendência antes de gerar — lote sem paleta nunca passa no `palette_check.py`.
3. **Brief e referências.** Brief/context pack pela skill `novo-asset`; conferir `Design/ArteConceitual/ReferenciasVisuais/{tema}/` e anotar em `fontes.md` o que foi usado — ou que a busca não achou nada.
4. **Prompt em camadas** — `[GLOBAL STYLE]`, `[REGION]`, `[ASSET]`, `[TECHNICAL]` (modelos em `pipeline-ia-sprites.md` → "Prompt em Camadas"). O negativo de qualquer humanoide inclui `nude, naked, bare skin, exposed breasts, nsfw`, e a roupa é descrita por peça concreta. Nenhum nome de artista vivo; nenhum dataset de jogo comercial.
5. **Gerar o lote** no ComfyUI local (setup em `Design/ArteFonte/IA/Models/comfyui-setup.md`; um modelo residente por vez):
   - texto: `py Design/ArteFonte/Ferramentas/comfy_batch.py --asset {slug} --seed {N} --positive "…" --negative "…"` — 6 a 12 thumbnails;
   - a partir de concept ou silhueta: `--reference-image {png} --denoise 0.4-0.6` — 1 imagem por submissão, variar a seed.
6. **Log.** Linha em `Design/ArteFonte/IA/ContextPacks/{asset}/lotes.md`: seed, modelo e o que mudou em relação ao lote anterior.
7. **Gate de decisão** — toda imagem termina em exatamente um lugar: aprovar → `IA/Selected/`; descartar → `IA/Rejected/`; iterar → novo lote com a mudança anotada. **Teto: 3 lotes por pedido de ajuste** — no terceiro sem resolver, levar o melhor candidato ao pixel pass (MCP `aseprite`).
8. **Propor ao usuário.** Candidato em `Design/ArteConceitual/{categoria}/{asset-slug}/concept.png` + `concept.md` no formato de `Design/ArteConceitual/index.md` ("Convenção do concept art de asset"), com `Status: proposto` e todo o contexto usado: lore, prompts, seed, referência e denoise, variações. **Nunca marcar aprovado sozinho.**
9. **Ao aprovar:** `Status: aprovado` com a data; concluir a linha no TODO criativo (skill `gerir-todo`); marcar a etapa "Concept Art" em `Desenvolvimento/Docs/Architecture/indices/assets.md`; aplicar a regra de retenção — manter só o aprovado e a referência prévia, limpar as iterações de `IA/Outputs/{asset}*/`.

## Regras

- Nada de IA vira asset final sem pixel pass.
- Nenhuma imagem descartada sem linha no `lotes.md`.
- Ferramentas rodam com `py`, não `python`.
