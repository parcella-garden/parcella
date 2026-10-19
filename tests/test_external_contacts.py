"""
External contacts module: suppliers, craftsmen, authorities -- a
company plus a contact person (docs/module-external-contacts.md, ADR
0096). Focus: the uniqueness rule (person's name unique ignoring case,
company may repeat, a deleted contact frees its name), the separate tag
pool, CSV export/import round trip, and the links from incoming
invoices and purchase requests.
"""
import base64

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, ExternalContact, ExternalContactTag, Group, GroupMembership, GroupModulePermission,
    IncomingInvoice, MemberTag, PurchaseRequest, User, UserRole,
)
from app.auth import hash_password
from tests.conftest import auth_header, login
from tests.test_detail_page_navigation import web_login


async def _contacts():
    async with AsyncSessionLocal() as db:
        return (await db.scalars(
            select(ExternalContact)
            .options(
                selectinload(ExternalContact.phone_numbers),
                selectinload(ExternalContact.email_addresses),
                selectinload(ExternalContact.tags),
            )
            .order_by(ExternalContact.last_name)
        )).all()


async def _create(client, **fields) -> str:
    data = {"company_name": "Gartenbau Müller GmbH", "first_name": "Max", "last_name": "Müller", **fields}
    response = await client.post("/contacts/new", data=data)
    assert response.status_code == 302, response.text
    return response.headers["location"].rsplit("/", 1)[1]


async def test_create_contact_with_phone_email_and_tag(client, admin_user):
    await web_login(client, "admin@example.com")
    contact_id = await _create(
        client, street="Am Teich 1", postal_code="12345", city="Gartenstadt", iban="DE02120300000000202051",
        email="Max@Mueller-Gartenbau.de", phone="+49 30 123456", notes="Liefert Rindenmulch",
        tags_present="1", new_tags="Lieferant",
    )
    [contact] = await _contacts()
    assert contact.id == contact_id
    assert contact.company_name == "Gartenbau Müller GmbH" and contact.full_name == "Max Müller"
    assert [e.address for e in contact.email_addresses] == ["max@mueller-gartenbau.de"]
    assert [p.number for p in contact.phone_numbers] == ["+49 30 123456"]
    assert [t.name for t in contact.tags] == ["Lieferant"]

    await client.post(f"/contacts/{contact_id}/phone/add", data={"number": "0170 999", "label": "Mobil"})
    await client.post(f"/contacts/{contact_id}/email/add", data={"address": "buero@mueller-gartenbau.de"})

    page = await client.get("/contacts/")
    assert page.status_code == 200
    assert "Gartenbau Müller GmbH" in page.text and "Müller, Max" in page.text

    detail = await client.get(f"/contacts/{contact_id}")
    assert detail.status_code == 200
    for text in ("0170 999", "buero@mueller-gartenbau.de", "Liefert Rindenmulch", "Lieferant", "Gartenstadt"):
        assert text in detail.text

    assert "Müller, Max" in (await client.get("/contacts/?search=mueller-gartenbau")).text
    assert "Müller, Max" not in (await client.get("/contacts/?search=nobody")).text
    assert "Müller, Max" in (await client.get("/contacts/?search=0170")).text


async def test_contact_person_name_is_unique_ignoring_case_company_may_repeat(client, admin_user):
    await web_login(client, "admin@example.com")
    first_id = await _create(client)
    # Same company, other person: fine.
    await _create(client, first_name="Erika", last_name="Muster")

    # Same person (other case), other company: refused, form comes back with the error.
    response = await client.post("/contacts/new", data={
        "company_name": "Ganz Andere AG", "first_name": "max", "last_name": "MÜLLER",
    })
    assert response.status_code == 409
    assert "Max Müller" in response.text and "Ganz Andere AG" in response.text  # entered values kept
    assert len(await _contacts()) == 2

    # Renaming the second contact onto the first one's name is refused too.
    erika = [c for c in await _contacts() if c.first_name == "Erika"][0]
    response = await client.post(f"/contacts/{erika.id}/edit", data={"first_name": "Max", "last_name": "Müller"})
    assert response.status_code == 409

    # A deleted contact frees its name.
    assert (await client.post(f"/contacts/{first_id}/delete")).status_code == 302
    await _create(client, company_name="Ganz Andere AG", first_name="max", last_name="müller")
    assert sorted(c.company_name for c in await _contacts()) == ["Ganz Andere AG", "Gartenbau Müller GmbH", "Gartenbau Müller GmbH"]
    assert "Gartenbau" not in (await client.get("/contacts/?search=max")).text


