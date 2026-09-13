---
name: novo-inimigo
description: Cria um inimigo novo do Braziliation como dado, não como código — perfil EnemyBehaviorProfile no motor EnemyBrain, EnemyProfileAsset em Assets/ScriptableObjects/Enemies/, linha no catálogo de InimigosIA.md e um teste que fixa o comportamento. Use quando o usuário pedir "novo inimigo", "criar inimigo", "perfil de inimigo" ou quando a skill fechar-decisao aprovar o inimigo base.
---

# Skill: novo-inimigo

O motor de IA é genérico: `EnemyBrain` (C# puro, `src/Braziliation.Game.Core/Enemies/`) decide a partir de um `EnemyBehaviorProfile` (números + `EnemyAggressionStyle`). Inimigo novo é **um perfil**, não uma classe. Guia completo: `Desenvolvimento/Docs/Mechanics/InimigosIA.md`.

## Roteiro

1. **Origem.** O inimigo precisa de uma origem criativa (monstro da cidade em `Design/Criativo/Estados/`, lenda em `Design/Criativo/Lendas/` ou um DDR da skill `fechar-decisao`). Sem origem, avisar e sugerir `fechar-decisao` antes.
2. **Ler o motor:** `EnemyBehaviorProfile.cs` (campos, faixas válidas, estilos de agressão) e a seção "Como criar um inimigo novo" de `InimigosIA.md`.
3. **Escolher o estilo** (`EnemyAggressionStyle`) que descreve o comportamento. Se nenhum servir, **parar**: estilo novo é mudança de motor → propor ao `@TechLead` (e ao `@SystemsDeveloper` para implementar com teste), não improvisar no perfil.
4. **Definir os números** (vida, dano, velocidades, alcances, tempos de reação/cooldown) partindo do inimigo mais parecido já catalogado; marcar como provisórios.
5. **Teste primeiro:** em `Desenvolvimento/Tests/Braziliation.Game.Tests/EnemyBrainTests.cs`, adicionar um caso que monta o perfil e verifica o comportamento que define o inimigo (ex.: "persegue ao ver o jogador a 4 unidades", "recua após atacar"). Rodar `dotnet test`.
6. **Asset Unity:** criar o `EnemyProfileAsset` em `Desenvolvimento/Assets/ScriptableObjects/Enemies/{Nome}.asset` com os mesmos números. Se não for possível criar o `.asset` sem o Editor, registrar a pendência para o `@UnityDeveloper` (menu `Create > Braziliation > Enemy Profile`) com os valores exatos.
7. **Catálogo:** adicionar a linha do inimigo em `InimigosIA.md` (nome, estilo, números, origem criativa, sprite).
8. **Arte e wiring:** sprite existe? Senão → `novo-asset`/`sprite-pipeline` (`@SpriteArtist`). Prefab e animações → pendência para o `@UnityDeveloper`. Rodar `unity-validar` se algo em `Assets/` mudou.

## Regras

- Nenhum código novo por inimigo. Se precisou de código, é mudança de motor e segue o passo 3.
- Números iguais no teste, no `.asset` e no catálogo — o teste é a fonte que o CI verifica.
