from itertools import product
from collections.abc import Iterable, Mapping, Generator, Sequence


def merge(items):
    """
    Return a single object (list or dict) resulting from merging all items in the
    iterable `items`. Each such item must be of the same type (list or dict).
    """
    # print("  merge", dicts)
    t = type(items[0])
    if not all(type(item) == t for item in items):
        raise ValueError(f"Cannot merge items of diverse types")
    if t == dict:
        return {name: value for d in items for name, value in d.items()}
    if t == list:
        return [element for l in items for element in l]
    raise ValueError(
        f"Cannot merge items of type {t}. Context: {items}"
    )


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
    return ismapping(x) and len(x) == 1 and list(x)[0].startswith("$")


def iterate(thing, seq=list):
    # print("### iterate", thing)
    if isoperator(thing):
        operator, operands = tuple(thing.items())[0]
        # print("op:", operator, operands)
        if operator == '$one':
            return [iterate(operands)]
        if operator in ['$merge', '$union', '$flatten']:
            return merge(iterate(operands))
        if operator == '$mergeeach':
            return mergeeach(iterate(operands))
        if operator in ['$for', '$each']:
            if ismapping(operands):
                # Special syntax for single key whose name is specified as a dict key
                key, values = tuple(operands.items())[0]
                keys = [key]
                value_seq = [[value] for value in values]
            else:
                keys, *value_seq = operands
                if type(keys) == str:
                    # Special syntax for single key whose name is specified by a single
                    # string value (not a list). Then all values must also be specified
                    # by single values (not lists).
                    keys = [keys]
                    value_seq = [[value] for value in value_seq]
            return for_(keys, iterate(value_seq))
        if operator == '$prod':
            return prod(iterate(operands))
        if operator in ['$mergeeachprod', '$combinations']:
            return mergeeachprod(iterate(operands))
        raise ValueError(f"Invalid operator '{operator}'")
    elif ismapping(thing):
        return {key: iterate(value) for key, value in thing.items()}
    elif isiterable(thing):
        return seq(iterate(item, seq=seq) for item in thing)
    else:
        return thing