async def test_contact_tags_are_separate_from_member_tags(client, admin_user):
    await web_login(client, "admin@example.com")
    contact_id = await _create(client)
    assert (await client.post(f"/contacts/{contact_id}/tags/add", data={"name": "Elektriker"})).status_code == 303

    async with AsyncSessionLocal() as db:
        assert [t.name for t in (await db.scalars(select(ExternalContactTag))).all()] == ["Elektriker"]
        assert (await db.scalars(select(MemberTag))).all() == []
    assert "Elektriker" not in (await client.get("/members/")).text
    assert "Elektriker" in (await client.get("/contacts/tags")).text


async def test_csv_export_imports_back_unchanged_and_updates_by_person(client, admin_user):
    await web_login(client, "admin@example.com")
    contact_id = await _create(client, city="Gartenstadt", phone="+49 30 123456", tags_present="1", new_tags="Lieferant")
    await client.post(f"/contacts/{contact_id}/email/add", data={"address": "a@example.org"})

    export = await client.get("/contacts/export/csv")
    assert export.status_code == 200
    assert "Gartenbau Müller GmbH" in export.text and "'+49 30 123456" in export.text  # formula-safe

    # Re-import the export plus one changed row and one new contact.
    csv_text = export.text + "Neue Firma;Erika;Muster;;;Hafenstadt;;e@example.org; 0170 1;Behörde;\n"
    csv_text = csv_text.replace("Gartenstadt", "Neustadt")
    preview = await client.post(
        "/contacts/import/preview", files={"file": ("contacts.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    assert 'value="first_name" selected' in preview.text  # headers of our own export are recognised

    mapping = {f"map_{i}": field for i, field in enumerate([
        "company_name", "first_name", "last_name", "street", "postal_code", "city",
        "iban", "email_addresses", "phone_numbers", "tags", "notes",
    ])}
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode("utf-8")).decode("ascii"), "delimiter": ";", **mapping,
    })
    assert response.status_code == 302

    contacts = {c.first_name: c for c in await _contacts()}
    assert set(contacts) == {"Max", "Erika"}
    max_ = contacts["Max"]
    assert max_.city == "Neustadt"
    assert [p.number for p in max_.phone_numbers] == ["+49 30 123456"]  # apostrophe stripped, no duplicate
    assert [e.address for e in max_.email_addresses] == ["a@example.org"]
    assert [t.name for t in max_.tags] == ["Lieferant"]
    erika = contacts["Erika"]
    assert erika.company_name == "Neue Firma" and erika.city == "Hafenstadt"
    assert [p.number for p in erika.phone_numbers] == ["0170 1"]
    assert [t.name for t in erika.tags] == ["Behörde"]


async def test_import_same_person_twice_in_one_file_does_not_duplicate(client, admin_user):
    await web_login(client, "admin@example.com")
    csv_text = 'Vorname;Nachname;Telefonnummern;Tags\nMax;Müller;0170 1;A\nmax;müller;"0170 1; 0170 2";"a; B"\n'
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode()).decode(), "delimiter": ";",
        "map_0": "first_name", "map_1": "last_name", "map_2": "phone_numbers", "map_3": "tags",
    })
    assert response.status_code == 302
    [contact] = await _contacts()
    assert sorted(p.number for p in contact.phone_numbers) == ["0170 1", "0170 2"]
    assert sorted(t.name for t in contact.tags) == ["A", "B"]


