"""
ASE calculator for RASPA
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from ase.calculators.genericfileio import (
    BaseProfile,
    CalculatorTemplate,
    GenericFileIOCalculator,
)

from raspa_ase.utils.dicts import merge_parameters, pop_parameter
from raspa_ase.utils.io import parse_output, write_frameworks, write_simulation_input
from raspa_ase.utils.params import get_framework_params

if TYPE_CHECKING:
    from typing import Any

    from ase.atoms import Atoms

SIMULATION_INPUT = "simulation.input"
LABEL = "raspa"


class RaspaProfile(BaseProfile):
    """
    RASPA profile, which defines the command that will be executed and where.
    """

    def __init__(self, command: Path | str | None = None, **kwargs) -> None:
        """
        Initialize the RASPA profile. $RASPA_DIR must be set in the environment.

        Parameters
        ----------
        command
            The command to run RASPA. This defaults to doing `${RASPA_DIR}/bin/simulate`
            and typically does not need to be changed.

        Returns
        -------
        None
        """
        if not command:
            raspa_dir = os.environ.get("RASPA_DIR")
            if not raspa_dir:
                raise OSError("RASPA_DIR environment variable not set")
            command = f"{raspa_dir}/bin/simulate"
        super().__init__(command, **kwargs)

    def get_calculator_command(self, inputfile: str = SIMULATION_INPUT) -> list[str]:
        """
        Construct the command for the calculator.

        Parameters
        ----------
        inputfile
            The name of the input file to use.

        Returns
        -------
        list[str]
            The command to run the calculator.
        """
        return [self.command, f"{inputfile}"]

    def version(self) -> str:
        """
        Get the RASPA version number.

        Returns
        ------
        str
            The RASPA version.
        """
        raise NotImplementedError


class RaspaTemplate(CalculatorTemplate):
    """
    RASPA template, used to define how to read and write RASPA files.
    """

    def __init__(self, frameworks: list[Atoms] | None = None) -> None:
        """
        Initialize the RASPA template.

        Parameters
        ----------
        frameworks
            The frameworks to use, to be used in place of the `Atoms` object
            the calculator is applied to.

        Returns
        -------
        None
        """
        super().__init__(
            name="raspa",
            implemented_properties=["energy"],
        )

        self.inputname = SIMULATION_INPUT
        self.outputname = "raspa.stdout"
        self.errorfile = "raspa.stderr"
        self.frameworks = frameworks

    def write_input(
        self,
        profile: RaspaProfile,  # skipcq: PYL-W0613
        directory: Path | str,
        atoms: Atoms,
        parameters: dict[str, Any],
        properties: Any,  # skipcq: PYL-W0613
    ) -> None:
        """
        Write the RASPA input files.

        Parameters
        ----------
        directory
            The path to the directory to write the RASPA input files in.
        atoms
            The ASE atoms object to use as the framework.
        parameters
            The RASPA parameters to use, formatted as a dictionary.
        profile
             This is needed the base class and should not be explicitly specified.
        properties
            This is needed the base class and should not be explicitly specified.

        Returns
        -------
        None
        """
        frameworks = self.frameworks if self.frameworks else [atoms]
        parameters = merge_parameters(parameters, get_framework_params([atoms]))

        write_simulation_input(parameters, directory / self.inputname)
        write_frameworks(frameworks, directory)

    def execute(self, directory: Path | str, profile: RaspaProfile) -> None:
        profile.run(
            directory,
            self.inputname,
            self.outputname,
            errorfile=self.errorfile,
        )

    @staticmethod
    def read_results(directory: Path | str) -> dict[str, Any]:
        """
        Read the results of a RASPA calculation.

        Parameters
        ----------
        directory
            The path to the directory to read the RASPA results from.

        Returns
        -------
        Results
            The RASPA results, formatted as a dictionary.
        """
        output_path = Path(directory) / "Output"
        systems = Path(output_path).glob("System_*")
        results = {"energy": None}
        for system in systems:
            data_files = Path(system).glob("*.data")
            results[system.name] = {}
            for data_file in data_files:
                output = parse_output(data_file)
                results[system.name][data_file.name] = output
        return results

    def load_profile(self, cfg, **kwargs) -> RaspaProfile:
        """
        Load the RASPA profile.

        Parameters
        ----------
        cfg
            The ASE configuration profile, if any.
        **kwargs
            Any additional arguments to pass to the RASPA profile.

        Returns
        -------
        RaspaProfile
            The RASPA profile.
        """
        raise NotImplementedError


class Raspa(GenericFileIOCalculator):
    """
    The RASPA calculator.
    """

    def __init__(
        self,
        profile: RaspaProfile | None = None,
        directory: Path | str = ".",
        boxes: list[dict[str, Any]] | None = None,
        components: list[dict[str, Any]] | None = None,
        parameters: dict[str, Any] | None = None,
        multiple_frameworks: list[Atoms] | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the RASPA calculator. The $RASPA_DIR environment variable must
        be set.

        This calculator is to be set on an `Atoms` object, which will be the
        framework. All framework-related parameters should be set in the `Atoms.info`
        dictionary.

        If you have an ASE `Atoms` object of the MFI zeolite ("atoms"), then:

        ```python
        atoms.info = {"HeliumVoidFraction": 0.29}
        ```

        would be written out as the following:

        ```
        Framework 0
            FrameworkName framework0
            UnitCells 12 12 12
            HeliumVoidFraction 0.29
        ```

        The `FrameworkName` is automaticallly set by the calculator.
        The UnitCells parameter will be automatically set to prevent spurious
        interactions between periodic images based on the cutoff,
        if the parameter is not already supplied by the user.

        To use partial atomic charges on the framework, set the `Atoms.set_initial_charges`
        method on the `Atoms` object. The charges will be written out to the CIF file
        and `UseChargesFromCIFFile` will be set to `yes` in the `simulation.input` file.

        To use no framework, have the `Atoms` object be empty, i.e. `Atoms()`.

        Parameters
        ----------
        profile
            An instantiated [raspa_ase.calculator.RaspaProfile][] object to use.
            The default is typically fine, which runs the following:
            `$RASPA_DIR/bin/simulate simulation.input`.
        directory
            The path to the directory to run the RASPA calculation in, which
            defaults to the current working directory.
        boxes
            A list of dictionaries, where each dictionary is a RASPA box.
            The default is an empty list.

            Example:

            ```python
            boxes = [{"BoxLengths": [25, 25, 25], "ExternalTemperature": 300.0, "Movies": True, "WriteMoviesEvery": 10}, {"BoxLengths": [30, 30, 30], "BoxAngles": [90, 120, 90], "ExternalTemperature": 500.0, "Movies": True, "WriteMoviesEvery": 10}]
            Raspa(boxes=boxes)
            ```

            would be written out as the following from 4.2 Example 2 of the RASPA manual:

            ```
            Box 0
                BoxLengths 25 25 25
                ExternalTemperature 300.0
                Movies yes
                WriteMoviesEvery 10
            Box 1
                BoxLengths 30 30 30
                BoxAngles 90 120 90
                ExternalTemperature 500.0
                Movies yes
                WriteMoviesEvery 10
            ```
        components
            A list of dictionaries, where each dictionary is a RASPA component.
            The default is an empty list.

            Example:

            ```python
            components = [{"MolelculeName": "N2", "MoleculeDefinition": "ExampleDefinition", "TranslationProbability": 1.0, "RotationProbability": 1.0, "ReinsertionProbability": 1.0, "CreateNumberOfMolecules": [50, 25]}, {"MoleculeName": "CO2", "MoleculeDefinition": "ExampleDefinitions", "TranslationProbability": 1.0, "RotationProbability": 1.0, "ReinsertionProbability": 1.0, "CreateNumberOfMolecules": [25, 50]}]
            Raspa(components=components)
            ```

            would be written out as the following from 4.2 Example 2 of the RASPA manual:

            ```
            Component 0 MoleculeName N2
                MoleculeDefinition ExampleDefinitions
                TranslationProbability 1.0
                RotationProbability 1.0
                ReinsertionProbability 1.0
                CreateNumberOfMolecules 50 25
            Component 1 MoleculeName CO2
                MoleculeDefinition ExampleDefinitions
                TranslationProbability 1.0
                RotationProbability 1.0
                ReinsertionProbability 1.0
                CreateNumberOfMolecules 25 50
            ```
        parameters
            Any RASPA parameters beyond the Box and Component parameters, formatted as a dictionary.
            Booleans will be converted to "Yes" or "No" automatically, and lists will be converted to
            space-separated strings. The RASPA parameters are case-insensitive.

            Example:

            ```python
            parameters = {"SimulationType": "MonteCarlo", "NumberOfCycles": 10000, "NumberOfInitializationCycles": 1000, "PrintEvery": 100, "ForceField": "ExampleMoleculeForceField"}
            Raspa(parameters=parameters)
            ```

            would be written out as the following from 4.2 Example 2 of the RASPA manual:

            ```
            SimulationType MonteCarlo
            NumberOfCycles 10000
            NumberOfInitializationCycles 1000
            PrintEvery 100
            Forcefield ExampleMoleculeForceField
            ```
        multiple_frameworks
            If you need to use multiple frameworks, then special treatment is required. Instead of
            having the framework as the `Atoms` object, you need to supply a list of `Atoms` objects
            to the `multiple_frameworks` keyword argument. In this case, the `Atoms` object
            the calculator is applied to should be empty, i.e. `Atoms()`.

            Example:

            ```python
            atoms1 = read("my_framework1.cif")
            atoms2 = read("my_framework2.cif")
            atoms1.info = {"UnitCells": [1, 1, 1]}
            atoms2.info = {"HeliumVoidFraction": 0.25, "UnitCells": [4, 4, 4]}
            Raspa(multiple_frameworks=[atoms1, atoms2])
            ```

            would be written out as the following:

            ```
            Framework 0
                FrameworkName framework0
                UnitCells 1 1 1
            Framework 1
                FrameworkName framework1
                HeliumVoidFraction 0.25
                UnitCells 4 4 4
            ```
        **kwargs
            Any additional arguments to pass to the `GenericFileIO` calculator.

        Returns
        -------
        None
        """

        profile = profile or RaspaProfile()
        multiple_frameworks = multiple_frameworks or []
        boxes = boxes or []
        components = components or []
        parameters = parameters or {}

        parameters = merge_parameters(
            parameters, get_framework_params(multiple_frameworks)
        )
        for i, component in enumerate(components):
            molecule_name = pop_parameter(component, "MoleculeName")
            parameters = merge_parameters(
                parameters, {f"Component {i} MoleculeName {molecule_name}": component}
            )
        for i, box in enumerate(boxes):
            parameters = merge_parameters(parameters, {f"Box {i}": box})

        super().__init__(
            template=RaspaTemplate(frameworks=multiple_frameworks),
            profile=profile,
            directory=directory,
            parameters=parameters,
            **kwargs,
        )
