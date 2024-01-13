"""Init data"""
from __future__ import annotations

from importlib.metadata import version

from raspa_ase.calculator import Raspa

__all__ = ["Raspa"]

# Load the version
__version__ = version("raspa_ase")
