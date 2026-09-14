---
name: structure-audit
description: Audita a estrutura do Braziliation em todos os níveis — disco vs. docs (AssetsStructure, GuiasDeArte, índices, AGENTS.md vs. agentes reais nas 2 camadas) — e reporta gaps com plano de correção. Use quando o usuário pedir para auditar/validar estrutura, verificar padrão de pastas ou sincronizar documentação estrutural.
context: fork
agent: agent-architect
---

# Skill: structure-audit

Valida que o estado real do disco corresponde ao estado documentado. Não corrige nada sem aprovação — o output é um relatório.

## Níveis de auditoria

### 1. Assets Unity
- Comparar `Desenvolvimento/Assets/` (disco) com `Desenvolvimento/Docs/Architecture/Assets/AssetsStructure.md`.
- Detectar: pastas no disco não documentadas; pastas documentadas ausentes; assets em pastas legadas (`Assets/Sprites/`, `Assets/UI/` raiz, `Art/Environment/`); sprites em `Assets/Art/` sem registro em `Docs/Architecture/indices/assets.md`.

### 2. Design
- `Design/ArteFonte/IA/` deve ter `ContextPacks/`, `Outputs/`, `Selected/`, `Rejected/`, `Models/`.
- *Já são teste — não conferir à mão:* todo `.md` listado no `index.md` da própria pasta (`DocsConsistencyTests`, roteador completo) e paletas com `"status"` (`ConventionGuardTests`).

### 3. Documentação
- *Já são teste:* links relativos válidos, roteadores completos em `Docs/` e `Design/`, todo `.cs` numa ficha de sistema, feature no índice e no backlog. Aqui fica só o que exige julgamento: o conteúdo de uma ficha ainda descreve o código?

### 4. Ecossistema de agentes
- Cada agente de `.claude/agents/` na tabela do `AGENTS.md`, com `name` = arquivo e `model:` — já é teste (`AgentDefinitionTests`).
- Wrappers da 1ª camada na raiz do workspace (`.claude/agents/`, fora do repositório) apontando para agentes existentes.

### 5. Skills
- Toda skill em `.claude/skills/` referencia docs canônicos que existem e aparece no catálogo de `Desenvolvimento/Docs/Tech/processos.md` (checado pelo `DocsConsistencyTests`).

## Formato do relatório

```
## Auditoria de Estrutura — {data}
### Resumo: {N} conformes / {N} gaps ({críticos}/{médios}/{baixos})
### Gaps por nível
| Nível | Gap | Severidade | Correção proposta |
### Correções recomendadas (aguardando aprovação)
```

Após aprovação do usuário, aplicar correções e retroalimentar pendências em `Desenvolvimento/Docs/TODO.md`.
