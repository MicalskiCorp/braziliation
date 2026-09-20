# CI do Unity (GameCI)

O workflow [`unity-ci.yml`](../../../.github/workflows/unity-ci.yml) compila o projeto e roda os testes de `Assets/Tests/EditMode/` no GitHub Actions. Ele fica **desligado** — o job aparece como `skipped` — até a variável `UNITY_CI_ENABLED` existir.

Localmente, a mesma validação é a skill `unity-validar` (`py .claude/skills/unity-validar/scripts/validar.py`).

> **Por que `skipped` e não `success`:** até 20 set 2026 o gate ficava nos passos, e o job fechava como **success em 6 segundos** com tudo pulado. Um check verde que não verificou nada é indistinguível de um que verificou — e quem o lê como "o Unity passou" está confiando num passo pulado. O gate subiu para o nível do job.

## Estado em 20 set 2026

Nada configurado: `gh secret list` volta vazio, não existe `.ulf` em lugar nenhum da máquina, e `unity auth status` diz "Você não está logado". O que existe é `AppData/Local/Unity/licenses/UnityEntitlementLicense.xml` — o *entitlement* do Hub, que **não** serve como `UNITY_LICENSE`.

## Habilitar — 4 passos

O passo 1 exige a sua conta Unity (navegador ou Hub); os outros três são linha de comando.

### 1. Ativar a licença e gerar o `.ulf`

Pelo Hub: `Preferences → Licenses → Add → Get a free personal license`.

Pelo CLI oficial (mais rápido, se funcionar):

```bash
unity auth login                                   # abre o navegador
unity license activate --personal --accept-eula
unity license status                               # confirmar "ativa"
```

> O CLI **expõe** `license activate --personal --accept-eula` — o que contraria a nota antiga deste projeto de que Personal só ativa pelo Hub. Não foi testado nesta máquina, porque exige o login. Se falhar, o caminho do Hub continua valendo; o que importa é o arquivo no fim.

Confirmar que o arquivo saiu — o Hub pode mostrar a licença **sem** ter gerado o `.ulf`, e foi nisso que este projeto tropeçou:

```bash
ls "C:/ProgramData/Unity/Unity_lic.ulf"
```

| Sistema | Caminho do `.ulf` |
|---|---|
| Windows | `C:\ProgramData\Unity\Unity_lic.ulf` |
| macOS | `/Library/Application Support/Unity/Unity_lic.ulf` |
| Linux | `~/.local/share/unity3d/Unity/Unity_lic.ulf` |

### 2. Criar os três secrets

O primeiro lê do arquivo; os outros dois pedem o valor no terminal, para a senha não passar por histórico de shell nem por conversa.

```bash
gh secret set UNITY_LICENSE < "C:/ProgramData/Unity/Unity_lic.ulf"
gh secret set UNITY_EMAIL
gh secret set UNITY_PASSWORD
```

| Secret | Conteúdo |
|--------|----------|
| `UNITY_LICENSE` | conteúdo inteiro do `.ulf` |
| `UNITY_EMAIL` | e-mail da conta Unity |
| `UNITY_PASSWORD` | senha da conta Unity |

`UNITY_SERIAL` só existe para Plus/Pro — não usar.

### 3. Ligar o workflow

```bash
gh variable set UNITY_CI_ENABLED --body true
```

Com a variável ligada e os secrets faltando, o job **falha** no primeiro passo dizendo exatamente isso — configuração pela metade não vira verde.

### 4. Testar na hora

Sem esperar um commit em `Assets/`, pelo `workflow_dispatch`:

```bash
gh workflow run "Unity (compilação + EditMode)"
gh run list --limit 3
```

## O que isso destrava junto

O mesmo `.ulf` é o que falta para `unity-validar --testes` rodar os EditMode por linha de comando — hoje o Editor sai com código 198 (`No valid Unity Editor license found`). É um item Alta do `TODO.md` e uma dívida Alta em `tech_debt.md`: os dois caem na mesma ativação.

## Imagem do editor

O GameCI publica imagem para a versão exata do projeto — conferido em 20 set 2026: `6000.2.8f1` tem 95 tags, entre elas `unityci/editor:6000.2.8f1-base-3.2.2`. O `unity-test-runner` detecta a versão pelo `ProjectSettings/ProjectVersion.txt`, então não é preciso fixá-la no workflow.

## Custo

O primeiro run importa a `Library/` inteira (lento). Os seguintes usam o cache da `Library/`, chaveado pelo `packages-lock.json`.
