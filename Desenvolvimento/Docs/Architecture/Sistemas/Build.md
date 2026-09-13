# Sistema: Build

> **Responsabilidade:** Estado da build do personagem (itens instalados nos receptáculos, habilidades, resistências, flags de exploração) e detecção de sinergias híbridas entre pilares.
> **Status:** 🔨 Em Desenvolvimento — lógica implementada e testada; números e tabela de sinergias são provisórios até as decisões de design ([`Mechanics/Build.md`](../../Mechanics/Build.md)).

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `BuildState.cs` | `src/Braziliation.Game.Core/Build/BuildState.cs` | Estado da build: itens equipados, habilidades, flags de exploração |
| `HybridSynergyResolver.cs` | `src/Braziliation.Game.Core/Build/HybridSynergyResolver.cs` | Detecta combinações de pilares e devolve os efeitos híbridos ativos |
| `BuildServiceBinder.cs` | `Assets/Scripts/Build/BuildServiceBinder.cs` | Registra o estado da build no `GameServiceLocator` |
| `PlayerBuildController.cs` | `Assets/Scripts/Build/PlayerBuildController.cs` | Aplica stats e habilidades ao jogador (`IStatReceiver`) |
| `ExplorationFlagHandler.cs` | `Assets/Scripts/Build/ExplorationFlagHandler.cs` | Liga/desliga objetos de exploração conforme as flags da build |
| `HybridSynergyActivator.cs` | `Assets/Scripts/Build/HybridSynergyActivator.cs` | Ativa efeitos de sinergia no runtime |
| `SlotExpansionHandler.cs` | `Assets/Scripts/Build/SlotExpansionHandler.cs` | Expansão de slots via NPC |
| `ItemSwapTotem.cs` | `Assets/Scripts/Build/ItemSwapTotem.cs` | Totem de troca de itens sem custo |

Testes: `BuildStateTests.cs`, `HybridSynergyResolverTests.cs`.

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Crafting](Crafting.md) | `ItemComponent.cs` | Itens instalados vêm do crafting e carregam o pilar |
| [Core](Core.md) | `GameServiceLocator.cs` | Resolução do estado da build no runtime |

## Notas de Design

- `Braziliation.Build` existe nas duas camadas (ADR-005): lógica pura em `src/`, adaptadores Unity em `Assets/Scripts/Build/`. Nomes de tipo não podem colidir.
- A pasta chama `Build/` e é código — a regra de ignore de player build é ancorada em `/Desenvolvimento/Build/`.
- O efeito `"PrótesisViva"` tem erro de grafia registrado em `tech_debt.md`; renomear antes de o identificador entrar no save.
