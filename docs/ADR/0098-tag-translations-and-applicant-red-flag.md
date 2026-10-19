# Tags: per-language names; applicants: a live red flag from a contact tag

**Context:** Two requests came together, both built on the free-form tags
(member tags, ADR 0093; external-contact tags, ADR 0096):

1. A tag is typed once in one language ("Rote Liste") but should read in
   the club's language ("red flag" in English). Tags are user data, so
   the translation files (`app/translations/*.json`, ADR 0020) can't hold
   them.
2. The board keeps people it doesn't want to rent to again as external
   contacts with such a tag. A new applicant who is one of them should
   stand out the moment they're entered.

**Decision:**

- **Translations live on the tag as JSON** (`translations`,
  `{language code: name}`, migration 0100), on both tag tables. A join
  table would be one row per language for something that's read whole
  and edited whole on one form, with no query that filters by it.
  `tag_label()` / the Jinja global `tag_name()` (`app/tag_translations.py`)
  show the translation for `request.state.language`, otherwise the typed
  name. The language is club-wide (`ClubSetting` `language`); there's no
  per-user language to resolve.
- **The typed name stays the identity.** CSV export writes the base
  name, so a file re-imports the same way whatever language the club
  switches to. Lookup by a typed name (tagging, the form's "new tags"
  field, CSV import) matches the base name **or** any translation,
  ignoring case. Typing "red flag" in an English UI therefore reuses
  "Rote Liste" instead of splitting the group into two tags. For the same
  reason a translation may not equal another tag's name or translation.
- **Red flag = one chosen external-contact tag**, stored by id in
  `ClubSetting` `applicant_red_flag_tag_id`. It's picked on
  `/contacts/tags`. An id survives renames and translations. A deleted
  tag simply means "none".
- **Any one of name, email, phone matching is enough.** The name match is
  first + last, both present, case-insensitive with spacing collapsed.
  The email match is case-insensitive against any of the contact's
  addresses. Phone numbers are compared digits-only, so "0170 999" and
  "0170-999" agree. That normalization is scoped to this check: the list
  search stays a plain substring match. Soft-deleted contacts don't count.
- **Computed live, never stored** (`find_red_flags()` in
  `app/services/applicants.py`), on every applicants list and detail
  view. A contact flagged *after* someone applied still shows up, and
  nothing about the match outlives the applicant, which can be
  hard-deleted (ADR 0091). The detail page links the matching contact
  only for users who may read external contacts. Without that permission
  the warning shows the name but no link. With the external contacts
  module off, there are no flags.

**Consequences:** One query for the flagged contacts per page view, and
matching happens in Python. That's fine for a handful of flagged contacts
and a page of applicants, but would need an indexed query if either
grew into the thousands. A name match can be a different person with the
same name: the flag is a prompt to look closer, not a verdict. Tag
lookups now load the tag list instead of running a single `WHERE`. Tag
pools are small, so this costs nothing measurable.
