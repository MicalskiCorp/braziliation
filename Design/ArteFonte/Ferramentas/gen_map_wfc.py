#!/usr/bin/env python3
"""Gerador de mapas por Wave Function Collapse (Opcao B do pipeline, camada de nivel).

Enquanto `gen_tileset.py` gera os TILES, este script os MONTA em mapa. WFC colapsa
uma grade onde cada celula comeca podendo ser qualquer tile e vai sendo restringida
pelas regras de adjacencia ate sobrar uma possibilidade por celula.

Por que WFC e nao ruido/automato: as regras sao declaradas em termos do que *pode
encostar em que*, entao o resultado nunca produz uma parede flutuando na agua ou uma
viga que nao encosta em nada. E o algoritmo que gera nivel em Bad North, Caves of Qud
e Townscaper.

Dois modos de obter as regras:
  1. Escrever a adjacencia a mao no ruleset JSON.
  2. `--learn exemplo.json` -- derivar adjacencia e pesos de um trecho de mapa que
     voce desenhou. E o modo mais rapido: desenhe uma tela boa, gere mil parecidas.

Saidas (todas ao lado de -o):
  {out}.png            preview composto a partir dos tilesets reais
  {out}.map.json       grade de tiles + variacao por celula -- e isto que o Unity le
  {out}.manifest.json  seed, ruleset, tentativas (registro de reprodutibilidade)

Uso:
  py gen_map_wfc.py rulesets/blumenau-fachada.json --seed 42 -w 24 -H 14 -o ../IA/Outputs/mapa.png
  py gen_map_wfc.py rulesets/blumenau-fachada.json --learn exemplos/fachada.json --seed 7 -o out.png
  py gen_map_wfc.py rulesets/blumenau-fachada.json --seed 42 --pin 3,10=passarela -o out.png

Dependencia: pip install pillow
"""
import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image

# Direcoes e seus opostos. A ordem e fixa para o log ficar estavel.
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


class Contradiction(Exception):
    """Uma celula ficou sem nenhuma possibilidade. Recomeca com outra sequencia."""


# ------------------------------------------------------------------ ruleset

class Ruleset:
    """Tiles, pesos e adjacencia -- o vocabulario e a gramatica do mapa."""

    def __init__(self, data: dict, base_dir: Path):
        self.name = data.get("name", "sem-nome")
        self.base_dir = base_dir
        self.tilesets = data.get("tilesets", {})
        self.constraints = data.get("constraints", {})

        self.ids = [t["id"] for t in data["tiles"]]
        if len(set(self.ids)) != len(self.ids):
            raise ValueError("ids de tile duplicados no ruleset")
        self.index = {tid: i for i, tid in enumerate(self.ids)}
        self.tiles = {t["id"]: t for t in data["tiles"]}
        self.weights = [float(t.get("weight", 1)) for t in data["tiles"]]
        if any(w <= 0 for w in self.weights):
            raise ValueError("peso de tile deve ser > 0")

        self.allowed = self._build_adjacency(data.get("adjacency", {}))

    def _build_adjacency(self, raw: dict) -> dict:
        """Converte a adjacencia declarada em mascaras de bits, ja simetrizada.

        Simetrizar e obrigatorio: se A aceita B a direita mas B nao aceita A a
        esquerda, a propagacao fica inconsistente e o WFC trava em contradicoes
        que parecem aleatorias. Em vez de exigir que quem escreve o ruleset
        mantenha as duas metades em dia, deduzimos a metade que falta.
        """
        pairs = {d: set() for d in DIRS}
        for tile_id, per_dir in raw.items():
            if tile_id not in self.index:
                raise ValueError(f"adjacencia cita tile inexistente: {tile_id}")
            for direction, neighbours in per_dir.items():
                # Chaves com "_" sao anotacoes do autor do ruleset, nao direcoes.
                # Ruleset e documento de design: precisa caber comentario nele.
                if direction.startswith("_"):
                    continue
                if direction not in DIRS:
                    raise ValueError(f"direcao invalida '{direction}' em {tile_id}")
                for other in neighbours:
                    if other not in self.index:
                        raise ValueError(f"adjacencia de {tile_id} cita tile inexistente: {other}")
                    pairs[direction].add((self.index[tile_id], self.index[other]))
                    pairs[OPPOSITE[direction]].add((self.index[other], self.index[tile_id]))

        n = len(self.ids)
        allowed = {d: [0] * n for d in DIRS}
        for direction, entries in pairs.items():
            for a, b in entries:
                allowed[direction][a] |= 1 << b
        return allowed

    def full_mask(self) -> int:
        return (1 << len(self.ids)) - 1

    def orphans(self) -> list:
        """Tiles sem nenhum vizinho possivel em alguma direcao -- travam o mapa."""
        bad = []
        for tid, i in self.index.items():
            for d in DIRS:
                if self.allowed[d][i] == 0:
                    bad.append(f"{tid} nao aceita nada em '{d}'")
        return bad


