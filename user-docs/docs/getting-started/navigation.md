# Finding your way around

Every page in Parcella has the same frame: a green **sidebar** on the
left with the navigation, and a white **top bar** above the page with
the page title and the buttons for that page.

!!! info "Who can use this"
    Everyone who is signed in. Which entries *you* see depends on the
    modules your club has switched on and on your permissions -- see
    [Why entries appear and disappear](#why-entries-appear-and-disappear).

![Sidebar and top bar](../assets/screenshots/getting-started/navigation.png)

## The sidebar

From top to bottom the sidebar holds:

1. **Your club's name and logo**, with the word **Management** below.
2. **The navigation entries** -- one per module.
3. **Administration** -- only for administrators, always at the very
   bottom of the list.
4. **The footer** with your own account.

### Single entries and groups

Smaller modules are a single link, for example **Members**,
**Parcels**, **Inventory** or **Notes**. Click it and the module opens.

Bigger modules are a **group**: a heading in capital letters with a
small arrow. Clicking the heading unfolds its pages:

| Group | Pages inside |
|---|---|
| **Work Sessions** | **Sessions & Overview**, **Annual Evaluation**, **Sponsorships**, **Hours transfers**, **Tasks** |
| **Water** | **Overview**, **Metering Points**, **Readings**, **Evaluation**, **Configuration** |
| **Electricity** | **Overview**, **Metering Points**, **Readings**, **Evaluation**, **Configuration** |
| **Insurance** | **Overview**, **Parcels**, **Configuration**, **Evaluation** |
| **Calendar** | **Community Calendar**, **Birthdays**, **Council Presence**, **Council Absence**, **My calendars** |
| **Finances** | **Overview**, **Outgoing Invoices**, **Reminders**, **Incoming Invoices** |
| **Administration** | **System**, **Users**, **Groups**, **API tokens**, **Settings**, **Integrations**, **Email log**, **Sample data**, **API Documentation (Swagger)** |

Only **one group is open at a time**: opening a group folds the
previously open one away, so the sidebar stays short. The group that
contains the page you are on always opens by itself. Otherwise your
browser remembers which group you opened last.

The page you are on is highlighted with a light bar on its left edge.

**API Documentation (Swagger)** opens the technical description of
Parcella's programming interface in a new browser tab. It is meant for
people connecting other software and can be ignored otherwise.

### Badges: things that need attention

Some entries show a small red number. It tells you how many things are
waiting there. Hover over it to see what it counts.

| Entry | The badge counts |
|---|---|
| **Work Sessions** and **Sessions & Overview** | New sign-ups for upcoming work sessions from the last 14 days that nobody has marked as reviewed yet. |
| **Purchase Requests** | Requests still waiting for a decision. |
| **Applicants** | New applications nobody has looked at yet. |
| **Support** | Open conversations (active or pending) in the club's helpdesk. |
| **Task Board** | Tasks whose due date has passed and which aren't done. |

A badge disappears on its own once the matter is dealt with -- for
example when the purchase request is approved or rejected, or the task
is done. There is no "mark as read". The same numbers appear as tiles
on the [Dashboard](dashboard.md).

### The footer: your account

At the bottom of the sidebar you see your avatar and name, and below
it the groups you belong to (or **Administrator** / **Board** for older
accounts that have a role instead of groups -- see
[Roles, groups and permissions](roles-and-permissions.md)).

| Button | What it does |
|---|---|
| **Change password** | Opens your profile: password, avatar and API tokens. See [First login and your account](first-login.md#change-password). |
| **Log Out** | Signs you out and returns to the sign-in page. |

## The top bar

The top bar shows the title of the current page on the left. On the
right are the actions for this page, such as **New member**, an
export, or a back button. The top bar stays visible when you scroll
down a long list.

## Why entries appear and disappear

An entry is only shown when **both** of these are true:

1. **The module is switched on** for your club. Administrators switch
   modules on and off under
   [Turning modules on and off](../administration/modules.md). A
   switched-off module disappears for everybody -- its data is kept
   and comes back when the module is switched on again.
2. **You are allowed to read it.** Board members and administrators
   see every switched-on module. Everybody else sees **Members** and
   **Parcels** plus the modules one of their groups grants **Read**
   for. See [Roles, groups and permissions](roles-and-permissions.md).

A few entries follow their own rule:

- **Task Board** and **Announcements** are only shown to people with
  full access (board members, administrators, or a group with **Full
  access to every module**). Groups can't grant them separately.
- **Support**: with read permission for **Support (helpdesk)** you get
  Parcella's own list of conversations. Without it, the entry still
  appears if your club's helpdesk has a web address, and then opens the
  helpdesk itself in a new tab.
- **Administration** is only shown to administrators.

If you open a page you aren't allowed to see -- from a bookmark or a
link a colleague sent -- you get the message **You don't have
permission to do this**. A page of a switched-off module answers with a
"not found" page: "This feature is switched off for this club."

### The order of the entries

Your club decides the order of the entries. An administrator sets it
under [Club settings](../administration/settings.md#navigation-order).
The order is the same for everybody.

## Keyboard shortcut for detail pages

On detail pages that have **Previous** and **Next** buttons -- members,
parcels, metering points, a parcel's insurance page and external
contacts -- **Ctrl + ←** and **Ctrl + →** jump to the previous and next
record, the same as those buttons. The shortcut does nothing while you
are typing in a field.

!!! note "Mac users"
    On a Mac, Ctrl + arrow keys usually switch between desktops
    ("Spaces"), so the system catches the shortcut before Parcella sees
    it. Use the buttons on the page instead, or turn that system
    shortcut off.

## On a phone or small tablet

On narrow screens the sidebar is hidden to make room for the page.

- Tap the **☰** button at the top left of the top bar to slide the
  sidebar in.
- Tap an entry to go there; the sidebar closes by itself.
- To close it without going anywhere, tap the darkened page next to
  it, or press **Esc** on a keyboard.

Buttons and input fields are slightly larger on touch screens, and
rows of filter buttons wrap onto several lines instead of running off
the screen. Wide tables can be scrolled sideways with your finger.

## Related

- [Dashboard](dashboard.md)
- [Roles, groups and permissions](roles-and-permissions.md)
- [Turning modules on and off](../administration/modules.md)
