# ADR — Decisões de arquitetura do Braziliation

Registro das **decisões significativas de arquitetura e estrutura**, para que trabalho futuro e agentes de IA sigam consistentes. Um arquivo por ADR, com caminho previsível (`ADR/ADR-0NN.md`): sabendo o número, leia direto. ADR novo: skill `novo-adr`.

Formato de cada arquivo (os rótulos ficam em inglês — o `DocsConsistencyTests` e a skill leem `**Status:**`):
- `# ADR-NNN: Título`
- **Date:** AAAA-MM-DD
- **Status:** Proposed | Accepted | Superseded por ADR-NNN
- **Context:** o problema ou a opção que se apresentou
- **Decision:** o que foi escolhido
- **Consequences:** trade-offs e desdobramentos

A coluna Status desta tabela tem de bater com o `**Status:**` do arquivo — o `DocsConsistencyTests` cobra.

| ADR | Título | Status | Data |
|-----|--------|--------|------|
| [ADR-001](ADR-001.md) | Unity 6 + URP 2D + 320×180 @ 16 PPU | Superseded por ADR-004 | — |
| [ADR-002](ADR-002.md) | Input System (com.unity.inputsystem) | Accepted | — |
| [ADR-003](ADR-003.md) | Recommended Assets/Scripts layout | Superseded por ADR-005 | — |
| [ADR-004](ADR-004.md) | Upgrade de resolução para 640×360 (Blasphemous-like) | Superseded por ADR-011 | 2026-07-12 |
| [ADR-005](ADR-005.md) | Layout de `Assets/Scripts/` por domínio | Accepted | 2026-09-02 |
| [ADR-006](ADR-006.md) | Todo input passa por `GameInput` sobre o action map | Accepted | 2026-09-02 |
| [ADR-007](ADR-007.md) | Save versionado com migração explícita | Accepted | 2026-09-02 |
| [ADR-008](ADR-008.md) | Claude Code é o único harness de agentes | Accepted | 2026-09-13 |
| [ADR-009](ADR-009.md) | Captura de entrevistas de pesquisa via WhatsApp (Baileys + Whisper local) | Accepted | 2026-09-14 |
| [ADR-010](ADR-010.md) | CI do Unity desligado — a validação do lado Unity é local e obrigatória | Accepted | 2026-09-20 |
| [ADR-011](ADR-011.md) | Resolução de referência 960×540 @ 48 PPU | Accepted | 2026-09-25 |
| [ADR-012](ADR-012.md) | Central — painel local das filas de trabalho, com parser único dos TODOs | Accepted | 2026-11-03 |
| [ADR-013](ADR-013.md) | Declaração ampla de uso de IA na ficha da Steam | Accepted | 2026-11-03 |
| [ADR-014](ADR-014.md) | LoRA de estilo próprio — gate de dataset antes do treino | Accepted | 2026-11-03 |
| [ADR-015](ADR-015.md) | Economia de tokens nas execuções da Central | Accepted | 2026-11-04 |
| [ADR-016](ADR-016.md) | Motor `pxfx` e pipeline de personagem por esqueleto | Accepted | 2026-11-04 |
| [ADR-017](ADR-017.md) | Controle na Steam por emulação de gamepad, rebind no jogo e glifos próprios | Accepted | 2026-11-09 |
| [ADR-018](ADR-018.md) | Os receptáculos da build vivem no `BuildState` | Accepted | 2026-11-09 |

> Até 2026-11-09 todos os ADRs viviam num arquivo único, o `architecture_decisions.md`. Ele passou do teto de 5 mil tokens do `TokenBudgetTests` e foi dividido. O texto de cada ADR foi preservado; só os links relativos ganharam um `../`.