def learn_adjacency(example: dict, ruleset_data: dict) -> dict:
    """Deriva adjacencia e pesos observando um mapa de exemplo.

    Todo par que aparece encostado no exemplo vira uma adjacencia permitida; a
    frequencia de cada tile vira seu peso. E o modo 'gere mais disto' do WFC.
    """
    grid = example["grid"]
    if not grid or not grid[0]:
        raise ValueError("mapa de exemplo vazio")

    known = {t["id"] for t in ruleset_data["tiles"]}
    seen = {cell for row in grid for cell in row}
    unknown = seen - known
    if unknown:
        raise ValueError(f"exemplo usa tiles fora do ruleset: {sorted(unknown)}")

    counts = {tid: 0 for tid in known}
    adjacency = {tid: {d: set() for d in DIRS} for tid in known}

    height, width = len(grid), len(grid[0])
    for y, row in enumerate(grid):
        if len(row) != width:
            raise ValueError(f"linha {y} do exemplo tem largura diferente das demais")
        for x, cell in enumerate(row):
            counts[cell] += 1
            for direction, (dx, dy) in DIRS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    adjacency[cell][direction].add(grid[ny][nx])

    ruleset_data["adjacency"] = {
        tid: {d: sorted(v) for d, v in per_dir.items() if v}
        for tid, per_dir in adjacency.items()
    }
    for tile in ruleset_data["tiles"]:
        # Peso minimo 1: um tile visto uma vez no exemplo continua possivel,
        # apenas raro. Peso 0 o removeria do vocabulario sem avisar.
        tile["weight"] = max(1, counts[tile["id"]])
    return ruleset_data


# ---------------------------------------------------------------------- WFC

