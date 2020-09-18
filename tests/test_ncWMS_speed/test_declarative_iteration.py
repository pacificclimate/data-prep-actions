import pytest
from itertools import product
import yaml
from actions.test_ncWMS_speed.declarative_iteration import merge, for_, iterate


@pytest.mark.parametrize('input, expected', (
    (
        [{'a': 1},],
        {'a': 1}
    ),
    (
        [{'a': 1}, {'b': 2}],
        {'a': 1, 'b': 2}
    ),
    (
        [{'a': 1}, {'b': 2}, {'c': 3, 'd': 4}],
        {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    ),
    (
        [{'a': 1}, {'b': 2}, {'c': 3, 'd': 4}, {'a': 99}],
        {'a': 99, 'b': 2, 'c': 3, 'd': 4}
    ),
))
def test_merge(input, expected):
    assert merge(input) == expected


@pytest.mark.parametrize('names, values_seq, expected', (
    (
        ['a', 'b'],
        [[1, 2], [3, 4]],
        ({'a': 1, 'b': 2}, {'a': 3, 'b': 4})
    ),
))
def test_for(names, values_seq, expected):
    assert tuple(for_(names, values_seq)) == expected


@pytest.mark.parametrize('input, expected', (
    (
        [1, 2, 3],
        [1, 2, 3]
    ),
    (
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2}
    ),
    (
        {'$merge': [{'a': 1}, {'b': 2}]},
        {'a': 1, 'b': 2}
    ),
    (
        {'$prod': [['a', 'b'], [1, 2]]},
        list(map(list, product(['a', 'b'], [1, 2])))
    ),
    (
        {'$prod': [ [{'a': 1}, {'a': 2}], [{'b': 3}, {'b': 4}] ]},
        list(map(list, product([{'a': 1}, {'a': 2}], [{'b': 3}, {'b': 4}])))
    ),
    (
        {'$for': [
            ['a', 'b'],
            [1, 2],
            [3, 4]
        ]},
        [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    ),
    (
        {
            '$prod': [
                {'$for': [['a', 'b'], [1, 2], [3, 4]]},
                {'$for': [['c', 'd'], [11, 12], [13, 14]]},
            ]
        },
        [
            [{'a': 1, 'b': 2}, {'c': 11, 'd': 12}],
            [{'a': 1, 'b': 2}, {'c': 13, 'd': 14}],
            [{'a': 3, 'b': 4}, {'c': 11, 'd': 12}],
            [{'a': 3, 'b': 4}, {'c': 13, 'd': 14}],
        ]
    ),
    (
        {
            '$mergeeach': [
                [{'a': 1, 'b': 2}, {'c': 11, 'd': 12}],
                [{'a': 3, 'b': 4}, {'c': 13, 'd': 14}],
            ]
        },
        [
            {'a': 1, 'b': 2, 'c': 11, 'd': 12},
            {'a': 3, 'b': 4, 'c': 13, 'd': 14}
        ]
    ),
    (
        {
            '$mergeeach': {
                '$prod': [
                    {'$for': [['a', 'b'], [1, 2], [3, 4]]},
                    {'$for': [['c', 'd'], [11, 12], [13, 14]]},
                ]
            }
        },
        [
            {'a': 1, 'b': 2, 'c': 11, 'd': 12},
            {'a': 1, 'b': 2, 'c': 13, 'd': 14},
            {'a': 3, 'b': 4, 'c': 11, 'd': 12},
            {'a': 3, 'b': 4, 'c': 13, 'd': 14},
        ]
    ),
    (
        {
            '$mergeeachprod': [
                { '$for': [['a', 'b'], [1, 2], [3, 4]]},
                { '$for': [['c', 'd'], [11, 12], [13, 14]]},
            ]
        },
        [
            {'a': 1, 'b': 2, 'c': 11, 'd': 12},
            {'a': 1, 'b': 2, 'c': 13, 'd': 14},
            {'a': 3, 'b': 4, 'c': 11, 'd': 12},
            {'a': 3, 'b': 4, 'c': 13, 'd': 14},
        ]
    ),
))
def test_process(input, expected):
    print()
    print()
    print("input", input)
    result = iterate(input)
    print("result", result)
    assert result == expected


@pytest.mark.parametrize('input, expected', (
    (
        """
        $merge:
            - a: 1
            - b: 2
        """,
        """
        a: 1
        b: 2
        """
    ),
    (
        """
        $mergeeachprod:
            - $for:
                - [a, b]
                - [1, 2]
                - [3, 4]
            - $for:
                - [c, d]
                - [11, 12]
                - [13, 14]
        """,
        """
        - {a: 1, b: 2, c: 11, d: 12}
        - {a: 1, b: 2, c: 13, d: 14}
        - {a: 3, b: 4, c: 11, d: 12}
        - {a: 3, b: 4, c: 13, d: 14}
        """
    )
))
def test_process_yaml(input, expected):
    assert iterate(yaml.safe_load(input)) == yaml.safe_load(expected)
