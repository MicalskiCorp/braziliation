# Template — Ficha de cidade

A ficha de uma cidade é uma **pasta** `Design/Criativo/Estados/{Estado}/cidades/{Cidade}/`, com um arquivo por seção.
O `index.md` é a porta: identidade da cidade e a tabela que lista cada arquivo. O `DocsConsistencyTests` cobra que todo
arquivo da pasta apareça nela, e o `TokenBudgetTests` cobra o teto de roteador (~1.500 tokens).

> Até 2026-11-09 a ficha era um `index.md` único. A de Blumenau passou de 5 mil tokens e era lida inteira mesmo para
> mexer num lugar só. Agora cada lugar vive no seu arquivo e a ficha cresce de lado, não para baixo.

| Arquivo | Conteúdo | Quando criar |
|---------|----------|--------------|
| `index.md` | Cabeçalho, Características e a tabela da ficha | Sempre |
| `monstros.md` | Estética e tipos de monstro | Sempre |
| `lugar-{slug}.md` | Um local real: lenda, ideias, mapa, NPC, side-quest e boss **daquele lugar** | Um por lugar |
| `ideias.md` | Ideias e easter eggs sem lugar específico | Sempre |

- **Slug:** minúsculo, sem acento, hífen no lugar de espaço, só o nome do local: `lugar-teatro-carlos-gomes.md`, `lugar-ilha-feia.md`.
- **Missão, NPC e boss** de um lugar ficam no arquivo do lugar, como seção `##`. Os de cidade inteira vão para `ideias.md`.
- **Túnel** entre cidades é um lugar (`lugar-tunel-{nome}.md`), com Origem Histórica, Como o Personagem Descobre e Características do Trecho.
- Feature do GDD que nasce de um lugar aponta o `lugar-{slug}.md` como "Referência criativa", não o `index.md`.
- Lugar novo: criar o arquivo **e** a linha na tabela do `index.md`.

## `index.md`

```markdown
# {Nome da Cidade} — "{Nome no Game}"

> **Estado:** {Estado}
> **Punk Genre:** {ClockPunk | BioPunk | SteamPunk | DieselPunk | CoalPunk | OccultPunk | HorrorPunk | WeirdWest | ...}
> **Status:** 📋 Rascunho | 🔨 Em Construção | ✅ Pronto

---

## Características

- **Estrutura:** {Estilo de estrutura da cidade hoje — arquitetura, geografia, origem histórica}
- **Tipo:** {Gênero punk que mais combina com a cidade — com justificativa baseada na realidade local}
- **Descrição:** {Como essa cidade se parece no futuro distópico dieselpunk do Braziliation — use Estrutura + Tipo como base}

---

## Ficha

Um arquivo por seção; cada lugar no seu `lugar-{slug}.md`. Template: [`ModelCidade.md`](../../../../../Models/ModelCidade.md).

| Arquivo | Conteúdo |
|---------|----------|
| [`monstros.md`](monstros.md) | Estética e tipos de monstro |
| [`lugar-{slug}.md`](lugar-{slug}.md) | {Nome do Local de Referência Real} |
| [`ideias.md`](ideias.md) | Ideias e easter eggs sem lugar específico |
```

## `monstros.md`

```markdown
# Monstros

> Ficha de [{Nome da Cidade} — "{Nome no Game}"](index.md).

- **Estética:** {Descrição visual/estética dos monstros dessa cidade — baseada em Cultura/Estrutura/Tipo/Folclore local}
- **Tipos:**
  - `{NomeMonstro}` — {Descrição curta do comportamento e aparência}
  - `{NomeMonstro}` — {Descrição}
```

## `lugar-{slug}.md`

```markdown
# {Nome do Local de Referência Real}

> Ficha de [{Nome da Cidade} — "{Nome no Game}"](index.md).

- **Lenda / Mistério / Folclore:** {O que existe de lenda, horror ou mistério sobre esse local}
- **Ideias:**
  - {Ideia de cenário, evento, Easter Egg ou missão ligada a este local}
  - {Mais ideias...}
```

## `ideias.md`

```markdown
# Ideias / Easter Eggs *(sem lugar específico)*

> Ficha de [{Nome da Cidade} — "{Nome no Game}"](index.md).

## {Referência Cultural / Histórica / Folclórica}

- {Descrição da ideia, missão ou Easter Egg}
- {Variações ou desdobramentos}
```
