"""
Regression tests for the findings of the security review on branch
claude/security-issues-review-jsfhoh.

Every test here pins down a hole that was actually open in the code at
some point -- not a hypothetical. Grouped by finding, in the order they
were fixed:

1. Stored XSS via a member address (members/detail.html rendered
   `address_lines(...)|join('<br>')|safe`, which marks the raw member
   data as trusted -- see app/l10n.py's jinja_address_html).
2. /api/v1/stats was reachable with no authentication at all, unlike
   every other /api/v1 router.
3. Login brute-force protection (app/rate_limit.py).
4. The default SECRET_KEY must not boot outside development.
5. The bootstrap admin must change its documented default password
   before it can use the app.
6. Security response headers.
7. CSRF protection for cookie-authenticated form POSTs.
8. CSV formula injection in the finance bookings, member, parcel, and
   work-hours evaluation exports (flagged by an external pentest, not
   found in-house -- see docs/security.md).
"""
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from app.database import AsyncSessionLocal
from app.models import (
    Member, ClubSetting, FinanceAccount, FinanceAccountType, AccountTransaction,
    Parcel, ParcelStatus, MemberParcel, WorkHoursConfiguration, WorkHoursMode,
    PurchaseRequest,
)
from tests.conftest import auth_header, login


async def web_login(client: AsyncClient, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303), response.text


# ---------------------------------------------------------------------------
# 1. Stored XSS via member address fields
# ---------------------------------------------------------------------------

XSS_PAYLOAD = '<img src=x onerror="alert(1)">'


async def test_member_address_is_escaped_on_detail_page(client, admin_user):
    """A member's address is free text entered by anyone with
    members_parcels write access (web UI or REST API). It used to be
    rendered through `|join('<br>')|safe`, which -- because Jinja's join
    returns a plain str for plain-str items and separators -- emitted it
    completely unescaped, so a colleague's address could run script in a
    full-access admin's session."""
    async with AsyncSessionLocal() as session:
        member = Member(
            first_name="Xss", last_name="Test",
            street=XSS_PAYLOAD, postal_code="12345", city="Town",
        )
        session.add(member)
        await session.commit()
        member_id = member.id

    await web_login(client, admin_user.email)
    response = await client.get(f"/members/{member_id}")
    assert response.status_code == 200

    assert XSS_PAYLOAD not in response.text, "member address must never be rendered as raw HTML"
    assert "&lt;img src=x onerror=" in response.text, "the address should still be shown, escaped"
    # The <br> between address lines is genuine markup and must survive
    # the escaping -- otherwise the fix would just break the layout.
    assert "12345 Town" in response.text
    assert "&lt;br&gt;" not in response.text


async def test_address_html_escapes_every_line():
    """Unit-level counterpart to the route test above, so the guarantee
    is pinned to the helper and not only to one template."""
    from app.l10n import jinja_address_html

    rendered = jinja_address_html({}, XSS_PAYLOAD, "12345", "<b>Town</b>")
    assert "<img" not in rendered
    assert "&lt;img" in rendered
    assert "&lt;b&gt;Town" in rendered
    assert "<br>" in rendered, "line separator must stay real markup"


# ---------------------------------------------------------------------------
# 2. /api/v1/stats authentication
# ---------------------------------------------------------------------------

async def test_api_stats_requires_authentication(client):
    """Shipped unauthenticated: member counts, parcel counts and total
    areas were readable by anyone who could reach the port."""
    response = await client.get("/api/v1/stats")
    assert response.status_code == 401


async def test_api_stats_works_with_token(client, admin_user):
    token = await login(client, admin_user.email)
    response = await client.get("/api/v1/stats", headers=auth_header(token))
    assert response.status_code == 200
    assert "members_total" in response.json()


# ---------------------------------------------------------------------------
# 3. Login brute-force throttling
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_login_throttle():
    """The counters are module-level and would otherwise leak between
    tests (and into the rest of the suite, which logs in constantly)."""
    from app.rate_limit import reset_all
    reset_all()
    yield
    reset_all()


