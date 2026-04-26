# Design — Camada Criativa do Braziliation

> Camada criativa e conceitual do projeto Braziliation — separada do repositório Unity para ciclo de vida independente.
> Agente responsável: `@GameCriativoMarkdown`

## Estrutura

| Pasta | Descrição | Agente |
|-------|-----------|--------|
| [`Criativo/`](Criativo/index.md) | Lendas, narrativa, ideias e brainstorm | `@GameCriativoMarkdown` |
| `Arts Conceituas/` | Arte conceitual de cidades, monstros e cenários | Referência visual |

## Conexão com o Projeto Técnico

Quando uma ideia criativa virar feature de jogo:

```
@GameCriativoMarkdown ideia aprovada
    ↓
@GameArquitetoMarkdown Nova feature: {Nome}  →  Desenvolvimento/Docs/GDD/Features/
```

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Criativa (aqui) | `Design/Criativo/` | Lendas, personagens, arcos, brainstorm |
| Arte conceitual | `Design/Arts Conceituas/` | Referências visuais para assets |
| Técnica (repo Unity) | `Desenvolvimento/Docs/` | Features, sistemas, ADRs, roadmap |

---

> Para catalogar lenda: `@GameCriativoMarkdown Catalogar lenda: {Nome}`
> Para iniciar brainstorm: `@GameCriativoMarkdown Brainstorm: {tema}`
> Para criar feature técnica a partir de ideia: `@GameArquitetoMarkdown Nova feature: {Nome}`
