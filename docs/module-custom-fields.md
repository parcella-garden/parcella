# Custom fields (members and parcels)

Issue #443, [ADR 0147](./ADR/0147-custom-fields.md). Fields of the club's
own on members and parcels, set up by a system admin; not a toggleable
module (no fields defined = nothing shows).

## Data model

```
custom_fields          target MEMBER|PARCEL, parent_id (-> group), key (fixed slug), label,
                       kind TEXT|LONG_TEXT|NUMBER|DATE|YEAR|CHECKBOX|CHOICE|GROUP, unit, options (JSON),
                       required, position, archived_at
custom_field_values    field_id, exactly one of member_id / parcel_id,
                       value_text | value_number | value_date | value_bool
```

- A GROUP is a yes/no with sub-fields (`parent_id`), one level deep.
- A value row exists only for a ticked yes/no or a filled-in field.
- `key` is unique per target and never changes (the label can).
- YEAR (kermie: "when was your summer house built" is a year, not a day)
  is four digits, 1000-9999, stored in `value_number`, returned by the
  API as an integer.

## Code

- `app/models/custom_fields.py` -- the two models and enums.
- `app/services/custom_fields.py` -- everything else, no HTTP:
  definitions (`create_field`, `update_field`, `set_archived`,
  `delete_field` -- for good, with values and sub-fields --,
  `move_field`, `value_counts` for the delete confirmation), values from the edit form (`save_form_values`: all or
  nothing, unticked group clears its sub-fields), detail rows
  (`view_rows`), the list filter (`filter_condition`), CSV
  (`csv_columns`, `csv_cell`, `import_targets`, `import_values`: only
  filled-in cells, like the rest of the import), and the API
  (`api_values`, `api_update`: only the given keys).
- `app/routers/admin/custom_fields.py` -- Admin → Custom fields
  (`require_system_admin`).
- `app/templates/_custom_fields.html` -- the form card, the detail
  card and the list filter controls, used by the member and parcel
  templates.
- `app/routers/api_custom_fields.py` -- `GET /api/v1/custom-fields?target=`,
  `GET|PUT /api/v1/members/{id}/custom-fields`,
  `GET|PUT /api/v1/parcels/{id}/custom-fields`.

## Hooks in the member and parcel modules

- Edit forms carry a hidden `custom_fields_present` marker and inputs
  `cf_<field id>`; a post without the marker leaves the values alone.
- The list filter is `cf_field` + `cf_value` (`__yes__`, `__no__`,
  `=<choice>` for an exact match, anything else = text contains). For
  members it is part of `MemberListFilter` (stored with announcements);
  for parcels a parameter of `filtered_parcels_query`.
- CSV: one column per active field after the fixed ones (sub-fields as
  "Group: Field", yes/no as Ja/Nein). In the import the fields are
  mapping targets `cf:<field id>`. The parcel import still skips
  existing parcels' own fields but fills in their custom fields.

## Known gaps

- Groups aren't repeatable (one pool per parcel).
- No change history for custom-field values yet (the parcel history
  only covers its own columns).
- Labels have no translations.
- Only members and parcels.
