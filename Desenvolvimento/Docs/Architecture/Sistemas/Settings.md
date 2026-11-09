# Sistema: Settings

> **Responsabilidade:** Configurações persistentes do jogador (áudio, vídeo, controles, etc.).
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `ISettingsStorage.cs` | `src/Braziliation.Game.Core/Settings/ISettingsStorage.cs` | Contrato de armazenamento de configurações |
| `SettingsService.cs` | `src/Braziliation.Game.Core/Settings/SettingsService.cs` | Serviço de leitura e escrita de configurações |
| `GameSettings.cs` | `src/Braziliation.Game.Core/Settings/GameSettings.cs` | Modelo de dados das configurações do jogo: volumes, overrides de binding e estilo de glifo |
| `ControllerFamily.cs` | `src/Braziliation.Game.Core/Settings/ControllerFamily.cs` | `ControllerFamily` (teclado/mouse, Xbox, PlayStation, Switch) e `GlyphRules.Resolve`: glifo pelo dispositivo ativo, preferência manual vencendo no controle |
| `GlyphStyle.cs` | `src/Braziliation.Game.Core/Settings/GlyphStyle.cs` | Família de glifo de controle (`Auto`/`Xbox`/`PlayStation`/`Switch`, ADR-017), gravada como número |

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
| `MasterVolume`, `MusicVolume`, `SfxVolume` | `float` | `1` | Volume em [0, 1]; NaN vira 0 |
| `InputBindingOverrides` | `string` | vazio | JSON opaco do `SaveBindingOverridesAsJson`, aplicado pelo `GameInput` no boot (ADR-017). O core não interpreta; null vira vazio |
| `GlyphStyle` | `GlyphStyle` | `Auto` | Glifo pelo dispositivo ativo (`Auto`) ou família forçada; valor fora do enum vira `Auto` |

## Notas de Design

- Segue o mesmo padrão de interface/adapter que o SaveSystem para desacoplamento do storage físico.
- Campo novo nasce com padrão no próprio modelo: arquivo de settings de uma versão anterior, sem o campo, carrega o padrão e mantém o resto. Valor inválido num campo (enum fora da faixa) é corrigido no setter, para não cair no `catch (JsonException)` do `SettingsService.Load`, que zera tudo.
- `ResetToDefaults` volta **todas** as configurações, inclusive os controles. O restaurar padrão de uma tela só (áudio, controles) não deve chamá-lo.
