from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from ase.atoms import Atoms

from raspa_ase.utils.dicts import get_parameter, merge_parameters

if TYPE_CHECKING:
    from typing import Any


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

    parameters = {}
    for i, framework in enumerate(frameworks):
        if framework == Atoms():
            continue

        name = f"framework{i}"
        cutoff = get_parameter(parameters, "CutOff", default=12.0)
        n_cells = get_suggested_cells(framework, cutoff)

        framework_params = {
            "FrameworkName": name,
            "UnitCells": n_cells,
        }

        if framework.has("initial_charges"):
            framework_params = merge_parameters(
                framework_params, {"UseChargesFromCIFFile": True}
            )

        parameters[f"Framework {i}"] = merge_parameters(
            framework_params,
            framework.info,
        )

    return parameters


def get_suggested_cells(framework: Atoms, cutoff: float) -> list[int]:
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
    return [int(np.ceil(cutoff / (0.5 * min_i))) for min_i in [min_A, min_B, min_C]]
