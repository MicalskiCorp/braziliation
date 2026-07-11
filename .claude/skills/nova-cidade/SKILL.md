---
name: nova-cidade
description: Faz o scaffolding completo de uma nova cidade/região do Braziliation em todos os níveis — Design/Criativo, paleta, pastas de arte no Unity — mantendo o padrão de Blumenau. Use quando o usuário pedir para criar/adicionar nova cidade, novo estado ou nova região ao jogo.
---

# Skill: nova-cidade

Cria a estrutura vazia e padronizada de uma região nova. **Conteúdo criativo (lendas, lore) não é desta skill** — é do `@GameCreative`; pesquisa é do `@Historiador`.

## Roteiro

1. **Verificar o padrão existente**: usar Blumenau como referência — `Design/Criativo/` (organização por estado/cidade), `Design/ArteConceitual/Paletas/blumenau.json`, `Assets/Art/Environments/Blumenau/`.
2. **Design/Criativo**: criar a estrutura da cidade seguindo o padrão das cidades existentes (verificar organização real em `Design/Criativo/` antes de criar).
3. **Paleta**: criar `Design/ArteConceitual/Paletas/{cidade}.json` com `"status": "proposta-inicial"`:
   - Derivar da "Paleta Base Sugerida" do `Design/GuiasDeArte/palette-guide.md`;
   - Adicionar camadas específicas da região se o usuário fornecer direção (materiais, clima, tema);
   - Registrar a seção da cidade no próprio `palette-guide.md` (padrão da seção "Blumenau").
4. **Unity**: criar `Desenvolvimento/Assets/Art/Environments/{Cidade}/` com subpastas `Backgrounds/`, `Palettes/`, `Props/`, `Tilesets/` (padrão do `Docs/Architecture/Assets/AssetsStructure.md`).
   > Pastas vazias não são versionadas pelo git e o Unity gera `.meta` — criar um `index.md`/`.gitkeep` apenas nas pastas de Design; no Unity, criar as pastas pelo Editor quando possível.
5. **Registros**: adicionar as novas pastas em `Docs/Architecture/indices/assets.md`; registrar pendências (pesquisa, lendas, paleta a aprovar) nos TODOs das camadas corretas (`Design/Pesquisa/TODO.md`, `Design/Criativo/TODO.md`, `Desenvolvimento/Docs/TODO.md`).
6. **Reportar**: árvore criada + próximos passos por camada (pesquisa → criativo → arte).

## Regras

- Nomes: PascalCase nas pastas Unity (`Environments/Itajai/`), kebab/lowercase nos JSON (`itajai.json`).
- Não inventar direção de paleta sem input — na ausência, usar só a base do palette-guide e marcar TODO de direção de arte.
