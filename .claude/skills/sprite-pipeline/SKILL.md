---
name: sprite-pipeline
description: Gera um sprite pixel art programático seguindo o pipeline do Braziliation — spec JSON, ciclo gerar→visualizar→criticar→refinar, validação de paleta e mock 640x360. Use quando o usuário pedir para gerar/criar sprite, placeholder, prop pixel art ou validar um sprite existente.
---

# Skill: sprite-pipeline

Processo canônico: **`Design/GuiasDeArte/pipeline-sprites-programaticos.md`** — leia-o integralmente antes de começar; esta skill é só o roteiro de execução.

## Roteiro

1. Ler o guia canônico + `style-bible.md` + `sprite-scale-guide.md`.
2. Carregar a paleta da região: `Design/ArteConceitual/Paletas/{regiao}.json`. Se não existir, derivar do `palette-guide.md` com `"status": "proposta-inicial"` e avisar o usuário.
3. Criar/confirmar brief e context pack em `Design/ArteFonte/IA/ContextPacks/{asset}/` (templates em `GuiasDeArte/`; usar a skill `novo-asset` se não existirem). Se o asset tiver múltiplas ações, confirmar que `variations.md` (Passo 3, `variation-spec-template.md`) já mapeia cada ação para um id de `outputs`/`sheets`.
4. Escrever a spec **consolidada** `{asset}.spec.json` (um JSON por objeto — ver `pipeline-sprites-programaticos.md#formato-da-spec-consolidada`): um `output` por frame/variação, e uma entrada em `sheets` para cada animação. **Silhueta primeiro** (1 cor) no output `idle`, depois detalhe e demais outputs.
5. Executar o ciclo com as ferramentas de `Design/ArteFonte/Ferramentas/` (requer Python + Pillow):
   - `python render_spec.py {spec}` → renderiza todos os `outputs` + monta `sheets` automaticamente em `ArteFonte/IA/Outputs/`; use `--only {id} -o {out}.png` para iterar um output isolado durante a crítica
   - `python upscale_preview.py {png} -s 8 --grid` → **abrir a imagem com Read e criticar** (repetir por output/sheet relevante)
   - `python mock_scene.py {png} {paleta}` → **abrir o mock e validar leitura em 1x**
   - Critérios: checklist de crítica visual do guia canônico. Reprovou → ajustar a spec (o output/frame específico) e repetir.
6. Gate final: `python palette_check.py {png} {paleta}` deve APROVAR para cada output/sheet relevante.
7. Entregar: PNG aprovado em `ArteFonte/IA/Selected/`; se solicitado export, copiar para `Desenvolvimento/Assets/Art/{destino}` (nomes conforme `Docs/Architecture/Assets/AssetsStructure.md`) e registrar em `Docs/Architecture/indices/assets.md` (mover a linha do asset de "Backlog por Asset" para "Assets Registrados").
8. Retroalimentar pendências em `Desenvolvimento/Docs/TODO.md`.

Para gerar o **concept art (Passo 2)** de personagens/criaturas via ComfyUI (rota C), ou quando não houver ainda spec/context pack, ver `Design/GuiasDeArte/pipeline-ia-sprites.md` — inclui o modo `comfy_batch.py --reference-image` para usar concept art/silhueta como base image-to-image.

## Regras

- Nunca usar cor fora da paleta da região; nunca criar paleta sem registrar.
- Nunca entregar PNG sem a spec correspondente versionada.
- Wiring Unity (prefab/animação/cena) está fora do escopo → sugerir `@UnityDeveloper`.
- Se Python/Pillow não estiver disponível, instalar (`pip install pillow`) ou avisar o usuário antes de prosseguir.
