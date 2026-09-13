# Regras de Desenvolvimento – Braziliation

## Fase atual — até a v1 consolidada

- **Commits direto no `main`.** Não há branch de integração nem Pull Request ainda (decisão registrada no `CLAUDE.md` e no roadmap, fase "Preparação da v1").
- **Pre-commit obrigatório:** ativar uma vez por clone com `git config core.hooksPath .githooks`. Ele roda `dotnet test` (core + guardas de docs, tokens, convenções, agentes e `.gitignore`), o meta-check quando `Assets/` muda, o gate de paletas quando arte ou paleta muda e o gate do Unity quando há script de `Assets/` em stage.
- **Mudou script em `Assets/`?** Rodar `py .claude/skills/unity-validar/scripts/validar.py` antes do commit — o pre-commit recusa o commit se a última validação OK for anterior à edição.
- `--no-verify` só em emergência, dizendo o motivo na mensagem do commit.

## Depois da v1 (fluxo com PR)

- Branches: `main` (produção estável) · `develop` (integração) · `feature/*` · `hotfix/*` · `chore/*`.
- Merge apenas via Pull Request, com o CI verde (`ci.yml` e, com os secrets configurados, `unity-ci.yml`).

## Commits

`tipo(escopo): descrição breve`, em português. Tipos em uso: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`.
Ex.: `feat(player): adicionar salto duplo` · `docs(arte): processo de criação de assets em 5 etapas`

## Versionamento

- `Desenvolvimento/VERSION` e o `bundleVersion` do Unity andam juntos: atualizar só com `Desenvolvimento/scripts/update_version.ps1` (o `RepositoryLayoutTests` falha se divergirem).
- Releases com tag em semantic versioning: `v0.1.0`, `v0.1.1`, …
