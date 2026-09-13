# Créditos — Braziliation

Assets de terceiros usados no projeto, com autoria e licença. Esta lista é obrigatória:
qualquer asset que **permaneça** no jogo precisa constar aqui, mesmo quando a licença
dispensa atribuição.

> O código do Braziliation é MIT (ver [`LICENSE`](LICENSE)). Os assets de terceiros
> listados abaixo **não** são cobertos por essa licença — cada um mantém a sua.

---

## Arte

### Gothicvania — Luis Zuno (@ansimuz)

- **Autor:** Luis Zuno — [ansimuz.com](https://ansimuz.com) · [patreon.com/ansimuz](https://www.patreon.com/ansimuz)
- **Licença:** [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) (domínio público — atribuição não exigida, creditamos por reconhecimento)
- **Fontes:**
  - [Gothicvania Patreon's Collection](https://opengameart.org/content/gothicvania-patreons-collection) — OpenGameArt
  - [GothicVania - Church Pack](https://opengameart.org/content/gothicvania-church-pack) — OpenGameArt
- **No projeto:** `Assets/Art/ThirdParty/Gothicvania/`
- **Onde aparece:** cena `Assets/Scenes/DemoGameplay.unity` — jogador, inimigo, chão e fundo
- **Modificações:** upscale ×2 nearest-neighbor, recorte por bbox de união por animação e
  reempacotamento dos spritesheets em células quadradas. Sem alteração de paleta ou de forma.
  Detalhe completo em [`Assets/Art/ThirdParty/Gothicvania/SOURCES.txt`](Assets/Art/ThirdParty/Gothicvania/SOURCES.txt);
  licença original em [`LICENSE-ansimuz.txt`](Assets/Art/ThirdParty/Gothicvania/LICENSE-ansimuz.txt).
- **Status:** ⚠️ **placeholder** — destrava o desenvolvimento de mecânicas enquanto o pipeline
  próprio produz a arte final. Não segue a paleta de Blumenau nem a style-bible. Ao ser
  substituído por arte própria, remover a pasta e esta entrada.

---

## Ferramentas e pacotes

| Item | Autor | Licença | Observação |
|------|-------|---------|------------|
| TextMesh Pro / EmojiOne | Unity Technologies / EmojiOne | ver `Assets/TextMesh Pro/Sprites/EmojiOne Attribution.txt` | Pacote padrão da Unity |

---

## Como adicionar um asset de terceiro

1. Verifique a licença **antes** de baixar. Prefira CC0; CC-BY exige atribuição obrigatória;
   evite CC-BY-NC e "free for non-commercial" (o projeto pretende ser comercial).
2. Instale em `Assets/Art/ThirdParty/{Pacote}/`, com o texto de licença original junto.
3. Crie um `SOURCES.txt` no pacote com URL de origem, licença, procedência arquivo a arquivo
   e as modificações aplicadas.
4. Adicione a entrada aqui, incluindo onde o asset aparece no jogo.
5. Registre em [`Docs/Architecture/indices/assets.md`](Docs/Architecture/indices/assets.md).
