import os
from pathlib import Path

import pytest
from ase import Atoms
from ase.build import bulk

from raspa_ase.calculator import Raspa, RaspaProfile, RaspaTemplate


def test_profile_bad(monkeypatch):
    monkeypatch.delenv("RASPA_DIR", "/tmp")
    with pytest.raises(OSError):
        RaspaProfile()


def test_profile():
    profile = RaspaProfile()
    assert profile.argv == [
        f"{os.getenv('RASPA_DIR')}/bin/simulate",
        "simulation.input",
    ]


def test_profile2():
    profile = RaspaProfile(argv=["test"])
    assert profile.argv == ["test"]


def test_run(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    RaspaProfile().run(tmp_path, tmp_path / "simulation.input")


def test_template():
    template = RaspaTemplate()
    assert template.input_file == "simulation.input"
    assert template.output_file == "raspa.out"


def test_template_execute(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    template = RaspaTemplate()
    template.execute(tmp_path, RaspaProfile())


def test_template_write_input(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    template = RaspaTemplate()
    template.write_input(
        tmp_path, bulk("Cu"), {"CutOff": 12.8}, RaspaProfile(), "energy"
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
        == "CutOff 12.8\nComponent 0 MoleculeName N2\n    MoleculeDefinition ExampleDefinition\nComponent 1 MoleculeName CO2\n    MoleculeDefinition ExampleDefinition\n    TranslationProbability 1.0\nBox 0\n    BoxLengths 1 2 3\nBox 1\n    BoxLengths 4 5 6\nFramework 0\n    FrameworkName framework0\n    UnitCells 12 12 12\n"
    )


def test_multi_frameworks(tmp_path):
    atoms1 = bulk("Cu")
    atoms1.info = {"HeliumVoidFraction": 0.75}
    atoms2 = bulk("Fe")
    atoms = Atoms()
    atoms.calc = Raspa(directory=tmp_path, multiple_frameworks=[atoms1, atoms2])
    atoms.get_potential_energy()
    assert Path(tmp_path, "simulation.input").exists()
    assert (
        Path(tmp_path / "simulation.input").read_text()
        == "Framework 0\n    FrameworkName framework0\n    UnitCells 12 12 12\n    HeliumVoidFraction 0.75\nFramework 1\n    FrameworkName framework1\n    UnitCells 12 12 12\n"
    )
