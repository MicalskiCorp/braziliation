#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Baixa, prepara e instala os placeholders CC0 do Gothicvania (ansimuz).

Os assets sao PLACEHOLDER: existem para destravar o desenvolvimento de mecanicas
enquanto o pipeline proprio produz a arte final. Ver
`Desenvolvimento/Assets/Art/ThirdParty/Gothicvania/SOURCES.txt` e
`Desenvolvimento/CREDITS.md`.

Preparacao aplicada (ADR-004: 32 PPU, 1 tile = 32px, arte propria ja em 2x):
  - upscale x2 nearest-neighbor;
  - recorte por bbox de uniao POR ANIMACAO (preserva alinhamento entre frames);
  - sheets em celulas quadradas com pivot no centro-inferior, casando com
    `Assets/Editor/Art/SheetAutoSlicer.cs`;
  - .meta com GUID fixo, porque a cena DemoGameplay referencia estes assets.

Uso:
    py prepare_thirdparty_gothicvania.py            # baixa, prepara e instala
    py prepare_thirdparty_gothicvania.py --dry-run  # so prepara, em ./_gothicvania_out
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import shutil
import sys
import urllib.request
import zipfile

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit('Pillow ausente. Rode: py -m pip install pillow')

SCALE = 2
PPU = 32

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', '..'))
ASSETS = os.path.join(REPO, 'Desenvolvimento', 'Assets')
PACK_DIR = os.path.join(ASSETS, 'Art', 'ThirdParty', 'Gothicvania')

PACKS = {
    'church': ('https://opengameart.org/sites/default/files/gothicvania%20church%20files.zip',
               'https://opengameart.org/content/gothicvania-church-pack'),
    'patreon': ('https://opengameart.org/sites/default/files/%20gothicvania%20patreon%20collection.zip',
                'https://opengameart.org/content/gothicvania-patreons-collection'),
}

# GUIDs fixos — a cena referencia estes assets diretamente. NAO alterar.
GUIDS = {
    'Art/ThirdParty': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c50',
    'Art/ThirdParty/Gothicvania': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c51',
    'Art/ThirdParty/Gothicvania/Resources': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c52',
    'Art/ThirdParty/Gothicvania/Resources/Demo': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c53',
    'Art/ThirdParty/Gothicvania/Resources/Demo/Sheets': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c54',
    'Art/ThirdParty/Gothicvania/Environments': 'b7a1c0d2e3f4451a8c9d0e1f2a3b4c56',
    'chr_placeholder_heroi_idle.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b21',
    'enm_placeholder_cao_idle.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b22',
    'env_placeholder_chao_tile.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b23',
    'env_placeholder_fundo_castelo.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b24',
    'chr_placeholder_heroi_idle_sheet.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b25',
    'chr_placeholder_heroi_run_sheet.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b26',
    'enm_placeholder_cao_idle_sheet.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b27',
    'enm_placeholder_cao_walk_sheet.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b28',
    'env_placeholder_castelo_tileset.png': 'c1a2b3d4e5f6401a9b8c7d6e5f4a3b29',
    'LICENSE-ansimuz.txt': 'd1a2b3d4e5f6401a9b8c7d6e5f4a3b31',
}

# nome -> (SpriteAlignment, pivot x, pivot y, spriteMeshType)
# 0=Center, 2=TopCenter, 7=BottomCenter | meshType 0=FullRect (exigido por drawMode Tiled)
PIVOTS = {
    'chr_placeholder_heroi_idle.png': (7, 0.5, 0.0, 1),
    'chr_placeholder_heroi_idle_sheet.png': (7, 0.5, 0.0, 1),
    'chr_placeholder_heroi_run_sheet.png': (7, 0.5, 0.0, 1),
    'enm_placeholder_cao_idle.png': (7, 0.5, 0.0, 1),
    'enm_placeholder_cao_idle_sheet.png': (7, 0.5, 0.0, 1),
    'enm_placeholder_cao_walk_sheet.png': (7, 0.5, 0.0, 1),
    'env_placeholder_chao_tile.png': (2, 0.5, 1.0, 0),
    'env_placeholder_fundo_castelo.png': (0, 0.5, 0.5, 1),
    'env_placeholder_castelo_tileset.png': (0, 0.5, 0.5, 1),
}

