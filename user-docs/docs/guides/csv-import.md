# Importing members and parcels

If your club already keeps its member list, parcel list or meter list in
a spreadsheet, you don't have to type everything in again. Save the
spreadsheet as a CSV file, upload it, tell Parcella which column is
which, and import.

This works the same way for **parcels**, **members**, **metering
points**, **meter readings** and **external contacts**. This guide goes
through them in the order that makes sense for a new installation.

!!! info "Who can do this"
    Importing members and parcels needs **write** permission on
    **Members & Parcels**; metering points and readings need write on
    **Water** or **Electricity**; external contacts need write on
    **External contacts**. Board members and administrators have all of
    these.

!!! warning "Download a backup first"
    An import writes many records at once and there is no "undo". Open
    **Administration → Users** and click **Download backup** before you
    start. See [Backup and restore](../administration/backup.md).

## How every import works

All five imports have the same two steps.

1. **Upload.** On the list page, click **CSV Import** (for external
   contacts: **CSV import**), choose the file and click **Import**.
   Nothing is saved yet.
2. **Map CSV columns.** Parcella shows a table: one column per column
   of your file, with your header on top and the first five rows of
   data underneath. Above each column is a drop-down. Parcella has
   already guessed the matching field from the header (English and
   German headers both work, for example "Nachname" or "Last name").
   Check every drop-down, correct the wrong ones, and set columns you
   don't want to **— Ignore —**. Then click **Import**.

Afterwards you are back on the list page with a short summary: how many
rows were created, updated or skipped, and the reasons for the first
few skipped rows.

### What your file should look like

- **The first row holds the column headers.** Every row below it is one
  record. Headers don't need to match exactly -- you map them in step 2.
- **Semicolon or comma** between columns: Parcella detects which one
  your file uses.
- **Save it as UTF-8.** Most spreadsheet programs offer "CSV UTF-8" when
  you save. Umlauts and accents then come through correctly.
  <!-- TODO(verify): the upload step also reads older Windows/Latin-1 files, but the final import step appears to read UTF-8 only -- a Latin-1 file may fail after the mapping screen. Confirm and fix or keep this advice. -->
- **Dates** as `2026-03-15` or `15.03.2026` (also `15.03.26`).
- **Decimal numbers** with a comma or a point: `312,5` and `312.5` both
  work.
- **Several values in one cell** (email addresses, phone numbers, tags)
  are separated by a semicolon. Your spreadsheet program puts quotes
  around such a cell when it saves the file -- that's fine.

!!! tip "Start from an export"
    The easiest template is Parcella's own export. Every list with an
    import also has **CSV Export**. Export the (still empty or
    sample-filled) list, fill the file in your spreadsheet program, and
    import it again: the headers then match without any mapping work.

## 1. Parcels

Import parcels first. Members, metering points and readings refer to
parcels by their plot number.

1. Open **Parcels** and click **CSV Import**.
2. Choose your file and click **Import**.
3. On **Map CSV columns**, map at least **Plot number**. The other
   fields are optional.
4. Click **Import**. The summary reads like *"24 imported, 0 skipped"*.

| Field | What Parcella expects |
|---|---|
| **Plot number** | Required. Stored in capital letters ("g12" becomes "G12"). |
| **Area (sqm)** | A number, comma or point as decimal separator. Anything else is left empty. |
| **Latitude** / **Longitude** | Optional GPS position, decimal degrees (e.g. `51,339695`). |
| **Status** | `ACTIVE`, `TERMINATED`, `COMMUNAL` or `DELETED` (upper or lower case). Empty or anything else means active. |
| **Notes** | Free text. |

!!! warning "Existing parcels are skipped, not updated"
    If a plot number already exists in Parcella, that row is **skipped**
    and the existing parcel stays exactly as it is. To change existing
    parcels, edit them by hand. Rows without a plot number are ignored
    and counted separately in the summary.

The parcel import does **not** assign tenants. The parcel export has a
column with the tenants' names, but the import ignores it -- see step 3
below.

## 2. Members

1. Open **Members** and click **CSV Import**.
2. Choose your file and click **Import**.
3. On **Map CSV columns**, map at least **First name** and **Last
   name**. Without both, the import stops with *"Please map both the
   first name and last name columns before importing."*
