# Elements, Models, Selection, Scan, Fence

Use this reference for DGN model access, element creation, transforms, copy/delete, selection sets, scans, and fences.

## Common Usings

```csharp
using System.Windows.Forms;
using Bentley.DgnPlatformNET;
using Bentley.DgnPlatformNET.Elements;
using Bentley.GeometryNET;
using Bentley.MstnPlatformNET;
```

## Units

Use model resolution ratios before hard-coding dimensions. For model-unit-relative geometry, multiply by `UorPerMaster`. For real-world standard components that should not change with master unit settings, use `UorPerMeter`.

```csharp
public static void CmdUnitConversion(string unparsed)
{
    double uorPerMas = Session.Instance.GetActiveDgnModel().GetModelInfo().UorPerMaster;
    double uorPerMeter = Session.Instance.GetActiveDgnModel().GetModelInfo().UorPerMeter;
    double uorPerSub = Session.Instance.GetActiveDgnModel().GetModelInfo().UorPerSub;

    MessageBox.Show("UorPerMaster = " + uorPerMas
        + "\nUorPerMeter = " + uorPerMeter
        + "\nUorPerSub = " + uorPerSub);
}
```

## Create Elements

Create geometry in memory, create an element from it, then call `AddToModel()`.

### LineElement

```csharp
public static void CmdCreateLine(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();

    DPoint3d p1 = DPoint3d.Zero;
    DPoint3d p2 = new DPoint3d(10000, 0, 0);
    DSegment3d segment = new DSegment3d(p1, p2);

    LineElement line = new LineElement(dgnModel, null, segment);
    line.AddToModel();
}
```

### LineStringElement

```csharp
public static void CmdCreateLineString(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();

    DPoint3d[] points =
    {
        DPoint3d.Zero,
        new DPoint3d(10000, 10000, 0),
        new DPoint3d(20000, 0, 0),
        new DPoint3d(30000, -10000, 0),
        new DPoint3d(40000, 0, 0)
    };

    LineStringElement lineString = new LineStringElement(dgnModel, null, points);
    lineString.AddToModel();
}
```

### ArcElement

```csharp
public static void CmdCreateArc(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    DPoint3d center = DPoint3d.Zero;

    ArcElement arc = new ArcElement(
        dgnModel,
        null,
        center,
        50000,
        50000,
        DMatrix3d.Identity,
        Angle.PI.Radians / 3,
        Angle.PI.Radians);

    arc.AddToModel();
}
```

### ShapeElement

```csharp
public static void CmdCreateShape(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    DPoint3d[] points =
    {
        new DPoint3d(-5 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(5 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(5 * uorPerMas, -5 * uorPerMas, 0),
        new DPoint3d(-5 * uorPerMas, -5 * uorPerMas, 0)
    };

    ShapeElement shape = new ShapeElement(dgnModel, null, points);
    shape.AddToModel();
}
```

### ComplexStringElement

Complex element components must be ordered and connected end-to-start.

```csharp
public static void CmdCreateComplexString(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();

    LineElement line = new LineElement(
        dgnModel,
        null,
        new DSegment3d(DPoint3d.Zero, new DPoint3d(10000, 0, 0)));

    ArcElement arc = new ArcElement(
        dgnModel,
        null,
        DPoint3d.Zero,
        10000,
        10000,
        DMatrix3d.Identity,
        0,
        Angle.PI.Radians / 2);

    DPoint3d[] points =
    {
        new DPoint3d(0, 10000, 0),
        new DPoint3d(-10000, 10000, 0),
        new DPoint3d(-10000, 20000, 0),
        new DPoint3d(20000, 20000, 0)
    };
    LineStringElement lineString = new LineStringElement(dgnModel, null, points);

    ComplexStringElement complexString = new ComplexStringElement(dgnModel, null);
    complexString.AddComponentElement(line);
    complexString.AddComponentElement(arc);
    complexString.AddComponentElement(lineString);
    complexString.AddComponentComplete();
    complexString.AddToModel();
}
```

