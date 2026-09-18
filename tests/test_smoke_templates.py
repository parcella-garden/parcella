from tests.conftest import login, auth_header


async def test_smoke_parcels_pages_render_without_jinja_errors(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "ZZTEST1"}, headers=headers)).json()
    member = (await client.post("/api/v1/members", json={"first_name": "Smoke", "last_name": "Test"}, headers=headers)).json()

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_list = await client.get("/parcels/", params={"search": "ZZTEST"})
    assert r_list.status_code == 200
    assert "ZZTEST1" in r_list.text
    assert "UndefinedError" not in r_list.text

    r_detail = await client.get(f"/parcels/{parcel['id']}")
    assert r_detail.status_code == 200
    assert "UndefinedError" not in r_detail.text

    r_assign = await client.post(
        f"/parcels/{parcel['id']}/member/assign",
        data={"member_id": member["id"], "assigned_from": ""},
    )
    assert r_assign.status_code in (302, 303)

    r_detail2 = await client.get(f"/parcels/{parcel['id']}")
    assert r_detail2.status_code == 200
    assert "Smoke Test" in r_detail2.text
    assert "UndefinedError" not in r_detail2.text

    assignment_id = None
    r_edit_page = None
    import re
    m = re.search(r'/parcels/[a-f0-9-]+/member/([a-f0-9-]+)/edit', r_detail2.text)
    assert m, "no edit link found in detail page"
    assignment_id = m.group(1)

    r_edit_page = await client.get(f"/parcels/{parcel['id']}/member/{assignment_id}/edit")
    assert r_edit_page.status_code == 200
    assert "UndefinedError" not in r_edit_page.text

    r_dup = await client.post("/parcels/new", data={"plot_number": "ZZTEST1"})
    assert r_dup.status_code == 400
    assert "UndefinedError" not in r_dup.text
    assert "already exists" in r_dup.text or "existiert" in r_dup.text


async def test_smoke_members_pages_render_without_jinja_errors(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "ZZSearchTest"}, headers=headers
    )).json()
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "ZZM1"}, headers=headers)).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_list = await client.get("/members/", params={"search": "ZZSearchTest"})
    assert r_list.status_code == 200
    assert "ZZSearchTest" in r_list.text
    assert "UndefinedError" not in r_list.text

    r_list_inactive = await client.get("/members/", params={"search": "ZZSearchTest", "include_inactive": "true"})
    assert r_list_inactive.status_code == 200
    assert "UndefinedError" not in r_list_inactive.text

    r_no_results = await client.get("/members/", params={"search": "NoSuchMemberXYZ"})
    assert r_no_results.status_code == 200
    assert "NoSuchMemberXYZ" in r_no_results.text
    assert "UndefinedError" not in r_no_results.text

    r_detail = await client.get(f"/members/{member['id']}")
    assert r_detail.status_code == 200
    assert "ZZM1" in r_detail.text
    assert "UndefinedError" not in r_detail.text


async def test_smoke_dashboard_renders_without_jinja_errors(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.post("/api/v1/members", json={"first_name": "Dash", "last_name": "Board"}, headers=headers)
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "ZZD1"}, headers=headers)).json()

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r = await client.get("/")
    assert r.status_code == 200
    assert "UndefinedError" not in r.text
    assert "Dash Board" in r.text


async def test_smoke_admin_pages_render_without_jinja_errors(client, admin_user):
    """
    Deliberately doesn't hit /admin/updates/check-now: that route makes
    a real GitHub API call (see app/update_check.py), and tests here
    follow the project convention of not depending on live external
    calls in the test suite (see test_update_check.py). Rendering
    /admin/system with the default "nothing cached yet" update_status
    is covered here instead.
    """
    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_root_redirect = await client.get("/admin/", follow_redirects=False)
    assert r_root_redirect.status_code == 302
    assert r_root_redirect.headers["location"] == "/admin/users/"

    r_dashboard = await client.get("/admin/users/")
    assert r_dashboard.status_code == 200
    assert "UndefinedError" not in r_dashboard.text

    r_system = await client.get("/admin/system")
    assert r_system.status_code == 200
    assert "UndefinedError" not in r_system.text

    r_settings = await client.get("/admin/settings")
    assert r_settings.status_code == 200
    assert "UndefinedError" not in r_settings.text


