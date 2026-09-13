# Bench de modelo Claude na autoria de spec JSON — 2026-09-03

> Pergunta que este bench responde: **o `@SpriteArtist` deve rodar em qual modelo?**
> Ele estava em `sonnet` por escolha default, nunca medida.

## Método

Tarefa idêntica para os três modelos, executada pelo próprio agente `@SpriteArtist` com
override de modelo — a intenção era medir a configuração real do projeto, não um agente
genérico.

**Tarefa:** autorar um frame de **ataque** do Autômato Abandonado como spec JSON 64×64,
ancorado em `enm_automato_idle_f1.2x.spec.json`, validado por `palette_check.py`.
Escolhida por já estar listada como pendência no context pack ("animações de patrol/attack
quando o design definir o comportamento") e por **não existir spec prévia** — autoria fria.

Saídas em `IA/Outputs/bench-spec-automato/{modelo}/`. Comparação em `comparacao.png` (6×)
e `comparacao_1x.png` (densidade real).

## Resultado bruto

| Modelo | palette_check | Cores | px preenchidos | Iterações | Tool uses | Tokens | Tempo |
|--------|---------------|-------|----------------|-----------|-----------|--------|-------|
| sonnet | APROVADO | 10/32 | 1162 | 1 | 18 | 58,6k | 5,8 min |
| **opus** | APROVADO | 11/32 | 1298 | **5** | 29 | 109,3k | 18,4 min |
| fable | APROVADO | 11/32 | 1167 | 1 | 13 | 51,9k | 4,9 min |

Todas as specs verificadas de forma independente (64 linhas × 64 chars, caminho de paleta
resolvendo, PNG RGBA válido) — não por auto-relato dos agentes.

## O que o número não mostra

**O gate objetivo não discriminou.** Os três aprovaram no `palette_check`, dois deles de
primeira. Se o critério fosse só o gate, o veredito seria "use o mais barato".

**A leitura em 1× discriminou, e com folga.** Critério da própria `style-bible`
("silhueta reconhecível só pela forma, em 1x"):

- **sonnet** e **fable** interpretaram a tarefa como *editar o idle*: mantiveram torso,
  cabeça e pernas idênticos e estenderam um braço. Em 1× lê como "o robô parado com uma
  haste saindo do ombro" — o corpo está inerte, não há ataque.
- **opus** interpretou como *desenhar um ataque*: torso inclinado à frente, pernas em
  afundo com calcanhar erguido, braço traseiro em contrapeso, massa do punho elevada. Em
  1× a silhueta **sozinha** comunica a ação.

As 5 iterações do opus não foram desperdício: foram ele criticando o próprio resultado
contra a leitura em 1× e refazendo — que é literalmente o ciclo
gerar→visualizar→criticar→refinar do pipeline. Os outros dois pararam na primeira porque
o `palette_check` aprovou.

**Defeito do opus:** quebrou continuidade com o idle — redesenhou a engrenagem do peito
(virou radial laranja em vez do painel retangular vermelho), a cabeça e a silhueta do
torso. Como frame que intercala com o idle, isso "estala". É corrigível e não anula o
resultado, mas precisa de passe manual antes de virar asset.

**Ruído do próprio bench:** o prompt pedia "braço estendido à frente" sem dizer o que o
outro braço faz. Sonnet apagou o braço esquerdo; fable deixou um toco apontando para fora.
Isso é falha do enunciado, não dos modelos — não pesou no veredito.

## Veredito

**Promover o `@SpriteArtist` para `model: opus`.**

O custo é real — ~2× tokens e ~3× tempo do sonnet — mas o produto é a única das três
saídas que cumpre o critério declarado do projeto. E o gasto extra veio de iterar contra a
crítica visual, que é exatamente o trabalho que se quer desse agente.

**Fable 5 não se justifica aqui.** Custa o dobro do Opus por token e entregou o mesmo
padrão do sonnet: uma iteração, silhueta inerte. Nesta tarefa ele não usou a capacidade
extra que o preço cobra.

## Ressalva

Um asset, um prompt, uma execução por modelo. Não é significância estatística — é um
indício forte num caso representativo. Se um segundo bench contradisser, o segundo vale.
