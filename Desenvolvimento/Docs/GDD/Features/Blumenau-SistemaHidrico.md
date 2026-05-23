# Blumenau — Sistema Hídrico de Die Unterwelt

> **Tipo:** Feature — Sistema Global de Estado (afeta todos os mapas de Blumenau)
> **Status:** 📋 Planejado
> **Sistema(s) envolvido(s):** Exploração, Economia, Combate, Progressão de Bosses
> **Prioridade:** Alta
> **Referência criativa:** [`Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md`](../../../../../Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md)

---

## Descrição

O rio Itajaí-Açu é o coração de Die Unterwelt — fonte de energia e ameaça permanente. O sistema hídrico controla **quatro estados do rio** (Rotina, Alerta, Cheia, Saturação) que afetam diretamente a acessibilidade de áreas, o comportamento de NPCs, a disponibilidade de itens e a progressão de eventos em **todos os mapas de Blumenau**.

> ⚠️ Este é o sistema de dependência central de Blumenau. Todas as outras features da cidade o referenciam.

---

## Os Quatro Estados do Rio

| Estado | Nível | Sinal da Cidade | Efeito Global |
|--------|-------|-----------------|---------------|
| **Rotina** | Baixo / Normal | Marcadores verdes nos pilares | Acesso completo a todos os bairros e instalações |
| **Alerta** | Subindo | Sinos e marcadores amarelos | Passarelas elevadas, alguns bairros baixos fechados |
| **Cheia** | Alto | Sirenes pneumáticas, marcadores vermelhos | Bairros baixos inundados, comportas fechadas, docas ativas |
| **Saturação** | Crítico | Sirenes contínuas, colapso parcial | Sistema falha, comportas travam, subterrâneos revelados, lama exposta |

---

## Componentes do Sistema

### Comportas
- Instaladas nos acessos a bairros baixos, túneis, pontes e travessias
- **Rotina:** abertas — livre circulação
- **Alerta:** parcialmente fechadas — acessos restritos, algumas passagens bloqueadas
- **Cheia:** totalmente fechadas — bairros inteiros isolados
- **Saturação:** **travam** — alguns bairros ficam aprisionados entre água represada e refluxo interno

### Passarelas Elevadas
- Ruas, calçadas e plataformas erguidas por trilhos, guinchos e dobradiças
- **Rotina:** ao nível do chão — comércio normal
- **Alerta:** elevando — corredores militares e rotas de fuga da elite ficam acessíveis
- **Cheia:** completamente elevadas — rota padrão entre alguns mapas
- **Saturação:** algumas **colapsam** — rotas cortadas permanentemente até o estado normalizar

### Docas Internas
- Porões de casarões, depósitos e armazéns convertidos em ancoradouros menores
- **Rotina:** inativos (portas fechadas)
- **Alerta:** abrindo para carga preventiva
- **Cheia:** totalmente ativas — rota alternativa de travessia de bairro por barco/jangada
- **Saturação:** caóticas — misturadas com contrabando de emergência e evacuação

### Sistema de Alertas
- **Sinos mecânicos:** vibração audível em qualquer ponto da cidade
- **Sirenes pneumáticas:** alertas de curto e longo alcance
- **Marcadores pintados nos pilares:** cores codificadas (verde / amarelo / vermelho / preto)
- **Sinalizadores em towers:** visíveis no horizonte do mapa

---

## Impacto em Outras Features

| Feature | Cota Rotina | Cota Alerta | Cota Cheia | Cota Saturação |
|---------|-------------|-------------|-----------|----------------|
| **Igreja Luterana** | Acesso completo | Rota norte bloqueada | Cemitério parcialmente alagado | Cripta inundada — Hermann isolado |
| **Igreja Matriz** | Acesso completo | Rua de acesso reduzida | Catacumbas Nível 1 parcialmente alagadas | Câmara do arquivo exposta pelo refluxo |
| **Teatro Carlos Gomes** | Engrenagem 1 disponível | Engrenagem 2 disponível | Engrenagem 3 disponível | Engrenagem 4 disponível |
| **Jardim de Edith** | Acesso pela trilha oculta | Trilha parcialmente obstruída | Acesso via rota alta | Área protegida — enclave seco |
| **Mausoléu do Fundador** | Superfície acessível | Catacumba acessível | Catacumba inundada | Documentos expostos pela subida |
| **Morro do Zendron** | Acesso completo | Escalada dificultada | Bairros base isolados | Deslizamento ativo — acesso bloqueado |

---

## Mecânicas Envolvidas

### Progressão de Estado
- O estado do rio **muda ao longo da narrativa** conforme eventos de campanha em Blumenau
- O jogador não controla os estados — são mudanças diegéticas vinculadas à progressão
- Eventos específicos podem **forçar um estado** (ex: o clero abre comportas deliberadamente para isolar uma área)
- O jogador aprende a ler os alertas e planejar rotas antes das mudanças

