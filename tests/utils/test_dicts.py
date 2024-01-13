from raspa_ase.utils.dicts import (
    convert_booleans,
    get_parameter,
    merge_parameters,
    pop_parameter,
)


def test_convert_booleans():
    d = {"a": True, "b": {"c": False}, "d": "wow"}
    assert convert_booleans(d) == {"a": "Yes", "b": {"c": "No"}, "d": "wow"}


def test_get_parameter():
    d = {"a": 1, "b": 2}
    assert get_parameter(d, "a") == 1
    assert get_parameter(d, "A") == 1
    assert get_parameter(d, "c") is None
    assert get_parameter(d, "c", default=3) == 3


def test_merge_parameters():
    d1 = {"a": 1, "b": 2}
    d2 = {"A": 3, "C": 4}
    assert merge_parameters(d1, d2) == {"a": 3, "b": 2, "C": 4}


def test_pop_parameter():
    d = {"a": 1, "b": 2}
    assert pop_parameter(d, "A") == 1
    assert pop_parameter(d, "c") is None
    assert d == {"b": 2}
