# Mechanics — Mecânicas de Gameplay

> Regras, parâmetros e comportamentos das mecânicas do Braziliation.
> Agentes: `@GameplayEngineer` (implementação) · `@GameArchitect` (documentação)

## Conteúdo

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| [Crafting.md](Crafting.md) | Sistema de Crafting — coleta, compatibilidade de slots e expansão via NPC | 🔨 Lógica implementada e testada · números provisórios |
| [Build.md](Build.md) | Build do Personagem — receptáculos, habilidades, progressão visual e exploração | 🔨 Lógica implementada e testada · números provisórios |
| [InimigosIA.md](InimigosIA.md) | IA de Inimigos — motor genérico por perfil, estados, estilos de agressão e como criar um inimigo novo | ✅ Implementado |

> Crafting e Build têm o código em `src/Braziliation.Game.Core/` e nos adaptadores Unity (ver [`Sistemas/`](../Architecture/Sistemas/index.md)); os valores atuais são placeholders até as decisões de design do [`TODO.md`](../TODO.md).

---

> Para documentar mecânica: `@GameArchitect Nova mecânica: {Nome}`
> Template: `Desenvolvimento/Docs/Models/ModelMecanica.md`
