---
name: processar-entrevistas
description: Lê as entrevistas e conversas de pesquisa capturadas via WhatsApp — áudio transcrito, texto, foto e documento — em Design/Pesquisa/Entrevistas/_pendente-curadoria/, aplica o critério de memória oral do Historiador e decide, item a item, o que vira pesquisa aprovada, pendência de checagem, handoff direto pro criativo ou descarte. Use quando o usuário pedir para "processar entrevistas", "ver as conversas do whats", "curar entrevistas" ou houver itens em _pendente-curadoria/.
---

# Skill: processar-entrevistas

Entrada do pipeline de captura via WhatsApp (ADR-009, `Design/Pesquisa/Entrevistas/index.md`).
Um listener (Baileys) e um transcritor (faster-whisper) locais, fora do Claude Code, rodam na
máquina do usuário e alimentam `Design/Pesquisa/Entrevistas/_pendente-curadoria/` com o que foi
dito e enviado numa conversa dedicada — cada item é uma pasta com `meta.json` (remetente, data,
`tipo`) mais o conteúdo, conforme o `tipo`:

| `tipo` | Arquivos na pasta | Como ler |
|---|---|---|
| `audio` | `transcricao.txt` | ler a transcrição |
| `texto` | `mensagem.txt` | ler o texto |
| `imagem` | `imagem.*`, às vezes `legenda.txt` | **`Read` na imagem** — descrever o que se vê e transcrever o que estiver escrito nela |
| `documento` | `documento.*`, `texto-documento.txt`, às vezes `legenda.txt` | ler `texto-documento.txt`; se ele trouxer `[sem camada de texto extraivel…]`, **`Read` no arquivo** (PDF escaneado, foto de página) |

> Esta skill só processa o que já chegou transcrito. Não conecta no WhatsApp nem transcreve —
> isso é `Ferramentas/whatsapp-listener/` e `Ferramentas/transcrever.py`, rodando fora desta sessão.

## Roteiro

1. **Listar** `Design/Pesquisa/Entrevistas/_pendente-curadoria/` — uma pasta por captura. Vazia →
   avisar e parar.
2. **Áudio é curado por bloco, nunca por resumo.** Rodar
   `py Design/Pesquisa/Entrevistas/Ferramentas/blocos.py` — divide cada transcrição em blocos de
   ~150 palavras (`A1.01`, `A1.02`…, gravados em `blocos.txt` na pasta) e imprime a tabela
   "Trechos". Antes de escrever qualquer linha de pesquisa, montar o **inventário de assuntos** em
   `Design/Pesquisa/Entrevistas/Inventarios/AAAA-MM-DD-{assunto}.md` (modelo:
   `2026-10-11-teatro-carlos-gomes.md`) lendo **todos** os blocos, um a um:
   - um assunto por linha; bloco com dois assuntos gera duas linhas;
   - status `✅` (vai para a pesquisa), `🔎` (vira pendência no TODO) ou `⛔` (fica fora — motivo
     obrigatório na coluna Destino, incluindo "decisão do responsável" quando for o caso);
   - em `✅`/`🔎`, as **chaves** são trechos literais que precisam aparecer no arquivo de destino.

   O inventário é a lista que o usuário valida no passo 4 — não um resumo do áudio. Por que existe:
   em 2026-10-11 a curadoria resumiu ~62 min de áudio e perdeu 12 assuntos sem ninguém notar.
3. **Para cada item**, ler `meta.json` e o conteúdo conforme a tabela acima, e apresentar ao
   usuário: remetente, data, tipo, resumo do conteúdo (em áudio, o inventário). Em imagem e documento, a legenda
   (`legenda.txt`) costuma ser o contexto que o remetente deu — sempre mostrar junto.