class Wave:
    """A grade de superposicoes. Cada celula e uma mascara de bits de tiles possiveis."""

    def __init__(self, rules: Ruleset, width: int, height: int, rng: random.Random):
        self.rules = rules
        self.w, self.h = width, height
        self.rng = rng
        self.cells = [rules.full_mask()] * (width * height)

    def at(self, x: int, y: int) -> int:
        return self.cells[y * self.w + x]

    def options(self, mask: int) -> list:
        return [i for i in range(len(self.rules.ids)) if mask >> i & 1]

    def constrain(self, x: int, y: int, mask: int) -> bool:
        """Interseca a celula com `mask`. Devolve True se mudou algo."""
        idx = y * self.w + x
        new = self.cells[idx] & mask
        if new == self.cells[idx]:
            return False
        if new == 0:
            raise Contradiction(f"celula ({x},{y}) ficou sem opcoes")
        self.cells[idx] = new
        return True

    def propagate(self, start: tuple) -> None:
        """Empurra as restricoes a partir de uma celula ate a onda estabilizar."""
        stack = [start]
        while stack:
            x, y = stack.pop()
            current = self.at(x, y)
            for direction, (dx, dy) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.w and 0 <= ny < self.h):
                    continue
                # Uniao do que os candidatos desta celula permitem naquela direcao.
                permitted = 0
                for i in self.options(current):
                    permitted |= self.rules.allowed[direction][i]
                if self.constrain(nx, ny, permitted):
                    stack.append((nx, ny))

    def _entropy(self, mask: int) -> float:
        """Entropia de Shannon ponderada. Menor = celula mais decidida."""
        weights = [self.rules.weights[i] for i in self.options(mask)]
        total = sum(weights)
        return math.log(total) - sum(w * math.log(w) for w in weights) / total

    def observe(self) -> bool:
        """Colapsa a celula mais restrita. Devolve False quando tudo ja colapsou."""
        best, best_key = None, None
        for y in range(self.h):
            for x in range(self.w):
                mask = self.at(x, y)
                if mask & (mask - 1) == 0:  # zero ou um bit: ja decidida
                    continue
                # Ruido minusculo desempata sem enviesar; vem do rng semeado,
                # entao a escolha continua reproduzivel.
                key = self._entropy(mask) + self.rng.random() * 1e-6
                if best_key is None or key < best_key:
                    best, best_key = (x, y), key

        if best is None:
            return False

        x, y = best
        candidates = self.options(self.at(x, y))
        chosen = self.rng.choices(candidates, weights=[self.rules.weights[i] for i in candidates])[0]
        self.cells[y * self.w + x] = 1 << chosen
        self.propagate((x, y))
        return True

    def result(self) -> list:
        grid = []
        for y in range(self.h):
            row = []
            for x in range(self.w):
                opts = self.options(self.at(x, y))
                if len(opts) != 1:
                    raise Contradiction(f"celula ({x},{y}) nao colapsou")
                row.append(self.rules.ids[opts[0]])
            grid.append(row)
        return grid


def apply_constraints(wave: Wave, rules: Ruleset, pins: dict) -> None:
    """Fixa bordas declaradas no ruleset e pinos passados na linha de comando.

    Pinos sao o que torna WFC utilizavel num jogo autoral: a Igreja Matriz fica
    onde o designer quer, e o WFC preenche o que existe entre os pontos fixos.
    """
    def force(x: int, y: int, tile_id: str) -> None:
        if tile_id not in rules.index:
            raise ValueError(f"tile desconhecido em constraint/pin: {tile_id}")
        wave.constrain(x, y, 1 << rules.index[tile_id])
        wave.propagate((x, y))

    row_rules = {
        "top_row": lambda: [(x, 0) for x in range(wave.w)],
        "bottom_row": lambda: [(x, wave.h - 1) for x in range(wave.w)],
        "left_column": lambda: [(0, y) for y in range(wave.h)],
        "right_column": lambda: [(wave.w - 1, y) for y in range(wave.h)],
    }
    for key, coords in row_rules.items():
        tile_id = rules.constraints.get(key)
        if tile_id:
            for x, y in coords():
                force(x, y, tile_id)

    for (x, y), tile_id in pins.items():
        if not (0 <= x < wave.w and 0 <= y < wave.h):
            raise ValueError(f"pino ({x},{y}) fora da grade {wave.w}x{wave.h}")
        force(x, y, tile_id)


def solve(rules: Ruleset, width: int, height: int, seed: int, pins: dict, attempts: int) -> tuple:
    """Roda o WFC, recomecando em caso de contradicao. Devolve (grade, tentativas).

    Recomecar e a estrategia padrao e e barata nestas dimensoes -- backtracking
    fino custa mais codigo e mais tempo do que simplesmente tentar de novo com
    outra sequencia derivada da mesma seed (entao continua reproduzivel).
    """
    last = None
    for attempt in range(attempts):
        rng = random.Random(f"{seed}:{attempt}")
        wave = Wave(rules, width, height, rng)
        try:
            apply_constraints(wave, rules, pins)
            while wave.observe():
                pass
            return wave.result(), attempt + 1
        except Contradiction as exc:
            last = exc
    raise SystemExit(
        f"ERRO: WFC nao convergiu em {attempts} tentativas ({last}).\n"
        "Causas comuns: adjacencia restrita demais, constraints de borda que se\n"
        "contradizem, ou pinos incompativeis com os vizinhos possiveis."
    )


