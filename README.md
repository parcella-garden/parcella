# Parcella Garden Allotment Manager

---

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)

Parcella is an open-source web [application for managing allotment garden associations](https://parcella.org) AKA ("Kleingartenverein" / "Schrebergarten" associations): members, parcels,
lease administration, mandatory work hours and much more.

Started as a vibe-coding project for we became sick of these ill-architectured proprietary software - hopefully generic enough for any allotment garden association, in any country. If you miss anything, feel free to drop a line at https://forum.parcella.org - or just fix it yourself here on Github.

## This software provides (tech, operational and logical features):

- ✅ a responsive design so you can use it on your smart phone during your garden inspections, water meter reading etc...
- ✅ strict separation of association and lease
- ✅ REST API with JWT authentication and Swagger documentation
- ✅ Database migrations via Alembic
- ✅ a certain testing suite
- ✅ an integration with Nextcloud for file dropping (other clouds can be done within a wink of an eye)
- ✅ CMS integrations for your beloved website
- ✅ bullet proof runs against shannon and strix (for now)
- ✅ switch off and sort modules like "electricity" as you like it


📖 **Detailed [documentation](https://github.com/parcella-garden/parcella/tree/main/docs), which later might become an HTTP online help.**

---

## License

This project is licensed under the **GNU Affero General Public License v3.0** (see [LICENSE](./LICENSE)). In particular, this means: anyone who runs a modified version of this software as a network service (e.g. SaaS for other associations) must make the source code of that modified version publicly available. Details and contribution guidelines in [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Screenshot of the dashboard

![parcella dashboard](dashboard_screenshot.png "parcella screenshot")

## Features (current state)

### General

- ✅ Session-based login (cookie-based)
- ✅ Invitation system (no public sign-up)
- ✅ Advanced rights and roles via a group system: Admin, board and other users enjoy fine-grained access to modules.
- ✅ Member management (core data, multiple phone numbers, multiple email addresses, IBAN, soft delete for Admin/Board)
- ✅ Parcel management (status: active/terminated/deleted, area, termination)
- ✅ Many-to-many member ↔ parcel assignment, multiple parcels per member; every resident of a parcel is held jointly responsible, with no hierarchy between them
- ✅ CSV export and import (members, parcels) with duplicate detection
- ✅ Dashboard with live statistics (members, parcels, areas, plus open purchase requests and open tickets when those modules are enabled)
- ✅ Public signup API: lets an external CMS (WordPress, TYPO3, Contao, or anything else) submit work-session signups without a Parcella login, identifying only by parcel number (never a member name - the public site must not expose who lives where). Parcella matches the optional submitted name against the parcel's current residents and registers just that member if it's unambiguous, or every current resident as a precaution if it isn't, creating real participants the board can review and correct like any other signup. Off by default (it opens a public write endpoint) and protected by a regenerable shared token; a reference WordPress connector plugin (`parcella-connector`) is included under `integrations/wordpress/`, consolidating every WordPress <-> Parcella integration (currently signup; more planned) behind one shared settings screen

### Settings

- ✅ Club settings (A/B/C area sizes, lang settings, SMTP configuration and much more)
- ✅ Custom club branding: upload your own logo and set your club's display name from Admin -> Settings, replacing the default tree icon and "Parcella" placeholder everywhere in the sidebar 
- ✅ i18n: 7 languages (German, English, Polish, Czech, Slovak, French, Dutch), one language per installation, switchable in admin settings, every module and the navigation fully translated. JSON translation catalogs, English as the base/authoring language and the runtime fallback for any missing key.
- ✅ l10n: region and currency are independent settings from language (e.g. an English-language UI can still show German number formatting and EUR). Number and money formatting (correct decimal/thousands separators and currency symbol position per
region); address display order adapts per region (continental
postcode-before-city vs. UK-style postcode-last).

### Modules (can be toggled and sorted in navigation)

#### Working sessions

- ✅ Work-hours system (year-based configuration, configurable per parcel or per member)
- ✅ Work sessions (standard and special), participant management with hours tracking
- ✅ Task backlog for work sessions: create tasks, optionally schedule to a session, optionally assign to a specific signed-up participant (workload label only - no member ability/health data stored, task matching stays a manual coordinator decision)
- ✅ Sponsorships (flat-rate hour credit for area coordinators)
- ✅ Club roles / extended board with work-hours exemption
- ✅ Annual work-hours report with CSV export

#### Water and electricity metering

- ✅ Water and electricity metering (metering points, meters, readings, consumption reports)

#### Property and accident insurance

- ✅ Property and accident insurance tracking per parcel, with annual report

#### Calendar module

- ✅ Calendar module: community calendar (member meetings, parcel inspections, work sessions - all in one simple upcoming-items list,  no full calendar-grid UI), member birthdays (with a dashboard "this week" widget highlighting round-number birthdays), council on-site presence scheduling, and self-service council absence logging (anyone with a login can enter their own). Each with its own ICS export - the community calendar's feed is public (embeddable on your public website), the other three require a private access token since they contain more sensitive information

#### Support ticket system

- ✅ Ticket system with automatic member matching, spam heuristics, IMAP inbox polling, six explicit statuses (Active/Assigned/Waiting/Postponed/Closed/Deleted), bulk status-change and bulk-assign from the ticket list, and safely rendered HTML emails (allowlist-based sanitization, no tracking pixels, no script execution)

#### Purchase requests

- ✅ Purchase requests with a two-person approval principle (two distinct board members must approve before a purchase is made)

#### Announcements module

- ✅ Author a piece of club news once (Markdown body, image, optional print override) and deliver it to all three channels - a paced email send to current members with notifications enabled (plus a one-off test send), a WordPress blog draft via the site's REST API (credentials on Admin -> Integrations), and a one-page branded PDF that auto-shortens and adds a QR code to the published blog post if the full text doesn't fit. Off by default, admin/board only. See `docs/module-announcements.md`.

#### Inventory module

- ✅ An asset register for everything the club owns (and personal items members store on club property, tracked with the same financial fields for insurance/liability purposes), grouped into freely-configurable categories, with a quantity-aware lending system for borrowable items (checkout/return, a suggested per-loan fee, a board-wide "who has what out right now" view). Full REST API alongside the web UI. See `docs/module-inventory.md`.

#### Cloud storage module

- ✅ Lets board/admin browse, upload to, and download from a per-parcel document folder in the club's own Nextcloud instance (lease agreements, membership paperwork). Off by default, admin/board only; who can see a folder's contents is managed directly in Nextcloud, not by Parcella. See `docs/module-cloud-storage.md`.

#### Task board module

- ✅ A general kanban board (To Do / In Progress / Done) for club business that isn't tied to a work session, with drag-and-drop reordering. Admin/board only, separate from the work-hours module's session-scoped task backlog. Full REST API alongside the web UI. See `docs/module-tasks.md`.

---

## Tech stack

| Component | Technology |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Templates | Jinja2 (server-side rendering) |
| CSS | Bootstrap 5 |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| i18n/l10n | JSON translation catalogs + Babel (number/currency formatting) |
| Calendar/ICS | icalendar (RFC 5545 feed generation) |
| Announcements | markdown (authoring), bleach (sanitizing), WeasyPrint (PDF), qrcode (print QR codes) |
| Container | Docker + docker compose |

---

## Quick start (development)

### 1. Clone and configure the repository

```bash
git clone https://github.com/parcella-garden/parcella.git
cd parcella
cp .env.example .env

# adjust .env as needed (passwords, SMTP, etc.)
```

### 2. Set UID/GID (avoids root-owned files on the host)

```bash
# only if you work on Linux. Please do not do this on Mac or Windows

echo "UID=$(id -u)" >> .env
echo "GID=$(id -g)" >> .env
```

### 3. Build the Docker container, migrate the database, and start

```bash
docker compose build web
docker compose run --rm --entrypoint alembic web upgrade head
docker compose up -d
```

The application is now available at **http://localhost:8000**; documentation: **https://github.com/parcella-garden/parcella/tree/main/docs**

### 4. First login

An admin account is created automatically on first startup:

- **Email:** `admin@parcella.local`
- **Password:** `admin1234`

⚠️ **Please change the password immediately after your first login! Create yourself a new admin user and delete admin@parcella.local**

---

## REST API

Alongside the web UI, there is a full REST API under `/api/v1/`.

**Interactive documentation:**

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI schema (JSON): http://localhost:8000/api/openapi.json

### Authentication (JWT)

```bash
# Request a token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@parcella.local", "password": "admin1234"}'

# Response: {"access_token": "...", "token_type": "bearer", "expires_in_minutes": 1440}

# Use the token
curl http://localhost:8000/api/v1/members \
  -H "Authorization: Bearer <access_token>"
```

Tokens are valid for 24 hours. The Swagger UI has an "Authorize" button for convenient testing.

### Key endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Request token (JSON) |
| GET | `/api/v1/auth/me` | Retrieve own profile |
| GET | `/api/v1/stats` | Dashboard statistics |
| GET | `/api/v1/members` | List members (search, pagination) |
| GET | `/api/v1/members/{id}` | Retrieve member incl. parcels |
| POST | `/api/v1/members` | Create member |
| PUT | `/api/v1/members/{id}` | Update member (partial update) |
| DELETE | `/api/v1/members/{id}` | Delete member (soft delete) |
| POST | `/api/v1/members/{id}/phones` | Add phone number |
| POST | `/api/v1/members/{id}/emails` | Add email address |
| GET | `/api/v1/parcels` | List parcels (status filter) |
| GET | `/api/v1/parcels/{id}` | Retrieve parcel incl. members |
| POST | `/api/v1/parcels` | Create parcel |
| PUT | `/api/v1/parcels/{id}` | Update parcel (also status/termination) |
| POST | `/api/v1/parcels/{id}/assignments` | Assign a member |
| DELETE | `/api/v1/parcels/{id}/assignments/{aid}` | Remove assignment |
| GET | `/api/v1/club-settings` | Retrieve club settings |
| PUT | `/api/v1/club-settings/{key}` | Set a setting (admin/board only) |
| GET/PUT | `/api/v1/work-hours/configuration/{year}` | Work-hours configuration |
| GET/POST/PUT/DELETE | `/api/v1/work-hours/club-roles` | Club roles + assignments |
| GET/POST/PUT/DELETE | `/api/v1/work-hours/sessions` | Work sessions + participations |
| GET/POST/PUT/DELETE | `/api/v1/work-hours/tasks` | Task backlog, scheduling, assignment |
| GET/POST/PUT/DELETE | `/api/v1/work-hours/sponsorships` | Sponsorships |
| GET | `/api/v1/work-hours/evaluation/{year}` | Annual report |
| GET/POST/PUT/DELETE | `/api/v1/water/metering-points` | Water metering points + meters |
| POST | `/api/v1/water/metering-points/{id}/meter/exchange` | Exchange water meter |
| GET/POST/DELETE | `/api/v1/water/metering-points/{id}/readings` | Water readings |
| GET | `/api/v1/water/evaluation/{year}` | Water consumption report |
| GET/POST/PUT/DELETE | `/api/v1/electricity/metering-points` | Electricity metering points + meters (same shape as water) |
| GET/POST/PUT/DELETE | `/api/v1/insurance/packages` | Property insurance packages |
| GET/PUT | `/api/v1/insurance/configuration/{year}` | Accident insurance amounts |
| GET/PUT | `/api/v1/insurance/parcels/{id}/{year}` | Insurance status of a parcel |
| GET | `/api/v1/insurance/evaluation/{year}` | Annual report |
| GET/POST | `/api/v1/tickets` | List/create tickets |
| GET/PUT | `/api/v1/tickets/{id}` | Ticket detail / status / assignment |
| GET/POST | `/api/v1/tickets/{id}/messages` | Ticket messages |
| GET/POST | `/api/v1/purchase-requests` | List/create purchase requests |
| POST | `/api/v1/purchase-requests/{id}/approve` | Approve (two distinct approvals needed) |
| POST | `/api/v1/purchase-requests/{id}/reject` | Reject (single rejection is enough) |
| GET | `/api/v1/public/work-sessions/upcoming` | Public, unauthenticated: upcoming sessions for external CMS forms |
| GET | `/api/v1/public/parcels` | Public, unauthenticated: parcel list for external CMS forms |
| POST | `/api/v1/public/work-sessions/signup` | Public signup, requires `X-Parcella-API-Token` header |

Write access (POST/PUT/DELETE) requires the role `admin`, `board`, or
`treasurer`. Read access is available to all authenticated users
(including `readonly`).

---

## Database migrations (Alembic)

Schema changes go through Alembic rather than automatic `create_all()`.

```bash
# Apply migrations (also runs automatically on container startup)
docker compose run --rm --entrypoint alembic web upgrade head

# Generate a new migration after a model change
docker compose run --rm web alembic revision --autogenerate -m "Short description"
```

For an existing installation predating Alembic: see
[MIGRATION-NOTE.md](https://github.com/parcella-garden/parcella/blob/main/MIGRATION-NOTE.md).

---

## Production

### Using the published image

Running a club's own instance doesn't require cloning the whole repo or
building the image yourself. Versioned images are published to
[GHCR](https://github.com/parcella-garden/parcella/pkgs/container/parcella) on every
release. Grab just the two files you need:

```bash
mkdir parcella && cd parcella
curl -O https://raw.githubusercontent.com/parcella-garden/parcella/main/docker-compose.prod.yml
curl -o .env https://raw.githubusercontent.com/parcella-garden/parcella/main/.env.example
# edit .env: passwords, SECRET_KEY, ENVIRONMENT=production, SMTP, etc.
docker compose -f docker-compose.prod.yml run --rm --entrypoint alembic web upgrade head
docker compose -f docker-compose.prod.yml up -d
```

The admin panel's "update available" notice (`/admin/system`) uses this
same `docker-compose.prod.yml` for its `pull`/`up` instructions. Pin
`PARCELLA_VERSION` in `.env` to a specific release for a reproducible
deploy instead of always tracking `latest`.

### Environment

For production, set `ENVIRONMENT=production`:

```bash
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
ENVIRONMENT=production
POSTGRES_PASSWORD=<secure-password>
```

Both are enforced, not just recommended: with `ENVIRONMENT` set to anything other than `development`, the app refuses to start while `SECRET_KEY` is still the built-in default (which is published in this repository and signs every session cookie and API token). Setting `ENVIRONMENT=production` is also what makes the session and CSRF cookies HTTPS-only and enables HSTS. Keep `SECRET_KEY` with your backups - changing it later logs everyone out and makes stored SMTP/Nextcloud credentials unreadable.

Recommended: put Nginx in front as a reverse proxy with Let's Encrypt (Certbot).

```nginx
server {
    listen 443 ssl;
    server_name verwaltung.myassociation.example;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # Needed for login throttling and the signup API's rate limit to
        # see the real client address; run uvicorn with --proxy-headers
        # to trust it (only ever behind a proxy you control).
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Database structure

```
users                         – application users (not club members)
invitations                   – email invitation tokens
members                       – club members
member_phones                 – n phone numbers per member
member_emails                 – n email addresses per member
parcels                       – garden parcels
member_parcels                – m:n member <-> parcel assignment (with metadata)
club_settings                 – key-value store for club master data
work_hours_configuration      – year-based hours/rate configuration
club_roles                    – club offices (board, extended board, etc.)
member_club_roles             – member -> club role assignment (year-based)
work_sessions                 – standard and special work sessions
session_participations        – who attended which session (with hours)
sponsorships                  – area responsibilities (flat-rate hour credit)
change_history                 – generic audit log for field changes
metering_points, meters,
meter_readings                 – water/electricity metering
property_insurance_packages,
insurance_configuration,
parcel_insurance                – insurance tracking per parcel/year
tickets, ticket_messages        – support ticket system
purchase_requests,
purchase_request_approvals      – purchase requests with two-person approval
```