async def test_web_login_throttles_repeated_failures(client, admin_user):
    from app.login_throttle import MAX_FAILURES_PER_ACCOUNT

    for _ in range(MAX_FAILURES_PER_ACCOUNT):
        response = await client.post(
            "/auth/login", data={"email": admin_user.email, "password": "wrong"}
        )
        assert response.status_code == 401

    blocked = await client.post(
        "/auth/login", data={"email": admin_user.email, "password": "wrong"}
    )
    assert blocked.status_code == 429

    # ... and the throttle holds even once the RIGHT password shows up:
    # otherwise an attacker's final, successful guess would sail through.
    with_correct_password = await client.post(
        "/auth/login", data={"email": admin_user.email, "password": "testpasswort123"}
    )
    assert with_correct_password.status_code == 429


async def test_api_login_shares_the_same_throttle(client, admin_user):
    """The API must not be a way around the web limit -- both entry
    points count into the same buckets."""
    from app.login_throttle import MAX_FAILURES_PER_ACCOUNT

    for _ in range(MAX_FAILURES_PER_ACCOUNT):
        response = await client.post(
            "/api/v1/auth/login", json={"email": admin_user.email, "password": "wrong"}
        )
        assert response.status_code == 401

    blocked = await client.post(
        "/auth/login", data={"email": admin_user.email, "password": "wrong"}
    )
    assert blocked.status_code == 429


async def test_successful_login_clears_the_failure_counter(client, admin_user):
    from app.login_throttle import MAX_FAILURES_PER_ACCOUNT

    for _ in range(MAX_FAILURES_PER_ACCOUNT - 1):
        await client.post("/auth/login", data={"email": admin_user.email, "password": "wrong"})

    ok = await client.post(
        "/auth/login", data={"email": admin_user.email, "password": "testpasswort123"}
    )
    assert ok.status_code in (302, 303)

    # A fresh budget: the earlier near-miss must not leave the user one
    # typo away from being locked out.
    again = await client.post("/auth/login", data={"email": admin_user.email, "password": "wrong"})
    assert again.status_code == 401


# ---------------------------------------------------------------------------
# 4. The published default SECRET_KEY must not boot in production
# ---------------------------------------------------------------------------

def test_default_secret_key_rejected_outside_development():
    from app.config import DEFAULT_SECRET_KEY, Settings

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(environment="production", secret_key=DEFAULT_SECRET_KEY)


def test_default_secret_key_allowed_in_development():
    from app.config import DEFAULT_SECRET_KEY, Settings

    assert Settings(environment="development", secret_key=DEFAULT_SECRET_KEY).secret_key


def test_own_secret_key_accepted_in_production():
    from app.config import Settings

    assert Settings(environment="production", secret_key="a-real-and-sufficiently-long-secret")


# ---------------------------------------------------------------------------
# 5. Forced password change for the bootstrap admin
# ---------------------------------------------------------------------------

@pytest.fixture
async def must_change_user(admin_user):
    async with AsyncSessionLocal() as session:
        user = await session.get(type(admin_user), admin_user.id)
        user.must_change_password = True
        await session.commit()
    return admin_user


async def test_bootstrap_admin_is_redirected_to_change_password(client, must_change_user):
    await web_login(client, must_change_user.email)

    for path in ("/", "/members/", "/admin/users/"):
        response = await client.get(path)
        assert response.status_code == 302, path
        assert response.headers["location"] == "/auth/change-password", path

    # The change form itself and logging out have to stay reachable, or
    # the account would be stuck in a redirect loop.
    form = await client.get("/auth/change-password")
    assert form.status_code == 200


async def test_password_change_lifts_the_lock(client, must_change_user):
    await web_login(client, must_change_user.email)

    response = await client.post("/auth/change-password", data={
        "current_password": "testpasswort123",
        "new_password": "ein-neues-passwort",
        "new_password_confirm": "ein-neues-passwort",
    })
    assert response.status_code == 200

    dashboard = await client.get("/")
    assert dashboard.status_code == 200


async def test_reusing_the_same_password_is_rejected(client, must_change_user):
    await web_login(client, must_change_user.email)

    response = await client.post("/auth/change-password", data={
        "current_password": "testpasswort123",
        "new_password": "testpasswort123",
        "new_password_confirm": "testpasswort123",
    })
    assert response.status_code == 400

    still_locked = await client.get("/")
    assert still_locked.status_code == 302


