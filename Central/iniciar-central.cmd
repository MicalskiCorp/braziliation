@echo off
rem Sobe a Central do Braziliation (ADR-012) em http://127.0.0.1:8765 - Ctrl+C encerra.
rem Uso manual. A tarefa agendada "Braziliation - Central" chama o pythonw direto, sem console
rem (ver registrar-tarefa.ps1). Na primeira vez cria o ambiente Python da Central.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Criando o ambiente da Central em .venv ...
  py -m venv .venv || exit /b 1
  ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt || exit /b 1
)
".venv\Scripts\python.exe" -m central
