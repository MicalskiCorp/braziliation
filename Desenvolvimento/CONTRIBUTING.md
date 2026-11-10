# Guia de Contribuição – Braziliation

## Fluxo de trabalho
1. Até a v1 estar consolidada, os commits vão direto no `main`. O fluxo com branch e Pull
   Request entra depois (roadmap › Preparação da v1).
2. Faça commits pequenos e significativos.
3. As tarefas vivem nos TODOs de camada e na Central (ADR-012) — o commit não leva ID de
   tarefa externo.

## Convenções de commit
Formato `tipo(escopo): descrição`, por exemplo `feat(pxfx): ...` ou `docs(todo): ...`.
- **feat:** novas funcionalidades  
- **fix:** correções  
- **docs:** documentação  
- **refactor:** refatoração sem alterar comportamento  
- **chore:** manutenção técnica

## Estilo de código
Siga as convenções C# (Microsoft Style).  
Antes de commit, rode `dotnet format`.

## Hooks e ferramentas recomendadas
- **dotnet format** — formatação de C#
- **StyleCop / EditorConfig** — regras de estilo (quando configurados no projeto)
- **pre-commit** — obrigatório. Ative uma vez por clone com `git config core.hooksPath .githooks`.
  Ele roda os testes .NET, os pares asset/`.meta` e as paletas, o `unity-validar` (quando há
  script em `Assets/`), o `todo.py validar` e os testes da Central. `--no-verify` só em
  emergência, explicando o motivo na mensagem do commit.
