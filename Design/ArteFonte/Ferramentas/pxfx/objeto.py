"""`Obj`: o objeto literal do JS em Python.

Um dict que também aceita atributo (`o.palette`) e devolve `None` para o que não
existe — o equivalente ao `undefined` do JS. É o que deixa o port dos efeitos ser
tradução quase linha a linha: `o.palette`, `meta.options`, `hit.stop`.
"""
from __future__ import annotations


class Obj(dict):
    __slots__ = ()

    def __getattr__(self, nome):
        if nome.startswith("__"):
            raise AttributeError(nome)
        return self.get(nome)

    def __setattr__(self, nome, valor):
        self[nome] = valor

    def __delattr__(self, nome):
        self.pop(nome, None)

    def copia(self, **mais):
        """`{ ...o, ...mais }`."""
        n = Obj(self)
        n.update(mais)
        return n


def obj(v):
    """Converte dicts (e listas de dicts) em Obj, recursivamente."""
    if isinstance(v, Obj):
        return v
    if isinstance(v, dict):
        return Obj({k: obj(x) for k, x in v.items()})
    if isinstance(v, list):
        return [obj(x) for x in v]
    return v


def nn(v, padrao):
    """`v ?? padrao`."""
    return padrao if v is None else v
