# WinForms UI

Use this reference for MicroStation Addin WinForms UI. The course examples include normal WinForms controls and MicroStation adapter-based forms. The user's rule overrides any generated designer default:

- Every form/user control must have the standard three files: `Name.cs`, `Name.Designer.cs`, and `Name.resx`.
- Put UI layout, control creation, sizes, locations, anchoring/docking, `AutoScaleMode`, and design-time font settings in `Name.Designer.cs`.
- Put constructor code, event handlers, command entry methods, validation, and MicroStation model operations in `Name.cs`.
- Put resources in `Name.resx`. Do not collapse resources or layout into the main `.cs` file.
- `AutoScaleMode` must be `System.Windows.Forms.AutoScaleMode.Dpi`.
- Font must be Microsoft YaHei (`"Microsoft YaHei"`; Chinese display name `"微软雅黑"` is acceptable for explanation, but use the English font family in code).

## Required Three-File Structure

For a form named `BeamCreateMenu`, create and maintain exactly this WinForms file split:

```text
BeamCreateMenu.cs
BeamCreateMenu.Designer.cs
BeamCreateMenu.resx
```

`BeamCreateMenu.cs`:

```csharp
using System;
using System.Windows.Forms;

namespace MyAddin.UI
{
    public partial class BeamCreateMenu : Form
    {
        public BeamCreateMenu()
        {
            InitializeComponent();
        }

        private void buttonCreate_Click(object sender, EventArgs e)
        {
            // Validate input and call MicroStation model code here.
        }
    }
}
```

`BeamCreateMenu.Designer.cs`:

```csharp
namespace MyAddin.UI
{
    partial class BeamCreateMenu
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Button buttonCreate;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.buttonCreate = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // buttonCreate
            // 
            this.buttonCreate.Location = new System.Drawing.Point(12, 12);
            this.buttonCreate.Name = "buttonCreate";
            this.buttonCreate.Size = new System.Drawing.Size(90, 30);
            this.buttonCreate.TabIndex = 0;
            this.buttonCreate.Text = "创建";
            this.buttonCreate.UseVisualStyleBackColor = true;
            this.buttonCreate.Click += new System.EventHandler(this.buttonCreate_Click);
            // 
            // BeamCreateMenu
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 17F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi;
            this.ClientSize = new System.Drawing.Size(320, 180);
            this.Controls.Add(this.buttonCreate);
            this.Font = new System.Drawing.Font("Microsoft YaHei", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Name = "BeamCreateMenu";
            this.Text = "梁生成";
            this.ResumeLayout(false);
        }
    }
}
```

`BeamCreateMenu.resx`: keep the normal Visual Studio-generated `.resx` file, even when no explicit icon/image resource is currently used.

For old-style `.NET Framework` `.csproj`, keep the dependent file relationship:

```xml
<Compile Include="BeamCreateMenu.cs">
  <SubType>Form</SubType>
</Compile>
<Compile Include="BeamCreateMenu.Designer.cs">
  <DependentUpon>BeamCreateMenu.cs</DependentUpon>
</Compile>
<EmbeddedResource Include="BeamCreateMenu.resx">
  <DependentUpon>BeamCreateMenu.cs</DependentUpon>
</EmbeddedResource>
```

For a `UserControl`, use the same split with `<SubType>UserControl</SubType>`.

## Mandatory Designer Pattern

Apply this in every `.Designer.cs` file for forms and user controls:

```csharp
this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi;
this.Font = new System.Drawing.Font(
    "Microsoft YaHei",
    9F,
    System.Drawing.FontStyle.Regular,
    System.Drawing.GraphicsUnit.Point,
    ((byte)(134)));
```

If the designer generated `AutoScaleMode.Font`, replace it with `AutoScaleMode.Dpi`.

For `UserControl`, also set its font:

```csharp
this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi;
this.Font = new System.Drawing.Font("Microsoft YaHei", 9F);
```

## Defensive Runtime Enforcement

Use this helper after `InitializeComponent()` only as a runtime fallback when editing an existing UI with nested controls. Keep `AutoScaleMode`, control layout, and design-time font settings in `.Designer.cs`; the helper is not a replacement for the hard three-file rule.

```csharp
using System.Drawing;
using System.Windows.Forms;

internal static class WinFormsStyle
{
    public static void Apply(Control root)
    {
        if (root == null)
        {
            return;
        }

        root.Font = new Font("Microsoft YaHei", root.Font.Size, root.Font.Style, root.Font.Unit);
        foreach (Control child in root.Controls)
        {
            Apply(child);
        }
    }
}
```

