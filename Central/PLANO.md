# Central do Braziliation — desenho e plano

> Painel local com as **N filas de trabalho** do projeto, cada uma gerida separadamente: escolher a fila, selecionar itens, executá-los com o agente dono, conversar quando ele precisar de uma decisão, validar o que saiu e só então commitar. **Estado: implementado de ponta a ponta em 2026-11-03** (fases 0 a 5; a 6 fica para depois, por decisão). Uso no dia a dia: [`README.md`](README.md). Daqui em diante, só ajustes pontuais — sem TODO próprio da Central.

## 1. Decisões do responsável (2026-11-03)

| Tema | Decisão |
|---|---|
| Forma | Um painel de **várias filas**, não um backlog único. Cada fila é a que já existe hoje, na mesma estrutura |
| Ciclo | Fila → selecionar N itens → executar → chat quando precisar de input → validar a saída → commitar |
| Lugar | Camada externa a todas as outras, numa pasta própria na raiz: `Central/` |
| Status | Uma fonte só (os arquivos de fila em Markdown) e um parser só |
| Processo | Hooks, agentes, skills, regras e o modelo reativo continuam como estão |
| Rede | **Só local** (self-hosted nesta máquina). Acesso remoto fica para depois (Fase 6) |
| Commit | Local, pela Central, só depois de o responsável validar a saída e confirmar; passa pelo pre-commit |
| Push | **Nunca pela Central** — sempre manual, pelo VS Code, para revisar os commits que sobem |
| Paralelismo | Filas diferentes rodam em paralelo; quando podem conflitar, a Central avisa ou impede |
| Disponibilidade | PC sempre ligado em casa |

## 2. As filas

Uma fila por seção dos TODOs de camada, mais as duas filas que vivem fora deles. Nada muda de lugar: a Central lê e escreve nos mesmos arquivos.

| Camada | Fila | Fonte | Executa com |
|---|---|---|---|
| Pesquisa | Estados a pesquisar | `Design/Pesquisa/TODO.md` § Estados a Pesquisar | `@Historiador` |
| | Temas transversais | § Temas Transversais a Pesquisar | `@Historiador` |
| | Checagem | § Pendências de Checagem | `@Historiador` (+ `hemeroteca-blumenau`) |
| | Entrevistas para curar | `Entrevistas/_pendente-curadoria/` e `_lotes/` | `@Historiador` + `processar-entrevistas` |
| | Handoffs enviados | § Handoffs Pendentes para @GameCreative | Só acompanhamento: espelho da entrada do Criativo |
| Criativo | História | `Design/Criativo/TODO.md` § História | `@GameCreative` |
| | Lendas | § Lendas | `@GameCreative` |
| | Cidades | § Cidades — Santa Catarina | `@GameCreative` (+ `nova-cidade`) |
| | Estados planejados | § Estados Planejados | `@GameCreative` (+ `nova-cidade`) |
| | Crafting & Build | § Crafting & Build — Conteúdo Criativo | `@GameCreative` |
| | Ideias | § Ideias | `@GameCreative` |
| | Entrada da Pesquisa | § Handoffs de Pesquisa | `@GameCreative` (+ `handoff`) |
| Arte | Concept art | Criativo § Concept Art Pendente | `@SpriteArtist` + `concept-art` |
| Desenvolvimento | Entrada do Criativo | `Desenvolvimento/Docs/TODO.md` § Handoffs do @GameCreative | `@GameArchitect` |
| | Decisões de design | § Decisões de design | `@GameCreative` + `fechar-decisao` (`@TechLead` nos números) |
| | Unity | § Unity — validação no Editor e wiring | Coluna Responsável do item |
| | Gameplay | § Gameplay | Coluna Responsável do item |
| | UI e arte | § UI e arte | Coluna Responsável do item |
| | Ecossistema | § Ecossistema e processo | Coluna Responsável do item |
| | Dívida técnica | `Tech/tech_debt.md` (Alta, Média, Baixa) | `@TechLead` decide o agente |

