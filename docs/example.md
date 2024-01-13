# Examples

In this section, I provide the necessary inputs to run several of the examples in [section 4.2 of the RASPA manual](https://iraspa.org/download/raspa-manual-23-may-2021/).

!!! Tip

    Pre-tabulated force fields and molecule definition files can be found in the [`share`](https://github.com/Quantum-Accelerators/raspa_ase/tree/main/share) directory.

## Example 1: Monte Carlo of Methane in a Box

```python
from ase import Atoms
from raspa_ase import Raspa

atoms = Atoms()  # no framework
boxes = [
    {
        "BoxLengths": [30, 30, 30],
        "ExternalTemperature": 300,
        "Movies": True,
        "WriteMoviesEvery": 100,
    }
]
components = [
    {
        "MoleculeName": "methane",
        "MoleculeDefinition": "ExampleDefinitions",
        "TranslationProbability": 1.0,
        "CreateNumberOfMolecules": 100,
    }
]
parameters = {
    "SimulationType": "MonteCarlo",
    "NumberOfCycles": 10000,
    "NumberOfInitializationCycles": 1000,
    "PrintEvery": 1000,
    "Forcefield": "ExampleMoleculeForceField",
}
calc = Raspa(boxes=boxes, components=components, parameters=parameters)

atoms.calc = calc
atoms.get_potential_energy()
```

## Example 2: Monte Carlo of CO2 in a Box and N2 in Another Box

```python
from ase import Atoms
from raspa_ase import Raspa

atoms = Atoms()  # no framework
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
```

## Example 7: Adsorption isotherm of methane in MFI

```python

```

## Example 8: Adsorption isotherm of CO2 in Cu-BTC

```python

```