async def test_smoke_sample_data_page_add_and_remove_cycle(client, admin_user):
    # add_sample_data() seeds task-board cards into the "To Do"/"In
    # Progress"/"Done" lists by name -- normally seeded by migration
    # 0054_task_lists, but the test DB is built via create_all (see
    # tests/conftest.py), not Alembic, so tests seed them manually.
    from app.database import AsyncSessionLocal
    from app.models import TaskList

    async with AsyncSessionLocal() as session:
        for position, name in enumerate(["To Do", "In Progress", "Done"]):
            session.add(TaskList(name=name, position=position))
        await session.commit()

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_fresh = await client.get("/admin/sample-data")
    assert r_fresh.status_code == 200
    assert "UndefinedError" not in r_fresh.text

    r_add = await client.post("/admin/sample-data/add")
    assert r_add.status_code in (302, 303)

    r_after_add = await client.get("/admin/sample-data")
    assert r_after_add.status_code == 200
    assert "UndefinedError" not in r_after_add.text
    assert "DEMO-01" not in r_after_add.text  # page shows counts, not raw sample rows

    r_remove = await client.post("/admin/sample-data/remove")
    assert r_remove.status_code in (302, 303)

    r_after_remove = await client.get("/admin/sample-data")
    assert r_after_remove.status_code == 200
    assert "UndefinedError" not in r_after_remove.text


