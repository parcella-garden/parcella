# Collecting meter readings

Once a year someone walks the grounds and reads every water and
electricity meter: the club's main meter, one meter per parcel, and the
club's own connections (clubhouse, wash area). This guide covers
entering those readings -- on a phone while you walk, or afterwards
from a list -- plus replacing a meter and checking the results.

Water and electricity work exactly the same way; each has its own menu.
The steps below say **Water**; for electricity use the **Electricity**
menu instead.

!!! info "Who can do this"
    Entering readings needs **write** permission on **Water** (or
    **Electricity**); deleting a reading needs **delete**. Both modules
    are on by default. A club can give the meter team a group with
    exactly these rights -- see [Groups](../administration/groups.md).

## How Parcella counts consumption

- Each **[metering point](../glossary.md#metering-point)** (a parcel's
  connection, the main meter, a club connection) has one **meter**
  installed at a time.
- A meter has **one reading per year**. The year's consumption is that
  reading minus the previous year's reading -- or minus the meter's
  **Initial reading** if it's the first one.
- Entering a reading for a year that already has one **replaces** it.
- Readings are entered exactly as the display shows them. Some
  electricity meters show only a fraction of the real value; their
  metering point then has a **Factor** (e.g. 20) that the evaluation
  multiplies in.

## 1. Before the round: check the list of metering points

1. Open **Water → Overview**. The tiles show how many main meters,
   parcel and club connections exist, and **Missing metering points**:
   parcels without a water connection in Parcella.
2. Click **Show** under **Missing metering points** to see those
   parcels; each links to **New metering point** with the parcel
   already selected. Add the ones that really have a meter.
3. A connection without supply for a while (water shut off on a vacant
   parcel)? Open its metering point, set **Switch off as of** and click
   **Switch off**. It drops out of the reading list until you **Switch
   on again**.

If your meter list is still in a spreadsheet, import it -- see
[Importing members and parcels](csv-import.md#4-metering-points).

## 2. Option A: enter readings on your phone while you walk

1. Open **Water → Readings** on your phone. The page shows the current
   year; pick another one in the year drop-down at the top if needed.
2. The page lists **Main meter**, **Parcels** (sorted by plot number)
   and **Club connections**. Each row shows the meter number and the
   **Previous year** reading as a check.
3. Type the reading into the row's field and tap the save button next
   to it. The row then shows the value as **recorded**.
4. Continue with the next meter. Rows without a value say **Not yet
   recorded**.

Readings entered here get today's date. To use a different date or add
a note, enter the reading on the metering point's page instead (option
C).

## 3. Option B: collect on paper or in a spreadsheet, then import

1. Open **Water → Readings**, choose the year, and click **CSV Export**.
   You get a file with one row per meter: **Type**, **Parcel number**,
   **Label**, **Meter number**, **Year**, and empty **Date**,
   **Reading** and **Note** columns.
2. Print it or fill it in on a tablet. Fill **Date** and **Reading**
   for every meter you read.
3. Back on **Water → Readings**, click **CSV Import**, choose the file
   and click **Import**.
4. On **Map CSV columns**, check the mapping. If your file has no year
   column, enter it in **Default year (optional)**. Click **Import**.
5. Read the summary on the readings page: how many readings were
   recorded, and how many rows were skipped and why.

Rows without a reading are skipped as "invalid row" -- that's expected
for meters you haven't read yet. Details on columns and error messages:
[Importing members and parcels](csv-import.md#5-meter-readings).

## 4. Option C: enter a single reading with date and note

1. Open **Water → Metering Points** and click the metering point.
2. At the bottom, under **Readings**, fill in **Year**, **Date**,
   **Meter reading** and optionally a **Note**.
3. Click **Record reading**.

The **Readings** table on the same page lists every year with its
reading and consumption. A wrong reading can be deleted there.

## 5. When a reading looks wrong

A reading lower than the previous year's (or higher than an already
recorded later one) is **saved anyway**, with a warning like *"Reading
saved, but please check it: The meter reading (…) is lower than the
previous reading (…) of the same meter. Was an earlier reading
estimated? Please check."* The reading keeps a warning marker on the
readings page and the metering point.

Common causes: a typo, a misread digit, an earlier reading that was
estimated too high, or a meter that was actually replaced (step 6).
Correct the value by recording the reading again for the same year.

## 6. A meter is replaced { #a-meter-is-replaced }

When a meter is physically swapped -- for example because its
calibration runs out:

1. Read the old meter one last time, if you still can, and enter it on
   the metering point's page as the year's reading (option C).
2. In the **Current Water meter** card (**Current Electricity meter**
   for electricity), open **Exchange meter**.
3. Enter **Old meter removed on**, **New meter installed on**, the **New
   number**, **Calibrated until** (a year) and the new meter's
   **Initial reading** (usually what its display shows when installed).
4. Click **Exchange** and confirm.

The old meter is not deleted: it moves to **Former meters** with its
installation and removal dates and its **Last reading**. From now on,
readings go to the new meter, whose consumption starts from its
**Initial reading**.

!!! warning "Consumption in the year of the swap"
    Readings can only be entered for the meter that's currently
    installed, and the annual invoice uses the current meter's
    consumption. What the old meter counted in the year of the swap is
    shown under **Former meters** but is **not** added to that year's
    invoice. Check such parcels by hand and add the old meter's share
    to the invoice separately if your club bills it.
    <!-- TODO(verify): confirm that neither the invoice nor the evaluation adds the old meter's partial-year consumption, and what the recommended way to bill it is. -->

!!! tip "Typo, not a new meter?"
    If you only mistyped the meter number or initial reading, use **Edit
    meter** instead. **Exchange meter** is for a real swap.

## 7. Check the year

1. Open **Water → Evaluation** and choose the year.
2. The tiles compare **Main meter** with **Parcels total** and **Club
   total**; the tables below list every metering point with its
   **Consumption**. Points still missing a reading show **no reading**.
3. If the parcels and club connections together used more than the main
   meter, Parcella shows a warning. That's normal while readings are
   still being entered; once all are in, it points to a misread meter.
4. **CSV Export** downloads the evaluation for your own records or the
   utility company.

**Water → Overview** also tells you how many metering points are still
missing a reading for the year, with a **Record now →** link.

## 8. Set the price for billing

If you bill water and electricity with Parcella's annual invoices:

1. Open **Water → Configuration**.
2. Under **New/update price**, enter the **Year** and the **Price per
   m³** and optionally a **Note** (e.g. "utility provider rate change").
3. Click **Save**.

Without a price for the year, the invoice run bills no water for that
year. Then continue with [Running the annual
invoices](annual-invoicing.md).

## Related

- [Water and electricity](../modules/metering.md)
- [Importing members and parcels](csv-import.md)
- [Running the annual invoices](annual-invoicing.md)
- [Handing over a parcel](parcel-handover.md)
- Glossary: [metering point](../glossary.md#metering-point),
  [meter](../glossary.md#meter)
