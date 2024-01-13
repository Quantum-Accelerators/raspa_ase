import pytest

from raspa_ase.calculator import RaspaProfile


def mock_run(self, *args, **kwargs):
    return None


@pytest.fixture(autouse=True)
def patch_get_potential_energy(monkeypatch):
    monkeypatch.setattr(RaspaProfile, "run", mock_run)


@pytest.fixture(autouse=True)
def env_set(monkeypatch):
    monkeypatch.setenv("RASPA_DIR", ".")
