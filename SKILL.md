---
name: microstation-addin
description: Build, modify, debug, and review MicroStation CONNECT C# Addin projects. Use when Codex works on MicroStation secondary development, Bentley.MstnPlatformNET Addin entry points, Commands.xml key-ins, .NET Framework 4.6.2 projects, MicroStation DLL references through $(MS) relative HintPath, DGN element creation or transformation, selection sets, scan criteria, fences, DgnElementSetTool interactive tools, EC/ItemType engineering properties, WinForms Addin UIs, WPF Addin windows attached through WPFInteropHelper, auto-loading through MS_DGNAPPS, or Visual Studio debugging for MicroStation.
---

# MicroStation Addin

## Core Rules

Use the local course references first. Do not invent MicroStation API names when an example exists in `references/course-code-snippets.md`.

Target the tutorial baseline unless the user's repo proves otherwise:

- MicroStation CONNECT Edition U16-era C# Addin.
- `.NET Framework 4.6.2`.
- Visual Studio opened as administrator when debugging or writing to `Mdlapps`.
- Addin DLL output under `C:\Program Files\Bentley\MicroStation CONNECT Edition\MicroStation\Mdlapps` unless the project defines a different MicroStation path.
- Reference MicroStation/Bentley DLLs through `$(MS)` plus relative `HintPath`; do not hard-code absolute DLL paths in `<Reference>`.
- Treat DLL references as a strict whitelist from `references/addin-framework.md`; never invent DLL names from namespaces, classes, examples, or error messages.
- Command XML embedded as `CommandTable.xml`.
- Load manually with `mdl load <assembly-name>` or auto-load with `MS_DGNAPPS`.

For WinForms in a MicroStation Addin, enforce both requirements:

- Use the standard three-file WinForms structure for every form/user control: `Name.cs`, `Name.Designer.cs`, and `Name.resx`.
- Keep layout/control creation in `Name.Designer.cs`; keep constructors, events, commands, and business logic in `Name.cs`; keep resources in `Name.resx`.
- Set every form/user-control designer to `AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi`.
- Set UI fonts to Microsoft YaHei: `new System.Drawing.Font("Microsoft YaHei", ...)`.

For WPF in a MicroStation Addin, keep layout in `.xaml`, logic in `.xaml.cs`, bind state through a ViewModel, vertically center content for all basic controls, and attach/detach the window with `Bentley.MstnPlatformNET.WPF.WPFInteropHelper` when the existing project supports it.

Before finalizing WinForms work, run `scripts/check_winforms_rules.py <project-or-solution-dir>` and fix any reported file.

Before finalizing WPF work, run `scripts/check_wpf_rules.py <project-or-solution-dir>` and fix any reported file.

Before finalizing `.csproj` reference work, run `scripts/check_microstation_references.py <project-or-solution-dir> --profile baseline`; use `--profile ec` when EC/ItemType APIs are used and `--profile all` for full course-template coverage.

## Reference Routing

Read only the relevant reference file(s):

- `references/addin-framework.md`: Addin skeleton, `Commands.xml`, `.csproj`, manual load, auto-load, and Visual Studio debugging.
- `references/elements-model-selection.md`: element creation, units, transforms, copy/delete, model/file operations, selection sets, scan criteria, and fences.
- `references/interactive-tools.md`: `DgnElementSetTool` patterns for dynamic drawing, element modification, drag select, and active fences.
- `references/ec-itemtype.md`: EC schema/instance flow and ItemType create/read/update/delete/attach examples.
- `references/winforms-ui.md`: WinForms patterns, MicroStation adapter/preview notes, and mandatory DPI/Microsoft YaHei UI rules.
- `references/wpf-ui.md`: WPF window patterns based on `PlaceSupportWindow` and `PlaceCustomSupportTool`: XAML layout, ViewModel binding, `WPFInteropHelper`, singleton window lifecycle, and DgnElementSetTool integration.
- `references/course-code-snippets.md`: mechanically extracted original code blocks from the course Markdown. Search this file for exact examples before writing large code.

## Workflow

1. Inspect the existing project before editing:
   - `.csproj` target framework, references, output path, embedded resources.
   - Addin entry class and constructor signature.
   - `Commands.xml` key-in/function mappings.
   - Existing namespaces and helper classes.
2. Choose the closest course snippet:
   - Search `course-code-snippets.md` by API or task name, e.g. `LineElement`, `DTransform3d`, `SelectionSetManager`, `ScanCriteria`, `FenceManager`, `DgnElementSetTool`, `ItemTypeLibrary`, `DgnECManager`, `AutoScaleMode`.
3. Adapt conservatively:
   - Keep `Session.Instance.GetActiveDgnModel()`, `GetActiveDgnFile()`, and `GetActiveDgnModelRef()` patterns consistent with the snippet.
   - Use `AddToModel()` for new elements, `ReplaceInModel(original)` for modified elements, and `DeleteFromModel()` for deletion.
   - Wrap `ElementCopyContext` in `using`.
   - Check for `null` when reading elements, ItemTypes, EC instances, and file/model objects.
4. Validate:
   - For C# compile work, build the solution/project if MicroStation SDK references resolve locally.
   - For project references, run `scripts/check_microstation_references.py`.
   - For WinForms, run `scripts/check_winforms_rules.py`.
   - For WPF, run `scripts/check_wpf_rules.py`.
   - For command changes, verify `Commands.xml` is embedded with logical name `CommandTable.xml`.

## Minimal Addin Pattern

Use this only when the repo does not already have an entry class. The tutorial states the required Addin entry conditions: derive from `Bentley.MstnPlatformNET.Addin`, provide the single `IntPtr` MDL descriptor constructor, and override `Run()`.

```csharp
using System;
using System.Windows.Forms;
using Bentley.MstnPlatformNET;

namespace MyMicroStationAddin
{
    public sealed class MyAddin : Addin
    {
        private static MyAddin s_instance;

        public static MyAddin Instance => s_instance;

        public MyAddin(IntPtr mdlDesc) : base(mdlDesc)
        {
            s_instance = this;
        }

        protected override int Run(string[] commandLine)
        {
            return 0;
        }

        public static void HelloWorld(string unparsed)
        {
            MessageBox.Show("Hello World!");
        }
    }
}
```

Command handlers used from `Commands.xml` should be `public static void MethodName(string unparsed)` unless the existing project uses a different verified pattern.
