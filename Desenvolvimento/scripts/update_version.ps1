Param(
    [Parameter(Mandatory = $true)]
    [string]$NewVersion
)

# Atualiza a versão do jogo nos dois lugares que precisam concordar:
#   - Desenvolvimento/VERSION  (fonte da verdade, lida por scripts e docs)
#   - bundleVersion em ProjectSettings/ProjectSettings.asset (versão gravada no build do Unity)
# O RepositoryLayoutTests falha se os dois divergirem.
#
# Não faz commit, tag nem push: fechar uma versão é decisão de release, feita à mão.
# Uso: pwsh Desenvolvimento/scripts/update_version.ps1 -NewVersion 0.2.0-alpha

$ErrorActionPreference = "Stop"
$projeto = Split-Path -Parent $PSScriptRoot

[IO.File]::WriteAllText((Join-Path $projeto "VERSION"), "$NewVersion`n", (New-Object Text.UTF8Encoding($false)))

$settings = Join-Path $projeto "ProjectSettings/ProjectSettings.asset"
$texto = [IO.File]::ReadAllText($settings)
$novo = [regex]::Replace($texto, '(?m)^(\s*bundleVersion:\s*)\S+', "`${1}$NewVersion")
[IO.File]::WriteAllText($settings, $novo, (New-Object Text.UTF8Encoding($false)))

Write-Host "Versão atualizada para $NewVersion (VERSION + bundleVersion)."
Write-Host "Próximos passos, à mão: git commit, git tag v$NewVersion, git push --tags."
