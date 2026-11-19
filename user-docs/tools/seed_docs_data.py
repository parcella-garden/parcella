#!/usr/bin/env python3
"""Extra fake data for the user-docs screenshots, on top of the built-in
sample data (Admin -> Sample data), which has no applicants, member
tags, external contacts, bank bookings, invoices, announcements, notes,
processes or custom calendars.

Goes through the app's own web routes (log in, POST forms with the CSRF
token), like a board member clicking through the UI. Every section
checks for its own marker first, so running it twice adds nothing.
All names, addresses and numbers are made up.

    python user-docs/tools/seed_docs_data.py [--base-url http://127.0.0.1:8000]

Run it on a throwaway dev instance only (see tools/dev_server.sh).
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta

import httpx

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
TODAY = date.today()


class Client:
    def __init__(self, base_url: str, user: str, password: str):
        self.c = httpx.Client(base_url=base_url, follow_redirects=False, timeout=60)
        self.get("/auth/login")
        r = self.post("/auth/login", {"email": user, "password": password}, ok=(302,))
        if r.headers.get("location", "").startswith("/auth/login"):
            sys.exit("login failed")

    def get(self, path: str) -> str:
        r = self.c.get(path, follow_redirects=True)
        r.raise_for_status()
        return r.text

    def post(self, path: str, data, ok=(200, 302, 303), files=None) -> httpx.Response:
        token = self.c.cookies.get("csrf", "")
        r = self.c.post(path, data=data, files=files, headers={"X-CSRF-Token": token})
        if r.status_code not in ok:
            raise RuntimeError(f"POST {path} -> HTTP {r.status_code}: {r.text[:300]}")
        return r

    def ids(self, path: str, pattern: str) -> list[str]:
        """Unique UUIDs from hrefs on `path` matching e.g. '/members/{id}'."""
        rx = re.compile(r'href="' + pattern.replace("{id}", f"({UUID})") + r'"')
        seen = []
        for m in rx.finditer(self.get(path)):
            if m.group(1) not in seen:
                seen.append(m.group(1))
        return seen


def location_id(r: httpx.Response) -> str:
    m = re.search(UUID, r.headers.get("location", ""))
    if not m:
        raise RuntimeError(f"no id in redirect {r.headers.get('location')!r}")
    return m.group(0)


def section(name: str, done: bool):
    print(f"{'skip' if done else 'seed'}  {name}{' (already there)' if done else ''}")
    return not done


# ---------------------------------------------------------------------------

def seed_applicants(cl: Client) -> None:
    if not section("applicants", "jonas.beispiel@example.org" in cl.get("/applicants/?filter=all")):
        return
    people = [
        ("Jonas", "Beispiel", "jonas.beispiel@example.org", "+49 151 0000001", 3, None,
         "We are a family of four and would love a plot close to the playground."),
        ("Aylin", "Muster", "aylin.muster@example.org", "+49 151 0000002", 40, "CONTACTED",
         "I have been gardening on my balcony for years and want to grow vegetables."),
        ("Peter", "Probe", "peter.probe@example.org", "", 120, "OFFERED",
         "Retired, lots of time, happy to help with communal work."),
    ]
    for first, last, email, phone, days_ago, status, message in people:
        values = {"first_name": first, "last_name": last, "email": email, "phone": phone,
                  "message": message, "board_note": "", "applied_at": (TODAY - timedelta(days=days_ago)).isoformat()}
        aid = location_id(cl.post("/applicants/new", values))
        if status:
            cl.post(f"/applicants/{aid}/edit", {**values, "status": status})


def seed_member_tags(cl: Client) -> None:
    members = cl.ids("/members/", "/members/{id}")
    if not section("member tags", "Board" in cl.get("/members/tags") and "Beekeeper" in cl.get("/members/tags")):
        return
    plan = [("Board", members[:2]), ("Beekeeper", members[2:4]), ("Newsletter by post", members[4:7])]
    for tag, mids in plan:
        for mid in mids:
            cl.post(f"/members/{mid}/tags/add", {"tag_id": "", "name": tag})


def seed_contacts(cl: Client) -> dict:
    page = cl.get("/contacts/")
    if not section("external contacts", "Grünwerk Gartenbau" in page):
        return {"company": (cl.ids("/contacts/?search=Grünwerk", "/contacts/{id}") or [None])[0]}
    company = location_id(cl.post("/contacts/new", {
        "kind": "COMPANY", "company_name": "Grünwerk Gartenbau GmbH", "street": "Lindenweg 12",
        "postal_code": "12345", "city": "Musterstadt", "iban": "", "email": "info@gruenwerk.example",
        "phone": "+49 30 0000100", "notes": "Hedge cutting and tree care for the communal areas.",
    }))
    person = location_id(cl.post("/contacts/new", {
        "kind": "PERSON", "company_name": "Grünwerk Gartenbau GmbH", "first_name": "Sabine",
        "last_name": "Grün", "position": "Project manager", "email": "s.gruen@gruenwerk.example",
        "phone": "+49 30 0000101",
    }))
    craftsman = location_id(cl.post("/contacts/new", {
        "kind": "PERSON", "first_name": "Klaus", "last_name": "Hammer", "position": "Plumber",
        "street": "Am Bach 3", "postal_code": "12345", "city": "Musterstadt",
        "email": "klaus.hammer@example.net", "phone": "+49 170 0000200",
        "notes": "Water pipes and meter changes. Call before 8 am.",
    }))
    for cid, tag in [(company, "Gardening"), (person, "Gardening"), (craftsman, "Craftsman"), (craftsman, "Water")]:
        cl.post(f"/contacts/{cid}/tags/add", {"name": tag})
    return {"company": company}


def seed_finances(cl: Client, contacts: dict) -> None:
    if not section("finances", "Girokonto Sparkasse" in cl.get("/finances/accounts")):
        return
    cl.post("/finances/accounts", {"name": "Girokonto Sparkasse", "account_type": "BANK",
                                   "account_number": "DE00 1234 5678 0000 0000 00", "note": "Main account",
                                   "is_active": "on"})
    cl.post("/finances/accounts", {"name": "Cash box", "account_type": "CASH", "is_active": "on"})
    account = cl.ids("/finances/accounts", "/finances/accounts/{id}[^\"]*")[0]

    for days_ago, amount, desc, who in [
        (30, "-245.90", "Electricity bill communal house", "Stadtwerke Musterstadt"),
        (21, "120.00", "Donation summer party", "Anna Example"),
        (10, "-58.40", "Seeds and compost", "Gartenmarkt Musterstadt"),
    ]:
        cl.post(f"/finances/accounts/{account}/bookings/manual/confirm", {
            "booking_date": (TODAY - timedelta(days=days_ago)).isoformat(), "amount": amount,
            "description": desc, "counterparty": who, "match_choice": "none"})

    categories = cl.get("/finances/categories")
    cat = re.search(r'value="(' + UUID + r')"[^>]*>[^<]*Ehrenamt', categories) or \
        re.search(r'/finances/categories/(' + UUID + ')', categories)
    cl.post("/finances/incoming-invoices", {
        "sender": "Grünwerk Gartenbau GmbH", "invoice_number": "GW-2026-0815",
        "invoice_date": (TODAY - timedelta(days=14)).isoformat(), "note": "Hedge cutting, main path",
        "external_contact_id": contacts.get("company") or "",
        "category_id": cat.group(1) if cat else "", "description": "Hedge cutting (6 h)", "amount": "384.00",
    }, files={"file": ("", b"", "application/octet-stream")})

    year = TODAY.year
    r = cl.post("/finances/runs", {"year": str(year), "subject": f"Annual invoice {year}",
                                    "issued_date": TODAY.isoformat(),
                                    "due_date": (TODAY + timedelta(days=30)).isoformat(),
                                    "footer_text": "Please transfer the amount by the due date."})
    run = location_id(r)
    income = re.search(r'value="(' + UUID + r')"[^>]*>[^<]*Membership', cl.get(f"/finances/runs/{run}"))
    cl.post(f"/finances/runs/{run}/items", {"order_number": "1", "name": "Membership fee",
                                             "pricing_mode": "fixed_per_parcel", "unit_price": "60.00",
                                             "applies_to_all_parcels": "on",
                                             "category_id": income.group(1) if income else ""})
    cl.post(f"/finances/runs/{run}/items", {"order_number": "2", "name": "Lease",
                                             "pricing_mode": "per_sqm", "unit_price": "0.25",
                                             "applies_to_all_parcels": "on"})
    cl.post(f"/finances/runs/{run}/finalize", {})
    invoices = cl.ids(f"/finances/runs/{run}", "/finances/invoices/{id}")
    if not invoices:
        print("WARN  invoice run not finalized -- no invoices created")
        return
    # invoice 1: paid in full through a matched bank booking; invoice 2: partly
    # paid by hand; the rest stay open -- so every payment state is on screen.
    total = invoice_subtotal(cl, invoices[0])
    cl.post(f"/finances/accounts/{account}/bookings/manual/confirm", {
        "booking_date": (TODAY - timedelta(days=1)).isoformat(), "amount": total,
        "description": f"Annual invoice {year}", "counterparty": "", "match_choice": f"invoice:{invoices[0]}"})
    if len(invoices) > 1:
        cl.post(f"/finances/invoices/{invoices[1]}/payments", {
            "amount": "50.00", "paid_on": TODAY.isoformat(), "note": "Partial payment, rest by end of month",
            "account_id": account})


def invoice_subtotal(cl: Client, invoice_id: str) -> str:
    """The invoice's amount as shown on its page, as a plain decimal string."""
    html = cl.get(f"/finances/invoices/{invoice_id}")
    m = re.search(r"Subtotal</dt>\s*<dd[^>]*>([^<]+)</dd>", html)
    if not m:
        raise RuntimeError("couldn't read the invoice subtotal")
    raw = re.sub(r"[^\d,.]", "", m.group(1))
    # "1.234,56" / "1,234.56" / "60,00" / "60.00" -> "1234.56"
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".") if raw.rfind(",") > raw.rfind(".") else raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")
    return raw


