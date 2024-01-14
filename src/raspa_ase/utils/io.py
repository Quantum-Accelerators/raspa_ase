from __future__ import annotations

import re
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


def parse_output(filepath: str | Path) -> dict[str, Any]:
    """
    Specific parsing of the output file. Adapted from the following:
    https://github.com/iRASPA/RASPA2/blob/master/python/output_parser.py

    Parameters
    ----------
    filepath
        The path to the RASPA output file.

    Returns
    -------
    dict
        The parsed output data.
    """

    def _clean(split_list: list[str]) -> list[float]:
        """Strips and attempts to convert a list of strings to floats."""

        def try_float(s):
            try:
                return float(s)
            except ValueError:
                return s

        return [try_float(s.strip()) for s in split_list if s]

    with Path(filepath).open(mode="r") as fd:
        raspa_output = fd.read()

    # Reads the string into a newline-separated list, skipping useless lines
    data = [
        row.strip()
        for row in raspa_output.splitlines()
        if row and all(d not in row for d in ["-----", "+++++"])
    ]

    # Generally, categories in the output are delimited by equal signs
    delimiters = [
        i
        for i, row in enumerate(data)
        if "=====" in row and "Exclusion constraints energy" not in data[i - 1]
    ]

    # Append a row for "absolute adsorption:" and "excess adsorption:"
    # These values are separated into two rows
    abs_adsorp_rows = [i for i, row in enumerate(data) if "absolute adsorption:" in row]
    for row in abs_adsorp_rows:
        data[row] += "  " + data[row + 1]
        data[row + 2] += data[row + 3]
        data[row + 1], data[row + 3] = " ", " "

    # Use the delimiters to make a high-level dict. Title is row before
    # delimiter, and content is every row after delimiter, up to the next title
    info = {
        data[n - 1].strip(":"): data[n + 1 : delimiters[i + 1] - 1]
        for i, n in enumerate(delimiters[:-1])
    }

    # Let's PARSE!
    for key, values in info.items():
        d, note_index = {}, 1
        for item in values:
            # Takes care of all "Blocks[ #]", skipping hard-to-parse parts
            if (
                "Block" in item
                and "Box-lengths" not in key
                and "Van der Waals:" not in item
            ):
                blocks = _clean(item.split())
                d["".join(blocks[:2])] = blocks[2:]

            # Most of the average data values are parsed in this section
            elif (
                any(s in item for s in ["Average     ", "Surface area:"])
                and "desorption" not in key
            ):
                average_data = _clean(item.split())
                # Average values organized by its unit, many patterns here
                if len(average_data) == 8:
                    del average_data[2:4]
                    d[" ".join(average_data[4:6])] = average_data[1:4]
                elif len(average_data) == 5:
                    d[average_data[-1]] = average_data[1:4]
                elif "Surface" in average_data[0]:
                    d[average_data[-1]] = average_data[2:5]
                # This is the common case
                else:
                    del average_data[2]
                    d[average_data[-1]] = average_data[1:4]

            # Average box-lengths has its own pattern
            elif "Box-lengths" in key:
                box_lengths = _clean(item.split())
                i = 3 if "angle" in item else 2
                d[" ".join(box_lengths[:i])] = box_lengths[i:]

            # "Heat of Desorption" section
            elif "desorption" in key:
                if "Note" in item:
                    notes = re.split(r"[:\s]{2,}", item)
                    d["%s %d" % (notes[0], note_index)] = notes[1]
                    note_index += 1
                else:
                    heat_desorp = _clean(item.split())
                    # One line has "Average" in front, force it to be normal
                    if "Average" in item:
                        del heat_desorp[0]
                    d[heat_desorp[-1]] = heat_desorp[0:3]

            # Parts where Van der Waals are included
            elif (
                "Host-" in key or "-Cation" in key or "Adsorbate-Adsorbate" in key
            ) and "desorption" not in key:
                van_der = item.split()
                # First Column
                if "Block" in van_der[0]:
                    sub_data = [
                        _clean(s.split(":")) for s in re.split(r"\s{2,}", item)[1:]
                    ]
                    sub_dict = {s[0]: s[1] for s in sub_data[:2]}
                    d["".join(van_der[:2])] = [float(van_der[2]), sub_dict]
                # Average for each columns
                elif "Average" in item:
                    avg = _clean(re.split(r"\s{2,}", item))
                    vdw, coulomb = (_clean(s.split(": ")) for s in avg[2:4])
                    d[avg[0]] = avg[1]
                    d["Average %s" % vdw[0]] = vdw[1]
                    d["Average %s" % coulomb[0]] = coulomb[1]
                else:
                    d["standard deviation"] = _clean(van_der)

            # IMPORTANT STUFF
            elif "Number of molecules" in key:
                adsorb_data = _clean(item.rsplit(" ", 12))
                if "Component" in item:
                    gas_name = adsorb_data[2].strip("[]")
                    d[gas_name] = {}
                else:
                    d[gas_name][adsorb_data[0]] = adsorb_data[1:]

            # Henry and Widom
            elif "Average Widom" in item:
                d["Widom"] = _clean(item.rsplit(" ", 5))[1:]

            elif "Average Henry" in item:
                d["Henry"] = _clean(item.rsplit(" ", 5))[1:]

            # Ignore these
            elif any(
                s in item
                for s in ["=====", "Starting simulation", "Finishing simulation"]
            ):
                continue

            # Other strings
            else:
                parsed_data = _clean(re.split(r"[()[\]:,\t]", item))
                d[parsed_data[0]] = parsed_data[1:]
        # Putting subdictionary back into main object
        info[key] = d

    return info


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
        if isinstance(v, dict):
            s += f"    {k}\n    " + _dict_to_str(v)
        elif isinstance(v, Iterable) and not isinstance(v, str):
            s += f"    {k} " + _iterable_to_str(v)
        else:
            s += f"    {k} {v}\n"
    return s
