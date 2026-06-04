# greenhouse_m5

Simple loaders and notebooks for analysing PlantEye derived CSV files from NPEC greenhouse Module 5.

The main data is here:

```text
<path-to-your-data-folder>\PlantEye\derived
```

Those CSV files are the core of the analysis. The code does not calculate traits from point clouds; it reads the traits already exported by the PlantEye/NPEC pipeline.

## Set The Data Path

Open [paths.py](src/greenhouse_m5/paths.py) and edit this line if your data folder is somewhere else:

```python
DATA_ROOT = Path(r"<path-to-your-data-folder>")
```

You can also override the path in code:

```python
from greenhouse_m5 import load_measured_traits

traits = load_measured_traits(data_root=r"<path-to-your-data-folder>")
```

## Setup Python

Before running the notebooks, decide which Python installation you want to use. Ask where the Python environment is installed, then replace `<path-to-python.exe>` with the full path to that Python executable.

Create a virtual environment in this project folder:

```powershell
cd <path-to-greenhouse_m5>
& '<path-to-python.exe>' -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install this project and the notebook tools:

```powershell
python -m pip install -e .[notebook,test]
```

Register the virtual environment as a Jupyter kernel:

```powershell
python -m ipykernel install --user --name greenhouse-m5 --display-name "greenhouse-m5"
```

Then open the notebook and select the `greenhouse-m5` kernel.

For PlantEye derived CSV analysis you do not need `spectral` or `scipy`. Those packages are only relevant for the old Snapscan hyperspectral examples.

If you already have an environment and do not want a new virtual environment, install into that environment instead:

```powershell
& '<path-to-python.exe>' -m pip install -e .[notebook,test]
```

## Start Analysis

```python
from greenhouse_m5 import (
    load_average_indices,
    load_histogram,
    load_measured_traits,
    load_phenotypic_data,
    load_voxel_volume,
)

traits = load_measured_traits()
traits_without_empty_pots = load_phenotypic_data(include_empty=False)
average_indices = load_average_indices()
voxel_volume = load_voxel_volume()
ndvi_histogram = load_histogram("ndvi")
```

## CSV Files Loaded

The package reads these files from `PlantEye/derived`:

- `<experiment_id>_measured_traits.csv`
- `<experiment_id>_averages_of_all_indices.csv`
- `<experiment_id>_voxel_volume.csv`
- `<experiment_id>_greenness.csv`
- `<experiment_id>_hue.csv`
- `<experiment_id>_ndvi.csv`
- `<experiment_id>_npci.csv`
- `<experiment_id>_psri.csv`

## Important Columns

`<experiment_id>_measured_traits.csv` contains the most important PlantEye traits:

- `height`, `height_max`
- `area_3d`
- `leaf_area_index`
- `digital_biomass`
- `leaf_angle`, `leaf_inclination`
- `proj_area`
- `light_pen_depth`

The original CSV column `Treatment` is the PlantEye scan treatment id. The loader renames it to `ScanTreatmentId`.

Biological metadata is parsed from the `sample` name:

```text
NPEC33.20260330.LU1.BIV.D_JA.1
```

This becomes:

- `Position`: `LU1`
- `Genotype`: `BIV`
- `Treatment`: `D_JA`
- `Replicate`: `1`

Rows where genotype or treatment is `empty` get `IsEmptyPot = True`.

## Histograms

The histogram files contain one special row where `sample == "edges"`. `load_histogram()` separates this row:

```python
histogram = load_histogram("greenness")

histogram.edges  # bin edges
histogram.data   # real sample rows
```

## Tests

Run fast tests:

```powershell
& '<path-to-python.exe>' -m pytest -q
```

Run tests against the real data:

```powershell
$env:M5_DATA_ROOT='<path-to-your-data-folder>'
& '<path-to-python.exe>' -m pytest -q
```

## Notebooks

- `planteye/planteye.ipynb`: current PlantEye derived CSV analysis.
- `snapscan/...`: Snapscan examples only.
- `RGB_sideview/...`: RGB side-view example only.
