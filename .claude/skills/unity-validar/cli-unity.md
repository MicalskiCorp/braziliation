# CLI `unity` — cola para dirigir o Editor aberto

> Por que existe (ADR-015): até 2026-11-04 cada sessão de Unity redescobria a CLI. `unity list`
> devolvia 22 mil caracteres, `unity skill show` 18 mil e `unity command` sem filtro 16 mil, e
> essas saídas ficavam no contexto, relidas a cada requisição da sessão. Comece por aqui.
> Os comandos e a sintaxe abaixo são os que deram certo nas execuções da Central.

**Não rode** `unity list`, `unity command` sem filtro, `unity skill show` nem `--help` para "ver o que
tem". Precisa de um comando que não está aqui? Filtre:
`unity command --query <termo> --detail compact --limit 10`.

## Antes de tudo

- **Validar compilação ou testes não é por aqui:** é `py .claude/skills/unity-validar/scripts/validar.py`
  (com `--testes`). `unity command recompile` à mão não grava o resultado, e o pre-commit recusa.
- Rode de dentro de `Desenvolvimento/` ou passe `--project-path "D:/Backup/Projetos/Games/Braziliation/Desenvolvimento"`.
- `unity status`: o Editor precisa aparecer como `ready`. Sem conexão, é provável que o Editor esteja em
  **Safe Mode** por erro de compilação: rode o `validar.py` (batchmode) para ver os erros, não edite cena à mão.
- Sufixos úteis: `--json` (saída para script), `--timeout 60` (o padrão é 30 s), `2>&1`.

## Sintaxe

```bash
unity command <nome>                              # sem argumentos
unity command <nome> -- <posicional>              # ex.: open_scene -- Assets/Scenes/DemoGameplay.unity
unity command <nome> -- '<json com os argumentos>' # ex.: find_gameobjects -- '{"name":"Player_Demo"}'
unity command <nome> --<arg> <valor>              # ex.: menu --path "Tools/Braziliation/Setup/..."
```

## Os comandos que o projeto usa

| Para | Comando |
|---|---|
| Estado do Editor | `status` · `command editor_status` |
| Console (erros e logs) | `command console_status` · `command console` |
| Cenas | `command list_open_scenes` · `command open_scene -- <caminho.unity>` · `command create_scene` |
| Achar e ler objetos | `command find_gameobjects -- '{"name":"…"}'` · `command get_scene_hierarchy` · `command get_component_properties` · `command get_serialized_fields` |
| Mudar objetos | `command create_gameobject` · `command delete_gameobject` · `command set_serialized_field` |
| Assets | `command find_assets` · `command get_import_settings` |
| Menu do projeto (editor tools) | `command menu --path "Tools/Braziliation/…"` |
| C# no Editor | `command eval_file --file <arquivo.cs>` · `command run_script --file <arquivo.cs> --entry "Classe.Metodo"` |
| Play Mode | `command editor_play` · `command editor_stop` · `command set_autotick` |
| Imagem da tela | `command capture_game_view` · `command capture_scene_view` — **sempre com `save_path`** (ver abaixo) |

## O que mais gasta contexto

- **Captura sem `save_path` volta a imagem inteira em base64 no resultado.** Passe um caminho fora de
  `Assets/` (a pasta temporária do sistema serve) e abra a imagem pelo caminho, se precisar vê-la.
- **`eval_file` e `run_script`:** imprima só o que vai usar. Um dump de hierarquia inteira ou de JSON
  grande fica no contexto até o fim da sessão.
- **Ler `.unity`, `.prefab` ou `.inputactions` inteiros com Read** custa de 5 a 15 mil tokens. Para
  uma informação, prefira `find_gameobjects`/`get_component_properties` ou um `grep` no arquivo.