O mapa fila → fonte → agente fica em `Central/filas.json`. Um teste da Central falha se uma seção de TODO não tiver fila no registro, ou se o registro apontar para uma seção que não existe mais. Item com "Usuário" no Responsável vira conversa com o agente que o acompanha (ou com o `@TechLead`) para ajudar a decidir.

## 3. O ciclo de uma execução

1. **Selecionar.** Na fila, marcar N itens. Itens com responsáveis diferentes viram uma execução por responsável, em sequência.
2. **Executar.** A Central abre uma sessão do agente dono com o comando da camada (ex.: `@GameCreative TODOs: executar: {itens}`) e um contrato anexado: seguir o Passo 0 e o Passo Final do agente, perguntar e parar quando precisar de decisão, **não commitar**, e terminar com um bloco de resultado por item (feito, precisa de decisão ou bloqueado, com resumo e arquivos).
3. **Conversar.** O chat mostra o agente trabalhando ao vivo. Quando ele pergunta, a execução passa a "aguardando você", a fila ganha um aviso e o chat abre. Pedido de permissão aparece como cartão de aprovar ou negar. Imagens citadas pelo agente (thumbnails de concept art, folhas de entrevista) aparecem no próprio chat.
   As edições à mão no painel (status, prioridade, baixa, item novo) seguem o mesmo caminho: vão para um worktree próprio da fila e entram direto no passo 4.
4. **Validar.** A execução termina em "aguardando validação": o resumo de cada item, o diff por arquivo, as mudanças de TODO em destaque (baixa, status, handoff escrito na camada seguinte) e as checagens que se aplicam (`dotnet test`, `todo.py validar`, meta e paletas quando houver arte, `unity-validar` quando houver `.cs` em `Assets/`).
5. **Decidir.** Três saídas: **pedir ajuste** (volta ao chat, na mesma sessão, com o seu comentário), **descartar** (os arquivos voltam ao estado de antes da execução) ou **aprovar e commitar** (mensagem proposta pelo agente, editável, confirmação; a saída do pre-commit aparece na tela, e se ele recusar a execução volta ao chat para corrigir).

Estados de uma execução: na fila → rodando → aguardando você → aguardando validação → commitada ou descartada. Esse é estado da Central, guardado em `Central/.estado/`; o status do trabalho continua só no TODO.

## 4. Invariantes

1. **Dependência de fora para dentro.** A Central importa as ferramentas do projeto; nada do projeto importa a Central. Desligada, tudo funciona pelo VS Code como hoje.
2. **Sem banco.** Status nos TODOs, decisões em DDR/ADR, histórico no git. Só o que é da Central (execuções, conversas, log) fica em `Central/.estado/`, fora do git.
3. **Toda escrita pelo parser único**, o mesmo do hook de sessão, das skills e do pre-commit. Antes de gravar, confere o hash do arquivo lido; se mudou, recusa e recarrega.
4. **Modelo reativo.** Toda execução nasce de uma seleção do responsável. Handoff que chega não dispara a camada seguinte.
5. **Agente não commita nem dá push.** Além do contrato, a sessão sobe com `git commit` e `git push` em `--disallowedTools`. Commit é sempre da validação.
6. **Paralelismo com isolamento.** Fila de Markdown roda num worktree próprio (`.git/central/wt/`) e pode correr ao lado de qualquer outra; fila que depende de arquivo fora do git, do Unity ou da GPU roda na árvore principal, uma por vez, e só começa com a árvore limpa — é o que permite descartar com segurança. O mesmo item em duas execuções é **bloqueado**; duas execuções no mesmo TODO geram **aviso**; se as mudanças não se juntarem no rebase, o agente da execução junta as duas versões (rebase parado, marcadores conferidos) e o responsável aprova a versão combinada antes da integração. No máximo 3 agentes vivos; o excedente espera.
7. **Travas intactas.** Nunca `--no-verify`, nunca `claude --bare` (pula hooks e `CLAUDE.md`), nunca `bypassPermissions`.
8. **Local de verdade.** Escuta só em `127.0.0.1`. Toda ação é `POST` com token CSRF, e o servidor recusa `Host`/`Origin` que não sejam o da Central — sem isso, qualquer site aberto no navegador poderia acionar a máquina.

