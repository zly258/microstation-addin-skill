# Interactive Tools

Use this reference for `DgnElementSetTool` and related interactive commands.

## Tool Choice

- Use `DgnTool` for simple mouse/keyboard interactions.
- Use `DgnPrimitiveTool` when view and mouse events are enough.
- Use `DgnElementSetTool` when the tool needs element locate, selection set, drag select, dynamic redraw, modification, or fence support.

Common lifecycle methods:

- `InstallNewInstance()`: static command entry used by `Commands.xml`.
- `OnInstall()`: configure element source before the tool starts.
- `OnPostInstall()`: initialize model state and prompts after activation.
- `OnDataButton(DgnButtonEvent ev)`: left-click/data button.
- `OnResetButton(DgnButtonEvent ev)`: right-click/reset button.
- `OnDynamicFrame(DgnButtonEvent ev)`: dynamic preview frame.
- `OnElementModify(Element element)`: modification callback.
- `OnModifyComplete(DgnButtonEvent ev)` or `ProcessAgenda(DgnButtonEvent ev)`: process collected elements.
- `OnRestartTool()`: reinstall the tool after completion.

## Dynamic Circle Drawing Pattern

The course dynamic drawing example stores the first data point, starts dynamics, previews an ellipse/circle, then writes the final element on the second data point.

```csharp
using System.Collections.Generic;
using Bentley.DgnPlatformNET;
using Bentley.DgnPlatformNET.Elements;
using Bentley.GeometryNET;
using Bentley.MstnPlatformNET;

namespace MyAddin.Tools
{
    internal sealed class CreateEllipseTool : DgnElementSetTool
    {
        private DgnModel m_dgnModel;
        private List<DPoint3d> m_points;

        private CreateEllipseTool(int toolId, int prompt) : base(toolId, prompt)
        {
        }

        public static void InstallNewInstance()
        {
            CreateEllipseTool tool = new CreateEllipseTool(0, 0);
            tool.InstallTool();
        }

        protected override void OnPostInstall()
        {
            base.OnPostInstall();
            m_dgnModel = Session.Instance.GetActiveDgnModel();
            m_points = new List<DPoint3d>();
            NotificationManager.OutputPrompt("输入圆心点");
        }

        protected override bool OnDataButton(DgnButtonEvent ev)
        {
            m_points.Add(ev.Point);

            if (m_points.Count == 1)
            {
                BeginDynamics();
                NotificationManager.OutputPrompt("输入半径点");
                return false;
            }

            EllipseElement element = CreateEllipseElement(m_points[0], m_points[1]);
            element.AddToModel();
            OnReinitialize();
            return true;
        }

        protected override void OnDynamicFrame(DgnButtonEvent ev)
        {
            if (m_points.Count == 1)
            {
                EllipseElement element = CreateEllipseElement(m_points[0], ev.Point);
                element.Redraw(DrawMode.TempDraw);
            }
        }

        protected override bool OnResetButton(DgnButtonEvent ev)
        {
            ExitTool();
            return true;
        }

        protected override void OnRestartTool()
        {
            InstallNewInstance();
        }

        public override StatusInt OnElementModify(Element element)
        {
            return StatusInt.Success;
        }

        private EllipseElement CreateEllipseElement(DPoint3d center, DPoint3d radiusPoint)
        {
            double radius = center.Distance(radiusPoint);
            EllipseElement ellipse = new EllipseElement(
                m_dgnModel,
                null,
                DPoint3d.Zero,
                radius,
                radius,
                DMatrix3d.Identity);

            Session.GetActiveViewport().GetRotation().TryInvert(out DMatrix3d invertMatrix);

            DTransform3d rotation = new DTransform3d(invertMatrix);
            ellipse.ApplyTransform(new TransformInfo(rotation));

            DTransform3d move = DTransform3d.FromTranslation(center);
            ellipse.ApplyTransform(new TransformInfo(move));

            return ellipse;
        }
    }
}
```

If `BeginDynamics`, `OnReinitialize`, or `NotificationManager` signatures differ in the installed SDK, search the existing project or `course-code-snippets.md` for `CreateEllipse`.

## Modify Located/Selected Elements

Use this pattern for a tool that changes properties on elements selected by locate, drag select, or a pre-existing selection set.

