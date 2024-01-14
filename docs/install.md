# Installation

## RASPA

First, install RASPA based on the [official instructions](https://iraspa.org/raspa/) and set the `$RASPA_DIR` environment variable as instructed.

!!! Tip

    Don't forget the `make install` step at the end!

## ASE Calculator

To install `raspa_ase`, install the latest version of ASE followed by the latest version of `raspa_ase` as follows:

```
pip install --force-reinstall --no-deps https://gitlab.com/ase/ase/-/archive/master/ase-master.zip
pip install git+https://github.com/Quantum-Accelerators/raspa_ase.git
```
