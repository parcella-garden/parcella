"""
Tests for the Inventory module: categories (freely configurable),
items (club- or member-owned, with financial fields), and the
quantity-aware lending system.

Category/item/loan CRUD is tested via the JWT API (this module has a
full REST API alongside its web UI, per the project's "API-first"
convention). A few web-UI-specific things -- route-registration
ordering (a real bug found and fixed while building this: /categories/
and /new must be registered before the single-segment /{item_id}
catch-all, or they'd be swallowed by it) and the require_admin
permission boundary for mutating actions -- are tested via the
cookie-based web login instead, since that's what those routes
actually use.
"""
from tests.conftest import login, auth_header


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


# ---------------------------------------------------------------------------
# ADR 0070: shared service layer + unified (Group-based, not role-only)
# authorization for the API.
# ---------------------------------------------------------------------------

async def test_treasurer_without_group_grant_is_blocked_from_inventory_write_via_api(client):
    """api_inventory.py used require_write_access (role-only) -- ANY
    TREASURER could write inventory data via the API regardless of
    Group configuration. Now the API checks the same Group-derived
    permission as HTML."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="treasurer-no-group-inventory@example.com", name="Treasurer No Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.TREASURER,
        )
        db.add(user)
        await db.commit()

    token = await login(client, "treasurer-no-group-inventory@example.com")
    response = await client.post(
        "/api/v1/inventory/categories", json={"name": "Fences"}, headers=auth_header(token),
    )
    assert response.status_code == 403


async def test_readonly_with_group_grant_can_write_inventory_via_api(client):
    """Flip side: a READONLY user granted inventory:write via a Group
    could already write inventory data through the HTML UI, but the
    role-only API check blocked them regardless of Group membership."""
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupModulePermission, GroupMembership
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        user = User(
            email="readonly-with-group-inventory@example.com", name="Readonly With Group",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        db.add(user)
        await db.flush()

        group = Group(name="Inventory Handlers")
        db.add(group)
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="inventory", can_read=True, can_write=True))
        db.add(GroupMembership(user_id=user.id, group_id=group.id))
        await db.commit()

    token = await login(client, "readonly-with-group-inventory@example.com")
    response = await client.post(
        "/api/v1/inventory/categories", json={"name": "Fences"}, headers=auth_header(token),
    )
    assert response.status_code == 201, response.text


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

async def test_create_and_list_categories(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await client.post(
        "/api/v1/inventory/categories", json={"name": "Playground", "description": "Slides, swings, sandbox"},
        headers=headers,
    )
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == "Playground"

    listing = await client.get("/api/v1/inventory/categories", headers=headers)
    assert listing.status_code == 200
    assert any(c["name"] == "Playground" for c in listing.json())


async def test_duplicate_category_name_rejected(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    await client.post("/api/v1/inventory/categories", json={"name": "Fences"}, headers=headers)
    duplicate = await client.post("/api/v1/inventory/categories", json={"name": "Fences"}, headers=headers)
    assert duplicate.status_code == 400


async def test_deleting_category_does_not_delete_its_items(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    category = (await client.post(
        "/api/v1/inventory/categories", json={"name": "Locks & Keys"}, headers=headers,
    )).json()

    item = (await client.post(
        "/api/v1/inventory/items",
        json={"name": "Gate padlock", "category_id": category["id"]},
        headers=headers,
    )).json()

    delete_response = await client.delete(f"/api/v1/inventory/categories/{category['id']}", headers=headers)
    assert delete_response.status_code == 204

    still_there = await client.get(f"/api/v1/inventory/items/{item['id']}", headers=headers)
    assert still_there.status_code == 200
    assert still_there.json()["category_id"] is None


# ---------------------------------------------------------------------------
# Items -- ownership and financials
# ---------------------------------------------------------------------------

async def test_create_club_owned_item_with_financials(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    response = await client.post(
        "/api/v1/inventory/items",
        json={
            "name": "Wheelbarrow", "owner_type": "CLUB",
            "purchase_date": "2022-04-01", "purchase_price": "89.90",
            "current_value": "40.00", "current_value_updated_at": "2026-01-01",
            "replacement_cost": "110.00", "quantity_total": 3,
        },
        headers=headers,
    )
    assert response.status_code == 201
    item = response.json()
    assert item["quantity_total"] == 3
    assert item["quantity_on_loan"] == 0
    assert item["available_quantity"] == 3
    assert item["purchase_price"] == "89.90"


async def test_member_owned_item_requires_owner_member_id(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Anna", "last_name": "Muster"}, headers=headers,
    )).json()

    missing_owner = await client.post(
        "/api/v1/inventory/items", json={"name": "Personal tent", "owner_type": "MEMBER"}, headers=headers,
    )
    assert missing_owner.status_code == 400

    with_owner = await client.post(
        "/api/v1/inventory/items",
        json={
            "name": "Personal tent", "owner_type": "MEMBER", "owner_member_id": member["id"],
            "purchase_price": "150.00",
        },
        headers=headers,
    )
    assert with_owner.status_code == 201
    item = with_owner.json()
    assert item["owner_type"] == "MEMBER"
    assert item["owner_member_id"] == member["id"]
    # Explicit product decision: personally-owned items get the same
    # financial fields as club-owned ones.
    assert item["purchase_price"] == "150.00"


async def test_retired_items_excluded_from_list_by_default(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Old lawnmower"}, headers=headers,
    )).json()

    await client.post(f"/api/v1/inventory/items/{item['id']}/retire", headers=headers)

    default_list = await client.get("/api/v1/inventory/items", headers=headers)
    assert not any(i["id"] == item["id"] for i in default_list.json())

    with_retired = await client.get("/api/v1/inventory/items?include_retired=true", headers=headers)
    assert any(i["id"] == item["id"] for i in with_retired.json())


# ---------------------------------------------------------------------------
# Loans -- quantity-aware checkout/return
# ---------------------------------------------------------------------------

async def test_loan_checkout_reduces_available_quantity(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Bernd", "last_name": "Beispiel"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items",
        json={"name": "Tent", "is_borrowable": True, "quantity_total": 5, "default_loan_fee": "5.00"},
        headers=headers,
    )).json()

    loan = await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 2, "borrowed_date": "2026-07-01"},
        headers=headers,
    )
    assert loan.status_code == 201
    loan_data = loan.json()
    # No fee_charged given -> falls back to the item's default_loan_fee.
    assert loan_data["fee_charged"] == "5.00"

    updated_item = (await client.get(f"/api/v1/inventory/items/{item['id']}", headers=headers)).json()
    assert updated_item["quantity_on_loan"] == 2
    assert updated_item["available_quantity"] == 3


async def test_loan_checkout_rejects_more_than_available(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Carla", "last_name": "Testperson"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Tent", "is_borrowable": True, "quantity_total": 2},
        headers=headers,
    )).json()

    too_many = await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 3, "borrowed_date": "2026-07-01"},
        headers=headers,
    )
    assert too_many.status_code == 400


async def test_loan_checkout_rejected_for_non_borrowable_item(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Dieter", "last_name": "Testperson"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Office printer", "is_borrowable": False},
        headers=headers,
    )).json()

    response = await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 1, "borrowed_date": "2026-07-01"},
        headers=headers,
    )
    assert response.status_code == 400


async def test_returning_a_loan_restores_availability(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Erika", "last_name": "Testperson"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Rake", "is_borrowable": True, "quantity_total": 1},
        headers=headers,
    )).json()

    loan = (await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 1, "borrowed_date": "2026-07-01"},
        headers=headers,
    )).json()

    fully_booked = (await client.get(f"/api/v1/inventory/items/{item['id']}", headers=headers)).json()
    assert fully_booked["available_quantity"] == 0

    return_response = await client.post(
        f"/api/v1/inventory/loans/{loan['id']}/return", json={"returned_date": "2026-07-05"}, headers=headers,
    )
    assert return_response.status_code == 200
    assert return_response.json()["returned_date"] == "2026-07-05"

    available_again = (await client.get(f"/api/v1/inventory/items/{item['id']}", headers=headers)).json()
    assert available_again["available_quantity"] == 1

    # Returning an already-returned loan is rejected, not silently
    # no-op'd -- catches a double-click or duplicate submission.
    double_return = await client.post(
        f"/api/v1/inventory/loans/{loan['id']}/return", json={}, headers=headers,
    )
    assert double_return.status_code == 400


async def test_active_loans_endpoint_lists_only_outstanding(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Franz", "last_name": "Testperson"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Ladder", "is_borrowable": True, "quantity_total": 2},
        headers=headers,
    )).json()

    loan_a = (await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 1, "borrowed_date": "2026-07-01"},
        headers=headers,
    )).json()
    loan_b = (await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 1, "borrowed_date": "2026-07-02"},
        headers=headers,
    )).json()
    await client.post(f"/api/v1/inventory/loans/{loan_a['id']}/return", json={}, headers=headers)

    active = await client.get("/api/v1/inventory/loans", headers=headers)
    assert active.status_code == 200
    active_ids = [loan["id"] for loan in active.json()]
    assert loan_b["id"] in active_ids
    assert loan_a["id"] not in active_ids


# ---------------------------------------------------------------------------
# Web UI -- route ordering and permissions
# ---------------------------------------------------------------------------

async def test_web_categories_page_is_not_shadowed_by_item_detail_route(client, admin_user):
    """Regression check for a real bug found while building this: the
    single-segment GET /{item_id} catch-all was initially registered
    before GET /categories/, which would have made Starlette match
    "categories" as an item_id and 404 instead of showing the
    categories page."""
    await web_login(client, "admin@example.com")
    response = await client.get("/inventory/categories/")
    assert response.status_code == 200
    assert "categor" in response.text.lower()


async def test_web_new_item_form_is_not_shadowed_by_item_detail_route(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.get("/inventory/new")
    assert response.status_code == 200


async def test_web_active_loans_page_is_not_shadowed_by_item_detail_route(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.get("/inventory/loans/active")
    assert response.status_code == 200


async def test_readonly_role_can_view_but_not_create_items(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    from app.database import AsyncSessionLocal
    from app.models import User, UserRole, Group, GroupMembership, GroupModulePermission
    from app.auth import hash_password

    # Since the group-permission system defaults to no access at all
    # (see app/permissions.py), a READONLY user must be placed in a
    # group with "inventory: read" to see anything -- this is the
    # narrowly-scoped access the system is meant to provide, replacing
    # the old blanket "any logged-in user can view" behavior.
    async with AsyncSessionLocal() as session:
        user = User(
            email="readonly@example.com", name="Test-Readonly",
            password_hash=hash_password("testpasswort123"), role=UserRole.READONLY,
        )
        session.add(user)
        await session.flush()

        group = Group(name="Inventory Viewers")
        session.add(group)
        await session.flush()
        session.add(GroupModulePermission(group_id=group.id, module="inventory", can_read=True))
        session.add(GroupMembership(user_id=user.id, group_id=group.id))
        await session.commit()

    await web_login(client, "readonly@example.com")

    view_response = await client.get("/inventory/")
    assert view_response.status_code == 200

    create_response = await client.get("/inventory/new")
    assert create_response.status_code == 403


async def test_insufficient_quantity_error_is_shared_and_formatted(client, admin_user):
    """ADR 0070: the "only N of M available" rule now lives in
    app/services/inventory.py's checkout_loan(), shared by HTML and API
    -- confirms the ServiceError's {available}/{total} params actually
    get substituted into the resolved i18n text via the API surface."""
    from app.i18n import translate

    token = await login(client, "admin@example.com")
    headers = auth_header(token)

    member = (await client.post(
        "/api/v1/members", json={"first_name": "Petra", "last_name": "Testperson"}, headers=headers,
    )).json()
    item = (await client.post(
        "/api/v1/inventory/items", json={"name": "Wheelbarrow", "is_borrowable": True, "quantity_total": 2},
        headers=headers,
    )).json()

    response = await client.post(
        f"/api/v1/inventory/items/{item['id']}/loans",
        json={"member_id": member["id"], "quantity": 5, "borrowed_date": "2026-07-01"},
        headers=headers,
    )
    assert response.status_code == 400
    expected = translate("inventory.errors.insufficient_quantity", "en", available=2, total=2)
    assert response.json()["detail"] == expected


# ---------------------------------------------------------------------------
# Issue #315: text in the loan fee field was an Internal Server Error
# ---------------------------------------------------------------------------

async def _borrowable_item_and_member(client, default_loan_fee=None):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    member = (await client.post(
        "/api/v1/members", json={"first_name": "Petra", "last_name": "Testperson"}, headers=headers,
    )).json()
    payload = {"name": "Hedge trimmer", "is_borrowable": True, "quantity_total": 1}
    if default_loan_fee is not None:
        payload["default_loan_fee"] = default_loan_fee
    item = (await client.post("/api/v1/inventory/items", json=payload, headers=headers)).json()
    await web_login(client, "admin@example.com")
    return item, member


async def test_loan_fee_with_text_shows_a_message_instead_of_a_500(client, admin_user):
    item, member = await _borrowable_item_and_member(client)

    for bad_fee in ("5 €", "five", "NaN", "-3", "Infinity"):
        response = await client.post(f"/inventory/{item['id']}/loans/checkout", data={
            "member_id": member["id"], "quantity": "1", "borrowed_date": "2026-07-01",
            "fee_charged": bad_fee, "note": "for the hedge",
        })
        assert response.status_code == 400, bad_fee
        assert "Please enter amounts as a number only" in response.text
        # What was typed is still there, and nothing was lent out.
        assert 'value="for the hedge"' in response.text
        assert f'value="{member["id"]}" selected' in response.text

    detail = await client.get(f"/inventory/{item['id']}")
    assert "for the hedge" not in detail.text


async def test_loan_fee_with_a_comma_is_accepted(client, admin_user):
    item, member = await _borrowable_item_and_member(client, default_loan_fee=5)
    detail = await client.get(f"/inventory/{item['id']}")
    assert "the default fee of" in detail.text

    response = await client.post(f"/inventory/{item['id']}/loans/checkout", data={
        "member_id": member["id"], "quantity": "1", "borrowed_date": "2026-07-01", "fee_charged": " 2,50 ",
    })
    assert response.status_code == 303

    from decimal import Decimal
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import ItemLoan
    async with AsyncSessionLocal() as session:
        loan = (await session.execute(select(ItemLoan).where(ItemLoan.item_id == item["id"]))).scalar_one()
        assert loan.fee_charged == Decimal("2.50")


async def test_bad_quantity_or_date_on_checkout_is_a_message_too(client, admin_user):
    item, member = await _borrowable_item_and_member(client)
    for field, value, message in (
        ("quantity", "two", "whole number of 1 or more"),
        ("quantity", "0", "whole number of 1 or more"),
        ("borrowed_date", "yesterday", "valid date"),
    ):
        data = {"member_id": member["id"], "quantity": "1", "borrowed_date": "2026-07-01", field: value}
        response = await client.post(f"/inventory/{item['id']}/loans/checkout", data=data)
        assert response.status_code == 400, (field, value)
        assert message in response.text


async def test_item_form_with_text_in_an_amount_shows_a_message(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/inventory/new", data={
        "name": "Lawn mower", "owner_type": "CLUB", "purchase_price": "199 Euro",
    })
    assert response.status_code == 400
    assert "Please enter amounts as a number only" in response.text
