# Protocolo de Comunicação — Motor ↔ Produto

> Define as regras de sincronização entre `docs/estrutura/` (motor externo) e `docs/IA/` (produto).

## Camadas

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Motor externo | `Docs/estrutura/` | Índice técnico dos arquivos-fonte (scripts, assets, cenas) |
| Produto (IA) | `Docs/IA/` | Documentação navegável por agentes: features, sistemas, mecânicas |

## Regras de Sincronização

1. **Novo script criado** → adicionar linha em `indices/sistemas.md` na seção do sistema correspondente.
2. **Novo sistema criado** → criar `Docs/IA/Sistemas/{Sistema}.md` e adicionar seção em `indices/sistemas.md`.
3. **Script renomeado/movido** → atualizar `indices/sistemas.md` e `Docs/IA/Sistemas/{Sistema}.md` (seção Fontes Técnicas).
4. **Feature documentada** → verificar se sistemas referenciados têm entrada em `indices/sistemas.md`.
5. **Varredura automática (Modo 6)** → detecta gaps automaticamente e cria stubs.

## Verificação de Consistência

Executar periodicamente:

```powershell
# Sistemas em src/ sem seção em indices/sistemas.md
$sistemasNoFonte = Get-ChildItem "src/Braziliation.Game.Core" -Directory | Select-Object -ExpandProperty Name
# Comparar com seções em indices/sistemas.md
```

## Ponto de Contato

O agente `GameArquitetoMarkdown` é o único responsável por manter ambas as camadas sincronizadas.
Documentação do agente: [`../../IA/Agentes/GameArquitetoMarkdown.md`](../../IA/Agentes/GameArquitetoMarkdown.md)