## 5. Stack

| Parte | Escolha | Por quê |
|---|---|---|
| Linguagem | Python 3.13 (`py`) | As ferramentas do projeto são Python; a Central importa e chama o que existe |
| Servidor | FastAPI + Uvicorn | Leve, com streaming nativo para o chat |
| Interface | Jinja2 + JavaScript próprio em `static/` (sem biblioteca) | Sem npm, sem build, sem CDN; a CSP proíbe script inline |
| Ao vivo | `watchfiles` + Server-Sent Events, só nas pastas de trabalho (nunca `Library/`) | TODO editado no VS Code atualiza o painel sozinho |
| Agente | `claude.exe` sem interface: `-p --agent {nome} --input-format stream-json --output-format stream-json --permission-prompt-tool stdio --permission-mode auto --append-system-prompt-file {contrato} --disallowedTools …` | Mesmo `CLAUDE.md`, hooks, agentes e skills do VS Code, mesma licença, sem chamada de API à parte (ADR-009) |
| Ambiente | venv em `Central/.venv` (fora do git), `requirements.txt` fixado | Não mexe no Python global das skills |
| Testes | `unittest` (biblioteca padrão) em `Central/tests/` e ao lado do parser | Entram no pre-commit e no CI; o agente é trocado por um falso |
| Sempre ligada | Tarefa "Braziliation - Central" no Agendador (`registrar-tarefa.ps1`): `conhost --headless` sem janela, reinício automático, log rotativo em `.estado/` | Mesmo papel do listener (ADR-009), sem janela aberta |

## 6. Fases

Toda fase termina com `dotnet test` e `pytest` verdes e com o commit validado pelo responsável.

### Fase 0 — Fundação no projeto (sem Central ainda)

1. **ADR-012** (skill `novo-adr`, `@TechLead`) com as seções 1, 3 e 4.
2. **Vocabulário de status** em `.claude/rules/todos.md`: ❌ 📋 🔨 ⏸ ✅, mais 🟡 e 🎙️ da Pesquisa, dizendo quais contam como abertos.
3. **Esquema de tabela**: os cabeçalhos aceitos em cada seção e o campo canônico de cada um (título, referência, responsável, prioridade, status, data).
4. **Parser único**: `gerir-todo/todo.py` vira biblioteca + CLI, com leitura por seção, identidade de item (arquivo + seção + título), escrita (adicionar, status, concluir com a regra de baixa da camada, handoff) e o comando `validar`. O `session_snapshot.py` passa a importá-la.
5. **Corrigir o diagnóstico de 2026-11-03**: tabela das Lendas quebrada por uma citação; 4 linhas 🟡/🎙️ invisíveis ao `listar`; handoff "11 lendas — rodada 2" em ❌ na Pesquisa mas processado no Criativo; 3 linhas ✅ que deveriam ter saído do TODO de Desenvolvimento; roadmap e descrições do `@UnityDeveloper` e do `@SpriteArtist` ainda em 640×360 (ADR-011).
6. **Trava**: `todo.py validar` e o `pytest` do parser no pre-commit e no CI.

Pronto quando: hook de sessão e `todo.py` dão os mesmos números, e `validar` passa nos três TODOs.

### Fase 1 — Painel das filas (só leitura)

Esqueleto seguro (invariante 8), tarefa no Agendador, `README.md` da Central. Tela inicial com as 20 filas agrupadas por camada — em cada uma: abertos, Alta, bloqueados e o que espera o responsável. Tela da fila: os itens com filtro por status, prioridade e responsável, caixas de seleção (ainda sem ação) e o documento referenciado do item renderizado ao lado. Entre "Handoffs enviados" e "Entrada da Pesquisa", o painel marca dessincronia. `filas.json` e o teste de registro.

