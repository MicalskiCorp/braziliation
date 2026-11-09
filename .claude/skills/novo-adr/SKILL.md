---
name: novo-adr
description: Registra uma decisão de arquitetura do Braziliation como ADR numerado — um arquivo Desenvolvimento/Docs/Architecture/ADR/ADR-NNN.md mais a linha no ADR/index.md —, no formato dos existentes, e marca como substituído qualquer ADR que ela invalide. Use quando o usuário ou o @TechLead tomar uma decisão estrutural (layout, dependência, padrão, plataforma, resolução, persistência) ou pedir "novo ADR", "registrar decisão de arquitetura".
---

# Skill: novo-adr

Os ADR-001 e ADR-003 ficaram meses com status errado depois de serem substituídos. Esta skill fecha esse buraco: todo ADR novo pergunta quem ele substitui.

Um arquivo por ADR em `Desenvolvimento/Docs/Architecture/ADR/` (até 2026-11-09 era um arquivo único, que passou do teto de tokens). O `ADR/index.md` é o roteador: tabela com número, título, status e data.

## Roteiro

1. Ler `Desenvolvimento/Docs/Architecture/ADR/index.md` — o próximo número é o maior `ADR-NNN` da tabela + 1. Ler por inteiro só os ADRs cujo tema encosta na decisão nova.
2. Confirmar com o usuário (perguntar só o que não der para inferir da conversa):
   - **contexto** — o problema ou a opção que levou à decisão;
   - **decisão** — o que foi escolhido, em uma ou duas frases;
   - **consequências** — trade-offs e o que muda para quem escreve código/asset;
   - **substitui algum ADR?** Procurar ativamente na tabela ADRs cujo tema conflite (mesmo sistema, mesmo parâmetro).
3. Criar `ADR/ADR-NNN.md` no formato dos existentes:
   `# ADR-NNN: Título` · `- **Date:**` (AAAA-MM-DD) · `- **Status:** Accepted` · `- **Context:**` · `- **Decision:**` · `- **Consequences:**`. Links relativos partem de `ADR/` (para o repositório: `../../../../`).
4. Acrescentar a linha no fim da tabela do `ADR/index.md`: `| [ADR-NNN](ADR-NNN.md) | Título curto | Accepted | AAAA-MM-DD |`.
5. Para cada ADR substituído: trocar o status no arquivo dele para `**Superseded por ADR-NNN** (data). {o que continua valendo, se algo}` **e** a coluna Status da linha dele no índice para `Superseded por ADR-NNN`. O `DocsConsistencyTests` falha se um ADR substituído não indicar o substituto ou se o índice divergir do arquivo.
6. Atualizar os pontos que repetem a decisão: `CLAUDE.md` (seção "Estado conhecido") e `.claude/rules/*.md` se tratarem do tema. Se a decisão tiver consequência de código, registrar a pendência em `Desenvolvimento/Docs/TODO.md`.
7. Rodar `dotnet test Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj` e reportar — o `DocsConsistencyTests` cobra substituto, índice e links; o `TokenBudgetTests`, o teto de cada arquivo.

## Regras

- Um ADR por decisão, um arquivo por ADR. Status `Proposed` só se o usuário ainda não decidiu — e então com data para voltar ao assunto.
- Nunca apagar ADR antigo: ele vira histórico com status `Superseded`.
- A lista de vigentes é a coluna Status do `ADR/index.md`. Não a repita em outro documento.
