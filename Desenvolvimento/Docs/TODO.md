# TODO — Pendências de Documentação

> Itens pendentes de documentação na camada IA. Atualizar a cada sessão de trabalho.
> **Modelo reativo:** o @GameArchitect lê este arquivo no Passo 0 de cada sessão. Handoffs do @GameCreative chegam na seção abaixo e são processados manualmente pelo usuário acionando @GameArchitect.

---

## Handoffs do @GameCreative

> Itens criativos aprovados aguardando documentação técnica. O @GameArchitect é acionado **manualmente** pelo usuário para processar estes itens.

| Feature/Sistema | Referência Criativa | Prioridade | Status |
|----------------|---------------------|-----------|--------|
| Criar feature: Blumenau — Igreja Luterana Matriz, cemitério histórico e linha de quests do Hermann | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ✅ Concluído |
| Criar feature: Blumenau — Igreja Matriz do Centro e horror social de Podres de Ricos | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ✅ Concluído |
| Criar feature: Blumenau — Teatro Carlos Gomes como mercado negro e boss Autômato de Engrenagens Esquecidas | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ✅ Concluído |
| Criar feature: Blumenau — sistema hídrico com comportas, passarelas, docas e estados de cheia | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ✅ Concluído |
| Criar feature: Blumenau — Jardim de Edith, SQ-01 e relíquia Guizo de Edith | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Alta | ✅ Concluído |
| Criar feature: Blumenau — Mausoléu do Fundador como área de culto político com catacumba inferior | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Média | ✅ Concluído |
| Criar feature: Blumenau — Morro do Zendron e mapas periféricos pós-enchente | Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md | Média | ✅ Concluído |

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
| Criar `ItemComponent.cs` — modelo de componente com tipo de pilar (Mecânico/Místico/Biológico), stats e lore | Alta | ✅ Concluído |
| Criar `SlotData.cs` — modelo de slot com tipo aceito, item equipado e estado (vazio/preenchido) | Alta | ✅ Concluído |
| Criar `ReceptacleData.cs` — modelo de receptáculo com lista de slots, pilar e nível de expansão | Alta | ✅ Concluído |
| Criar `CraftingRecipe.cs` — modelo de receita com lista de componentes e resultado (item + flag de sinergia híbrida) | Alta | ✅ Concluído |
| Criar `CraftingService.cs` — resolução de receitas, validação de compatibilidade de slot e detecção de combinações híbridas | Alta | ✅ Concluído |

### `@GameplayEngineer` — Mecânicas Unity (Crafting)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar `ReceptacleController.cs` — gerencia slots dos 3 receptáculos, equipa/desequipa componentes | Alta | ✅ Concluído |
| Implementar lógica de sorteio 50/50 ao craftar item híbrido + componente de 3º tipo | Alta | ✅ Concluído |

### `@UnityDeveloper` — UI e Wiring

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar painel de crafting — visualização dos 3 receptáculos com seus slots e componentes disponíveis | Alta | ✅ Concluído |
| Conectar `CraftingService` ao Unity via `GameServiceLocator` | Alta | ✅ Concluído |

---

## TODOs de Implementação — Build do Personagem

> Gerados pelo `@GameArchitect` em 2026-05-10. Referência: [`Mechanics/Build.md`](Mechanics/Build.md)
> Concluído em 2026-05-17 via sessão de orquestração swarm.

### `@SystemsDeveloper` — Modelos C# puros (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `BuildState.cs` — estado atual da build: habilidades ativas, resistências, flags de exploração desbloqueadas | Alta | ✅ Concluído |
| Criar `HybridSynergyResolver.cs` — detecta combinações híbridas válidas e retorna efeitos especiais | Média | ✅ Concluído |

### `@GameplayEngineer` — Mecânicas Unity (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar `PlayerBuildController.cs` — aplica stats e habilidades ao jogador conforme `BuildState` | Alta | ✅ Concluído |
| Implementar expansão de slots via interação com NPC específico (Artesão, Costureira, Alquimista) | Alta | ✅ Concluído |
| Implementar totem de troca de itens — permitir substituir item do slot sem custo, retornar item ao inventário | Alta | ✅ Concluído |
| Implementar efeitos de exploração por pilar (visão noturna, passagens ocultas, respiração submersa, etc.) | Alta | ✅ Concluído |
| Implementar ativação de sinergias híbridas via `HybridSynergyResolver` | Média | ✅ Concluído |

