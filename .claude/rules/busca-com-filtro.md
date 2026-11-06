# Busca com filtro

Antes de procurar arquivo, regra ou processo: [`estrutura.md`](../../estrutura.md), uma vez por sessão.

- Caminho conhecido (mapa, pedido, `CLAUDE.md`) → `Read` direto, sem `Glob` para confirmar.
- `Glob`/`Grep` com `path` de pasta, nunca a raiz; `**/*.ext` solto só para listar pasta delimitada.
- `Glob` com `path`: padrão sem `/` (falha no Windows) — `**/*Save*Tests.cs`, não `Tests/**/*.cs`.
