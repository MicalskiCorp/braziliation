---
name: handoff
description: Executa um handoff entre as camadas do fluxo reativo do Braziliation (Pesquisa→Criativo→Docs→Implementação) escrevendo a entrada no TODO da camada seguinte, sem pular etapas nem invocar agentes. Use quando o usuário pedir handoff, "passar para o criativo/arquiteto/dev" ou concluir trabalho que gera pendência em outra camada.
---

# Skill: handoff

O modelo do projeto é **reativo**: nenhuma camada invoca a seguinte — ela escreve no TODO da próxima e o usuário aciona quando quiser. Fluxo canônico no `AGENTS.md` (seção "Fluxo entre Camadas"). Operações no TODO da **própria** camada são da skill `gerir-todo`.

## Rotas válidas

| De | Para | Destino |
|----|------|---------|
| Pesquisa (`Design/Pesquisa/`) | Criativo | `Design/Criativo/TODO.md` → `## Handoffs de Pesquisa` |
| Criativo (`Design/Criativo/`) | Documentação | `Desenvolvimento/Docs/TODO.md` → `## Handoffs do @GameCreative` |
| Documentação (`Desenvolvimento/Docs/`) | Implementação | `Desenvolvimento/Docs/TODO.md` → seção da área (Unity, Gameplay, UI e arte) |

## Roteiro

1. Identificar a rota. **Nunca pular camada** (ex.: Pesquisa direto para Docs) sem pedido explícito do usuário.
2. Verificar a pré-condição: pesquisa aprovada e com fontes · item criativo completo (lenda mapeada, personagem, arco, cidade) · spec pronta em `GDD/Features/` ou `Mechanics/`.
3. Ler o TODO de destino. **A seção já existe — nunca criar outra.** Seguir o formato das linhas vizinhas.
4. Escrever conforme a rota (abaixo).
5. Reportar: entrada criada, camada seguinte e comando para acioná-la.

## Pesquisa → Criativo

Três tipos — o `@Historiador` escolhe no Modo 4:

| Tipo | Quando | Briefing |
|------|--------|----------|
| **processar** | Pesquisa aprovada pronta para uso criativo | Sim |
| **brainstorm** | Material para uma sessão criativa | Sim |
| **revisão** | Pesquisa nova enriquece ou contradiz lore existente | Não — a linha aponta direto para a pesquisa e diz quais arquivos criativos ela afeta |

1. Briefing em `Design/Pesquisa/Handoffs/AAAA-MM-DD-{tema}.md`:

   ```markdown
   # Handoff — {tema} ({tipo})
   > Data · pesquisa de origem: `Design/Pesquisa/{caminho}`

   ## Contexto factual
   {resumo com 📌 Fonte em cada afirmação}

   ## Destaques para uso criativo

   ## Sugestões de conexão *(sugestão criativa, não fato)*
   {no brainstorm: criaturas, locais, eventos e tecnologias do período + conexões dieselpunk}

   ## Instrução para o @GameCreative
   {o que fazer com o material}
   ```

2. Linha em `## Handoffs de Pesquisa` do TODO criativo:
   `| {Processar handoff | Brainstorm | Revisar}: {tema} | [{arquivo}]({link relativo}) | Alta | ❌ Não iniciado |`
3. Registrar o mesmo handoff em "Handoffs Pendentes para @GameCreative" de `Design/Pesquisa/TODO.md` e na tabela de handoffs de `Design/Pesquisa/index.md`.
4. Guardrails de `memories/repo/historian-guardrails.md`: a Pesquisa não edita conteúdo criativo — a única escrita permitida em `Design/Criativo/` é esta linha.

## Criativo → Documentação

`| Criar feature: {Nome} | Design/Criativo/{arquivo} | Alta | ❌ Não iniciado |` em `## Handoffs do @GameCreative`.

## Documentação → Implementação

`| {tarefa acionável, com a feature ou mecânica de referência} | @{Agente} | {Prioridade} | ❌ |` na seção da área.

## Regras

- Handoff escreve TODO — **nunca executa o trabalho da camada seguinte** nem invoca o agente.
- Em ambiguidade sobre a rota, perguntar antes de escrever.
