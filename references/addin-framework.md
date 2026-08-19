# Addin Framework

Use this reference for project setup, Addin entry classes, command key-ins, auto-loading, and Visual Studio debugging.

## Project Baseline

- Create a C# Class Library targeting `.NET Framework 4.6.2` for the tutorial baseline.
- Open Visual Studio as administrator when outputting to the MicroStation installation directory.
- Output the DLL to the MicroStation `Mdlapps` folder unless the repo already uses a different deploy path.
- Reference `ustation.dll` from the MicroStation installation folder for the Addin framework.
- Add `System.Windows.Forms` when using message boxes or WinForms UI.
- Define `MS` in the project file and reference Bentley DLLs through `$(MS)` plus relative `HintPath`; do not commit absolute DLL paths.
- If using SDK examples as a template, define `MS` and `ReferencePath` in the project file when references use `$(MS)`.

```xml
<MS Condition="'$(MS)' == ''">C:\Program Files\Bentley\MicroStation CONNECT Edition\MicroStation\</MS>
<ReferencePath>$(MS);$(MS)Assemblies\ECFramework\</ReferencePath>
```

Keep the trailing backslash on the `MS` value. The conditional form allows a developer or build script to override the MicroStation path with an `MS` environment variable or `/p:MS=...`.

## DLL Reference Rules

Use `$(MS)` and relative paths from the MicroStation root. Set `<Private>False</Private>` for Bentley runtime DLLs so Visual Studio does not copy MicroStation assemblies into the Addin output.

Treat the tables below as a strict whitelist for this skill. Do not add Bentley DLL references by guessing from a namespace, class name, method name, sample heading, or compiler error. If a project truly needs another Bentley DLL, first verify the exact file in the installed MicroStation/SDK directory or an existing working project, then update this reference and `scripts/check_microstation_references.py` with that evidence.

Baseline Addin + element/model work:

| DLL | HintPath | Use |
| --- | --- | --- |
| `ustation.dll` | `$(MS)ustation.dll` | Addin framework, `Bentley.MstnPlatformNET.Addin`, command integration |
| `Bentley.DgnPlatformNET.dll` | `$(MS)Bentley.DgnPlatformNET.dll` | DGN model/file/element platform APIs |
| `Bentley.DgnDisplayNet.dll` | `$(MS)Bentley.DgnDisplayNet.dll` | element display and redraw-related APIs |
| `Bentley.GeometryNET.dll` | `$(MS)Bentley.GeometryNET.dll` | geometry primitives, transforms, points, vectors, matrices |
| `Bentley.GeometryNET.Common.dll` | `$(MS)Bentley.GeometryNET.Common.dll` | shared geometry support types |

Add these when using EC, ItemType, ECSchema, `DgnECManager`, `IDgnECInstance`, or property workflows:

| DLL | HintPath | Use |
| --- | --- | --- |
| `Bentley.EC.Persistence3.dll` | `$(MS)Assemblies\ECFramework\Bentley.EC.Persistence3.dll` | EC persistence/read-write support |
| `Bentley.ECObjects.Interop3.dll` | `$(MS)Assemblies\ECFramework\Bentley.ECObjects.Interop3.dll` | EC interop layer |
| `Bentley.ECObjects3.dll` | `$(MS)Assemblies\ECFramework\Bentley.ECObjects3.dll` | EC schema/class/property object model |
| `Bentley.ECSystem3.dll` | `$(MS)Assemblies\ECFramework\Bentley.ECSystem3.dll` | EC system services |

Do not reference these DLLs from arbitrary copied folders. Match the installed MicroStation and SDK version.

### .csproj Reference Template

Use this old-style .NET Framework project pattern unless the existing project already has a working equivalent:

