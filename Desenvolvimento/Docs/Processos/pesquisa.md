# Pesquisa

> Camada 1 · Design · Fonte canônica: [`historiador.md`](../../../.claude/agents/historiador.md) · skills [`handoff`](../../../.claude/skills/handoff/SKILL.md), [`hemeroteca-blumenau`](../../../.claude/skills/hemeroteca-blumenau/SKILL.md), [`gerir-todo`](../../../.claude/skills/gerir-todo/SKILL.md). Este manual resume; em divergência, vale a fonte.

Dono **@Historiador** · Pasta **Design/Pesquisa/** · TODO **Design/Pesquisa/TODO.md** · Sai por **## Handoffs de Pesquisa** no TODO criativo

Confirma que uma lenda, figura ou referência cultural *existe* como elemento reconhecido — não se os eventos aconteceram. Nada é inventado e nada é salvo sem aprovação. A pesquisa é um procedimento só; os gatilhos mudam a profundidade da saída e o destino, por isso são 4 modos, não 7.

## Protocolo de inicialização

- Ler `Design/Pesquisa/index.md` (cobertura) e `Design/Criativo/index.md`.
- Ler `memories/repo/historian-guardrails.md`.
- Buscar o tema com Grep em Pesquisa, Criativo e GDD; abrir só o que aparecer.
- Avisar se o tema já tem cobertura: complementar, substituir ou usar de base?

## Protocolo de fonte

- Toda afirmação armazenada leva `📌 Fonte: [Site](URL) — acesso em DD/MM/AAAA`.
- Conhecimento sem fonte web vem marcado `[CONHECIMENTO INTERNO — NÃO ARMAZENAR SEM VALIDAR]`.
- Fontes em conflito: apresentar as duas e o usuário escolhe.
- Causos e memória oral valem com convergência de várias matérias locais, rotulados como tal.

## Gatilho → modo

- `Pesquisar:` · `Lenda de:` · `História de:` → P1 completa
- `Fontes sobre:` → P1 só fontes
- `Aprovar e salvar:` → P2
- `Listar pesquisas:` · `Compilar estado:` → P3
- `Delegar ao criativo:` · `Brainstorm:` → P4
- `Processar entrevistas` → P7 (skill)

## P1 — Pesquisar tema

**Quem:** @Historiador · Modo 1
**Aciona:** `@Historiador Pesquisar: Curupira — Amazônia` · `@Historiador Fontes sobre: Palmares`

1. Rodar o protocolo de inicialização.
2. Buscar na web a existência da lenda ou referência, em fontes variadas (museus, universidades, portais culturais; Wikipedia só como ponto de partida). Fonte primária de Blumenau → P5.
3. **Só fontes:** listar nome, URL, tipo e confiabilidade — e parar.
4. **Completa:** como a lenda é contada, variações regionais, conexões com outros estados e períodos; à parte, o potencial criativo dieselpunk marcado como sugestão.
5. Listar as fontes consultadas ao final.
6. Parar e aguardar aprovação; nada é armazenado.

- **Lê:** Índices de Pesquisa e Criativo, arquivos que citam o tema
- **Escreve:** Nada — só a resposta
- **Gate:** Fonte web para cada afirmação
- **Unificou:** Antigos "Pesquisar tema" e "Buscar fontes"

## P2 — Aprovar e armazenar

**Quem:** @Historiador · Modo 2
**Aciona:** `@Historiador Aprovar e salvar: Curupira`

1. Confirmar o escopo aprovado: tudo ou só partes.
2. Identificar o destino (`Estados/{Estado}/…`, cidade ou `Temas/{tema}.md`) e criar o arquivo se não existir.
3. Gravar como "referência folclórica confirmada", com fonte por elemento e nota criativa se houver.
4. Registrar as fontes em `Fontes/index.md` e atualizar a cobertura em `Pesquisa/index.md`.
5. Grep pelo tema no Criativo: se enriquece ou contradiz lore, P4 tipo **revisão**.
6. Confirmar ao usuário o que foi salvo e onde.

- **Escreve:** `Design/Pesquisa/…`, `Fontes/index.md`
- **Gate:** Aprovação explícita do usuário na conversa

## P3 — Consultar acervo

**Quem:** @Historiador · Modo 3
**Aciona:** `@Historiador Listar pesquisas: todas` · `@Historiador Compilar estado: Bahia`

1. **Listagem:** ler `Pesquisa/index.md` (e o estado, se pedido); tabela com tema, estado ou cidade, arquivo e status; destacar lacunas.
2. **Compilação:** ler os arquivos aprovados de `Estados/{Estado}/`; montar resumo histórico, lendas, cidades e destaques, conexões temáticas.
3. Apresentar para revisão; na compilação, oferecer P4 tipo **brainstorm**.

- **Escreve:** Nada
- **Unificou:** Antigos "Listar pesquisas" e "Compilar estado" — mesma leitura, duas profundidades

## P4 — Handoff para o Criativo

**Quem:** @Historiador · Modo 4 · skill `handoff`
**Aciona:** `@Historiador Delegar ao criativo: Curupira` · `@Historiador Brainstorm: borracha — Amazônia`

1. Escolher o tipo: **processar** (pesquisa pronta para uso), **brainstorm** (base factual + conexões dieselpunk para uma sessão) ou **revisão** (vem do P2).
2. Sem pesquisa aprovada sobre o tema, rodar P1 e esperar aprovação.
3. Processar e brainstorm: briefing `Design/Pesquisa/Handoffs/AAAA-MM-DD-{tema}.md` no formato da skill (contexto factual com fontes, destaques, sugestões marcadas, instrução).
4. Linha em `## Handoffs de Pesquisa` do TODO criativo (a seção já existe).
5. Registrar também em "Handoffs Pendentes" do TODO de Pesquisa e no `Pesquisa/index.md`.
6. Avisar o usuário para acionar o @GameCreative.

- **Gate:** Só pesquisa aprovada, com fontes, sai da camada
- **Unificou:** Antigos "Brainstorm de pesquisa", "Handoff" e o handoff de dentro do "Armazenar" — o briefing agora vive só na skill
- **Próximo:** C3 ou C8 no Criativo

## P5 — Verificar em fonte primária (Blumenau)

**Quem:** @Historiador · skill `hemeroteca-blumenau` (fork do Historiador)
**Aciona:** Dentro do P1, quando o tema exige data, nome ou evento específico de Blumenau

1. Abrir o índice da década certa da revista "Blumenau em Cadernos" na Hemeroteca Digital de SC.
2. Localizar a edição pela data ou número.
3. Baixar o PDF OCR e procurar o termo.
4. Citar edição, página e URL.

- **Gate:** Links vêm dos índices por década — nunca adivinhar URL de PDF
- **Por que é skill em fork:** Procedimento especializado e longo que lê PDFs de 25-30 páginas: roda isolado e devolve só edição, trecho e fonte. De dentro do Historiador, ele segue o roteiro do SKILL.md direto (subagente não abre outro)

## P6 — TODO de Pesquisa

**Quem:** @Historiador · skill `gerir-todo`

1. Ler `Design/Pesquisa/TODO.md` no início da sessão.
2. Estados e temas a pesquisar em tabelas com prioridade e status; handoffs gerados em "Handoffs Pendentes".
3. Item concluído vai para "Concluído" com a data.

- **Estado hoje:** 6 estados e 3 temas não iniciados; só Blumenau pesquisada

## P7 — Processar entrevistas (WhatsApp)

**Quem:** @Historiador · skill `processar-entrevistas` · ADR-009
**Aciona:** "processar entrevistas" · "curar entrevistas" — quando há itens em `Design/Pesquisa/Entrevistas/_pendente-curadoria/`

1. Fora do Claude Code: o listener local (Node + Baileys, no PC de casa) grava cada áudio, texto, foto ou documento da conversa dedicada em `Entrevistas/_inbox/`.
2. `py Design/Pesquisa/Entrevistas/Ferramentas/transcrever.py` transcreve o áudio com faster-whisper local, extrai o texto de PDF/DOCX, e move o lote para `_pendente-curadoria/`. Sem API em nenhuma etapa.
3. A skill lista os itens e apresenta cada um: remetente, data, tipo e resumo — imagem e PDF escaneado são lidos direto pelo Claude Code, que não tem OCR automático no pipeline.
4. Classifica como memória oral (critério do guardrail do Historiador) e cruza com a pesquisa existente — e com busca web quando der.
5. Decide com o usuário, item a item: aprovar e salvar (P2, citando o relato oral), pendência no TODO de Pesquisa, handoff direto (P4) ou descarte. Imagem/documento aprovado é copiado para `Design/Pesquisa/Fontes/Arquivos/` e registrado no índice de lá — é a única cópia versionada.
6. Move a pasta para `_processado/` com o resultado no `meta.json` e resume o lote.

- **Gate:** Decisão sempre do usuário · consentimento de terceiros antes de aprovar · áudio, imagem, documento e transcrição brutos nunca entram no git
- **Estado:** Validado de ponta a ponta em 2026-09-14 (áudio e texto) e em 2026-09-20 (imagem e documento) — grupo privado dedicado; listener sempre ligado pelo Agendador do Windows (`iniciar-listener.cmd`, log em `listener.log`); transcrever e curar sob demanda
- **Risco:** Baileys é não-oficial — risco baixo, mas não nulo, de bloqueio da conta; preferir número secundário

---

[← Manual de processos](index.md)
