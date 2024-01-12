# Installation

## RASPA

First, install RASPA based on the [official instructions](https://iraspa.org/raspa/).

For most users, this can be done as follows.

```
git clone https://github.com/iRASPA/RASPA2.git
export RASPA_DIR=/path/to/RASPA2  # (1)!
```

1. In practice, you will likely want to define the `RASPA_DIR` environment variable in your `~/.bashrc`.

```
make clean
./configure --prefix=${RASPA_DIR}
make
make install
```

For additional compilation details, refer to the RASPA manual.

## `raspa_ase`

To install `raspa_ase`, install the latest version of ASE followed by the latest version of `raspa_ase` as follows:

```
pip install --force-reinstall --no-deps https://gitlab.com/ase/ase/-/archive/master/ase-master.zip
pip install git+https://github.com/Quantum-Accelerators/raspa_ase.git
```