```csharp
using Bentley.DgnPlatformNET;
using Bentley.DgnPlatformNET.Elements;
using Bentley.MstnPlatformNET;

namespace MyAddin.Tools
{
    internal sealed class ChangeSolidColorTool : DgnElementSetTool
    {
        private DgnModelRef m_dgnModelRef;
        private int m_count;

        private ChangeSolidColorTool(int toolId, int prompt) : base(toolId, prompt)
        {
        }

        public static void InstallNewInstance()
        {
            ChangeSolidColorTool tool = new ChangeSolidColorTool(0, 0);
            tool.InstallTool();
        }

        protected override void OnPostInstall()
        {
            base.OnPostInstall();
            m_dgnModelRef = Session.Instance.GetActiveDgnModelRef();
            m_count = 0;
            NotificationManager.OutputPrompt("选择需要修改颜色的实体");
        }

        protected override bool WantAdditionalLocate(DgnButtonEvent ev)
        {
            return ElementAgenda.GetCount() == 0;
        }

        protected override UsesDragSelect AllowDragSelect()
        {
            return UsesDragSelect.Box;
        }

        protected override bool NeedAcceptPoint()
        {
            return false;
        }

        protected override bool OnModifyComplete(DgnButtonEvent ev)
        {
            ChangeSolidsColor();
            NotificationManager.OutputPrompt("修改实体数量: " + m_count);
            OnReinitialize();
            return true;
        }

        public override StatusInt OnElementModify(Element element)
        {
            return StatusInt.Success;
        }

        protected override bool OnResetButton(DgnButtonEvent ev)
        {
            ExitTool();
            return true;
        }

        protected override void OnRestartTool()
        {
            InstallNewInstance();
        }

        private void ChangeSolidsColor()
        {
            for (uint i = 0; i < ElementAgenda.GetCount(); i++)
            {
                Element original = ElementAgenda.GetEntry(i);
                Element changed = SetSolidColor(original);
                if (changed != null)
                {
                    changed.ReplaceInModel(original);
                    m_count++;
                }
            }
        }

        private Element SetSolidColor(Element element)
        {
            if (element.ElementType != MSElementType.Solid)
            {
                return null;
            }

            ElementPropertiesSetter setter = new ElementPropertiesSetter();
            setter.SetFillColor(3);
            setter.SetColor(3);
            setter.Apply(element);
            return element;
        }
    }
}
```

Use `ReplaceInModel(original)` after mutating an existing element. Do not call `AddToModel()` for modified existing elements.

## Active Fence Tool

Use this setup when a command must require an already active fence.

```csharp
protected override bool OnInstall()
{
    SetElementSource(ElementSource.Fence);
    return base.OnInstall();
}

protected override bool NeedPointForSelection()
{
    return false;
}

protected override bool NeedAcceptPoint()
{
    return false;
}

protected override bool UseActiveFence()
{
    return true;
}

protected override UsesFence AllowFence()
{
    return UsesFence.Required;
}
```

Process agenda and clip by active fence:

```csharp
protected override StatusInt ProcessAgenda(DgnButtonEvent ev)
{
    int count = ClipElementsByFence();
    NotificationManager.OutputPrompt("围栅剪切元素数量: " + count);
    OnReinitialize();
    return StatusInt.Success;
}

private int ClipElementsByFence()
{
    int count = 0;
    FenceParameters fenceParams = new FenceParameters(m_dgnModelRef, DTransform3d.Identity);
    FenceManager.InitFromActiveFence(fenceParams, true, true, FenceClipMode.Original);

    for (uint i = 0; i < ElementAgenda.GetCount(); i++)
    {
        ElementAgenda insideElems = new ElementAgenda();
        ElementAgenda outsideElems = new ElementAgenda();
        Element element = ElementAgenda.GetEntry(i);

        FenceManager.ClipElement(fenceParams, insideElems, outsideElems, element, FenceClipFlags.Optimized);

        for (uint j = 0; j < outsideElems.GetCount(); j++)
        {
            using (ElementCopyContext copyContext = new ElementCopyContext(m_dgnModelRef))
            {
                copyContext.DoCopy(outsideElems.GetEntry(j));
                count++;
            }
        }

        for (uint j = 0; j < insideElems.GetCount(); j++)
        {
            using (ElementCopyContext copyContext = new ElementCopyContext(m_dgnModelRef))
            {
                copyContext.DoCopy(insideElems.GetEntry(j));
                count++;
            }
        }
    }

    FenceManager.ClearFence();
    return count;
}
```

Search `course-code-snippets.md` for `FenceClipTool`, `WantAdditionalLocate`, `AllowDragSelect`, `NeedAcceptPoint`, `OnModifyComplete`, and `ProcessAgenda` before changing behavior.
