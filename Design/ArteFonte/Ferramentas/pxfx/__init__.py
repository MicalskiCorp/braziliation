"""pxfx — motor de pixel art do Braziliation: efeitos, esqueleto e animação por código.

Port para Python do PixelFX (https://github.com/patch-gg/pixelfx, MIT — ver
LICENSE-pixelfx.txt), decidido no ADR-016. Tudo o que um efeito importa vem daqui,
com os MESMOS nomes do `src/core/index.js` original, para o port de cada efeito ser
tradução direta e o guia de autoria (`GuiasDeArte/vfx-guide.md`) continuar valendo.

Uso a partir de `Design/ArteFonte/Ferramentas/`:

    py -m pxfx.render fire/torch            # folha de contato
    py -m pxfx.check fire/torch             # checagens automáticas
    py -m pxfx.paridade fire/torch          # compara com o JS original

Mapa dos módulos e convenções do port: PORT.md.
"""
from .matematica import *  # noqa: F401,F403
from .matematica import (TAU, Rng, angleTo, bump, call, clamp, dist, ease, fbm, fract, hash, i32, imul,  # noqa: F401
                         invLerp, jsmod, jsround, lerp, loopNoise, noise, noise2, pingpong, rand, remap, rng, seg,
                         smooth, tileFbm, tileNoise, u32, wrap)
from .cor import (BLACK, INK, PAL, PATCH, RAMP, WHITE, alpha, at, blend, blue, fit, green, hex, luma, mix,  # noqa: F401
                  paleta_regional, rampa_regional, ramp, red, rgb, scale, toHex)
from .objeto import Obj, nn, obj  # noqa: F401
from .particulas import burst, cycle, fly, flyV, stream, ParticlesSimples  # noqa: F401
from .formas import bolt, forks, ngon, star, trail  # noqa: F401
from .simulacao import (B, FIRE_RAMP, GRAVITY, P, PF, SMOKE_RAMP, Bits, Blazes, Lights, Particles,  # noqa: F401
                        band, crystal, flare, sparkle)
from .pintor import Painter  # noqa: F401
from .fonte import FONTS, textWidth  # noqa: F401
from .quadro import clearFrame, composite, createFrame, createFx, painterFor, resolveOptions  # noqa: F401
from .ator import DUMMY_PAL, HERO, HERO2, HERO_PAL, actorAlphaOf, drawActor, stockActor  # noqa: F401
from .cenario import BACKDROPS, backdrop  # noqa: F401
from .golpe import chain, shiftHits, shiftKeys  # noqa: F401

__version__ = "0.1.0"
