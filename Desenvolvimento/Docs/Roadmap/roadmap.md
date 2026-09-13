# Roadmap – Braziliation

> Visão por fases. O detalhe de cada pendência vive no [`TODO.md`](../TODO.md). A fase atual está bloqueada por decisões de design (premissa, inimigo base, arma inicial, números de Crafting e Build) — fechar com a skill `fechar-decisao`.
> **Atualizado em 2026-09-13.** Legenda: ✅ feito · 🔨 parcial · ❌ não iniciado.

## Fase: Fundação — ✅ concluída

- ✅ Unity 6 + URP 2D + Pixel Perfect (640×360, 32 PPU — ADR-004)
- ✅ GameInitializer, CameraScaler
- ✅ Input via `GameInput` sobre o action map project-wide (ADR-006)
- ✅ Layout de `Assets/Scripts/` por domínio (ADR-005)
- ✅ Movimento básico (andar, pular) e colisão com layers dedicadas (Ground, Player, Enemy)
- ✅ Combate básico (vida, dano, ataque corpo a corpo)
- ✅ Uma fase jogável de demonstração (`DemoGameplay`, placeholders CC0)
- ✅ Projeto Unity compilando fora do Editor (skill `unity-validar`)

## Fase: Loop de jogo — 🔨 atual

- 🔨 Moveset conforme o GDD — andar, pular e interagir prontos; dash e demais ações dependem do GDD
- 🔨 2–3 tipos de inimigo — motor genérico `EnemyBrain` pronto; falta o inimigo base e os arquétipos de Blumenau
- ❌ Arma inicial — decisão de design pendente
- 🔨 Checkpoints e respawn — `FallRespawn` cobre queda no vazio; checkpoints ainda não existem
- 🔨 UI básica — HUD de vida e menu principal prontos; pausa não existe
- ❌ Primeiro passe de feel (juice, feedback, som) — o projeto ainda não tem áudio

## Fase: Conteúdo e polimento — ❌

- 🔨 Crafting e Build — lógica implementada e testada; números e catálogo de componentes dependem de design
- ❌ Inventário real (hoje é uma lista sem capacidade nem persistência)
- ❌ Áreas de Blumenau — 7 features documentadas no GDD, nenhuma implementada
- ❌ Lore e narrativa dentro do jogo (premissa ainda vazia)
- ❌ Balanceamento e dificuldade
- ❌ Performance e checagens de plataforma

## Fase: Preparação da v1 — 🔨

- ✅ Save versionado com migração explícita (ADR-007)
- 🔨 Opções — `SettingsService` e tela de configurações prontos; rebind de controles e Steam Input pendentes
- 🔨 Pipeline de build — CI .NET ativo; CI do Unity (GameCI) aguardando os secrets de licença
- ✅ Versionamento — `VERSION` e `bundleVersion` sincronizados por `scripts/update_version.ps1`, com teste
- ❌ Créditos e jurídico finais (hoje `CREDITS.md` só lista os placeholders CC0)
- ❌ Fluxo com Pull Requests — entra depois da v1 consolidada; até lá, commits direto no `main`

---

*Atualizar ao fechar uma fase ou quando uma decisão de design mudar a ordem. Detalhe de feature: [`GDD/`](../GDD/).*