async def test_smoke_finances_pages_render_without_jinja_errors(client, admin_user):
    """Finances (issue #55/#56) defaults to off, like cloud_storage/
    announcements -- enable it directly via ClubSetting, same pattern
    test_announcements.py uses."""
    from app.database import AsyncSessionLocal
    from app.models import ClubSetting

    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        await session.commit()

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_dashboard = await client.get("/finances/")
    assert r_dashboard.status_code == 200
    assert "UndefinedError" not in r_dashboard.text

    r_list = await client.get("/finances/runs")
    assert r_list.status_code == 200
    assert "UndefinedError" not in r_list.text

    r_reminders = await client.get("/finances/reminders")
    assert r_reminders.status_code == 200
    assert "UndefinedError" not in r_reminders.text

    r_incoming = await client.get("/finances/incoming-invoices")
    assert r_incoming.status_code == 200
    assert "UndefinedError" not in r_incoming.text

    r_create = await client.post("/finances/runs", data={
        "year": "2026", "subject": "Test run", "issued_date": "2026-08-01",
        "due_date": "2026-09-01", "footer_text": "",
    })
    assert r_create.status_code in (302, 303)
    run_id = r_create.headers["location"].rstrip("/").split("/")[-1]

    r_detail = await client.get(f"/finances/runs/{run_id}")
    assert r_detail.status_code == 200
    assert "UndefinedError" not in r_detail.text

    for mode, unit_price in [
        ("fixed_per_parcel", "12.50"), ("fixed_per_person", "5.00"), ("per_sqm", "0.30"),
        ("water_usage", "3.10"), ("electricity_usage", "0.40"), ("insurance_cost", ""),
    ]:
        r_item = await client.post(f"/finances/runs/{run_id}/items", data={
            "order_number": "10", "name": f"Item {mode}", "description": "",
            "pricing_mode": mode, "unit_price": unit_price, "applies_to_all_parcels": "on",
        })
        assert r_item.status_code in (302, 303)

    r_detail2 = await client.get(f"/finances/runs/{run_id}")
    assert r_detail2.status_code == 200
    assert "UndefinedError" not in r_detail2.text
    assert "Item insurance_cost" in r_detail2.text

    # Preview and finalize (phase 2, issue #57). A real parcel+member
    # with is_invoice_address so the fixed_per_parcel item actually
    # produces a computed/finalized invoice, not just an empty run.
    from app.models import Member, Parcel, MemberParcel

    async with AsyncSessionLocal() as session:
        member = Member(first_name="Preview", last_name="Tester", street="Test-Str 1", postal_code="12345", city="Testort")
        parcel = Parcel(plot_number="SMOKE-01", area_sqm=100)
        session.add_all([member, parcel])
        await session.flush()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id))
        await session.commit()

    r_preview = await client.get(f"/finances/runs/{run_id}/preview")
    assert r_preview.status_code == 200
    assert "UndefinedError" not in r_preview.text
    assert "SMOKE-01" in r_preview.text

    r_finalize = await client.post(f"/finances/runs/{run_id}/finalize")
    assert r_finalize.status_code in (302, 303)

    r_detail3 = await client.get(f"/finances/runs/{run_id}")
    assert r_detail3.status_code == 200
    assert "UndefinedError" not in r_detail3.text
    assert "2026/" in r_detail3.text

    # Can no longer add items to a finalized run.
    r_blocked = await client.post(f"/finances/runs/{run_id}/items", data={
        "order_number": "99", "name": "Too late", "pricing_mode": "fixed_per_parcel",
        "unit_price": "1.00", "applies_to_all_parcels": "on",
    })
    assert r_blocked.status_code == 400

    # Re-using items in another year (issue #66): a finalized run's
    # item definitions stay attached to it, so a new draft run can
    # pick from a curated item catalog instead of retyping everything
    # (replaces the old "copy items from another run" mechanism).
    r_second_run = await client.post("/finances/runs", data={
        "year": "2027", "subject": "Second run", "issued_date": "2027-08-01",
        "due_date": "2027-09-01", "footer_text": "",
    })
    second_run_id = r_second_run.headers["location"].rstrip("/").split("/")[-1]

    r_templates_empty = await client.get("/finances/item-templates")
    assert r_templates_empty.status_code == 200
    assert "UndefinedError" not in r_templates_empty.text

    r_template_create = await client.post("/finances/item-templates", data={
        "order_number": "10", "name": "Catalog fee", "description": "",
        "pricing_mode": "fixed_per_parcel", "unit_price": "9.90",
    })
    assert r_template_create.status_code in (302, 303)
    assert "error" not in r_template_create.headers["location"]

    r_templates = await client.get("/finances/item-templates")
    assert r_templates.status_code == 200
    assert "Catalog fee" in r_templates.text

    from sqlalchemy import select as sa_select
    from app.models import InvoiceItemTemplate

    async with AsyncSessionLocal() as session:
        result = await session.execute(sa_select(InvoiceItemTemplate).where(InvoiceItemTemplate.name == "Catalog fee"))
        template = result.scalars().first()

    r_apply = await client.post(
        f"/finances/runs/{second_run_id}/items/add-from-catalog", data={"template_ids": [template.id]},
    )
    assert r_apply.status_code in (302, 303)

    r_second_detail = await client.get(f"/finances/runs/{second_run_id}")
    assert r_second_detail.status_code == 200
    assert "UndefinedError" not in r_second_detail.text
    assert "Catalog fee" in r_second_detail.text

    # Bookkeeping categories (issue #67): CRUD, CSV import, and the
    # item-form picker.
    r_categories = await client.get("/finances/categories")
    assert r_categories.status_code == 200
    assert "UndefinedError" not in r_categories.text

    r_cat_create = await client.post("/finances/categories", data={
        "code": "40000", "title": "Membership fees", "group": "INCOME",
    })
    assert r_cat_create.status_code in (302, 303)
    assert "error" not in r_cat_create.headers["location"]

    r_cat_invalid = await client.post("/finances/categories", data={
        "code": "not5digits", "title": "Bad", "group": "INCOME",
    })
    assert "invoice_number_format_error" not in r_cat_invalid.headers["location"]
    assert "error=" in r_cat_invalid.headers["location"]

    csv_content = "code,title,group\n60020,Ehrenamtspauschale,EXPENSE\n40000,Duplicate skip,income\n"
    r_import = await client.post(
        "/finances/categories/import",
        files={"file": ("categories.csv", csv_content, "text/csv")},
    )
    assert r_import.status_code in (302, 303)
    assert "imported=1" in r_import.headers["location"]
    assert "skipped=1" in r_import.headers["location"]

    r_categories2 = await client.get("/finances/categories")
    assert "UndefinedError" not in r_categories2.text
    assert "40000" in r_categories2.text
    assert "60020" in r_categories2.text

    r_third_run = await client.get(f"/finances/runs/{second_run_id}")
    assert "40000" in r_third_run.text and "Membership fees" in r_third_run.text

    # Global starting-number override, sourced from the ClubSetting a
    # user edits on /admin/settings (not a per-run field): always
    # available, not just when the year has zero invoices -- checked
    # for collisions at finalize time, and auto-cleared once consumed
    # so it doesn't keep forcing every later run back to the same number.
    from app.models import ClubSetting
    from sqlalchemy import select as sa_select

    async def _set_invoice_number_start(value):
        async with AsyncSessionLocal() as session:
            result = await session.execute(sa_select(ClubSetting).where(ClubSetting.key == "invoice_number_start"))
            entry = result.scalar_one_or_none()
            if entry is None:
                session.add(ClubSetting(key="invoice_number_start", value=value, description="test"))
            else:
                entry.value = value
            await session.commit()

    await _set_invoice_number_start("500")
    r_override_run = await client.post("/finances/runs", data={
        "year": "2028", "subject": "Override test", "issued_date": "2028-08-01",
        "due_date": "2028-09-01", "footer_text": "",
    })
    override_run_id = r_override_run.headers["location"].rstrip("/").split("/")[-1]

    await client.post(f"/finances/runs/{override_run_id}/items", data={
        "order_number": "10", "name": "Override fee", "pricing_mode": "fixed_per_parcel",
        "unit_price": "1.00", "applies_to_all_parcels": "on",
    })
    r_override_finalize = await client.post(f"/finances/runs/{override_run_id}/finalize")
    assert r_override_finalize.status_code in (302, 303)
    assert "error" not in r_override_finalize.headers["location"]

    r_override_detail = await client.get(f"/finances/runs/{override_run_id}")
    assert "2028/500" in r_override_detail.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(sa_select(ClubSetting).where(ClubSetting.key == "invoice_number_start"))
        assert result.scalar_one().value == ""

    # A second run in the same year, re-setting the override to the
    # number just used, collides.
    await _set_invoice_number_start("500")
    r_collide_run = await client.post("/finances/runs", data={
        "year": "2028", "subject": "Collision test", "issued_date": "2028-08-01",
        "due_date": "2028-09-01", "footer_text": "",
    })
    collide_run_id = r_collide_run.headers["location"].rstrip("/").split("/")[-1]
    await client.post(f"/finances/runs/{collide_run_id}/items", data={
        "order_number": "10", "name": "Fee", "pricing_mode": "fixed_per_parcel",
        "unit_price": "1.00", "applies_to_all_parcels": "on",
    })
    r_collide_finalize = await client.post(f"/finances/runs/{collide_run_id}/finalize")
    assert "error=" in r_collide_finalize.headers["location"]

    # Setting it to a free number lets it finalize; with no override
    # set at all, a later run just continues naturally from there.
    await _set_invoice_number_start("600")
    r_collide_retry = await client.post(f"/finances/runs/{collide_run_id}/finalize")
    assert "error" not in r_collide_retry.headers["location"]

    r_natural_run = await client.post("/finances/runs", data={
        "year": "2028", "subject": "Natural continuation", "issued_date": "2028-08-01",
        "due_date": "2028-09-01", "footer_text": "",
    })
    natural_run_id = r_natural_run.headers["location"].rstrip("/").split("/")[-1]
    await client.post(f"/finances/runs/{natural_run_id}/items", data={
        "order_number": "10", "name": "Fee", "pricing_mode": "fixed_per_parcel",
        "unit_price": "1.00", "applies_to_all_parcels": "on",
    })
    r_natural_finalize = await client.post(f"/finances/runs/{natural_run_id}/finalize")
    assert "error" not in r_natural_finalize.headers["location"]
    r_natural_detail = await client.get(f"/finances/runs/{natural_run_id}")
    assert "2028/601" in r_natural_detail.text

    # Delivery + payments (phase 3, issue #58). The SMOKE-01 member has
    # no stored email, so deliver() should email nobody and the print
    # bundle should include this invoice instead.
    from app.models import Invoice
    from sqlalchemy import select as sa_select

    async with AsyncSessionLocal() as session:
        result = await session.execute(sa_select(Invoice).where(Invoice.invoice_run_id == run_id))
        invoice = result.scalars().first()
    invoice_id = invoice.id

    r_deliver = await client.post(f"/finances/runs/{run_id}/deliver")
    assert r_deliver.status_code in (302, 303)
    assert "emailed=0" in r_deliver.headers["location"]

    r_bundle = await client.get(f"/finances/runs/{run_id}/print-bundle")
    assert r_bundle.status_code == 200
    assert r_bundle.headers["content-type"] == "application/pdf"

    r_inv_list = await client.get("/finances/invoices")
    assert r_inv_list.status_code == 200
    assert "UndefinedError" not in r_inv_list.text
    assert "SMOKE-01" in r_inv_list.text

    r_inv_detail = await client.get(f"/finances/invoices/{invoice_id}")
    assert r_inv_detail.status_code == 200
    assert "UndefinedError" not in r_inv_detail.text

    r_payment = await client.post(f"/finances/invoices/{invoice_id}/payments", data={
        "amount": "1.00", "paid_on": "2026-08-15", "note": "smoke test payment",
    })
    assert r_payment.status_code in (302, 303)

    r_inv_detail2 = await client.get(f"/finances/invoices/{invoice_id}")
    assert r_inv_detail2.status_code == 200
    assert "UndefinedError" not in r_inv_detail2.text

    # Issue #175/#176/#177: the invoice detail page no longer shows a
    # Payments card -- payments are recorded/displayed from the run
    # page instead (#173).
    r_run_detail_after_payment = await client.get(f"/finances/runs/{run_id}")
    assert r_run_detail_after_payment.status_code == 200
    assert "UndefinedError" not in r_run_detail_after_payment.text
    assert "smoke test payment" in r_run_detail_after_payment.text

    # Reminders (issue #59): sending one adds an optional, custom fee
    # that actually counts toward what "paid" requires. Delivery
    # mirrors the invoice's own recipient resolution -- SMOKE-01's
    # member has no stored email, so this always resolves to "print".
    from sqlalchemy.orm import selectinload as sa_selectinload

    r_reminder_send = await client.post(f"/finances/invoices/{invoice_id}/reminders", data={
        "fee_amount": "5.00", "message": "Please pay soon.",
    })
    assert r_reminder_send.status_code in (302, 303)
    assert "error" not in r_reminder_send.headers["location"]

    r_inv_detail3 = await client.get(f"/finances/invoices/{invoice_id}")
    assert r_inv_detail3.status_code == 200
    assert "UndefinedError" not in r_inv_detail3.text
    assert "Reminder #1" in r_inv_detail3.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sa_select(Invoice).where(Invoice.id == invoice_id)
            .options(sa_selectinload(Invoice.reminders), sa_selectinload(Invoice.payments))
        )
        invoice_after_reminder = result.scalar_one()
        assert len(invoice_after_reminder.reminders) == 1
        first_reminder = invoice_after_reminder.reminders[0]
        assert first_reminder.level == 1
        assert first_reminder.delivery_method == "print"
        assert float(first_reminder.fee_amount) == 5.00
        subtotal_before_fee = float(invoice_after_reminder.subtotal)
        # The 5.00 fee now counts toward what "paid" requires.
        assert invoice_after_reminder.total_owed == subtotal_before_fee + 5.00
        assert invoice_after_reminder.payment_status == "partially_paid"

    r_reminder_pdf = await client.get(f"/finances/reminders/{first_reminder.id}/pdf")
    assert r_reminder_pdf.status_code == 200
    assert r_reminder_pdf.headers["content-type"] == "application/pdf"

    # A second reminder, no fee this time -- level increments, and the
    # first reminder's fee still counts (it doesn't reset/disappear).
    r_reminder_send2 = await client.post(f"/finances/invoices/{invoice_id}/reminders", data={
        "fee_amount": "", "message": "",
    })
    assert r_reminder_send2.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sa_select(Invoice).where(Invoice.id == invoice_id).options(sa_selectinload(Invoice.reminders))
        )
        invoice_after_second = result.scalar_one()
        assert len(invoice_after_second.reminders) == 2
        levels = sorted(r.level for r in invoice_after_second.reminders)
        assert levels == [1, 2]
        assert invoice_after_second.reminder_fees_total == 5.00

    # Paying the rest (subtotal + fee - the 1.00 already paid) settles it.
    remaining = subtotal_before_fee + 5.00 - 1.00
    r_final_payment = await client.post(f"/finances/invoices/{invoice_id}/payments", data={
        "amount": f"{remaining:.2f}", "paid_on": "2026-08-20", "note": "settles including reminder fee",
    })
    assert r_final_payment.status_code in (302, 303)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sa_select(Invoice).where(Invoice.id == invoice_id)
            .options(sa_selectinload(Invoice.reminders), sa_selectinload(Invoice.payments))
        )
        invoice_final = result.scalar_one()
        assert invoice_final.payment_status == "paid"
        assert invoice_final.amount_due == 0.0

    # Reminders overview (the "don't let it get forgotten" page):
    # a separate run with a due date safely in the past, so it shows
    # up regardless of what today happens to be when this test runs.
    r_overdue_run = await client.post("/finances/runs", data={
        "year": "2020", "subject": "Overdue test run", "issued_date": "2020-01-01",
        "due_date": "2020-02-01", "footer_text": "",
    })
    overdue_run_id = r_overdue_run.headers["location"].rstrip("/").split("/")[-1]
    await client.post(f"/finances/runs/{overdue_run_id}/items", data={
        "order_number": "10", "name": "Overdue fee", "pricing_mode": "fixed_per_parcel",
        "unit_price": "9.00", "applies_to_all_parcels": "on",
    })
    r_overdue_finalize = await client.post(f"/finances/runs/{overdue_run_id}/finalize")
    assert r_overdue_finalize.status_code in (302, 303)

    r_reminders_list = await client.get("/finances/reminders")
    assert r_reminders_list.status_code == 200
    assert "UndefinedError" not in r_reminders_list.text
    assert "SMOKE-01" in r_reminders_list.text
    assert "Overdue test run" not in r_reminders_list.text  # subject isn't shown, invoice number is
    assert "2020/" in r_reminders_list.text

    # Regression guard: dashboard and the (unfiltered + status-filtered)
    # invoice list both compute payment_status -- which now touches
    # Invoice.reminders -- for every invoice, including ones that
    # actually have reminders by this point in the test. A route that
    # doesn't eager-load .reminders 500s here (MissingGreenlet from a
    # lazy-load outside the request's async context) even though it
    # looks fine with zero reminders, which this test's earlier,
    # reminder-free calls to these same routes wouldn't have caught.
    r_dashboard2 = await client.get("/finances/")
    assert r_dashboard2.status_code == 200
    assert "UndefinedError" not in r_dashboard2.text

    r_inv_list2 = await client.get("/finances/invoices")
    assert r_inv_list2.status_code == 200
    assert "UndefinedError" not in r_inv_list2.text

    r_inv_list_filtered = await client.get("/finances/invoices?status=partially_paid")
    assert r_inv_list_filtered.status_code == 200
    assert "UndefinedError" not in r_inv_list_filtered.text


