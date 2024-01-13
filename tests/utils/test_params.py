from ase.build import bulk

from raspa_ase.utils.params import get_framework_params, get_suggested_cells


def test_get_suggested_cells():
    assert get_suggested_cells(bulk("Cu"), cutoff=12) == [12, 12, 12]
    assert get_suggested_cells(bulk("Cu"), cutoff=4) == [4, 4, 4]


def test_get_framework_params():
    frameworks = [bulk("Cu"), bulk("Cu")]
    frameworks[0].info = {"HeliumVoidFraction": 0.75}
    frameworks[1].info = {"UnitCells": [1, 2, 3]}
    framework_params = get_framework_params(frameworks)
    assert "Framework 0" in framework_params
    assert "Framework 1" in framework_params
    assert framework_params["Framework 0"] == {
        "FrameworkName": "framework0",
        "UnitCells": [12, 12, 12],
        "HeliumVoidFraction": 0.75,
    }
    assert framework_params["Framework 1"] == {
        "FrameworkName": "framework1",
        "UnitCells": [1, 2, 3],
    }