async def test_names_are_optional_and_company_only_contacts_are_unique_per_company(client, admin_user):
    await web_login(client, "admin@example.com")
    # Nothing at all is allowed -- twice, there's nothing to compare.
    empty_id = await _create(client, company_name="", first_name="", last_name="")
    await _create(client, company_name="", first_name="", last_name="")
    assert "Unnamed contact" in (await client.get(f"/contacts/{empty_id}")).text

    # Company without a person: unique per company, ignoring case.
    stadtwerke_id = await _create(client, company_name="Stadtwerke", first_name="", last_name="")
    response = await client.post("/contacts/new", data={"company_name": "STADTWERKE"})
    assert response.status_code == 409 and "Stadtwerke" in response.text
    # ...but the same company with a person is fine, and so is a last name alone.
    await _create(client, company_name="Stadtwerke", first_name="", last_name="Strom")
    assert (await client.post("/contacts/new", data={"last_name": "strom"})).status_code == 409
    # A first name alone is a person name too.
    await _create(client, company_name="", first_name="Ina", last_name="")
    assert (await client.post("/contacts/new", data={"first_name": "INA"})).status_code == 409

    contacts = await _contacts()
    stadtwerke = next(c for c in contacts if c.id == stadtwerke_id)
    assert stadtwerke.first_name is None and stadtwerke.last_name is None
    assert stadtwerke.display_name == "Stadtwerke"
    assert next(c for c in contacts if c.last_name == "Strom").display_name == "Stadtwerke (Strom)"
    assert "Stadtwerke" in (await client.get("/contacts/")).text

    # Deleting the company-only contact frees the company again.
    await client.post(f"/contacts/{stadtwerke_id}/delete")
    await _create(client, company_name="Stadtwerke", first_name="", last_name="")


async def test_import_without_names_matches_company_only_contacts_and_skips_blank_rows(client, admin_user):
    await web_login(client, "admin@example.com")
    await _create(client, company_name="Stadtwerke", first_name="", last_name="", city="Altstadt")
    csv_text = "Firma;Ort;Telefonnummern\nstadtwerke;Neustadt;0800 1\n;;\nBaumarkt;;\n;Nur Ort;\n"
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode()).decode(), "delimiter": ";",
        "map_0": "company_name", "map_1": "city", "map_2": "phone_numbers",
    })
    assert response.status_code == 302
    contacts = await _contacts()
    # Matched ignoring case; like any non-empty cell, the file's spelling wins.
    assert sorted((c.company_name or "", c.city or "") for c in contacts) == [
        ("", "Nur Ort"), ("Baumarkt", ""), ("stadtwerke", "Neustadt"),
    ]
    stadtwerke = next(c for c in contacts if c.company_name == "stadtwerke")
    assert [p.number for p in stadtwerke.phone_numbers] == ["0800 1"]

    # Nothing mapped at all: refused before reading any row.
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode()).decode(), "delimiter": ";",
    })
    assert response.status_code == 303 and "error=" in response.headers["location"]