DESTINOS = {
    'chr_placeholder_heroi_idle.png': ('Resources', 'Demo'),
    'enm_placeholder_cao_idle.png': ('Resources', 'Demo'),
    'env_placeholder_chao_tile.png': ('Resources', 'Demo'),
    'env_placeholder_fundo_castelo.png': ('Resources', 'Demo'),
    'chr_placeholder_heroi_idle_sheet.png': ('Resources', 'Demo', 'Sheets'),
    'chr_placeholder_heroi_run_sheet.png': ('Resources', 'Demo', 'Sheets'),
    'enm_placeholder_cao_idle_sheet.png': ('Resources', 'Demo', 'Sheets'),
    'enm_placeholder_cao_walk_sheet.png': ('Resources', 'Demo', 'Sheets'),
    'env_placeholder_castelo_tileset.png': ('Environments',),
}


# --------------------------------------------------------------------- download
def fetch(cache_dir: str, key: str) -> zipfile.ZipFile:
    url = PACKS[key][0]
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, key + '.zip')
    if not os.path.exists(path):
        print('  baixando %s...' % key)
        with urllib.request.urlopen(url, timeout=180) as r, open(path, 'wb') as f:
            shutil.copyfileobj(r, f)
    return zipfile.ZipFile(path)


def read_png(zf: zipfile.ZipFile, endswith: str) -> Image.Image:
    for n in zf.namelist():
        if '__MACOSX' not in n and n.endswith(endswith):
            return Image.open(io.BytesIO(zf.read(n))).convert('RGBA')
    raise KeyError(endswith)


# ---------------------------------------------------------------------- imagem
def up(img: Image.Image) -> Image.Image:
    return img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)


def split_and_crop(sheet: Image.Image, count: int) -> list[Image.Image]:
    """Fatia em grade uniforme e recorta todos os frames pela bbox de uniao."""
    assert sheet.width % count == 0, (sheet.width, count)
    fw = sheet.width // count
    frames = [sheet.crop((i * fw, 0, (i + 1) * fw, sheet.height)) for i in range(count)]
    box = None
    for fr in frames:
        b = fr.getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                     max(box[2], b[2]), max(box[3], b[3]))
    return [up(fr.crop(box)) for fr in frames]


