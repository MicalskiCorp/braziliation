# Sistema: UI

> **Responsabilidade:** Telas de menu principal, slots de save e configurações do jogador.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `MenuController.cs` | `Assets/Scripts/UI/MenuController.cs` | Controle de navegação do menu principal |
| `SaveSlotsView.cs` | `Assets/Scripts/UI/SaveSlotsView.cs` | Tela de listagem de slots de save |
| `SaveSlotEntryView.cs` | `Assets/Scripts/UI/SaveSlotEntryView.cs` | Componente visual de um slot individual |
| `SettingsView.cs` | `Assets/Scripts/UI/SettingsView.cs` | Tela de configurações do jogo |
| `SimpleHealthHud.cs` | `Assets/Scripts/UI/SimpleHealthHud.cs` | HUD de vida mínima (OnGUI) usada na demo |
| `CanvasHealthHud.cs` | `Assets/Scripts/UI/CanvasHealthHud.cs` | HUD de vida em Canvas |
| `CraftingPanelController.cs` | `Assets/Scripts/UI/CraftingPanelController.cs` | Painel de crafting (ver [Crafting](Crafting.md)) |
| `BuildProgressionView.cs` | `Assets/Scripts/UI/BuildProgressionView.cs` | Progressão visual da build por receptáculo (ver [Build](Build.md)) |
| `HybridSynergyFeedbackView.cs` | `Assets/Scripts/UI/HybridSynergyFeedbackView.cs` | Feedback de sinergia híbrida ativada |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [SaveSystem](SaveSystem.md) | `SaveSlotsView.cs`, `SaveSlotEntryView.cs` | Exibe e manipula dados dos slots |
| [Settings](Settings.md) | `SettingsView.cs` | Lê e persiste configurações do jogador |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar)* | — | — | — |

## Notas de Design

- As views de UI não devem conter lógica de negócio — apenas apresentação e eventos.
- Toda comunicação com SaveSystem e Settings passa pelos serviços, nunca diretamente pelos arquivos.

### Estado do slot por `SaveLoadStatus` (ADR-007)

Contrato fechado pelo `@TechLead` em 2026-11-05. `SaveSlotsView` carrega cada slot com
`SaveGameService.LoadDetailed` e entrega o `SaveLoadResult` inteiro ao `SaveSlotEntryView.Bind`.
Enquanto a dívida "UI de slots trata `Corrupt`…" constar em [`tech_debt.md`](../../Tech/tech_debt.md),
o código ainda usa `Load`.

| Status | Indicador | Texto | Continuar (`Mode.Load`) | Novo Jogo (`Mode.New`) |
|--------|-----------|-------|-------------------------|------------------------|
| `Ok`, `Migrated` | `filledSlotIndicator` | nome, tempo de jogo e data do `Slot` | selecionável | selecionável (sobrescreve) |
| `Empty` | `emptySlotIndicator` | — | bloqueado | selecionável |
| `Corrupt` | `unavailableSlotIndicator` | "Save danificado." | bloqueado | selecionável: bloquear deixaria o slot inutilizável para sempre, porque não há tela para apagar |
| `FromNewerBuild` | `unavailableSlotIndicator` | "Salvo numa versão mais nova do jogo. Atualize para continuar." | bloqueado | bloqueado: ADR-007, nunca sobrescrever |
| `NoMigrationPath` | `unavailableSlotIndicator` | "Save de uma versão antiga que esta versão não converte." | bloqueado | bloqueado: é bug de release, e o patch com o degrau de migração recupera o save |

- **A regra de seleção vive no core**, não na view: `SaveLoadResult.IsUsable` decide Continuar e
  `SaveLoadResult.CanOverwrite` decide Novo Jogo; o `interactable` do botão só lê um dos dois.
  `CanOverwrite` **lista os status permitidos** (`Empty`, `Ok`, `Migrated`, `Corrupt`), então um
  status novo nasce bloqueado até alguém decidir.
- Os textos são `[SerializeField, TextArea]` no `SaveSlotEntryView`, com o padrão em PT-BR acima,
  até existir localização. `statusLabel` e `unavailableSlotIndicator` são campos novos.
- `SaveSlotsView` registra no log o que o jogador não vê: `LogWarning` para `Corrupt` e
  `FromNewerBuild` (slot e `FoundVersion`), `LogError` para `NoMigrationPath`.