async def test_readonly_user_without_group_cannot_see_contacts(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(User(email="ro@example.com", name="Read Only",
                    password_hash=hash_password("testpasswort123"), role=UserRole.READONLY))
        await db.commit()
    await web_login(client, "ro@example.com")
    assert (await client.get("/contacts/")).status_code == 403


async def test_group_with_read_only_cannot_create(client, admin_user):
    async with AsyncSessionLocal() as db:
        user = User(email="treasurer@example.com", name="Treasurer",
                    password_hash=hash_password("testpasswort123"), role=UserRole.READONLY)
        group = Group(name="Contacts readers")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="external_contacts", can_read=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()
    await web_login(client, "treasurer@example.com")
    assert (await client.get("/contacts/")).status_code == 200
    assert (await client.post("/contacts/new", data={"first_name": "A", "last_name": "B"})).status_code == 403


async def test_module_flag_hides_the_module(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_external_contacts", value="false", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    assert (await client.get("/contacts/")).status_code == 404
    headers = auth_header(await login(client, "admin@example.com"))
    assert (await client.get("/api/v1/external-contacts", headers=headers)).status_code == 404


async def test_rest_api_crud_and_duplicate_name(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    created = await client.post("/api/v1/external-contacts", json={
        "company_name": "Stadtwerke", "first_name": "Ina", "last_name": "Strom", "city": "Gartenstadt",
    }, headers=headers)
    assert created.status_code == 201, created.text
    contact_id = created.json()["id"]

    duplicate = await client.post("/api/v1/external-contacts", json={"first_name": "INA", "last_name": "strom"}, headers=headers)
    assert duplicate.status_code == 409
    company_only = await client.post("/api/v1/external-contacts", json={"company_name": "Bauhof"}, headers=headers)
    assert company_only.status_code == 201 and company_only.json()["first_name"] is None
    assert (await client.post("/api/v1/external-contacts", json={"company_name": "bauhof"}, headers=headers)).status_code == 409

    assert (await client.post(f"/api/v1/external-contacts/{contact_id}/phone_numbers", json={"number": "123"}, headers=headers)).status_code == 201
    assert (await client.post(f"/api/v1/external-contacts/{contact_id}/tags", json={"name": "Versorger"}, headers=headers)).status_code == 201

    updated = await client.put(f"/api/v1/external-contacts/{contact_id}", json={"city": "Neustadt"}, headers=headers)
    assert updated.status_code == 200
    body = updated.json()
    assert body["city"] == "Neustadt" and body["company_name"] == "Stadtwerke"
    assert [p["number"] for p in body["phone_numbers"]] == ["123"]
    assert [t["name"] for t in body["tags"]] == ["Versorger"]

    listed = await client.get("/api/v1/external-contacts?search=strom", headers=headers)
    assert [c["id"] for c in listed.json()] == [contact_id]

    assert (await client.delete(f"/api/v1/external-contacts/{contact_id}", headers=headers)).status_code == 204
    assert (await client.get(f"/api/v1/external-contacts/{contact_id}", headers=headers)).status_code == 404


async def test_incoming_invoice_links_to_contact(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    contact_id = await _create(client)

    form = await client.get("/finances/incoming-invoices")
    assert f'value="{contact_id}"' in form.text and 'data-sender="Gartenbau Müller GmbH"' in form.text

    response = await client.post("/finances/incoming-invoices", data={
        "sender": "Gartenbau Müller GmbH", "invoice_date": "2026-10-01", "external_contact_id": contact_id,
        "category_id": [""], "description": ["Mulch"], "amount": ["99.00"],
    })
    assert response.status_code in (302, 303)
    async with AsyncSessionLocal() as db:
        invoice = (await db.scalars(select(IncomingInvoice))).one()
    assert invoice.external_contact_id == contact_id

    detail = await client.get(f"/contacts/{contact_id}")
    assert f"/finances/incoming-invoices/{invoice.id}" in detail.text

    # A deleted contact drops out of the picker but stays on the invoice.
    await client.post(f"/contacts/{contact_id}/delete")
    assert f'value="{contact_id}"' not in (await client.get("/finances/incoming-invoices")).text
    invoice_page = await client.get(f"/finances/incoming-invoices/{invoice.id}")
    assert "Gartenbau Müller GmbH (Max Müller)" in invoice_page.text

    # ...and can't be newly picked any more.
    response = await client.post(f"/finances/incoming-invoices/{invoice.id}/contact", data={"external_contact_id": contact_id})
    assert response.status_code == 400


async def test_purchase_request_links_to_contact(client, admin_user):
    await web_login(client, "admin@example.com")
    contact_id = await _create(client)

    assert f'value="{contact_id}"' in (await client.get("/purchase-requests/new")).text
    response = await client.post("/purchase-requests/new", data={
        "title": "Rindenmulch", "justification": "Wege", "external_contact_id": contact_id,
    })
    assert response.status_code == 302
    async with AsyncSessionLocal() as db:
        pr = (await db.scalars(select(PurchaseRequest))).one()
    assert pr.external_contact_id == contact_id
    assert f"/purchase-requests/{pr.id}" in (await client.get(f"/contacts/{contact_id}")).text

    # Unlink from the detail page.
    assert (await client.post(f"/purchase-requests/{pr.id}/contact", data={"external_contact_id": ""})).status_code == 303
    async with AsyncSessionLocal() as db:
        assert (await db.get(PurchaseRequest, pr.id)).external_contact_id is None

    # API: an unknown contact is refused.
    headers = auth_header(await login(client, "admin@example.com"))
    response = await client.post("/api/v1/purchase-requests", json={
        "title": "X", "justification": "Y", "external_contact_id": "does-not-exist",
    }, headers=headers)
    assert response.status_code == 422
    response = await client.post("/api/v1/purchase-requests", json={
        "title": "X", "justification": "Y", "external_contact_id": contact_id,
    }, headers=headers)
    assert response.status_code == 201 and response.json()["external_contact_id"] == contact_id


# ---------------------------------------------------------------------------
# Documents in the cloud (ADR 0097)
# ---------------------------------------------------------------------------

class _FakeCloud:
    """Stands in for the cloud storage provider; records what was asked."""

    def __init__(self, files_by_path):
        self.files_by_path = files_by_path
        self.listed, self.uploaded, self.downloaded = [], [], []

    async def list_files(self, path):
        self.listed.append(path)
        return self.files_by_path.get(path, [])

    async def upload_file(self, path, filename, content):
        self.uploaded.append((path, filename, content))

    async def download_file(self, path, filename):
        self.downloaded.append((path, filename))
        return b"pdf bytes"

    async def aclose(self):
        pass


async def _setup_documents(client, monkeypatch, files_by_path):
    from app.cloud_storage import CloudFileEntry

    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_cloud_storage", value="true", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    saved = await client.post("/admin/integrations/nextcloud/external-contacts-folder", data={"relative_path": "/kgv_dokumente/extern/"})
    assert saved.status_code == 303
    cloud = _FakeCloud({
        path: [CloudFileEntry(name=name, is_directory=is_dir) for name, is_dir in entries]
        for path, entries in files_by_path.items()
    })

    async def fake_provider(db, client=None):
        return cloud

    monkeypatch.setattr("app.routers.external_contacts.get_nextcloud_provider", fake_provider)
    return cloud


async def test_documents_pick_folder_browse_upload_download(client, admin_user, monkeypatch):
    cloud = await _setup_documents(client, monkeypatch, {
        "kgv_dokumente/extern": [("Stadtwerke", True), ("Gartenbau Müller", True), ("readme.txt", False)],
        "kgv_dokumente/extern/Gartenbau Müller": [("Eingang", True), ("Angebot 2026.pdf", False)],
        "kgv_dokumente/extern/Gartenbau Müller/Eingang": [("Rechnung 42.pdf", False)],
    })
    contact_id = await _create(client)

    # No folder yet: the picker offers the subfolders of the base folder (no files).
    page = await client.get(f"/contacts/{contact_id}")
    assert '<option value="Gartenbau Müller"' in page.text and '<option value="Stadtwerke"' in page.text
    assert 'value="readme.txt"' not in page.text
    assert cloud.listed == ["kgv_dokumente/extern"]

    assert (await client.post(f"/contacts/{contact_id}/documents/folder", data={"folder_name": "Gartenbau Müller"})).status_code == 303
    page = await client.get(f"/contacts/{contact_id}")
    assert "Angebot 2026.pdf" in page.text and "Eingang" in page.text
    assert cloud.listed[-1] == "kgv_dokumente/extern/Gartenbau Müller"

    # Into a subfolder, upload there, download from there.
    page = await client.get(f"/contacts/{contact_id}?docs_path=Eingang")
    assert "Rechnung 42.pdf" in page.text
    upload = await client.post(
        f"/contacts/{contact_id}/documents/upload", data={"docs_path": "Eingang"},
        files={"file": ("C:\\Users\\x\\Brief.pdf", b"brief", "application/pdf")},
    )
    assert upload.status_code == 303 and "docs_path=Eingang" in upload.headers["location"]
    assert cloud.uploaded == [("kgv_dokumente/extern/Gartenbau Müller/Eingang", "Brief.pdf", b"brief")]

    download = await client.get(f"/contacts/{contact_id}/documents/download?filename=Rechnung%2042.pdf&docs_path=Eingang")
    assert download.status_code == 200 and download.content == b"pdf bytes"
    assert cloud.downloaded == [("kgv_dokumente/extern/Gartenbau Müller/Eingang", "Rechnung 42.pdf")]
    assert "\r" not in download.headers["content-disposition"]

    # Traversal out of the contact's folder goes nowhere.
    await client.get(f"/contacts/{contact_id}?docs_path=../Stadtwerke")
    assert cloud.listed[-1] == "kgv_dokumente/extern/Gartenbau Müller"
    assert (await client.post(f"/contacts/{contact_id}/documents/folder", data={"folder_name": "../x"})).status_code == 303
    async with AsyncSessionLocal() as db:
        assert (await db.get(ExternalContact, contact_id)).cloud_folder == "Gartenbau Müller"


async def test_documents_need_the_cloud_module_and_respect_permissions(client, admin_user, monkeypatch):
    await web_login(client, "admin@example.com")
    contact_id = await _create(client)
    # Module off: no card, routes 404.
    assert 'id="documents"' not in (await client.get(f"/contacts/{contact_id}")).text
    assert (await client.get(f"/contacts/{contact_id}/documents/download?filename=a.pdf")).status_code == 404

    await _setup_documents(client, monkeypatch, {"kgv_dokumente/extern": [("Firma", True)]})
    await client.post(f"/contacts/{contact_id}/documents/folder", data={"folder_name": "Firma"})

    async with AsyncSessionLocal() as db:
        user = User(email="reader@example.com", name="Reader",
                    password_hash=hash_password("testpasswort123"), role=UserRole.READONLY)
        group = Group(name="Contact readers")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="external_contacts", can_read=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()
    await web_login(client, "reader@example.com")
    page = await client.get(f"/contacts/{contact_id}")
    assert 'id="documents"' in page.text and "/documents/upload" not in page.text
    assert (await client.get(f"/contacts/{contact_id}/documents/download?filename=a.pdf")).status_code == 200
    assert (await client.post(f"/contacts/{contact_id}/documents/upload", files={"file": ("a.pdf", b"x")})).status_code == 403
    assert (await client.post(f"/contacts/{contact_id}/documents/folder", data={"folder_name": ""})).status_code == 403


async def test_list_search_covers_notes_and_links_name_and_organisation(client, admin_user):
    """A ticket number in a contact's notes finds it; the list shows the
    contact person before the organisation and links both to the detail
    page."""
    async with AsyncSessionLocal() as db:
        noted = ExternalContact(company_name="Notiz GmbH", first_name="Nora", last_name="Notiz", notes="Ticket #4711")
        db.add_all([noted, ExternalContact(company_name="Andere AG")])
        await db.commit()
        noted_id = noted.id
    await web_login(client, "admin@example.com")

    page = (await client.get("/contacts/?search=4711")).text
    assert "Notiz GmbH" in page and "Andere AG" not in page
    assert page.count(f'href="/contacts/{noted_id}?search=4711"') == 3  # name, organisation, eye button
    assert page.index("Notiz, Nora") < page.index("Notiz GmbH")
