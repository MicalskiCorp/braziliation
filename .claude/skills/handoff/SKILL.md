---
name: handoff
description: Executa um handoff entre as camadas do fluxo reativo do Braziliation (Pesquisa→Criativo→Docs→Implementação) escrevendo a entrada no TODO da camada seguinte, sem pular etapas nem invocar agentes. Use quando o usuário pedir handoff, "passar para o criativo/arquiteto/dev" ou concluir trabalho que gera pendência em outra camada.
---

# Skill: handoff

O modelo do projeto é **reativo**: nenhuma camada invoca a seguinte — ela escreve no TODO da próxima e o usuário aciona quando quiser. Fluxo canônico no `Braziliation/AGENTS.md` (seção "Fluxo entre Camadas").

## Rotas válidas

| De | Para | TODO de destino |
|----|------|-----------------|
| Pesquisa (`Design/Pesquisa/`) | Criativo | `Design/Criativo/TODO.md` |
| Criativo (`Design/Criativo/`) | Documentação | `Desenvolvimento/Docs/TODO.md` |
| Documentação (`Desenvolvimento/Docs/`) | Implementação | `Desenvolvimento/Docs/TODO.md` (item para agente de implementação) |

## Roteiro

1. Identificar a rota: de qual camada vem o material e qual é a próxima. **Nunca pular camada** (ex.: Pesquisa direto para Docs) sem pedido explícito do usuário.
2. Verificar pré-condições do material de origem:
   - Pesquisa→Criativo: pesquisa aprovada, com fontes, em `Design/Pesquisa/{estado}/`;
   - Criativo→Docs: item criativo completo em `Design/Criativo/` (lenda mapeada, personagem, arco);
   - Docs→Implementação: spec/feature documentada em `Docs/GDD/Features/` ou `Docs/Mechanics/`.
3. Ler o TODO de destino e **seguir o formato das entradas existentes** (tabela/seção usada no arquivo).
4. Escrever a entrada com: descrição acionável, referência ao material de origem (caminho), agente sugerido, prioridade.
5. Respeitar os guardrails de `Braziliation/memories/repo/historian-guardrails.md` quando a origem for a camada de Pesquisa (não editar conteúdo criativo; exceção única: `Design/Criativo/TODO.md`).
6. Reportar ao usuário: entrada criada, camada seguinte e comando sugerido para acionar.

## Regras

- Handoff escreve TODO — **nunca executa o trabalho da camada seguinte**.
- Em ambiguidade sobre a rota, perguntar antes de escrever.
