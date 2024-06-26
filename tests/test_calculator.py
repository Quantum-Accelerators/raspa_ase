import os
from pathlib import Path

import pytest
from ase import Atoms
from ase.build import bulk
from ase.io import read

from raspa_ase.calculator import Raspa, RaspaProfile, RaspaTemplate

DATA_DIR = Path(__file__).parent / "data"


def test_profile_bad(monkeypatch):
    monkeypatch.delenv("RASPA_DIR", "/tmp")
    with pytest.raises(OSError):
        RaspaProfile()


def test_profile():
    profile = RaspaProfile()
    assert profile.command == f"{os.getenv('RASPA_DIR')}/bin/simulate"

    assert profile.get_calculator_command() == [
        f"{os.getenv('RASPA_DIR')}/bin/simulate",
        "simulation.input",
    ]

    with pytest.raises(NotImplementedError):
        profile.version()


def test_profil2e():
    profile = RaspaProfile(command="my/path")
    assert profile.command == "my/path"

    assert profile.get_calculator_command() == [
        "my/path",
        "simulation.input",
    ]


def test_template():
    template = RaspaTemplate()
    assert template.inputname == "simulation.input"
    assert template.outputname == "raspa.stdout"
    assert template.errorfile == "raspa.stderr"


def test_notimplemented():
    template = RaspaTemplate()
    with pytest.raises(NotImplementedError):
        template.load_profile(None)


