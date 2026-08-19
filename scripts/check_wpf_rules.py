#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check MicroStation Addin WPF file structure and code-behind rules."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


EXCLUDED_DIRS = {".git", ".vs", "bin", "obj", "packages", "node_modules"}

CONTENT_CENTER_CONTROLS = {
    "Button",
    "ToggleButton",
    "RepeatButton",
    "CheckBox",
    "RadioButton",
    "TextBox",
    "PasswordBox",
    "ComboBox",
    "ComboBoxItem",
    "Label",
    "ListBoxItem",
    "TabItem",
}

TEXT_CENTER_CONTROLS = {
    "TextBlock",
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def iter_files(root: Path, pattern: str):
    for path in root.rglob(pattern):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def attr_by_local(elem: ET.Element, name: str) -> str:
    for attr_name, value in elem.attrib.items():
        if local_name(attr_name) == name:
            return value.strip()
    return ""


def text_of(elem: ET.Element | None) -> str:
    return "" if elem is None or elem.text is None else elem.text.strip()


def first_child(elem: ET.Element, name: str) -> ET.Element | None:
    for child in elem:
        if local_name(child.tag) == name:
            return child
    return None


def is_wpf_ui_xaml(text: str) -> bool:
    return bool(re.search(r"<\s*(Window|UserControl|Page)\b", text))


def get_x_class(text: str) -> str:
    match = re.search(r"\bx:Class\s*=\s*\"([^\"]+)\"", text)
    return match.group(1) if match else ""


def is_center(value: str) -> bool:
    return value.strip().lower() == "center"


def normalize_target_type(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    match = re.search(r"\{x:Type\s+([^}]+)\}", value)
    if match:
        value = match.group(1)
    return value.rsplit(":", 1)[-1].strip()


def static_resource_key(value: str) -> str:
    match = re.search(r"\{(?:StaticResource|DynamicResource)\s+([^}]+)\}", value.strip())
    return match.group(1).strip() if match else ""


def element_label(elem: ET.Element) -> str:
    tag = local_name(elem.tag)
    name = attr_by_local(elem, "Name")
    if name:
        return f"{tag} '{name}'"
    content = attr_by_local(elem, "Content") or attr_by_local(elem, "Text")
    if content and len(content) <= 30:
        return f"{tag} '{content}'"
    return tag


def collect_centering_styles(xaml_root: ET.Element):
    implicit_content: set[str] = set()
    implicit_text: set[str] = set()
    keyed_content: set[str] = set()
    keyed_text: set[str] = set()

    for elem in xaml_root.iter():
        if local_name(elem.tag) != "Style":
            continue

        target_type = normalize_target_type(attr_by_local(elem, "TargetType"))
        style_key = attr_by_local(elem, "Key")
        has_content_center = False
        has_text_center = False

        for child in elem.iter():
            if local_name(child.tag) != "Setter":
                continue
            prop = attr_by_local(child, "Property")
            value = attr_by_local(child, "Value")
            if prop.endswith("VerticalContentAlignment") and is_center(value):
                has_content_center = True
            if prop.endswith("VerticalAlignment") and is_center(value):
                has_text_center = True

        if style_key:
            if has_content_center:
                keyed_content.add(style_key)
            if has_text_center:
                keyed_text.add(style_key)
        else:
            if target_type and has_content_center:
                implicit_content.add(target_type)
            if target_type and has_text_center:
                implicit_text.add(target_type)

    return implicit_content, implicit_text, keyed_content, keyed_text


def has_content_centering(elem: ET.Element, styles) -> bool:
    if is_center(attr_by_local(elem, "VerticalContentAlignment")):
        return True

    implicit_content, _, keyed_content, _ = styles
    tag = local_name(elem.tag)
    if tag in implicit_content or "Control" in implicit_content or "ContentControl" in implicit_content:
        return True

    style_key = static_resource_key(attr_by_local(elem, "Style"))
    return bool(style_key and style_key in keyed_content)


def has_text_centering(elem: ET.Element, styles) -> bool:
    if is_center(attr_by_local(elem, "VerticalAlignment")):
        return True

    _, implicit_text, _, keyed_text = styles
    tag = local_name(elem.tag)
    if tag in implicit_text or "FrameworkElement" in implicit_text:
        return True

    style_key = static_resource_key(attr_by_local(elem, "Style"))
    return bool(style_key and style_key in keyed_text)


def check_basic_control_centering(xaml_root: ET.Element) -> list[str]:
    violations: list[str] = []
    styles = collect_centering_styles(xaml_root)

    for elem in xaml_root.iter():
        tag = local_name(elem.tag)
        if "." in tag or tag in {"Style", "Setter"}:
            continue

        if tag in CONTENT_CENTER_CONTROLS and not has_content_centering(elem, styles):
            violations.append(f"{element_label(elem)} should set VerticalContentAlignment=\"Center\" or be covered by a Center style")

        if tag in TEXT_CENTER_CONTROLS and not has_text_centering(elem, styles):
            violations.append(f"{element_label(elem)} should set VerticalAlignment=\"Center\" or be covered by a Center style")

    return violations


def codebehind_layout_markers(text: str) -> list[str]:
    markers: list[tuple[str, str]] = [
        (
            r"new\s+(?:System\.Windows\.Controls\.)?(?:Button|Label|TextBox|ComboBox|ListBox|TreeView|Grid|StackPanel|DockPanel|Border|Image|GridSplitter|ToolBar|GroupBox|CheckBox|RadioButton|WindowsFormsHost)\b",
            "WPF control creation belongs in .xaml",
        ),
        (r"\.(?:Children|Items)\.Add\s*\(\s*new\s+(?:System\.Windows\.Controls\.)", "WPF visual tree construction belongs in .xaml"),
        (r"\bGrid\.Set(?:Row|Column)\s*\(", "Grid row/column placement belongs in .xaml"),
        (r"\.Margin\s*=\s*new\s+Thickness", "layout Margin belongs in .xaml"),
        (r"\.Width\s*=", "layout Width belongs in .xaml"),
        (r"\.Height\s*=", "layout Height belongs in .xaml"),
        (r"\.HorizontalAlignment\s*=", "layout alignment belongs in .xaml"),
        (r"\.VerticalAlignment\s*=", "layout alignment belongs in .xaml"),
    ]

    found = []
    for pattern, message in markers:
        if re.search(pattern, text):
            found.append(message)
    return found


def parse_project(path: Path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None


def collect_project_data(projects: list[Path], root: Path):
    page_items: set[str] = set()
    page_generators: dict[str, str] = {}
    compile_dependents: dict[str, str] = {}
    references: set[str] = set()

    for project in projects:
        project_root = parse_project(project)
        if project_root is None:
            continue
        base = project.parent
        for elem in project_root.iter():
            name = local_name(elem.tag)
            include = elem.attrib.get("Include", "")
            if name == "Reference" and include:
                references.add(include.split(",", 1)[0])
            elif name == "Page" and include:
                normalized = str((base / include).resolve()).lower()
                page_items.add(normalized)
                page_generators[normalized] = text_of(first_child(elem, "Generator"))
            elif name == "Compile" and include.lower().endswith(".xaml.cs"):
                normalized = str((base / include).resolve()).lower()
                compile_dependents[normalized] = text_of(first_child(elem, "DependentUpon"))

    return page_items, page_generators, compile_dependents, references


def main() -> int:
    parser = argparse.ArgumentParser(description="Check WPF XAML/code-behind rules.")
    parser.add_argument("path", nargs="?", default=".", help="Project or solution directory")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    xaml_files = [path for path in iter_files(root, "*.xaml") if is_wpf_ui_xaml(read_text(path))]
    if not xaml_files:
        print("No WPF UI XAML files found.")
        return 0

    projects = list(iter_files(root, "*.csproj"))
    page_items, page_generators, compile_dependents, references = collect_project_data(projects, root)

    violations: list[tuple[Path, str]] = []
    needs_windows_forms_host = False

    for xaml in xaml_files:
        xaml_text = read_text(xaml)
        codebehind = xaml.with_suffix(xaml.suffix + ".cs")
        display = xaml.relative_to(root)
        x_class = get_x_class(xaml_text)

        try:
            xaml_root = ET.fromstring(xaml_text)
        except ET.ParseError as exc:
            violations.append((display, f"invalid XAML XML: {exc}"))
            continue

        for message in check_basic_control_centering(xaml_root):
            violations.append((display, message))

        if "WindowsFormsHost" in xaml_text:
            needs_windows_forms_host = True

        if not x_class:
            violations.append((display, "missing x:Class"))

        if not codebehind.exists():
            violations.append((display, f"missing WPF code-behind file: {codebehind.name}"))
        else:
            code_text = read_text(codebehind)
            if "InitializeComponent();" not in code_text:
                violations.append((codebehind.relative_to(root), "constructor should call InitializeComponent()"))

            if x_class:
                class_name = x_class.rsplit(".", 1)[-1]
                if not re.search(r"\bpartial\s+class\s+" + re.escape(class_name) + r"\b", code_text):
                    violations.append((codebehind.relative_to(root), f"code-behind partial class should match x:Class '{x_class}'"))

            for message in codebehind_layout_markers(code_text):
                violations.append((codebehind.relative_to(root), message))

            if "WPFInteropHelper" in code_text:
                if ".Attach(" not in code_text:
                    violations.append((codebehind.relative_to(root), "WPFInteropHelper usage should call Attach"))
                if ".Detach(" not in code_text:
                    violations.append((codebehind.relative_to(root), "WPFInteropHelper usage should call Detach on close"))
                if ".Dispose(" not in code_text:
                    violations.append((codebehind.relative_to(root), "WPFInteropHelper usage should call Dispose on close"))

        if projects:
            xaml_key = str(xaml.resolve()).lower()
            code_key = str(codebehind.resolve()).lower()
            if xaml_key not in page_items:
                violations.append((display, "old-style .csproj should include XAML as <Page>"))
            elif page_generators.get(xaml_key) != "MSBuild:Compile":
                violations.append((display, "XAML <Page> should set <Generator>MSBuild:Compile</Generator>"))

            if codebehind.exists():
                dependent = compile_dependents.get(code_key)
                if dependent != xaml.name:
                    violations.append((codebehind.relative_to(root), f"code-behind <Compile> should set <DependentUpon>{xaml.name}</DependentUpon>"))

    if projects:
        for required in ("PresentationCore", "PresentationFramework", "System.Xaml", "WindowsBase"):
            if required not in references:
                violations.append((Path("."), f"missing WPF framework reference: {required}"))

        if needs_windows_forms_host:
            for required in ("WindowsFormsIntegration", "System.Windows.Forms"):
                if required not in references:
                    violations.append((Path("."), f"WindowsFormsHost requires reference: {required}"))

    if violations:
        print("WPF rule violations:")
        for path, message in violations:
            print(f"- {path}: {message}")
        return 1

    print(f"WPF rules passed for {len(xaml_files)} XAML file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
