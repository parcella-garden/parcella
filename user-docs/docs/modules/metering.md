# Water and electricity

Many clubs buy water and electricity through one main connection and
pass it on to the parcels through sub-meters. This chapter covers both
the **Water** and the **Electricity** module. They keep track of your
meters, collect the yearly meter readings, work out each parcel's
consumption, and show whether the parcels' meters add up to what the
main meter says. The yearly price per unit you enter here is used when
invoices bill consumption.

The two modules work exactly the same way. Only these things differ:

| | Water | Electricity |
|---|---|---|
| Menu | **Water** | **Electricity** |
| Unit | m³ | kWh |
| Readings are entered with | one decimal place (e.g. 145,0) | whole numbers (e.g. 950) |
| Module switch | **Water management** | **Electricity management** |
| Group permission | **Water** | **Electricity** |

Water and electricity data are completely separate: a parcel can have a
water metering point and an electricity metering point, and each has its
own meters, readings, prices and permissions. The screenshots below show
the water module. In the electricity module everything is in the same
place, with kWh instead of m³.

!!! info "Who can use this"
    Both modules are switched on by default. Turn off the one your club
    doesn't manage under **Administration → Settings** (**Water
    management**, **Electricity management**) -- see
    [Turning modules on and off](../administration/modules.md). The data
    stays and reappears when you switch the module on again.

    Admin and Board users can do everything. Other users need a
    [group](../administration/groups.md) with **Water** or
    **Electricity** permissions: *read* to see the pages and download
    CSV files, *write* to create metering points, record readings,
    exchange meters, import and set prices, *delete* to delete metering
    points, readings and prices.

In the side menu, each module has the entries **Overview**, **Metering
Points**, **Readings**, **Evaluation** and **Configuration**.

## Metering points and meters

Two words are used throughout:

- A **metering point** is a place where consumption is measured. It is
  one of three types:
    - **Main meter** -- the utility's handover point, where the club
      receives water or power,
    - **Parcel** -- the connection of one parcel,
    - **Club** -- a club-owned connection, such as the clubhouse or a
      wash station.
- A **meter** is the physical device at a metering point, with its own
  number. When a meter is replaced, the metering point stays and gets a
  new meter; the old one is kept in the history.

## How readings and consumption work

These rules apply everywhere readings are entered -- on the readings
page, on a metering point's page, and in the CSV import.

- **One reading per meter per year.** Each reading belongs to a year
  (the billing year) and has a date. If you record a reading for a year
  that already has one, the old value, date and note are **replaced**.
  That is also how you correct a mistake.
- **Consumption** of a year = that year's reading minus the last reading
  of an earlier year. If there is no earlier reading, the meter's
  **Initial reading** is used. Without a reading for the year, there is
  no consumption ("no reading" or "–").
- **The year is not taken from the date.** A reading taken in January
  may still belong to last year's cycle. You always choose the year
  yourself.

### Plausibility warnings

A meter normally only counts up. Parcella warns you -- but **still saves
the reading** -- when:

- the reading is **lower than the previous reading** of the same meter
  (the last earlier year, or the initial reading), or
- the reading is **higher than an already recorded later reading** of
  the same meter.

Right after saving you see a yellow banner, for example **Reading saved,
but please check it: The meter reading (110.0) is lower than the
previous reading (120.5) of the same meter. Was an earlier reading
estimated? Please check.** The warning stays visible next to the
reading on the metering point's page and on the readings page until the
values fit together.

!!! tip "Why it only warns"
    If last year's reading was estimated too high, this year's real
    reading is lower. Blocking it would make it impossible to enter the
    real value. Record the real reading, then correct the estimated one.

A second check compares totals: if the parcels and club connections
together used **more** than the main meter for a year, a red banner on
the overview and the evaluation says so. That is a hint, not an error:
while readings are still being collected the numbers are often
incomplete.

### Meter exchange