Constructor pattern:

```csharp
public partial class BeamCreateMenu : Form
{
    public BeamCreateMenu()
    {
        InitializeComponent();
        WinFormsStyle.Apply(this);
    }
}
```

If the project uses MicroStation's WinForms adapter, keep the existing base class from the project/course example:

```csharp
using Bentley.MstnPlatformNET.WinForms;

public partial class BeamCreateMenu : Adapter
{
    public BeamCreateMenu()
    {
        InitializeComponent();
        WinFormsStyle.Apply(this);
    }
}
```

## Show UI from Command

Keep one instance if the UI should behave like a singleton tool window; otherwise create a new dialog per command.

```csharp
private static BeamCreateMenu s_beamCreateMenu;

public static void ShowBeamCreateMenu(string unparsed)
{
    if (s_beamCreateMenu == null || s_beamCreateMenu.IsDisposed)
    {
        s_beamCreateMenu = new BeamCreateMenu();
    }

    s_beamCreateMenu.Show();
    s_beamCreateMenu.Activate();
}
```

For modal input:

```csharp
public static void ShowDialogMenu(string unparsed)
{
    using (BeamCreateMenu form = new BeamCreateMenu())
    {
        form.ShowDialog();
    }
}
```

## Common Control Snippets

Button click:

```csharp
private void button1_Click(object sender, EventArgs e)
{
    MessageBox.Show("确认");
}
```

CheckBox:

```csharp
private void checkBox1_CheckedChanged(object sender, EventArgs e)
{
    bool enabled = checkBox1.Checked;
}
```

ComboBox:

```csharp
comboBox1.Items.Add("obj");
comboBox1.Items.Remove("obj");
comboBox1.Items.Clear();
bool isExist = comboBox1.Items.Contains("obj");
```

ListBox:

```csharp
listBox1.Items.Add("obj");
listBox1.Items.Remove("obj");
listBox1.Items.Clear();
bool isExist = listBox1.Items.Contains("obj");
```

TreeView:

```csharp
TreeNode root = treeView1.Nodes.Add("Root");
root.Nodes.Add("Child");
treeView1.ExpandAll();
```

TextBox numeric-only input:

```csharp
private void textBox1_KeyPress(object sender, KeyPressEventArgs e)
{
    bool isDigit = char.IsDigit(e.KeyChar);
    bool isControl = char.IsControl(e.KeyChar);
    e.Handled = !(isDigit || isControl);
}
```

ProgressBar:

```csharp
progressBar1.Minimum = 0;
progressBar1.Maximum = 100;
progressBar1.Value = 50;
```

## DGN Preview Control

The course uses a custom `PreviewPanel : UserControl` backed by a Bentley preview control. When adapting that pattern:

- Keep `unsafe` blocks only if the existing project already enables them.
- Pass the target `DgnModelRef` into the preview panel constructor.
- Apply the same DPI/font rules to the panel designer and constructor.
- Search `course-code-snippets.md` for `PreviewPanel` and `Bentley.DgnPlatform.PreviewControl` before rewriting.

## UI + Model Operation Pattern

For UI-driven model creation:

1. Validate text input.
2. Convert units with `UorPerMeter` or `UorPerMaster`.
3. Create elements in memory.
4. Apply transforms/properties.
5. Call `AddToModel()` or `ReplaceInModel(original)`.
6. Report concise success/failure.

Example:

```csharp
private void buttonCreate_Click(object sender, EventArgs e)
{
    if (!double.TryParse(textBoxWidth.Text, out double widthMm))
    {
        MessageBox.Show("请输入有效宽度");
        return;
    }

    DgnModel model = Session.Instance.GetActiveDgnModel();
    double uorPerMeter = model.GetModelInfo().UorPerMeter;
    double width = widthMm / 1000.0 * uorPerMeter;

    DPoint3d[] points =
    {
        DPoint3d.Zero,
        new DPoint3d(width, 0, 0),
        new DPoint3d(width, width, 0),
        new DPoint3d(0, width, 0)
    };

    ShapeElement shape = new ShapeElement(model, null, points);
    shape.AddToModel();
}
```

## Validation

Run the bundled script from the skill folder:

```powershell
python scripts/check_winforms_rules.py <project-or-solution-dir>
```

Fix every reported `.Designer.cs` or form/control file before finalizing.
