"""
Issue #241: free-form tags on members ("water responsible", "extended
board" ...) and a tag filter on /members/ -- see ADR 0093 and
docs/module-members-parcels.md. The filter goes through
MemberListFilter (app/member_filters.py), so the CSV export and the
detail page's Previous/Next follow it like every other list filter.
"""
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.member_filters import MemberListFilter
from app.models import Member, MemberTag, member_tag_links
from tests.conftest import auth_header, login
from tests.test_detail_page_navigation import web_login


async def _members(*names):
    async with AsyncSessionLocal() as db:
        members = [Member(first_name=first, last_name=last) for first, last in names]
        db.add_all(members)
        await db.commit()
        return [m.id for m in members]


async def _tags_of(member_id):
    async with AsyncSessionLocal() as db:
        rows = await db.execute(
            select(MemberTag.name).join(member_tag_links, member_tag_links.c.tag_id == MemberTag.id)
            .where(member_tag_links.c.member_id == member_id).order_by(MemberTag.name)
        )
        return [r[0] for r in rows]


async def test_tag_members_and_filter_the_list(client, admin_user):
    await web_login(client, "admin@example.com")
    anna, bert, carl = await _members(("Anna", "Aal"), ("Bert", "Berg"), ("Carl", "Cord"))

    assert (await client.post(f"/members/{anna}/tags/add", data={"name": "  Wasser  verantwortlich "})).status_code == 303
    # Same name, other case and spacing: reuses the tag, doesn't split the group.
    assert (await client.post(f"/members/{carl}/tags/add", data={"name": "wasser verantwortlich"})).status_code == 303
    await client.post(f"/members/{bert}/tags/add", data={"name": "Vorstand"})
    await client.post(f"/members/{anna}/tags/add", data={"name": "Wasser verantwortlich"})  # twice: no-op

    async with AsyncSessionLocal() as db:
        tags = {t.name: t.id for t in (await db.scalars(select(MemberTag))).all()}
    assert set(tags) == {"Wasser verantwortlich", "Vorstand"}
    assert await _tags_of(anna) == ["Wasser verantwortlich"]

    detail = await client.get(f"/members/{anna}")
    assert detail.status_code == 200 and "Wasser verantwortlich" in detail.text

    water = tags["Wasser verantwortlich"]
    page = await client.get(f"/members/?tag={water}")
    assert page.status_code == 200
    assert "Aal, Anna" in page.text and "Cord, Carl" in page.text and "Berg, Bert" not in page.text
    assert f"tag={water}" in page.text  # carried into row links and the CSV export link

    csv = await client.get(f"/members/export/csv?tag={water}")
    assert csv.status_code == 200
    assert "Anna" in csv.text and "Carl" in csv.text and "Bert" not in csv.text
    assert "Wasser verantwortlich" in csv.text

    # Previous/Next on the detail page stay within the tag (ADR 0075):
    # Anna's next is Carl, not Bert.
    nav = await client.get(f"/members/{anna}?tag={water}")
    assert f"/members/{carl}?tag={water}" in nav.text
    assert f"/members/{bert}" not in nav.text

    assert (await client.post(f"/members/{anna}/tags/{water}/remove")).status_code == 303
    assert await _tags_of(anna) == []


async def test_manage_tags_rename_and_delete(client, admin_user):
    await web_login(client, "admin@example.com")
    [anna] = await _members(("Anna", "Aal"))
    await client.post(f"/members/{anna}/tags/add", data={"name": "Hecke"})
    await client.post(f"/members/{anna}/tags/add", data={"name": "Wasser"})
    async with AsyncSessionLocal() as db:
        tags = {t.name: t.id for t in (await db.scalars(select(MemberTag))).all()}

    page = await client.get("/members/tags")
    assert page.status_code == 200 and "Hecke" in page.text

    assert (await client.post(f"/members/tags/{tags['Hecke']}/rename", data={"name": "Heckenteam"})).status_code == 303
    clash = await client.post(f"/members/tags/{tags['Hecke']}/rename", data={"name": "WASSER"})
    assert clash.status_code == 303 and "error=" in clash.headers["location"]
    assert await _tags_of(anna) == ["Heckenteam", "Wasser"]

    assert (await client.post(f"/members/tags/{tags['Wasser']}/delete")).status_code == 303
    assert await _tags_of(anna) == ["Heckenteam"]

    empty = await client.post(f"/members/{anna}/tags/add", data={"name": "   "})
    assert empty.status_code == 303 and "error=" in empty.headers["location"]


async def test_tags_rest_api(client, admin_user):
    headers = auth_header(await login(client, "admin@example.com"))
    anna, bert = await _members(("Anna", "Aal"), ("Bert", "Berg"))

    created = await client.post(f"/api/v1/members/{anna}/tags", json={"name": "Vorstand"}, headers=headers)
    assert created.status_code == 201, created.text
    tag_id = created.json()["id"]
    by_id = await client.post(f"/api/v1/members/{bert}/tags", json={"tag_id": tag_id}, headers=headers)
    assert by_id.status_code == 201 and by_id.json()["id"] == tag_id
    assert (await client.post(f"/api/v1/members/{bert}/tags", json={}, headers=headers)).status_code == 422

    assert [t["name"] for t in (await client.get("/api/v1/members/tags", headers=headers)).json()] == ["Vorstand"]
    listed = await client.get(f"/api/v1/members?tag={tag_id}", headers=headers)
    assert {m["id"] for m in listed.json()} == {anna, bert}
    assert [t["name"] for t in (await client.get(f"/api/v1/members/{anna}", headers=headers)).json()["tags"]] == ["Vorstand"]

    renamed = await client.patch(f"/api/v1/members/tags/{tag_id}", json={"name": "Erweiterter Vorstand"}, headers=headers)
    assert renamed.status_code == 200 and renamed.json()["name"] == "Erweiterter Vorstand"

    assert (await client.delete(f"/api/v1/members/{anna}/tags/{tag_id}", headers=headers)).status_code == 204
    assert (await client.delete(f"/api/v1/members/{anna}/tags/{tag_id}", headers=headers)).status_code == 404
    assert (await client.delete(f"/api/v1/members/tags/{tag_id}", headers=headers)).status_code == 204
    assert (await client.get(f"/api/v1/members/{bert}", headers=headers)).json()["tags"] == []


def test_member_list_filter_round_trips():
    """#242 stores a filter as JSON on an announcement -- unknown keys
    from an older or newer version must not break loading it."""
    f = MemberListFilter(search="Aal", active_only=True, tag="abc")
    assert MemberListFilter.from_dict(f.to_dict()) == f
    assert MemberListFilter.from_dict({**f.to_dict(), "gone_field": 1}) == f
    assert f.query_string() == "search=Aal&active_only=true&tag=abc"
    assert MemberListFilter().is_empty() and not f.is_empty()
