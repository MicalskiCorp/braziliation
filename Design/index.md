# Design — Camadas de Pesquisa, Criativo e Arte do Braziliation

> Tudo que vem antes do código: pesquisa com fonte, lore, direção e fonte de arte. Mesmo repositório do projeto Unity (`Desenvolvimento/`), com dono por pasta.

## Estrutura

| Pasta | Descrição | Dono |
|-------|-----------|------|
| [`Pesquisa/`](Pesquisa/index.md) | Pesquisa histórica e folclórica aprovada, com fonte | `@Historiador` |
| [`Criativo/`](Criativo/index.md) | Lendas, cidades, personagens, arcos, ideias e brainstorm | `@GameCreative` |
| [`Models/`](Models/index.md) | Templates de cidade e personagem | `@GameCreative` |
| [`ArteConceitual/`](ArteConceitual/index.md) | Concept art aprovado, referências visuais e paletas | `@SpriteArtist` + usuário |
| [`ArteFonte/`](ArteFonte/index.md) | Ferramentas do pipeline, context packs e saídas de IA | `@SpriteArtist` |
| [`GuiasDeArte/`](GuiasDeArte/index.md) | Style bible, escala, paletas, animação e pipelines de sprite | Usuário (direção de arte) |

## Fluxo até o código

```
@Historiador   Pesquisa/  → handoff em Criativo/TODO.md
@GameCreative  Criativo/  → handoff em Desenvolvimento/Docs/TODO.md
@GameArchitect Desenvolvimento/Docs/GDD/Features/
```

Cada passo é acionado manualmente pelo usuário — mapa completo no [`AGENTS.md`](../AGENTS.md).

---

> Catalogar lenda: `@GameCreative Catalogar lenda: {Nome}` · pesquisar tema: `@Historiador Pesquisar: {tema}`
