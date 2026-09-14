---
name: novo-adr
description: Registra uma decisão de arquitetura do Braziliation como ADR numerado em Desenvolvimento/Docs/Architecture/architecture_decisions.md, no formato do arquivo, e marca como substituído qualquer ADR que ela invalide. Use quando o usuário ou o @TechLead tomar uma decisão estrutural (layout, dependência, padrão, plataforma, resolução, persistência) ou pedir "novo ADR", "registrar decisão de arquitetura".
---

# Skill: novo-adr

Os ADR-001 e ADR-003 ficaram meses com status errado depois de serem substituídos. Esta skill fecha esse buraco: todo ADR novo pergunta quem ele substitui.

## Roteiro

1. Ler `Desenvolvimento/Docs/Architecture/architecture_decisions.md` inteiro — o próximo número é o maior `ADR-NNN` + 1.
2. Confirmar com o usuário (perguntar só o que não der para inferir da conversa):
   - **contexto** — o problema ou a opção que levou à decisão;
   - **decisão** — o que foi escolhido, em uma ou duas frases;
   - **consequências** — trade-offs e o que muda para quem escreve código/asset;
   - **substitui algum ADR?** Procurar ativamente ADRs cujo tema conflite (mesmo sistema, mesmo parâmetro).
3. Escrever o ADR **antes** da linha final `*(Novos ADRs entram acima desta linha...)*`, no formato dos existentes:
   `## ADR-NNN: Título` · `- **Date:**` (AAAA-MM-DD) · `- **Status:** Accepted` · `- **Context:**` · `- **Decision:**` · `- **Consequences:**`.
4. Para cada ADR substituído: trocar o status para `**Superseded por ADR-NNN** (data). {o que continua valendo, se algo}`. O `DocsConsistencyTests` falha se um ADR substituído não indicar o substituto.
5. Atualizar os pontos que repetem a decisão: `CLAUDE.md` (seção "Estado conhecido") e `.claude/rules/*.md` se tratarem do tema. Se a decisão tiver consequência de código, registrar a pendência em `Desenvolvimento/Docs/TODO.md`.
6. Rodar `dotnet test Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj` e reportar. O `@TechLead` não tem `Bash`: executado por ele, avisar o usuário que o teste roda no pre-commit — o `DocsConsistencyTests` cobra o ADR substituído sem substituto.

## Regras

- Um ADR por decisão. Status `Proposed` só se o usuário ainda não decidiu — e então com data para voltar ao assunto.
- Nunca apagar ADR antigo: ele vira histórico com status `Superseded`.
