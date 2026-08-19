#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check MicroStation Addin .csproj Bentley DLL references."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


EXCLUDED_DIRS = {".git", ".vs", "bin", "obj", "packages", "node_modules"}

BASELINE_DLLS = {
    "ustation.dll": "$(MS)ustation.dll",
    "Bentley.DgnPlatformNET.dll": "$(MS)Bentley.DgnPlatformNET.dll",
    "Bentley.DgnDisplayNet.dll": "$(MS)Bentley.DgnDisplayNet.dll",
    "Bentley.GeometryNET.dll": "$(MS)Bentley.GeometryNET.dll",
    "Bentley.GeometryNET.Common.dll": "$(MS)Bentley.GeometryNET.Common.dll",
}

EC_DLLS = {
    "Bentley.EC.Persistence3.dll": "$(MS)Assemblies\\ECFramework\\Bentley.EC.Persistence3.dll",
    "Bentley.ECObjects.Interop3.dll": "$(MS)Assemblies\\ECFramework\\Bentley.ECObjects.Interop3.dll",
    "Bentley.ECObjects3.dll": "$(MS)Assemblies\\ECFramework\\Bentley.ECObjects3.dll",
    "Bentley.ECSystem3.dll": "$(MS)Assemblies\\ECFramework\\Bentley.ECSystem3.dll",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element | None) -> str:
    return "" if elem is None or elem.text is None else elem.text.strip()


def children(elem: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(elem) if local_name(child.tag) == name]


def first_child(elem: ET.Element, name: str) -> ET.Element | None:
    for child in elem:
        if local_name(child.tag) == name:
            return child
    return None


def normalize_path(value: str) -> str:
    return value.replace("/", "\\").strip().lower()


def is_absolute_microstation_path(value: str) -> bool:
    normalized = normalize_path(value)
    return bool(re.match(r"^[a-z]:\\", normalized)) and "microstation" in normalized


def iter_projects(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() == ".csproj":
        return [root]

    projects: list[Path] = []
    for path in root.rglob("*.csproj"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        projects.append(path)
    return sorted(projects)


def required_dlls(profile: str) -> dict[str, str]:
    if profile == "baseline":
        return dict(BASELINE_DLLS)
    if profile == "ec":
        result = dict(BASELINE_DLLS)
        result.update(EC_DLLS)
        return result
    if profile == "all":
        result = dict(BASELINE_DLLS)
        result.update(EC_DLLS)
        return result
    raise ValueError(f"Unknown profile: {profile}")


def is_bentley_reference(reference: ET.Element, hint_path: str) -> bool:
    include = reference.attrib.get("Include", "")
    return (
        include == "ustation"
        or include.startswith("Bentley.")
        or "bentley." in normalize_path(hint_path)
        or normalize_path(hint_path).endswith("\\ustation.dll")
    )


def dll_name_from_reference(reference: ET.Element, hint_path: str) -> str:
    if hint_path:
        value = hint_path.replace("/", "\\").strip()
        candidate = value.split("\\")[-1]
        if candidate.lower().startswith("$(ms)"):
            candidate = candidate[len("$(MS)") :]
        if candidate.lower().endswith(".dll"):
            return candidate

    include = reference.attrib.get("Include", "").split(",", 1)[0].strip()
    if include == "ustation":
        return "ustation.dll"
    if include.startswith("Bentley."):
        return include if include.lower().endswith(".dll") else include + ".dll"
    return ""


def check_project(path: Path, profile: str) -> list[str]:
    violations: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"invalid XML: {exc}"]

    ms_values = []
    reference_paths = []
    references = []

    for elem in root.iter():
        name = local_name(elem.tag)
        if name == "MS":
            ms_values.append(text_of(elem))
        elif name == "ReferencePath":
            reference_paths.append(text_of(elem))
        elif name == "Reference":
            hint = text_of(first_child(elem, "HintPath"))
            private = text_of(first_child(elem, "Private"))
            references.append((elem, hint, private))

    if not ms_values:
        violations.append("missing <MS Condition=\"'$(MS)' == ''\">...MicroStation\\</MS> fallback property")
    elif not any(value.endswith("\\") for value in ms_values if value):
        violations.append("<MS> value should keep a trailing backslash")

    if not any("$(MS)" in value for value in reference_paths):
        violations.append("ReferencePath should include $(MS)")

    needs_ec = profile in {"ec", "all"}
    if needs_ec and not any("$(MS)Assemblies\\ECFramework\\" in value.replace("/", "\\") for value in reference_paths):
        violations.append("ReferencePath should include $(MS)Assemblies\\ECFramework\\ for EC/ItemType projects")

    hints = [hint for _, hint, _ in references if hint]
    for hint in hints:
        if is_absolute_microstation_path(hint):
            violations.append(f"absolute MicroStation HintPath is not allowed: {hint}")

    required = required_dlls(profile)
    required_names = {name.lower() for name in required}
    normalized_hints = {normalize_path(hint): hint for hint in hints}
    for dll_name, expected in required.items():
        expected_norm = normalize_path(expected)
        found = expected_norm in normalized_hints
        if not found:
            violations.append(f"missing required HintPath for {dll_name}: {expected}")

    for reference, hint, private in references:
        if not is_bentley_reference(reference, hint):
            continue
        dll_name = dll_name_from_reference(reference, hint)
        if not hint:
            violations.append(f"Bentley reference must include a $(MS) HintPath: {reference.attrib.get('Include', '')}")
        if hint and "$(MS)" not in hint:
            violations.append(f"Bentley reference must use $(MS) HintPath: {reference.attrib.get('Include', '')}")
        if private.lower() != "false":
            violations.append(f"Bentley reference should set <Private>False</Private>: {reference.attrib.get('Include', '')}")
        if dll_name and dll_name.lower() not in required_names:
            violations.append(f"Bentley reference is outside the strict DLL whitelist: {dll_name}")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Check MicroStation .csproj DLL references.")
    parser.add_argument("path", nargs="?", default=".", help="Project file or directory")
    parser.add_argument(
        "--profile",
        choices=("baseline", "ec", "all"),
        default="baseline",
        help="baseline requires Addin/element DLLs; ec/all also require ECFramework DLLs",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    projects = iter_projects(root)
    if not projects:
        print(f"No .csproj files found under: {root}", file=sys.stderr)
        return 2

    all_violations: list[tuple[Path, str]] = []
    for project in projects:
        for violation in check_project(project, args.profile):
            all_violations.append((project, violation))

    if all_violations:
        print("MicroStation reference violations:")
        for project, violation in all_violations:
            print(f"- {project}: {violation}")
        return 1

    print(f"MicroStation reference rules passed for {len(projects)} project(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