# -------------------------------------------------------------- renderizacao

def load_tilesets(rules: Ruleset) -> dict:
    """Carrega os PNGs de tileset e seus manifests, indexando linha por nome."""
    loaded = {}
    for name, cfg in rules.tilesets.items():
        sheet_path = (rules.base_dir / cfg["sheet"]).resolve()
        manifest_path = (rules.base_dir / cfg["manifest"]).resolve()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        loaded[name] = {
            "image": Image.open(sheet_path).convert("RGBA"),
            "tile": manifest["tile_size"],
            "variations": manifest["variations"],
            "rows": {row: i for i, row in enumerate(manifest["rows"])},
        }
    return loaded


def render(grid: list, rules: Ruleset, sheets: dict, seed: int) -> tuple:
    """Compoe o preview PNG e devolve tambem a variacao escolhida por celula."""
    tile_px = next(iter(sheets.values()))["tile"] if sheets else 32
    for data in sheets.values():
        if data["tile"] != tile_px:
            raise ValueError("tilesets do ruleset tem tile_size diferentes entre si")

    height, width = len(grid), len(grid[0])
    canvas = Image.new("RGBA", (width * tile_px, height * tile_px), (0, 0, 0, 0))
    variations = []

    for y, row in enumerate(grid):
        var_row = []
        for x, tile_id in enumerate(row):
            source = rules.tiles[tile_id].get("source")
            if not source:  # tile vazio (ceu, ar) -- deixa transparente
                var_row.append(None)
                continue
            family, row_name = source
            data = sheets[family]
            if row_name not in data["rows"]:
                raise ValueError(f"tileset '{family}' nao tem a linha '{row_name}'")
            # Variacao por celula, derivada da seed + posicao: mesma seed, mesmo mapa.
            col = random.Random(f"{seed}:var:{x}:{y}").randrange(data["variations"])
            sy = data["rows"][row_name] * tile_px
            crop = data["image"].crop((col * tile_px, sy, (col + 1) * tile_px, sy + tile_px))
            canvas.paste(crop, (x * tile_px, y * tile_px))
            var_row.append(col)
        variations.append(var_row)

    return canvas, variations, tile_px


# ------------------------------------------------------- saida para o Unity

