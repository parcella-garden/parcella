"""
External contacts module: suppliers, craftsmen, authorities --
companies and the people there (docs/module-external-contacts.md, ADR
0096, ADR 0110). Focus: the uniqueness rule (person's name and company
name unique ignoring case, a deleted contact frees its name), people
under a company, merging companies, the separate tag pool, CSV
export/import round trip, and the links from incoming invoices and
purchase requests.
"""
import base64

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, ExternalContact, ExternalContactKind, ExternalContactTag, Group, GroupMembership, GroupModulePermission,
    IncomingInvoice, MemberTag, PurchaseRequest, User, UserRole,
)
from app.auth import hash_password
from tests.conftest import auth_header, login
from tests.test_detail_page_navigation import web_login


PERSON, COMPANY = ExternalContactKind.PERSON, ExternalContactKind.COMPANY


async def _contacts(kind=None):
    async with AsyncSessionLocal() as db:
        query = (
            select(ExternalContact)
            .options(
                selectinload(ExternalContact.phone_numbers),
                selectinload(ExternalContact.email_addresses),
                selectinload(ExternalContact.tags),
            )
            .order_by(ExternalContact.last_name)
        )
        if kind is not None:
            query = query.where(ExternalContact.kind == kind)
        return (await db.scalars(query)).all()


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
    [contact] = await _contacts(PERSON)
    assert contact.id == contact_id
    assert contact.organisation_name == "Gartenbau Müller GmbH" and contact.full_name == "Max Müller"
    assert contact.company_name is None and contact.city is None and contact.iban is None
    # The address came with a new company, so it's the company's.
    [company] = await _contacts(COMPANY)
    assert company.company_name == "Gartenbau Müller GmbH" and contact.company_id == company.id
    assert (company.city, company.iban) == ("Gartenstadt", "DE02120300000000202051")
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
    assert len(await _contacts(PERSON)) == 2
    assert [c.company_name for c in await _contacts(COMPANY)] == ["Gartenbau Müller GmbH"]  # not created either

    # Renaming the second contact onto the first one's name is refused too.
    erika = [c for c in await _contacts(PERSON) if c.first_name == "Erika"][0]
    response = await client.post(f"/contacts/{erika.id}/edit", data={"first_name": "Max", "last_name": "Müller"})
    assert response.status_code == 409

    # A deleted contact frees its name.
    assert (await client.post(f"/contacts/{first_id}/delete")).status_code == 302
    await _create(client, company_name="Ganz Andere AG", first_name="max", last_name="müller")
    assert sorted(c.organisation_name for c in await _contacts(PERSON)) == ["Ganz Andere AG", "Gartenbau Müller GmbH", "Gartenbau Müller GmbH"]
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
    assert "Firma;Gartenbau Müller GmbH;;;;;;Gartenstadt" in export.text  # the company's row...
    assert "Person;Gartenbau Müller GmbH;Max;Müller;" in export.text  # ...followed by its people
    csv_text = export.text + "Person;Neue Firma;Erika;Muster;;;;Hafenstadt;;e@example.org; 0170 1;Behörde;\n"
    csv_text = csv_text.replace("Gartenstadt", "Neustadt")
    preview = await client.post(
        "/contacts/import/preview", files={"file": ("contacts.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert preview.status_code == 200
    assert 'value="first_name" selected' in preview.text  # headers of our own export are recognised

    mapping = {f"map_{i}": field for i, field in enumerate([
        "kind", "company_name", "first_name", "last_name", "position", "street", "postal_code", "city",
        "iban", "email_addresses", "phone_numbers", "tags", "notes",
    ])}
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode("utf-8")).decode("ascii"), "delimiter": ";", **mapping,
    })
    assert response.status_code == 302

    contacts = {c.first_name: c for c in await _contacts(PERSON)}
    assert set(contacts) == {"Max", "Erika"}
    companies = {c.company_name: c for c in await _contacts(COMPANY)}
    assert set(companies) == {"Gartenbau Müller GmbH", "Neue Firma"}
    max_ = contacts["Max"]
    assert companies["Gartenbau Müller GmbH"].city == "Neustadt" and max_.city is None
    assert [p.number for p in max_.phone_numbers] == ["+49 30 123456"]  # apostrophe stripped, no duplicate
    assert [e.address for e in max_.email_addresses] == ["a@example.org"]
    assert [t.name for t in max_.tags] == ["Lieferant"]
    erika = contacts["Erika"]
    assert erika.company_id == companies["Neue Firma"].id and erika.city is None
    assert companies["Neue Firma"].city == "Hafenstadt"  # a new company takes the row's address
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

    # A company with people can't be deleted...
    response = await client.post(f"/contacts/{stadtwerke_id}/delete")
    assert response.status_code == 303 and "error=" in response.headers["location"]
    # ...once they're gone, deleting it frees the company name again.
    strom = next(c for c in contacts if c.last_name == "Strom")
    assert (await client.post(f"/contacts/{strom.id}/delete")).status_code == 302
    assert (await client.post(f"/contacts/{stadtwerke_id}/delete")).status_code == 302
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

    monkeypatch.setattr("app.routers.external_contacts.get_cloud_storage_provider", fake_provider)
    return cloud


