# WPF UI

Use this reference for WPF windows in MicroStation/OpenPlant Addins. The patterns here are based on the existing project files:

- `Tools/PlaceCustomSupportTool.cs`
- `Windows/PlaceSupportWindow.xaml`
- `Windows/PlaceSupportWindow.xaml.cs`
- `ViewModel/PlaceSupportViewModel.cs`

## Core Rules

- Keep WPF layout in `.xaml`; do not create the UI tree in `.xaml.cs`.
- Keep lifecycle, events, data loading, validation, and MicroStation calls in `.xaml.cs`.
- Keep user state in a ViewModel and bind with `DataContext`.
- Use `WPFInteropHelper` only when the existing project references the verified Bentley WPF assembly. In the sample OPM project this is `$(OPM)Assemblies\Bentley.MicroStation.WPF.dll`; do not invent or guess a DLL name for plain MicroStation projects.
- Use a singleton/static window pattern when a `DgnElementSetTool` needs to read current UI state while the tool is active.
- Close/detach the WPF window from the tool cleanup path.
- If hosting a WinForms control inside WPF, use `WindowsFormsHost` and keep the WinForms control as a separate user control.
- Vertically center content for all basic WPF controls. For `Button`, `CheckBox`, `RadioButton`, `TextBox`, `PasswordBox`, `ComboBox`, `Label`, and similar controls use `VerticalContentAlignment="Center"` directly or through an implicit `Style`. For `TextBlock`, use `VerticalAlignment="Center"`.

## Basic Control Centering

Prefer implicit styles at the window/user-control level so every basic control is covered consistently:

```xml
<Window.Resources>
    <Style TargetType="{x:Type Button}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type CheckBox}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type RadioButton}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type TextBox}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type PasswordBox}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type ComboBox}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type Label}">
        <Setter Property="VerticalContentAlignment" Value="Center" />
    </Style>
    <Style TargetType="{x:Type TextBlock}">
        <Setter Property="VerticalAlignment" Value="Center" />
    </Style>
</Window.Resources>
```

For a one-off control, explicit properties are also acceptable:

```xml
<Button Content="确定" VerticalContentAlignment="Center" />
<TextBox Text="{Binding Code}" VerticalContentAlignment="Center" />
<TextBlock Text="提示" VerticalAlignment="Center" />
```

## Project Items

For old-style `.NET Framework` projects, WPF windows need framework references and paired project items:

```xml
<Reference Include="PresentationCore" />
<Reference Include="PresentationFramework" />
<Reference Include="System.Xaml" />
<Reference Include="WindowsBase" />
```

Add these only when the XAML actually hosts WinForms:

```xml
<Reference Include="System.Windows.Forms" />
<Reference Include="WindowsFormsIntegration" />
```

Project item pattern:

```xml
<Compile Include="Windows\PlaceSupportWindow.xaml.cs">
  <DependentUpon>PlaceSupportWindow.xaml</DependentUpon>
</Compile>
<Page Include="Windows\PlaceSupportWindow.xaml">
  <SubType>Designer</SubType>
  <Generator>MSBuild:Compile</Generator>
</Page>
```

For WPF resources:

```xml
<Resource Include="Datas\SupportTypeCode.xml">
  <CopyToOutputDirectory>Always</CopyToOutputDirectory>
</Resource>
<Resource Include="Images\settings.png" />
```

## Tool Opens and Closes the WPF Window

Use `OnPostInstall` to open the WPF window, keep a typed field to read ViewModel state, and close the window in `OnCleanup`.

```csharp
private PlaceSupportWindow mWin;
private ScriptInfo _scriptInfo;

protected override void OnPostInstall()
{
    if (_scriptInfo == null)
    {
        MessageCenterHelper.ShowWarm("脚本为空！", true);
        ExitTool();
        return;
    }

    PlaceSupportWindow.OpenWindow(_scriptInfo);
    mWin = PlaceSupportWindow.s_window;

    BeginPickElements();
    AccuSnap.LocateEnabled = false;
    AccuSnap.SnapEnabled = true;

    NotificationManager.OutputPrompt("放置参数化支吊架：请选择管道");
}

protected override void OnCleanup()
{
    PlaceSupportWindow.CloseWindow();
    mWin = null;
    bMECObject1 = null;
}
```

Read UI state from the active window during the tool flow:

```csharp
if (mWin.ViewModel.CustomDirection)
{
    AccuDraw.Origin = startPt;
    SetupAndPromptForNextAction();
    NotificationManager.OutputPrompt("放置参数化支吊架：请选择方向");
}

if (mWin.ViewModel.ContinuousPlace)
{
    nPt = 0;
    AccuDraw.Origin = startPt;
}
else
{
    OnRestartTool();
}
```

## Dynamic Preview from Window Current Element

The tool can ask the WPF window for the current preview element and redraw it dynamically.

