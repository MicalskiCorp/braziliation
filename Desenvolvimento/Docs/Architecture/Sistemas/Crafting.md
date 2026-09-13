# Sistema: Crafting

> **Responsabilidade:** Componentes coletáveis, receitas, slots dos três receptáculos e resolução de combinações (incluindo o sorteio de itens híbridos).
> **Status:** 🔨 Em Desenvolvimento — lógica implementada e testada; parâmetros numéricos e catálogo de componentes aguardam design ([`Mechanics/Crafting.md`](../../Mechanics/Crafting.md)).

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `ItemComponent.cs` | `src/Braziliation.Game.Core/Crafting/ItemComponent.cs` | Componente com pilar (Mecânico/Místico/Biológico), stats e lore |
| `SlotData.cs` | `src/Braziliation.Game.Core/Crafting/SlotData.cs` | Slot com tipo aceito e item equipado |
| `ReceptacleData.cs` | `src/Braziliation.Game.Core/Crafting/ReceptacleData.cs` | Receptáculo com slots, pilar e nível de expansão |
| `CraftingRecipe.cs` | `src/Braziliation.Game.Core/Crafting/CraftingRecipe.cs` | Receita: componentes de entrada e resultado |
| `CraftingService.cs` | `src/Braziliation.Game.Core/Crafting/CraftingService.cs` | Resolve receitas, valida compatibilidade e detecta híbridos |
| `ReceptacleController.cs` | `Assets/Scripts/Crafting/ReceptacleController.cs` | Gerencia os slots dos 3 receptáculos no runtime |
| `HybridRollHandler.cs` | `Assets/Scripts/Crafting/HybridRollHandler.cs` | Sorteio 50/50 ao craftar item híbrido |
| `CraftingPanelController.cs` | `Assets/Scripts/UI/CraftingPanelController.cs` | Painel de crafting (UI) |

Testes: `CraftingServiceTests.cs`.

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Core](Core.md) | `GameServiceLocator.cs`, `PlayerInventory.cs` | `CraftingService` registrado no locator; componentes vêm do inventário |

## Notas de Design

- Política de seed do sorteio híbrido (determinístico × aleatório) ainda é pendência de Design+Tech no `TODO.md`.
- `PlayerInventory` ainda é uma lista sem limite nem persistência (`tech_debt.md`).