async def test_documents_pick_folder_browse_upload_download(client, admin_user, monkeypatch):
    cloud = await _setup_documents(client, monkeypatch, {
        "kgv_dokumente/extern": [("Stadtwerke", True), ("Gartenbau Müller", True), ("readme.txt", False)],
        "kgv_dokumente/extern/Gartenbau Müller": [("Eingang", True), ("Angebot 2026.pdf", False)],
        "kgv_dokumente/extern/Gartenbau Müller/Eingang": [("Rechnung 42.pdf", False)],
    })
    contact_id = await _create(client, first_name="", last_name="")

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
    contact_id = await _create(client, first_name="", last_name="")
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


async def test_list_search_covers_notes_and_shows_the_person_under_its_company(client, admin_user):
    """A ticket number in a person's notes finds them; the list shows
    their company's row with the person highlighted beneath it."""
    async with AsyncSessionLocal() as db:
        company = ExternalContact(kind=COMPANY, company_name="Notiz GmbH")
        noted = ExternalContact(kind=PERSON, first_name="Nora", last_name="Notiz", notes="Ticket #4711", company=company)
        other = ExternalContact(kind=PERSON, first_name="Olaf", last_name="Other", company=company)
        db.add_all([company, noted, other, ExternalContact(kind=COMPANY, company_name="Andere AG")])
        await db.commit()
        company_id, noted_id = company.id, noted.id
    await web_login(client, "admin@example.com")

    page = (await client.get("/contacts/?search=4711")).text
    assert "Notiz GmbH" in page and "Andere AG" not in page
    assert page.count(f'href="/contacts/{noted_id}?search=4711"') == 2  # name, eye button
    assert page.count(f'href="/contacts/{company_id}?search=4711"') == 2
    assert page.index("Notiz GmbH") < page.index("Notiz, Nora")
    assert "Other, Olaf" in page  # the company's other people are listed too...
    assert page.count("table-active") == 1  # ...but only the match is highlighted


# ---------------------------------------------------------------------------
# Companies and their people (ADR 0110)
# ---------------------------------------------------------------------------

