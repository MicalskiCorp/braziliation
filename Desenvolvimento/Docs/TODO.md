# TODO — Pendências de Documentação

> Itens pendentes de documentação na camada IA. Atualizar a cada sessão de trabalho.
> **Modelo reativo:** o @GameArchitect lê este arquivo no Passo 0 de cada sessão. Handoffs do @GameCreative chegam na seção abaixo e são processados manualmente pelo usuário acionando @GameArchitect.

---

## Handoffs do @GameCreative

> Itens criativos aprovados aguardando documentação técnica. O @GameArchitect é acionado **manualmente** pelo usuário para processar estes itens.

| Feature/Sistema | Referência Criativa | Prioridade | Status |
|----------------|---------------------|-----------|--------|
| Criar feature: Blumenau — Igreja Luterana Matriz, cemitério histórico e linha de quests do Hermann | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ❌ Não iniciado |
| Criar feature: Blumenau — Igreja Matriz do Centro e horror social de Podres de Ricos | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ❌ Não iniciado |
| Criar feature: Blumenau — Teatro Carlos Gomes como mercado negro e boss Autômato de Engrenagens Esquecidas | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ❌ Não iniciado |
| Criar feature: Blumenau — sistema hídrico com comportas, passarelas, docas e estados de cheia | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ❌ Não iniciado |
| Criar feature: Blumenau — Jardim de Edith, SQ-01 e relíquia Guizo de Edith | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ❌ Não iniciado |
| Criar feature: Blumenau — Mausoléu do Fundador como área de culto político com catacumba inferior | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Média | ❌ Não iniciado |
| Criar feature: Blumenau — Morro do Zendron e mapas periféricos pós-enchente | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Média | ❌ Não iniciado |

---

## Pendências

| Item | Tipo | Prioridade | Observação |
|------|------|-----------|------------|
| Preencher parâmetros configuráveis dos sistemas | Sistemas | Média | Todos os 6 sistemas têm `*(a documentar)*` |
| Documentar cenas Unity | Motor | Média | `Assets/Scenes/` ainda não mapeado |
| Preencher índice de assets | Motor | Baixa | `Docs/Architecture/indices/assets.md` vazio |
| Documentar features do jogo | Features | Alta | Nenhuma feature documentada ainda |
| Mapear pasta `AI/` na estrutura Docs/ | Agentes | Baixa | **Concluído** — AI/ migrada para .github/ e Docs/ |

---

## TODOs de Implementação — Sistema de Crafting

> Gerados pelo `@GameArchitect` em 2026-05-10. Referência: [`Mechanics/Crafting.md`](Mechanics/Crafting.md)
> Acionar cada agente **manualmente** quando pronto para implementar.

### `@SystemsDeveloper` — Modelos C# puros (Crafting)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `ItemComponent.cs` — modelo de componente com tipo de pilar (Mecânico/Místico/Biológico), stats e lore | Alta | ❌ Não iniciado |
| Criar `SlotData.cs` — modelo de slot com tipo aceito, item equipado e estado (vazio/preenchido) | Alta | ❌ Não iniciado |
| Criar `ReceptacleData.cs` — modelo de receptáculo com lista de slots, pilar e nível de expansão | Alta | ❌ Não iniciado |
| Criar `CraftingRecipe.cs` — modelo de receita com lista de componentes e resultado (item + flag de sinergia híbrida) | Alta | ❌ Não iniciado |
| Criar `CraftingService.cs` — resolução de receitas, validação de compatibilidade de slot e detecção de combinações híbridas | Alta | ❌ Não iniciado |

### `@GameplayEngineer` — Mecânicas Unity (Crafting)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar `ReceptacleController.cs` — gerencia slots dos 3 receptáculos, equipa/desequipa componentes | Alta | ❌ Não iniciado |
| Implementar lógica de sorteio 50/50 ao craftar item híbrido + componente de 3º tipo | Alta | ❌ Não iniciado |

### `@UnityDeveloper` — UI e Wiring

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar painel de crafting — visualização dos 3 receptáculos com seus slots e componentes disponíveis | Alta | ❌ Não iniciado |
| Conectar `CraftingService` ao Unity via `GameServiceLocator` | Alta | ❌ Não iniciado |

---

## TODOs de Implementação — Build do Personagem

> Gerados pelo `@GameArchitect` em 2026-05-10. Referência: [`Mechanics/Build.md`](Mechanics/Build.md)
> Acionar cada agente **manualmente** quando pronto para implementar.

### `@SystemsDeveloper` — Modelos C# puros (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `BuildState.cs` — estado atual da build: habilidades ativas, resistências, flags de exploração desbloqueadas | Alta | ❌ Não iniciado |
| Criar `HybridSynergyResolver.cs` — detecta combinações híbridas válidas e retorna efeitos especiais | Média | ❌ Não iniciado |

### `@GameplayEngineer` — Mecânicas Unity (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar `PlayerBuildController.cs` — aplica stats e habilidades ao jogador conforme `BuildState` | Alta | ❌ Não iniciado |
| Implementar expansão de slots via interação com NPC específico (Artesão, Costureira, Alquimista) | Alta | ❌ Não iniciado |
| Implementar totem de troca de itens — permitir substituir item do slot sem custo, retornar item ao inventário | Alta | ❌ Não iniciado |
| Implementar efeitos de exploração por pilar (visão noturna, passagens ocultas, respiração submersa, etc.) | Alta | ❌ Não iniciado |
| Implementar ativação de sinergias híbridas via `HybridSynergyResolver` | Média | ❌ Não iniciado |

### `@UnityDeveloper` — UI e Wiring (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar progressão visual do personagem — atualizar sprite/aparência por estágio de cada receptáculo | Média | ❌ Não iniciado |
| Criar feedback visual de sinergias híbridas desbloqueadas | Média | ❌ Não iniciado |
| Conectar `BuildState` ao Unity via `GameServiceLocator` | Alta | ❌ Não iniciado |

---

## TODOs de Design — Crafting & Build

> Decisões de design pendentes. Não são de implementação — requerem definição pelo usuário ou `@GameCreative` antes de serem passados aos agentes.

| Item | Referência | Responsável | Prioridade | Status |
|------|-----------|------------|-----------|--------|
| Localização exata dos totens no mapa — quantidade, cidades e áreas | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Média | ❌ Não iniciado |
| Parâmetros numéricos de Crafting — slots iniciais/máximos, número de expansões, combinações híbridas únicas | [`Mechanics/Crafting.md`](Mechanics/Crafting.md) | Design | Alta | ❌ Não iniciado |
| Parâmetros numéricos de Build — habilidades máximas por receptáculo, escala de resistências, estágios visuais | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Alta | ❌ Não iniciado |

---

## Concluído

| Item | Data |
|------|------|
| Documentar mecânica principal — Sistema de Crafting (Receptáculos) | 2026-05-10 |
| Documentar mecânica — Build do Personagem (separação de Crafting.md) | 2026-05-10 |
| Bootstrap da estrutura unificada `Docs/` | 2026-04-25 |
| Stubs de 6 sistemas: Core, UI, SaveSystem, Serialization, Settings, Storage | 2026-04-25 |