async def test_api_refuses_tokens_while_a_password_change_is_pending(client, must_change_user):
    """Otherwise the forced change would be a web-only gate that any API
    client could walk straight past with the default credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": must_change_user.email, "password": "testpasswort123"},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 6. Security response headers
# ---------------------------------------------------------------------------

async def test_security_headers_present_on_every_response(client):
    for path in ("/auth/login", "/static/uploads/logo.png"):
        response = await client.get(path)
        headers = response.headers
        assert headers["x-content-type-options"] == "nosniff", path
        assert headers["x-frame-options"] == "DENY", path
        assert headers["referrer-policy"] == "same-origin", path
        csp = headers["content-security-policy"]
        assert "frame-ancestors 'none'" in csp, path
        assert "form-action 'self'" in csp, path
        assert "object-src 'none'" in csp, path


async def test_hsts_only_outside_development(client):
    """A local http:// instance must not pin the browser to https for a
    year; a production one should."""
    from app.security_headers import security_headers
    from app.config import settings

    assert "Strict-Transport-Security" not in security_headers()

    original = settings.environment
    try:
        settings.environment = "production"
        assert "Strict-Transport-Security" in security_headers()
    finally:
        settings.environment = original


# ---------------------------------------------------------------------------
# 7. CSRF protection
# ---------------------------------------------------------------------------

async def test_form_post_without_csrf_token_is_rejected(raw_client, admin_user):
    """The cross-site forgery case: a request that carries the session
    cookie but no token. Simulated here by a client that never renders a
    form -- exactly what an attacker's page can produce."""
    await raw_client.post("/auth/login", data={"email": admin_user.email, "password": "testpasswort123"})
    response = await raw_client.post("/members/new", data={"first_name": "Mallory", "last_name": "Test"})
    assert response.status_code == 403


async def test_csrf_cookie_is_httponly(raw_client):
    """The token is compared server-side, so the cookie never has to be
    readable by JavaScript -- an XSS still can't lift it."""
    response = await raw_client.get("/auth/login")
    set_cookie = response.headers.get("set-cookie", "")
    assert "csrf=" in set_cookie
    assert "HttpOnly" in set_cookie


async def test_csrf_token_in_form_body_is_accepted(raw_client, admin_user):
    """The path a real browser takes: render the login form, submit the
    hidden field that came with it."""
    page = await raw_client.get("/auth/login")
    assert 'name="csrf_token"' in page.text, "the login form must carry the hidden field"

    import re
    token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
    response = await raw_client.post(
        "/auth/login",
        data={"email": admin_user.email, "password": "testpasswort123", "csrf_token": token},
    )
    assert response.status_code in (302, 303)


async def test_mismatched_csrf_token_is_rejected(raw_client, admin_user):
    await raw_client.get("/auth/login")
    response = await raw_client.post(
        "/auth/login",
        data={"email": admin_user.email, "password": "testpasswort123", "csrf_token": "not-the-token"},
    )
    assert response.status_code == 403


async def test_api_endpoints_stay_exempt(raw_client, admin_user):
    """The REST API authenticates with a bearer token, never with an
    ambient cookie, so requiring CSRF there would break every client
    without adding protection."""
    response = await raw_client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "testpasswort123"},
    )
    assert response.status_code == 200


async def test_every_post_form_in_the_templates_carries_a_token():
    """Catches the next form somebody adds without one -- which would
    otherwise only surface as a 403 in production."""
    import pathlib
    import re

    form_open = re.compile(r'<form\b[^>]*>', re.I | re.S)
    missing = []
    for path in sorted(pathlib.Path("app/templates").rglob("*.html")):
        source = path.read_text()
        for match in form_open.finditer(source):
            method = re.search(r'method\s*=\s*["\']?(\w+)', match.group(0), re.I)
            if not method or method.group(1).lower() != "post":
                continue
            if "csrf_field()" not in source[match.end():match.end() + 200]:
                line = source[:match.start()].count("\n") + 1
                missing.append(f"{path}:{line}")

    assert not missing, "POST forms without {{ csrf_field() }}:\n" + "\n".join(missing)


