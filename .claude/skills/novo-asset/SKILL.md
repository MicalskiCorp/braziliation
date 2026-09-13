---
name: novo-asset
description: Cria o brief e o context pack de um novo asset visual do Braziliation seguindo os templates de GuiasDeArte, define escala/paleta/destino e registra a pendência. Use quando o usuário pedir um asset novo (sprite, prop, tileset, personagem) e ainda não existir brief/context pack para ele.
---

# Skill: novo-asset

Nenhum asset começa com "faz um sprite de X" — esta skill formaliza a entrada.

## Roteiro

Esta skill cobre o brief + context pack — que são os Passos 3/4 de entrada do fluxo completo (`Design/GuiasDeArte/pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas`). Para **personagens/inimigos complexos** (múltiplas ações/estados), os Passos 2 e 3 desse fluxo devem estar resolvidos antes do passo 4 abaixo; para **props simples**, eles são opcionais.

1. Ler os templates: `Design/GuiasDeArte/asset-brief-template.md`, `context-pack-template.md` e, se o asset tiver múltiplas ações, `variation-spec-template.md`.
2. Localizar a origem criativa: feature em `Design/Criativo/` ou `Desenvolvimento/Docs/GDD/Features/`. Se não existir, avisar — conceito criativo é do `@GameCreative`, não desta skill.
3. **Se for personagem/inimigo/boss** (não prop simples): verificar se já existe concept art aprovado em `Design/ArteConceitual/{Personagens|Criaturas}/{asset}/concept.md` com `status: aprovado`.
   - Se não existir: avisar que o Passo 2 (concept art) ainda não foi feito e sugerir acionar `@SpriteArtist` para gerá-lo (rota C, `pipeline-ia-sprites.md`) antes de continuar — não criar o context pack sem isso.
   - Se existir mas não houver `variation-spec-template.md` preenchido para as ações do brief: preencher `Design/ArteFonte/IA/ContextPacks/{asset}/variations.md` (Passo 3) antes do passo 5.
4. Definir com o usuário (perguntar apenas o que não puder inferir):
   - **Função** do asset no jogo; **região/cidade**;
   - **Tamanho** conforme `sprite-scale-guide.md`; **paleta** (`Design/ArteConceitual/Paletas/{regiao}.json`);
   - **Destino final** em `Assets/Art/` + nome conforme convenções do `Docs/Architecture/Assets/AssetsStructure.md` (prefixos `chr_`, `enm_`, `env_`, `prop_`, `ui_`, `vfx_`);
   - **Rota de geração**: programática (`pipeline-sprites-programaticos.md`) ou difusão (`pipeline-ia-sprites.md`).
5. Criar `Design/ArteFonte/IA/ContextPacks/{asset}/context.md` preenchendo o template (usar `exemplo-prop-comporta-blumenau/` como referência de preenchimento). Se houver concept art aprovado (passo 3), referenciá-lo na seção "Referências Autorizadas".
6. Registrar a pendência de produção em `Desenvolvimento/Docs/TODO.md`, apontando o agente executor (`@SpriteArtist` para rota programática).

## Regras

- Um context pack por asset ou lote coeso; nome da pasta em kebab-case descritivo.
- Não gerar o sprite aqui — a produção é da skill `sprite-pipeline` / `@SpriteArtist`.
- Se a paleta da região não existir, registrar isso como pendência no TODO antes de prosseguir.
- Para personagens/inimigos, não pular o gate de concept art aprovado — é o que torna o spec JSON (Passo 4) rastreável até uma referência visual real.
