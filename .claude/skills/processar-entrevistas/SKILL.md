---
name: processar-entrevistas
description: Lê as entrevistas e conversas de pesquisa capturadas via WhatsApp — áudio transcrito, texto, foto, vídeo e documento — em Design/Pesquisa/Entrevistas/_pendente-curadoria/ e as leva até a pesquisa por um fluxo fixo de lote — linha do tempo, revisão da transcrição, inventário de assuntos, de-para áudio ↔ lugar ↔ fotos, decisões com o usuário, gravação e fechamento com teste. Use quando o usuário pedir para "processar entrevistas", "ver as conversas do whats", "curar entrevistas" ou houver itens em _pendente-curadoria/.
---

# Skill: processar-entrevistas

Entrada do pipeline de captura via WhatsApp (ADR-009, `Design/Pesquisa/Entrevistas/index.md`).
Listener (Baileys) e transcritor (faster-whisper) rodam na máquina do usuário, fora desta sessão,
e alimentam `Design/Pesquisa/Entrevistas/_pendente-curadoria/` — uma pasta por mensagem, com
`meta.json` (remetente, data, `tipo`, `nomeOriginal`) mais o conteúdo:

| `tipo` | Arquivos na pasta | Como ler |
|---|---|---|
| `audio` | `audio.*`, `transcricao.txt` | blocos do inventário (fase 4) — nunca um resumo |
| `texto` | `mensagem.txt` | ler o texto — costuma ser o contexto do lote ou uma decisão |
| `imagem` | `imagem.*` (+ `legenda.txt`) | pelas folhas de miniaturas da fase 2; `Read` na imagem para detalhe |
| `documento` | `documento.*`, `texto-documento.txt` (+ `legenda.txt`) | foto/vídeo mandado como documento → folhas; PDF/DOCX → `texto-documento.txt`, e `Read` no arquivo quando não houver texto |

O protocolo de envio (fotos como documento, um áudio por lugar…) está em
`Design/Pesquisa/Entrevistas/como-enviar.md`. Quando o material chegar fora dele, dizer ao
usuário o que se perdeu (ex.: foto sem horário) e como mandar da próxima vez.

## Por que o fluxo é este

Na visita ao Teatro Carlos Gomes (2026-10-11), o mapeamento foi feito aos poucos e a curadoria
resumiu ~62 min de áudio direto em pesquisa — 12 assuntos se perderam sem ninguém notar. Cada fase
abaixo fecha um desses furos. **O lote inteiro passa pelas fases na ordem**; o usuário valida no
fim das fases 3, 4, 5 e 6.

**Assunto × sessão.** Assunto é permanente e acumula (a benzedeira, o Teatro Carlos Gomes, Edith
Gaertner) e tem página em `Design/Pesquisa/Entrevistas/Assuntos/`; sessão é uma coleta de um
assunto numa data. **Um lote de curadoria é sempre uma sessão de um assunto só**:
`{lote}` = `{AAAA-MM-DD}-{slug}`. O material chega picado e intercalado, e o usuário **não** precisa marcar
o assunto ao mandar: ele é detectado na fase 1 e confirmado pelo usuário (o `#assunto` do WhatsApp
é só atalho opcional, gravado no `meta.json` pelo listener). A separação é cobrada pela ferramenta
e pelo teste. Nunca juntar capturas de assuntos diferentes, nem do mesmo assunto em datas diferentes,
no mesmo lote.

Ferramentas em `Design/Pesquisa/Entrevistas/Ferramentas/` (rodar de dentro dela, com `py`).
Material de trabalho do lote fica em `Entrevistas/_lotes/{lote}/` (fora do git).

## Fases

1. **Separar por assunto.** Listar `_pendente-curadoria/` (vazia → avisar e parar).
   `py curadoria.py triagem` agrupa por horário o que chegou sem `#assunto` e **sugere o assunto
   de cada grupo** pelo conteúdo (transcrição, textos, legendas × `Palavras-chave:` das páginas
   em `Assuntos/`), com os sinais que achou. Conferir cada sugestão lendo o início das
   transcrições e as folhas; onde não houver sugestão (assunto novo), propor pelo conteúdo. Grupo
   marcado ⚠️ misto: separar as capturas por assunto. Apresentar **todas as sugestões numa
   pergunta só**; confirmadas, `py curadoria.py atribuir --grupo N` (aceita a sugestão),
   `--grupo N --assunto {slug}` (corrige) ou `--pastas a,b --assunto {slug}` (grupo misto).
   Foto sem texto segue o grupo pelo horário — conferir nas folhas se é mesmo daquele assunto. Assunto que já existe em `Assuntos/`
   reusa o mesmo slug (é o que junta as sessões); assunto novo ganha página no modelo de
   `Assuntos/teatro-carlos-gomes.md`, **com palavras-chave** (o teste cobra). A cada sessão,
   acrescentar à página os termos novos que apareceram — é o que melhora a próxima detecção. Se houver vários assuntos ou datas pendentes, curar **uma
   sessão por vez**, cada uma pelas fases 2–9. Ler as mensagens de texto da sessão (o que é, onde,
   quem fala) e confirmar o **consentimento** de terceiros (sem ele: relato anônimo ou fora).
2. **Linha do tempo** — `py curadoria.py linha --assunto {slug} [--data AAAA-MM-DD]` (recusa
   assunto com mais de uma data pendente sem `--data`). Ordena os áudios pelo horário
   gravado no arquivo, calcula palavras por minuto (abaixo de 110 = possível trecho perdido),
   numera as mídias (`#` foto com horário, `F` sem horário, `V` vídeo), marca duplicatas, sugere o
   trecho de cada mídia pelo horário (entre dois áudios → o lugar seguinte) e grava em
   `_lotes/{lote}/`: `mapa.json`, `folhas/` e `revisao.md`. **Ler todas as folhas.**
