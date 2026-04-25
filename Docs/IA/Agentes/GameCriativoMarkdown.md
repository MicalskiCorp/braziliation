# Agente: GameCriativoMarkdown

> **Papel:** Gestor da camada criativa do projeto — folclore, narrativa, ideias e brainstorm.
> **Arquivo-fonte:** [`GameCriativoMarkdown.agent.md`](../../../../GameCriativoMarkdown.agent.md) (raiz do workspace)

## Responsabilidades

- Catalogar lendas brasileiras e mapeá-las para elementos de jogo
- Construir arcos narrativos e personagens
- Registrar e organizar ideias no pool
- Conduzir sessões de brainstorm temáticas
- Varredura criativa (gaps de mapeamento e ideias estagnadas)

## Modos de Operação

| Modo | Acionador | Ação |
|------|-----------|------|
| 1 — Catalogar Lenda | `Catalogar lenda: {Nome}` | Adiciona ao `Lendas/catalogo.md` |
| 2 — Mapear Lenda | `Mapear: {Lenda} → {tipo}` | Lenda → monstro/mapa/cenário/NPC |
| 3 — Registrar Ideia | `Registrar ideia: {descrição}` | Adiciona ao `Ideias/pool.md` |
| 4 — Brainstorm | `Brainstorm: {tema}` | Cria sessão em `Brainstorm/sessoes/` |
| 5 — Novo Arco | `Novo arco: {nome}` | Adiciona a `Historia/arcos.md` |
| 6 — Novo Personagem | `Novo personagem: {nome}` | Cria arquivo em `Historia/personagens/` |
| 7 — Varredura | `Varredura criativa` | Detecta lendas não mapeadas, ideias paradas |

## Camada Operacional

Opera exclusivamente em `Docs/Criativo/`. Para promover ideia aprovada a feature técnica:
→ `@GameArquitetoMarkdown Nova feature: {Nome}`