def write_unity_map(path: Path, grid: list, variations: list, rules: Ruleset, tile_px: int) -> None:
    """Emite o companheiro que o importer do Unity le.

    O `.map.json` e a saida legivel: dicionarios e listas aninhadas. O JsonUtility do
    Unity nao le nem dicionario nem array irregular, entao em vez de escrever um parser
    JSON a mao em C# emitimos ESTE arquivo, so com arrays planos de primitivos --
    exatamente o que o JsonUtility desserializa sem ajuda.

    Os dois descrevem o mesmo mapa; este e o formato de maquina.
    """
    tileset_names = list(rules.tilesets.keys())
    tileset_index = {name: i for i, name in enumerate(tileset_names)}

    # Caminho do tileset relativo a pasta Assets/, que e como o Unity enderaca asset.
    asset_paths, tileset_variations, tileset_rows = [], [], []
    for name in tileset_names:
        sheet = (rules.base_dir / rules.tilesets[name]["sheet"]).resolve()
        parts = sheet.as_posix().split("/Assets/", 1)
        asset_paths.append("Assets/" + parts[1] if len(parts) == 2 else "")
        mf = json.loads((rules.base_dir / rules.tilesets[name]["manifest"]).resolve()
                        .read_text(encoding="utf-8"))
        # O importer fatia o PNG em grade e indexa row-major, entao precisa saber
        # quantas colunas (variacoes) cada tileset tem para achar o sprite certo.
        tileset_variations.append(mf["variations"])
        tileset_rows.append(len(mf["rows"]))

    tile_ids = list(rules.ids)
    tile_family, tile_row = [], []
    for tid in tile_ids:
        source = rules.tiles[tid].get("source")
        if not source:  # tile vazio (ceu/ar): nao pinta celula nenhuma
            tile_family.append(-1)
            tile_row.append(-1)
            continue
        family, row_name = source
        manifest = json.loads((rules.base_dir / rules.tilesets[family]["manifest"]).resolve()
                              .read_text(encoding="utf-8"))
        tile_family.append(tileset_index[family])
        tile_row.append(manifest["rows"].index(row_name))

    tile_index = {tid: i for i, tid in enumerate(tile_ids)}
    cells = [tile_index[c] for row in grid for c in row]
    cell_variation = [(-1 if v is None else v) for row in variations for v in row]

    path.write_text(json.dumps({
        "ruleset": rules.name,
        "width": len(grid[0]),
        "height": len(grid),
        "tileSize": tile_px,
        "tilesetNames": tileset_names,
        "tilesetAssetPaths": asset_paths,
        "tilesetVariations": tileset_variations,
        "tilesetRows": tileset_rows,
        "tileIds": tile_ids,
        "tileFamily": tile_family,
        "tileRow": tile_row,
        "cells": cells,
        "cellVariation": cell_variation,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ------------------------------------------------------------------------ cli

def parse_pin(text: str) -> tuple:
    try:
        coords, tile_id = text.split("=", 1)
        x, y = coords.split(",", 1)
        return (int(x), int(y)), tile_id
    except ValueError:
        raise argparse.ArgumentTypeError(f"pino invalido '{text}' -- use X,Y=tile_id")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ruleset", type=Path)
    ap.add_argument("--seed", type=int, required=True, help="Seed deterministica (registrada no manifest)")
    ap.add_argument("-w", "--width", type=int, default=20, help="Largura em tiles (default 20)")
    ap.add_argument("-H", "--height", type=int, default=12, help="Altura em tiles (default 12)")
    ap.add_argument("--learn", type=Path, help="Deriva adjacencia e pesos de um mapa de exemplo")
    ap.add_argument("--pin", type=parse_pin, action="append", default=[], metavar="X,Y=TILE",
                    help="Fixa um tile numa celula. Repetivel.")
    ap.add_argument("--attempts", type=int, default=40, help="Tentativas antes de desistir (default 40)")
    ap.add_argument("--save-learned", type=Path, help="Grava o ruleset com a adjacencia derivada")
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.ruleset.read_text(encoding="utf-8"))
    if args.learn:
        data = learn_adjacency(json.loads(args.learn.read_text(encoding="utf-8")), data)
        if args.save_learned:
            args.save_learned.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"ruleset aprendido: {args.save_learned}")

    rules = Ruleset(data, args.ruleset.parent)
    for problem in rules.orphans():
        print(f"AVISO: {problem}")

    pins = dict(args.pin)
    grid, attempts = solve(rules, args.width, args.height, args.seed, pins, args.attempts)

    sheets = load_tilesets(rules)
    canvas, variations, tile_px = render(grid, rules, sheets, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out)

    map_path = args.out.with_suffix(".map.json")
    map_path.write_text(json.dumps({
        "ruleset": rules.name,
        "seed": args.seed,
        "size": [args.width, args.height],
        "tile_size": tile_px,
        "tiles": {t: rules.tiles[t].get("source") for t in rules.ids},
        "grid": grid,
        "variations": variations,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_unity_map(args.out.with_suffix(".unity.json"), grid, variations, rules, tile_px)

    manifest_path = args.out.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps({
        "generator": "gen_map_wfc.py",
        "ruleset": str(args.ruleset),
        "ruleset_name": rules.name,
        "learned_from": str(args.learn) if args.learn else None,
        "seed": args.seed,
        "size": [args.width, args.height],
        "tile_size": tile_px,
        "pins": {f"{x},{y}": t for (x, y), t in pins.items()},
        "attempts_used": attempts,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    used = sorted({c for row in grid for c in row})
    print(f"OK: {args.out} ({args.width}x{args.height} tiles, seed {args.seed}, "
          f"{attempts} tentativa(s))")
    print(f"     tiles usados: {', '.join(used)}")
    print(f"     + {map_path.name} + {manifest_path.name}")


if __name__ == "__main__":
    main()