## Transform Elements

Apply transforms before `AddToModel()` for new elements, or call `ReplaceInModel(original)` after transforming an existing element.

### Move

```csharp
public static void CmdElementMove(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    LineElement line = new LineElement(
        dgnModel,
        null,
        new DSegment3d(DPoint3d.Zero, new DPoint3d(10 * uorPerMas, 0, 0)));

    DTransform3d trans = DTransform3d.FromTranslation(new DPoint3d(0, 5 * uorPerMas, 0));
    line.ApplyTransform(new TransformInfo(trans));
    line.AddToModel();
}
```

### Rotate Around Axis

```csharp
public static void CmdElementRotateWithCustomAxis(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    LineElement line = new LineElement(
        dgnModel,
        null,
        new DSegment3d(
            new DPoint3d(-10 * uorPerMas, 0, 0),
            new DPoint3d(10 * uorPerMas, 0, 0)));

    Angle angle = new Angle();
    angle.Degrees = 45;

    DTransform3d trans = DTransform3d.FromRotationAroundLine(
        new DPoint3d(5 * uorPerMas, 5 * uorPerMas, 0),
        DVector3d.UnitZ,
        angle);

    line.ApplyTransform(new TransformInfo(trans));
    line.AddToModel();
}
```

### Scale

```csharp
public static void CmdElementScale(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    DPoint3d[] points =
    {
        new DPoint3d(-5 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(5 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(5 * uorPerMas, -5 * uorPerMas, 0),
        new DPoint3d(-5 * uorPerMas, -5 * uorPerMas, 0)
    };

    ShapeElement shape = new ShapeElement(dgnModel, null, points);
    shape.ApplyTransform(new TransformInfo(DTransform3d.Scale(2, 1, 1)));
    shape.AddToModel();
}
```

### Copy and Delete

Always dispose `ElementCopyContext`; otherwise copied elements can be incomplete.

```csharp
public static void CmdElementCopy(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    DPoint3d[] points =
    {
        new DPoint3d(5 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(10 * uorPerMas, 5 * uorPerMas, 0),
        new DPoint3d(10 * uorPerMas, -5 * uorPerMas, 0),
        new DPoint3d(5 * uorPerMas, -5 * uorPerMas, 0)
    };

    ShapeElement shape = new ShapeElement(dgnModel, null, points);
    shape.AddToModel();

    using (ElementCopyContext context = new ElementCopyContext(dgnModel))
    {
        context.DoCopy(shape);
    }
}
```

```csharp
public static void CmdElementDelete(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    long id = 1428;
    Element elem = dgnModel.FindElementById(new ElementId(ref id));

    if (elem != null)
    {
        elem.DeleteFromModel();
    }
}
```

## Selection Set

Use `ElementAgenda` as the container for selected elements.

```csharp
public static void QueryElemsInSelection(string unparsed)
{
    ElementAgenda agenda = new ElementAgenda();
    SelectionSetManager.BuildAgenda(ref agenda);

    string result = "The selected elements:\n";
    for (uint i = 0; i < agenda.GetCount(); i++)
    {
        Element elem = agenda.GetEntry(i);
        result += (i + 1) + ": ElementId = " + elem.ElementId
            + ", Element type = " + elem.ElementType + "\n";
    }

    MessageBox.Show(result);
}
```

```csharp
public static void AddSolidsToSelection(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    SelectionSetManager.EmptyAll();

    foreach (Element elem in dgnModel.GetGraphicElements())
    {
        if (elem.ElementType == MSElementType.Solid)
        {
            SelectionSetManager.AddElement(elem, dgnModel);
        }
    }
}
```

```csharp
public static void RemoveSolidsFromSelection(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    ElementAgenda agenda = new ElementAgenda();
    SelectionSetManager.BuildAgenda(ref agenda);

    for (uint i = 0; i < agenda.GetCount(); i++)
    {
        Element elem = agenda.GetEntry(i);
        if (elem.ElementType == MSElementType.Solid)
        {
            SelectionSetManager.RemoveElement(elem, dgnModel);
        }
    }
}
```

