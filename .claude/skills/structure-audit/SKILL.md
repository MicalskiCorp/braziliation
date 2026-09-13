---
name: structure-audit
description: Audita a estrutura do Braziliation em todos os níveis — disco vs. docs (AssetsStructure, GuiasDeArte, índices, AGENTS.md vs. agentes reais nas 2 camadas/2 formatos) — e reporta gaps com plano de correção. Use quando o usuário pedir para auditar/validar estrutura, verificar padrão de pastas ou sincronizar documentação estrutural.
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
- Tabela do `AGENTS.md` vs. arquivos reais em `.github/agents/` E `.claude/agents/` (2ª camada, 2 formatos). A lista e a paridade de corpo já são checadas pelo `AgentParityTests`.
- Wrappers da 1ª camada na raiz (`.github/agents/` e `.claude/agents/`) apontando para agentes de referência existentes.
- Paridade Copilot↔Claude: mesmo agente presente nos dois formatos, corpo equivalente.
  > **Cuidado com falso positivo:** os `.agent.md` Copilot mantêm BOM UTF-8 + CRLF de propósito (não tocar); os `.md` Claude não têm BOM e usam LF. Um `diff` bruto entre os dois mostra o arquivo inteiro como diferente por causa disso — sempre normalizar (remover BOM, `\r\n`→`\n`) antes de comparar corpo, senão gera um gap falso.

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
