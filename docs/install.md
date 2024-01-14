# Installation

## RASPA

First, install RASPA based on the [official instructions](https://iraspa.org/raspa/) and set the `$RASPA_DIR` environment variable as instructed.

??? Tip "Can't find the `bin` folder?

    Don't forget the `make install` step at the end!

## ASE Calculator

To use `raspa_ase`, first install the latest version of ASE:

```bash
pip install --force-reinstall --no-deps https://gitlab.com/ase/ase/-/archive/master/ase-master.zip
```

Then install `raspa_ase`:

```bash
pip install git+https://github.com/Quantum-Accelerators/raspa_ase.git
```