def seed_announcement(cl: Client) -> None:
    if not section("announcement", "Spring work day" in cl.get("/announcements/")):
        return
    cl.post("/announcements/new", {
        "title": "Spring work day on Saturday",
        "summary": "Join us to get the communal areas ready for the season.",
        "body_markdown": ("Dear gardeners,\n\nour **spring work day** starts on Saturday at 9 am at the "
                          "club house. Please bring gloves and, if you have one, a rake.\n\n"
                          "- hedge cutting along the main path\n- cleaning the water pipes\n"
                          "- coffee and cake from 12 noon\n\nThe hours count towards your work hours."),
    }, files={"image": ("", b"", "application/octet-stream")})


def seed_note(cl: Client) -> None:
    if not section("note", "Board meeting: water pipes" in cl.get("/notes/")):
        return
    cl.post("/notes/new", {
        "title": "Board meeting: water pipes", "note_date": (TODAY - timedelta(days=5)).isoformat(),
        "category_id": "", "new_tags": "Board meeting, Water",
        "body_markdown": ("## Decisions\n\n1. The main water pipe gets new shut-off valves before winter.\n"
                          "2. Klaus Hammer sends a quote by the end of the month.\n\n## Open questions\n\n"
                          "- Who reads the meters on the eastern row?"),
        "source_url": "",
    })


