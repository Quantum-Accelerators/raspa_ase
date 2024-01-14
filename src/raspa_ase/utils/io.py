from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from ase.atoms import Atoms
from pymatgen.io.ase import AseAtomsAdaptor

from raspa_ase.utils.dicts import convert_booleans

if TYPE_CHECKING:
    from typing import Any


def write_simulation_input(
    parameters: dict[str, Any], input_filepath: str | Path
) -> str:
    """
    Write the `simulation.input` file for a given set of parameters.

    Parameters
    ----------
    parameters
        The parameters to write to the simulation input file.
    input_filepath
        The path to the simulation input file.

    Returns
    -------
    str
        The simulation input string.
    """

    simulation_input = ""
    parameters = convert_booleans(parameters)

    for k, v in parameters.items():
        if isinstance(v, dict):
            simulation_input += f"{k}\n"
            simulation_input += _dict_to_str(v)
        elif isinstance(v, list):
            simulation_input += f"{k} "
            simulation_input += _iterable_to_str(v)
        else:
            simulation_input += f"{k} {v}\n"

    with Path(input_filepath).open(mode="w") as fd:
        fd.write(simulation_input)


def write_frameworks(frameworks: list[Atoms], directory: str | Path) -> None:
    """
    Write the CIF files for a list of frameworks.

    Parameters
    ----------
    frameworks
        The frameworks to write.
    directory
        The directory to write the CIF files to.

    Returns
    -------
    None
    """
    for i, framework in enumerate(frameworks):
        if framework == Atoms():
            continue
        name = f"framework{i}"

        structure = AseAtomsAdaptor.get_structure(framework)
        structure.to(str(Path(directory, name + ".cif")), write_site_properties=True)


def _iterable_to_str(v: list[Any]) -> str:
    """
    Convert a list to a space-separated string.

    Parameters
    ----------
    v
        The list to convert.

    Returns
    -------
    str
        The space-separated string.
    """
    return " ".join([str(i) for i in v]) + "\n"


def _dict_to_str(d: dict[str, Any]) -> str:
    """
    Convert a dictionary to a formatted string.

    Parameters
    ----------
    d
        The dictionary to convert.

    Returns
    -------
    str
        The formatted string.
    """
    s = ""
    for k, v in d.items():
        s += f"    {k} "
        if isinstance(v, dict):
            s += _dict_to_str(v)
        elif isinstance(v, Iterable) and not isinstance(v, str):
            s += _iterable_to_str(v)
        else:
            s += f"{v}\n"
    return s
