# EC and ItemType

Use this reference for engineering properties. Prefer ItemType for simpler user-facing property workflows; use EC schema/instances when the task needs explicit ECSchema/ECClass/ECRelationship control.

## Concepts

- `ECSchema`: schema definition, like a database schema.
- `ECClass`: class/table definition.
- `ECProperty`: property/column definition.
- `ECInstance`: instance/row.
- `ECPropertyValue`: value/cell.
- `ItemTypeLibrary`: MicroStation user-facing library of ItemTypes.
- `ItemType`: simplified EC-backed property set.
- `CustomItemHost`: host wrapper for applying/removing ItemTypes on elements.

## ECSchema Shape

The course uses ECXML such as:

```xml
<ECSchema schemaName="ComplexSchema" nameSpacePrefix="ComplexSchema" version="1.0" xmlns="http://www.bentley.com/schemas/Bentley.ECXML.2.0">
  <ECClass typeName="Contact" isStruct="True" isDomainClass="False">
    <ECProperty propertyName="Name" typeName="string" />
    <ECProperty propertyName="Age" typeName="int" />
    <ECArrayProperty propertyName="PhoneNumber" typeName="string" />
  </ECClass>
  <ECClass typeName="ComplexClass" isDomainClass="True">
    <ECProperty propertyName="IntProperty" typeName="int" />
    <ECProperty propertyName="StringProperty" typeName="string" />
    <ECProperty propertyName="DoubleProperty" typeName="double" />
    <ECProperty propertyName="DateTimeProperty" typeName="dateTime" />
    <ECProperty propertyName="BooleanProperty" typeName="boolean" />
    <ECProperty propertyName="APoint2d" typeName="point2d" />
    <ECProperty propertyName="APoint3d" typeName="point3d" />
    <ECArrayProperty propertyName="SimpleArrayProperty" typeName="string" />
  </ECClass>
</ECSchema>
```

For complete EC schema import and EC instance examples, search `course-code-snippets.md` for `ImportSchemaOptions`, `DgnECManager.Manager.ImportSchema`, `CreateInstanceOnElement`, `CreateInstanceOnModel`, and `ECRelationship`.

## Create ItemType

```csharp
public static void CreateItemType(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        itemTypeLibrary = ItemTypeLibrary.Create(itemLibName, dgnFile);
    }

    itemTypeLibrary.AddItemType(itemTypeName);
    ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);

    CustomProperty intProperty = itemType.AddProperty("IntProperty");
    intProperty.Type = CustomProperty.TypeKind.Integer;

    CustomProperty strProperty = itemType.AddProperty("StrProperty");
    strProperty.Type = CustomProperty.TypeKind.String;
    strProperty.DefaultValue = "test string";

    bool result = itemTypeLibrary.Write();
    if (result)
    {
        MessageBox.Show("Input ItemType Success");
    }
}
```

## Delete ItemType or Library

```csharp
public static void DeleteItemType(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        MessageBox.Show("Can't find itemType library!");
        return;
    }

    ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
    bool result = itemTypeLibrary.RemoveItemType(itemType);
    if (result)
    {
        MessageBox.Show("Remove ItemType Success");
    }

    itemTypeLibrary.Write();
}
```

```csharp
public static void DeleteItemTypeLib(string unparsed)
{
    string itemLibName = "testLib";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        MessageBox.Show("Can't find itemType library!");
        return;
    }

    SchemaDeleteStatus status = itemTypeLibrary.Delete();
    MessageBox.Show("ItemTypeLib remove status:\n" + status);
}
```

## Attach ItemType to Element

Use `CustomItemHost` to apply an ItemType. Call `ScheduleChanges(element)` before writing/replacing the element.

```csharp
public static void AttachItemTypeToElem(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();

    DPoint3d topCenter = new DPoint3d(0, 0, 100000);
    DPoint3d bottomCenter = DPoint3d.Zero;
    ConeElement cone = new ConeElement(
        dgnModel,
        null,
        50000,
        100000,
        topCenter,
        bottomCenter,
        DMatrix3d.Identity,
        true);

    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        MessageBox.Show("Can't find ItemType Library");
        return;
    }

    ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
    CustomItemHost host = new CustomItemHost(cone, true);
    IDgnECInstance item = host.ApplyCustomItem(itemType, true);

    item.SetValue("IntProperty", 123);
    item.SetValue("StrProperty", "CCCC");

    EditParameterDefinitions defs = EditParameterDefinitions.GetForModel(dgnModel);
    DgnECInstanceEnabler enabler = DgnECManager.Manager.ObtainInstanceEnabler(dgnFile, itemType.ECClass);
    if (enabler != null && enabler.SupportsCreateInstanceOnElement)
    {
        defs.SetDomainParameters(enabler.SharedWipInstance);
    }

    item.ScheduleChanges(cone);
    cone.AddToModel();
}
```