def seed_process(cl: Client) -> None:
    if not section("process", bool(cl.ids("/processes/", "/processes/{id}"))):
        return
    tpl = location_id(cl.post("/processes/templates/example", {"key": "plot_handover"}))
    parcel = cl.ids("/parcels/", "/parcels/{id}")[0]
    cl.post("/processes/new", {"template_id": tpl, "subject_id": parcel, "title": ""})


def seed_calendar(cl: Client) -> None:
    if not section("custom calendar", "Club house bookings" in cl.get("/calendar/custom")):
        return
    cl.post("/calendar/custom/new", {"name": "Club house bookings", "description": "Who uses the club house when.",
                                     "color": "#2e7d32"})
    cal = cl.ids("/calendar/custom", "/calendar/custom/{id}")[0]
    for days, title, start, end, where in [
        (6, "Birthday party (parcel 12)", "15:00", "21:00", "Club house"),
        (13, "Seed swap", "10:00", "13:00", "Club house terrace"),
    ]:
        cl.post(f"/calendar/custom/{cal}/new", {
            "title": title, "description": "", "location": where,
            "start_date": (TODAY + timedelta(days=days)).isoformat(), "start_time": start,
            "end_date": "", "end_time": end})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--user", default="admin@parcella.local")
    ap.add_argument("--password", default="admin1234")
    args = ap.parse_args()
    cl = Client(args.base_url.rstrip("/"), args.user, args.password)
    failed = []
    contacts = {}
    for name, fn in [("applicants", seed_applicants), ("member tags", seed_member_tags),
                     ("external contacts", seed_contacts), ("finances", None),
                     ("announcement", seed_announcement), ("note", seed_note),
                     ("process", seed_process), ("custom calendar", seed_calendar)]:
        try:
            if name == "external contacts":
                contacts = fn(cl) or {}
            elif name == "finances":
                seed_finances(cl, contacts)
            else:
                fn(cl)
        except Exception as e:  # keep going; report at the end
            failed.append(name)
            print(f"FAIL  {name}: {e}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
