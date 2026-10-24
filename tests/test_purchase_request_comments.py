"""
Issue #249: discuss a purchase request inside Parcella instead of by
phone. A comment is emailed to the requester and to everyone who
commented or approved before -- never to its author, each address once.
"""
from tests.conftest import auth_header, login
from tests.test_detail_page_navigation import web_login


def _record_emails(monkeypatch):
    sent = []

    async def fake_send_email(to, subject, html_body, text_body=None, db=None, attachments=None):
        sent.append((to, subject, html_body))
        return True

    monkeypatch.setattr("app.services.purchase_requests.send_email", fake_send_email)
    return sent


async def _create(client, email, **extra):
    response = await client.post(
        "/api/v1/purchase-requests",
        json={"title": "Beschriftungsgerät", "justification": "Für die Stromzähler", **extra},
        headers=auth_header(await login(client, email)),
    )
    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


async def test_comment_reaches_requester_and_discussion_not_author(
    client, admin_user, board_user, second_board_user, monkeypatch,
):
    # vorstand@ requests, admin@ approves, vorstand2@ comments.
    pr_id = await _create(client, "vorstand@example.com")
    approve = await client.post(
        f"/api/v1/purchase-requests/{pr_id}/approve", headers=auth_header(await login(client, "admin@example.com")),
    )
    assert approve.status_code == 200
    sent = _record_emails(monkeypatch)

    await web_login(client, "vorstand2@example.com")
    response = await client.post(
        f"/purchase-requests/{pr_id}/comments",
        data={"content": "Wir haben schon eins <b>im Schuppen</b>.\nRegal 3."},
    )
    assert response.status_code == 303
    assert sorted(to for to, _, _ in sent) == ["admin@example.com", "vorstand@example.com"]
    _, subject, html = sent[0]
    assert subject == 'New comment: purchase request "Beschriftungsgerät"'
    # Escaped, line break kept, link to answer in Parcella.
    assert "&lt;b&gt;im Schuppen&lt;/b&gt;.<br>Regal 3." in html and "<b>im Schuppen" not in html
    assert f"/purchase-requests/{pr_id}" in html

    detail = await client.get(f"/purchase-requests/{pr_id}")
    assert "Wir haben schon eins &lt;b&gt;im Schuppen&lt;/b&gt;." in detail.text

    # The requester answers through the API: now the commenter hears of it, the requester doesn't.
    sent.clear()
    reply = await client.post(
        f"/api/v1/purchase-requests/{pr_id}/comments", json={"content": "Danke, dann ziehe ich ihn zurück."},
        headers=auth_header(await login(client, "vorstand@example.com")),
    )
    assert reply.status_code == 201
    assert sorted(to for to, _, _ in sent) == ["admin@example.com", "vorstand2@example.com"]

    thread = await client.get(
        f"/api/v1/purchase-requests/{pr_id}/comments", headers=auth_header(await login(client, "admin@example.com")),
    )
    assert [c["content"] for c in thread.json()] == [
        "Wir haben schon eins <b>im Schuppen</b>.\nRegal 3.", "Danke, dann ziehe ich ihn zurück.",
    ]


async def test_external_requester_is_told_to_contact_the_board(client, admin_user, monkeypatch):
    pr_id = await _create(client, "admin@example.com", requester_name="Erika Extern", requester_email="erika@example.org")
    sent = _record_emails(monkeypatch)
    response = await client.post(
        f"/api/v1/purchase-requests/{pr_id}/comments", json={"content": "Welches Modell?"},
        headers=auth_header(await login(client, "admin@example.com")),
    )
    assert response.status_code == 201
    assert [to for to, _, _ in sent] == ["erika@example.org"]
    html = sent[0][2]
    assert "get in touch with the board" in html and f"/purchase-requests/{pr_id}" not in html


async def test_empty_comment_is_refused(client, admin_user, monkeypatch):
    pr_id = await _create(client, "admin@example.com")
    sent = _record_emails(monkeypatch)
    response = await client.post(
        f"/api/v1/purchase-requests/{pr_id}/comments", json={"content": "   "},
        headers=auth_header(await login(client, "admin@example.com")),
    )
    assert response.status_code == 400
    assert sent == []
