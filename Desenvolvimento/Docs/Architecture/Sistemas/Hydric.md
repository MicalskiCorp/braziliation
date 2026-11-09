# Sistema: Hydric

> **Responsabilidade:** Estado global do rio Itajaí-Açu em Blumenau: Rotina, Alerta, Cheia e Saturação, e as regras de mundo que saem dele.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `HydricState.cs` | `src/Braziliation.Game.Core/Hydric/HydricState.cs` | Enum dos 4 estados (valores persistíveis) e `HydricStateRules` (ex.: `LocksFloodgates`, Cheia e Saturação) |
| `HydricStateManager.cs` | `src/Braziliation.Game.Core/Hydric/HydricStateManager.cs` | Serviço com o estado atual, `SetState` (eventos de campanha) e o evento `StateChanged` (anterior, novo) |

Testes: `HydricStateManagerTests.cs`.

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| Sistema Hídrico de Blumenau | [`Blumenau-SistemaHidrico.md`](../../GDD/Features/Blumenau-SistemaHidrico.md) | Implementa os 4 estados e o evento de mudança |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Core](Core.md) | `GameServiceLocator.cs` | Registra um `HydricStateManager` no `BuildServices`; o locator dura entre cenas |
| [Gameplay](Gameplay.md) | `FloodgateController.cs` | Assina `StateChanged` no `Start` e chama `SetLocked(LocksFloodgates())` |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| Estado inicial | `HydricState` | `Routine` | Construtor do `HydricStateManager`; quando o rio entrar no save, vem dele |

## Notas de Design

- **Serviço, não singleton estático.** A feature falava em singleton; o core não guarda estado estático, então o rio é uma instância registrada no `GameServiceLocator`.
- **O jogador não muda o estado.** Quem chama `SetState` são os eventos de campanha. Qualquer estado pode seguir qualquer outro, porque um evento pode forçar um salto (o clero abrindo comportas).
- Quem reage ao rio assina `StateChanged` e lê `Current` ao se inscrever; `SetState` com o estado atual não notifica.
- Regra de mundo por estado é função pura em `HydricStateRules`, testada no core. O MonoBehaviour só aplica.
- Falta, pela feature: a tabela de acessibilidade área × estado, passarelas, docas, sinos e marcadores. O estado do rio ainda não entra no save.
