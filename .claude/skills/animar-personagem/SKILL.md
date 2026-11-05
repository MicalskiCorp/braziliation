---
name: animar-personagem
description: Anima um personagem, inimigo ou criatura do Braziliation pelo esqueleto do motor pxfx (ADR-016) — rig.json (bípede, mecânico, quadrúpede, serpente), blocagem no manequim, gabarito e pele, anim.json com poses-chave e eventos de impacto, sheet + JSON lateral para o Unity, crítica em passos consecutivos. Use quando o usuário pedir animação de personagem/inimigo (idle, andar, correr, ataque, dano, morte), "animar no esqueleto", "rig", "pose", "pele do personagem" ou quando um item de animação dos TODOs for executado.
allowed-tools: Bash(py -m pxfx*) Bash(py Design/ArteFonte/Ferramentas/*)
---

# Skill: animar-personagem

Processo canônico: **`Design/GuiasDeArte/animacao-por-esqueleto.md`** — leia antes; esta skill é o roteiro.
Rode tudo de `Design/ArteFonte/Ferramentas/`.

## Roteiro

1. **Rig:** escolher o modelo (tabela do guia) e escrever `ContextPacks/{asset}/{asset}.rig.json` com
   `"escala": 2.5`, `"regiao"` e, se já existir, `"rampas"` (4 degraus aceso → escuro por material, keys da paleta).
2. **Blocagem:** animar primeiro no manequim (`pxfx/esqueleto/modelos/manequim_bipede.rig.json`). Ponto de
   partida da biblioteca: `py -m pxfx.esqueleto.animar <rig> --biblioteca melee/sword-slash --acao ataque`.
   Escrever o `{acao}.anim.json` próprio (chaves, chegada, eventos de impacto com `congela`).
3. **Olhar a `_tira.png`** (passos consecutivos) e o relatório. Corrigir o PIOR problema, gerar de novo.
   **Três rodadas no mínimo**; mostrar o GIF ao usuário e aprovar o MOVIMENTO antes de qualquer pele.
4. **Gabarito:** `py -m pxfx.esqueleto.animar <rig> --referencia` → pintar a pele por cima (Aseprite via MCP
   ou concept aprovado reduzido com `pixelize.py`) só com keys da paleta; declarar as rampas no rig.
5. **Com pele:** gerar de novo; relatório sem FALHA (paleta, cores ≤ 32). Retocar quadros de pico em
   `{acao}.retoques/fNN.png` e conferir `retoques_a_revisar` no JSON.
6. **Entregar:** sheet + `.json` em `Assets/Art/{destino}` (o `SheetAutoSlicer` fatia pelo JSON) → skill
   `meta-check` → registro em `Docs/Architecture/indices/assets.md`. Clipe e prefab = `@UnityDeveloper`.

## Regras

- Pose nas unidades do boneco de 38 px; nunca multiplicar à mão pela escala.
- Pele só com cores da paleta regional; cor fora de rampa é detalhe fixo (não re-ilumina) — de propósito.
- Movimento se julga em passos consecutivos; aprovar no checador não é estar pronto.
- Rosto, expressão, smear e virar de costas são retoque ou pele extra — não forçar o esqueleto.
- Faltou recurso no motor (arma na mão, osso novo): registrar no TODO de Desenvolvimento, não improvisar no asset.
