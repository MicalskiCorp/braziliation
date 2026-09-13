# Sistema: Core

> **Responsabilidade:** Inicialização do jogo, service locator global e escala de câmera por resolução.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `GameServiceLocator.cs` | `Assets/Scripts/Core/GameServiceLocator.cs` | Service locator global — registro e resolução de serviços |
| `GameInitializer.cs` | `Assets/Scripts/Core/GameInitializer.cs` | Bootstrap do jogo — ordem de inicialização |
| `CameraScaler.cs` | `Assets/Scripts/Core/CameraScaler.cs` | Adapta a câmera Unity à resolução alvo (pixel-perfect) |
| `GameInput.cs` | `Assets/Scripts/Core/GameInput.cs` | Única porta de leitura de input, sobre o action map project-wide (ADR-006) |
| `GameLayers.cs` | `Assets/Scripts/Core/GameLayers.cs` | Nomes e máscaras das physics layers — nunca índice mágico |
| `IDamageable.cs` | `Assets/Scripts/Core/IDamageable.cs` | Contrato de quem recebe dano |
| `IInteractable.cs` | `Assets/Scripts/Core/IInteractable.cs` | Contrato de objeto com o qual o jogador interage |
| `IStatReceiver.cs` | `Assets/Scripts/Core/IStatReceiver.cs` | Contrato de quem recebe modificadores de atributo da build |
| `PlayerInventory.cs` | `Assets/Scripts/Core/PlayerInventory.cs` | Inventário provisório (lista sem capacidade — ver `tech_debt.md`) |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| *(sem dependências externas)* | — | — |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar)* | — | — | — |

## Notas de Design

- O `GameServiceLocator` é o ponto central de acesso a serviços — evitar dependência direta entre sistemas.
- O `GameInitializer` define a ordem de bootstrap; novos serviços devem ser registrados aqui.
- O `CameraScaler` é essencial para manter a fidelidade pixel-art em diferentes resoluções.