```xml
<PropertyGroup>
  <TargetFrameworkVersion>v4.6.2</TargetFrameworkVersion>
  <MS Condition="'$(MS)' == ''">C:\Program Files\Bentley\MicroStation CONNECT Edition\MicroStation\</MS>
  <ReferencePath>$(MS);$(MS)Assemblies\ECFramework\</ReferencePath>
</PropertyGroup>

<ItemGroup>
  <Reference Include="ustation">
    <HintPath>$(MS)ustation.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.DgnPlatformNET">
    <HintPath>$(MS)Bentley.DgnPlatformNET.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.DgnDisplayNet">
    <HintPath>$(MS)Bentley.DgnDisplayNet.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.GeometryNET">
    <HintPath>$(MS)Bentley.GeometryNET.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.GeometryNET.Common">
    <HintPath>$(MS)Bentley.GeometryNET.Common.dll</HintPath>
    <Private>False</Private>
  </Reference>
</ItemGroup>

<ItemGroup>
  <Reference Include="Bentley.EC.Persistence3">
    <HintPath>$(MS)Assemblies\ECFramework\Bentley.EC.Persistence3.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.ECObjects.Interop3">
    <HintPath>$(MS)Assemblies\ECFramework\Bentley.ECObjects.Interop3.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.ECObjects3">
    <HintPath>$(MS)Assemblies\ECFramework\Bentley.ECObjects3.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="Bentley.ECSystem3">
    <HintPath>$(MS)Assemblies\ECFramework\Bentley.ECSystem3.dll</HintPath>
    <Private>False</Private>
  </Reference>
</ItemGroup>
```

For a project that does not use EC/ItemType, omit the ECFramework reference group. For course-style examples that may use most APIs, include the full set.

## Addin Entry Class

The tutorial states three required conditions for a .NET assembly to run as a MicroStation Addin:

1. Include a class derived from `Bentley.MstnPlatformNET.Addin`.
2. Provide a constructor with the single MDL descriptor pointer parameter and chain it to the base constructor.
3. Override `Run()`, which is executed after the constructor and acts like the Addin entry point.

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

        public static void OutputWordsSuccess(string unparsed)
        {
            MessageBox.Show("Success");
        }
    }
}
```

Load manually from MicroStation Key-in:

```text
mdl load MyMicroStationAddin
```

## Commands.xml

Prefer copying a working `Commands.xml` from the MicroStation SDK example or existing project, then edit the command words and handler names. The course notes describe the required structure:

- One `KeyinTree` root.
- `RootKeyinTable` for the root command words.
- `SubKeyinTables` for nested command words.
- `KeyinHandlers` mapping a full `Keyin` string to a handler `Function`.
- `KeyinHandler Keyin` must match the words defined in `RootKeyinTable` and `SubKeyinTables`.
- `Function` must match a public static command method, usually `public static void Handler(string unparsed)`.

Typical handler:

```csharp
public static void OutputWordsSuccess(string unparsed)
{
    MessageBox.Show("Success");
}
```

Project file embedding must make the resource logical name `CommandTable.xml`:

```xml
<EmbeddedResource Include="Commands.xml">
  <SubType>Designer</SubType>
  <LogicalName>CommandTable.xml</LogicalName>
</EmbeddedResource>
```

Before changing XML, save the Visual Studio project. Editing `.csproj` while Visual Studio has unsaved changes can discard work when the project reloads.

## Auto Load

For a managed Addin DLL under `Mdlapps`, use `MS_DGNAPPS`.

Create a `.cfg` file under the MicroStation `config/appl` folder:

```text
MS_DGNAPPS > MyApp.dll
```

Or set the configuration variable in MicroStation:

```text
MS_DGNAPPS = MyApp.dll;AnotherApp.dll
```

Use semicolons between multiple DLL names. Auto-loading increases MicroStation startup time and fails noisily when configured DLLs are missing.

For old MDL `.ma` or `.ma` + `.dll` packages, use the MDL loading mechanism described by the SDK/template rather than treating them as Addins.

## Visual Studio Debugging

For Addin debugging:

1. Build the DLL into `Mdlapps`.
2. Start MicroStation.
3. Attach Visual Studio to the MicroStation process, or set MicroStation as the external program in project Debug settings.
4. Load the Addin with `mdl load <assembly-name>`.
5. Trigger the command key-in mapped in `Commands.xml`.

Useful debugger actions:

- `F10` Step Over for normal line-by-line execution.
- `F11` Step Into when entering a method is necessary.
- `Shift+F11` Step Out to return to the caller.
- `F5` Continue to next breakpoint.
- Set Next Statement only when you understand the changed execution path.

## Common Failure Checks

- DLL did not build into `Mdlapps`: check project output path and admin rights.
- `mdl load` cannot find DLL: check file name and path.
- Key-in does nothing: verify `Commands.xml` is embedded as `CommandTable.xml`, key-in words match, and handler method is public static.
- Yellow warning icons on references: update `<MS>` path and reload the project.
- API references unresolved: verify MicroStation and SDK versions match.