### `@UnityDeveloper` — UI e Wiring (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Implementar progressão visual do personagem — atualizar sprite/aparência por estágio de cada receptáculo | Média | ✅ Concluído |
| Criar feedback visual de sinergias híbridas desbloqueadas | Média | ✅ Concluído |
| Conectar `BuildState` ao Unity via `GameServiceLocator` | Alta | ✅ Concluído |

---

## TODOs de Design — Crafting & Build

> Decisões de design pendentes. Não são de implementação — requerem definição pelo usuário ou `@GameCreative` antes de serem passados aos agentes.

| Item | Referência | Responsável | Prioridade | Status |
|------|-----------|------------|-----------|--------|
| Localização exata dos totens no mapa — quantidade, cidades e áreas | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Média | ❌ Não iniciado |
| Parâmetros numéricos de Crafting — slots iniciais/máximos, número de expansões, combinações híbridas únicas | [`Mechanics/Crafting.md`](Mechanics/Crafting.md) | Design | Alta | ❌ Não iniciado |
| Parâmetros numéricos de Build — habilidades máximas por receptáculo, escala de resistências, estágios visuais | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Alta | ❌ Não iniciado |

---

---

## TODOs de Testes — Cobertura Faltante

> Identificados pela auditoria de 2026-05-23. Acionar `@TestEngineer` para implementar.

### `@TestEngineer` — Testes ausentes no `src/` (Build)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `BuildStateTests.cs` — testar `GetEquippedItems()`, `HasAbility()`, `UnlockedExplorationFlags` | Alta | ✅ Concluído |
| Criar `HybridSynergyResolverTests.cs` — testar `HasHybridSynergy()`, `GetActiveHybridEffects()`, chave simétrica, tabela vazia | Alta | ✅ Concluído |

### `@TestEngineer` — Sincronização CI (`dotnet-tests/`)

> Os testes abaixo existem apenas em `Tests/Braziliation.Game.Tests/` e **não rodam no CI** (`Braziliation.CI.slnx` usa `dotnet-tests/`).

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Copiar/vincular `CraftingServiceTests.cs` para `dotnet-tests/Braziliation.Game.Tests/` | Alta | ℹ️ N/A — CI usa `Tests/` diretamente via `Braziliation.CI.slnx` |
| Copiar/vincular `SettingsServiceTests.cs` para `dotnet-tests/Braziliation.Game.Tests/` | Alta | ℹ️ N/A — CI usa `Tests/` diretamente via `Braziliation.CI.slnx` |
| Verificar se `Braziliation.CI.slnx` inclui o projeto `src/Braziliation.Game.Core/Build/` | Alta | ✅ Confirmado — CI aponta para `Tests/Braziliation.Game.Tests/` que já referencia `Braziliation.Game.Core` |

---

## TODOs de Implementação — Primeira Demo (Foundation)

> Identificados pela auditoria de 2026-05-23 como requisitos bloqueadores da primeira demo jogável.
> Referência: `Desenvolvimento/Docs/Roadmap/roadmap.md` — fase Foundation.

### `@GameplayEngineer` — Jogador (Player)

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `PlayerController.cs` — movimentação básica: andar, pular, colisão com tilemap | Alta | ❌ Não iniciado |
| Implementar `IStatReceiver` em `PlayerController` — receber stats da build via `PlayerBuildController` | Alta | ❌ Não iniciado |
| Criar sistema de interação — jogador usa `IInteractable.Interact()` ao pressionar botão próximo a objeto | Alta | ❌ Não iniciado |

