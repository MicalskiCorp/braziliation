---
name: sprite-pipeline
description: Gera um sprite pixel art programático seguindo o pipeline do Braziliation — spec JSON, ciclo gerar→visualizar→criticar→refinar, validação de paleta e mock 320x180. Use quando o usuário pedir para gerar/criar sprite, placeholder, prop pixel art ou validar um sprite existente.
---

# Skill: sprite-pipeline

Processo canônico: **`Design/GuiasDeArte/pipeline-sprites-programaticos.md`** — leia-o integralmente antes de começar; esta skill é só o roteiro de execução.

## Roteiro

1. Ler o guia canônico + `style-bible.md` + `sprite-scale-guide.md`.
2. Carregar a paleta da região: `Design/ArteConceitual/Paletas/{regiao}.json`. Se não existir, derivar do `palette-guide.md` com `"status": "proposta-inicial"` e avisar o usuário.
3. Criar/confirmar brief e context pack em `Design/ArteFonte/IA/ContextPacks/{asset}/` (templates em `GuiasDeArte/`).
4. Escrever a spec `{asset}.spec.json` — **silhueta primeiro** (1 cor), depois detalhe.
5. Executar o ciclo com as ferramentas de `Design/ArteFonte/Ferramentas/` (requer Python + Pillow):
   - `python render_spec.py {spec}` → PNG em `ArteFonte/IA/Outputs/`
   - `python upscale_preview.py {png} -s 8 --grid` → **abrir a imagem com Read e criticar**
   - `python mock_scene.py {png} {paleta}` → **abrir o mock e validar leitura em 1x**
   - Critérios: checklist de crítica visual do guia canônico. Reprovou → ajustar spec e repetir.
6. Gate final: `python palette_check.py {png} {paleta}` deve APROVAR.
7. Entregar: PNG aprovado em `ArteFonte/IA/Selected/`; se solicitado export, copiar para `Desenvolvimento/Assets/Art/{destino}` (nomes conforme `Docs/Architecture/Assets/AssetsStructure.md`) e registrar em `Docs/Architecture/indices/assets.md`.
8. Retroalimentar pendências em `Desenvolvimento/Docs/TODO.md`.

## Regras

- Nunca usar cor fora da paleta da região; nunca criar paleta sem registrar.
- Nunca entregar PNG sem a spec correspondente versionada.
- Wiring Unity (prefab/animação/cena) está fora do escopo → sugerir `@UnityDeveloper`.
- Se Python/Pillow não estiver disponível, instalar (`pip install pillow`) ou avisar o usuário antes de prosseguir.