### Mecânica de Falha por Saturação
- Em cota de saturação: comportas travam, eixos rompem, passarelas colapsam
- **Revelação:** bairros inteiros expõem subterrâneos, segredos e mortos escondidos
- **Gameplay:** a saturação é o estado de maior risco e maior recompensa em termos de acesso a áreas secretas

### Navegação Alternativa por Estado
- **Cheia:** docas ativas permitem travessias que não existem nos estados normais
- **Saturação:** rotas de superfície colapsam mas rotas subterrâneas (antes cobertas por lama) abrem
- **Memória do mapa:** o jogador vê quais rotas estão acessíveis conforme o estado atual — HUD ou pistas visuais no cenário

### Sinos Submersos (Lore Ambiental)
- Durante a madrugada em cota de cheia/saturação, **sinos submersos tocam**
- Som direcional — indica locais de interesse ocultos sob a água
- Objetos perdidos "retornam" para pontos improváveis após cheias — mecânica de recolha de itens surpresa

---

## Design — Direção de Arte por Estado

| Estado | Visual | Som |
|--------|--------|-----|
| Rotina | Cidade clockpunk operando normalmente, engrenagens girando | Maquinário rítmico, vozes de mercado |
| Alerta | Céu cinza, passarelas subindo lentamente, comércio fechando | Sinos intermitentes, vozes apressadas, sirenes distantes |
| Cheia | Ruas baixas submersas, reflexo d'água em fachadas, barcos | Água correndo, sirenes longas, silêncio de bairro vazio |
| Saturação | Lama nas paredes, comportas trancadas, colapso estrutural visível | Sirenes contínuas, rangidos metálicos, silêncio de abandono |

---

## Dependências

| Feature / Sistema | Tipo | Arquivo |
|-------------------|------|---------|
| Teatro Carlos Gomes | Controlado por — cotas determinam disponibilidade das engrenagens do boss | [Blumenau-TeatroCarlosGomes.md](Blumenau-TeatroCarlosGomes.md) |
| Igreja Luterana | Afeta — rotas e acessibilidade da dungeon | [Blumenau-IgrejaLuterana.md](Blumenau-IgrejaLuterana.md) |
| Igreja Matriz | Afeta — catacumbas e câmara do arquivo | [Blumenau-IgrejaMatriz.md](Blumenau-IgrejaMatriz.md) |
| Jardim de Edith | Afeta — acessibilidade da trilha | [Blumenau-JardimEdith.md](Blumenau-JardimEdith.md) |
| Mausoléu do Fundador | Afeta — catacumba e acesso a documentos | [Blumenau-MausoleumFundador.md](Blumenau-MausoleumFundador.md) |
| Morro do Zendron | Afeta — deslizamento e acesso aos bairros periféricos | [Blumenau-MorroZendron.md](Blumenau-MorroZendron.md) |

---

## Critérios de Aceitação

| # | Critério | Testável? |
|---|----------|-----------|
| 1 | Sistema possui 4 estados discretos com transições controladas pela narrativa | Sim |
| 2 | Cada estado altera o acesso de pelo menos 2 áreas de Blumenau | Sim |
| 3 | Sistema de alertas (sinos, sirenes, marcadores) comunica o estado atual ao jogador | Sim |
| 4 | Docas ativas em estado de Cheia permitem rotas alternativas | Sim |
| 5 | Saturação revela áreas secretas inacessíveis nos outros estados | Sim |
| 6 | Engrenagens do Teatro Carlos Gomes acessíveis nas cotas corretas | Sim |
| 7 | Sinos submersos soam durante a noite em estados de Cheia e Saturação | Sim |

---

## TODOs de Implementação

### `@SystemsDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Modelar `HydricState.cs` — enum com 4 estados (Rotina/Alerta/Cheia/Saturação) e dados de configuração | Alta |
| Modelar `HydricStateManager.cs` — singleton que mantém estado atual e dispara eventos de mudança | Alta |
| Implementar eventos/callbacks que notificam todas as features dependentes ao mudar estado | Alta |
| Modelar tabela de acessibilidade por área × estado (scriptable object ou config) | Alta |

### `@GameplayEngineer`
| Tarefa | Prioridade |
|--------|-----------|
| Implementar comportas com estados aberta/parcial/fechada/travada por `HydricStateManager` | Alta |
| Implementar passarelas elevadas com animação de subida/descida por estado | Alta |
| Implementar docas ativas com rota de barco/jangada em estado de Cheia | Alta |
| Implementar sinos submersos com áudio posicional direcional em Cheia/Saturação | Média |
| Implementar mecânica de item surpresa pós-cheia (objetos que "retornam") | Baixa |

### `@UnityDeveloper`
| Tarefa | Prioridade |
|--------|-----------|
| Criar variantes visuais de Blumenau por estado hídrico (iluminação, nível de água, lama) | Alta |
| Criar sistema de marcadores nos pilares com cor por estado | Média |
| Implementar HUD ou indicador visual de estado atual acessível ao jogador | Média |

---

## Histórico

| Data | Alteração |
|------|-----------|
| 2026-05-17 | Criado — handoff do @GameCreative processado pelo @GameArchitect |