async def test_company_with_people_form_list_and_detail(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/contacts/new", data={
        "kind": "COMPANY", "company_name": "Stadtwerke", "first_name": "ignored", "city": "Gartenstadt",
        "phone": "0800 1",
    })
    assert response.status_code == 302
    company_id = response.headers["location"].rsplit("/", 1)[1]

    # "Add person" pre-fills the company.
    form = await client.get(f"/contacts/new?company_id={company_id}")
    assert 'value="Stadtwerke"' in form.text and 'value="PERSON" id="kind-person" autocomplete="off" checked' in form.text
    for first, last in (("Ina", "Strom"), ("Wolf", "Wasser")):
        response = await client.post("/contacts/new", data={
            "kind": "PERSON", "company_name": "stadtwerke", "first_name": first, "last_name": last, "position": "Vertrieb",
        })
        assert response.status_code == 302
    [company] = await _contacts(COMPANY)
    assert company.first_name is None  # a company has no person name
    people = await _contacts(PERSON)
    assert [p.company_id for p in people] == [company_id, company_id]

    page = (await client.get("/contacts/")).text
    assert page.index("Stadtwerke") < page.index("Strom, Ina") < page.index("Wasser, Wolf")

    detail = (await client.get(f"/contacts/{company_id}")).text
    assert "Strom" in detail and "Wasser" in detail and f"/contacts/new?company_id={company_id}" in detail
    person = (await client.get(f"/contacts/{people[0].id}")).text
    assert f'href="/contacts/{company_id}"' in person and "Gartenstadt" in person and "Vertrieb" in person

    # Moving a person to another company by name, which gets created.
    response = await client.post(f"/contacts/{people[0].id}/edit", data={
        "company_name": "Netzbetreiber", "first_name": "Ina", "last_name": "Strom",
    })
    assert response.status_code == 302
    async with AsyncSessionLocal() as db:
        moved = await db.get(ExternalContact, people[0].id)
        assert moved.organisation_name == "Netzbetreiber" and moved.position is None


