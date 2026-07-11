---
name: structure-audit
description: Audita a estrutura do Braziliation em todos os níveis — disco vs. docs (AssetsStructure, GuiasDeArte, índices, AGENTS.md vs. agentes reais nas 2 camadas/2 formatos) — e reporta gaps com plano de correção. Use quando o usuário pedir para auditar/validar estrutura, verificar padrão de pastas ou sincronizar documentação estrutural.
---

# Skill: structure-audit

Valida que o estado real do disco corresponde ao estado documentado. Não corrige nada sem aprovação — o output é um relatório.

## Níveis de auditoria

### 1. Assets Unity
- Comparar `Desenvolvimento/Assets/` (disco) com `Desenvolvimento/Docs/Architecture/Assets/AssetsStructure.md`.
- Detectar: pastas no disco não documentadas; pastas documentadas ausentes; assets em pastas legadas (`Assets/Sprites/`, `Assets/UI/` raiz, `Art/Environment/`); sprites em `Assets/Art/` sem registro em `Docs/Architecture/indices/assets.md`.

### 2. Design
- `Design/ArteFonte/IA/` deve ter `ContextPacks/`, `Outputs/`, `Selected/`, `Rejected/`, `Models/`.
- Todo guia em `Design/GuiasDeArte/` deve estar listado em `GuiasDeArte/index.md` (e vice-versa).
- Paletas JSON em `Design/ArteConceitual/Paletas/` com `"status"` definido.

### 3. Documentação
- Todo arquivo de `Docs/Architecture/` listado em `Architecture/index.md`.
- Links internos dos `index.md` apontam para arquivos existentes (verificar caminhos relativos).

### 4. Ecossistema de agentes
- Tabela do `Braziliation/AGENTS.md` vs. arquivos reais em `Braziliation/.github/agents/` E `Braziliation/.claude/agents/` (2ª camada, 2 formatos).
- Wrappers da 1ª camada na raiz (`.github/agents/` e `.claude/agents/`) apontando para agentes de referência existentes.
- Paridade Copilot↔Claude: mesmo agente presente nos dois formatos, corpo equivalente.

### 5. Skills
- Toda skill em `Braziliation/.claude/skills/` referencia docs canônicos que existem.

## Formato do relatório

```
## Auditoria de Estrutura — {data}
### Resumo: {N} conformes / {N} gaps ({críticos}/{médios}/{baixos})
### Gaps por nível
| Nível | Gap | Severidade | Correção proposta |
### Correções recomendadas (aguardando aprovação)
```

Após aprovação do usuário, aplicar correções e retroalimentar pendências em `Desenvolvimento/Docs/TODO.md`.
