# Assuntos das Entrevistas

Assunto é o fio que junta material que chega picado: uma benzedeira visitada várias vezes, um
lugar, uma figura histórica. Cada assunto tem uma página com todas as suas **sessões** (coletas
numa data), os inventários e onde o material vive no projeto. Uma sessão é sempre de um assunto
só — é o que impede que a conversa com a benzedeira se misture com a visita a um museu no mesmo
dia. O teste `InterviewInventoryTests` cobra que todo inventário aponte para um assunto daqui e
que este liste o inventário de volta.

| Assunto | Slug | Sessões | Página |
|---|---|---|---|
| Teatro Carlos Gomes | `teatro-carlos-gomes` | 1 (11/10/2026) | [`teatro-carlos-gomes.md`](teatro-carlos-gomes.md) |

## Assunto novo

1. Escolher o slug (minúsculo, sem acento, hífen): é o que vai no WhatsApp — `#assunto benzedeira`.
2. Criar `{slug}.md` no modelo de [`teatro-carlos-gomes.md`](teatro-carlos-gomes.md): slug,
   estado/cidade, pessoas (com o consentimento), tabela de sessões, onde o material vive.
3. Linha nesta tabela.

Assunto que volta (a benzedeira de novo, um mês depois) **não** ganha página nova: ganha uma
linha na tabela de sessões da página que já existe.
