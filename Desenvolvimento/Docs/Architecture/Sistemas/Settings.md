# Sistema: Settings

> **Responsabilidade:** Configurações persistentes do jogador (áudio, vídeo, controles, etc.).
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `ISettingsStorage.cs` | `src/Braziliation.Game.Core/Settings/ISettingsStorage.cs` | Contrato de armazenamento de configurações |
| `SettingsService.cs` | `src/Braziliation.Game.Core/Settings/SettingsService.cs` | Serviço de leitura e escrita de configurações |
| `GameSettings.cs` | `src/Braziliation.Game.Core/Settings/GameSettings.cs` | Modelo de dados das configurações do jogo |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Storage](Storage.md) | `StorageProviderSettingsAdapter.cs` | Persistência em disco via adapter |
| [UI](UI.md) | `SettingsView.cs` | Apresenta e edita configurações na UI |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar — ex: volume master, fullscreen, etc.)* | — | — | — |

## Notas de Design

- Segue o mesmo padrão de interface/adapter que o SaveSystem para desacoplamento do storage físico.