async def test_merge_companies_moves_people_details_and_links(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    source_id = await _create(client, company_name="Commerzbank", first_name="", last_name="", city="Leipzig",
                              phone="0341 1", tags_present="1", new_tags="Bank")
    target_id = await _create(client, company_name="Commerzbank AG", first_name="", last_name="")
    person_id = await _create(client, company_name="Commerzbank", first_name="Kurt", last_name="Konto")
    response = await client.post("/purchase-requests/new", data={
        "title": "Tresor", "justification": "Kasse", "external_contact_id": source_id,
    })
    assert response.status_code == 302

    # The source's page offers the other company as a target.
    assert f'<option value="{target_id}">Commerzbank AG</option>' in (await client.get(f"/contacts/{source_id}")).text
    response = await client.post(f"/contacts/{source_id}/merge", data={"target_id": target_id})
    assert response.status_code == 303 and response.headers["location"].startswith(f"/contacts/{target_id}?")

    contacts = {c.id: c for c in await _contacts()}
    source, target = contacts[source_id], contacts[target_id]
    assert source.deleted_at is not None and not source.phone_numbers and not source.tags
    assert contacts[person_id].company_id == target_id
    assert target.city == "Leipzig" and [p.number for p in target.phone_numbers] == ["0341 1"]
    assert [t.name for t in target.tags] == ["Bank"]
    async with AsyncSessionLocal() as db:
        assert (await db.scalars(select(PurchaseRequest))).one().external_contact_id == target_id

    # Only companies merge, and not into themselves.
    response = await client.post(f"/contacts/{person_id}/merge", data={"target_id": target_id})
    assert response.status_code == 303 and "error=" in response.headers["location"]


async def test_merge_needs_the_delete_permission(client, admin_user):
    async with AsyncSessionLocal() as db:
        user = User(email="writer@example.com", name="Writer",
                    password_hash=hash_password("testpasswort123"), role=UserRole.READONLY)
        group = Group(name="Contacts writers")
        db.add_all([user, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="external_contacts", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        a = ExternalContact(kind=COMPANY, company_name="A")
        b = ExternalContact(kind=COMPANY, company_name="B")
        db.add_all([a, b])
        await db.commit()
        a_id, b_id = a.id, b.id
    await web_login(client, "writer@example.com")
    assert (await client.post(f"/contacts/{a_id}/merge", data={"target_id": b_id})).status_code == 403
    assert "/merge" not in (await client.get(f"/contacts/{a_id}")).text


async def test_csv_import_without_type_column_groups_people_under_one_company(client, admin_user):
    """An old-style file (one row = company + person + company address)
    ends up as one company with the address, and its people."""
    await web_login(client, "admin@example.com")
    csv_text = (
        "Firma;Vorname;Nachname;Strasse;Ort\n"
        "Handelshof;Hans;Hof;Markt 1;Bitterfeld\n"
        "HANDELSHOF;Heike;Hof;Markt 1;Bitterfeld\n"
        "Handelshof;Herbert;Hof;Lager 9;Bitterfeld\n"
    )
    response = await client.post("/contacts/import/finalize", data={
        "csv_content_b64": base64.b64encode(csv_text.encode()).decode(), "delimiter": ";",
        "map_0": "company_name", "map_1": "first_name", "map_2": "last_name", "map_3": "street", "map_4": "city",
    })
    assert response.status_code == 302
    [company] = await _contacts(COMPANY)
    assert (company.company_name, company.street, company.city) == ("Handelshof", "Markt 1", "Bitterfeld")
    people = {p.first_name: p for p in await _contacts(PERSON)}
    assert {p.company_id for p in people.values()} == {company.id}
    assert people["Hans"].street is None and people["Heike"].street is None
    assert people["Herbert"].street == "Lager 9"  # differs from the company's: kept on the person


async def test_picker_groups_people_under_their_company(client, admin_user):
    await web_login(client, "admin@example.com")
    person_id = await _create(client)
    company_id = (await _contacts(COMPANY))[0].id
    page = (await client.get("/purchase-requests/new")).text
    group = page[page.index('<optgroup label="Gartenbau Müller GmbH">'):page.index("</optgroup>")]
    assert f'value="{company_id}"' in group and f'value="{person_id}"' in group


async def test_rest_api_companies_and_people(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    company = await client.post("/api/v1/external-contacts", json={"kind": "COMPANY", "company_name": "Bauhof"}, headers=headers)
    assert company.status_code == 201 and company.json()["kind"] == "COMPANY"
    company_id = company.json()["id"]
    person = await client.post("/api/v1/external-contacts", json={
        "first_name": "Bea", "last_name": "Bagger", "company_id": company_id, "position": "Polier",
    }, headers=headers)
    assert person.status_code == 201, person.text
    body = person.json()
    assert (body["kind"], body["company_id"], body["company_name"], body["position"]) == ("PERSON", company_id, "Bauhof", "Polier")

    listed = await client.get(f"/api/v1/external-contacts?kind=PERSON&company_id={company_id}", headers=headers)
    assert [c["id"] for c in listed.json()] == [body["id"]]
    assert [c["id"] for c in (await client.get("/api/v1/external-contacts?kind=COMPANY", headers=headers)).json()] == [company_id]

    assert (await client.put(f"/api/v1/external-contacts/{body['id']}", json={"kind": "COMPANY"}, headers=headers)).status_code == 422
    assert (await client.post("/api/v1/external-contacts", json={"last_name": "X", "company_id": body["id"]}, headers=headers)).status_code == 404
    assert (await client.delete(f"/api/v1/external-contacts/{company_id}", headers=headers)).status_code == 409

    other = (await client.post("/api/v1/external-contacts", json={"company_name": "Bauhof GmbH"}, headers=headers)).json()
    merged = await client.post(f"/api/v1/external-contacts/{company_id}/merge-into/{other['id']}", headers=headers)
    assert merged.status_code == 200 and merged.json()["id"] == other["id"]
    moved = (await client.get(f"/api/v1/external-contacts/{body['id']}", headers=headers)).json()
    assert moved["company_id"] == other["id"] and moved["company_name"] == "Bauhof GmbH"
