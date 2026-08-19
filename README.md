# MicroStation Addin Skill

[English](#english) | [中文](#中文)

---

## English

### Overview

`microstation-addin` is a reusable AI coding skill for **MicroStation CONNECT Edition C# Addin development**. It provides practical guidance, reference material, and validation scripts for building, reviewing, debugging, and maintaining MicroStation extensions based on the Bentley .NET APIs.

The skill focuses on real Addin engineering rather than generic C# examples. It covers Addin structure, DGN model and element operations, selection, interactive tools, EC/ItemType data, WinForms/WPF integration, API-reference checks, and common compatibility constraints.

### Scope

The skill is intended for tasks such as:

- Creating or restructuring a MicroStation C# Addin project.
- Implementing commands and command registration.
- Working with `DgnFile`, `DgnModel`, `Element`, `ElementAgenda`, and selection sets.
- Creating, modifying, replacing, and deleting DGN elements.
- Building interactive placement, locate, modify, and primitive tools.
- Handling mouse input, reset, dynamics, snapping, and tool lifecycle.
- Reading and writing EC properties and ItemType data.
- Building WinForms or WPF user interfaces hosted by MicroStation.
- Reviewing MicroStation API usage for namespace/reference mistakes.
- Checking UI code against known MicroStation integration rules.
- Debugging common Addin loading, API-version, and UI-integration issues.

### Repository Structure

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── addin-framework.md
│   ├── course-code-snippets.md
│   ├── ec-itemtype.md
│   ├── elements-model-selection.md
│   ├── interactive-tools.md
│   ├── winforms-ui.md
│   └── wpf-ui.md
└── scripts/
    ├── check_microstation_references.py
    ├── check_winforms_rules.py
    └── check_wpf_rules.py
```

### Core Files

#### `SKILL.md`

The main skill definition. It describes when the skill should be used, the recommended workflow, MicroStation-specific development rules, validation expectations, and how the supporting references should be consulted.

#### `agents/openai.yaml`

Agent-facing metadata for discovering and invoking the skill.

#### `references/`

Focused technical references used on demand instead of loading all MicroStation knowledge into the main skill file.

| File | Purpose |
| --- | --- |
| `addin-framework.md` | Addin entry points, command framework, configuration, loading, and project organization |
| `elements-model-selection.md` | DGN models, elements, selection, agendas, element creation/modification, and model operations |
| `interactive-tools.md` | Primitive/locate/modify tool patterns, dynamics, input handling, and tool lifecycle |
| `ec-itemtype.md` | EC schema, EC instances, ItemTypes, custom properties, and related APIs |
| `winforms-ui.md` | WinForms integration patterns and MicroStation-specific constraints |
| `wpf-ui.md` | WPF integration patterns, hosting considerations, and UI rules |
| `course-code-snippets.md` | Larger collection of MicroStation C# API examples and implementation snippets |

### Validation Scripts

The repository includes lightweight static checks that can be run locally.

#### Check MicroStation references

```bash
python scripts/check_microstation_references.py <project-or-source-directory>
```

This script looks for suspicious Bentley/MicroStation references and common API usage problems.

#### Check WinForms integration rules

```bash
python scripts/check_winforms_rules.py <project-or-source-directory>
```

#### Check WPF integration rules

```bash
python scripts/check_wpf_rules.py <project-or-source-directory>
```

These scripts are intended as development aids. They do not replace compiling and testing the Addin against the actual MicroStation SDK/runtime.

### Recommended Workflow

1. Identify the MicroStation version and the target .NET runtime used by the existing Addin.
2. Inspect the existing project references before suggesting API changes.
3. Read `SKILL.md` and only the relevant reference documents for the task.
4. Prefer Bentley-supported .NET APIs already used by the project.
5. Keep UI and MicroStation-host integration separate from domain logic where practical.
6. Run the included validation scripts after code changes.
7. Build against the real Bentley assemblies used by the target MicroStation installation.
8. Validate interactive behavior inside MicroStation, especially tool lifecycle, selection, dynamics, and model edits.

### MicroStation Development Notes

MicroStation Addin development is sensitive to the exact Bentley product/version and referenced assemblies. API availability and signatures can differ between releases. Therefore:

- Do not assume that an API from a newer Bentley release exists in an older project.
- Prefer the project's existing Bentley references as the compatibility baseline.
- Avoid replacing working Bentley APIs merely because an alternative exists.
- Treat native/managed interoperability and host-window ownership carefully.
- Compile and test with the actual MicroStation environment whenever possible.

Typical Bentley namespaces encountered by this skill include, depending on the project and product version:

```csharp
Bentley.MstnPlatformNET
Bentley.DgnPlatformNET
Bentley.DgnPlatformNET.Elements
Bentley.ECObjects.Instance
Bentley.EC.Persistence
```

The exact references must be verified against the target SDK and the existing project.

### Using the Skill

Copy the `microstation-addin` skill directory into the skills location supported by your AI coding environment, or use the repository as a reference when maintaining an existing MicroStation Addin.

The main entry point is:

```text
SKILL.md
```

A coding agent should read the main skill first and load only the reference documents relevant to the current task.

### Design Principles

- **Project evidence first** — inspect the existing Addin before proposing framework changes.
- **Bentley API accuracy** — do not invent MicroStation APIs or signatures.
- **Version awareness** — preserve compatibility with the project's MicroStation generation.
- **Minimal changes** — avoid unnecessary architectural rewrites when fixing focused issues.
- **Host-aware UI** — WinForms and WPF code must account for MicroStation ownership and lifecycle.
- **Interactive correctness** — placement and locate tools must handle reset, dynamics, cleanup, and re-entry correctly.
- **Validation** — static checks are useful, but the real SDK build and MicroStation runtime remain authoritative.

### Contributing

Contributions that improve Bentley API accuracy, add version-specific notes, improve validation rules, or provide well-tested MicroStation Addin patterns are welcome.

When contributing:

1. Keep `SKILL.md` concise and workflow-oriented.
2. Put detailed technical material in `references/`.
3. Avoid undocumented or speculative APIs.
4. State version-specific assumptions when necessary.
5. Keep examples focused and compilable where possible.
6. Use clear English commit messages.

### Disclaimer

This is an independent developer resource and is not an official Bentley Systems project. Bentley, MicroStation, and related product names are trademarks of their respective owners.

---

## 中文

### 简介

`microstation-addin` 是一个面向 **MicroStation CONNECT Edition C# Addin 开发**的可复用 AI 编程 Skill，提供实际工程开发中需要的规则、参考资料和静态校验脚本，用于辅助创建、审查、调试和维护基于 Bentley .NET API 的 MicroStation 扩展程序。

该 Skill 重点解决真实 MicroStation Addin 工程问题，而不是提供通用 C# 示例。覆盖 Addin 框架、DGN 模型和元素操作、选择集、交互工具、EC/ItemType、WinForms/WPF 集成、Bentley API 引用检查以及常见兼容性问题。

### 适用范围

主要适用于以下任务：

- 创建或重构 MicroStation C# Addin 工程。
- 实现命令及命令注册。
- 使用 `DgnFile`、`DgnModel`、`Element`、`ElementAgenda` 和选择集。
- 创建、修改、替换和删除 DGN 元素。
- 开发交互式放置、定位、修改和 Primitive Tool。
- 处理鼠标输入、Reset、Dynamics、捕捉和工具生命周期。
- 读取和写入 EC 属性及 ItemType 数据。
- 开发 MicroStation 内嵌的 WinForms 或 WPF 界面。
- 检查 Bentley/MicroStation API 的命名空间和程序集引用问题。
- 检查 WinForms/WPF 与 MicroStation 集成时的常见错误。
- 排查 Addin 加载、API 版本和 UI 集成问题。

### 仓库结构

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── addin-framework.md
│   ├── course-code-snippets.md
│   ├── ec-itemtype.md
│   ├── elements-model-selection.md
│   ├── interactive-tools.md
│   ├── winforms-ui.md
│   └── wpf-ui.md
└── scripts/
    ├── check_microstation_references.py
    ├── check_winforms_rules.py
    └── check_wpf_rules.py
```

### 主要文件

#### `SKILL.md`

Skill 的主入口，定义适用场景、推荐工作流程、MicroStation 专用开发规则、校验要求以及参考文档的读取策略。

#### `agents/openai.yaml`

用于 Agent 发现和调用 Skill 的元数据配置。

#### `references/`

按主题拆分的技术参考资料。详细内容放在参考文档中，可避免主 Skill 文件过大，并允许 Agent 根据任务按需加载。

| 文件 | 内容 |
| --- | --- |
| `addin-framework.md` | Addin 入口、命令框架、配置、加载和工程组织 |
| `elements-model-selection.md` | DGN 模型、元素、选择集、Agenda、元素创建与修改 |
| `interactive-tools.md` | Primitive/Locate/Modify Tool、Dynamics、输入处理和生命周期 |
| `ec-itemtype.md` | EC Schema、EC Instance、ItemType 和自定义属性 |
| `winforms-ui.md` | WinForms 与 MicroStation 集成方式和约束 |
| `wpf-ui.md` | WPF 托管、窗口集成及相关 UI 规则 |
| `course-code-snippets.md` | 较完整的 MicroStation C# API 示例和代码片段集合 |

### 校验脚本

仓库提供三个轻量级静态检查脚本。

#### MicroStation 引用检查

```bash
python scripts/check_microstation_references.py <项目或源码目录>
```

用于检查可疑的 Bentley/MicroStation 引用及常见 API 使用问题。

#### WinForms 规则检查

```bash
python scripts/check_winforms_rules.py <项目或源码目录>
```

#### WPF 规则检查

```bash
python scripts/check_wpf_rules.py <项目或源码目录>
```

这些脚本用于开发辅助，不能替代在实际 MicroStation SDK 和运行环境中的编译与测试。

### 推荐工作流程

1. 首先确认目标 MicroStation 版本以及现有 Addin 使用的 .NET 运行时。
2. 在修改代码前检查项目中已有的 Bentley 程序集引用。
3. 阅读 `SKILL.md`，再根据当前任务读取对应的参考文档。
4. 优先使用项目中已经验证可用的 Bentley .NET API。
5. 在条件允许时，将 MicroStation UI 托管逻辑与业务逻辑分离。
6. 修改代码后运行仓库中的静态校验脚本。
7. 使用目标 MicroStation 对应的真实 Bentley 程序集进行编译。
8. 在 MicroStation 中验证交互工具、选择、Dynamics 和模型修改行为。

### MicroStation 开发注意事项

MicroStation Addin 对 Bentley 产品版本和程序集版本较为敏感。不同版本之间 API 的可用性和函数签名可能发生变化，因此：

- 不应默认较新 Bentley 版本中的 API 在旧工程中同样存在。
- 应以当前项目实际引用的 Bentley 程序集作为兼容性基线。
- 不应仅因为存在新的 API 就替换已经稳定工作的实现。
- Native/Managed 互操作和宿主窗口所有权需要谨慎处理。
- 条件允许时，应始终在真实 MicroStation 环境中完成最终编译和运行验证。

根据具体工程和版本，该 Skill 常涉及以下命名空间：

```csharp
Bentley.MstnPlatformNET
Bentley.DgnPlatformNET
Bentley.DgnPlatformNET.Elements
Bentley.ECObjects.Instance
Bentley.EC.Persistence
```

具体程序集和 API 必须以目标 SDK 及现有工程为准。

### 使用方式

可以将 `microstation-addin` 目录复制到 AI 编程工具支持的 Skills 目录中，也可以直接将本仓库作为 MicroStation Addin 开发参考资料使用。

Skill 主入口为：

```text
SKILL.md
```

Agent 应首先读取主 Skill，再按当前任务需要加载对应的 `references/` 文档。

### 设计原则

- **以工程事实为准**：先检查已有 Addin，再决定如何修改。
- **保证 Bentley API 准确性**：禁止臆造 MicroStation API、类型或函数签名。
- **关注版本兼容性**：保持与目标 MicroStation 版本一致。
- **最小化修改**：处理具体问题时避免无必要的大规模架构重写。
- **宿主环境意识**：WinForms/WPF 必须正确处理 MicroStation 的窗口所有权和生命周期。
- **保证交互正确性**：放置与定位工具应正确处理 Reset、Dynamics、清理和重新启动。
- **必须验证**：静态检查只能辅助开发，实际 SDK 编译和 MicroStation 运行结果才是最终依据。

### 贡献

欢迎补充经过验证的 Bentley API 使用方式、不同 MicroStation 版本的差异说明、校验规则以及真实 Addin 工程模式。

提交贡献时建议：

1. `SKILL.md` 保持精简，重点描述工作流程和约束。
2. 详细技术内容放入 `references/`。
3. 不加入未经验证或推测出来的 API。
4. 与特定版本相关的内容明确注明适用版本。
5. 示例代码尽可能保持聚焦并能够编译。
6. Git Commit 使用清晰、规范的英文描述。

### 免责声明

本仓库为独立开发者资源，并非 Bentley Systems 官方项目。Bentley、MicroStation 及相关产品名称和商标归其各自权利人所有。