4. Click **Import**. The summary reads like *"80 newly imported, 0
   updated"*.

| Field | What Parcella expects |
|---|---|
| **First name**, **Last name** | Required. A row with one of them empty is skipped. |
| **Street**, **Postal code**, **City** | Free text. |
| **Date of birth** | A date (see above). Also used to tell apart two members with the same name. |
| **IBAN** | Free text, not checked. |
| **Member since**, **Member until** | Dates. An empty **Member until** means an active member. |
| **Email notifications** | "No", "Nein", "false" or "0" means the member does **not** want club information by email. Anything else -- including an empty cell or an unmapped column -- means yes. |
| **Email addresses** | One or more, separated by semicolons. The first becomes the primary address. |
| **Phone numbers** | One or more, separated by semicolons. The first becomes the primary number. |
| **Notes** | Free text. |

**Matching existing members.** For each row, Parcella looks for an
existing member with the same first and last name -- and, if the row
has a date of birth, the same date of birth. If it finds one, it
**updates** that member instead of creating a second one.

!!! warning "An update overwrites every field"
    When a row matches an existing member, *all* of that member's fields
    above are replaced with what the row contains -- including blanks. A
    column you set to **— Ignore —**, or an empty cell, **clears** the
    stored value (address, IBAN, dates, notes), and **Email
    notifications** goes back to yes. Only email addresses and phone
    numbers are left alone on an update: they are added for new members
    only.

    So for updating existing members, always import a *complete* file --
    ideally a fresh **CSV Export** that you edited -- never a file with
    just one or two columns.

Tags, parcel assignments and the **Declines birthday presents** setting
are not part of the import. The export does contain **Parcels** and
**Tags** columns, but the import ignores them.

## 3. Assign members to their parcels

There is no import for tenancies. Assign them by hand once members and
parcels exist:

1. Open a parcel under **Parcels**.
2. In **Current tenants**, start typing the member's name in **Choose
   member…** and pick them from the list.
3. Optionally enter the date the tenancy started.
4. Leave **Use as invoice address** ticked for the tenant who should
   receive the parcel's invoices.
5. Click **Assign**.

With many parcels, the **Next** button at the top of the parcel page
takes you straight to the next one.

More: [Parcels](../modules/parcels.md).

## 4. Metering points

Metering points are the water and electricity connections (main meter,
one per parcel, club connections). Water and electricity are imported
separately, each in its own menu.

1. Open **Water → Metering Points** (or **Electricity → Metering
   Points**) and click **CSV Import**.
2. Choose your file and click **Import**.
3. Map the columns and click **Import**. At least one column must be
   mapped.

| Field | What Parcella expects |
|---|---|
| **Type** | `PARCEL`, `MAIN_METER` or `CLUB`. If you don't map this column at all, every row counts as a parcel connection. If you map it, a row with an empty or unknown type is skipped ("invalid type"). |
| **Parcel number** | Required for parcel connections; must match an existing plot number, otherwise the row is skipped ("parcel not found"). |
| **Label** | The name of a main meter or club connection, e.g. "Clubhouse". |
| **Meter number** | The number printed on the meter. |
| **Installed on** | A date. |
| **Calibrated until** | A **year** only, e.g. `2031`. |
| **Initial reading** | The reading when the meter was installed. Empty means 0. |
| **Factor** | Usually empty (= 1). For meters that show only a fraction of the real value, e.g. `20`. Must be greater than 0. |

The import only **creates** metering points. A parcel that already has a
metering point for this medium, or a main meter or club connection with
the same label, is skipped as "already exists" -- so importing the same
export twice does no harm. New metering points always start switched
on.

!!! warning
    Enter **Calibrated until** as a plain year. A full date in that
    column is not understood.
    <!-- TODO(verify): a non-numeric "Calibrated until" value looks like it aborts the whole import with an error page instead of skipping the row. -->

More: [Water and electricity](../modules/metering.md).

## 5. Meter readings

Readings are attached to metering points that already exist; the
import never creates a metering point.

1. Open **Water → Readings** (or **Electricity → Readings**) and click
   **CSV Import**.
