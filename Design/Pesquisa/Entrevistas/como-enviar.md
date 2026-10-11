# Como Enviar Material de Pesquisa pelo WhatsApp

Protocolo de entrada para quem grava e manda material no grupo dedicado. Cada regra aqui veio de
um problema real da curadoria da visita ao Teatro Carlos Gomes (2026-10-11): seguir o protocolo é
o que permite ligar cada foto ao áudio certo sem adivinhar.

## Assunto: sempre marcar antes de mandar

O material chega picado e intercalado: a benzedeira hoje, um museu amanhã, a benzedeira de novo
no mês que vem. O que mantém cada coisa no seu lugar é o **assunto**:

```
#assunto benzedeira          ← abre: tudo o que chegar depois vai para "benzedeira"
(áudios, fotos, textos…)
#fim                         ← fecha
```

- O nome vira um identificador sem acento (`#assunto Dona Zélia benzedeira` → `dona-zelia-benzedeira`).
  **Use sempre o mesmo nome** para o mesmo assunto: é ele que junta as sessões de datas diferentes.
- Trocar de assunto é só mandar outro `#assunto` — não precisa de `#fim` no meio.
- O listener confirma (`📂 Assunto benzedeira aberto`) e todo aviso de recebimento mostra o
  assunto (`📂 Assunto: benzedeira`). Se aparecer `📂 Sem assunto`, faltou o `#assunto`.
- Esqueceu o `#fim`? Depois de 12 h sem nada chegar, o assunto fecha sozinho — não contamina o
  próximo. Material sem assunto não se perde: vai para a triagem e você confirma o assunto na
  curadoria.

## Antes de começar

1. **`#assunto {nome}` e, em seguida, uma mensagem de texto de contexto:** o que é, onde, quando e
   quem fala. Ex.: `Visita guiada ao Teatro Carlos Gomes, Blumenau, 11/10 — guia do teatro, visita
   pública`. A curadoria usa essa mensagem como contexto da sessão inteira.
2. **Consentimento de terceiros:** se quem fala não é você, peça autorização no começo da
   gravação ("posso usar esse relato na pesquisa do jogo?"). Sem isso, o relato entra anônimo ou
   não entra.

## Durante

| Faça | Por quê |
|---|---|
| **Um áudio por lugar ou por assunto**, começando pelo nome dele ("agora no porão, sob o palco") | O áudio vira um trecho da curadoria; dizer o lugar no começo dispensa deduzir pelo conteúdo |
| **Grave no gravador do celular e mande o arquivo** (ou grave direto no WhatsApp) | O arquivo `.m4a` do gravador traz o horário da gravação — é ele que liga as fotos ao áudio |
| **Mande as fotos como _Documento_, não como _Foto_** (📎 → Documento → escolher da galeria) | Como documento, a foto chega com o nome original da câmera (`20261011_102033.jpg`), que tem o horário. Como foto, o WhatsApp comprime e **apaga o horário** — na visita, 16 fotos tiveram de ser ligadas aos lugares só pelo que mostravam |
| **Vídeo também como Documento** | Mantém o horário e a qualidade para tirar quadros |
| **Fotografe o exterior na chegada e na saída** | Fachada, praça e estátuas viram uma seção própria ("Exterior"), mesmo sem narração |
| **Evite rosto de pessoas** em primeiro plano | Foto com rosto identificável não entra no repositório |

## Depois

1. **Uma mensagem de texto para cada destaque** que você já sabe que importa, citando a foto
   (responda à foto no WhatsApp). Ex.: `essa abertura emparedada no porão vai ser a entrada do
   túnel`. Decisão criativa dita na hora entra no handoff sem depender de memória.
2. **Mande tudo de uma vez se quiser** — o listener confirma o lote numa mensagem só.
3. **`#fim`** fechando a sessão.

## O que acontece com o material

O listener grava cada mensagem em `_inbox/`; o `transcrever.py` transcreve os áudios; a skill
`processar-entrevistas` monta a linha do tempo, a revisão da transcrição, o inventário de assuntos
e o de-para áudio ↔ lugar ↔ fotos, e só então grava a pesquisa. Detalhes em [index.md](index.md).