### `@GameplayEngineer` — Combate Básico

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Criar `HealthComponent.cs` — vida, dano, morte (C# puro ou MonoBehaviour) | Alta | ❌ Não iniciado |
| Criar `PlayerCombat.cs` — ataque básico com uma arma (tipo a definir com design) | Alta | ❌ Não iniciado |
| Criar `EnemyController.cs` — inimigo básico: patrulha, detecta jogador, causa dano | Alta | ❌ Não iniciado |

### `@UnityDeveloper` — Nível Jogável

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Montar primeira cena jogável com blockout de tilemap + plataformas + colisores | Alta | ❌ Não iniciado |
| Criar `BootstrapScene` com `GameServiceLocator` + `BuildServiceBinder` configurados | Alta | ❌ Não iniciado |
| Criar HUD básico — barra de vida, indicador de build ativa | Média | ❌ Não iniciado |

### `@SystemsDeveloper` — Completar integrações pendentes

| Tarefa | Prioridade | Status |
|--------|-----------|--------|
| Completar registro de `CraftingService` no `GameServiceLocator` (flag `initializeCraftingService` existe mas wiring estava comentado) | Alta | ✅ Concluído |
| Conectar `ReceptacleController` e `HybridRollHandler` via `GameServiceLocator` | Alta | ✅ Concluído |
| Implementar lógica completa de `PlayerInventory` — limites de capacidade, categorias por `PillarType` | Média | ❌ Não iniciado |

---

## TODOs de Design — Bloqueadores de Implementação (Build)

> Decisões de design que bloqueiam a finalização funcional do sistema de Build.

| Item | Referência | Responsável | Prioridade | Status |
|------|-----------|------------|-----------|--------|
| Definir tabela de sinergias híbridas — `HybridSynergyResolver._hybridEffectTable` está vazia | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Alta | ❌ Não iniciado |
| Definir IDs dos materiais especiais de expansão de slots (Artesão/Costureira/Alquimista) | [`Mechanics/Build.md`](Mechanics/Build.md) | Design | Alta | ❌ Não iniciado |
| Definir implementação concreta das flags de exploração — `ExplorationFlagHandler` tem apenas `Debug.Log` | [`Mechanics/Build.md`](Mechanics/Build.md) | Design+Eng | Média | ❌ Não iniciado |
| Definir arma inicial do jogador (tipo, dano base, animação) para combate básico | GDD | Design | Alta | ❌ Não iniciado |
| Definir inimigo básico da demo — comportamento, vida, dano | GDD | Design | Alta | ❌ Não iniciado |

---

## Concluído

| Item | Data |
|------|------|
| Feature: Blumenau — Igreja Luterana Matriz + cemitério + linha de quests do Hermann | 2026-05-17 |
| `BuildStateTests.cs` — 14 testes cobrindo defaults, GetEquippedItems, HasAbility, flags | 2026-05-23 |
| `HybridSynergyResolverTests.cs` — 11 testes cobrindo simetria, tabela, 3 sinergias, sem duplicatas | 2026-05-23 |
| `HybridSynergyResolver` — tabela populada: PrótesisViva, MutaçãoArcana, ArmaduraEncantada | 2026-05-23 |
| `ExplorationFlagHandler` — substituídos Debug.Log por ativação/desativação de GameObjects via Inspector | 2026-05-23 |
| `ReceptacleController` + `HybridRollHandler` — conectados via `GameServiceLocator.Resolve<CraftingService>()` | 2026-05-23 |
| `PlayerBuildController` — adicionada referência ao `ExplorationFlagHandler`; `OnBuildChanged` chama `SyncFlags` | 2026-05-23 |
| Feature: Blumenau — Igreja Matriz do Centro + horror social *Podres de Ricos* | 2026-05-17 |
| Feature: Blumenau — Teatro Carlos Gomes + mercado negro + boss Autômato de Engrenagens Esquecidas | 2026-05-17 |
| Feature: Blumenau — Sistema Hídrico (comportas, passarelas, docas, 4 estados) | 2026-05-17 |
| Feature: Blumenau — Jardim de Edith + SQ-01 + relíquia Guizo de Edith | 2026-05-17 |
| Feature: Blumenau — Mausoléu do Fundador + catacumba + culto político | 2026-05-17 |
| Feature: Blumenau — Morro do Zendron + mapas periféricos pós-enchente | 2026-05-17 |
| Documentar mecânica principal — Sistema de Crafting (Receptáculos) | 2026-05-10 |
| Documentar mecânica — Build do Personagem (separação de Crafting.md) | 2026-05-10 |
| Bootstrap da estrutura unificada `Docs/` | 2026-04-25 |
| Stubs de 6 sistemas: Core, UI, SaveSystem, Serialization, Settings, Storage | 2026-04-25 |
