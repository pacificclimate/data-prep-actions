from itertools import product
from collections.abc import Iterable, Mapping, Generator, Sequence


def merge(dicts):
    """
    Return a single dict resulting from merging all `dict`s in the iterable `dicts`
    """
    # print("  merge", dicts)
    return {
        name: value for d in dicts for name, value in d.items()
    }


def mergeeach(dicts_seq, seq=list):
    """
    Return a tuple of dicts resulting from mapping `merge` over `seq`

    :param dicts_seq: an iterable of iterables of dicts
    :return: tuple of dicts (each sub-interable merged)
    """
    # print("  mergeeach", dicts_seq)
    return seq(merge(dicts) for dicts in dicts_seq)


def prod(items, seq=list):
    """
    Return a tuple containing the cross product of each iterable in iterable `items`.

    :param items: iterable of iterables of items
    :return: tuple of tuples
    """
    # print("  prod", items)
    return seq(map(seq, product(*items)))


def for_(keys, values_seq, seq=list):
    """
    Return a tuple of dicts formed from paring the iterable `keys` with each
    iterable of of values in `values_seq`.
    :param keys: iterable of keys (strings)
    :param values_seq: iterable of iterable of values
    :return:
    """
    # print("  for", keys, values_seq)
    return seq(dict(zip(keys, values)) for values in values_seq)


def mergeeachprod(items, seq=list):
    """
    Return the result of mergeing each set of tuples in the cross product of items.
    :param items:
    :return:
    """
    return mergeeach(prod(items, seq=seq), seq=seq)


def isiterable(x):
    return isinstance(x, Iterable) and type(x) != str


def ismapping(x):
    return isinstance(x, Mapping)


def isoperator(x):
    return (
        ismapping(x) and
        len(x) == 1 and
        list(x)[0] in {"$merge", "$mergeeach", "$for", "$prod", "$mergeeachprod"}
    )


def iterate(thing, seq=list):
    # print("process", thing)
    if isoperator(thing):
        operator, operands = tuple(thing.items())[0]
        # print("op:", operator, operands)
        if operator == '$merge':
            return merge(iterate(operands))
        elif operator == '$mergeeach':
            return mergeeach(iterate(operands))
        elif operator == '$for':
            names, *value_seq = operands
            return for_(names, iterate(value_seq))
        elif operator == '$prod':
            return prod(iterate(operands))
        elif operator == '$mergeeachprod':
            return mergeeachprod(iterate(operands))
        else:
            raise ValueError(f"Invalid operator '{operator}'")
    elif ismapping(thing):
        return {key: iterate(value) for key, value in thing.items()}
    elif isiterable(thing):
        return seq(iterate(item, seq=seq) for item in thing)
    else:
        return thing
