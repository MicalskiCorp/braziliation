---
name: processar-entrevistas
description: Lê as entrevistas e conversas de pesquisa capturadas via WhatsApp (transcritas em Design/Pesquisa/Entrevistas/_pendente-curadoria/), aplica o critério de memória oral do Historiador e decide, item a item, o que vira pesquisa aprovada, pendência de checagem, handoff direto pro criativo ou descarte. Use quando o usuário pedir para "processar entrevistas", "ver as conversas do whats", "curar entrevistas" ou houver itens em _pendente-curadoria/.
---

# Skill: processar-entrevistas

Entrada do pipeline de captura via WhatsApp (ADR-009, `Design/Pesquisa/Entrevistas/index.md`).
Um listener (Baileys) e um transcritor (faster-whisper) locais, fora do Claude Code, rodam na
máquina do usuário e alimentam `Design/Pesquisa/Entrevistas/_pendente-curadoria/` com o que foi
dito numa conversa dedicada — cada item é uma pasta com `meta.json` (remetente, data, tipo) e
`transcricao.txt` (áudio) ou `mensagem.txt` (texto).

> Esta skill só processa o que já chegou transcrito. Não conecta no WhatsApp nem transcreve —
> isso é `Ferramentas/whatsapp-listener/` e `Ferramentas/transcrever.py`, rodando fora desta sessão.

## Roteiro

1. **Listar** `Design/Pesquisa/Entrevistas/_pendente-curadoria/` — uma pasta por captura. Vazia →
   avisar e parar.
2. **Para cada item**, ler `meta.json` + `transcricao.txt`/`mensagem.txt` e apresentar ao usuário:
   remetente, data, resumo do conteúdo.
3. **Classificar como memória oral**, não fonte web — critério de
   `memories/repo/historian-guardrails.md`: causo, mito urbano ou memória oral vale para
   `Design/Pesquisa/` quando há convergência com outras fontes locais/secundárias, **sem exigir
   documento primário**, desde que o texto deixe claro que é relato oral, não fato comprovado.
   - Se o relato citar algo já coberto, `Grep` pelo tema em `Design/Pesquisa/` antes de decidir.
   - Puder cruzar com uma busca web rápida (nome, data, evento) → fazer, como no Modo 1.
   - Nunca gravar como "fato histórico" — sempre "relato de {remetente}, {data}" ou "memória
     oral convergente com {fonte}".
4. **Decidir com o usuário**, item a item — a decisão é dele, não da skill:
   - **Aprovar e salvar** → Modo 2 do Historiador (destino em `Estados/{Estado}/` ou
     `Temas/{tema}.md`), citando a entrevista como fonte no lugar do Protocolo de Fonte padrão:
     `> 🎙️ Relato oral: {remetente}, entrevista de DD/MM/AAAA`.
   - **Precisa mais pesquisa** → linha em `Design/Pesquisa/TODO.md` (skill `gerir-todo`)
     referenciando o item.
   - **Vira brainstorm/handoff direto** → Modo 4 do Historiador (skill `handoff`), se o usuário
     já quiser passar pro criativo sem gravar pesquisa formal antes.
   - **Descartar** → sem uso; segue para o passo 5 sem gravação em `Design/Pesquisa/`.
5. **Mover a pasta** de `_pendente-curadoria/` para `_processado/`, acrescentando ao `meta.json`
   os campos `resultado` (`aprovado` | `pendente-pesquisa` | `handoff` | `descartado`) e, se
   houver, `destino` (arquivo/linha criada).
6. **Resumir ao usuário** ao final do lote: quantos itens, quantos aprovados, pendentes,
   handoffs e descartes.

## Regras

- Seguem as Regras Invioláveis do `@Historiador` (sem alucinação, sem armazenamento sem
  aprovação explícita, fonte obrigatória — aqui a "fonte" é a própria entrevista, citada como tal).
- Nunca decidir por conta própria: mostrar o conteúdo ao usuário antes de aprovar, arquivar
  como pendência ou descartar.
- Áudio e transcrição brutos nunca são commitados — `.gitignore` cobre `_inbox/`,
  `_pendente-curadoria/` e `_processado/`; só o material curado que vai para
  `Design/Pesquisa/Estados/` ou `Temas/` entra no git.
- Entrevista com terceiros (não o próprio usuário): confirmar que há consentimento para
  guardar e usar o relato antes de aprovar.
- Roda na conversa principal, não em fork — a decisão de cada item é interativa com o usuário.
