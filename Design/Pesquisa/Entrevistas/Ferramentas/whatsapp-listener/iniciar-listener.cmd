@echo off
rem Sobe o listener de entrevistas e o reinicia se o processo cair (ADR-009).
rem Usado pela tarefa "Braziliation - Listener de entrevistas" do Agendador do Windows;
rem a saida vai para listener.log (fora do git). Rodar a mao tambem funciona.
cd /d "%~dp0"
:loop
rem Rotaciona o log acima de 20 MB: a Baileys loga cada erro de rede e o arquivo
rem passou de 27 MB em 6 dias. Guarda uma geracao anterior e recomeca.
for %%A in ("listener.log") do if %%~zA GTR 20971520 move /y "listener.log" "listener.log.1" >nul
echo [%date% %time%] iniciando listener>> listener.log
node listener.js>> listener.log 2>&1
set saida=%errorlevel%
rem -1073741502 (0xC0000142) = o node nao achou console. Acontece quando o conhost da
rem tarefa morre (Stop-ScheduledTask so derruba ele) e este cmd fica orfao: reiniciar so
rem repetiria a falha em laco. Sai e deixa a tarefa agendada subir uma instancia nova.
if "%saida%"=="-1073741502" (echo [%date% %time%] sem console, encerrando o laco orfao>> listener.log & exit /b 1)
echo [%date% %time%] listener saiu (codigo %saida%), reiniciando em 30 s>> listener.log
rem ping no lugar do timeout: timeout exige console e, sem ele, nao espera nada.
ping -n 31 127.0.0.1 > nul
goto loop