async def test_no_confirm_dialog_hand_quotes_a_template_string():
    """Issue #238: `confirm('{{ ... }}')` breaks on any apostrophe in the
    rendered text (French "l'accès", a member named O'Brien) -- the
    browser decodes &#39; back to ' before parsing the JS, the string
    ends early, the handler throws, and the form submits without asking.
    Every call site must go through |tojson|forceescape instead."""
    import pathlib
    import re

    hand_quoted = re.compile(r"confirm\(\s*['\"]\{\{")
    offenders = []
    for path in sorted(pathlib.Path("app/templates").rglob("*.html")):
        source = path.read_text()
        for match in hand_quoted.finditer(source):
            line = source[:match.start()].count("\n") + 1
            offenders.append(f"{path}:{line}")

    assert not offenders, "confirm() with a hand-quoted template string:\n" + "\n".join(offenders)


async def test_confirm_dialog_survives_an_apostrophe_in_french():
    """Same issue, end to end: render the actual pattern with a real
    French string containing ' (and "), then undo the HTML escaping the
    way a browser does before handing the attribute to the JS parser --
    what's left must be exactly one valid string literal."""
    import html
    import json

    from app.i18n import translate
    from app.templating import templates

    text = translate("admin.groups.delete_confirm", "fr")
    assert "'" in text  # the precondition that made this a bug

    attribute = templates.env.from_string(
        '<form onsubmit="return confirm({{ text|tojson|forceescape }})">'
    ).render(text=text)
    handler = html.unescape(attribute.split('onsubmit="', 1)[1].rsplit('"', 1)[0])

    assert handler.startswith("return confirm(") and handler.endswith(")")
    literal = handler[len("return confirm("):-1]
    assert "'" not in literal
    assert json.loads(literal) == text


# ---------------------------------------------------------------------------
# 8. CSV formula injection in export paths
# ---------------------------------------------------------------------------
# A cell that starts with =, +, -, or @ is interpreted as a formula by
# Excel/LibreOffice Calc when the exported file is opened. These exports
# wrote user-entered free text straight into cells -- fixed with
# app/csv_utils.csv_safe(), which prefixes such cells with a single quote.

FORMULA_PAYLOAD = "=cmd|'/c calc'!A1"


async def test_finance_bookings_csv_export_sanitizes_formula_injection(client, admin_user):
    await web_login(client, admin_user.email)

    async with AsyncSessionLocal() as session:
        session.add(ClubSetting(key="modul_finances", value="true", description="test"))
        account = FinanceAccount(name="Vereinskonto", account_type=FinanceAccountType.BANK, is_active=True)
        session.add(account)
        await session.commit()
        account_id = account.id

    async with AsyncSessionLocal() as session:
        session.add(AccountTransaction(
            account_id=account_id, booking_date=date.fromisoformat("2026-08-01"), amount="-9.99",
            description=FORMULA_PAYLOAD, counterparty="+1;DDE payload", source="manual",
        ))
        await session.commit()

    response = await client.get(f"/finances/accounts/{account_id}/bookings/export.csv")
    assert response.status_code == 200
    assert f"'{FORMULA_PAYLOAD}" in response.text
    assert "'+1;DDE payload" in response.text


async def test_members_csv_export_sanitizes_formula_injection(client, admin_user):
    await web_login(client, admin_user.email)

    async with AsyncSessionLocal() as session:
        session.add(Member(first_name=FORMULA_PAYLOAD, last_name="Gardener", notes="@SUM(1+1)"))
        await session.commit()

    response = await client.get("/members/export/csv")
    assert response.status_code == 200
    assert f"'{FORMULA_PAYLOAD}" in response.text
    assert "'@SUM(1+1)" in response.text


async def test_parcels_csv_export_sanitizes_formula_injection(client, admin_user):
    await web_login(client, admin_user.email)

    async with AsyncSessionLocal() as session:
        session.add(Parcel(plot_number="G999", status=ParcelStatus.ACTIVE, termination_note=FORMULA_PAYLOAD))
        await session.commit()

    response = await client.get("/parcels/export/csv")
    assert response.status_code == 200
    assert f"'{FORMULA_PAYLOAD}" in response.text


