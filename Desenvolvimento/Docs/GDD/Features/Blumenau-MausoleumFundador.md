# Blumenau — Mausoléu do Fundador

> **Tipo:** Feature — Área + Culto Político + Catacumba de Arquivo
> **Status:** 📋 Planejado
> **Sistema(s) envolvido(s):** Exploração, Diálogo/NPC, Sistema Hídrico
> **Prioridade:** Média
> **Referência criativa:** [`Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`](../../../../../Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md)

---

## Descrição

O Mausoléu do Fundador é um templo cívico de legitimação política: não preserva apenas um corpo, mas uma versão **autorizada** de Blumenau. Superfície solene e policiada; catacumba inferior com o arquivo fechado das famílias dominantes — livros de linhagem adulterados, decretos de posse e a história oficial reescrita após as enchentes. Contraste narrativo direto com o Jardim de Edith.

---

## Mapa / Área

- **Tipo de espaço:** Exterior monumental (praça cerimonial) + interior do mausoléu + catacumba inferior (arquivo)
- **Atmosfera superfície:** Solene, cerimonial, policiado — quase templo cívico. Peregrinos deixam engrenagens, medalhas e nomes de família aos pés da pedra
- **Atmosfera catacumba:** Arquivo fechado, claustrofóbico, silêncio de poder escondido

### Layout de Referência

```
[Via Processional] ← peregrinos e patrulhas
        ↓
[Praça Cerimonial] → [Altar/Pedra do Fundador] (oferendas: engrenagens, medalhas)
        ↓
[Interior do Mausoléu — câmara principal]
  → [Vitrine de relíquias do fundador]
  → [Painel de genealogia oficial]
        ↓
[Acesso selado à Catacumba] (requer autorização ou key item)
        ↓
[Catacumba — Nível 1: livros de linhagem e brasões das famílias]
        ↓
[Catacumba — Nível 2: arquivo de decretos e registros adulterados]
  → [Câmara oculta: documentos que contradizem a narrativa oficial]
```

---

## Mecânicas Envolvidas

### Culto Político — Superfície
- **Peregrinação:** NPCs civis deixam oferendas regularmente — mecânica de observação social
- **Patrulha clerical:** soldados cléricos controlam quem se aproxima do altar e podem questionar o jogador
- **Rituais encenados:** cerimônias periódicas onde o alto clero reafirma a narrativa oficial do fundador como legitimação do poder atual
- **Disfarce:** o jogador pode se misturar aos peregrinos para acessar áreas internas sem confronto

### Catacumba — Arquivo das Famílias Dominantes
- **Conteúdo:** livros de linhagem, retratos adulterados, decretos de posse, brasões e documentos que reescrevem a cidade após enchentes, censura e reorganizações de poder
- **Mecânica de lore:** cada seção da catacumba revela uma família diferente e seu papel na reescrita da história
- **Contradições:** documentos na câmara oculta contradizem diretamente os painéis da superfície — o jogador pode coletar provas

### Impacto do Sistema Hídrico
- **Cota de Cheia:** catacumba Nível 1 parcialmente alagada — alguns documentos danificados; perigos de água
- **Cota de Saturação:** subida da água expõe a câmara oculta pelo refluxo — documentos que normalmente estão selados ficam acessíveis

### Contraste com o Jardim de Edith
- **Ritmo intencional:** ao transitar entre os dois espaços, a mudança deve ser sentida: do mármore seco e monumental do Mausoléu para a vegetação úmida e íntima do Jardim
- **Significado:** o fundador tem pedra, rito e culto público; Edith tem silêncio, vegetação e memória afetiva — e é mais viva que o mármore

---

## Personagens / NPCs

### Guardião Vogt *(patrulheiro de elite)*
- Clérico de alta patente responsável pela segurança do Mausoléu
- Não é um boss — é um NPC de obstáculo que pode ser contornado por disfarce, suborno ou combate
- Conhece o conteúdo real da catacumba e tem interesse em mantê-la selada

### Peregrinos *(NPCs ambiente)*
- Civis que visitam regularmente para deixar oferendas
- Alguns podem ser abordados para lore sobre a história "oficial" da cidade
- Um peregrino específico pode dar pista sobre a câmara oculta — alguém que encontrou o acesso por acidente

