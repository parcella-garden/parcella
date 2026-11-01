"""
Issue #266: /finances/runs works like the incoming invoices list (#265)
-- filterable by year, subject and status, and "New invoice run" is a
modal behind a topbar button (write permission only).
"""
from datetime import date

from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, Group, GroupMembership, GroupModulePermission, InvoiceRun, InvoiceRunStatus, User, UserRole,
)
from tests.test_incoming_invoices import web_login


async def _setup():
    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        for year, subject, status in (
            (2025, "Jahresrechnung 2025", InvoiceRunStatus.FINALIZED),
            (2026, "Jahresrechnung 2026", InvoiceRunStatus.DRAFT),
            (2026, "Wasser Nachzahlung", InvoiceRunStatus.DRAFT),
        ):
            session.add(InvoiceRun(
                year=year, subject=subject, status=status,
                issued_date=date(year, 1, 15), due_date=date(year, 2, 15),
            ))
        await session.commit()


async def test_run_list_filters(client, admin_user):
    await _setup()
    await web_login(client)

    def subjects(page):
        return [s for s in ("Jahresrechnung 2025", "Jahresrechnung 2026", "Wasser Nachzahlung") if s in page.text]

    assert subjects(await client.get("/finances/runs")) == ["Jahresrechnung 2025", "Jahresrechnung 2026", "Wasser Nachzahlung"]
    assert subjects(await client.get("/finances/runs?year=2026")) == ["Jahresrechnung 2026", "Wasser Nachzahlung"]
    assert subjects(await client.get("/finances/runs?subject=jahres")) == ["Jahresrechnung 2025", "Jahresrechnung 2026"]
    assert subjects(await client.get("/finances/runs?status=finalized")) == ["Jahresrechnung 2025"]
    assert subjects(await client.get("/finances/runs?year=2026&status=draft&subject=wasser")) == ["Wasser Nachzahlung"]
    # Garbage is ignored, not a 500.
    assert len(subjects(await client.get("/finances/runs?year=abc&status=bogus"))) == 3

    empty = await client.get("/finances/runs?year=1999")
    assert "No invoice runs match the filter." in empty.text


async def test_new_run_form_is_a_modal_for_writers_only(client, admin_user):
    await _setup()
    await web_login(client)
    page = (await client.get("/finances/runs")).text
    assert 'data-bs-target="#newRunModal"' in page
    modal = page[page.index('id="newRunModal"'):]
    assert 'action="/finances/runs"' in modal and 'name="due_date"' in modal

    created = await client.post("/finances/runs", data={
        "year": "2027", "subject": "Jahresrechnung 2027", "issued_date": "2027-01-10", "due_date": "2027-02-10",
    })
    assert created.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        user = User(
            email="reader@example.com", name="Reader",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        group = Group(name="Finance readers")
        session.add_all([user, group])
        await session.flush()
        session.add(GroupModulePermission(group_id=group.id, module="finances", can_read=True))
        session.add(GroupMembership(user_id=user.id, group_id=group.id))
        await session.commit()
    await client.get("/auth/logout")
    await web_login(client, "reader@example.com")
    page = await client.get("/finances/runs")
    assert page.status_code == 200
    assert "newRunModal" not in page.text
