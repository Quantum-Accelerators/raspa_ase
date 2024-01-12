"""
ASE calculator for RASPA_ase
"""
from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from subprocess import check_call
from typing import TYPE_CHECKING

import numpy as np
from ase.calculators.genericfileio import CalculatorTemplate, GenericFileIOCalculator
from pymatgen.io.ase import AseAtomsAdaptor

if TYPE_CHECKING:
    from typing import Any, TypedDict

    from ase.atoms import Atoms

    class Results(TypedDict, total=False):
        pass


# TODO:
# - Take a list of Atoms as the frameworks
# - Take a list of Atoms as the molecules
# - Take a list of blank Atoms() as the Boxes
# atoms.get_cell().array for BoxMatrix


# - Use logger for n_cells
# - Allow user to override n_cell changes
# - Warn if the other env vars aren't set in the manual
class RaspaProfile:
    """
    RASPA profile
    """

    def __init__(self, argv: list[str] | None = None) -> None:
        """
        Initialize the RASPA profile.

        Parameters
        ----------
        argv
            The command line arguments to the RASPA executable.

        Returns
        -------
        None
        """
        raspa_dir = os.environ.get("RASPA_DIR")
        if not raspa_dir:
            raise EnvironmentError("RASPA_DIR environment variable not set")
        self.argv = argv or [f"{raspa_dir}/bin/simulate", "simulate.input"]

    def run(
        self,
        directory: Path | str,
        output_filename: Path | str,
    ) -> None:
        """
        Run the RASPA calculation.

        Parameters
        ----------
        directory
            The directory where the calculation will be run.
        output_filename
            The name of the log file to write to in the directory.

        Returns
        -------
        None
        """
        with Path(output_filename).open("w") as fd:
            check_call(self.argv, stdout=fd, cwd=directory)


class RaspaTemplate(CalculatorTemplate):
    """
    RASPA template
    """

    def __init__(self) -> None:
        """
        Initialize the RASPA template.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        label = "raspa"
        super().__init__(
            name=label,
            implemented_properties=["energy"],
        )

        self.input_file = f"simulation.input"
        self.output_file = f"{label}.out"

    def execute(self, directory: Path | str, profile: RaspaProfile) -> None:
        """
        Run the RASPA executable.

        Parameters
        ----------
        directory
            The path to the directory to run the RASPA executable in.
        profile
            The RASPA profile to use.

        Returns
        -------
        None
        """
        profile.run(directory, self.output_file)

    def write_input(
        self,
        profile: RaspaProfile,  # skipcq: PYL-W0613
        directory: Path | str,
        atoms: Atoms | list[Atoms],
        properties: Any,  # skipcq: PYL-W0613
        parameters: dict[str, Any],
    ) -> None:
        """
        Write the RASPA input files.

        Parameters
        ----------
        directory
            The path to the directory to write the RASPA input files in.
        atoms
            The ASE atoms object(s) to write.
        parameters
            The RASPA parameters to use, formatted as a dictionary.
        properties
            This is needed the base class and should not be explicitly specified.

        Returns
        -------
        None
        """
        simulation_input = ""
        frameworks = atoms if isinstance(atoms, list) else [atoms]

        # TODO: do this recursively
        parameters = {
            k: "Yes" if v is True else "No" if v is False else v
            for k, v in parameters.items()
        }

        reserved = ["framework", "frameworkname", "usechargesfromciffile"]
        for key in reserved:
            if key in parameters:
                raise ValueError(f"{key} is a reserved parameter name.")

        cutoff = 12.0
        for k, v in parameters.items():
            if k.lower() == "cutoff":
                cutoff = v
                break

        # TODO: Add support for writing charges to CIF
        # with _atom_site_charge and in RASPA set UseChargesFromCIFFile yes

        for i, framework in enumerate(frameworks):
            name = f"framework{i}"
            A, B, C = framework.get_cell()[:3]

            def _calculate_min_dist(v1, v2, v3):
                cross_product = np.cross(v1, v2)
                numerator = np.linalg.norm(np.dot(cross_product, v3))
                denominator = np.linalg.norm(cross_product)
                return np.divide(numerator, denominator)

            min_A = _calculate_min_dist(B, C, A)
            min_B = _calculate_min_dist(C, A, B)
            min_C = _calculate_min_dist(A, B, C)
            n_cells = [
                int(np.ceil(float(cutoff) / (0.5 * min_i)))
                for min_i in [min_A, min_B, min_C]
            ]
            parameters |= {
                f"Framework {i}": {"FrameworkName": name, "UnitCells": n_cells}
                | framework.info
            }
            structure = AseAtomsAdaptor.get_structure(framework)
            structure.to(str(Path(directory, name + ".cif")))

        def _write_iterable(v: list[Any]) -> str:
            return " ".join([str(i) for i in v]) + "\n"

        def _write_dict(d: dict[Any, Any]) -> str:
            s = ""
            for k, v in d.items():
                s += f"    {k} "
                if isinstance(v, dict):
                    s += _write_dict(v)
                elif isinstance(v, Iterable) and not isinstance(v, str):
                    s += _write_iterable(v)
                else:
                    s += f"{v}\n"
            return s

        for k, v in parameters.items():
            if isinstance(v, dict):
                simulation_input += f"{k}\n"
                simulation_input += _write_dict(v)
            elif isinstance(v, list):
                simulation_input += f"{k} "
                simulation_input += _write_iterable(v)
            else:
                simulation_input += f"{k} {v}\n"

        with Path(directory, "simulation.input").open(mode="w") as fd:
            fd.write(simulation_input)

    def read_results(self, directory: Path | str) -> Results:
        """
        Use cclib to read the results from the RASPA calculation.

        Parameters
        ----------
        directory
            The path to the directory to read the RASPA results from.

        Returns
        -------
        Results
            The RASPA results, formatted as a dictionary.
        """
        return {}

    def load_profile(self, cfg, **kwargs):
        return RaspaProfile.from_config(cfg, self.name, **kwargs)


class Raspa(GenericFileIOCalculator):
    """
    RASPA calculator
    """

    def __init__(
        self,
        profile: RaspaProfile | None = None,
        directory: Path | str = ".",
        n_cells: tuple[int, int, int] | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the RASPA calculator.

        Parameters
        ----------
        profile
            An instantiated [RASPA_ase.calculator.RASPAProfile][] object to use.
        directory
            The path to the directory to run the RASPA calculation in.
        **kwargs
            Any additional RASPA parameters.

        Returns
        -------
        None
        """

        profile = profile or RaspaProfile()
        parameters = kwargs

        super().__init__(
            template=RaspaTemplate(),
            profile=profile,
            directory=directory,
            parameters=parameters,
        )
