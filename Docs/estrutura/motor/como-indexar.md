# Como Indexar — Convenções para Unity/C#

> Metodologia de indexação de arquivos-fonte adaptada para o projeto Braziliation (Unity, C#).

## Regras de Indexação

1. **Nunca editar fontes** — apenas referenciar caminhos relativos à raiz do repositório.
2. **Agrupar por sistema** — cada entrada em `indices/sistemas.md` mapeia um conjunto coeso de scripts.
3. **Usar caminhos relativos** — ex.: `Assets/Scripts/Core/GameServiceLocator.cs`.
4. **Ignorar pastas binárias** — `Library/`, `Temp/`, `Logs/`, `bin/`, `obj/`.
5. **Priorizar interfaces** — ao listar scripts de um sistema, listar interfaces antes de implementações.

## Estrutura de Entrada no Índice

```markdown
| Arquivo | Caminho | Responsabilidade |
|---------|---------|-----------------|
| GameServiceLocator.cs | `Assets/Scripts/Core/GameServiceLocator.cs` | Service locator global |
```

## Frequência de Atualização

- Ao criar um novo script → adicionar ao índice do sistema correspondente
- Ao renomear/mover um script → atualizar todos os links em `docs/IA/Sistemas/`
- Na Varredura Automática (Modo 6) → verificar gaps automaticamente