### Archivista Morto-Vivo *(inimigo — catacumba profunda)*
- NPC que foi "declarado morto" pelo clero e enterrado na catacumba como guardião involuntário do arquivo
- Comportamento: patrulha metodicamente as seções de documentos; ataca qualquer um que tente retirar material do arquivo
- **Conexão com Hermann:** pode ser um dos "declarados mortos" da lista de Hermann

---

## Itens / Relíquias

| Item | Tipo | Como Obter | Efeito |
|------|------|-----------|--------|
| Chave da Catacumba do Mausoléu | Key Item | Suborno ou roubo do Guardião Vogt | Abre o acesso selado à catacumba |
| Livro de Linhagem — Família Blumenau | Lore / Key Item | Catacumba Nível 1 | Revela genealogia real vs. genealogia oficial |
| Decreto de Reescrita Pós-Enchente | Lore / Key Item | Catacumba Nível 2 | Prova de adulteração histórica — uso em confronto com o Arcebispo na Matriz |
| Engrenagem de Bronze (oferenda) | Material | Coletada das oferendas no altar | Componente de crafting clockpunk |
| Medalhão do Fundador *(réplica)* | Relíquia *(opcional)* | Câmara oculta, cota de saturação | Permite acesso a diálogos específicos sobre a fundação da cidade |

---

## Dependências

| Feature / Sistema | Tipo | Arquivo |
|-------------------|------|---------|
| Sistema Hídrico de Blumenau | Usa — cota de Cheia/Saturação altera acesso e expõe documentos | [Blumenau-SistemaHidrico.md](Blumenau-SistemaHidrico.md) |
| Jardim de Edith | Lore cruzado — contraste narrativo direto (oficial vs. íntimo) | [Blumenau-JardimEdith.md](Blumenau-JardimEdith.md) |
| Igreja Luterana (Hermann) | Lore cruzado — Archivista pode ser "declarado morto" da lista de Hermann | [Blumenau-IgrejaLuterana.md](Blumenau-IgrejaLuterana.md) |
| Igreja Matriz | Usa — Decreto de Reescrita pode ser usado no confronto com Arcebispo | [Blumenau-IgrejaMatriz.md](Blumenau-IgrejaMatriz.md) |

---

## Critérios de Aceitação

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Peregrinos realizam oferendas regularmente (sistema de ambiente) | Sim |
| 2 | Catacumba inacessível sem a Chave correta | Sim |
| 3 | Catacumba Nível 1 parcialmente alagada em cota de Cheia | Sim |
| 4 | Câmara oculta acessível apenas em cota de Saturação | Sim |
| 5 | Decreto de Reescrita desbloqueável como prova para confronto na Igreja Matriz | Sim |
| 6 | Archivista Morto-Vivo patrulha e protege documentos da catacumba profunda | Sim |
| 7 | Contraste visual/sonoro perceptível ao transitar entre Mausoléu e Jardim de Edith | Sim |

---

## TODOs de Implementação

### `@GameplayEngineer`
| Tarefa | Prioridade |
|--------|-----------|
| Implementar mecânica de disfarce entre peregrinos para acesso interno | Alta |
| Implementar NPC Archivista Morto-Vivo com patrulha de documentos | Alta |
| Implementar câmara oculta com trigger de acessibilidade por cota de saturação | Alta |
| Implementar uso do Decreto de Reescrita como prova em diálogo com Arcebispo | Média |

### `@UnityDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Criar cena exterior monumental + praça cerimonial com peregrinos ambiente | Alta |
| Criar cena da catacumba (Nível 1 e 2) com layout de arquivo e seções por família | Alta |
| Implementar variante de inundação parcial para catacumba em cota de Cheia | Média |
| Criar câmara oculta com acesso por refluxo hídrico | Média |

### `@SystemsDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Modelo de estado: catacumba com variantes por cota hídrica | Média |
| Integração com lista de "declarados mortos" do sistema de Hermann | Média |

---

## Histórico

| Data | Alteração |
|------|-----------|
| 2026-05-17 | Criado — handoff do @GameCreative processado pelo @GameArchitect |
