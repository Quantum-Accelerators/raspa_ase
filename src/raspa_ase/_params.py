from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from typing import Any

    from ase.atoms import Atoms


def get_framework_params(frameworks: list[Atoms]) -> dict[str, Any]:
    """
    Get the framework-related parameters.

    Parameters
    ----------
    frameworks
        The frameworks to get the parameters for.

    Returns
    -------
    dict
        The framework-related parameters.
    """
    # TODO: Add support for writing charges to CIF
    # with _atom_site_charge and in RASPA set UseChargesFromCIFFile yes
    parameters = {}
    for i, framework in enumerate(frameworks):
        name = f"framework{i}"

        n_cells = get_suggested_cells(framework, parameters.get("cutoff", 12.0))

        parameters[f"framework {i}"] = {
            "frameworkname": name,
            "unitcells": n_cells,
        } | framework.info
    return parameters


def get_suggested_cells(framework: Atoms, cutoff: float) -> tuple[int, int, int]:
    """
    Get the suggested number of unit cells in each dimension for a given cutoff.

    Parameters
    ----------
    framework
        The framework to calculate the suggested number of unit cells for.
    cutoff
        The cutoff used for the calculation, in A.

    Returns
    -------
    tuple[int, int, int]
        The suggested number of unit cells in each dimension.
    """
    A, B, C = framework.get_cell()[:3]

    def _calculate_min_dist(v1, v2, v3):
        cross_product = np.cross(v1, v2)
        numerator = np.linalg.norm(np.dot(cross_product, v3))
        denominator = np.linalg.norm(cross_product)
        return np.divide(numerator, denominator)

    min_A = _calculate_min_dist(B, C, A)
    min_B = _calculate_min_dist(C, A, B)
    min_C = _calculate_min_dist(A, B, C)
    return [
        int(np.ceil(float(cutoff) / (0.5 * min_i))) for min_i in [min_A, min_B, min_C]
    ]


def sanitize_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize the parameters by making them lower-case and converting
    boolean values to "yes" or "no".

    Parameters
    ----------
    parameters
        The parameters to sanitize.

    Returns
    -------
    dict
        The sanitized parameters.
    """
    parameters = convert_keys_to_lowercase(parameters)
    parameters = convert_boolean_values(parameters)
    return parameters


def convert_keys_to_lowercase(d: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively convert the keys of a dictionary to lowercase.

    Parameters
    ----------
    d
        The dictionary to convert.

    Returns
    -------
    dict
        The dictionary with the keys converted to lowercase.
    """
    if isinstance(d, dict):
        return {
            key.lower(): convert_keys_to_lowercase(value) for key, value in d.items()
        }
    else:
        return d


def convert_boolean_values(d: dict[str, Any]) -> dict[str, Any]:
    for key, value in d.items():
        if isinstance(value, bool):
            d[key] = "yes" if value else "no"
        elif isinstance(value, dict):
            convert_boolean_values(value)
    return d
