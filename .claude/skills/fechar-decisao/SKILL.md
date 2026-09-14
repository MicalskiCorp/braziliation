---
name: fechar-decisao
description: Fecha uma decisão de design pendente do Braziliation (premissa, protagonista, arma inicial, inimigo base, números de crafting/build, totens, materiais) em um Registro de Decisão de Design — problema, 2 a 3 opções amarradas à lore e aos sistemas existentes, recomendação e números iniciais — e, aprovada, grava a decisão, baixa a pendência e faz o handoff. Use quando o usuário pedir para "decidir", "fechar decisão", "definir a arma/inimigo/premissa" ou para destravar um item "Design" parado nos TODOs.
---

# Skill: fechar-decisao

As camadas criativas têm ferramentas para **gerar** ideias (brainstorm, cidades, lendas) e nenhuma para **fechar** uma. Por isso as pendências de design de prioridade Alta ficam paradas. Esta skill produz a decisão; quem decide é o usuário.

## Roteiro

1. **Escolher a pendência.** Se o usuário não disser qual, listar as de tipo Design com prioridade Alta em `Desenvolvimento/Docs/TODO.md` e `Design/Criativo/TODO.md` e sugerir começar pela que desbloqueia mais outras. A premissa (`Design/Criativo/Historia/premissa.md`) vem antes de todas.
2. **Juntar o contexto que restringe a decisão** — ler só o necessário:
   - lore e tom: `Design/Criativo/Historia/premissa.md`, a cidade envolvida em `Design/Criativo/Estados/`, `Desenvolvimento/Docs/GDD/visao.md`;
   - sistemas que já existem e aceitam a decisão como dado: `Docs/Mechanics/` (Crafting, Build, InimigosIA) e o código em `src/Braziliation.Game.Core/`;
   - assets já prontos que tornam uma opção mais barata (ex.: o Autômato Abandonado já tem sprite e perfil de IA).
3. **Escrever o registro** em `Desenvolvimento/Docs/GDD/Decisoes/DDR-{NNN}-{slug}.md` (numeração sequencial; criar a pasta e o `index.md` na primeira vez), com:
   - **Problema** — o que está parado e o que depende disto;
   - **Opções** (2 ou 3) — cada uma com como se encaixa na lore, custo de implementação com o que já existe, e o que fecha/abre para depois;
   - **Recomendação** — uma, com o porquê;
   - **Números iniciais** — valores de partida para tuning (vida, dano, cooldown, slots), explicitamente marcados como provisórios;
   - **Status:** `Proposta`.
4. **Apresentar ao usuário** a recomendação em poucas linhas e perguntar: aprovar, escolher outra opção ou ajustar. **Não aprovar sozinho.**
5. **Ao aprovar:**
   - status do DDR → `Aprovada` com data;
   - aplicar a decisão onde ela mora (ex.: preencher `premissa.md`; tabela de `Mechanics/Build.md`; perfil em `Mechanics/InimigosIA.md`);
   - baixar a pendência no TODO de origem: em `Desenvolvimento/Docs/TODO.md` a linha **sai** (o DDR e o commit são o registro); em `Design/Criativo/TODO.md` ela vai para `## Concluído` com a data e o link do DDR;
   - fazer o handoff para a implementação com a skill `handoff` (ex.: inimigo base → `novo-inimigo`).

## Regras

- Uma decisão por execução. Decisão grande (premissa) pode virar mais de um DDR encadeado.
- Opção que exige sistema novo quando um existente resolveria deve dizer isso explicitamente.
- Números sempre provisórios e rastreáveis ao DDR — o tuning muda o número, não reescreve a decisão.
- Não editar `Design/Pesquisa/`. Fato histórico novo → pendência para o `@Historiador`.