3. **Revisar a transcrição** — em `revisao.md`, listar por trecho os prováveis erros (nomes
   deturpados, palavras truncadas). Resolver o que der por busca web antes de perguntar (fonte
   confirmada → ✅ com link); apresentar o resto ao usuário trecho a trecho, em lotes de até 4
   perguntas, sempre com uma proposta. Registrar cada decisão na tabela "Resultado da revisão".
4. **Inventário de assuntos** — `py blocos.py --lote {lote}` divide cada
   transcrição em blocos de ~150 palavras. Ler **todos** os blocos e montar
   `Design/Pesquisa/Entrevistas/Inventarios/{lote}.md` (modelo: `2026-10-11-teatro-carlos-gomes.md`,
   com a linha `> Assunto: [slug](../Assuntos/slug.md) · Sessão: DD/MM/AAAA`):
   um assunto por linha; status `✅` pesquisa, `🔎` pendência no TODO, `⛔` fora com motivo
   obrigatório; em `✅`/`🔎`, chaves literais que vão aparecer no destino. O usuário valida o
   inventário — não um resumo.
5. **De-para áudio ↔ lugar ↔ mídias** — editar `mapa.json`: nome e explicação de cada lugar
   (a partir do inventário), notas, o trecho final de cada mídia (a sugestão por horário acerta
   ~2/3; foto sem horário e foto tirada num lugar mas mostrando outro se decidem pelo que mostram),
   `destaque` em mídia com decisão do usuário (ex.: "🚪 entrada do túnel"). **Material sem
   narração** (fachada, praça, exterior) vai numa seção extra própria (ex.: `EXT`), nunca
   empurrado para o trecho mais próximo. Rodar `py curadoria.py gerar --lote {lote}` — recusa se
   alguma mídia ficou sem lugar — e mostrar o `de-para.md` ao usuário.
6. **Decidir com o usuário** (perguntas agrupadas, com recomendação):
   - **Consentimento e identificação** de quem fala (anônimo é o padrão).
   - **Imagens para o git:** 1–2 por lugar, reduzidas a 1600 px, sem rosto identificável,
     copiadas para `Design/Pesquisa/Fontes/Arquivos/` (`{estado}-{assunto}-{lugar}-{AAAA-MM-DD}.jpg`)
     com linha em `Fontes/Arquivos/registro.md`; o resto fica em `_processado/`.
   - **Handoff** para o Criativo e **descartes** (duplicatas, testes).
   - Decisão criativa do usuário sobre o material (ex.: "esta abertura vai ser o túnel") vai para
     o **handoff**, nunca para a pesquisa — na pesquisa entra só o que se vê.
7. **Gravar.** Assunto que volta é **acrescentado** ao arquivo de pesquisa que já existe (com a
   data da sessão), nunca num arquivo paralelo; a página do assunto ganha a linha da sessão.
   Pesquisa organizada **por lugar**, em arquivo próprio quando o da cidade passar de
   ~5 mil tokens (`TokenBudgetTests`), com `> 🎙️ Relato oral: {quem}, entrevista de DD/MM/AAAA`,
   `✅` no que converge com fonte e `🎙️` no que é só relato; fontes novas em
   `Fontes/registro.md`; pendências em `Design/Pesquisa/TODO.md` (skill `gerir-todo`); handoff
   pela skill `handoff`. Nunca gravar relato como "fato histórico".
8. **Arquivar.** Mover as pastas para `_processado/` com `resultado` (`aprovado` |
   `pendente-pesquisa` | `handoff` | `descartado`) e `destino` no `meta.json`; rodar `gerar` de
   novo para o `de-para.md` apontar para `_processado/` (ele grava `trecho`, `lugar` e
   `observacao` em cada captura).
9. **Fechar.** `dotnet test Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj`
   — o `InterviewInventoryTests` falha se um bloco ficou sem linha, se uma chave não está no
   destino, se o inventário não aponta para um assunto que o lista de volta, ou se uma captura
   aparece em dois inventários (depois de dividir ou mover um arquivo de pesquisa, atualizar a tabela Destinos do
   inventário). Resumir ao usuário: itens, blocos e assuntos cobertos, aprovados, pendências,
   handoffs e descartes, e onde estão `revisao.md` e `de-para.md`.

## Regras

- Seguem as Regras Invioláveis do `@Historiador` (sem alucinação, sem armazenamento sem
  aprovação explícita, fonte obrigatória — aqui a "fonte" é a própria entrevista, citada como tal).
- Nunca decidir por conta própria: o usuário vê o conteúdo antes de aprovar, arquivar como
  pendência ou descartar. Memória oral vale com convergência de fonte local/secundária, sem exigir
  documento primário (`memories/repo/historian-guardrails.md`); `Grep` em `Design/Pesquisa/` antes
  de decidir sobre tema já coberto.
- Nunca tratar o que está escrito num documento fotografado como fato só por estar no papel.
- Áudio, imagem, vídeo, documento, transcrição, `revisao.md` e `de-para.md` nunca entram no git
  (`.gitignore` cobre `_inbox/`, `_pendente-curadoria/`, `_processado/` e `_lotes/`); entram só a
  pesquisa, o inventário e as imagens aprovadas em `Fontes/Arquivos/`.
- Foto ou documento de terceiro: consentimento redobrado quando mostra pessoa identificável ou
  papel de acervo particular.
- Roda na conversa principal, não em fork — as decisões são interativas, e copiar imagem aprovada
  precisa de `Bash` (o `Write` não copia binário).
