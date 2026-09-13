---
name: nova-cidade
description: Faz o scaffolding de uma nova cidade ou de um novo estado do Braziliation em todos os níveis — estrutura em Design/Criativo pelo template, índices, paleta proposta e pastas de arte no Unity — no padrão de Blumenau. Use quando o usuário pedir para criar ou adicionar nova cidade, novo estado ou nova região ao jogo.
---

# Skill: nova-cidade

Cria a estrutura padronizada de uma região nova. **Conteúdo** (lendas, monstros, lugares, lore) não é desta skill — é do `@GameCreative` (Modo 6); pesquisa é do `@Historiador`.

## Roteiro

1. **Padrão:** Blumenau como referência — `Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/`, `Design/ArteConceitual/Paletas/blumenau.json`, `Assets/Art/Environments/Blumenau/`.
2. **Estado novo** (se o estado ainda não existe): criar `Design/Criativo/Estados/{Estado}/index.md`, `ideias.md` e `cidades/index.md`; em `Estados/index.md`, mover o estado de "Planejados" para "Mapeados". Sem cidade pedida, parar aqui e pedir as primeiras.
3. **Cidade:** conferir no `cidades/index.md` do estado se já existe; criar `Estados/{Estado}/cidades/{Cidade}/index.md` a partir de `Design/Models/ModelCidade.md`; linha no `cidades/index.md` e no `index.md` do estado.
4. **Paleta:** `Design/ArteConceitual/Paletas/{cidade}.json` com `"status": "proposta-inicial"`, derivada da "Paleta Base Sugerida" do `Design/GuiasDeArte/palette-guide.md`; camadas da região só com direção do usuário (materiais, clima, tema); registrar a seção da cidade no `palette-guide.md`.
5. **Unity:** `Desenvolvimento/Assets/Art/Environments/{Cidade}/` com `Backgrounds/`, `Palettes/`, `Props/`, `Tilesets/` (padrão do `Docs/Architecture/Assets/AssetsStructure.md`), de preferência pelo Editor, que gera os `.meta`.
   > **Fronteira de agente:** executado pelo `@GameCreative` (sem `Bash`, não toca o engine), **pular** este passo e registrar a pendência para o `@UnityDeveloper` no TODO de Dev. Executar direto só com acesso de engine (usuário, orquestrador ou `@UnityDeveloper`).
6. **Registros:** pastas novas em `Docs/Architecture/indices/assets.md`; pendências no TODO de quem executa e no da camada seguinte (lendas e paleta a aprovar → TODO criativo; pastas Unity → TODO de Dev). Lacuna de **pesquisa** é reportada ao usuário para acionar o `@Historiador` — a camada criativa não escreve no TODO de Pesquisa (rota invertida).
7. **Reportar:** árvore criada + próximos passos por camada (pesquisa → criativo → arte).

## Regras

- Nomes: PascalCase nas pastas Unity (`Environments/Itajai/`), kebab/lowercase nos JSON (`itajai.json`).
- Não inventar direção de paleta sem input — na ausência, usar só a base do palette-guide e marcar TODO de direção de arte.