async def test_smoke_metering_pages_render_without_jinja_errors(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "ZZW1"}, headers=headers)).json()

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_overview = await client.get("/water/")
    assert r_overview.status_code == 200
    assert "UndefinedError" not in r_overview.text

    r_points_list = await client.get("/water/metering-points")
    assert r_points_list.status_code == 200
    assert "UndefinedError" not in r_points_list.text

    # Overview stat tile filters (issue #224).
    r_type_filter = await client.get("/water/metering-points", params={"type": "PARCEL"})
    assert r_type_filter.status_code == 200
    assert "UndefinedError" not in r_type_filter.text

    r_missing_filter = await client.get("/water/metering-points", params={"missing": "1"})
    assert r_missing_filter.status_code == 200
    assert "UndefinedError" not in r_missing_filter.text
    assert "ZZW1" in r_missing_filter.text

    r_new_page = await client.get("/water/metering-points/new")
    assert r_new_page.status_code == 200
    assert "UndefinedError" not in r_new_page.text

    r_create = await client.post(
        "/water/metering-points/new",
        data={"type": "PARCEL", "parcel_id": parcel["id"], "number": "WSM-1", "initial_reading": "0"},
    )
    assert r_create.status_code in (302, 303)
    location = r_create.headers["location"]
    point_id = location.rstrip("/").rsplit("/", 1)[-1]

    r_detail = await client.get(f"/water/metering-points/{point_id}")
    assert r_detail.status_code == 200
    assert "UndefinedError" not in r_detail.text
    assert "WSM-1" in r_detail.text

    r_reading = await client.post(
        f"/water/metering-points/{point_id}/readings/new",
        data={"year": "2026", "date": "2026-10-01", "reading": "42.0"},
    )
    assert r_reading.status_code in (302, 303)

    r_detail2 = await client.get(f"/water/metering-points/{point_id}")
    assert r_detail2.status_code == 200
    assert "UndefinedError" not in r_detail2.text

    r_readings_list = await client.get("/water/readings", params={"year": "2026"})
    assert r_readings_list.status_code == 200
    assert "UndefinedError" not in r_readings_list.text
    assert "WSM-1" in r_readings_list.text

    r_evaluation = await client.get("/water/evaluation", params={"year": "2026"})
    assert r_evaluation.status_code == 200
    assert "UndefinedError" not in r_evaluation.text

    r_evaluation_csv = await client.get("/water/evaluation/csv", params={"year": "2026"})
    assert r_evaluation_csv.status_code == 200

    r_exchange = await client.post(
        f"/water/metering-points/{point_id}/meter/exchange",
        data={"new_number": "WSM-2", "removed_at": "2026-10-02", "installed_at": "2026-10-02", "initial_reading": "0"},
    )
    assert r_exchange.status_code in (302, 303)

    r_detail3 = await client.get(f"/water/metering-points/{point_id}")
    assert r_detail3.status_code == 200
    assert "UndefinedError" not in r_detail3.text
    assert "WSM-2" in r_detail3.text