## Scan Criteria

Use scan criteria when filtering by element type and range is cheaper than iterating every element.

```csharp
public static void FilterByScanCriteria(string unparsed)
{
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    double uorPerMas = dgnModel.GetModelInfo().UorPerMaster;

    ScanCriteria sc = new ScanCriteria();
    sc.SetModelRef(dgnModel);
    sc.SetModelSections(DgnModelSections.GraphicElements);

    BitMask elemTypeMask = new BitMask(false);
    elemTypeMask.Capacity = 128;
    elemTypeMask.ClearAll();
    elemTypeMask.SetBit(18, true); // Solid element type number - 1.
    sc.SetElementTypeTest(elemTypeMask);

    ScanRange range = new ScanRange(
        (long)(99439.621 * uorPerMas),
        (long)(79738.341 * uorPerMas),
        0,
        (long)(99701.215 * uorPerMas),
        (long)(79946.173 * uorPerMas),
        0);
    sc.SetRangeTest(range);

    string result = "The result of scan is:\n";
    ScanDelegate scanDelegate = (Element elem, DgnModelRef modelRef) =>
    {
        result += "ElementId = " + elem.ElementId
            + ", element type = " + elem.TypeName + "\n";
        return StatusInt.Success;
    };

    sc.Scan(scanDelegate);
    MessageBox.Show(result);
}
```

## Fence Basics

`DgnModelRef` can refer to an active model or attachment. Fence operations commonly use `Session.Instance.GetActiveDgnModelRef()` and `Session.GetActiveViewport()`.

```csharp
public static void CreateFenceByPointsAndQuery(string unparsed)
{
    DgnModelRef dgnModelRef = Session.Instance.GetActiveDgnModelRef();
    Viewport view = Session.GetActiveViewport();
    double uorPerMas = Session.Instance.GetActiveDgnModel().GetModelInfo().UorPerMaster;

    DPoint3d[] points =
    {
        new DPoint3d(-10 * uorPerMas, 0, -130 * uorPerMas),
        new DPoint3d(50 * uorPerMas, 0, -130 * uorPerMas),
        new DPoint3d(50 * uorPerMas, 0, 130 * uorPerMas),
        new DPoint3d(-10 * uorPerMas, 0, 130 * uorPerMas)
    };

    if (StatusInt.Success == FenceManager.DefineByPoints(points, view))
    {
        FenceParameters fenceParams = new FenceParameters(dgnModelRef, DTransform3d.Identity);
        FenceManager.InitFromActiveFence(fenceParams, true, false, FenceClipMode.None);

        ElementAgenda agenda = new ElementAgenda();
        DgnModelRef[] refs = { dgnModelRef };
        FenceManager.BuildAgenda(fenceParams, agenda, refs, false, false, false);

        string result = "Result:\n";
        for (uint i = 0; i < agenda.GetCount(); i++)
        {
            result += "ElementId = " + agenda.GetEntry(i).ElementId + "\n";
        }
        result += "Total count: " + agenda.GetCount();
        MessageBox.Show(result);
    }
}
```

For clipping, initialize with a clipping mode and pass inside/outside agendas to `FenceManager.ClipElement`.

```csharp
ElementAgenda insideElems = new ElementAgenda();
ElementAgenda outsideElems = new ElementAgenda();
FenceManager.ClipElement(fenceParams, insideElems, outsideElems, element, FenceClipFlags.Optimized);
```

For stretching, use:

```csharp
StatusInt status = FenceManager.StretchElement(
    fenceParams,
    element,
    DTransform3d.FromTranslation(new DPoint3d(-50 * uorPerMas, 0, 0)),
    FenceStretchFlags.None);
```

Search `references/course-code-snippets.md` for `CreateFenceByElement`, `FenceClipMode.Copy`, `FenceClipMode.Original`, `ClipElement`, and `StretchElement` for full course examples.
