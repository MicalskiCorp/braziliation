# CI do Unity (GameCI) — desligado por decisão

**ADR-010.** O workflow [`unity-ci.yml`](../../../.github/workflows/unity-ci.yml) existe, está correto e **não roda**: o job é gateado por `vars.UNITY_CI_ENABLED` e aparece como `skipped`. Não é pendência de configuração — é decisão, porque o caminho foi fechado pela Unity.

A validação do lado Unity é **local e obrigatória**: skill `unity-validar` (compila em batchmode e roda os EditMode), exigida pelo `pre-commit` para qualquer script de `Assets/` em stage.

## Por que não dá para ligar

A Unity encerrou a ativação manual de licenças Personal. O fluxo `.alf → ulf` — única porta do tier gratuito no GameCI — responde hoje:

> *You are not eligible to activate your license offline. Offline activation is available only for Enterprise and Industry seats.*

O Unity 6 licencia Personal por **entitlement de conta** (`UnityEntitlementLicense.xml` em `AppData/Local/Unity/licenses/`), formato que o `game-ci/unity-test-runner@v4` não consome. O `.ulf` que o secret `UNITY_LICENSE` espera não é mais obtenível num seat gratuito. O [issue #408 do GameCI](https://github.com/game-ci/documentation/issues/408) documenta o impasse e segue aberto.

Medido em 20 set 2026, nesta máquina: licença **ativa** (`Unity Personal (Assigned)`), nenhum `.ulf` em lugar nenhum do disco, `C:\ProgramData\Unity` inexistente, e `license activate --generate-request` gerando um `.alf` que o site recusa.

### Alternativas avaliadas e recusadas

| Caminho | Por que não |
|---|---|
| Runner self-hosted | Exige a máquina pessoal ligada e expõe superfície de ataque via PR de fork |
| `--include-personal` do CLI novo do GameCI ([PR #246](https://github.com/game-ci/cli/pull/246)) | É do CLI novo, não do `unity-test-runner@v4`; exige a senha da conta Unity como secret; e **consome o seat Personal até devolvê-lo** — pode derrubar a licença do Editor local no meio do trabalho |

## Se um dia voltar a ser possível

Ligar é criar os três secrets e a variável — o workflow já está pronto para isso.

```powershell
# o .ulf só existirá se a Unity voltar a oferecer ativação de Personal, ou com Plus/Pro
Get-Content "C:\ProgramData\Unity\Unity_lic.ulf" -Raw | gh secret set UNITY_LICENSE
gh secret set UNITY_EMAIL
gh secret set UNITY_PASSWORD
gh variable set UNITY_CI_ENABLED --body true
gh workflow run "Unity (compilação + EditMode)"
```

Com a variável ligada e os secrets faltando, o job **falha** no primeiro passo dizendo exatamente isso — configuração pela metade não vira verde.

Com licença **Plus/Pro**, o caminho é outro e mais simples: `UNITY_SERIAL` no lugar do `UNITY_LICENSE`.

A imagem do editor não é obstáculo: o GameCI publica para a versão exata do projeto — conferido em 20 set 2026, `6000.2.8f1` tem 95 tags, entre elas `unityci/editor:6000.2.8f1-base-3.2.2`. O `unity-test-runner` detecta a versão pelo `ProjectSettings/ProjectVersion.txt`.

## Licença local — essa sim funciona

Ativar na máquina destrava `unity-validar --testes`:

```powershell
unity auth login                                   # abre o navegador
unity license activate --personal --accept-eula
unity license status                               # "Licença: ativa — Unity Personal (Assigned)"
```

Feito em 20 set 2026; os testes EditMode rodaram pela primeira vez, 9/9. **O CLI ativa Personal** — ao contrário do que este projeto registrava até então, com base em ter visto `license status` vazio sem nunca ter tentado o `activate`.

## Custo, se um dia rodar

O primeiro run importa a `Library/` inteira (lento). Os seguintes usam o cache da `Library/`, chaveado pelo `packages-lock.json`.
