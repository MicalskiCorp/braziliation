# Central do Braziliation

Painel local das **filas de trabalho** do projeto ([ADR-012](../Desenvolvimento/Docs/Architecture/architecture_decisions.md#adr-012-central--painel-local-das-filas-de-trabalho-com-parser-único-dos-todos)). Cada seção dos TODOs de camada é uma fila — mais a dívida técnica e as entrevistas para curar. Escolhe a fila, seleciona os itens, executa com o agente dono, conversa quando ele pedir decisão, valida o que saiu e só então commita. Desenho completo e decisões: [`PLANO.md`](PLANO.md).

**Endereço:** <http://127.0.0.1:8765> — só nesta máquina. Nada fica exposto na rede.

## Subir

| Como | Comando |
|---|---|
| Sempre ligada (recomendado) | `powershell -ExecutionPolicy Bypass -File Central\registrar-tarefa.ps1` — uma vez; a tarefa "Braziliation - Central" sobe no logon, sem console, e volta sozinha se cair |
| À mão, com console | `Central\iniciar-central.cmd` (na primeira vez cria o `.venv`) |
| Parar · reiniciar | `powershell -ExecutionPolicy Bypass -File Central\parar-central.ps1` · com `-Reiniciar` — recusa se houver agente rodando (`-Forcar` interrompe). Só `Stop-ScheduledTask` deixa o servidor órfão segurando a porta |
| Tirar a tarefa | `Unregister-ScheduledTask -TaskName "Braziliation - Central" -Confirm:$false` |

Log: `Central/.estado/central.log`. Tudo o que é da Central (execuções, conversas, log) fica em `Central/.estado/`, fora do git.

## O ciclo

1. **Fila** — o painel mostra as filas por camada, com abertos, Alta e ⏸, e o que espera por você.
2. **Selecionar** — marque os itens. Itens com responsáveis diferentes (filas de Desenvolvimento) viram uma execução por agente.
3. **Executar** — a Central abre o agente dono pelo `claude -p`: o mesmo `CLAUDE.md`, os mesmos hooks, agentes e skills de uma sessão no VS Code, e a mesma licença.
4. **Conversar** — o chat mostra o agente ao vivo. Pergunta dele deixa a execução em *aguardando você*; a sessão roda em modo de permissão `auto`, então o rotineiro passa sem perguntar, e só o que o classificador barra vira um cartão com Permitir, Permitir sempre nesta execução e Negar. Imagem citada pelo caminho aparece no chat.
5. **Validar** — o resumo de cada item, o diff por arquivo e as checagens (`todo.py validar`, `dotnet test` e, conforme o que mudou, meta-check, paletas, testes do parser; `unity-validar` por botão).
6. **Decidir** — pedir ajuste (volta ao chat), descartar (os arquivos voltam ao que eram) ou commitar.

**O commit é local e passa pelo pre-commit do projeto.** O agente não commita nem dá push — a sessão sobe com `git commit`, `git push`, rebase, merge, reset, stash e worktree bloqueados. **Push é sempre manual, pelo VS Code.**

Editar status, prioridade, dar baixa ou adicionar item pelo painel também passa pela validação: a edição vai para um worktree próprio da fila e espera o commit como qualquer execução.

## Paralelismo e conflitos

| Fila | Onde roda | Em paralelo? |
|---|---|---|
| Markdown (Pesquisa, Criativo, Decisões, Entrada, Ecossistema) | worktree próprio em `.git/central/wt/` | Sim, com qualquer outra |
| Entrevistas, Concept art, Unity, Gameplay, UI e arte, Dívida | árvore principal | Uma por vez — as outras esperam na fila |

- **O mesmo item em duas execuções é bloqueado.**
- Duas execuções no mesmo TODO geram **aviso**: seções diferentes se juntam sozinhas no commit (rebase); se mexerem nas mesmas linhas, a segunda fica em *conflito na integração*.
- **Conflito é resolvido pelo Claude.** A Central deixa o rebase parado no worktree e pede ao agente da própria execução — na mesma sessão, com o contexto do que ele fez — que junte as duas versões (num TODO: as linhas das duas execuções, sem duplicar item). Se as mudanças forem incompatíveis, ele pergunta no chat. A Central confere que não sobrou marcador (`<<<<<<<`/`>>>>>>>`; se sobrar, devolve ao agente uma vez), conclui o rebase e traz a **versão combinada** para a validação: nada entra no branch principal antes do seu **Aprovar e integrar**. Na tela de conflito há também «Resolver com o Claude» com uma orientação sua, «Integrar de novo» para quem resolveu à mão no worktree, e Descartar.
- Execução na árvore principal **só começa com a árvore limpa** — é o que torna o descarte seguro. Commite (ou descarte) o que estiver pendente antes.
- No máximo 3 agentes vivos ao mesmo tempo (`CENTRAL_MAX_PARALELO`); o excedente espera. Execução esperando resposta há mais de 20 min tem o processo fechado e retomado quando você responde.

## Limite de uso do plano

Quando o limite do plano (janela de 5 h ou semanal) estoura no meio de uma execução, ela passa a **aguardando o limite virar**: a Central lê o horário da virada que o Claude Code informa, fecha o processo do agente (a sessão fica guardada) e, passado o horário (com ~1 min de folga), **retoma sozinha na mesma sessão** — não precisa mandar "continue". Sem horário informado, tenta de novo em 5, 10, 20… até 60 min. Enquanto o limite estiver esgotado, execução nova espera na fila e começa sozinha depois; o que você escrever no chat vira recado e vai junto na retomada. A espera sobrevive a um reinício da Central. Há «Retomar agora» para forçar, e um aviso no topo de todas as páginas.

## Regras que a Central não quebra

- Lê e escreve TODO só pelo parser único (`.claude/skills/gerir-todo/todo_md.py`); status continua só nos TODOs.
- Nada do projeto depende dela: desligada, tudo segue pelo VS Code.
- Nunca `--no-verify`, nunca `claude --bare`, nunca `bypassPermissions` — o modo `auto` ainda passa cada ação pelo classificador.
- Escuta só em `127.0.0.1`; toda ação exige o token da página e recusa `Host`/`Origin` de fora (proteção contra sites abertos no navegador).

## Limites conhecidos

- No modo sem interface não existe `AskUserQuestion`: o agente pergunta em texto e encerra o turno.
- Play-teste no Editor e pixel pass manual no Aseprite seguem com você — os itens aparecem nas filas, a execução é com as mãos.
- `unity-validar` exige o Editor fechado e roda só em execução da árvore principal (o worktree não tem a `Library/`).
- Arquivos fora do git que uma execução da árvore principal muda (`_lotes/`, `_processado/`) não voltam no descarte; a validação os lista.

## Manutenção

- **Fila nova** = seção nova num TODO → registrar em [`filas.json`](filas.json). O `test_filas` falha se uma seção com tabela ficar sem fila, e o painel avisa.
- **Testes:** `cd Central && .venv\Scripts\python.exe -m unittest discover -s tests -t .` — rodam no pre-commit quando algo em `Central/` está em stage, e no CI. O agente é substituído por um falso; o contrato com o `stream-json` real está gravado em `tests/fixtures/sessao.jsonl`.
- **Dependências:** versões fixas em `requirements.txt`.
- **Worktree preso** (raro, servidor de build do dotnet segurando arquivo): `dotnet build-server shutdown`, depois `git worktree prune`.