4. **Classificar como memória oral**, não fonte web — critério de
   `memories/repo/historian-guardrails.md`: causo, mito urbano ou memória oral vale para
   `Design/Pesquisa/` quando há convergência com outras fontes locais/secundárias, **sem exigir
   documento primário**, desde que o texto deixe claro que é relato oral, não fato comprovado.
   - Se o relato citar algo já coberto, `Grep` pelo tema em `Design/Pesquisa/` antes de decidir.
   - Puder cruzar com uma busca web rápida (nome, data, evento) → fazer, como no Modo 1.
   - Nunca gravar como "fato histórico" — sempre "relato de {remetente}, {data}" ou "memória
     oral convergente com {fonte}".
5. **Decidir com o usuário**, item a item — a decisão é dele, não da skill:
   - **Aprovar e salvar** → Modo 2 do Historiador (destino em `Estados/{Estado}/` ou
     `Temas/{tema}.md`), citando a entrevista como fonte no lugar do Protocolo de Fonte padrão:
     `> 🎙️ Relato oral: {remetente}, entrevista de DD/MM/AAAA`.
     - **Imagem ou documento aprovado**: copiar o arquivo para `Design/Pesquisa/Fontes/Arquivos/`
       na nomenclatura daquele `index.md`, acrescentar a linha em `Fontes/Arquivos/registro.md` e citar a
       fonte como `> 📎 Documento/foto: {nomeOriginal ou descrição}, enviado por {remetente} em
       DD/MM/AAAA — `Fontes/Arquivos/{arquivo}``. Acima de ~5 MB, não copiar: deixar em
       `_processado/` e referenciar o caminho (regra no `index.md` de `Fontes/Arquivos/`).
     - Nunca tratar o que está escrito num documento fotografado como fato verificado só por
       estar num papel — vale o mesmo critério de convergência da memória oral, e a origem do
       papel (quem escreveu, quando) entra no registro.
   - **Precisa mais pesquisa** → linha em `Design/Pesquisa/TODO.md` (skill `gerir-todo`)
     referenciando o item.
   - **Vira brainstorm/handoff direto** → Modo 4 do Historiador (skill `handoff`), se o usuário
     já quiser passar pro criativo sem gravar pesquisa formal antes.
   - **Descartar** → sem uso; segue para o passo 6 sem gravação em `Design/Pesquisa/`.
6. **Mover a pasta** de `_pendente-curadoria/` para `_processado/`, acrescentando ao `meta.json`
   os campos `resultado` (`aprovado` | `pendente-pesquisa` | `handoff` | `descartado`) e, se
   houver, `destino` (arquivo/linha criada).
7. **Fechar a cobertura:** rodar `dotnet test Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj`
   — o `InterviewInventoryTests` falha se algum bloco ficou sem linha no inventário ou se uma chave
   `✅`/`🔎` não aparece no destino (inclusive depois de dividir ou mover um arquivo de pesquisa:
   atualize a tabela Destinos). O pre-commit roda o mesmo teste.
8. **Resumir ao usuário** ao final do lote: quantos itens, quantos aprovados, pendentes,
   handoffs e descartes — e, para áudio, quantos blocos e assuntos o inventário cobriu.

## Regras

- Seguem as Regras Invioláveis do `@Historiador` (sem alucinação, sem armazenamento sem
  aprovação explícita, fonte obrigatória — aqui a "fonte" é a própria entrevista, citada como tal).
- Nunca decidir por conta própria: mostrar o conteúdo ao usuário antes de aprovar, arquivar
  como pendência ou descartar.
- Áudio, imagem, documento e transcrição brutos nunca são commitados — `.gitignore` cobre
  `_inbox/`, `_pendente-curadoria/` e `_processado/`; entra no git só o material curado que vai
  para `Design/Pesquisa/Estados/`, `Temas/` ou `Fontes/Arquivos/`.
- Entrevista com terceiros (não o próprio usuário): confirmar que há consentimento para
  guardar e usar o relato antes de aprovar. Vale igual para foto e documento de terceiro —
  e redobrado quando a imagem mostrar pessoas identificáveis ou papel de acervo particular.
- Roda na conversa principal, não em fork — a decisão de cada item é interativa com o usuário, e copiar imagem/documento aprovado para `Fontes/Arquivos/` precisa de `Bash` (o `Write` não copia binário).
