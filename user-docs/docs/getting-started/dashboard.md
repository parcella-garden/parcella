# Dashboard

The dashboard is the start page you see after signing in. It gives you
the club's key figures at a glance and points you to things that need
attention. Click **Dashboard** at the top of the sidebar to come back
to it.

!!! info "Who can use this"
    Everybody who is signed in. Some tiles only appear when their
    module is switched on, and a few also need read permission for that
    module (noted below).

![Dashboard](../assets/screenshots/getting-started/dashboard.png)

All figures are worked out fresh each time you open the page.

## The tiles

The tiles at the top come in a fixed order. The first four are always
shown; the others appear depending on your club's modules.

| Tile | What it counts | When it appears | Button |
|---|---|---|---|
| **Members** | Big number: current members -- not deleted, membership not ended, and either started already or without a **member since** date. Below: **... active** -- the members among them who have a **member since** date. If at least one current member has a date of birth on file: **Average age ... years**, worked out from those members only. | Always | **Show** opens the member list filtered to active members. |
| **Active Parcels** | Parcels with the status *active*. Below, in orange: **... vacant** -- active parcels without a current or upcoming tenant (a parcel whose last tenancy has ended counts as vacant; one whose tenant has given notice, or whose new tenant starts later, does not); or **all occupied** if there are none. | Always | **Show All** opens the parcel list. |
| **Terminated** | Parcels with the status *terminated*. | Always | **Show** opens the parcel list filtered to terminated parcels. |
| **Total Area (sqm)** | The sum of the area of all parcels, active and terminated. Deleted parcels and common areas don't count. This is the same figure as **Area A** in the [club settings](../administration/settings.md#areas-sqm). | Always | -- |
| **Open Purchase Requests** | Requests still **awaiting approval**. | **Purchase requests** module on and you may read purchase requests | **Show All** |
| **New applications** | Applications with the status *new*, i.e. **not looked at yet**. | **Applicants** module on and you may read applicants | **Show All** opens the applicant list filtered to new ones. |
| **Open processes** | Processes **in progress**. | **Processes** module on and you may read processes | **Show All** opens the open processes. |
| **Open support conversations** | **Active or pending helpdesk conversations** in the club's helpdesk. | **Support (helpdesk)** module on and you may read it | **Show All** |
| **Overdue Tasks** | Tasks on the task board whose due date has passed and that aren't done. | **Task board** module on and you have full access (the task board is for full-access users only) | **Show All** opens the task board showing only overdue tasks. |
| **New Sign-ups** | Sign-ups **in work sessions** from the last 14 days, for regular sessions that haven't happened yet. Sign-ups for a session someone has marked as reviewed no longer count. | **Work-hours management** module on and you may read work hours | **Show All** opens **Sessions & Overview**. |

The numbers on **Open Purchase Requests**, **New applications**,
**Open support conversations**, **Overdue Tasks** and **New Sign-ups**
are the same as the red badges in the sidebar (see
[Finding your way around](navigation.md#badges-things-that-need-attention)).
Like the badges, they go down by themselves once something has been
dealt with.

## Birthdays This Week

This card appears only when at least one current member has a birthday
in the next seven days, today included. It lists those members, the
soonest first:

- the member's name, linking to their member page,
- **today, turning ...** for a birthday today, otherwise the date and
  **turning ...**,
- a highlighted **Milestone** badge for round birthdays (30, 40, 50, ...).

Members without a date of birth on file are not listed. The card is
shown even when the **Calendar** module is off; its **Show All** button
leads to the full birthday list in the calendar, which needs the
calendar module and permission.

## Recent Members

The five current members who were **entered into Parcella** most
recently, with their **member since** date on the right (– if none is
set). Click a name to open the member. **No members created yet.**
appears on a fresh installation.

**New Member** opens the form for a new member.

## Quick Access

Shortcuts for frequent jobs:

| Button | What it does |
|---|---|
| **Create New Member** | Opens the form for a new member. |
| **Create New Parcel** | Opens the form for a new parcel. |
| **Export Members as CSV** | Downloads the member list as a CSV file, e.g. for a spreadsheet. |
| **Export Parcels as CSV** | Downloads the parcel list as a CSV file. |

Creating members and parcels needs **Write** on **Members & Parcels**.
Without it, the form answers with **You don't have permission to do
this**.

## Related

- [Members](../modules/members.md) and [Parcels](../modules/parcels.md)
- [Finding your way around](navigation.md)
- [Turning modules on and off](../administration/modules.md)
