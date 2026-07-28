from __future__ import annotations

import hashlib
import os
import platform
import sys
from pathlib import Path


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(base_dir: Path):
    if not base_dir.exists():
        return []
    return sorted(path for path in base_dir.rglob("*") if path.is_file())


def write_run_trace(complete_path_dir: str) -> None:
    base_dir = Path(complete_path_dir).resolve()
    outp_dir = base_dir / "OUTP"
    outp_dir.mkdir(parents=True, exist_ok=True)
    trace_path = outp_dir / "AquaCrop_debug_trace.txt"

    lines = [
        f"platform={platform.platform()}",
        f"python={sys.version}",
        f"executable={sys.executable}",
        f"cwd={Path.cwd()}",
        f"complete_path_dir={base_dir}",
        "",
    ]

    for folder_name in ("LIST", "DATA", "OBS", "PARAM", "SIMUL"):
        folder = base_dir / folder_name
        lines.append(f"[{folder_name}]")
        if not folder.exists():
            lines.append("missing")
            lines.append("")
            continue

        for file_path in _iter_files(folder):
            rel_path = file_path.relative_to(base_dir)
            lines.append(
                f"{rel_path}|size={file_path.stat().st_size}|sha256={_file_hash(file_path)}"
            )
        lines.append("")

    trace_path.write_text("\n".join(lines), encoding="utf-8")


def append_file_preview(
    complete_path_dir: str,
    label: str,
    file_path: str | Path,
    max_lines: int = 12,
) -> None:
    base_dir = Path(complete_path_dir).resolve()
    outp_dir = base_dir / "OUTP"
    outp_dir.mkdir(parents=True, exist_ok=True)
    trace_path = outp_dir / "AquaCrop_debug_trace.txt"
    target_path = Path(file_path).resolve()

    lines = [
        "",
        f"[PREVIEW:{label}]",
        f"path={target_path}",
    ]

    if not target_path.exists():
        lines.append("missing")
        trace_path.write_text(
            trace_path.read_text(encoding="utf-8") + "\n".join(lines) + "\n",
            encoding="utf-8",
        )
        return

    try:
        lines.append(f"size={target_path.stat().st_size}")
        with target_path.open("r", encoding="utf-8", errors="replace") as handle:
            for idx, line in enumerate(handle, start=1):
                if idx > max_lines:
                    lines.append("...")
                    break
                lines.append(f"{idx:03d}: {line.rstrip()}")
    except OSError as exc:
        lines.append(f"error={exc}")

    existing = ""
    if trace_path.exists():
        existing = trace_path.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    trace_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")
