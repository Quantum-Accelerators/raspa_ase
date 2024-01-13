# Example

In this section, I provide the necessary inputs to run several of the examples in section 4.2 of the RASPA manual.

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

```

## Example 7: Adsorption isotherm of methane in MFI

```python

```

## Example 8: Adsorption isotherm of CO2 in Cu-BTC

```python

```
