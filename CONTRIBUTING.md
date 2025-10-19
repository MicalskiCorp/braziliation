# Guia de Contribuição – Braziliation

## Fluxo de trabalho
1. Crie um branch a partir de `develop`:  
   `git checkout -b feature/<descrição>`
2. Faça commits pequenos e significativos.
3. Inclua o ID da tarefa ClickUp no commit: `#CU-xxxx`.
4. Abra um Pull Request para `develop`.
5. Aguarde revisão e aprovação antes de merge.

## Convenções de commit
- **feature:** novas funcionalidades  
- **fix:** correções  
- **docs:** documentação  
- **refactor:** refatoração sem alterar comportamento  
- **chore:** manutenção técnica

## Estilo de código
Siga as convenções C# (Microsoft Style).  
Antes de commit, rode `dotnet format`.
