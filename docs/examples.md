# Examples

In this section, we provide the necessary inputs to run several of the examples in [section 4.2 of the RASPA manual](https://iraspa.org/download/raspa-manual-23-may-2021/).

!!! Tip

    Pre-tabulated force fields and molecule definition files can be found in the [`share`](https://github.com/Quantum-Accelerators/raspa_ase/tree/main/share) directory.

## Example 1: Monte Carlo of Methane in a Box

```python
from ase import Atoms
from raspa_ase import Raspa

atoms = Atoms()  #  (1)!
boxes = [  #  (2)!
    {
        "BoxLengths": [30, 30, 30],
        "ExternalTemperature": 300,
        "Movies": True,  # (3)!
        "WriteMoviesEvery": 100,
    }
]
components = [  # (4)!
    {
        "MoleculeName": "methane",
        "MoleculeDefinition": "ExampleDefinitions",
        "TranslationProbability": 1.0,
        "CreateNumberOfMolecules": 100,
    }
]
parameters = {  # (5)!
    "SimulationType": "MonteCarlo",
    "NumberOfCycles": 10000,
    "NumberOfInitializationCycles": 1000,
    "PrintEvery": 1000,
    "Forcefield": "ExampleMoleculeForceField",
}
calc = Raspa(boxes=boxes, components=components, parameters=parameters)

atoms.calc = calc
atoms.get_potential_energy()
print(calc.results)
```

1. Use an empty `Atoms` object to create a system without a framework.

2. You do not need to specify the box number. It will be determined automatically based on the order in which the components are listed. We define the box parameters as a dictionary to be provided to the `boxes` keyword argument.

3. `True` and `False` will be automatically translated to "Yes" and "No", respectively.

4. You do not need to specify the component number. It will be determined automatically based on the order in which the components are listed. We define the component parameters as a dictionary to be provided to the `components` keyword argument.

5. The remaining force field parameters (i.e. all those beyond the box, component, and framework parameters) are to be specified as a dictionary to be provided to the `parameters` keyword argument.

## Example 2: Monte Carlo of CO2 in a Box and N2 in Another Box

```python
from ase import Atoms
from raspa_ase import Raspa

atoms = Atoms()
boxes = [
    {
        "BoxLengths": [25, 25, 25],
        "ExternalTemperature": 300.0,
        "Movies": True,
        "WriteMoviesEvery": 10,
    },
    {
        "BoxLengths": [30, 30, 30],
        "BoxAngles": [90, 120, 120],
        "ExternalTemperature": 500,
        "Movies": True,
        "WriteMoviesEvery": 10,
    },
]
components = [
    {
        "MoleculeName": "N2",
        "MoleculeDefinition": "ExampleDefinitions",
        "TranslationProbability": 1.0,
        "RotationProbability": 1.0,
        "ReinsertionProbability": 1.0,
        "CreateNumberOfMolecules": [50, 25],
    },
    {
        "MoleculeName": "CO2",
        "MoleculeDefinition": "ExampleDefinitions",
        "TranslationProbability": 1.0,
        "RotationProbability": 1.0,
        "ReinsertionProbability": 1.0,
        "CreateNumberOfMolecules": [25, 50],
    },
]
parameters = {
    "SimulationType": "MonteCarlo",
    "NumberOfCycles": 10000,
    "NumberOfInitializationCycles": 1000,
    "PrintEvery": 100,
    "Forcefield": "ExampleMoleculeForceField",
}
calc = Raspa(boxes=boxes, components=components, parameters=parameters)

atoms.calc = calc
atoms.get_potential_energy()
print(calc.results)
```

## Example 7: Adsorption isotherm of methane in MFI

```python
from ase.io import read
from raspa_ase import Raspa

atoms = read("MFI_SI.cif")  # (1)!
atoms.info = {  # (2)!
    "UnitCells": [2, 2, 2],
    "HeliumVoidFraction": 0.29,
    "ExternalTemperature": 300.0,
    "ExternalPressure": [1e4, 1e5],
}
components = [
    {
        "MoleculeName": "methane",
        "MoleculeDefinition": "ExampleDefinitions",
        "TranslationProbability": 0.5,
        "ReinsertionProbability": 0.5,
        "SwapProbability": 1.0,
        "CreateNumberOfMolecules": 0,
    }
]
parameters = {
    "SimulationType": "MonteCarlo",
    "NumberOfCycles": 25000,
    "NumberOfInitializationCycles": 2000,
    "PrintEvery": 1000,
    "Forcefield": "ExampleZeolitesForceField",
    "RemoveAtomNumberCodeFromLabel": True,
    "ComputeNumberOfMoleculesHistogram": True,
    "WriteNumberOfMoleculesHistogramEvery": 5000,
    "NumberOfMoleculesHistogramSize": 1100,
    "NumberOfMoleculesRange": 80,
    "ComputeEnergyHistogram": True,
    "WriteEnergyHistogramEvery": 5000,
    "EnergyHistogramSize": 400,
    "EnergyHistogramLowerLimit": -110000,
    "EnergyHistogramUpperLimit": -20000,
}
calc = Raspa(components=components, parameters=parameters)

atoms.calc = calc
atoms.get_potential_energy()
print(calc.results)
```

1. This file is provided in [`raspa_ase/docs/files/MFI_SI.cif`](https://github.com/Quantum-Accelerators/raspa_ase/blob/main/docs/files/MFI_SI.cif) for the sake of this tutorial. The `Atoms` object represents the framework to be studied and will be written out to the current working directory to be used by RASPA.

2. The framework parameters are to be specified as `info` attributes of the `Atoms` object. You do not need to include the framework number or framework name. These will be included automatically.