```csharp
protected override void OnDynamicFrame(DgnButtonEvent ev)
{
    try
    {
        RedrawElems redrawElems = new RedrawElems();
        redrawElems.SetDynamicsViewsFromActiveViewSet(Session.GetActiveViewport());
        redrawElems.DrawMode = DgnDrawMode.TempDraw;
        redrawElems.DrawPurpose = DrawPurpose.Dynamics;

        if (bMECObject1 == null || mWin == null)
        {
            return;
        }

        Element cellEle = mWin.CurrentElement;
        if (cellEle == null)
        {
            return;
        }

        DTransform3d transform1 = DTransform3d.FromTranslation(ev.Point);
        DTransform3d transform2 = DTransform3d.FromMatrixAndFixedPoint(
            bMECObject1.Transform3d.Matrix,
            ev.Point);

        redrawElems.Transform = transform2 * transform1;
        redrawElems.DoRedraw(cellEle);
    }
    catch
    {
    }
}
```

Prefer the project's existing transform math for real placement; the snippet only shows the window/tool interaction pattern.

## WPF Window Code-Behind Pattern

Use `WPFInteropHelper` to attach the WPF window to MicroStation, subscribe to `Loaded`, set `DataContext`, detach on close, and reset the static singleton.

```csharp
using Bentley.DgnPlatformNET.Elements;
using Bentley.MstnPlatformNET;
using Bentley.MstnPlatformNET.WPF;
using System.Collections.Generic;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace OPMParametricToolAddin2.Windows
{
    public partial class PlaceSupportWindow : Window
    {
        private ScriptInfo _scriptInfo;
        private string _configPath;
        private WPFInteropHelper m_wndHelper;
        private bool _closeFlag;
        private Element currentElement;

        public static PlaceSupportWindow s_window;
        public PlaceSupportViewModel ViewModel = new PlaceSupportViewModel();
        public Dictionary<string, string> SpecParameterValueDict;

        public PlaceSupportWindow()
        {
            InitializeComponent();

            m_wndHelper = new WPFInteropHelper(this);
            m_wndHelper.Attach(MainAddin.Instance, true, "PlaceSupportWindow");

            Loaded += PlaceSupportWindow_Loaded;
        }

        private void PlaceSupportWindow_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                string specFile = _scriptInfo.GetSpec;
                if (File.Exists(specFile))
                {
                    CbbSpecSheet.ItemsSource = ExcelHelper.GetSheetNames(specFile);
                }

                _configPath = ConfigHelper.GetFormConfigFilePath("PlaceSupportViewModel");
                PlaceSupportViewModel saved = XMLHelper.LoadFromXml<PlaceSupportViewModel>(_configPath);
                if (saved != null)
                {
                    ViewModel = saved;
                }

                DataContext = ViewModel;
                if (CbbSpecSheet.Items.Contains(ViewModel.SpecSheetName))
                {
                    CbbSpecSheet.SelectedItem = ViewModel.SpecSheetName;
                }
                if (string.IsNullOrWhiteSpace(ViewModel.SpecSheetName) && CbbSpecSheet.Items.Count > 0)
                {
                    CbbSpecSheet.SelectedIndex = 0;
                }
            }
            catch (System.Exception ex)
            {
                MessageCenterHelper.ShowError($"PlaceSupportWindow.Loaded ex={ex.Message}", ex.StackTrace);
            }

            Closing += Window_Closing;
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            XMLHelper.SaveToXml(_configPath, ViewModel);

            m_wndHelper.Detach();
            m_wndHelper.Dispose();

            if (s_window?._closeFlag == false)
            {
                Session.Instance.EnqueueKeyin("runxcommand Mstn.Selection.SelectElement");
            }

            s_window = null;
        }

        public static void OpenWindow(ScriptInfo scriptInfo)
        {
            if (s_window == null)
            {
                s_window = new PlaceSupportWindow();
                s_window._scriptInfo = scriptInfo;
                s_window.Show();
            }
        }

        public static void CloseWindow()
        {
            if (s_window != null)
            {
                s_window._closeFlag = true;
                s_window.Close();
            }
        }

        public Element CurrentElement
        {
            get
            {
                if (currentElement == null)
                {
                    currentElement = _scriptInfo.CreateCellElement();
                }
                return currentElement;
            }
        }
    }
}
```

## XAML Layout Pattern

Use XAML for structure, resources, bindings, and event wiring. This pattern includes XML data, image preview, bound controls, and a hosted WinForms parameter control.