2. Choose your file and click **Import**.
3. Map the columns. If your file has no year column, or some rows leave
   it empty, enter the year in **Default year (optional)**.
4. Click **Import**.

| Field | What Parcella expects |
|---|---|
| **Type** | As for metering points. Not mapped = every row is a parcel connection. |
| **Parcel number** / **Label** | Find the metering point, the same way as above. |
| **Meter number** | Optional cross-check. If it doesn't match the meter currently installed, the row is skipped ("meter number mismatch") -- it probably belongs to a meter that has since been exchanged. |
| **Year** | The year the reading belongs to. Wins over **Default year (optional)**. |
| **Date** | The day the meter was read. Required. |
| **Reading** | The value on the display. Required. |
| **Note** | Free text. |

Parcella never guesses the year from the date. A reading taken in
January can still belong to the previous year's billing, so you say
which year it is.

One file may contain several years. If a metering point already has a
reading for that year, the import **replaces** it.

A reading that looks implausible -- lower than the previous one, for
example -- is still saved. The summary then shows a separate warning
with the affected rows, so you can check them.

More: [Collecting meter readings](meter-readings.md).

## 6. External contacts

Suppliers, craftsmen and authorities, if you use the **External
contacts** module.

1. Open **External contacts** and click **CSV import**.
2. Choose your file and click **Import**.
3. On **Assign columns**, map the columns. No field is required;
   completely empty rows are skipped.
4. Click **Import**.

| Field | What Parcella expects |
|---|---|
| **Type (company/person)** | "Firma", "Company" or "Unternehmen" for a company; "Person" for a person. Without it, a row with a first or last name is a person, otherwise a company. |
| **Company name** | For a company: its name. For a person: the company they belong to -- created if it doesn't exist yet. |
| **First name**, **Last name**, **Position** | For persons. |
| **Street**, **Postal code**, **City**, **IBAN** | Address and bank details. For a person in a company, they fill the company's empty fields. |
| **Email addresses**, **Phone numbers**, **Tags** | Several values separated by semicolons. |
| **Notes** | Free text. |

A company that already exists (same name, ignoring upper and lower
case) or a person with the same name is **updated** from the row's
non-empty cells. Missing phone numbers, emails and tags are added.
Unlike the member import, nothing is ever cleared or removed.

More: [External contacts](../modules/external-contacts.md).

## Common problems

| What you see | Why, and what to do |
|---|---|
| *"That CSV file appears to be empty."* | The file has no rows at all. Check that you saved the right sheet. |
| All data ends up in one column on the mapping screen | Parcella couldn't tell the separator. Save the file again as "CSV (semicolon-separated)" or "CSV (comma-separated)". |
| Strange characters instead of umlauts | The file isn't UTF-8. Save it again as "CSV UTF-8". |
| Members skipped with "first or last name missing" | Those rows have an empty name cell, or the name column wasn't mapped. |
| A member appears twice | The two rows differ in spelling or date of birth, so Parcella treats them as different people. Delete the duplicate by hand. |
| Existing member's address suddenly empty | The member was updated from a row or a file without that column. See the warning in step 2; restore from your backup if needed. |
| Parcels "skipped" | The plot number already exists. Edit existing parcels by hand. |
| Metering points "parcel not found" | The plot number in the file doesn't exist in Parcella -- import the parcels first, and check the spelling ("G12" vs. "G 12"). |
| Readings "metering point not found" | Import or create the metering points first. If you mapped **Type**, check its value. |
| Readings "invalid row" | **Date** or **Reading** is empty or not understood, or there is no year (neither a **Year** column nor a **Default year (optional)**). |
| Readings "no active meter" | The metering point has no meter installed. Add one on the metering point's page. |
| Leading `'` in exported phone numbers | Parcella adds it to cells starting with `+`, `-`, `=` or `@` so spreadsheet programs don't treat them as formulas. Remove it before importing members, or leave it -- the external contacts import removes it for you. |

## Related

- [Members](../modules/members.md)
- [Parcels](../modules/parcels.md)
- [Water and electricity](../modules/metering.md)
- [External contacts](../modules/external-contacts.md)
- [Setting up a new club](new-club-setup.md)
- [Collecting meter readings](meter-readings.md)
