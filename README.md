# StokesMOST tests

Test cases for StokesMOST in [GOTM](https://gotm.net).

## Quick start

### Configure the gotmtool environment

Notebooks in this repository use the python tool [gotmtool](https://github.com/qingli411/gotmtool), which is included as a submodule.
Use
```
git submodule update --init --recursive
```
to check out the submodule.

Go to the gotmtool folder.
```
cd gotmtool
```

Follow the instructions in `README.md` or [here](https://github.com/qingli411/gotmtool) to set up the gotmtool environment. When prompted for input of GOTM source code repository and branch, type in `https://github.com/qingli411/code.git` for the repository and `stokes_most` for the branch name. You will see something like the following.

```
Download GOTM source code from a git repository? Type in 'y' to confirm and 'n' to skip: (n)
y
Repository URL: (https://github.com/gotm-model/code.git)
https://github.com/qingli411/code.git
Branch name: (master)
stokes_most
```

### Run the test cases

Run the notebook `run.ipynb` in the test case folder to run GOTM and the notebook `plot.ipynb` to visualize the results. For some cases, the notebook `preprocess_data.ipynb` and data information file `data.yaml` to prepare the surface forcing and initial condition data for GOTM are also included.
