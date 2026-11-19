# Roles, groups and permissions

Not everybody who helps run the club needs to see everything. The
person who reads the water meters doesn't need the bank details, and
the treasurer doesn't need to plan work sessions. Parcella lets you
give each person exactly the access their job needs.

!!! info "Who can use this"
    This page explains access for everybody. Only **administrators**
    can change who has which access, under
    [Users and invitations](../administration/users.md) and
    [Groups](../administration/groups.md).

## The three levels of access

Every account falls into one of three levels.

| Level | Sees and changes | Opens the **Administration** area | How you get it |
|---|---|---|---|
| **Administrator** | Everything in every switched-on module | Yes | A group with **Can access the administration panel**, or the older **Administrator** role |
| **Full access** (typically the board) | Everything in every switched-on module | No | A group with **Full access to every module**, or the older **Board** role |
| **Limited** | What their groups allow, module by module; at least read access to members and parcels | No | Membership in one or more groups without those two boxes ticked |

The **Administration** area -- users, groups, club settings,
integrations, backups -- is deliberately separate from full access.
Being on the board doesn't automatically make someone the person who
looks after the installation, and vice versa. Administrators always
have full access to the modules as well.

## Groups

A **group** is a named set of permissions, for example "Water team",
"Treasurer" or "Board". Administrators create groups and put accounts
into them. A person can be in several groups.

A group grants either:

- **Full access to every module**, or
- **Can access the administration panel** (which includes full access),
  or
- **Read**, **Write** and **Delete** per module, ticked individually.

### What Read, Write and Delete mean

| Permission | Allows |
|---|---|
| **Read** | Open the module, see its lists and detail pages, and download its exports and reports. Without it, the module doesn't appear in the sidebar. |
| **Write** | Create new records and change existing ones -- add a meter reading, edit a member, record an invoice payment. |
| **Delete** | Remove records, where the module allows deleting at all. |

!!! tip "Tick Read too"
    Write and Delete are meant on top of Read. A person who can't read
    a module doesn't see it in the sidebar and can't open its pages,
    so Write alone is of no use. Each module chapter says which actions
    need which permission.

### The modules a group can grant

| Module in the group form | Covers |
|---|---|
| **Members & Parcels** | [Members](../modules/members.md) and [Parcels](../modules/parcels.md) |
| **Work Sessions** | [Work hours](../modules/work-hours.md) |
| **Water** | Water part of [Water and electricity](../modules/metering.md) |
| **Electricity** | Electricity part of [Water and electricity](../modules/metering.md) |
| **Insurance** | [Insurance](../modules/insurance.md) |
| **Purchase Requests** | [Purchase requests](../modules/purchase-requests.md) |
| **Calendar** | [Calendar](../modules/calendar.md) |
| **Inventory** | [Inventory](../modules/inventory.md) |
| **Finances** | [Finances](../modules/finances/index.md) |
| **Support (helpdesk)** | [Support](../modules/support.md) |
| **Applicants** | [Applicants](../modules/applicants.md) |
| **External contacts** | [External contacts](../modules/external-contacts.md) |
| **Reporting** | [Reporting](../modules/reporting.md) |
| **Notes** | [Notes](../modules/notes.md) |
| **Processes** | [Processes](../modules/processes.md) |

### Several groups: the most generous wins

If a person is in several groups, their permissions add up. For each
module and each level, one group granting it is enough. Example: group
"Water team" grants Water read + write, group "Calendar" grants
Calendar read. Someone in both may read and change water data and read
the calendar.

### Everybody can look up members and parcels

Every account, even one in no group at all, can **read** members and
parcels. Anybody helping to run the club needs to know who is who and
which parcel is whose. Changing them needs **Write** on **Members &
Parcels**.

## Things only full access can do

A few areas can't be granted per module. They are always reserved for
people with full access (board, administrators, or a group with **Full
access to every module**):

- the [Task board](../modules/tasks.md),
- [Announcements](../modules/announcements.md),
- approving or rejecting a [purchase request](../modules/purchase-requests.md)
  -- the two required approvals have to come from people with full
  access,
- creating and editing calendars under **My calendars** in the
  [Calendar](../modules/calendar.md),
- the cloud folder of a parcel (browse, upload, download) and
  downloading the attachment of an incoming invoice,
- creating a task from a support conversation or linking one to a task.

## The older roles: Administrator, Board, Treasurer, Read-only

Earlier versions of Parcella gave each account a fixed **role**.
Accounts created back then may still have one:

| Role | Effect today |
|---|---|
| **Administrator** | Full access plus the administration area, without needing a group. The very first account of a new installation has this role. |
| **Board** | Full access, without needing a group. |
| **Treasurer** | Nothing beyond the basic read access to members and parcels. Use a group to grant more. |
| **Read-only (view only)** | Same as Treasurer: basic access only, everything else comes from groups. |

New accounts get the inert **Read-only** role; their real access comes only from groups. An
administrator can switch an Administrator or Board account over to
groups with **Remove legacy role** (see
[Users and invitations](../administration/users.md)). Put the account
into the right group *first*, otherwise it drops to basic access.

The sidebar footer shows the groups you are in. Without a group it shows
**Administrator** or **Board** if you have that role, otherwise a dash.

## Safety net: the last administrator

Parcella refuses any change that would leave **no active account able
to open the administration area**. You get the message **Cannot remove
admin access from the last remaining Administrator/Board account** when
you try to deactivate, delete, demote or remove from its group the last
such account, or delete or untick the last group that grants it.
Without at least one administrator nobody could fix access problems
any more.

## The REST API and API tokens

Programs that talk to Parcella through its programming interface use
an [API token](../administration/api-tokens.md). A personal token acts
with the permissions of the account it belongs to.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Related

- [Groups](../administration/groups.md) -- creating groups and ticking permissions
- [Users and invitations](../administration/users.md) -- adding people to groups
- [Finding your way around](navigation.md#why-entries-appear-and-disappear)
