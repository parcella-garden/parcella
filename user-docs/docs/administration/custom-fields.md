# Custom fields

Custom fields let you record things Parcella has no field for: a
member's occupation, or for a parcel whether it has a summer house --
and if so, its area and the year it was built. You set the fields up
once; after that they appear on the member and parcel forms like any
other field.

!!! info "Who can use this"
    Setting fields up: administrators only. Open
    **Administration → Custom fields**. Filling them in: everyone who
    may edit members and parcels.

## The page

At the top you choose the area: **Members** or **Parcels**. Each has its
own fields.

The card **Fields** lists them in the order they appear on the forms.
Fields inside a group are indented under it (↳).

| Column / button | What it shows or does |
|---|---|
| **Label** | The field's name, as it appears on the form. A red * means **Required**; **Archived** marks a field you've archived. The help text is shown below it. |
| **Type** | The kind of field, with the unit or the choices. |
| **Key** | The field's fixed name in exports and the API. It's created from the first label and stays when you rename the field. |
| Arrows | Move the field up or down. A field in a group moves within its group. |
| Pencil | Edit the field. |
| **Archive** / **Restore** | See [Archiving a field](#archiving-a-field). |

## Field types

| Type | On the form | Example |
|---|---|---|
| **Text** | One line of text | Occupation |
| **Long text** | Several lines | Notes on the hedge |
| **Number** | A number, with an optional unit such as m² or cm | Area of the summer house |
| **Date** | A date | Year the summer house was built |
| **Yes/no** | A checkbox | Has a rain barrel |
| **Choice** | A dropdown with the choices you give | Type of pool: frame, inflatable |
| **Group (yes/no with sub-fields)** | A checkbox; the fields inside it appear once it's ticked | Pool → diameter, height, removed in winter |

Numbers are kept with two decimal places.

## Adding a field or group

Use the card **New field or group**:

| Field | What it does |
|---|---|
| **Label** | Required. |
| **Type** | See [Field types](#field-types). |
| **In group** | Only shown once a group exists. Puts the field inside that group. A group can't be inside another group. |
| **Unit** | Numbers only, e.g. m². Shown next to the field and the value. |
| **Choices** | Choice fields only: one choice per line. |
| **Help text** | A short hint shown below the field on the form. |
| **Required** | The form can't be saved without a value. Inside a group the field is only required while the group is ticked. Yes/no fields and groups can't be required. |
| **Add** | Creates the field. It appears at the end of its area or group. |

### Example: a pool

1. Choose **Parcels**, enter the label "Pool", type **Group**, and **Add**.
2. Add "Diameter", type **Number**, unit "cm", **In group** "Pool".
3. Add "Height" the same way.
4. Add "Removed in winter", type **Yes/no**, in group "Pool".

On a parcel's edit form there is now a checkbox **Pool**; once you tick
it, the three fields below it appear.

## Editing a field

The pencil opens **Edit field**. You can change the label, the unit,
the choices, the help text and **Required** at any time. The **type**
can only be changed while nobody has entered a value yet; a group
always stays a group.

!!! warning "Removing a choice"
    If you remove a choice that some members or parcels have, their value
    stays as it is, but it can't be picked again on the form.

## Archiving a field

Fields are never deleted. **Archive** hides a field from the forms, the
detail pages, the list filter and the exports. The values entered so
far are kept. **Restore** brings the field back with its values.
Archiving a group hides the fields inside it too; a field inside an
archived group can only be restored after the group.

## Where custom fields show up

- **Edit form** of a member or parcel: the card **Further details**.
  See [Members](../modules/members.md) and
  [Parcels](../modules/parcels.md).
- **Detail page**: the card **Further details**, with the fields that
  have a value. A group only appears when it's ticked.
- **List filter**: the dropdown **– custom field –** on the member and
  parcel lists.
- **CSV export and import**: one column per field.
- **REST API**: for developers, see the API documentation.

Unticking a group on the form clears the fields inside it: no pool, no
pool measurements.

## Related

- [Members](../modules/members.md)
- [Parcels](../modules/parcels.md)
- [Roles, groups and permissions](../getting-started/roles-and-permissions.md)
