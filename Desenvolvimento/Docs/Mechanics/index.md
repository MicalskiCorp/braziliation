# Mechanics — Mecânicas de Gameplay

> **Como** o jogo funciona: regras, números e comportamentos que a implementação segue. É o contrato entre design e código — o `@QAEngineer` usa estas páginas como critério de aceitação.
> Agentes: `@GameplayEngineer` (implementação) · `@GameArchitect` (documentação)

## Conteúdo

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| [Crafting.md](Crafting.md) | Sistema de Crafting — coleta, compatibilidade de slots e expansão via NPC | 🔨 Lógica implementada e testada · números provisórios |
| [Build.md](Build.md) | Build do Personagem — receptáculos, habilidades, progressão visual e exploração | 🔨 Lógica implementada e testada · números provisórios |
| [InimigosIA.md](InimigosIA.md) | IA de Inimigos — motor genérico por perfil, estados, estilos de agressão e como criar um inimigo novo | ✅ Implementado |

> Crafting e Build têm o código em `src/Braziliation.Game.Core/` e nos adaptadores Unity (ver [`Sistemas/`](../Architecture/Sistemas/index.md)); os valores atuais são placeholders até as decisões de design do [`TODO.md`](../TODO.md).

**Ainda não documentadas** (entram quando o GDD definir): controles e moveset, combate (tipos de dano, knockback, invulnerabilidade), regras de mundo (checkpoints, perigos, respawn) e inventário.

---

> Para documentar mecânica: `@GameArchitect Nova mecânica: {Nome}`
> Template: `Desenvolvimento/Docs/Models/ModelMecanica.md`
