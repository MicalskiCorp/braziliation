# Ferramentas — Pipeline Programático de Sprites

Scripts que sustentam o pipeline descrito em [`../../GuiasDeArte/pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md). Todos rodam **sem nenhum agente de IA** — são código puro, versionado e reproduzível.

**Dependência única:** `pip install pillow` (Python 3.10+).

## Scripts

| Script | Função | Uso típico |
|--------|--------|-----------|
| [`render_spec.py`](render_spec.py) | Transforma spec JSON (matriz de chars + paleta) em PNG | `python render_spec.py spec.json` |
| [`palette_check.py`](palette_check.py) | Valida PNG contra paleta oficial (cores permitidas + limite de 16) | `python palette_check.py sprite.png paleta.json` |
| [`mock_scene.py`](mock_scene.py) | Compõe sprite em cena mock 320×180 para teste de leitura 1x | `python mock_scene.py sprite.png paleta.json` |
| [`upscale_preview.py`](upscale_preview.py) | Amplia PNG (nearest-neighbor, grade opcional) para crítica visual | `python upscale_preview.py sprite.png -s 8 --grid` |

## Onde vive o quê

- **Specs de sprite (fonte)**: junto do context pack do asset em `../IA/ContextPacks/{asset}/` — a spec É a fonte editável do sprite programático.
- **Paletas machine-readable**: `../../ArteConceitual/Paletas/*.json` (derivadas do [`palette-guide.md`](../../GuiasDeArte/palette-guide.md)).
- **PNGs gerados**: `../IA/Outputs/` → curadoria em `../IA/Selected/` → final em `Desenvolvimento/Assets/Art/`.
- **Import no Unity**: automático — `Desenvolvimento/Assets/Editor/Art/SpriteImportPostprocessor.cs` força 16 PPU / Point / sem compressão em tudo que entra em `Assets/Art/`.

## Formato da spec (Opção A)

```json
{
  "name": "prop_blumenau_floodgate_lever",
  "size": [32, 32],
  "palette": "../../ArteConceitual/Paletas/blumenau.json",
  "rows": ["...7A...", "..77AA..", "..."]
}
```

Cada caractere é um pixel: `.` = transparente; os demais são a `key` da cor na paleta JSON. `rows` deve ter exatamente `size[1]` linhas de `size[0]` caracteres.
