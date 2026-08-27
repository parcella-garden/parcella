# Production customizations belong in docker-compose.override.yml, not in docker-compose.prod.yml itself

**Context:** kermie ran the documented update flow (`docker compose -f
docker-compose.prod.yml pull` then `up -d`) on his own prod instance
after v1.0.7 was released, following exactly the instructions
`/admin/system`'s "update available" notice shows. `pull` reported
nothing to fetch, `up -d` just restarted the existing container, and
the instance stayed on v1.0.6 -- with no error at any point. It looked
successful.

**Root cause:** his `docker-compose.prod.yml` had been hand-edited
directly -- `web:` was switched from the tracked `image:
ghcr.io/parcella-garden/parcella:...` back to `build: context: .`, to
support his reverse-proxy setup (a custom `command:` adding uvicorn's
`--proxy-headers`, a non-default port bound to `127.0.0.1`, and a
bind-mounted `./postgres_data` instead of a named volume). Once that
edit exists, `docker compose pull` has nothing to do by design -- a
`build:`-based service was never pullable in the first place -- and
nothing in the documented flow, or in the update-check feature itself,
ever re-examines the compose file's own content. kermie: "why did I
fail with a simple update... that shall not happen!"

kermie's own reaction reframed the fix correctly: "we have to think
globally as it is open source software that everybody shall be able to
use" -- this isn't a one-off mistake on his box, it's a trap any
self-hoster who needs the single most common production requirement
(a reverse proxy) will walk into the same way, silently, with no error
to point them at the cause.

## Decision

Document -- in the README's Production section and as a warning
directly in `/admin/system`'s update notice -- that any deployment
customization (reverse-proxy headers, port, volume paths, anything)
belongs in a `docker-compose.override.yml` next to
`docker-compose.prod.yml`, never as a direct edit to the tracked file.
Compose merges an override file in automatically, with no extra flag
needed on any command already in use.

**Why this fixes the actual failure mode, not just this one symptom:**
`docker compose pull` only ever refreshes what an `image:` key points
at. It has no concept of "the compose file's own content is stale" --
that's not something Docker pulls, regardless of whether the local
copy was hand-edited or just never re-fetched after a template change.
Splitting customizations into their own file means
`docker-compose.prod.yml` itself never has local changes to protect,
so re-fetching it (via `curl -O`, the documented install method) stays
always safe, and the ordinary two-command update flow keeps working
for however a person's reverse proxy, ports, or volumes are set up.

**Not solved: making the failure loud instead of silent.** Detecting
"this docker-compose.prod.yml differs from what a fresh `curl -O`
would produce" from inside the running app would need either shipping
a checksum/manifest to compare against, or the app reading its own
compose file off disk and diffing it against a known-good version
fetched from GitHub -- meaningfully more machinery than a docs fix, and
it still wouldn't help anyone who already customized the file before
this was written down. Flagged here as a real gap, not attempted now:
the documentation fix stops it from recurring for the next new
deployment, but doesn't retroactively warn a diverged existing one.

## Not done here

kermie's own instance was not touched as part of this fix (a live prod
config/data change is a separate, deliberate action, not something to
bundle into a docs/template commit) -- migrating it to the
override-file pattern and completing its update to v1.0.7 is tracked
as its own follow-up, done with explicit confirmation before touching
the running container.