def test_template_execute(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with Path(tmp_path / "simulation.input").open(mode="w") as fd:
        fd.write("")
    template = RaspaTemplate()
    template.execute(tmp_path, RaspaProfile())


def test_template_write_input(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    template = RaspaTemplate()
    template.write_input(
        RaspaProfile(), tmp_path, bulk("Cu"), {"CutOff": 12.8}, "energy"
    )
    assert (tmp_path / "simulation.input").exists()
    assert (
        tmp_path / "simulation.input"
    ).read_text() == "CutOff 12.8\nFramework 0\n    FrameworkName framework0\n    UnitCells 12 12 12\n"
    assert (tmp_path / "framework0.cif").exists()


def test_template_read_results():
    template = RaspaTemplate()
    assert template.read_results(".") == {"energy": None}


def test_raspa_blank():
    calc = Raspa()
    assert calc.directory == Path(".")
    assert calc.parameters == {}


def test_raspa_parameters():
    calc = Raspa(parameters={"CutOff": 12.8})
    assert calc.parameters == {"CutOff": 12.8}


def test_raspa_boxes():
    calc = Raspa(boxes=[{"BoxLengths": [1, 2, 3]}, {"BoxLengths": [4, 5, 6]}])
    assert calc.parameters == {
        "Box 0": {"BoxLengths": [1, 2, 3]},
        "Box 1": {"BoxLengths": [4, 5, 6]},
    }


def test_raspa_components():
    calc = Raspa(
        components=[
            {"MoleculeName": "N2", "MoleculeDefinition": "ExampleDefinition"},
            {
                "MoleculeName": "CO2",
                "MoleculeDefinition": "ExampleDefinition",
                "TranslationProbability": 1.0,
            },
        ]
    )
    assert calc.parameters == {
        "Component 0 MoleculeName N2": {"MoleculeDefinition": "ExampleDefinition"},
        "Component 1 MoleculeName CO2": {
            "MoleculeDefinition": "ExampleDefinition",
            "TranslationProbability": 1.0,
        },
    }


def test_raspa_functional1(tmp_path):
    atoms = Atoms()
    atoms.calc = Raspa(directory=tmp_path)
    atoms.get_potential_energy()
    assert Path(tmp_path / "simulation.input").exists()
    assert Path(tmp_path / "simulation.input").read_text() == ""


def test_raspa_functional2(tmp_path):
    atoms = bulk("Cu")
    atoms.set_initial_charges([1.0] * len(atoms))
    atoms.calc = Raspa(
        directory=tmp_path,
        boxes=[{"BoxLengths": [1, 2, 3]}, {"BoxLengths": [4, 5, 6]}],
        parameters={"CutOff": 12.8},
        components=[
            {"MoleculeName": "N2", "MoleculeDefinition": "ExampleDefinition"},
            {
                "MoleculeName": "CO2",
                "MoleculeDefinition": "ExampleDefinition",
                "TranslationProbability": 1.0,
            },
        ],
    )
    atoms.get_potential_energy()
    assert Path(tmp_path, "simulation.input").exists()
    assert (
        Path(tmp_path / "simulation.input").read_text()
        == "CutOff 12.8\nComponent 0 MoleculeName N2\n    MoleculeDefinition ExampleDefinition\nComponent 1 MoleculeName CO2\n    MoleculeDefinition ExampleDefinition\n    TranslationProbability 1.0\nBox 0\n    BoxLengths 1 2 3\nBox 1\n    BoxLengths 4 5 6\nFramework 0\n    FrameworkName framework0\n    UnitCells 12 12 12\n    UseChargesFromCIFFile Yes\n"
    )


def test_multi_frameworks(tmp_path):
    atoms1 = bulk("Cu")
    atoms1.info = {"HeliumVoidFraction": 0.75}
    atoms2 = bulk("Fe")
    atoms = Atoms()
    atoms.calc = Raspa(
        directory=tmp_path,
        multiple_frameworks=[atoms1, atoms2],
        boxes=[{"BoxLengths": [1, 2, 3]}, {"BoxLengths": [4, 5, 6]}],
        parameters={"CutOff": 12.8},
        components=[
            {"MoleculeName": "N2", "MoleculeDefinition": "ExampleDefinition"},
            {
                "MoleculeName": "CO2",
                "MoleculeDefinition": "ExampleDefinition",
                "TranslationProbability": 1.0,
            },
        ],
    )
    atoms.get_potential_energy()
    assert Path(tmp_path, "simulation.input").exists()
    input_str = Path(tmp_path / "simulation.input").read_text()
    assert (
        "Framework 0\n    FrameworkName framework0\n    UnitCells 12 12 12\n    HeliumVoidFraction 0.75\n"
        in input_str
    )
    assert (
        "Framework 1\n    FrameworkName framework1\n    UnitCells 12 12 12\n"
        in input_str
    )
    assert Path(tmp_path / "framework0.cif").exists()
    assert Path(tmp_path / "framework1.cif").exists()
    assert read(tmp_path / "framework0.cif")[0].symbol == "Cu"
    assert read(tmp_path / "framework1.cif")[0].symbol == "Fe"


@pytest.mark.skipif("RASPA_DIR" not in os.environ, reason="This test requires RASPA")
def test_example(tmp_path):
    atoms = Atoms()
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
        "NumberOfCycles": 100,
        "NumberOfInitializationCycles": 10,
        "PrintEvery": 10,
        "Forcefield": "ExampleMoleculeForceField",
    }
    calc = Raspa(
        directory=tmp_path, boxes=boxes, components=components, parameters=parameters
    )

    atoms.calc = calc
    atoms.get_potential_energy()
    assert "System_0" in calc.results
    assert "output_Box_1.1.1_300.000000_0.data" in calc.results["System_0"]
    assert calc.results["System_0"]["output_Box_1.1.1_300.000000_0.data"]["Simulation"][
        "Dimensions"
    ] == [3.0]


@pytest.mark.skipif("RASPA_DIR" not in os.environ, reason="This test requires RASPA")
def test_example2(tmp_path):
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
        "NumberOfCycles": 20,
        "NumberOfInitializationCycles": 10,
        "PrintEvery": 10,
        "Forcefield": "ExampleMoleculeForceField",
    }
    calc = Raspa(
        directory=tmp_path, boxes=boxes, components=components, parameters=parameters
    )

    atoms.calc = calc
    atoms.get_potential_energy()
    assert "System_0" in calc.results
    assert "System_1" in calc.results
    assert "output_Box_1.1.1_300.000000_0.data" in calc.results["System_0"]
    assert "output_Box_1.1.1_500.000000_0.data" in calc.results["System_1"]


@pytest.mark.skipif("RASPA_DIR" not in os.environ, reason="This test requires RASPA")
def test_example3(tmp_path):
    atoms = read(Path(DATA_DIR / "MFI_SI.cif"))
    atoms.info = {
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
        "NumberOfCycles": 25,
        "NumberOfInitializationCycles": 2,
        "PrintEvery": 5,
        "Forcefield": "ExampleZeolitesForceField",
        "RemoveAtomNumberCodeFromLabel": True,
        "ComputeNumberOfMoleculesHistogram": True,
        "WriteNumberOfMoleculesHistogramEvery": 5,
        "NumberOfMoleculesHistogramSize": 5,
        "NumberOfMoleculesRange": 5,
        "ComputeEnergyHistogram": True,
        "WriteEnergyHistogramEvery": 5,
        "EnergyHistogramSize": 5,
        "EnergyHistogramLowerLimit": -110000,
        "EnergyHistogramUpperLimit": -20000,
    }
    calc = Raspa(directory=tmp_path, components=components, parameters=parameters)

    atoms.calc = calc
    atoms.get_potential_energy()
    assert "System_0" in calc.results
    assert "output_framework0_2.2.2_300.000000_10000.data" in calc.results["System_0"]
    assert "output_framework0_2.2.2_300.000000_100000.data" in calc.results["System_0"]
