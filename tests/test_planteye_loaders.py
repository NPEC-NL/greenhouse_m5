from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from greenhouse_m5.planteye import (
    HISTOGRAM_INDICES,
    load_histogram,
    load_measured_traits,
    parse_sample_metadata,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _minimal_data_root(tmp_path: Path) -> Path:
    root = tmp_path / "Data"
    _write(
        root / "PlantEye" / "derived" / "46_measured_traits.csv",
        "\n".join(
            [
                "timestamp;sample;height;area_3d;leaf_area_index;proj_area;Treatment;Experiment",
                "20260413T115530;NPEC33.20260330.LU1.BIV.D_JA.1;21,15;3324,645;0,041;2723,564;299;46",
            ]
        ),
    )
    return root


def test_measured_traits_parse_decimal_timestamp_and_sample_metadata(tmp_path: Path) -> None:
    root = _minimal_data_root(tmp_path)

    traits = load_measured_traits(root)

    assert traits.loc[0, "height"] == pytest.approx(21.15)
    assert traits.loc[0, "area_3d"] == pytest.approx(3324.645)
    assert traits.loc[0, "leaf_area_index"] == pytest.approx(0.041)
    assert traits.loc[0, "proj_area"] == pytest.approx(2723.564)
    assert traits.loc[0, "ScanTreatmentId"] == 299
    assert traits.loc[0, "Position"] == "LU1"
    assert traits.loc[0, "Genotype"] == "BIV"
    assert traits.loc[0, "Treatment"] == "D_JA"
    assert traits.loc[0, "Replicate"] == 1
    assert not bool(traits.loc[0, "IsEmptyPot"])
    assert pd.api.types.is_datetime64_any_dtype(traits["timestamp"])
    assert traits.loc[0, "timestamp_text"] == "20260413T115530"


def test_parse_sample_metadata_handles_empty_pots() -> None:
    metadata = parse_sample_metadata("NPEC33.20260330.LU20.empty.empty.16")

    assert metadata == {
        "Position": "LU20",
        "Genotype": "empty",
        "Treatment": "empty",
        "Replicate": 16,
    }


def test_histogram_splits_edges_from_measurements(tmp_path: Path) -> None:
    root = _minimal_data_root(tmp_path)
    _write(
        root / "PlantEye" / "derived" / "46_greenness.csv",
        "\n".join(
            [
                "timestamp;sample;bin_0;bin_1;bin_2",
                "20260413T115530;edges;-1,0;0,0;1,0",
                "20260413T115530;NPEC33.20260330.LU1.BIV.D_JA.1;0,0;3,0;5,0",
            ]
        ),
    )

    histogram = load_histogram("greenness", root)

    assert histogram.edges.tolist() == [-1.0, 0.0, 1.0]
    assert len(histogram.data) == 1
    assert histogram.data.loc[0, "sample"] == "NPEC33.20260330.LU1.BIV.D_JA.1"
    assert histogram.data.loc[0, "bin_2"] == pytest.approx(5.0)
    assert histogram.data.loc[0, "Genotype"] == "BIV"


@pytest.fixture(scope="module")
def real_data_root() -> Path:
    import os

    value = os.environ.get("M5_DATA_ROOT")
    if not value:
        pytest.skip("Set M5_DATA_ROOT to run integration checks against the real M5 data export.")
    root = Path(value)
    if not root.exists():
        pytest.skip(f"M5_DATA_ROOT does not exist: {root}")
    return root


def test_real_planteye_derived_counts(real_data_root: Path) -> None:
    traits = load_measured_traits(real_data_root)

    assert len(traits) == 11424
    assert traits["sample"].nunique() == 576
    assert traits["Genotype"].notna().all()
    assert traits["Treatment"].notna().all()

    for index in HISTOGRAM_INDICES:
        histogram = load_histogram(index, real_data_root)
        assert len(histogram.raw) == 11425
        assert len(histogram.data) == 11424
        assert len(histogram.edges) == 257
