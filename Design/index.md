# Design — Camada Criativa do Braziliation

> Camada criativa e conceitual do projeto Braziliation — separada do repositório Unity para ciclo de vida independente.
> Agente responsável: `@GameCreative`

## Estrutura

| Pasta | Descrição | Agente |
|-------|-----------|--------|
| [`Criativo/`](Criativo/index.md) | Lendas, narrativa, ideias e brainstorm | `@GameCreative` |
| [`ArteConceitual/`](ArteConceitual/index.md) | Referências visuais de cidades, personagens, criaturas, props e paletas | Referência visual |
| [`ArteFonte/`](ArteFonte/index.md) | Arquivos editáveis, estudos, exports e materiais de IA/Aseprite | Arte |
| [`GuiasDeArte/`](GuiasDeArte/index.md) | Bíblia visual, escala, paletas, animação e pipeline de sprites com IA | Arte + IA |

## Conexão com o Projeto Técnico

Quando uma ideia criativa virar feature de jogo:

```
@GameCreative ideia aprovada
    ↓
@GameArchitect Nova feature: {Nome}  →  Desenvolvimento/Docs/GDD/Features/
```

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Criativa (aqui) | `Design/Criativo/` | Lendas, personagens, arcos, brainstorm |
| Arte conceitual | `Design/ArteConceitual/` | Referências visuais para assets |
| Fonte de arte | `Design/ArteFonte/` | Arquivos editáveis e material de geração |
| Guias de arte | `Design/GuiasDeArte/` | Regras para manter estilo e consistência |
| Técnica (repo Unity) | `Desenvolvimento/Docs/` | Features, sistemas, ADRs, roadmap |

---

> Para catalogar lenda: `@GameCreative Catalogar lenda: {Nome}`
> Para iniciar brainstorm: `@GameCreative Brainstorm: {tema}`
> Para criar feature técnica a partir de ideia: `@GameArchitect Nova feature: {Nome}`
