# Overview

The calculator is quite straightforward to use. For details on each parameter, refer to the RASPA manual.

## Instantiating and Running the Calculator

The calculator is applied to an `Atoms` object, representing the framework under investigation. To run a RASPA calculator, call the `.get_potential_energy()` method like so:

```python
from ase.io import read
from raspa_ase import Raspa

atoms = read("my_framework.cif")
atoms.calc = Raspa(boxes=..., components=..., parameters=...)
atoms.get_potential_energy()
print(calc.results)
```

Tabulated results can be found in the `calc.results` dictionary.

## Framework Properties

### Defining the Structure

The calculator is applied to an `Atoms` object, which is the framework to be included in your system. If you want to run a calculation without a framework (i.e. with just a box of molecules), you can use an empty `Atoms` object, defined as `Atoms()`.

### Defining the Framework Properties

For framework-specific properties, they should be attached to the `Atoms` object's `.info` attribute.

For instance:

```python
atoms.info["HeliumVoidFraction"] = 0.149
```

would be equivalent to

```
Framework 0
    FrameworkName framework0
    HeliumVoidFraction 0.149
```

!!! Note

    You never need to specify the framework number or the framework name, and the the CIF will be automatically written out for you based on the `Atoms` object.

### Framework Charges

If you want to run a calculation with partial atomic charges on the framework, you can set the initial charges:

For instance:

```python
atoms.set_initial_charges([1.0, 2.0])
```

would write out the `_atom_site_charge` column in the CIF as 1.0 and 2.0 for atom indices 0 and 1, respectively. It will also automatically set "UseChargesFromCIFFile" to "Yes" in the `simulation.input` file.

### Framework Unit Cells

If you don't specify a "UnitCells" entry in `atoms.info`, the RASPA calculator will ensure that the minimum image convention is satisfied based on your "CutOff" value. If a "CutOff" is not specified, the number of unit cells will be set based on a value of 12.0 Å for the cutoff.

### Multiple Frameworks

If you need to use multiple frameworks in your simulation, you should apply the calculator to a blank `Atoms` object (i.e. `Atoms()`) and pass a `list[Atoms]` to the `multiple_frameworks` keyword argument.

## Boxes

The optional `boxes` keyword argument, of type `list[dict]`, is a list where each entry is a given set of box parameters formatted as a dictionary.

For instance:

```python
boxes = [
    {"BoxLengths": [30, 30, 30]},
    {"BoxLengths": [40, 40, 40], "BoxAngles": [90, 120, 120]},
]
calc = Raspa(boxes=boxes)
```

is equivalent to

```
Box 0
    BoxLengths 30 30 30
Box 1
    BoxLengths 40 40 40
    BoxAngles 90 120 120
```

!!! Note

    You never need to specify the box number. This is determined based on the index of the box in the list.

## Components

The optional `components` keyword argument, of type `list[dict]`, is a list where each entry is a given set of component parameters formatted as a dictionary.

For instance:

```python
components = [
    {"MoleculeName": "CO2", "MoleculeDefinition": "ExampleDefinitions"},
    {"MoleculeName": "N2", "MoleculeDefinition": "ExampleDefinitions"},
]
calc = Raspa(components=components)
```

is equivalent to

```
Component 0 MoleculeName CO2
    MoleculeDefinition ExampleDefinitions
Component 1 MoleculeName N2
    MoleculeDefinition ExampleDefinitions
```

!!! Note

    You never need to specify the component number. This is determined based on the index of the component in the list. The "MoleculeName" will also be formatted automatically for you.

## Remaining Parameters

The optional `parameters` keyword argument, of type `dict`, is a dictionary of all other parameters to be passed to RASPA.

For instance:

```python
parameters = {
    "SimulationType": "MonteCarlo",
    "NumberOfCycles": 10000,
    "NumberOfInitializationCycles": 1000,
    "Movies": True,
}
calc = Raspa(parameters=parameters)
```

is equivalent to

```
SimulationType MonteCarlo
NumberOfCycles 10000
NumberOfInitializationCycles 1000
Movies Yes
```

!!! Note

    The parameters are case-insensitive, booleans will be converted to "Yes" or "No" as appropriate, lists will be converted to space-separated strings, and dictionaries will be converted to properly formatted key-value pairs.
