# Como Indexar — Convenções para Unity/C#

> Metodologia de indexação de arquivos-fonte do Braziliation (Unity, C#).

## Regras de Indexação

1. **Nunca editar fontes** — apenas referenciar caminhos relativos a `Desenvolvimento/`.
2. **Agrupar por sistema** — cada ficha em `Architecture/Sistemas/` lista, na seção "Fontes Técnicas", o conjunto coeso de scripts daquele sistema. Não há índice paralelo.
3. **Usar caminhos relativos** — ex.: `Assets/Scripts/Core/GameServiceLocator.cs`.
4. **Nome entre crases** — a primeira coluna é `` `Nome.cs` ``; é o que o teste de consistência procura.
5. **Ignorar pastas geradas e de terceiros** — `Library/`, `Temp/`, `Logs/`, `bin/`, `obj/`, `TextMesh Pro/`.
6. **Priorizar interfaces** — listar interfaces antes das implementações.

## Estrutura de Entrada

```markdown
| Arquivo | Caminho | Função |
|---------|---------|--------|
| `GameServiceLocator.cs` | `Assets/Scripts/Core/GameServiceLocator.cs` | Service locator global |
```

## Quando Atualizar

- Script criado → linha na ficha do sistema.
- Script renomeado ou movido → corrigir a ficha.
- O `DocsConsistencyTests` falha se algum `.cs` ficar de fora — a varredura é o próprio teste.
