"""
ADR 0100: nav badges for the dashboard's "needs attention" counts --
new applicants, open purchase requests, open support conversations and
overdue tasks. Badge and dashboard tile read the same per-request
counts (app/nav_counts.py), and a badge disappears once its item is
dealt with.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import update

from app.database import AsyncSessionLocal
from app.models import (
    Applicant, ApplicantStatus, ClubSetting, FreescoutConversationLink,
    PurchaseRequest, PurchaseRequestStatus, Task, TaskList,
)


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_nav_badges_show_counts_and_clear_when_dealt_with(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_freescout_bridge", value="true"))
        db.add_all([
            Applicant(email="new1@example.com"),
            Applicant(email="new2@example.com"),
            # Already being worked on -- no badge.
            Applicant(email="old@example.com", status=ApplicantStatus.CONTACTED),
            PurchaseRequest(title="Rasenmäher", justification="kaputt"),
            FreescoutConversationLink(
                freescout_conversation_id=1, freescout_mailbox_id=1, subject="Frage",
                customer_email="x@example.com", freescout_status="active",
                freescout_updated_at=datetime.now(timezone.utc),
            ),
            FreescoutConversationLink(
                freescout_conversation_id=2, freescout_mailbox_id=1, subject="Erledigt",
                customer_email="y@example.com", freescout_status="closed",
                freescout_updated_at=datetime.now(timezone.utc),
            ),
        ])
        task_list = TaskList(name="To do", position=0)
        db.add(task_list)
        await db.flush()
        db.add_all([
            Task(title="Overdue", list_id=task_list.id, position=0, due_date=date.today() - timedelta(days=1)),
            Task(title="Due later", list_id=task_list.id, position=1, due_date=date.today() + timedelta(days=3)),
        ])
        await db.commit()

    await web_login(client, "admin@example.com")
    page = await client.get("/")
    assert page.status_code == 200
    html = page.text

    assert "2 new application(s) not yet looked at" in html
    assert "1 purchase request(s) awaiting a decision" in html
    assert "1 open support conversation(s)" in html
    assert '<span class="badge rounded-pill bg-danger ms-1" title="1 overdue task(s)">1</span>' in html

    # Dealing with the items clears the badges.
    async with AsyncSessionLocal() as db:
        await db.execute(update(Applicant).values(status=ApplicantStatus.CONTACTED))
        await db.execute(update(PurchaseRequest).values(status=PurchaseRequestStatus.APPROVED))
        await db.commit()

    html = (await client.get("/")).text
    assert "application(s) not yet looked at" not in html
    assert "purchase request(s) awaiting a decision" not in html
