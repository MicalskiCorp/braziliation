---
name: meta-check
description: Audita pares asset/.meta sob Desenvolvimento/Assets/ — detecta assets sem .meta (GUID instável) e .meta órfãos sem asset correspondente. Use quando o usuário pedir para validar/auditar assets do Unity, antes de commitar novos arquivos em Assets/, ou depois que @SpriteArtist entregar sprites em Assets/Art/.
---

# Skill: meta-check

Todo asset (arquivo ou pasta) versionado em `Desenvolvimento/Assets/` precisa de um `.meta` correspondente — é ele que guarda o GUID usado por cenas, prefabs e ScriptableObjects para referenciar o asset. Um asset sem `.meta` recebe um GUID novo na próxima vez que o Unity Editor abrir o projeto; se esse asset já for referenciado em algum lugar por GUID antigo (de um `.meta` perdido ou nunca criado), a referência quebra silenciosamente — sem erro de compilação, só um campo vazio no Inspector.

Nenhuma outra skill cobre isso: `structure-audit` compara disco vs. documentação, não pares `.meta`.

## Quando rodar

- Depois que `@SpriteArtist` entregar um sprite/tileset novo em `Assets/Art/` (passo final do pipeline de 5 etapas).
- Antes de qualquer commit que adicione arquivos/pastas em `Desenvolvimento/Assets/`.
- Quando `@UnityDeveloper` desconfiar de uma referência quebrada (campo vazio no Inspector, prefab "Missing").
- Periodicamente como parte de `structure-audit` nível 1 (Assets Unity) — pode ser chamado a partir de lá.

## Como rodar

```
py .claude/skills/meta-check/check_meta_pairs.py
```

Roda a partir da raiz do repo (`Braziliation/`); assume `Desenvolvimento/Assets` por padrão (`--assets-dir` para outro caminho). Sai com código 0 se não houver gaps, 1 se houver — usável tanto por um agente quanto num hook.

### Contra o índice do git, não contra o disco

```
py .claude/skills/meta-check/check_clean_checkout.py             # meta + paletas
py .claude/skills/meta-check/check_clean_checkout.py --gates meta
py .claude/skills/meta-check/check_clean_checkout.py --keep      # mantém a cópia
```

`check_meta_pairs.py` olha a **árvore de trabalho**. O CI olha um **checkout limpo** — e os dois divergem sempre que algo existe no disco mas não no git. Em 13 set 2026 duas pastas de arte ficaram vazias com os `.meta` ainda versionados; git não versiona pasta vazia, então em checkout limpo o `.meta` virava órfão. O CI reprovou por seis dias e o `meta-check` local passou o tempo todo, porque na máquina do desenvolvedor as pastas existem.

`check_clean_checkout.py` materializa o índice (`git checkout-index`) numa pasta temporária e roda os gates **a partir dela** — então a versão commitada dos próprios scripts de gate é que decide. É o que o pre-commit executa desde 19 set 2026, no lugar da checagem em disco. Arquivos de LFS materializam como binário de verdade; se algum objeto estiver ausente, o script avisa e não reprova o commit (ambiente incompleto não é erro de conteúdo).

Rode direto quando quiser conferir antes de um push, ou depois de remover arquivos de uma pasta de `Assets/`.

## Interpretando o resultado

- **Asset sem `.meta`**: se for um arquivo real (`.png`, `.cs`, `.asset`) já usado em alguma cena/prefab, é crítico — abrir o Unity Editor uma vez com o projeto para deixá-lo gerar o `.meta`, depois conferir no Git que o novo `.meta` foi adicionado. Se for pasta vazia de scaffold (só contém `.gitkeep`), é baixa severidade — o Editor gera o `.meta` da pasta automaticamente e não há referência para quebrar.
- **`.meta` órfão**: geralmente sobra de um asset renomeado/movido fora do Editor (ex.: `mv` manual, ferramenta externa). Remover o `.meta` órfão ou restaurar o asset — nunca deixar os dois estados coexistirem.

## Regras

- Esta skill só relata — não deleta nem gera `.meta` (isso é trabalho do Unity Editor, não deve ser simulado por código).
- Se encontrar gaps críticos (assets de produção sem `.meta`), registrar como pendência em `Desenvolvimento/Docs/TODO.md` apontando `@UnityDeveloper`.
