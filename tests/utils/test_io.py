from ase.build import bulk

from raspa_ase.utils.io import write_frameworks, write_simulation_input


def test_write_simulation_input(tmp_path):
    parameters = {"a": 1, "b": [2, 3], "c": {"d": 4, "e": False, "f": {"g": 5}}}
    input_filepath = tmp_path / "simulation.input"
    write_simulation_input(parameters, input_filepath)
    assert (
        input_filepath.read_text().strip()
        == "a 1\nb 2 3\nc\n    d 4\n    e No\n    f\n        g 5"
    )


def test_write_frameworks(tmp_path):
    frameworks = [bulk("Cu"), bulk("Cu")]
    write_frameworks(frameworks, tmp_path)
    assert (tmp_path / "framework0.cif").exists()
    assert (tmp_path / "framework1.cif").exists()