def pack_square_sheet(frames: list[Image.Image]) -> Image.Image:
    """Celulas quadradas, personagem ancorado no centro-inferior."""
    cell = max(max(f.width for f in frames), max(f.height for f in frames))
    cell += cell % 2
    sheet = Image.new('RGBA', (cell * len(frames), cell), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.alpha_composite(fr, (i * cell + (cell - fr.width) // 2, cell - fr.height))
    return sheet


def prepare(cache_dir: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    patreon = fetch(cache_dir, 'patreon')
    church = fetch(cache_dir, 'church')

    def emit(img: Image.Image, name: str) -> None:
        img.save(os.path.join(out_dir, name), optimize=True)
        print('  %-40s %sx%s  (%.2f x %.2f un)' % (
            name, img.width, img.height, img.width / PPU, img.height / PPU))

    heroi_idle = split_and_crop(read_png(patreon, 'PNG/gothic-hero-idle.png'), 4)
    emit(pack_square_sheet(heroi_idle), 'chr_placeholder_heroi_idle_sheet.png')
    emit(pack_square_sheet(split_and_crop(read_png(patreon, 'PNG/gothic-hero-run.png'), 12)),
         'chr_placeholder_heroi_run_sheet.png')
    emit(heroi_idle[0], 'chr_placeholder_heroi_idle.png')

    cao_idle = split_and_crop(read_png(patreon, 'PNG/hell-hound-idle.png'), 6)
    emit(pack_square_sheet(cao_idle), 'enm_placeholder_cao_idle_sheet.png')
    emit(pack_square_sheet(split_and_crop(read_png(patreon, 'PNG/hell-hound-walk.png'), 12)),
         'enm_placeholder_cao_walk_sheet.png')
    emit(cao_idle[0], 'enm_placeholder_cao_idle.png')

    tileset = read_png(patreon, 'PNG/old-dark-castle-interior-tileset.png')
    # Topo de plataforma que repete sem costura na horizontal. O recorte comeca em
    # y=154, a primeira linha 100% opaca da peca: comecar no limite da grade (y=144)
    # traria 10px transparentes e o chao desenharia abaixo da superficie do collider.
    emit(up(tileset.crop((432, 154, 448, 186))), 'env_placeholder_chao_tile.png')
    emit(up(tileset), 'env_placeholder_castelo_tileset.png')

    fundo = read_png(patreon, 'PNG/old-dark-castle-interior-background.png')
    emit(up(fundo.crop((0, 0, fundo.width // 2, fundo.height))),
         'env_placeholder_fundo_castelo.png')

    for n in church.namelist():
        if n.endswith('public-license.txt') and '__MACOSX' not in n:
            with open(os.path.join(out_dir, 'LICENSE-ansimuz.txt'), 'w',
                      encoding='utf-8', newline='\n') as f:
                f.write(church.read(n).decode('utf-8', 'replace'))
            break
    return out_dir


# ------------------------------------------------------------------ .meta Unity
FOLDER_META = ('fileFormatVersion: 2\nguid: {guid}\nfolderAsset: yes\n'
               'DefaultImporter:\n  externalObjects: {{}}\n  userData:\n'
               '  assetBundleName:\n  assetBundleVariant:\n')
TEXT_META = ('fileFormatVersion: 2\nguid: {guid}\nTextScriptImporter:\n'
             '  externalObjects: {{}}\n  userData:\n  assetBundleName:\n'
             '  assetBundleVariant:\n')
PLATFORM = """  - serializedVersion: 4
    buildTarget: {target}
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
"""
TEX_META = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: {mesh}
  alignment: {align}
  spritePivot: {{x: {px}, y: {py}}}
  spritePixelsToUnits: 32
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
{platforms}  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customData:
    physicsShape: []
    bones: []
    spriteID: {sprite_id}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""
TARGETS = ['DefaultTexturePlatform', 'Standalone', 'Android', 'WebGL', 'WindowsStoreApps']


def write_text(path: str, text: str) -> None:
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def install(out_dir: str) -> None:
    for rel, guid in GUIDS.items():
        if not rel.startswith('Art/'):
            continue
        folder = os.path.join(ASSETS, rel.replace('/', os.sep))
        os.makedirs(folder, exist_ok=True)
        write_text(folder + '.meta', FOLDER_META.format(guid=guid))

    platforms = ''.join(PLATFORM.format(target=t) for t in TARGETS)
    for name, sub in DESTINOS.items():
        dest_dir = os.path.join(PACK_DIR, *sub)
        shutil.copy2(os.path.join(out_dir, name), os.path.join(dest_dir, name))
        align, px, py, mesh = PIVOTS[name]
        guid = GUIDS[name]
        # mesmo formato que o Unity gera para o spriteID de sprite Single
        sprite_id = hashlib.md5(guid.encode()).hexdigest()[:16] + '0800000000000000'
        write_text(os.path.join(dest_dir, name + '.meta'),
                   TEX_META.format(guid=guid, align=align, px=px, py=py,
                                   mesh=mesh, platforms=platforms, sprite_id=sprite_id))
        print('  instalado %s' % os.path.relpath(os.path.join(dest_dir, name), ASSETS))

    shutil.copy2(os.path.join(out_dir, 'LICENSE-ansimuz.txt'),
                 os.path.join(PACK_DIR, 'LICENSE-ansimuz.txt'))
    write_text(os.path.join(PACK_DIR, 'LICENSE-ansimuz.txt.meta'),
               TEXT_META.format(guid=GUIDS['LICENSE-ansimuz.txt']))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                        help='prepara os PNGs mas nao instala em Assets/')
    parser.add_argument('--cache', default=os.path.join(os.path.dirname(__file__),
                                                        '_gothicvania_cache'),
                        help='pasta de cache dos zips baixados')
    parser.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__),
                                                            '_gothicvania_out'),
                        help='pasta de saida dos PNGs preparados')
    args = parser.parse_args()

    print('preparando (upscale x%d, 32 PPU):' % SCALE)
    out_dir = prepare(args.cache, args.out)

    if args.dry_run:
        print('\ndry-run: nada instalado. PNGs em %s' % out_dir)
        return

    print('\ninstalando em Assets/Art/ThirdParty/Gothicvania:')
    install(out_dir)
    print('\nOK. Abra o Unity para reimportar.')


if __name__ == '__main__':
    main()
