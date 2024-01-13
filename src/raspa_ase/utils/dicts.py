from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def get_parameter(d: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get a parameter from a dictionary, ignoring case.

    Parameters
    ----------
    d
        The dictionary to get the parameter from.
    key
        The parameter to get.
    default
        The default value to return if the parameter is not found.

    Returns
    -------
    Any
        The value of the parameter, or the default value if the parameter is not found.
    """
    d_lower = {k.lower(): v for k, v in d.items()}

    return d_lower.get(key.lower(), default)


def pop_parameter(d: dict[str, Any], key: str) -> Any:
    """
    Pop a parameter from a dictionary, ignoring case.

    Parameters
    ----------
    d
        The dictionary to pop the parameter from.
    key
        The parameter to pop.

    Returns
    -------
    Any
        The value of the parameter or None if the parameter is not found.
    """
    for k, v in d.items():
        if k.lower() == key.lower():
            del d[k]
            return v
    return None


def merge_parameters(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two dictionaries, ignoring case.

    Parameters
    ----------
    dict1
        The first dictionary to merge.
    dict2
        The second dictionary to merge.

    Returns
    -------
    dict
        The merged dictionary.
    """
    merged_dict = deepcopy(dict1)

    for key2, value2 in dict2.items():
        matching_key = next(
            (key1 for key1 in merged_dict if key1.lower() == key2.lower()), None
        )

        if matching_key:
            merged_dict[matching_key] = value2
        else:
            merged_dict[key2] = value2

    return merged_dict


def convert_booleans(d: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively convert boolean values to "yes" or "no".

    Parameters
    ----------
    d
        The dictionary to convert.

    Returns
    -------
    dict
        The dictionary with the boolean values converted to "Yes" or "No".
    """
    for key, value in d.items():
        if isinstance(value, bool):
            d[key] = "Yes" if value else "No"
        elif isinstance(value, dict):
            convert_booleans(value)
    return d
