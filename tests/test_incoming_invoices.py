"""
Issue #178: recording bills the club received from a supplier/vendor
-- the mirror image of the outgoing Invoice model, but recorded
directly by hand (no generation/finalization phases) with one or more
categorized cost positions (IncomingInvoiceLineItem). The optional
attachment is never stored in this app's own database/filesystem --
only a filename referencing a spot in a single shared Nextcloud folder
(ClubSetting "incoming_invoices_cloud_folder"), same connection
ParcelCloudFolder already uses (app/cloud_storage.py).
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from tests.conftest import login, auth_header
from app.database import AsyncSessionLocal
from app.models import ClubSetting, FinanceCategory, FinanceCategoryGroup, IncomingInvoice, IncomingInvoiceLineItem


async def web_login(client, email: str = "admin@example.com", password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def _enable_finances_module():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()


async def _make_category(code="40100", title="Insurance", group=FinanceCategoryGroup.EXPENSE) -> str:
    async with AsyncSessionLocal() as session:
        category = FinanceCategory(code=code, title=title, group=group)
        session.add(category)
        await session.commit()
        return category.id


async def test_incoming_invoice_create_with_single_position(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_id = await _make_category()

    response = await client.post("/finances/incoming-invoices", data={
        "sender": "Gartenbau Müller GmbH", "invoice_number": "R-2026-042",
        "invoice_date": "2026-07-15", "note": "Annual liability insurance",
        "category_id": [category_id], "description": ["Annual premium 2026"], "amount": ["123.45"],
    })
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncomingInvoice)
            .options(selectinload(IncomingInvoice.line_items))
            .where(IncomingInvoice.sender == "Gartenbau Müller GmbH")
        )
        invoice = result.scalar_one()

    assert invoice.invoice_number == "R-2026-042"
    assert invoice.note == "Annual liability insurance"
    assert len(invoice.line_items) == 1
    assert float(invoice.line_items[0].amount) == 123.45
    assert invoice.line_items[0].category_id == category_id
    assert invoice.line_items[0].description == "Annual premium 2026"
    assert invoice.total_amount == 123.45


async def test_incoming_invoice_position_without_description_is_optional(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_id = await _make_category()

    response = await client.post("/finances/incoming-invoices", data={
        "sender": "No Description Ltd", "invoice_number": "", "invoice_date": "2026-07-01", "note": "",
        "category_id": [category_id], "amount": ["7.00"],
    })
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncomingInvoice)
            .options(selectinload(IncomingInvoice.line_items))
            .where(IncomingInvoice.sender == "No Description Ltd")
        )
        invoice = result.scalar_one()

    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].description is None
    assert float(invoice.line_items[0].amount) == 7.00


async def test_incoming_invoice_create_with_multiple_positions(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_a = await _make_category(code="40100", title="Insurance")
    category_b = await _make_category(code="40200", title="Maintenance")

    response = await client.post("/finances/incoming-invoices", data={
        "sender": "Multi Corp", "invoice_number": "", "invoice_date": "2026-07-20", "note": "",
        "category_id": [category_a, category_b],
        "description": ["Fire insurance renewal", "Lawnmower repair"],
        "amount": ["50.00", "75.50"],
    })
    assert response.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncomingInvoice)
            .options(selectinload(IncomingInvoice.line_items))
            .where(IncomingInvoice.sender == "Multi Corp")
        )
        invoice = result.scalar_one()

    descriptions = {li.description for li in invoice.line_items}
    assert descriptions == {"Fire insurance renewal", "Lawnmower repair"}

    assert len(invoice.line_items) == 2
    assert invoice.total_amount == 125.50


async def test_incoming_invoice_list_and_detail_pages_render(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_id = await _make_category()

    await client.post("/finances/incoming-invoices", data={
        "sender": "Test Sender AG", "invoice_number": "INV-1", "invoice_date": "2026-07-01", "note": "",
        "category_id": [category_id], "amount": ["10.00"],
    })

    r_list = await client.get("/finances/incoming-invoices")
    assert r_list.status_code == 200
    assert "UndefinedError" not in r_list.text
    assert "Test Sender AG" in r_list.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IncomingInvoice).where(IncomingInvoice.sender == "Test Sender AG"))
        invoice = result.scalar_one()

    r_detail = await client.get(f"/finances/incoming-invoices/{invoice.id}")
    assert r_detail.status_code == 200
    assert "UndefinedError" not in r_detail.text
    assert "Test Sender AG" in r_detail.text
    assert "INV-1" in r_detail.text


async def test_incoming_invoice_delete(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_id = await _make_category()

    await client.post("/finances/incoming-invoices", data={
        "sender": "Delete Me Inc", "invoice_number": "", "invoice_date": "2026-07-01", "note": "",
        "category_id": [category_id], "amount": ["1.00"],
    })

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IncomingInvoice).where(IncomingInvoice.sender == "Delete Me Inc"))
        invoice = result.scalar_one()

    r_delete = await client.post(f"/finances/incoming-invoices/{invoice.id}/delete")
    assert r_delete.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IncomingInvoice).where(IncomingInvoice.id == invoice.id))
        assert result.scalar_one_or_none() is None

        # Line items must be cascade-deleted with the parent invoice.
        li_result = await session.execute(
            select(IncomingInvoiceLineItem).where(IncomingInvoiceLineItem.incoming_invoice_id == invoice.id)
        )
        assert li_result.scalar_one_or_none() is None


async def test_deleting_category_keeps_line_item_but_clears_category(client, admin_user):
    await web_login(client)
    await _enable_finances_module()
    category_id = await _make_category()

    await client.post("/finances/incoming-invoices", data={
        "sender": "Category Test", "invoice_number": "", "invoice_date": "2026-07-01", "note": "",
        "category_id": [category_id], "amount": ["5.00"],
    })

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FinanceCategory).where(FinanceCategory.id == category_id))
        category = result.scalar_one()
        await session.delete(category)
        await session.commit()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncomingInvoiceLineItem).where(IncomingInvoiceLineItem.amount == 5.00)
        )
        line_item = result.scalar_one()
        assert line_item.category_id is None, "the line item itself must survive, only its category link is cleared"


async def test_incoming_invoice_upload_and_download_use_configured_folder(client, admin_user, monkeypatch):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.put("/api/v1/club-settings/modul_finances", json={"value": "true"}, headers=headers)
    await client.put("/api/v1/club-settings/modul_cloud_storage", json={"value": "true"}, headers=headers)

    await web_login(client, "admin@example.com")
    category_id = await _make_category()

    r_folder = await client.post(
        "/admin/integrations/nextcloud/incoming-invoices-folder", data={"relative_path": "buchhaltung/eingangsrechnungen"},
    )
    assert r_folder.status_code in (302, 303)
    assert "incoming_invoices_folder_saved" in r_folder.headers["location"]

    import httpx as httpx_module
    from app.cloud_storage import NextcloudProvider as RealNextcloudProvider
    from tests.test_cloud_storage import _nextcloud_mock_transport

    mock_client = httpx_module.AsyncClient(transport=_nextcloud_mock_transport(get_body=b"pdf bytes"))

    async def fake_get_nextcloud_provider(db, client=None):
        return RealNextcloudProvider(
            base_url="https://cloud.example.org", username="board", app_password="secret",
            client=mock_client,
        )

    monkeypatch.setattr("app.routers.finances.get_cloud_storage_provider", fake_get_nextcloud_provider)

    r_create = await client.post(
        "/finances/incoming-invoices",
        data={
            "sender": "Cloud Sender", "invoice_number": "", "invoice_date": "2026-07-01", "note": "",
            "category_id": [category_id], "amount": ["9.99"],
        },
        files={"file": ("bill.pdf", b"scanned bill bytes", "application/pdf")},
    )
    assert r_create.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(IncomingInvoice).where(IncomingInvoice.sender == "Cloud Sender"))
        invoice = result.scalar_one()

    assert invoice.cloud_filename == f"{invoice.id}_bill.pdf"

    r_download = await client.get(f"/finances/incoming-invoices/{invoice.id}/download")
    assert r_download.status_code == 200
    assert r_download.content == b"pdf bytes"
