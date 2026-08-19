# Course Code Snippets

This file is the searchable entry point for the MicroStation C# course examples used by this skill.

The original source bundle contains a mechanically extracted code collection of about 400 KB from the tutorial series `MicroStation二次开发基础教学（一）` through `MicroStation二次开发基础教学（九）`. The repository keeps the high-value, verified patterns organized by topic in the focused reference files below so coding agents do not need to load the entire raw extraction for every task.

## Reference Map

| Topic | Reference | Typical APIs / patterns |
| --- | --- | --- |
| Addin framework | [`addin-framework.md`](addin-framework.md) | `Addin`, `Run`, `Commands.xml`, `CommandTable.xml`, `MS_DGNAPPS`, `.csproj`, debugging |
| Elements and models | [`elements-model-selection.md`](elements-model-selection.md) | `DgnModel`, `DgnFile`, `Element`, `LineElement`, `ShapeElement`, `ArcElement`, transforms |
| Selection / scan / fence | [`elements-model-selection.md`](elements-model-selection.md) | `ElementAgenda`, `SelectionSetManager`, `ScanCriteria`, `FenceManager` |
| Interactive tools | [`interactive-tools.md`](interactive-tools.md) | `DgnElementSetTool`, dynamics, locate, drag select, reset, restart, modify |
| EC / ItemType | [`ec-itemtype.md`](ec-itemtype.md) | `DgnECManager`, `IDgnECInstance`, `ItemTypeLibrary`, `CustomItemHost` |
| WinForms | [`winforms-ui.md`](winforms-ui.md) | `Adapter`, three-file form structure, DPI scaling, Microsoft YaHei, preview controls |
| WPF | [`wpf-ui.md`](wpf-ui.md) | XAML, ViewModel, `WPFInteropHelper`, `DgnElementSetTool` integration |

## Tutorial Coverage

The extracted course material is organized around the following source chapters and example groups.

### MicroStation二次开发基础教学（一）

- Addin project setup and entry points.
- MicroStation assembly references.
- Command tables and key-ins.
- Addin loading and Visual Studio debugging.

### MicroStation二次开发基础教学（二）

- Active DGN file/model access.
- Unit conversion and model information.
- Basic DGN element creation.
- Geometry primitives and element properties.
- Element transforms, copies, replacements, and deletion.

### MicroStation二次开发基础教学（三）

- Line, line string, arc, shape, complex and cell elements.
- Text and dimension-related examples.
- Symbology and level operations.
- Geometry and transform operations.

### MicroStation二次开发基础教学（四）

- Model and file operations.
- Element queries.
- Selection sets and agendas.
- Scan criteria and element filtering.
- Fence creation, clipping, copying, and stretching.

### MicroStation二次开发基础教学（五）

- Interactive tool framework.
- `DgnTool`, `DgnPrimitiveTool`, and `DgnElementSetTool`.
- Data/reset button handling.
- Dynamics and temporary redraw.
- Locate, modify, drag-selection, and restart patterns.

### MicroStation二次开发基础教学（六）

- EC concepts and ECSchema workflows.
- EC classes, properties, and instances.
- Importing schemas and attaching EC data to DGN elements.

### MicroStation二次开发基础教学（七）

- ItemType libraries and ItemTypes.
- Adding/removing custom properties.
- Attaching, reading, modifying, and deleting ItemType data.
- Engineering-property workflows on DGN elements.

### MicroStation二次开发基础教学（八）

- WinForms controls and events.
- MicroStation WinForms Adapter integration.
- DGN preview controls.
- Visual parameter input and model creation.
- EC property editing UI.

Important override for this skill: raw course designer examples may use `AutoScaleMode.Font`; generated or modified MicroStation WinForms code must instead use `AutoScaleMode.Dpi`, the standard `.cs` / `.Designer.cs` / `.resx` split, and Microsoft YaHei as defined in [`winforms-ui.md`](winforms-ui.md).

### MicroStation二次开发基础教学（九）

- Larger integrated examples combining UI, MicroStation commands, element operations, engineering data, and interactive tools.

## Search Guidance for Coding Agents

Before inventing a MicroStation API or implementation pattern:

1. Identify the task category.
2. Read the focused reference file listed above.
3. Reuse the verified API names and lifecycle patterns in that reference.
4. Check the target project's actual Bentley references and MicroStation version.
5. Prefer an existing working project pattern over a generic example when they differ.
6. Run the bundled validation scripts after edits.

Useful search terms across the reference set include:

```text
Addin
CommandTable.xml
Session.Instance.GetActiveDgnModel
Session.Instance.GetActiveDgnFile
DgnModel
DgnFile
LineElement
LineStringElement
ArcElement
ShapeElement
ComplexStringElement
CellHeaderElement
DimensionElement
DTransform3d
TransformInfo
ElementCopyContext
ReplaceInModel
DeleteFromModel
ElementAgenda
SelectionSetManager
ScanCriteria
FenceManager
DgnElementSetTool
BeginDynamics
OnDynamicFrame
OnDataButton
OnResetButton
OnRestartTool
DgnECManager
IDgnECInstance
ItemTypeLibrary
CustomItemHost
Bentley.MstnPlatformNET.WinForms
WPFInteropHelper
AutoScaleMode.Dpi
Microsoft YaHei
```

## Raw Extraction

The complete mechanically extracted course-code source remains part of the original skill source package used to build this repository. This repository entry is intentionally curated because loading a single several-hundred-kilobyte Markdown file is inefficient for coding agents; the topic references preserve the patterns that the skill actively routes to.