async def test_smoke_work_hours_pages_render_without_jinja_errors(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Wanda", "last_name": "Worker"}, headers=headers
    )).json()
    parcel = (await client.post("/api/v1/parcels", json={"plot_number": "ZZWH1"}, headers=headers)).json()
    await client.post(
        f"/api/v1/parcels/{parcel['id']}/assignments",
        json={"member_id": member["id"], "parcel_id": parcel["id"]},
        headers=headers,
    )

    response = await client.post("/auth/login", data={"email": "admin@example.com", "password": "testpasswort123"})
    assert response.status_code in (302, 303)

    r_config_new = await client.post(
        "/work-hours/configuration/new",
        data={"year": "2026", "hours_required": "5", "rate_per_hour_eur": "25", "mode": "PER_PARCEL"},
    )
    assert r_config_new.status_code in (302, 303)

    r_config_page = await client.get("/work-hours/configuration")
    assert r_config_page.status_code == 200
    assert "UndefinedError" not in r_config_page.text

    r_overview = await client.get("/work-hours/", params={"year": "2026"})
    assert r_overview.status_code == 200
    assert "UndefinedError" not in r_overview.text

    r_session_new_page = await client.get("/work-hours/sessions/new")
    assert r_session_new_page.status_code == 200
    assert "UndefinedError" not in r_session_new_page.text

    r_session_create = await client.post(
        "/work-hours/sessions/new",
        data={"title": "Spring Cleanup", "type": "STANDARD", "date": "2026-04-01"},
    )
    assert r_session_create.status_code in (302, 303)
    session_id = r_session_create.headers["location"].rstrip("/").rsplit("/", 1)[-1]

    r_session_detail = await client.get(f"/work-hours/sessions/{session_id}")
    assert r_session_detail.status_code == 200
    assert "UndefinedError" not in r_session_detail.text
    assert "Wanda Worker" in r_session_detail.text

    r_participant_add = await client.post(
        f"/work-hours/sessions/{session_id}/participants/add",
        data={"member_id": member["id"], "status": "ATTENDED", "hours_completed": "3"},
    )
    assert r_participant_add.status_code in (302, 303)

    r_session_detail2 = await client.get(f"/work-hours/sessions/{session_id}")
    assert r_session_detail2.status_code == 200
    assert "UndefinedError" not in r_session_detail2.text

    r_evaluation = await client.get("/work-hours/evaluation", params={"year": "2026"})
    assert r_evaluation.status_code == 200
    assert "UndefinedError" not in r_evaluation.text
    assert "ZZWH1" in r_evaluation.text

    r_evaluation_csv = await client.get("/work-hours/evaluation/csv", params={"year": "2026"})
    assert r_evaluation_csv.status_code == 200

    r_club_roles_page = await client.get("/work-hours/club-roles", params={"year": "2026"})
    assert r_club_roles_page.status_code == 200
    assert "UndefinedError" not in r_club_roles_page.text

    r_role_create = await client.post(
        "/work-hours/club-roles/new",
        data={"name": "Board Chair", "hours_exempt": "true", "exemption_reason": "BOARD"},
    )
    assert r_role_create.status_code in (302, 303)

    r_club_roles_page2 = await client.get("/work-hours/club-roles", params={"year": "2026"})
    assert r_club_roles_page2.status_code == 200
    assert "Board Chair" in r_club_roles_page2.text
    assert "UndefinedError" not in r_club_roles_page2.text

    r_sponsorships_page = await client.get("/work-hours/sponsorships", params={"year": "2026"})
    assert r_sponsorships_page.status_code == 200
    assert "UndefinedError" not in r_sponsorships_page.text

    r_sponsorship_create = await client.post(
        "/work-hours/sponsorships/new",
        data={"member_id": member["id"], "area": "Playground", "credited_hours": "5", "valid_from": "2026-01-01"},
    )
    assert r_sponsorship_create.status_code in (302, 303)

    r_sponsorships_page2 = await client.get("/work-hours/sponsorships", params={"year": "2026"})
    assert r_sponsorships_page2.status_code == 200
    assert "Playground" in r_sponsorships_page2.text
    assert "UndefinedError" not in r_sponsorships_page2.text

    r_tasks_page = await client.get("/work-hours/tasks")
    assert r_tasks_page.status_code == 200
    assert "UndefinedError" not in r_tasks_page.text