Pronto quando: as 20 filas aparecem com os mesmos números do parser, e os testes provam que requisição com Host estranho ou sem token é recusada.

### Fase 2 — Spike do agente

Confirmar na versão instalada (2.1.316): o protocolo `stream-json` de entrada e saída, como chegam pergunta e pedido de permissão com `--permission-prompts host`, retomar a mesma sessão para "pedir ajuste", e cancelar. Gravar uma conversa real como fixture do teste de contrato.

### Fase 3 — Executar com chat

Passos 1 a 3 do ciclo: seleção → execução → chat ao vivo, com aviso de "aguardando você", cartões de permissão e imagens. Fila de execução serial e histórico das conversas em `Central/.estado/`.

Pronto quando: um item de cada camada roda pelo painel, com ao menos uma pergunta respondida no chat.

### Fase 4 — Validar e commitar

Passos 4 e 5 do ciclo: tela de validação, checagens, pedir ajuste, descartar, aprovar e commitar pelo pre-commit.

Pronto quando: uma execução vai da seleção ao commit sem abrir o VS Code, e um descarte devolve a árvore exatamente ao estado anterior.

### Fase 5 — Ações de fila e ações globais

Na fila: adicionar item, mudar prioridade e status à mão (pelo parser, passando pela mesma validação) e varredura que propõe itens novos. Globais: conversa livre com qualquer agente (direção técnica, ADR), auditorias (`validar-todos`, `structure-audit`), análise de tokens, gates sob demanda, leitor de qualquer `.md`.

### Fase 6 — Acesso remoto (depois)

Tailscale, plano gratuito: `tailscale serve` publica só para os aparelhos do responsável; a Central continua em `127.0.0.1` e nenhuma porta abre no roteador. Atualizar o ADR-012 antes.

## 7. Onde cada um dos 45 processos entra

Códigos do [manual de processos](../Desenvolvimento/Docs/Processos/index.md).

| Como entra na Central | Processos |
|---|---|
| Item de fila, executado numa execução | P1, P5, P7, C1–C6, C9, A1–A6, D1, D2, I2–I5, O4 |
| Decidido no chat durante a execução | P2, D5 |
| Saída da execução, conferida na validação | P4, C10, D6, A7 |
| Ação de fila | P6, C7, C8, D7 |
| Ação global | P3, D3, D4, I1, O2, O3 |
| Etapa da validação | I6, I7, I8, I9, O5 |
| O próprio painel | O1 |

Ficam com o responsável, fora de qualquer tela: o play-teste no Editor e o pixel pass manual no Aseprite. Os itens existem nas filas; a execução é com as mãos no Editor.

## 8. Riscos

| Risco | Defesa |
|---|---|
| Site malicioso no navegador acionando a Central | Invariante 8, coberto por teste |
| Edição no VS Code durante uma execução cai no mesmo diff | A validação mostra tudo; não editar o repositório à mão com execução ativa |
| Execução cria arquivo fora do git (saída do ComfyUI, `_lotes/`) que o descarte não desfaz | A validação lista esses arquivos à parte |
| Formato do `stream-json` mudar numa atualização | Fase 2 e teste de contrato |
| Este plano passar do teto de tokens | `TokenBudgetTests` (5 000 por documento) |

Decidido em 2026-11-03: sem TODO da Central (o plano foi executado inteiro); paralelismo entre filas com aviso ou bloqueio de conflito; push só manual. A skill `gerir-todo` segue como estava — os agentes editam os TODOs à mão, com o `todo.py validar` no pre-commit como rede.

O que o spike da Fase 2 confirmou (2026-11-03): a conversa de vários turnos funciona no mesmo processo; a permissão só chega ao host com `--permission-prompt-tool stdio`; `--disallowedTools` nega sem perguntar; não existe `AskUserQuestion` sem interface; a saída é UTF-8.
