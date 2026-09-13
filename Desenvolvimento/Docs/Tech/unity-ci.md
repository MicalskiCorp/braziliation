# CI do Unity (GameCI)

O workflow [`unity-ci.yml`](../../../.github/workflows/unity-ci.yml) compila o projeto e roda os testes de `Assets/Tests/EditMode/` no GitHub Actions. Ele fica **em espera** (só imprime um aviso) até os três secrets abaixo existirem no repositório.

Localmente, a mesma validação é a skill `unity-validar` (`py .claude/skills/unity-validar/scripts/validar.py`).

## Licença Personal

A licença Personal funciona no CI. O que ela não permite é ser **ativada** pela linha de comando — por isso o `.ulf` é gerado uma vez e guardado como secret.

1. Seguir o passo de ativação do GameCI: <https://game.ci/docs/github/activation/>.
2. Conferir que o arquivo `.ulf` foi de fato criado: o Hub pode mostrar a licença sem ter gerado o arquivo — clicar em **Add** durante a ativação.
3. Em *Settings → Secrets and variables → Actions* do repositório, criar:

| Secret | Conteúdo |
|--------|----------|
| `UNITY_LICENSE` | conteúdo inteiro do arquivo `.ulf` |
| `UNITY_EMAIL` | e-mail da conta Unity |
| `UNITY_PASSWORD` | senha da conta Unity |

`UNITY_SERIAL` só existe para licenças Plus/Pro — não usar.

## Custo

O primeiro run importa a `Library/` inteira (lento). Os seguintes usam o cache da `Library/`, chaveado pelo `packages-lock.json`.
