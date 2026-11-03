# Para (ou reinicia) a Central do Braziliation (ADR-012).
# Stop-ScheduledTask sozinho NAO basta: a tarefa roda conhost -> python.exe do .venv (um lancador)
# -> python.exe real, e so o comeco da cadeia cai. O python real fica orfao segurando a porta 8765,
# e a Central nova sai com "porta em uso" (visto em 2026-11-03). Este script derruba a cadeia toda.
# Uso:  powershell -ExecutionPolicy Bypass -File Central\parar-central.ps1 [-Reiniciar] [-Forcar]
param([switch]$Reiniciar, [switch]$Forcar)
$ErrorActionPreference = "Stop"
$tarefa = "Braziliation - Central"

$servidores = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like "*Central\.venv\Scripts\python.exe*-m central*" })
$ids = @($servidores | ForEach-Object { $_.ProcessId })
$agentes = @(Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
    Where-Object { $ids -contains $_.ParentProcessId })
if ($agentes.Count -gt 0 -and -not $Forcar) {
    throw "$($agentes.Count) agente(s) da Central rodando. Espere terminar, ou use -Forcar (a execucao fica interrompida e se retoma depois)."
}

Stop-ScheduledTask -TaskName $tarefa -ErrorAction SilentlyContinue
foreach ($p in $agentes + $servidores) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

if ($Reiniciar) {
    Start-ScheduledTask -TaskName $tarefa
    Write-Host "Central reiniciada: http://127.0.0.1:8765"
} else {
    Write-Host "Central parada ($($servidores.Count) processo(s) do servidor encerrados)."
}
