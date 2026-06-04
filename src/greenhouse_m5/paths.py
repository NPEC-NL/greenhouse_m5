"""Data path configuration.

Edit ``DATA_ROOT`` if your M5 data folder is in a different location.
All loader functions also accept ``data_root=...`` to override this path.
"""

from __future__ import annotations

from pathlib import Path


DATA_ROOT = Path(r"D:\Maarten\M5\Data")


def resolve_data_root(data_root: str | Path | None = None, *, require_exists: bool = True) -> Path:
    """Return the configured M5 data root."""

    root = Path(data_root).expanduser() if data_root is not None else DATA_ROOT
    root = root.resolve()
    if require_exists and not root.exists():
        raise FileNotFoundError(f"M5 data root does not exist: {root}. Edit DATA_ROOT in paths.py.")
    return root
