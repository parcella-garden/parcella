# Glossary

Club terms and Parcella terms, in alphabetical order. Where the German
term is what most clubs actually say, it's given in brackets.

Chapters link straight to an entry, for example
`glossary.md#deposit`.

## Active, terminated, communal, deleted { #parcel-status }

The four statuses of a [parcel](#parcel):

- **active** -- a normal parcel, usually leased to someone.
- **terminated** -- the tenant has given [notice](#notice-of-termination)
  and the parcel is on its way to a new tenant. Only terminated parcels
  can be handed over to an [applicant](#applicant).
- **communal** -- club land tracked as a parcel (paths, playground),
  never leased out. It doesn't count towards the leased area.
- **deleted** -- no longer in use, but kept with its history.

## Applicant (Bewerber) { #applicant }

Someone who applied for a garden and is on the
[waiting list](#waiting-list). Applicants are kept apart from
[members](#member): they only become members when they actually get a
parcel. See [Applicants](modules/applicants.md).

## Area A, B and C { #areas }

The club's total area split into three parts, set under
**Administration → Settings → Areas (sqm)**:

- **Area A (parcels, sqm)** -- the sum of all parcel areas, worked out
  by Parcella.
- **Area B (communal, sqm)** -- paths, green spaces and other shared
  club land: the total minus A and C, worked out by Parcella.
- **Area C (municipal, sqm)** -- land the club manages but that belongs
  to the municipality, entered by hand.

Area B is what the [communal area share](#communal-area-share) and
[public burdens](#public-burdens) are based on.

## Board (Vorstand) { #board }

The elected board of the association. In Parcella, board members
usually have full access to every module. You list the current board
under **Administration → Settings → Board members**; their access comes
from a [group](#group) with **Full access to every module** (or, for
older accounts, the **Board** role).

## Calibration (Eichung) { #calibration }

Water and electricity meters may only be used for billing until their
calibration expires. Parcella stores the year as **Calibrated until**
and marks expired meters with **Calibration expired**. The usual fix is
to [replace the meter](guides/meter-readings.md#a-meter-is-replaced).

## Club role (Vereinsamt) { #club-role }

An office in the club -- chairperson, treasurer, water officer -- that a
member holds for a year. A club role can make its holder
[exempt](#exemption) from [mandatory hours](#mandatory-hours). Set up
under **Work Sessions → Sessions & Overview → Club Roles**. Not to be
confused with a [role](#role) in Parcella.

## Communal area share { #communal-area-share }

An invoice item that bills the lease of the shared club land
([Area B](#areas)), split evenly over the parcels it applies to. In the
app: **Share of the communal area lease**.

## Deposit (Kaution) { #deposit }

A sum the new tenant pays when taking over a parcel, which the club
holds and pays back -- or keeps a part of -- when the tenant leaves.
Parcella has no separate deposit feature: note the amount and date in
the handover [process](#process) and record the money in **Finances**.
See [Handing over a parcel](guides/parcel-handover.md#7-deposit-and-money).

## Dunning (Mahnung) { #dunning }

Reminding a member of an unpaid invoice. In Parcella: **Send reminder**
on an overdue invoice creates **Reminder #1**, **#2** and so on, with an
optional fee. There are no fixed dunning levels; the board decides when
to send the next one. See
[Invoices, payments and reminders](modules/finances/invoices.md).

## Exemption (Befreiung) { #exemption }

A member who doesn't have to do [mandatory hours](#mandatory-hours) in
a given year -- usually because of a [club role](#club-role), health or
age. If one tenant of a parcel is exempt, the whole parcel is exempt,
and an exemption always counts for the whole calendar year.

## External contact { #external-contact }

A supplier, craftsman, authority or other organisation the club deals
with -- a company and/or a contact person. Not a member. See
[External contacts](modules/external-contacts.md).

## Factor { #factor }

A multiplier on a [metering point](#metering-point) for meters that
show only a fraction of the real value (for example 20 for an
electricity meter with current transformers). Readings are entered as
displayed; the evaluation multiplies by the factor. Usually 1.

## Former, current and upcoming tenant { #former-tenant }

A [tenancy](#tenancy) is **current** while it runs, **upcoming** if it
starts on a future date (after a handover with a future date), and
**former** once it has ended. Former tenants stay on the parcel's page
under **Former tenants**; only current (and upcoming) tenants can be the
[invoice address](#invoice-address).

## General levy (Umlage) { #general-levy }

A one-off amount the club has to raise from all parcels together -- a
legal bill, a repair, an increase in an insurance premium -- shared
equally. In the app: **General levy (split evenly across all
parcels)**. You enter the *total* amount as the unit price; Parcella
divides it by the number of parcels billed and puts each share on the
parcel's invoice.

## Group { #group }

A set of [permissions](#permission) in Parcella -- read, write or delete
per [module](#module), or full access -- that you give to user
accounts. New users get their access only through groups. See
[Groups](administration/groups.md).

## Handover (Übergabe) { #handover }

The change from an old to a new tenant on a parcel. In Parcella,
**Assign a parcel** on an application ends the old
[tenancy](#tenancy), makes the applicant a member and tenant, and sets
the parcel active again. See
[Handing over a parcel](guides/parcel-handover.md).

## Hours transfer { #hours-transfer }

A member who did more [mandatory hours](#mandatory-hours) than required
gives some of the surplus to another member for the same year. See
**Work Sessions → Hours transfers**.

## Inspection (Begehung) { #inspection }

The walk-through of a parcel by the board when a tenant leaves, to note
defects before the [valuation](#valuation). Tracked in a handover
[process](#process).

## Invoice address { #invoice-address }

The tenant of a parcel whose address the parcel's invoices go to --
**Use as invoice address** on the tenancy. Several tenants of one
parcel can have it; the parcel still gets one invoice. A parcel without
one gets no invoice.

## Invoice run { #invoice-run }

One batch of invoices, usually the annual invoices for a year. You add
line items, check a preview, then **finalize** it -- which assigns the
permanent invoice numbers -- and send it. See
[Running the annual invoices](guides/annual-invoicing.md).

## Item catalog { #item-catalog }

Your list of reusable invoice line items (lease, water, insurance, ...),
picked into each year's [invoice run](#invoice-run). Found under
**Finances → Overview → Item catalog**.

## Main meter (Hauptzähler) { #main-meter }

The meter where the club takes over water or electricity from the
utility company. Its consumption should roughly equal the sum of all
parcel and club meters; Parcella warns if the parcels together used
more.

## Mandatory hours (Pflichtstunden) { #mandatory-hours }

The hours of community work (Gemeinschaftsarbeit) a parcel or member
owes the club each year, as decided by the general meeting. Hours not
worked are paid for at an hourly rate. Parcella counts attended
[work sessions](#work-session), [sponsorships](#sponsorship) and
[hours transfers](#hours-transfer) against them, and the shortfall can
be billed in the annual [invoice run](#invoice-run). See
[Work hours](modules/work-hours.md).

## Member (Mitglied) { #member }

A person who belongs to the association. Usually also a
[tenant](#tenant), but not necessarily (supporting or honorary
members). A member counts as active until their **Member until** date.

## Meter (Zähler) { #meter }

The physical water or electricity meter, with its number, calibration
year and initial reading. A [metering point](#metering-point) has one
meter at a time; when it is replaced, the old one is kept as a former
meter.

## Metering point (Zählpunkt) { #metering-point }

A place where water or electricity is measured: a parcel's connection,
the [main meter](#main-meter), or a club connection (clubhouse, wash
area). The metering point stays; the [meter](#meter) installed there
can change.

## Module { #module }

A feature area of Parcella -- Work hours, Water, Finances, Processes,
and so on -- that can be switched on or off for your club under
**Administration → Settings → Feature areas**. Switching one off hides
it; its data stays. See [Turning modules on and off](administration/modules.md).

## Notice of termination (Kündigung) { #notice-of-termination }

The tenant's (or the club's) notice that a lease ends. In Parcella you
set the parcel's status to **terminated**; the date is logged
automatically.

## Parcel (Parzelle, Garten) { #parcel }

One garden plot, identified by its **Plot number**. Called "Plot" in a
few places in the app.

## Permission { #permission }

What a user may do in a [module](#module): **Read** (look), **Write**
(add and change) or **Delete**. Everyone who can log in may look up
members and parcels. See
[Roles, groups and permissions](getting-started/roles-and-permissions.md).

## Print bundle { #print-bundle }

One PDF with every invoice of a run whose recipient can't be reached by
email, ready to print and post.

## Process { #process }

A step-by-step checklist you design yourself -- for example a parcel
handover or onboarding a member -- run for one parcel, member or
applicant. Each stage has fields to fill in; required fields must be
filled before moving on. See [Processes](modules/processes.md).

## Public burdens (Öffentliche Lasten) { #public-burdens }

Charges the landowner passes on to the club -- property tax, street
cleaning and similar municipal fees -- usually per square metre. The
club passes them on to the parcels, including a share for the communal
land. In the app: **Public burdens (own area + communal area share)**:
the parcel's own area plus its equal share of [Area B](#areas), times
the rate you enter.

## Purchase request { #purchase-request }

A request to spend club money, which needs
[two-person approval](#two-person-approval) before the purchase. See
[Purchase requests](modules/purchase-requests.md).

## Reading (Zählerstand) { #reading }

The value on a meter's display. Parcella keeps one reading per
[meter](#meter) and year; the year's consumption is this reading minus
the previous one.

## Role { #role }

Older accounts have a fixed role (**Administrator**, **Board**,
**Treasurer**, **Read-only**). New accounts get their access from
[groups](#group) instead. Not the same as a [club role](#club-role).

## Sample data { #sample-data }

Made-up members, parcels and other records you can add to a fresh
installation to try Parcella out, and remove again with one click.
See [Sample data](administration/sample-data.md).

## Sponsorship (Patenschaft) { #sponsorship }

A member looks after an area of the club grounds -- a hedge, the
playground -- for the year and gets a fixed number of
[mandatory hours](#mandatory-hours) credited for it. See
**Work Sessions → Sponsorships**.

## Tag { #tag }

A free label on a member, such as "hedge team" or "water responsible",
to find and filter people. Tags also exist for external contacts.

## Tenancy (Pacht) { #tenancy }

The lease of a parcel by a member, from a start date to an optional end
date. Ending a tenancy keeps it as history; several members can share
one parcel. See also [former tenant](#former-tenant).

## Tenant (Pächter) { #tenant }

A member who holds a [tenancy](#tenancy) on a parcel.

## Treasurer (Kassierer) { #treasurer }

The board member responsible for the club's money. In Parcella, give
the treasurer a [group](#group) with full rights on **Finances**.

## Two-person approval (Vier-Augen-Prinzip) { #two-person-approval }

A [purchase request](#purchase-request) is only approved once two
different board members have approved it -- and neither may be the
person who asked for it. A single board member can reject it.

## Valuation (Wertgutachten) { #valuation }

An expert's assessment of what the garden house, plants and fixtures on
a parcel are worth when the tenant leaves. Parcella doesn't calculate
it; you store the report in the handover [process](#process).

## Waiting list (Warteliste) { #waiting-list }

The [applicants](#applicant) waiting for a parcel, in the order they
applied. In Parcella: **Applicants** with the **Open** filter.

## Work session (Arbeitseinsatz) { #work-session }

A date on which members do community work for the club, credited
towards their [mandatory hours](#mandatory-hours). **Standard** sessions
are planned and can be published on the club website; **Special**
sessions are spontaneous and internal. See
[Organising a work session](guides/work-session.md).
