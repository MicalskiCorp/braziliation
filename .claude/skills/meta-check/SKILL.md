---
name: meta-check
description: Audita pares asset/.meta sob Desenvolvimento/Assets/ — detecta assets sem .meta (GUID instável) e .meta órfãos sem asset correspondente. Use quando o usuário pedir para validar/auditar assets do Unity, antes de commitar novos arquivos em Assets/, ou depois que @SpriteArtist entregar sprites em Assets/Art/.
---

# Skill: meta-check

Todo asset (arquivo ou pasta) versionado em `Desenvolvimento/Assets/` precisa de um `.meta` correspondente — é ele que guarda o GUID usado por cenas, prefabs e ScriptableObjects para referenciar o asset. Um asset sem `.meta` recebe um GUID novo na próxima vez que o Unity Editor abrir o projeto; se esse asset já for referenciado em algum lugar por GUID antigo (de um `.meta` perdido ou nunca criado), a referência quebra silenciosamente — sem erro de compilação, só um campo vazio no Inspector.

Nenhuma das 8 skills existentes cobre isso: `structure-audit` compara disco vs. documentação, não pares `.meta`.

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

## Interpretando o resultado

- **Asset sem `.meta`**: se for um arquivo real (`.png`, `.cs`, `.asset`) já usado em alguma cena/prefab, é crítico — abrir o Unity Editor uma vez com o projeto para deixá-lo gerar o `.meta`, depois conferir no Git que o novo `.meta` foi adicionado. Se for pasta vazia de scaffold (só contém `.gitkeep`), é baixa severidade — o Editor gera o `.meta` da pasta automaticamente e não há referência para quebrar.
- **`.meta` órfão**: geralmente sobra de um asset renomeado/movido fora do Editor (ex.: `mv` manual, ferramenta externa). Remover o `.meta` órfão ou restaurar o asset — nunca deixar os dois estados coexistirem.

## Regras

- Esta skill só relata — não deleta nem gera `.meta` (isso é trabalho do Unity Editor, não deve ser simulado por código).
- Se encontrar gaps críticos (assets de produção sem `.meta`), registrar como pendência em `Desenvolvimento/Docs/TODO.md` apontando `@UnityDeveloper`.
