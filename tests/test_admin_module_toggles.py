"""
Regression coverage for a real bug found while adding the
public_contact_api module: the "Optional Modules" toggle on
/admin/settings defaulted an unset checkbox to CHECKED
(settings_map.get(key, 'true')) regardless of what
app/module_flags.py's MODULE_DEFAULTS actually says for that module --
so a module that deliberately defaults to False (any module opening a
public endpoint, e.g. public_signup_api/public_contact_api) rendered as
already-on before it was ever explicitly saved, even though the backend
correctly treated it as off. Fixed by passing each field's real default
through to the template instead of hardcoding 'true'.
"""
import re


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


def _checkbox_html(page_html: str, input_id: str) -> str:
    match = re.search(rf'<input[^>]*id="{re.escape(input_id)}"[^>]*>', page_html)
    assert match, f"checkbox #{input_id} not found on the page"
    return match.group(0)


async def test_module_defaulting_to_false_renders_unchecked_when_never_saved(client, admin_user):
    """public_contact_api defaults to False (MODULE_DEFAULTS) and has
    never been saved for this club -- its checkbox must not be checked."""
    await web_login(client, "admin@example.com")

    response = await client.get("/admin/settings")
    assert response.status_code == 200

    checkbox = _checkbox_html(response.text, "modul_public_contact_api")
    assert "checked" not in checkbox


async def test_module_defaulting_to_true_renders_checked_when_never_saved(client, admin_user):
    """tickets defaults to True and has never been explicitly saved --
    its checkbox must be checked, same as before this fix."""
    await web_login(client, "admin@example.com")

    response = await client.get("/admin/settings")
    assert response.status_code == 200

    checkbox = _checkbox_html(response.text, "modul_tickets")
    assert "checked" in checkbox


async def test_explicitly_saved_value_overrides_the_default(client, admin_user):
    await web_login(client, "admin@example.com")

    save_response = await client.post(
        "/admin/settings", data={"modul_public_contact_api": "true"}, follow_redirects=False,
    )
    assert save_response.status_code in (302, 303)

    response = await client.get("/admin/settings")
    checkbox = _checkbox_html(response.text, "modul_public_contact_api")
    assert "checked" in checkbox
