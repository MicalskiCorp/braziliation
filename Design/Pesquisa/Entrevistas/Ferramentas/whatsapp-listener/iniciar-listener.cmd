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
echo [%date% %time%] listener saiu (codigo %errorlevel%), reiniciando em 30 s>> listener.log
timeout /t 30 /nobreak > nul
goto loop
