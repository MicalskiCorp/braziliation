# Registra a tarefa "Braziliation - Central" no Agendador do Windows (ADR-012).
# Sobe no logon, sem janela, so em 127.0.0.1, e volta sozinha se cair (1 min).
# Rodar uma vez:  powershell -ExecutionPolicy Bypass -File Central\registrar-tarefa.ps1
# Tirar:          Unregister-ScheduledTask -TaskName "Braziliation - Central" -Confirm:$false
$ErrorActionPreference = "Stop"
$central = $PSScriptRoot
$python = Join-Path $central ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Crie o ambiente antes: rode Central\iniciar-central.cmd uma vez." }

# conhost --headless, o mesmo esquema do listener: nenhuma janela. O pythonw.exe do .venv NAO
# serve - no Windows ele e um intermediario que abre o python.exe de console, e o Windows
# Terminal mostra a janela (visto em 2026-11-03; fechar a janela derrubava a Central).
$conhost = Join-Path $env:WINDIR "System32\conhost.exe"
$acao = New-ScheduledTaskAction -Execute $conhost -Argument "--headless `"$python`" -m central" -WorkingDirectory $central
$gatilho = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$config = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "Braziliation - Central" -Action $acao -Trigger $gatilho -Settings $config `
    -Principal $principal -Force `
    -Description "Central do Braziliation (ADR-012): painel local das filas em http://127.0.0.1:8765" | Out-Null
Start-ScheduledTask -TaskName "Braziliation - Central"
Write-Host "Tarefa registrada e iniciada. Abra http://127.0.0.1:8765"