When a meter is replaced -- for example because its calibration has
expired -- use **Exchange meter** on the [metering point's
page](#metering-point-page). The old meter is not deleted: it is marked
as removed and listed under **Former meters** with its last reading. The
new meter starts with its own **Initial reading**, so old and new
readings are never mixed up.

!!! warning "Record the old meter's final reading first"
    After the exchange, readings can only be recorded for the new meter.
    Enter the old meter's final reading (for the current year) **before**
    you exchange it.

<!-- TODO(verify): the Evaluation page and the metering point's readings table only use the current meter, while the Overview tiles add up all meters of a point (old ones included). In the year of an exchange, the old meter's final consumption therefore appears on the Overview but not on the Evaluation. Confirm which one invoicing follows and whether this difference is intended. -->

**Exchange** is for a real swap. If you only mistyped the meter number
or a date, use **Edit meter** instead -- it corrects the current meter
without creating a new one.

### Factor

Some meters show only part of what really flows through them. A large
electricity meter behind current transformers might count 1/20 of the
energy, so its display has to be multiplied by 20. For such a metering
point, set the **Factor** (usually 1):

- Readings are still entered exactly as the display shows them; the
  plausibility check works with those values.
- Consumption in this module is multiplied by the factor (rounded to two
  decimal places if the factor isn't 1). The factor belongs to the
  metering point, so it survives a meter exchange, and changing it
  applies to all years.
- Points with a factor other than 1 show a badge such as **×20**.

!!! warning "The factor is not used on invoices"
    Invoices bill the plain difference between the readings, without the
    factor.

### Switching a metering point off

If a connection has no supply for a while -- water turned off, a
parcel's power disconnected -- **switch it off** instead of deleting it.
A switched-off point:

- no longer appears on the readings page, in the readings CSV export,
  or in the "still have no reading" count -- **unless it already has a
  reading for that year**, so a final reading stays visible and
  editable,
- is greyed out with a **Switched off** badge in the list,
- keeps all its meters and readings.

Nothing special is needed for billing: without a reading for the year
there is no consumption, so nothing is billed. Switching it on again
brings it back.

## Overview

![Water overview](../assets/screenshots/water/overview.png)

The start page of the module, titled **Water** (or **Electricity**) and
the year. Come here to see whether all readings for a year are in and
whether the numbers add up.

![Electricity overview](../assets/screenshots/electricity/overview.png)

| Field / button | What it does |
|---|---|
| Year selector | Switches the year. Lists every year that has readings, plus the current year. |
| **Record reading** | Opens the [readings page](#readings) for this year. |
| Red banner | The parcels and club connections together used more than the main meter in this year. |
| Blue banner | **... metering point(s) still have no reading for ...**, with **Record now →**. Counts active points with a meter and no reading for the year. |
| **Main meter** tile | Consumption of the main meter(s), and how many there are. **Show** lists them. |
| **Parcels** tile | Total consumption of all parcel metering points, and how many there are. **Show** lists them. |
| **Club connections** tile | The same for club connections. |
| **Difference** tile | Main meter minus parcels and club (**Main - distributed**): the water or power that went unaccounted for, e.g. through leaks or meters running slow. Red when negative. |
| **Missing metering points** tile | How many parcels have no metering point for this medium. **Show** lists them. Terminated parcels count too -- they still need tracking until the next tenant moves in. |
| **All metering points** | Opens the [list](#metering-points). |
| **New metering point** | Opens the [form](#new-metering-point). Needs write permission. |
| **Annual report** | Opens the [Evaluation](#evaluation) for this year. |

## Metering Points

![Metering points](../assets/screenshots/water/metering-points.png)

All metering points of this medium: main meters first, then parcels by
plot number, then club connections by label.

| Field / button | What it does |
|---|---|
| **Back** | Returns to the overview. |
| **CSV Import** | Opens a dialog to upload a CSV file (see [Importing metering points](#importing-metering-points)). Needs write permission. |
| **CSV Export** | Downloads all metering points (see below). |
| **New metering point** | Opens the [form](#new-metering-point). Needs write permission. |
| **All** / **Active** / **Switched off** | Shows all points, only active ones or only switched-off ones. |
| Filter banner | When you came from an overview tile, a grey banner names the filter (e.g. **Parcel**). **Clear filter** shows everything again. |

| Column | What it shows / does |
|---|---|
| **Type** | **Main meter**, **Parcel** or **Club**. |
| **Metering point** | "Parcel" plus plot number, or the label. Links to the [metering point's page](#metering-point-page). |
| **Meter no.** | The current meter's number, with a **×** badge if a factor is set; **no active meter** if there is none. |
| **Status** | **active**, **Switched off** (hover to see since when), or **no meter**. |
| **Calibrated until** | The year the current meter's calibration runs out. A warning triangle means **Calibration expired** -- the year has been reached. |
| Eye button | Opens the metering point's page. |
| Bin | Deletes the metering point after the warning **Really delete this metering point? All its meters and readings will be deleted too.** Needs delete permission. |

The number of metering points is shown below the table.

!!! warning "Deleting removes the whole history"
    Deleting a metering point also deletes all its meters and readings,
    so past consumption disappears too. If the connection is only out of
    use, [switch it off](#switching-a-metering-point-off) instead.

### Missing metering points

![Parcels without a metering point](../assets/screenshots/water/metering-points-missing.png)

Opened with **Show** on the **Missing metering points** tile. Instead of
the table, the page lists every parcel without a metering point for this
medium -- terminated parcels are marked **(terminated)**. **Add metering
point** opens the [form](#new-metering-point) with that parcel already
chosen (write permission). If nothing is missing, it says **Every
parcel has a metering point.**

### CSV Export (metering points)

A semicolon-separated file with one row per metering point and its
current meter: Type, Parcel number, Label, Meter number, Installed on,
Calibrated until, Initial reading, Active, Inactive since, Factor. It
has the same format the import expects, so you can export, edit in a
spreadsheet and import new points again.

## Importing metering points

Useful for setting up the module for the first time. Click **CSV
Import** on the metering points list, choose a `.csv` file and click
**Import**. The columns don't need special names -- you match them up on
the next page. Semicolons and commas are both recognised, and files from
older Excel versions (not UTF-8) work too.

### Map CSV columns

There's no screenshot of this page, because it only appears after you
upload a file.

The page shows each column of your file with its first five rows. Above
each column, choose which field it belongs to, or **— Ignore —**.
Parcella guesses the mapping from the column headings, in English or
German (for example "Zählernummer" becomes **Meter number**).

| Field | What it means |
|---|---|
| **Type** | `MAIN_METER`, `PARCEL` or `CLUB`. If you don't map a Type column at all, every row is treated as a parcel -- typical for a plain list of parcel meters. |
| **Parcel number** | For parcel rows: the plot number of an existing parcel. |
| **Label** | The name of a main meter or club connection. |
| **Meter number** | The meter's number. |
| **Installed on** | Date as 2026-09-18 or 18.09.2026. |
| **Calibrated until** | A year, for example 2032. |
| **Initial reading** | The meter's reading when it was installed; empty = 0. |
| **Factor** | Empty = 1. |
| **Import** | Creates the metering points. At least one column must be mapped. |

What happens:

- Only **new** metering points are created; existing ones are never
  changed. A parcel row is skipped if the parcel already has a metering
  point, and a main meter or club row if one with the same label exists
  -- so importing the same file twice does no harm. Rows for main meters
  or club connections without a label can't be checked and are always
  created.
- Rows are skipped if the type is invalid, the parcel number doesn't
  exist, or the factor is invalid.
- New points start out active.

Afterwards the list shows a summary such as **12 imported, 2 skipped**,
with the reasons for the first three skipped rows.

<!-- TODO(verify): the hint on the mapping page says "Type is required.", but the import works without a Type column (all rows become parcel points). The on-screen hint may need updating. -->

## New metering point

![New metering point](../assets/screenshots/water/metering-point-form.png)

Opened from the overview, the list, or **Add metering point** for a
parcel without one. Needs write permission. The first card describes
the metering point, the second its meter.

| Field | What it does |
|---|---|
| **Type** | **Parcel**, **Club-owned connection point** or **Main meter (utility handover point)**. |
| **Parcel** | Shown for parcel points. Lists active and terminated parcels. |
| **Label** | Shown for club and main meter points, for example "clubhouse". |
| **Notes** | Anything worth knowing, e.g. where the meter is. |
| **Number** | Required. The meter's number. The same number may appear more than once -- Parcella doesn't check for duplicates. |
| **Calibrated until (year)** | The year the calibration runs out, e.g. 2032. |
| **Installed on** | Pre-filled with today. |
| **Initial reading** | The meter's reading when installed; the first year's consumption is calculated from it. Default 0. |
| **Factor** | Multiplier from the display to the real consumption, usually 1 (see [Factor](#factor)). Must be greater than 0, at most 100,000, with at most four decimal places. |
| **Cancel** / **Create metering point** | Saving opens the new metering point's page. |

!!! tip
    **Parcel** and **Label** are marked as required, but the form
    doesn't stop you if you leave them empty. Always fill them in,
    otherwise readings for this point can't be matched in a CSV import
    and the point is hard to find in lists.

## Metering point page

![Metering point page](../assets/screenshots/water/metering-point-detail.png)

Everything about one metering point: its details, its current meter,
the readings and former meters.

| Button (top) | What it does |
|---|---|
| **Previous** / **Next** | Go to the previous or next metering point in the list order. Also with Ctrl+← and Ctrl+→. |
| **Back** | Returns to the list. |

### Metering point

Shows **Type**, **Status** (**active** or **Switched off** with **since**
date), **Parcel** (linked), **Factor** if not 1, and **Notes**.

With write permission you can change:

| Field / button | What it does |
|---|---|
| **Label** | Optional for parcel points (e.g. "East entrance"); the name of club and main meter points. |
| **Notes** | Free text. |
| **Factor** | See [Factor](#factor). Changes consumption for all years, past ones included. Invalid values are refused with an explanation. |
| **Save** | Saves these three fields. |
| **Switch off as of** + **Switch off** | Switches the point off from the chosen date (default today). See [Switching a metering point off](#switching-a-metering-point-off). |
| **Switch on again** | Shown for switched-off points. |

### Current meter

Shows **Number**, **Installed on**, **Calibrated until** (with a
**Calibration expired** badge once that year is reached) and **Initial
reading**. If there is none: **No active meter for this metering
point.**

With write permission there are two buttons:

**Edit meter** -- corrects the current meter in place, for typing
mistakes:

| Field | What it does |
|---|---|
| **Number** | Required. |
| **Installed on**, **Calibrated until**, **Initial reading** | Change the stored values. Changing the initial reading changes the consumption of the meter's first year. |
| **Save** | Saves without creating a new meter. |

**Exchange meter** -- records a physical meter swap (see
[Meter exchange](#meter-exchange)):

| Field | What it does |
|---|---|
| **Old meter removed on** | Required, default today. |
| **New meter installed on** | Required, default today. |
| **New number** | Required. |
| **Calibrated until** | The new meter's calibration year. |
| **Initial reading** | The new meter's reading when installed, default 0. |
| **Exchange** | After the confirmation **Really exchange the meter? The old meter will be deactivated.** the old meter moves to **Former meters**. |

### Readings

The current meter's readings, newest year first.

| Column | What it shows / does |
|---|---|
| **Year** | The billing year. |
| **Date** | The reading date. |
| **Reading (m³)** | The value as shown on the meter, with a yellow plausibility warning if it doesn't fit. |
| **Consumption (m³)** | Consumption in that year, multiplied by the factor (shown as a badge in the heading). |
| **Note** | Your note. |
| Bin | Deletes the reading after a confirmation. Needs delete permission. |

**Recording a reading** (write permission), below the table:

| Field | What it does |
|---|---|
| **Year** | Required, default the current year. |
| **Date** | Required, default today. |
| **Meter reading (m³)** | Required. A comma or a point as decimal separator both work. |
| **Note** | Optional, e.g. "estimated". |
| **Record reading** | Saves the reading. If the year already has one, it is replaced. A text that isn't a number is refused with **Invalid meter reading**. |

### Former meters

Replaced meters, most recently removed first, with **Number**,
**Installed**, **Removed** and **Last reading**.

## Readings

![Readings](../assets/screenshots/water/readings.png)

The page for collecting the yearly readings, built to work on a phone
while you walk round the grounds. Open it with **Readings** in the menu
or **Record reading** on the overview. The title shows the medium and
the year, e.g. **Water reading 2026**.

| Field / button | What it does |
|---|---|
| Year selector | The year you are recording for: next year, this year, or one of the three years before. |
| **CSV Import** | Upload readings from a file (see [Importing readings](#importing-readings)). Needs write permission. |
| **CSV Export** | Downloads this year's list (see below). |
| **Back** | Returns to the overview. |

The page lists every metering point that needs a reading this year, in
three groups: **Main meter**, **Parcels** (by plot number) and **Club
connections**. Switched-off points only appear if they already have a
reading for the year. Each row shows:

- the metering point's name and meter number,
- **Previous year**: the last reading before this year, or the initial
  reading -- the new value should not be lower,
- if a reading is already in: the value with **recorded**, and any
  plausibility warning,
- otherwise, with write permission, an input field and a check button.
  Type the value and press the button; the date is set to today.
  Without write permission: **Not yet recorded**.

!!! tip "Correcting a recorded value"
    Once recorded, a value can't be changed on this page. Open the
    metering point's page and record the reading for the same year
    again -- it replaces the old one.

### CSV Export (readings)

A semicolon-separated file for the selected year with one row per
metering point that needs a reading: Type, Parcel number, Label, Meter
number, Year, Date, Reading, Note. Date and reading are empty where
nothing is recorded yet -- handy as a form for the person reading the
meters, which you can fill in and import again.

## Importing readings

Click **CSV Import** on the readings page, choose a file and click
**Import**. One file can contain readings for several years.

### Map CSV columns

There's no screenshot of this page, because it only appears after you
upload a file.

As with metering points, choose for each column which field it belongs
to, or **— Ignore —**.

| Field | What it means |
|---|---|
| **Type** | `MAIN_METER`, `PARCEL` or `CLUB`. If not mapped, every row counts as a parcel. |
| **Parcel number** / **Label** | Find the metering point: plot number for parcels, label for main meters and club connections. |
| **Meter number** | Optional cross-check: if it doesn't match the point's **current** meter, the row is skipped, because the reading might belong to a meter that has since been replaced. |
| **Year** | The billing year of the row. |
| **Date** | Required. 2026-09-18 or 18.09.2026. |
| **Reading** | Required. |
| **Note** | Optional. |
| **Default year (optional)** | Used for any row where Year isn't mapped or is left blank. A row's own Year always takes priority. Parcella never guesses the year from the date. |
| **Import** | Records the readings. At least one column must be mapped. |

What happens:

- Readings are only added to **existing** metering points; the import
  never creates one.
- A reading for a year that already has one replaces it.
- Rows are skipped if the metering point isn't found, it has no active
  meter, the meter number doesn't match, or year, date or reading are
  missing or invalid.
- Implausible readings are recorded anyway, the same as when entered by
  hand.

Afterwards the readings page shows a summary such as **40 readings
recorded, 2 skipped (metering point not found)** with the first few
reasons, and -- if needed -- a yellow banner **... reading(s) recorded
with a plausibility warning** naming the affected rows.

## Evaluation

![Evaluation](../assets/screenshots/water/evaluation.png)

The yearly consumption report, titled e.g. **Water report 2026**. Open
it with **Evaluation** in the menu or **Annual report** on the overview.

| Field / button | What it does |
|---|---|
| Year selector | Lists every year with readings, plus the current year. |
| **CSV Export** | Downloads the report (see below). |
| **Back** | Returns to the overview. |
| Red banner | **Distributed consumption ... exceeds main meter consumption ...** -- see [Plausibility warnings](#plausibility-warnings). |

Three tiles show the **Main meter**, **Parcels total** and **Club
total**. Below are three tables -- **Main meter**, **Parcels** and
**Club connections** -- each with **Metering point** (linked), **Meter
no.** and **Consumption (m³)**, or *no reading* where the year's reading
is missing. Consumption includes the factor.

The CSV export (semicolons) still has German column headings: Typ
(type), Zählpunkt (metering point), the meter number, Zählerstand
(reading) and Verbrauch (consumption).

## Price configuration

![Price configuration](../assets/screenshots/water/configuration.png)

The price per m³ or kWh for each year. Invoice runs use it for the
**Water usage (from module)** and **Electricity usage (from module)**
items: consumption × the price of the run's year. If no price is set for
that year, those items bill nothing. Each year keeps its own price, so
past invoice runs stay correct when the price changes. Open
**Configuration** in the menu.

### New/update price

Needs write permission.

| Field | What it does |
|---|---|
| **Year** | Required, pre-filled with the current year. |
| **Price per m³** (or **per kWh**) | Required, e.g. 2.50. Stored to two decimal places. |
| **Note** | E.g. "utility provider rate change". |
| **Save** | Saves the price. If the year already has one, it is **overwritten**. |

### Price history

All years, newest first, with **Year**, **Price** (per unit) and
**Note**. The pencil opens [Edit price](#edit-price) (write permission);
the bin deletes the year's price after a confirmation (delete
permission).

## Edit price

There's no screenshot of this page, because the sample data contains no
prices.

Opened with the pencil in the price history. Fields: **Year**, **Price
per m³** (or **per kWh**) and **Note**, with **Cancel** and **Save**.
If you change the year to one that already has a price, Parcella refuses
with **A different price configuration already exists for ...**.

<!-- TODO(verify): confirm that already-created invoices keep their amounts when a year's price is changed afterwards. -->

## Related

- [Collecting meter readings](../guides/meter-readings.md) -- the yearly
  routine step by step
- [Invoice runs](finances/invoice-runs.md) and
  [Running the annual invoices](../guides/annual-invoicing.md) -- billing
  consumption
- [Parcels](parcels.md) -- the parcels metering points belong to
- [Importing members and parcels](../guides/csv-import.md) -- the same
  kind of column mapping for other imports
- [Reporting](reporting.md)
