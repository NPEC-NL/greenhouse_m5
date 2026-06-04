"""Small loaders for PlantEye derived CSV analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .paths import resolve_data_root

TIMESTAMP_FORMAT = "%Y%m%dT%H%M%S"
HISTOGRAM_INDICES = ("greenness", "hue", "ndvi", "npci", "psri")


@dataclass(frozen=True)
class HistogramData:
    """A histogram file split into bin edges and measurement rows."""

    index: str
    edges: pd.Series
    data: pd.DataFrame
    raw: pd.DataFrame

    @property
    def bin_columns(self) -> list[str]:
        return [column for column in self.raw.columns if column.startswith("bin_")]


def derived_folder(data_root: str | Path | None = None) -> Path:
    """Return ``Data/PlantEye/derived``."""

    folder = resolve_data_root(data_root) / "PlantEye" / "derived"
    if not folder.exists():
        raise FileNotFoundError(folder)
    return folder


def _derived_file(data_root: str | Path | None, experiment_id: int, name: str) -> Path:
    path = derived_folder(data_root) / f"{experiment_id}_{name}.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", decimal=",")


def _parse_timestamp(data: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in data.columns:
        data = data.copy()
        data["timestamp_text"] = data["timestamp"].astype(str)
        data["timestamp"] = pd.to_datetime(data["timestamp"], format=TIMESTAMP_FORMAT, errors="coerce")
    return data


def parse_sample_metadata(sample: str) -> dict[str, object]:
    """Parse metadata from names like ``NPEC33.20260330.LU1.BIV.D_JA.1``."""

    parts = str(sample).split(".")
    result: dict[str, object] = {
        "Position": pd.NA,
        "Genotype": pd.NA,
        "Treatment": pd.NA,
        "Replicate": pd.NA,
    }
    if len(parts) >= 6:
        result["Position"] = parts[2]
        result["Genotype"] = parts[3]
        result["Treatment"] = parts[4]
        try:
            result["Replicate"] = int(parts[5])
        except ValueError:
            result["Replicate"] = parts[5]
    return result


def add_sample_metadata(data: pd.DataFrame, sample_column: str = "sample") -> pd.DataFrame:
    """Add position, genotype, treatment, replicate, and empty-pot flag."""

    if sample_column not in data.columns:
        return data
    parsed = pd.DataFrame([parse_sample_metadata(value) for value in data[sample_column]], index=data.index)
    result = data.copy()
    for column in parsed.columns:
        result[column] = parsed[column]
    result["IsEmptyPot"] = result["Genotype"].eq("empty") | result["Treatment"].eq("empty")
    return result


def load_measured_traits(data_root: str | Path | None = None, experiment_id: int = 46) -> pd.DataFrame:
    """Load ``46_measured_traits.csv`` from ``PlantEye/derived``."""

    data = _read_csv(_derived_file(data_root, experiment_id, "measured_traits"))
    if "Treatment" in data.columns:
        data = data.rename(columns={"Treatment": "ScanTreatmentId"})
    return add_sample_metadata(_parse_timestamp(data))


def load_phenotypic_data(
    data_root: str | Path | None = None,
    experiment_id: int = 46,
    *,
    include_empty: bool = True,
) -> pd.DataFrame:
    """Load measured traits, optionally excluding empty pots."""

    data = load_measured_traits(data_root, experiment_id)
    if not include_empty:
        data = data[~data["IsEmptyPot"]].reset_index(drop=True)
    return data


def load_average_indices(data_root: str | Path | None = None, experiment_id: int = 46) -> pd.DataFrame:
    """Load ``46_averages_of_all_indices.csv`` from ``PlantEye/derived``."""

    data = _read_csv(_derived_file(data_root, experiment_id, "averages_of_all_indices"))
    return add_sample_metadata(_parse_timestamp(data))


def load_voxel_volume(data_root: str | Path | None = None, experiment_id: int = 46) -> pd.DataFrame:
    """Load ``46_voxel_volume.csv`` from ``PlantEye/derived``."""

    data = _read_csv(_derived_file(data_root, experiment_id, "voxel_volume"))
    return add_sample_metadata(_parse_timestamp(data))


def load_histogram(
    index: str,
    data_root: str | Path | None = None,
    experiment_id: int = 46,
) -> HistogramData:
    """Load one index histogram and split the ``sample == 'edges'`` row."""

    index = index.lower()
    if index not in HISTOGRAM_INDICES:
        raise ValueError(f"Unsupported histogram index {index!r}; expected one of {HISTOGRAM_INDICES}")

    raw = _read_csv(_derived_file(data_root, experiment_id, index))
    bin_columns = [column for column in raw.columns if column.startswith("bin_")]
    edge_rows = raw[raw["sample"] == "edges"]
    edges = (
        edge_rows.iloc[0][bin_columns].astype(float)
        if not edge_rows.empty
        else pd.Series(dtype="float64")
    )
    edges.name = index

    data = raw[raw["sample"] != "edges"].copy().reset_index(drop=True)
    data = add_sample_metadata(_parse_timestamp(data))
    return HistogramData(index=index, edges=edges, data=data, raw=raw)


def load_histograms(
    data_root: str | Path | None = None,
    experiment_id: int = 46,
    indices: tuple[str, ...] = HISTOGRAM_INDICES,
) -> dict[str, HistogramData]:
    """Load all PlantEye histogram files by default."""

    return {index: load_histogram(index, data_root, experiment_id) for index in indices}
