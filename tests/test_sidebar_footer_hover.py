"""
Issue #199: hovering over the sidebar's "Change password" or "Log out"
button made its label text disappear. Bootstrap's own `.btn-outline-
light:hover` rule sets a light background *and* dark text; this
project's `.sidebar-footer a:hover { color: #fff; }` had higher
specificity (extra `a` selector) and overrode only the text color back
to white, on top of Bootstrap's light hover background -- white text on
a near-white background. Fixed by scoping the custom hover rule to
`a:not(.btn)`, so Bootstrap's own (correctly-contrasted) button hover
styling applies to these two links undisturbed.
"""


async def web_login(client, email: str, password: str = "testpasswort123") -> None:
    response = await client.post("/auth/login", data={"email": email, "password": password})
    assert response.status_code in (302, 303)


async def test_sidebar_footer_hover_rule_excludes_buttons(client, admin_user):
    await web_login(client, "admin@example.com")

    page = await client.get("/")
    assert page.status_code == 200
    assert ".sidebar-footer a:not(.btn) {" in page.text
    assert ".sidebar-footer a:not(.btn):hover {" in page.text
    # The old unscoped rule (the actual bug) must not be reintroduced.
    assert ".sidebar-footer a:hover {" not in page.text
    assert ".sidebar-footer a {" not in page.text
