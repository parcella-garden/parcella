# Support

Parcella doesn't have its own ticket system. Your club answers e-mails
and contact-form requests in a helpdesk -- FreeScout, Zammad, Znuny /
OTRS, osTicket, Zendesk or Freshdesk -- and the support module connects
that helpdesk to Parcella: you see which conversation belongs to which
member and parcel, read the conversation, and turn it into a card on
the task board. Answers are always written in the helpdesk itself.

!!! info "Who can use this"
    - The module is switched on with **Support (helpdesk)** under
      [Turning modules on and off](../administration/modules.md). It is
      **off by default**, because it stores the helpdesk's access data.
      The helpdesk itself is chosen and connected by an administrator
      under [Integrations](../administration/integrations.md).
    - **Support conversations in Parcella:** board members and
      administrators, and users whose group grants **Read** for
      **Support (helpdesk)** (see [Groups](../administration/groups.md)).
      **Write** is needed to link a conversation to a member or parcel.
    - **Create task:** only board members and administrators (or users
      in a group with full access), just like the task board itself.
    - **Everyone else** still gets a **Support** link in the navigation
      once the module is on and the helpdesk has a web address: it
      opens the helpdesk directly in a new tab.

## Where conversations come from

Parcella checks the helpdesk for new and changed conversations about
every five minutes. It only stores a cross-reference -- subject,
customer, status, number of messages, and the links to member, parcel
and task. The messages themselves stay in the helpdesk and are fetched
fresh each time you open a conversation.

**Matching members:** when a conversation comes in, Parcella looks for
the member it belongs to:

1. If this helpdesk customer was already linked to a member before,
   that member is used.
2. Otherwise, if **exactly one** member has the customer's e-mail
   address, that member is linked automatically.
3. If several members share the address (e.g. a couple with one
   inbox), or nobody has it (a neighbour, a supplier), the conversation
   stays without a member. You can link one by hand.

If the linked member has exactly one current parcel, that parcel is
linked too. A conversation that has a member -- whether automatic or
set by you -- is never re-matched later.

When a member's name changes in Parcella, their customer record in the
helpdesk is renamed too, if the helpdesk supports it.

**Statuses:** every helpdesk names its states differently; Parcella
shows them as `active`, `pending`, `closed`, `spam` or `deleted`. Closed,
spam and deleted conversations are hidden from the list, the badge and
the dashboard. If a conversation is reopened in the helpdesk, it shows
up again with its member link intact.

### What each helpdesk supports

| Helpdesk | Conversation list and badge | Read conversations | Contact form creates conversation | Customer names kept in sync |
|---|---|---|---|---|
| FreeScout | yes | yes | yes | yes |
| Zammad | yes | yes | yes | yes |
| Znuny / OTRS | yes | yes | yes | no |
| osTicket | no | no | yes | no |
| Zendesk | yes | yes | yes | yes |
| Freshdesk | yes | yes | yes | yes |

With osTicket, Parcella can only pass on requests from the website's
contact form; you work with them in osTicket alone.

Only messages the customer can see are shown -- internal notes stay in
the helpdesk. Attachments aren't shown; open the conversation in the
helpdesk for those.

## Support Conversations

![Support Conversations](../assets/screenshots/support/list.png)

**Support** in the navigation opens the list of open conversations of
the active helpdesk, most recently updated first. The red badge next to
**Support** -- and the **Open support conversations** tile on the
[dashboard](../getting-started/dashboard.md) -- counts the same
conversations, whether or not they have a member.

| Field / button | What it does |
|---|---|
| **Open in {helpdesk}** | Opens the helpdesk in a new tab. Only shown if the helpdesk's web address is set. |
| **Subject** | The conversation's subject. Click anywhere in the row to open the conversation. |
| **Customer** | The sender's name, or their e-mail address. |
| **Member** | The linked member, or "—". |
| **Status** | `active` or `pending` (closed ones aren't listed). |
| **Messages** | Number of messages, as last reported by the helpdesk. |
| **Updated** | When the conversation last changed in the helpdesk. |
| **Task** | A board icon if the conversation is linked to a task. |

Instead of the list you may see:

- "No helpdesk is set up yet. …" -- an administrator still has to
  choose one under [Integrations](../administration/integrations.md).
- "{helpdesk} can't list conversations through its interface. …" --
  the helpdesk is osTicket.
- "No support conversations yet." -- nothing open right now.

## Conversation page

<!-- TODO(verify): no screenshot -- the list's rows open conversations by click, not by a link, so the screenshot tool can't follow one; without a connected helpdesk the transcript would only show an error anyway. -->

Shows one conversation, titled with its subject.

| Button | What it does |
|---|---|
| **Back** | Returns to the list. |
| **Open in {helpdesk}** | Opens this conversation in the helpdesk -- that's where you answer it. |

### Conversation

The messages, oldest first, each with author and time. If they can't
be loaded, a notice explains why -- the helpdesk can't be reached, it
can't show conversations (osTicket), or "This conversation's helpdesk
isn't set up (anymore)." when the club has switched to another
helpdesk since. "No messages could be loaded." means the helpdesk
returned none.

### Member

Shows the linked member (with a link to their page), or "No member
matched.".

With write permission, choose a member and click **Save**:

- Members with the customer's e-mail address are listed first, marked
  **suggested**. If several members share the address, a note asks
  you to pick the right one.
- Below them, all current members.
- **-- none --** removes the link.

Saving a member also resets the parcel: if the member has exactly one
current parcel, it is linked; otherwise none is.

### Parcel

Shown once a member is linked. With write permission, choose one of
the member's current parcels, or **-- none --**, and click **Save**.
<!-- TODO(verify): without write permission the Parcel card is empty -- the linked parcel isn't displayed at all for read-only users. -->

### Task board

| Field / button | What it does |
|---|---|
| **Open task** | Shown when the conversation is linked to a task; opens the task. |
| List + **Create task** | Creates a new card in the chosen list of the [task board](tasks.md) and links it to the conversation. The card's title is the subject; its description names the helpdesk, the conversation number and, if linked, the member. Board members and administrators only. |

If the task board has no lists yet, creating a task fails with "No
lists exist on the task board yet".
<!-- TODO(verify): there is a route to link an existing task to a conversation, but no form on the page uses it. -->

!!! note "Answering happens in the helpdesk"
    Parcella deliberately has no reply box. Click **Open in
    {helpdesk}** and answer there; the new message shows up in
    Parcella the next time you open the conversation.

## The website contact form

If your club's website has a contact form, it can create a
conversation in the helpdesk directly through Parcella. This is a
separate switch, **Public contact-form API**, also off by default.
Setup is described under [Integrations](../administration/integrations.md).

## Related

- [Integrations](../administration/integrations.md) -- choosing and
  connecting the helpdesk
- [Task board](tasks.md) -- following up on a conversation
- [Members](members.md) -- e-mail addresses used for matching
- [Dashboard](../getting-started/dashboard.md)