# ---------------------------------------------------------------------------
# 9. Purchase-request confirmation links never expired
# ---------------------------------------------------------------------------

async def test_expired_confirmation_token_is_rejected(client):
    """A purchase-request confirmation link used to work forever. An old
    request's token (backdated past the max age) must now be treated
    the same as an unknown one -- shown the "invalid" page, not the
    confirmation form, and not usable to actually confirm."""
    async with AsyncSessionLocal() as session:
        pr = PurchaseRequest(
            title="Alter Antrag", justification="Test",
            requester_name="Extern", requester_email="extern@example.com",
            confirmation_token="expired-token-abc",
            created_at=datetime.now(timezone.utc) - timedelta(days=31),
        )
        session.add(pr)
        await session.commit()
        pr_id = pr.id

    get_response = await client.get("/purchase-requests/confirm/expired-token-abc")
    assert get_response.status_code == 200
    assert "confirmation_invalid" not in get_response.text  # sanity: template renders, doesn't leak its own name
    post_response = await client.post("/purchase-requests/confirm/expired-token-abc")
    assert post_response.status_code == 200

    async with AsyncSessionLocal() as session:
        refreshed = await session.get(PurchaseRequest, pr_id)
        assert refreshed.confirmed_by_requester is False, "an expired token must not be able to confirm"


async def test_fresh_confirmation_token_still_works(client):
    """Companion to the expiry test above: a token within the max age
    must still confirm normally, so the fix doesn't just reject
    everything."""
    async with AsyncSessionLocal() as session:
        pr = PurchaseRequest(
            title="Neuer Antrag", justification="Test",
            requester_name="Extern", requester_email="extern@example.com",
            confirmation_token="fresh-token-xyz",
        )
        session.add(pr)
        await session.commit()
        pr_id = pr.id

    response = await client.post("/purchase-requests/confirm/fresh-token-xyz")
    assert response.status_code == 200

    async with AsyncSessionLocal() as session:
        refreshed = await session.get(PurchaseRequest, pr_id)
        assert refreshed.confirmed_by_requester is True


# ---------------------------------------------------------------------------
# 10. crypto_utils.decrypt() used to silently return ciphertext on failure
# ---------------------------------------------------------------------------

async def test_decrypt_of_token_encrypted_with_a_different_key_raises():
    """Simulates a SECRET_KEY rotation: a value that really was
    encrypted (structurally a valid Fernet token) but with a different
    key than the one currently derived from SECRET_KEY. Previously this
    was returned unchanged -- a still-encrypted blob silently used as
    if it were the real plaintext (e.g. sent as an SMTP password). It
    must now fail loudly instead."""
    from cryptography.fernet import Fernet
    from app.crypto_utils import decrypt, DecryptionError

    token_from_another_key = Fernet(Fernet.generate_key()).encrypt(b"hunter2").decode("utf-8")

    with pytest.raises(DecryptionError):
        decrypt(token_from_another_key)


async def test_decrypt_still_returns_legacy_plaintext():
    """Values stored before encryption was introduced aren't valid
    Fernet tokens at all (unlike the rotated-key case above), so they
    must still come back unchanged instead of raising."""
    from app.crypto_utils import decrypt

    assert decrypt("") == ""
    assert decrypt(None) is None
    assert decrypt("hunter2") == "hunter2"


async def test_work_hours_evaluation_csv_sanitizes_formula_injection(client, admin_user):
    await web_login(client, admin_user.email)

    async with AsyncSessionLocal() as session:
        session.add(WorkHoursConfiguration(
            year=2026, hours_required="5.0", rate_per_hour_eur="25.00", mode=WorkHoursMode.PER_PARCEL,
        ))
        member = Member(first_name=FORMULA_PAYLOAD, last_name="Tenant")
        parcel = Parcel(plot_number="G998", status=ParcelStatus.ACTIVE)
        session.add_all([member, parcel])
        await session.commit()
        session.add(MemberParcel(member_id=member.id, parcel_id=parcel.id, is_invoice_address=True))
        await session.commit()

    response = await client.get("/work-hours/evaluation/csv", params={"year": "2026"})
    assert response.status_code == 200
    assert f"'{FORMULA_PAYLOAD}" in response.text
