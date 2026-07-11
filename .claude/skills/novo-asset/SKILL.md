---
name: novo-asset
description: Cria o brief e o context pack de um novo asset visual do Braziliation seguindo os templates de GuiasDeArte, define escala/paleta/destino e registra a pendência. Use quando o usuário pedir um asset novo (sprite, prop, tileset, personagem) e ainda não existir brief/context pack para ele.
---

# Skill: novo-asset

Nenhum asset começa com "faz um sprite de X" — esta skill formaliza a entrada.

## Roteiro

1. Ler os templates: `Design/GuiasDeArte/asset-brief-template.md` e `context-pack-template.md`.
2. Localizar a origem criativa: feature em `Design/Criativo/` ou `Desenvolvimento/Docs/GDD/Features/`. Se não existir, avisar — conceito criativo é do `@GameCreative`, não desta skill.
3. Definir com o usuário (perguntar apenas o que não puder inferir):
   - **Função** do asset no jogo; **região/cidade**;
   - **Tamanho** conforme `sprite-scale-guide.md`; **paleta** (`Design/ArteConceitual/Paletas/{regiao}.json`);
   - **Destino final** em `Assets/Art/` + nome conforme convenções do `Docs/Architecture/Assets/AssetsStructure.md` (prefixos `chr_`, `enm_`, `env_`, `prop_`, `ui_`, `vfx_`);
   - **Rota de geração**: programática (`pipeline-sprites-programaticos.md`) ou difusão (`pipeline-ia-sprites.md`).
4. Criar `Design/ArteFonte/IA/ContextPacks/{asset}/context.md` preenchendo o template (usar `exemplo-prop-comporta-blumenau/` como referência de preenchimento).
5. Registrar a pendência de produção em `Desenvolvimento/Docs/TODO.md`, apontando o agente executor (`@SpriteArtist` para rota programática).

## Regras

- Um context pack por asset ou lote coeso; nome da pasta em kebab-case descritivo.
- Não gerar o sprite aqui — a produção é da skill `sprite-pipeline` / `@SpriteArtist`.
- Se a paleta da região não existir, registrar isso como pendência no TODO antes de prosseguir.
