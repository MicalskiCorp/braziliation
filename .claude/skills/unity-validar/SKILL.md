---
name: unity-validar
description: Compila o projeto Unity do Braziliation em batchmode, sem abrir o Editor, e resume os erros de compilação com arquivo e linha; com --testes também roda os testes EditMode. Use depois de editar qualquer script em Assets/, antes de commitar mudança Unity, quando o usuário pedir para "validar no Unity", "ver se compila" ou "rodar testes do Unity".
allowed-tools: Bash(py .claude/skills/unity-validar/scripts/validar.py*)
---

# Skill: unity-validar

Fecha o ciclo que o CI não cobre: o CI roda só o core C# puro (`Tests/Braziliation.Game.Tests/`). Scripts de `Assets/Scripts/`, editor tools, cenas e import settings só são verificados por esta skill (ou pelo workflow `unity-ci.yml` quando os secrets de licença estiverem configurados).

> **Licença (medido em 2026-09-13):** a compilação acontece durante o carregamento do projeto e funciona com a licença Personal gerenciada pelo Unity Hub. **Rodar testes exige uma licença ativada na máquina**: sem ela o Editor sai com código 198 (`No valid Unity Editor license found`) — com ou sem `-batchmode`, com ou sem a CLI oficial (`unity license status` mostra "nenhuma ativa"). Ativar uma vez: Unity Hub → Preferences → Licenses → Add → *Get a free personal license*.

## Roteiro

1. Rodar:
   ```bash
   py .claude/skills/unity-validar/scripts/validar.py           # compila (padrão, ~1-2 min)
   py .claude/skills/unity-validar/scripts/validar.py --testes  # compila + testes EditMode (exige licença ativada)
   ```
   Se `--testes` responder que a licença foi recusada, a compilação reportada continua valendo; peça ao usuário para ativar a licença uma vez.
2. Se o script disser que **o Editor está aberto** para este projeto: não force. Peça ao usuário para fechar o Editor, ou use a CLI oficial (`unity status` / skill `unity-cli` do plugin da Unity) para agir no Editor aberto.
3. Ler o resumo:
   - **Erros de compilação** vêm como `arquivo(linha,coluna): error CSxxxx: mensagem` — corrigir na fonte e rodar de novo.
   - **Testes EditMode** falhando vêm com nome e mensagem — os testes vivem em `Desenvolvimento/Assets/Tests/EditMode/`.
4. Arquivos novos em `Assets/` ganham `.meta` nessa execução. Rodar a skill `meta-check` e incluir os `.meta` no commit.
5. O resultado fica em `.claude/state/unity-validar.json` (lido pelo hook de início de sessão) e o log completo em `.claude/state/unity-validar.log`.

## Regras

- Nunca apagar `Temp/UnityLockfile` para "destravar" — ele existe porque há um Editor aberto no projeto.
- Import do Unity pode reescrever `.meta` e `ProjectSettings/`: conferir o `git status` depois da execução e explicar qualquer arquivo alterado que não era esperado.
- Falha de compilação é bloqueadora: não commitar script Unity com esta skill reprovando.
