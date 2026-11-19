# Writing the Parcella user documentation

This folder is the **user** documentation published at
<https://docs.parcella.org>. It is separate from `../docs/`, which is the
developer documentation (module internals, ADRs). Both are kept up to date
in the same pull request as the code change they describe.

## Who we write for

Board members of an allotment garden association (chair, treasurer,
secretary, the person who keeps the meter list). They know their club
very well and know computers reasonably well. They do **not** know what
FastAPI, a module flag or an enum is. Gardeners only see the public
signup page (see `docs/gardeners/`).

## Voice

- Plain, friendly English, second person ("you"), present tense.
- Short sentences. One idea per paragraph.
- Explain the *club* consequence, not the implementation: "Ending a
  tenancy keeps the history -- the old tenant still shows on the
  parcel's history tab" rather than "rows are historized (ADR 0005)".
- No ADR numbers, file paths, class names or code identifiers in the
  user docs. Developers have `../docs/` for that.
- Never invent behaviour. If the code is unclear, write what you can
  verify and add an HTML comment `<!-- TODO(verify): ... -->`.

## UI wording

Use the exact English labels the user sees. They come from
`app/translations/en.json` -- look up the key a template uses
(`t('members.first_name')`) and copy the English text. Write UI labels
in **bold**: click **Save**, open **Members → Import**.

German club terms that have no good English equivalent (Kaution,
Wertgutachten, Pacht ...) go into `docs/glossary.md`; in the text, use
the English label the app uses and link to the glossary on first use.

## Page structure for a module chapter

```markdown
# <Module name>

One or two sentences: what this module is for, from the club's view.

!!! info "Who can use this"
    Which roles/groups see it, which module switch turns it on, and
    whether it's on by default.

## <Screen name>            <- one H2 per screen (list, detail, form, ...)

![<Screen name>](../assets/screenshots/<module>/<screen>.png)

What the screen shows and when you'd come here.

| Field / button | What it does |
|---|---|
| **Label** | Explanation, incl. validation, defaults, side effects |

Then any "What happens when you save", tips, and caveats as
`!!! tip`, `!!! warning` admonitions.

## Related
Links to task guides and neighbouring chapters.
```

Cover **every** screen (every template a user can reach, incl. import
previews, confirmation pages and configuration screens), and on each
screen every field, filter, column, button and action. Mention which
actions need write or delete permission.

## Screenshots

Screenshots are generated, never hand-made, so they stay current:
`tools/screenshots.py` logs into a local instance loaded with the
built-in sample data and photographs every entry in
`tools/screens/*.yml`.

Every image you reference must have a matching manifest entry in
`tools/screens/<module>.yml`:

```yaml
- name: members/list            # -> docs/assets/screenshots/members/list.png
  url: /members/
- name: members/detail
  from: /members/               # open this page ...
  follow: '^/members/\d+$'      # ... and follow the first link whose href matches
- name: members/form-new
  url: /members/new
  full_page: true               # optional, default false (viewport 1440x900)
```

Use only `url`, or `from` + `follow`. `follow` may also be a list of
regexes, followed one after another (list → detail → edit form), for
screens that are only linked from a detail page. Image paths in Markdown are
relative to the page: from `docs/modules/members.md` it's
`../assets/screenshots/members/list.png`, from
`docs/modules/finances/invoices.md` it's
`../../assets/screenshots/finances/invoice-list.png`.

## Building locally

```bash
pip install -r user-docs/requirements.txt
mkdocs serve -f user-docs/mkdocs.yml          # http://127.0.0.1:8000
mkdocs build --strict -f user-docs/mkdocs.yml # what CI runs
```

## Translations

English is written first and is the source. The other languages are the
app's own: de, pl, cs, sk, fr, nl. A chapter is translated once it is
stable. Anything not translated yet is shown in English, so a language
never has holes.

**Files.** A translation sits next to its English page with the language
as a suffix: `modules/members.md` → `modules/members.de.md`. File names,
folders and links stay English (`[Parcels](parcels.md)`, not
`parcels.de.md`); the build picks the right language by itself.

**Anchors.** Other pages link to headings (`members.md#membership`). A
translated heading would get a different anchor and break those links,
so give every translated H2/H3 its English anchor explicitly:

```markdown
## Mitgliedschaft {#membership}
```

The strict build checks this once the language is switched on.

**Labels.** Use the exact UI labels from `app/translations/<lang>.json`,
the same way English pages use `en.json`.

**Screenshots.** Optional. English ones are used until a language has its
own. To take them: `python user-docs/tools/screenshots.py --lang de`
saves `members/list.de.png` next to `members/list.png` (and leaves the
club's UI language on German; switch it back before English shots).

**Switching a language on.** In `mkdocs.yml`, set the language's
`build: true` with its first translated pages, and add its menu titles
under `nav_translations`. Until then the language isn't built at all, so
the live site never offers a language that is English behind the switch.

**Keeping translations current.** When an English page changes, update
its translations in the same PR if that's cheap (a renamed label, a new
field). If not, put this at the top of each translation that's now
behind, in that language, and remove it when the page is caught up:

```markdown
!!! warning "Noch nicht aktualisiert"
    Diese Seite beschreibt einen älteren Stand. Die englische Fassung
    ist aktuell (Sprache oben umschalten).
```

(English template for other languages: "Not updated yet" / "This page
describes an older version. The English version is current (switch the
language at the top)." No link: inside a translation, `members.md`
leads to the translated page itself.)