```xml
<Window x:Class="OPMParametricToolAddin2.Windows.PlaceSupportWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:wfi="clr-namespace:System.Windows.Forms.Integration;assembly=WindowsFormsIntegration"
        xmlns:usercontrols="clr-namespace:CustomScriptAddin.UserControls;assembly=CustomScriptAddin"
        mc:Ignorable="d"
        Title="放置支吊架"
        Height="630"
        Width="300">
    <Window.Resources>
        <Style TargetType="{x:Type Button}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type CheckBox}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type RadioButton}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type TextBox}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type PasswordBox}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type ComboBox}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type Label}">
            <Setter Property="VerticalContentAlignment" Value="Center" />
        </Style>
        <Style TargetType="{x:Type TextBlock}">
            <Setter Property="VerticalAlignment" Value="Center" />
        </Style>
        <XmlDataProvider x:Key="SupportTypeCodeSource"
                         Source="/OPMParametricToolAddin2;component/Datas/SupportTypeCode.xml"
                         XPath="SupportTypeCodes/SupportTypeCode" />
    </Window.Resources>

    <Grid Margin="1.5">
        <Grid.RowDefinitions>
            <RowDefinition Height="25" />
            <RowDefinition Height="2*" />
            <RowDefinition Height="5" />
            <RowDefinition Height="3*" />
            <RowDefinition Height="25" />
        </Grid.RowDefinitions>

        <ToolBar>
            <Button Content="预览材料表" Click="Btn_ViewReport" />
            <Separator />
            <Button Content="选择规格" Click="Btn_SelectSpec" />
        </ToolBar>

        <Border Grid.Row="1" Margin="0,1.5,0,0" BorderThickness="1" BorderBrush="LightGray">
            <Image x:Name="ImgModel"
                   MouseLeftButtonDown="ImgModel_MouseLeftButtonDown"
                   RenderOptions.BitmapScalingMode="HighQuality"
                   Stretch="Uniform" />
        </Border>

        <GridSplitter Grid.Row="2" HorizontalAlignment="Stretch" />

        <DockPanel Grid.Row="3">
            <GroupBox Header="设置" DockPanel.Dock="Top">
                <StackPanel>
                    <StackPanel Orientation="Horizontal" Margin="0,1">
                        <Label Content="代号" />
                        <ComboBox x:Name="CbbCode"
                                  Width="100"
                                  Height="23"
                                  SelectionChanged="CbbCode_SelectionChanged"
                                  ItemsSource="{Binding Source={StaticResource SupportTypeCodeSource}}"
                                  SelectedValuePath="ENName"
                                  DisplayMemberPath="CNName" />
                        <CheckBox Content="连续放置"
                                  Margin="10,0,0,0"
                                  IsChecked="{Binding ContinuousPlace, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
                    </StackPanel>

                    <StackPanel Orientation="Horizontal" Margin="0,1">
                        <Label Content="规格" />
                        <ComboBox x:Name="CbbSpecSheet"
                                  Width="100"
                                  SelectedValue="{Binding SpecSheetName, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
                        <CheckBox Content="指定方向"
                                  Margin="10,0,0,0"
                                  IsChecked="{Binding CustomDirection, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
                    </StackPanel>
                </StackPanel>
            </GroupBox>

            <wfi:WindowsFormsHost>
                <usercontrols:ParameterControl x:Name="parameterControl" />
            </wfi:WindowsFormsHost>
        </DockPanel>

        <Label Grid.Row="4" VerticalContentAlignment="Center" Content="Ctrl切换起点，Alt切换方向" />
    </Grid>
</Window>
```

## ViewModel Pattern

Use property notification for values bound from XAML.

```csharp
using CommonLibs.MVVM;

namespace OPMParametricToolAddin2.ViewModel
{
    public class PlaceSupportViewModel : NotifyObject
    {
        private string _specSheetName;
        public string SpecSheetName
        {
            get => _specSheetName;
            set => SetProperty(ref _specSheetName, value);
        }

        private string _code = "SP";
        public string Code
        {
            get => _code;
            set => SetProperty(ref _code, value);
        }

        private bool _customDirection;
        public bool CustomDirection
        {
            get => _customDirection;
            set => SetProperty(ref _customDirection, value);
        }

        private bool _continuousPlace;
        public bool ContinuousPlace
        {
            get => _continuousPlace;
            set => SetProperty(ref _continuousPlace, value);
        }
    }
}
```

## Placement Flow Pattern

For a WPF-driven `DgnElementSetTool`:

1. `OnPostInstall`: validate input script, open WPF window, store `mWin`, start element picking.
2. First `OnDataButton`: locate the pipe/component, update `_scriptInfo` defaults, call `mWin.SetParameterInfo(...)`, initialize `AccuDraw`, begin dynamics.
3. `OnDynamicFrame`: fetch `mWin.CurrentElement`, apply transform, redraw temp geometry.
4. Next `OnDataButton`: read `mWin.ViewModel` and parameter values, create/update EC/BMEC object, decide whether to continue or restart.
5. Modifier keys: update port/direction, restart dynamics.
6. `OnCleanup`: close WPF window and clear tool state.

Do not let the WPF window create DGN elements directly when the placement state belongs to the active interactive tool. Let the tool own placement; let the window own parameters, binding, preview source, and persisted UI options.

## Validation

Run:

```powershell
python scripts/check_wpf_rules.py <project-or-solution-dir>
```

The script checks WPF `.xaml`/`.xaml.cs` pairing, code-behind layout leakage, basic-control vertical content centering, and old-style `.csproj` `Page`/`DependentUpon` entries when a project file is present.
