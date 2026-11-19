# Groups

Groups decide what each person may see and change. You create a group
for a job in your club -- "Board", "Treasurer", "Water team" -- tick
what that job needs, and put the right people in it.

!!! info "Who can use this"
    Administrators only. Open **Administration → Groups**.

The ideas behind groups -- Read, Write and Delete, full access, the
administration area -- are explained in
[Roles, groups and permissions](../getting-started/roles-and-permissions.md).
This page describes the screen.

![Groups](../assets/screenshots/administration/groups.png)

## Create group

| Field / button | What it does |
|---|---|
| **Name** | Required, and must be unique (**A group with this name already exists**). |
| **Description** | Optional note on what the group is for. |
| **Full access to every module** | Members of the group may read, change and delete everything in every switched-on module, like the board. |
| **Can access the administration panel** | Members of the group may also open **Administration**. Ticking this includes full access, so the full-access box disappears. |
| **Create group** | Creates the group. You see **Group created**. |

A new group without either box ticked grants nothing yet. Open it below
to tick its permissions.

## The group cards

Every group appears as a card below the form, folded shut. The heading
shows its name and a badge **Administration** or **Full access** if it
grants one of those. Click the heading to unfold the card.

The **bin** button in the heading deletes the group after you confirm.
Its members lose whatever the group gave them. Parcella refuses to
delete the last group that gives anybody access to the administration
area, if no other account has it.

### Settings and permissions

| Field / button | What it does |
|---|---|
| **Name**, **Description** | As when creating. |
| **Full access to every module**, **Can access the administration panel** | As when creating. When either is ticked, the permission table is hidden because it isn't needed. |
| Permission table | One row per **Module** with the checkboxes **Read**, **Write** and **Delete**. See the table of modules below. |
| **Save** | Saves name, description, the two boxes and the whole table. You see **Group updated**. |

The modules in the table: **Members & Parcels**, **Work Sessions**,
**Water**, **Electricity**, **Insurance**, **Purchase Requests**,
**Calendar**, **Inventory**, **Finances**, **Support (helpdesk)**,
**Applicants**, **External contacts**, **Reporting**, **Notes**,
**Processes**. Modules your club has switched off are still listed;
their ticks take effect when the module is switched on.

!!! tip "Read comes first"
    Tick **Read** wherever you tick **Write** or **Delete**. Without
    Read the module doesn't even appear in the person's sidebar.

The task board and announcements are not in the table: they are only
ever available with full access.

### Assigned Users

Lists the accounts in the group, with avatar, name and e-mail address.

| Element | What it does |
|---|---|
| **×** next to a person | Takes them out of the group immediately (**User removed**). |
| **Add user...** + **Add** | Pick an account and add it (**User added**). |

The **Add user...** list only offers accounts that get their access
from groups. Older accounts with the **Administrator** or **Board**
role already have full access and aren't offered here; if you want to
switch them over to groups, add them from their
[Edit user](users.md#edit-user) page. When all eligible accounts are
already in the group you see a short note instead of the list; when
there are none at all, a link **Invite one**.

Changes to permissions take effect on the person's next click -- they
don't need to log in again.

## Example set-up

| Group | Ticked |
|---|---|
| Administrators | **Can access the administration panel** |
| Board | **Full access to every module** |
| Treasurer | Finances: Read, Write, Delete. Members & Parcels: Read, Write. Purchase Requests: Read. Insurance: Read. |
| Meter readers | Water: Read, Write. Electricity: Read, Write. |
| Work-session team | Work Sessions: Read, Write. Calendar: Read. |

A person can be in several groups; their permissions add up.

## Related

- [Users and invitations](users.md)
- [Roles, groups and permissions](../getting-started/roles-and-permissions.md)
- [Turning modules on and off](modules.md)
