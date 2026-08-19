#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check MicroStation Addin WinForms structure, DPI, and font rules."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".vs",
    "bin",
    "obj",
    "packages",
    "node_modules",
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def iter_cs_files(root: Path):
    for path in root.rglob("*.cs"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def is_candidate(path: Path, text: str) -> bool:
    if path.name.endswith(".Designer.cs"):
        markers = (
            "AutoScaleMode",
            "System.Windows.Forms",
            "this.Controls.Add",
            "InitializeComponent",
        )
        return any(marker in text for marker in markers)

    inheritance_patterns = (
        r":\s*(?:System\.Windows\.Forms\.)?Form\b",
        r":\s*(?:System\.Windows\.Forms\.)?UserControl\b",
        r":\s*(?:System\.Windows\.Forms\.)?ContainerControl\b",
        r":\s*Adapter\b",
    )
    if any(re.search(pattern, text) for pattern in inheritance_patterns):
        return True

    return "Bentley.MstnPlatformNET.WinForms" in text and "InitializeComponent" in text


def split_paths(path: Path) -> tuple[Path, Path, Path]:
    if path.name.endswith(".Designer.cs"):
        base = path.name[: -len(".Designer.cs")]
    else:
        base = path.stem
    return (
        path.with_name(base + ".cs"),
        path.with_name(base + ".Designer.cs"),
        path.with_name(base + ".resx"),
    )


def companion_files(path: Path) -> list[Path]:
    main_cs, designer_cs, _ = split_paths(path)
    files = []
    for file_path in (main_cs, designer_cs):
        if file_path.exists():
            files.append(file_path)
    return files


def combined_text(path: Path) -> str:
    parts = []
    for file_path in companion_files(path):
        try:
            parts.append(read_text(file_path))
        except OSError:
            pass
    return "\n".join(parts)


def layout_markers_in_main(text: str) -> list[str]:
    markers: list[tuple[str, str]] = [
        (r"\bvoid\s+InitializeComponent\s*\(", "InitializeComponent belongs in .Designer.cs"),
        (r"\bControls\.Add\s*\(", "Controls.Add belongs in .Designer.cs"),
        (r"\.Location\s*=\s*new\s+System\.Drawing\.Point", "control Location belongs in .Designer.cs"),
        (r"\.Size\s*=\s*new\s+System\.Drawing\.Size", "control Size belongs in .Designer.cs"),
        (r"\.AutoScaleMode\s*=", "AutoScaleMode belongs in .Designer.cs"),
        (r"\.AutoScaleDimensions\s*=", "AutoScaleDimensions belongs in .Designer.cs"),
        (r"\.ClientSize\s*=", "ClientSize belongs in .Designer.cs"),
        (r"\.Anchor\s*=", "Anchor belongs in .Designer.cs"),
        (r"\.Dock\s*=", "Dock belongs in .Designer.cs"),
        (r"\.TabIndex\s*=", "TabIndex belongs in .Designer.cs"),
        (r"\.SuspendLayout\s*\(", "layout calls belong in .Designer.cs"),
        (r"\.ResumeLayout\s*\(", "layout calls belong in .Designer.cs"),
        (
            r"new\s+(?:System\.Windows\.Forms\.)?(?:Button|Label|TextBox|ComboBox|ListBox|TreeView|Panel|ProgressBar|RadioButton|CheckBox|DataGridView|GroupBox|TabControl|TabPage)\b",
            "control creation belongs in .Designer.cs",
        ),
    ]
    found = []
    for pattern, message in markers:
        if re.search(pattern, text):
            found.append(message)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check WinForms three-file structure, AutoScaleMode.Dpi, and Microsoft YaHei rules."
    )
    parser.add_argument("path", nargs="?", default=".", help="Project or solution directory")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    violations: list[tuple[Path, str]] = []
    seen: set[Path] = set()

    for path in iter_cs_files(root):
        text = read_text(path)
        if not is_candidate(path, text):
            continue

        main_cs, designer_cs, resx = split_paths(path)
        key = main_cs
        if key in seen:
            continue
        seen.add(key)

        merged = combined_text(path)
        display_path = path.relative_to(root)
        base_name = main_cs.name

        if not main_cs.exists():
            violations.append((display_path, f"missing WinForms code-behind file: {base_name}"))

        if not designer_cs.exists():
            violations.append((display_path, f"missing WinForms designer file: {designer_cs.name}"))

        if not resx.exists():
            violations.append((display_path, f"missing WinForms resource file: {resx.name}"))

        if "AutoScaleMode.Dpi" not in merged:
            violations.append((display_path, "missing AutoScaleMode.Dpi"))

        if "Microsoft YaHei" not in merged and "微软雅黑" not in merged:
            violations.append((display_path, "missing Microsoft YaHei/微软雅黑 font"))

        if "AutoScaleMode.Font" in merged:
            violations.append((display_path, "contains forbidden AutoScaleMode.Font"))

        if main_cs.exists():
            main_text = read_text(main_cs)
            for message in layout_markers_in_main(main_text):
                violations.append((main_cs.relative_to(root), message))

    if violations:
        print("WinForms rule violations:")
        for path, message in violations:
            print(f"- {path}: {message}")
        return 1

    print("WinForms DPI/font rules passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
