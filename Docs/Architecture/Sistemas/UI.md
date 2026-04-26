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
