# Aseprite via MCP (pixel-mcp)

O `@SpriteArtist` controla o Aseprite instalado na máquina pelo servidor MCP **pixel-mcp** (MIT, 50 ferramentas: desenho, paleta, sombreamento, dithering, outline, camadas, frames e exportação de spritesheet). Uso previsto: **retoque fino** depois do `render_spec.py` e o **pixel pass** da rota C — a spec JSON continua sendo a fonte do sprite, e todo PNG retocado passa de novo pelo `palette_check.py`.

## Onde está cada peça

| Peça | Local |
|------|-------|
| Aseprite (Steam, 1.3.18) | `F:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe` |
| Servidor (release v0.5.0, sha256 conferido) | `D:\Tools\pixel-mcp\pixel-mcp.exe` |
| Configuração do servidor | `C:\Users\Usuario\.config\pixel-mcp\config.json` (`aseprite_path`, `temp_dir`, `timeout`) |
| Perfil limpo do Aseprite | `D:\Tools\pixel-mcp\aseprite-perfil\` |
| Registro no projeto | `.mcp.json` (servidor `aseprite`) + `enabledMcpjsonServers` em `.claude/settings.json` |

## Por que um perfil limpo

A extensão **PixelLab** instalada no Aseprite do usuário dá erro de Lua quando o Aseprite roda em modo batch (`handle-pose.lua:58: attempt to index a nil value`) e imprime esse erro antes da resposta dos scripts. O pixel-mcp espera JSON puro e falhava com `invalid character 'C'`. O servidor roda com `APPDATA` apontando para `aseprite-perfil/`, então esse Aseprite sobe sem extensões — **o Aseprite do dia a dia, com a PixelLab, não é afetado**.

## Verificação rápida

Com o Claude Code aberto no repositório, `/mcp` deve listar `aseprite` como conectado. Teste feito em 2026-09-13: `get_sprite_info` num PNG do projeto, `create_canvas` 16×16, `draw_pixels` e `export_sprite` para PNG — todos OK.

## Atualizar

Baixar a release nova de <https://github.com/willibrandon/pixel-mcp/releases>, conferir o `checksums.txt`, substituir o `.exe`. Se o Aseprite mudar de pasta (letra de drive da biblioteca Steam), atualizar `aseprite_path` no `config.json`.
