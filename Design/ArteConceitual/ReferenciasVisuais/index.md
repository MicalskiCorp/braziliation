# Referências Visuais — Braziliation

> Repositório de apoio visual para **qualquer asset** do fluxo de IA (`pipeline-ia-sprites.md`) — fotos e ilustrações reais de pessoas/lugares/fatos históricos, mas também referências de material, textura, anatomia, mood e composição para assets fictícios (criaturas, props, tiles). Serve pra dar mais controle e fidelidade ao prompt antes da geração, em vez de depender só de descrição verbal.

## Por que esta pasta existe

Gerar concept art só a partir de texto joga fora controle que uma referência visual concreta dá de graça — vale tanto pra uma pessoa/lugar real (ex.: Edith Gaertner, arquitetura enxaimel de Blumenau) quanto pra um elemento fictício do jogo (ex.: foto de latão oxidado real pra acertar o material de uma engrenagem inventada, referência de anatomia pra pose de uma criatura, mood de luz pra uma cena). Como visto no teste-âncora de 2026-07-24, prompts só-texto no SDXL base já têm dificuldade de isolar até o essencial do pedido — referência visual real ajuda tanto quem escreve o prompt quanto (se plugado no futuro) qualquer geração por imagem.

Esta pasta fica **antes** do Passo 2 (concept art) do fluxo em `pipeline-ia-sprites.md` — é insumo para montar o prompt/context pack, não substitui nenhuma etapa existente.

## Estrutura

```text
Design/ArteConceitual/ReferenciasVisuais/
├── index.md                     # este arquivo
├── {tema}/                      # ex.: edith-gaertner/, blumenau-arquitetura/, latao-oxidado/, anatomia-criatura-grande/
│   ├── *.jpg | *.png            # as referências em si
│   └── fontes.md                # obrigatório — de onde cada imagem veio
```

- Uma pasta por **tema** (pessoa, região, material, mood, criatura de referência...), não por asset — vários assets podem reaproveitar a mesma pasta (ex. vários NPCs de Blumenau reaproveitam `blumenau-arquitetura/`; vários props metálicos reaproveitam `latao-oxidado/`).
- Nomeie a pasta com o mesmo slug já usado em `Design/Criativo/` quando existir (pessoa/cidade); para temas sem entrada lá (material, mood, anatomia), use um slug descritivo curto.

## Regra de fontes (obrigatória)

Toda imagem depositada aqui precisa de uma linha correspondente em `fontes.md` da sua pasta:

```md
## {nome-do-arquivo}
- Fonte: {URL, banco de imagens licenciado, hemeroteca/museu/acervo, foto própria, etc.}
- O que é: {foto real | ilustração de época | pintura | referência de material/textura | referência de anatomia/pose | etc.}
- Data/período: {se conhecido/aplicável}
- Uso pretendido: {embasamento visual do prompt — não é material de treino/dataset}
```

Sem fonte citada, a imagem não deve ficar na pasta — mesma régua já aplicada pelo `@computador` para lendas/folclore ("nunca inventa, toda referência tem fonte citada"). Vale também pra referência não-histórica: se é banco de imagem licenciado, dizer qual e a licença; se é foto própria, dizer isso.

## Regra legal e de uso

- **Só embasamento visual por enquanto** — quem escreve o prompt olha a referência e traduz em texto mais preciso. Não está plugado em img2img/IP-Adapter ainda (decisão de 2026-07-24; revisar quando o pipeline por imagem for testado ponta a ponta).
- Continua valendo `pipeline-ia-sprites.md#regra-legal-e-criativa`: sem nome de artista vivo como atalho de estilo, sem sprite de jogo comercial como dataset. Referência real (foto de pessoa, material, lugar) é diferente disso — é fidelidade de fato/material, não atalho de estilo de terceiro.
- Não redistribuir/publicar essas referências fora do repositório de trabalho do projeto.

## Quando usar

No Passo 1 (brief) ou no Passo 2 do fluxo geral (`pipeline-sprites-programaticos.md`), antes de escrever o prompt de concept art: verificar se já existe pasta útil aqui pro tema do asset (pessoa/lugar real, material, mood, anatomia de referência). Se fizer sentido buscar mais e não existir, buscar (via `@computador`, skill `hemeroteca-blumenau`, banco de imagem licenciado, ou pesquisa direta) e depositar antes de seguir. Não é obrigatório pra todo asset — props simples com material já bem descrito no `palette-guide.md`/`style-bible.md` podem não precisar. Se buscar e não encontrar nada útil, registrar isso em `fontes.md` mesmo assim ("buscado em {data}, nada encontrado") em vez de simplesmente pular, para não repetir a busca do zero depois.

## Pastas existentes

| Pasta | Tema | Status |
|-------|------|--------|
| [`edith-gaertner/`](edith-gaertner/fontes.md) | NPC Edith Gaertner (pessoa real, 1882–1967, Blumenau) | 7 referências depositadas (figura histórica, tratamento espectral, local real — Cemitério dos Gatos) |
