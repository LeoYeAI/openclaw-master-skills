#!/usr/bin/env python3
"""Inventory bounded FluidSim output and HDF5/netCDF4 metadata lazily."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

try:
    from ._common import (
        MAX_ATTRIBUTES,
        MAX_DATASETS,
        MAX_FILES,
        MAX_HDF5_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
    )
except ImportError:  # Direct script execution.
    from _common import (
        MAX_ATTRIBUTES,
        MAX_DATASETS,
        MAX_FILES,
        MAX_HDF5_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
    )


TOOL = "fluidsim-output-inventory"
HDF5_SUFFIXES = (".h5", ".hdf5", ".nc")
SAFE_SCALAR_ATTRIBUTES = {
    "Lx",
    "Ly",
    "Lz",
    "class_name",
    "fluidfft",
    "fluidsim",
    "it",
    "module_name",
    "name_run",
    "nx",
    "ny",
    "nz",
    "solver",
    "time",
    "version",
}


def _clean_name(value: str) -> str:
    cleaned = "".join(
        character if character.isprintable() else "?" for character in value
    )
    return cleaned[:300]


def _scalar(value: Any) -> Any:
    """Convert a known scalar attribute without retaining arbitrary arrays."""

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[:300]
    if isinstance(value, str):
        return value[:300]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return None


def _attributes(
    obj: Any, *, count: list[int], max_attributes: int
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for name in sorted(obj.attrs):
        count[0] += 1
        if count[0] > max_attributes:
            raise ToolError("HDF5 attribute-count limit exceeded")
        identifier = obj.attrs.get_id(name)
        entry: dict[str, Any] = {
            "dtype": str(identifier.dtype)[:100],
            "name": _clean_name(str(name)),
            "shape": list(identifier.shape),
            "value": None,
        }
        if name in SAFE_SCALAR_ATTRIBUTES and identifier.shape == ():
            entry["value"] = _scalar(obj.attrs[name])
        result.append(entry)
    return result


def _object_address(h5py: Any, obj: Any) -> int:
    try:
        return int(h5py.h5o.get_info(obj.id).addr)
    except (AttributeError, TypeError, ValueError):
        return hash(obj.id)


def inspect_hdf5_metadata(
    path: Path,
    *,
    max_datasets: int,
    max_attributes: int,
    max_depth: int,
) -> dict[str, Any]:
    """Read only object/link metadata; never index a dataset."""

    try:
        import h5py  # Lazy optional dependency.
    except ImportError as exc:
        raise ToolError(
            "HDF5 inspection requires optional h5py; install the pinned FluidSim environment"
        ) from exc

    datasets: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    links = {"external_not_followed": 0, "soft_not_followed": 0}
    attribute_count = [0]
    try:
        with h5py.File(path, "r") as handle:
            stack: list[tuple[Any, str, int]] = [(handle, "/", 0)]
            seen_groups: set[int] = set()
            while stack:
                group, group_path, depth = stack.pop()
                address = _object_address(h5py, group)
                if address in seen_groups:
                    continue
                seen_groups.add(address)
                groups.append(
                    {
                        "attributes": _attributes(
                            group,
                            count=attribute_count,
                            max_attributes=max_attributes,
                        ),
                        "path": _clean_name(group_path),
                    }
                )
                if depth >= max_depth:
                    continue
                for name in sorted(group.keys(), reverse=True):
                    link = group.get(name, getlink=True)
                    child_path = (
                        f"/{name}" if group_path == "/" else f"{group_path}/{name}"
                    )
                    if isinstance(link, h5py.ExternalLink):
                        links["external_not_followed"] += 1
                        continue
                    if isinstance(link, h5py.SoftLink):
                        links["soft_not_followed"] += 1
                        continue
                    child = group.get(name, getlink=False)
                    if isinstance(child, h5py.Dataset):
                        if len(datasets) >= max_datasets:
                            raise ToolError("HDF5 dataset-count limit exceeded")
                        datasets.append(
                            {
                                "attributes": _attributes(
                                    child,
                                    count=attribute_count,
                                    max_attributes=max_attributes,
                                ),
                                "chunks": (
                                    list(child.chunks)
                                    if child.chunks is not None
                                    else None
                                ),
                                "compression": child.compression,
                                "dtype": str(child.dtype)[:100],
                                "path": _clean_name(child_path),
                                "shape": list(child.shape),
                                "storage_bytes": int(child.id.get_storage_size()),
                            }
                        )
                    elif isinstance(child, h5py.Group):
                        stack.append((child, child_path, depth + 1))
    except OSError as exc:
        return {
            "attributes": 0,
            "datasets": [],
            "groups": [],
            "hdf5_readable": False,
            "links": links,
            "message": str(exc)[:300],
        }
    return {
        "attributes": attribute_count[0],
        "datasets": datasets,
        "groups": groups,
        "hdf5_readable": True,
        "links": links,
    }


def _kind(path: Path) -> str:
    name = path.name.casefold()
    if name.startswith("state_phys"):
        return "physical_state"
    if name.startswith(("spectra", "spect_energy", "spectra_multidim")):
        return "spectral_output"
    if name.startswith("spatial_means"):
        return "scalar_output"
    if name in {"params_simul.xml", "info_solver.xml", "stdout.txt"}:
        return "provenance_or_log"
    if name.endswith(HDF5_SUFFIXES):
        return "hdf5_or_netcdf"
    return "other"


def inventory(
    path: Path,
    *,
    root: Path,
    max_files: int,
    max_hdf5_files: int,
    max_datasets: int,
    max_attributes: int,
    max_depth: int,
) -> dict[str, Any]:
    files = iter_local_files(
        path, suffixes=None, max_files=max_files, recursive=True
    )
    entries: list[dict[str, Any]] = []
    hdf5_entries: list[dict[str, Any]] = []
    total_bytes = 0
    for file_path in files:
        size = file_path.stat().st_size
        if size > MAX_HDF5_BYTES:
            raise ToolError("a file exceeds the hard inspection-size bound")
        total_bytes += size
        kind = _kind(file_path)
        entries.append(
            {
                "kind": kind,
                "path": relative_display(file_path, root),
                "size_bytes": size,
            }
        )
        if (
            file_path.name.casefold().endswith(HDF5_SUFFIXES)
            and len(hdf5_entries) < max_hdf5_files
        ):
            hdf5_entries.append(
                {
                    "metadata": inspect_hdf5_metadata(
                        file_path,
                        max_datasets=max_datasets,
                        max_attributes=max_attributes,
                        max_depth=max_depth,
                    ),
                    "path": relative_display(file_path, root),
                    "size_bytes": size,
                }
            )
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
    return {
        "arrays_loaded": False,
        "external_links_followed": False,
        "file_count": len(entries),
        "files": entries,
        "hdf5_files_inspected": len(hdf5_entries),
        "hdf5_metadata": hdf5_entries,
        "kind_counts": dict(sorted(counts.items())),
        "network_used": False,
        "ok": True,
        "root": ".",
        "total_bytes": total_bytes,
        "tool": TOOL,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory local FluidSim output. HDF5/netCDF4 datasets are described "
            "by shape/dtype/chunks only; array values and external links are not read."
        )
    )
    parser.add_argument("--path", required=True, help="Run directory or one file.")
    parser.add_argument("--root", default=".", help="Local I/O boundary.")
    parser.add_argument("--max-files", type=int, default=256)
    parser.add_argument("--max-hdf5-files", type=int, default=32)
    parser.add_argument("--max-datasets", type=int, default=2_000)
    parser.add_argument("--max-attributes", type=int, default=5_000)
    parser.add_argument("--max-depth", type=int, default=16)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        max_files = bounded_int(
            args.max_files, name="max_files", minimum=1, maximum=MAX_FILES
        )
        max_hdf5_files = bounded_int(
            args.max_hdf5_files,
            name="max_hdf5_files",
            minimum=0,
            maximum=MAX_FILES,
        )
        max_datasets = bounded_int(
            args.max_datasets,
            name="max_datasets",
            minimum=1,
            maximum=MAX_DATASETS,
        )
        max_attributes = bounded_int(
            args.max_attributes,
            name="max_attributes",
            minimum=1,
            maximum=MAX_ATTRIBUTES,
        )
        max_depth = bounded_int(
            args.max_depth, name="max_depth", minimum=1, maximum=64
        )
        root = checked_root(args.root)
        path = checked_input(args.path, root=root, kind="any")
        report = inventory(
            path,
            root=root,
            max_files=max_files,
            max_hdf5_files=max_hdf5_files,
            max_datasets=max_datasets,
            max_attributes=max_attributes,
            max_depth=max_depth,
        )
        emit_json(report)
        return 0
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
