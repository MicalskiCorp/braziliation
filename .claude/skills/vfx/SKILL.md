---
name: vfx
description: Cria, recolore, reescala, porta ou exporta efeitos visuais (VFX) do Braziliation no motor pxfx (ADR-016) — fogo, explosão, vapor, faísca, água, raio, impacto, aura — com a régua de qualidade do PixelFX, paleta regional, escala de 96 px, paridade com o original ao portar e sheet + JSON para o Unity. Use quando o usuário pedir efeito visual, VFX, partícula, "portar efeito do PixelFX", "onda de efeitos" ou um item de VFX dos TODOs.
allowed-tools: Bash(py -m pxfx*) Bash(node Design/ArteFonte/Ferramentas/pxfx/paridade/*)
---

# Skill: vfx

Processo canônico: **`Design/GuiasDeArte/vfx-guide.md`** (regras do projeto, régua, sintoma → correção, método).
Port e convenções: `Design/ArteFonte/Ferramentas/pxfx/index.md`. Rode tudo de `Design/ArteFonte/Ferramentas/`.

## Roteiro

1. **Já existe?** `py -m pxfx.render <categoria>` dos portados; o original está em
   `vendor/pixelfx/src/fx/` (ler sob demanda, nunca editar). Quase todo pedido é um efeito existente com outra
   rampa, seed ou escala.
2. **Portar** (efeito ainda não portado, ou uma onda do TODO): `_lib` da categoria primeiro, depois o efeito,
   seguindo as convenções do `pxfx/index.md`; `py -m pxfx.paridade <id>` até OK na escala 1.
3. **Reescalar:** `py -m pxfx.render <id> --escala 2.5 --all`; laço de pontos em passo fixo vira passo `1/p.k`,
   mantendo o caminho da escala 1 (a paridade tem que continuar OK).
4. **Recolorir** pela paleta: `--regiao blumenau --rampa <keys escuro → claro>`.
5. **Criticar:** 3–5 rascunhos divergentes quando a direção estiver aberta; três rodadas no mínimo; corrigir o
   pior problema por rodada (tabela do guia). `py -m pxfx.check <id> --escala 2.5` limpo.
6. **Exportar:** `--sheet --nome vfx_<nome>` → `Assets/Art/VFX/`, `palette_check.py` no sheet, skill `meta-check`,
   registro em `Docs/Architecture/indices/assets.md`. Atualizar a tabela "Ondas" do `pxfx/index.md`.

## Regras

- Nunca editar `vendor/pixelfx/`. Correção vai para o `pxfx`.
- Brilho aditivo e fumaça translúcida reprovam no `palette_check` até existir a camada emissiva: exportar com
  `"light": 0` ou dither, e registrar o brilho desejado no brief.
- Motivo de fantasia genérica (arcano, sagrado) é redesenhado para lenda/clero, nunca usado cru.
- Crédito: efeito que adapta receita do Hugo Duprez mantém o crédito no docstring.