## Read ItemType on Element

Use the property internal name when reading via `GetPropertyValue`.

```csharp
public static void ReadItemTypeOnElem(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();

    foreach (Element elem in dgnModel.GetGraphicElements())
    {
        CustomItemHost host = new CustomItemHost(elem, true);
        IDgnECInstance item = host.GetCustomItem(itemLibName, itemTypeName);
        if (item == null)
        {
            continue;
        }

        ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
        ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
        CustomProperty property = itemType.GetPropertyByName("StrProperty");
        string internalName = property.InternalName;

        IECPropertyValue val = item.GetPropertyValue(internalName);
        MessageBox.Show(val != null ? val.StringValue : "val == null");
    }
}
```

## Detach ItemType

```csharp
public static void DetachItemTypeOnElem(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();
    foreach (Element elem in dgnModel.GetGraphicElements())
    {
        Element newElem = elem;
        CustomItemHost host = new CustomItemHost(newElem, true);
        IDgnECInstance item = host.GetCustomItem(itemLibName, itemTypeName);
        if (item == null)
        {
            continue;
        }

        item.ScheduleDelete(newElem);
        newElem.ReplaceInModel(elem);
    }
}
```

## Change ItemType Value

```csharp
public static void ChangeItemTypeValueOnElem(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    DgnModel dgnModel = Session.Instance.GetActiveDgnModel();

    foreach (Element elem in dgnModel.GetGraphicElements())
    {
        Element newElem = elem;
        CustomItemHost host = new CustomItemHost(elem, true);
        IDgnECInstance item = host.GetCustomItem(itemLibName, itemTypeName);
        if (item == null)
        {
            continue;
        }

        ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
        ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
        CustomProperty property = itemType.GetPropertyByName("StrProperty");
        string internalName = property.InternalName;

        IECPropertyValue val = item.GetPropertyValue(internalName);
        val.StringValue = "Changed string";

        item.ScheduleChanges(elem);
        newElem.ReplaceInModel(elem);
    }
}
```

## Add or Remove ItemType Property

```csharp
public static void AddItemTypeProperty(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        MessageBox.Show("Find item type lib failure, please check");
        return;
    }

    ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
    if (itemType == null)
    {
        MessageBox.Show("Find item type failure, please check");
        return;
    }

    CustomProperty doubleProperty = itemType.AddProperty("DoubleProperty");
    doubleProperty.Type = CustomProperty.TypeKind.Double;
    doubleProperty.DefaultValue = 0.01;

    bool result = itemTypeLibrary.Write();
    if (result)
    {
        MessageBox.Show("Add ItemType Property Success");
    }
}
```

```csharp
public static void RemoveItemTypeProperty(string unparsed)
{
    string itemLibName = "testLib";
    string itemTypeName = "testItemTypeName";
    string propertyName = "StrProperty";

    DgnFile dgnFile = Session.Instance.GetActiveDgnFile();
    ItemTypeLibrary itemTypeLibrary = ItemTypeLibrary.FindByName(itemLibName, dgnFile);
    if (itemTypeLibrary == null)
    {
        MessageBox.Show("Find item type lib failure, please check");
        return;
    }

    ItemType itemType = itemTypeLibrary.GetItemTypeByName(itemTypeName);
    if (itemType == null)
    {
        MessageBox.Show("Find item type failure, please check");
        return;
    }

    CustomProperty property = itemType.GetPropertyByName(propertyName);
    if (property == null)
    {
        MessageBox.Show("Find item type property failure, please check");
        return;
    }

    itemType.RemoveProperty(property);
    bool result = itemTypeLibrary.Write();
    if (result)
    {
        MessageBox.Show("Remove ItemType Property Success");
    }
}
```

## Selection Set to EC Instance

The WinForms EC assignment example attaches an imported EC class to each selected element:

```csharp
IECClass ecClass = m_ecschema.GetClass(m_treeView_ECClass.SelectedNode.Text);
DgnECInstanceEnabler instanceEnabler = DgnECManager.Manager.ObtainInstanceEnabler(m_dgnFile, ecClass);

ElementAgenda agenda = new ElementAgenda();
SelectionSetManager.BuildAgenda(ref agenda);
for (uint i = 0; i < agenda.GetCount(); i++)
{
    IDgnECInstance instance = instanceEnabler.CreateInstanceOnElement(
        agenda.GetEntry(i),
        instanceEnabler.SharedWipInstance,
        false);

    instance.SetString("PropertyName", "PropertyValue");
    instance.ScheduleChanges(agenda.GetEntry(i));
}
```

Adapt property names and value types to the target `ECClass`; do not assume every property is a string.
