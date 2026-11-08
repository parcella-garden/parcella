"""
Notes module (issue #286, docs/module-notes.md, ADR 0122/0123). Focus:
the happy path in the database only, search/filter/sort, sanitized
rendering, permissions, the REST API -- and the cloud file being the
master: external edits pulled in, a save refused when the file changed
meanwhile, renamed/deleted files, and edits made while the cloud was
off pushed (or kept as a conflict copy) later.
"""
from datetime import date, time

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import hash_password
from app.cloud_storage import CloudFileEntry, CloudStorageError
from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, Group, GroupMembership, GroupModulePermission, Note, TaxonomyCategory, TaxonomyTag, User, UserRole,
)
from app.note_files import note_filename, parse_note_file, render_note_file
from app.services.notes import reset_sync_throttle
from tests.conftest import auth_header, login
from tests.test_detail_page_navigation import web_login

FOLDER = "Vorstand/Notizen"


@pytest.fixture(autouse=True)
def _fresh_sync_throttle():
    reset_sync_throttle()
    yield
    reset_sync_throttle()


async def _notes(include_deleted=False):
    async with AsyncSessionLocal() as db:
        query = select(Note).options(selectinload(Note.tags), selectinload(Note.category)).order_by(Note.title)
        if not include_deleted:
            query = query.where(Note.deleted_at.is_(None))
        return (await db.scalars(query)).all()


async def _category(name: str, **translations) -> str:
    async with AsyncSessionLocal() as db:
        category = TaxonomyCategory(name=name, translations=translations or None)
        db.add(category)
        await db.commit()
        return category.id


async def _create(client, **fields) -> str:
    data = {"title": "Vorstandssitzung März", "note_date": "2026-03-04", "note_time": "19:00",
            "body_markdown": "# TOP 1\n\nWasseruhren tauschen.", **fields}
    response = await client.post("/notes/new", data=data)
    assert response.status_code == 303, response.text
    return response.headers["location"].rsplit("/", 1)[1]


# ---------------------------------------------------------------------------
# File format (pure)
# ---------------------------------------------------------------------------

def test_note_file_round_trip_and_lenient_parsing():
    text = render_note_file(
        note_id="abc", title='Board: "March"', note_date=date(2026, 3, 4), note_time=time(19, 0),
        category="Board meeting", tags=["Wasser", "Budget"], body="Hello\n\n| a | b |\n|---|---|\n| 1 | 2 |",
    )
    parsed = parse_note_file(text.encode(), "x.md")
    assert (parsed.note_id, parsed.title, parsed.category) == ("abc", 'Board: "March"', "Board meeting")
    assert (parsed.note_date, parsed.note_time, parsed.tags) == (date(2026, 3, 4), time(19, 0), ["Wasser", "Budget"])
    assert parsed.body.startswith("Hello") and parsed.body.endswith("| 1 | 2 |")

    # Hand-written YAML: unquoted values, single quotes, block list, separate time.
    hand = "---\ntitle: Mitgliederversammlung 2026\ndate: 2026-05-01 # Samstag\ntime: '10:30'\ncategory: 'Sonstiges'\ntags:\n  - Wahl\n  - Satzung\n---\nText"
    parsed = parse_note_file(hand.encode("utf-8"), "irrelevant.md")
    assert parsed.title == "Mitgliederversammlung 2026" and parsed.note_date == date(2026, 5, 1)
    assert parsed.note_time == time(10, 30) and parsed.category == "Sonstiges"
    assert parsed.tags == ["Wahl", "Satzung"] and parsed.body == "Text"

    # No header at all: title from the first heading, date from the file name.
    parsed = parse_note_file("﻿# Treffen mit der Stadt\r\nInhalt".encode(), "2026-02-01-stadt.md")
    assert parsed.title == "Treffen mit der Stadt" and parsed.note_date == date(2026, 2, 1)
    assert parsed.note_id is None and parsed.body == "# Treffen mit der Stadt\nInhalt"


def test_note_filename_is_ascii_and_unique():
    taken = {"2026-03-04-vorstandssitzung-marz.md"}
    assert note_filename(date(2026, 3, 4), "Vorstandssitzung März", taken) == "2026-03-04-vorstandssitzung-marz-2.md"
    assert note_filename(date(2026, 3, 4), "../../etc/passwd\r\n", set()) == "2026-03-04-etc-passwd.md"
    assert note_filename(date(2026, 3, 4), "Łódź ✓", set()) == "2026-03-04-odz.md"


# ---------------------------------------------------------------------------
# Database only
# ---------------------------------------------------------------------------

async def test_create_list_search_filter_edit_delete(client, admin_user):
    board = await _category("Board meeting", de="Vorstandssitzung")
    other = await _category("Other")
    await web_login(client, "admin@example.com")

    first = await _create(client, category_id=board, new_tags="Wasser, Budget")
    await _create(client, title="Gespräch Stadtwerke", note_date="2026-01-10", note_time="", category_id=other,
                  body_markdown="Stromzähler ablesen")
    [budget] = [t for t in (await _notes())[1].tags if t.name == "Budget"]

    page = await client.get("/notes/")
    assert page.status_code == 200
    assert page.text.index("Vorstandssitzung März") < page.text.index("Gespräch Stadtwerke")  # newest first
    page = await client.get("/notes/?sort=date_asc")
    assert page.text.index("Gespräch Stadtwerke") < page.text.index("Vorstandssitzung März")
    assert "Gespräch Stadtwerke" not in (await client.get("/notes/?q=wasseruhren")).text  # body search
    assert "Gespräch Stadtwerke" in (await client.get("/notes/?q=STROM")).text
    assert "Vorstandssitzung März" in (await client.get("/notes/?q=budget")).text  # tag name search
    filtered = (await client.get(f"/notes/?category={other}")).text
    assert "Gespräch Stadtwerke" in filtered and "Vorstandssitzung März" not in filtered
    filtered = (await client.get(f"/notes/?tag={budget.id}&date_from=2026-03-01&date_to=2026-03-31")).text
    assert "Vorstandssitzung März" in filtered and "Gespräch Stadtwerke" not in filtered
    assert "Vorstandssitzung März" not in (await client.get("/notes/?date_to=2026-02-01")).text

    detail = await client.get(f"/notes/{first}")
    assert detail.status_code == 200
    assert "<h1>TOP 1</h1>" in detail.text and "04.03.2026 19:00" in detail.text

    edited = await client.post(f"/notes/{first}/edit", data={
        "title": "Vorstandssitzung März (Protokoll)", "note_date": "2026-03-04", "note_time": "",
        "category_id": board, "tag_ids": [budget.id], "body_markdown": "Neu",
    })
    assert edited.status_code == 303
    note = next(n for n in await _notes() if n.id == first)
    assert note.title == "Vorstandssitzung März (Protokoll)" and note.note_time is None
    assert [t.name for t in note.tags] == ["Budget"] and note.body_markdown == "Neu"
    assert note.cloud_dirty and note.cloud_filename is None  # waits for a notes folder

    download = await client.get(f"/notes/{first}/download")
    assert download.status_code == 200 and download.text.startswith("---\nid: " + first)
    assert "filename*=UTF-8''2026-03-04-vorstandssitzung-marz-protokoll.md" in download.headers["content-disposition"]

    assert (await client.post(f"/notes/{first}/delete")).status_code == 303
    assert [n.title for n in await _notes()] == ["Gespräch Stadtwerke"]
    assert len(await _notes(include_deleted=True)) == 2  # soft delete
    assert (await client.get(f"/notes/{first}")).status_code == 404


async def test_validation_keeps_the_typed_text(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/notes/new", data={"title": "  ", "note_date": "2026-03-04", "body_markdown": "Mein Text"})
    assert response.status_code == 400 and "Mein Text" in response.text
    assert await _notes() == []


async def test_rendering_is_sanitized_and_preview_uses_the_same_sanitizer(client, admin_user):
    await web_login(client, "admin@example.com")
    note_id = await _create(client, body_markdown='<script>alert(1)</script><img src=x onerror="alert(2)">'
                                                   '[x](javascript:alert(3))\n\n| a |\n|---|\n| 1 |')
    page = (await client.get(f"/notes/{note_id}")).text
    assert "<script>alert(1)" not in page and "onerror" not in page and "javascript:alert" not in page
    assert "<table>" in page
    preview = await client.post("/notes/preview", json={"markdown": "<script>x</script>\n\n**fett**"})
    assert preview.status_code == 200
    html = preview.json()["html"]
    assert "<strong>fett</strong>" in html and "script" not in html


async def test_taxonomy_page_rename_translate_delete(client, admin_user):
    category = await _category("Board meeting")
    await web_login(client, "admin@example.com")
    note_id = await _create(client, category_id=category, new_tags="Wasser")
    [tag] = (await _notes())[0].tags

    assert (await client.get("/notes/taxonomy")).status_code == 200
    assert (await client.post(f"/notes/taxonomy/tags/{tag.id}/rename", data={"name": "Trinkwasser"})).status_code == 303
    response = await client.post("/notes/taxonomy/tags/new", data={"name": "trinkwasser"})
    assert "already+exists" in response.headers["location"] or "error=" in response.headers["location"]
    await client.post(f"/notes/taxonomy/categories/{category}/translations", data={"name_de": "Vorstandssitzung"})
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="language", value="de", description="test"))
        await db.commit()
    assert "Vorstandssitzung" in (await client.get(f"/notes/{note_id}")).text

    await client.post(f"/notes/taxonomy/categories/{category}/delete")
    [note] = await _notes()
    assert note.category is None and [t.name for t in note.tags] == ["Trinkwasser"]


async def test_permissions_follow_the_group_matrix(client, admin_user):
    await web_login(client, "admin@example.com")
    note_id = await _create(client)
    async with AsyncSessionLocal() as db:
        nobody = User(email="nobody@example.com", name="Nobody", password_hash=hash_password("testpasswort123"),
                      role=UserRole.READONLY)
        reader = User(email="reader@example.com", name="Reader", password_hash=hash_password("testpasswort123"),
                      role=UserRole.READONLY)
        group = Group(name="Note readers")
        db.add_all([nobody, reader, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="notes", can_read=True))
        db.add(GroupMembership(user_id=reader.id, group_id=group.id))
        await db.commit()

    await web_login(client, "nobody@example.com")
    assert (await client.get("/notes/")).status_code == 403
    assert (await client.get(f"/notes/{note_id}")).status_code == 403

    await web_login(client, "reader@example.com")
    assert (await client.get("/notes/")).status_code == 200
    detail = await client.get(f"/notes/{note_id}")
    assert detail.status_code == 200 and f"/notes/{note_id}/edit" not in detail.text
    assert (await client.post("/notes/new", data={"title": "x", "note_date": "2026-01-01"})).status_code == 403
    assert (await client.post(f"/notes/{note_id}/delete")).status_code == 403
    assert (await client.post("/notes/taxonomy/tags/new", data={"name": "x"})).status_code == 403


async def test_module_flag_switches_it_off(client, admin_user):
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_notes", value="false", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    assert (await client.get("/notes/")).status_code == 404


async def test_api_create_list_get_update_delete(client, admin_user):
    token = await login(client, "admin@example.com")
    headers = auth_header(token)
    category = (await client.post("/api/v1/notes/categories", json={"name": "Board meeting"}, headers=headers)).json()
    created = await client.post("/api/v1/notes", headers=headers, json={
        "title": "API-Notiz", "note_date": "2026-04-01", "note_time": "18:30", "category_id": category["id"],
        "new_tags": ["Strom"], "body_markdown": "Hallo",
    })
    assert created.status_code == 201, created.text
    note = created.json()
    assert note["category"]["name"] == "Board meeting" and [t["name"] for t in note["tags"]] == ["Strom"]

    listed = await client.get("/api/v1/notes?q=hallo", headers=headers)
    assert [n["id"] for n in listed.json()] == [note["id"]]
    assert (await client.get("/api/v1/notes?q=nichts", headers=headers)).json() == []
    assert [t["name"] for t in (await client.get("/api/v1/notes/tags", headers=headers)).json()] == ["Strom"]

    updated = await client.put(f"/api/v1/notes/{note['id']}", headers=headers, json={
        "title": "API-Notiz 2", "note_date": "2026-04-02", "body_markdown": "Neu", "tag_ids": [],
    })
    assert updated.status_code == 200 and updated.json()["title"] == "API-Notiz 2" and updated.json()["tags"] == []
    bad = await client.post("/api/v1/notes", headers=headers, json={"title": " ", "note_date": "2026-04-01"})
    assert bad.status_code == 422

    assert (await client.delete(f"/api/v1/notes/{note['id']}", headers=headers)).status_code == 204
    assert (await client.get(f"/api/v1/notes/{note['id']}", headers=headers)).status_code == 404


# ---------------------------------------------------------------------------
# Cloud file as master (ADR 0123)
# ---------------------------------------------------------------------------

class _MemoryCloud:
    """An in-memory notes folder; every write bumps last_modified."""

    def __init__(self):
        self.files = {}
        self.clock = 0
        self.uploads = 0

    def put(self, name, text):
        self.clock += 1
        self.files[name] = (text.encode("utf-8"), f"t{self.clock}")

    def text(self, name):
        return self.files[name][0].decode("utf-8")

    async def list_files(self, path):
        assert path == FOLDER
        return [CloudFileEntry(name=n, is_directory=False, size=len(c), last_modified=m)
                for n, (c, m) in self.files.items()] + [CloudFileEntry(name="Anhänge", is_directory=True)]

    async def upload_file(self, path, filename, content):
        assert path == FOLDER
        self.uploads += 1
        self.clock += 1
        self.files[filename] = (content, f"t{self.clock}")

    async def download_file(self, path, filename):
        if filename not in self.files:
            raise CloudStorageError("not found")
        return self.files[filename][0]

    async def delete_file(self, path, filename):
        self.files.pop(filename, None)

    async def aclose(self):
        pass


async def _enable_cloud(client, monkeypatch, set_folder=True) -> _MemoryCloud:
    async with AsyncSessionLocal() as db:
        db.add(ClubSetting(key="modul_cloud_storage", value="true", description="test"))
        await db.commit()
    await web_login(client, "admin@example.com")
    if set_folder:
        saved = await client.post("/admin/integrations/nextcloud/notes-folder", data={"relative_path": f"/{FOLDER}/"})
        assert saved.status_code == 303
    cloud = _MemoryCloud()

    async def fake_provider(db):
        return cloud

    monkeypatch.setattr("app.services.notes.get_cloud_storage_provider", fake_provider)
    return cloud


async def _sync(client):
    response = await client.post("/notes/sync")
    assert response.status_code == 303 and "error=" not in response.headers["location"], response.headers["location"]


async def test_cloud_save_writes_the_file_and_external_edits_come_back(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    category = await _category("Board meeting")
    note_id = await _create(client, category_id=category, new_tags="Wasser")

    [name] = cloud.files
    assert name == "2026-03-04-vorstandssitzung-marz.md"
    text = cloud.text(name)
    assert f"id: {note_id}" in text and 'category: "Board meeting"' in text and 'tags: ["Wasser"]' in text
    assert "Wasseruhren tauschen." in text

    # Edited in the cloud: the next sync (or opening the note) shows it.
    cloud.put(name, text.replace("Wasseruhren tauschen.", "Wasseruhren bis Mai tauschen.").replace('["Wasser"]', '["Wasser", "Frist"]'))
    await _sync(client)
    [note] = await _notes()
    assert "bis Mai" in note.body_markdown and sorted(t.name for t in note.tags) == ["Frist", "Wasser"]

    cloud.put(name, cloud.text(name).replace("bis Mai", "bis Juni"))
    assert "bis Juni" in (await client.get(f"/notes/{note_id}")).text

    # A sync with nothing changed downloads nothing new and uploads nothing.
    uploads = cloud.uploads
    await _sync(client)
    await _sync(client)
    assert cloud.uploads == uploads


async def test_save_is_refused_when_the_file_changed_meanwhile(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    note_id = await _create(client)
    [name] = cloud.files

    form = (await client.get(f"/notes/{note_id}/edit")).text
    base_hash = form.split('name="base_hash" value="', 1)[1].split('"', 1)[0]
    assert len(base_hash) == 64

    cloud.put(name, cloud.text(name).replace("Wasseruhren tauschen.", "Von Anna im Nextcloud geändert."))
    payload = {"title": "Vorstandssitzung März", "note_date": "2026-03-04", "body_markdown": "Meine Fassung",
               "base_hash": base_hash}
    conflict = await client.post(f"/notes/{note_id}/edit", data=payload)
    assert conflict.status_code == 409
    assert "Von Anna im Nextcloud geändert." in conflict.text and "Meine Fassung" in conflict.text
    assert "Von Anna" in cloud.text(name)  # not overwritten
    [note] = await _notes()
    assert "Von Anna" in note.body_markdown  # the index follows the master

    # Saving again from the conflict page overwrites deliberately.
    new_hash = conflict.text.split('name="base_hash" value="', 1)[1].split('"', 1)[0]
    assert new_hash != base_hash
    saved = await client.post(f"/notes/{note_id}/edit", data={**payload, "base_hash": new_hash})
    assert saved.status_code == 303
    assert "Meine Fassung" in cloud.text(name) and "Von Anna" not in cloud.text(name)


async def test_new_renamed_and_deleted_files(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    await _category("Board meeting", de="Vorstandssitzung")
    cloud.put("protokoll.md", "---\ntitle: Mitgliederversammlung\ndate: 2026-05-01\ncategory: Vorstandssitzung\n"
                              "tags: [Wahl]\n---\nGewählt wurde ...")
    cloud.put("readme.txt", "not a note")
    await _sync(client)
    [note] = await _notes()
    assert note.title == "Mitgliederversammlung" and note.category.name == "Board meeting"  # matched via translation
    assert [t.name for t in note.tags] == ["Wahl"] and note.cloud_filename == "protokoll.md"

    # Edited once in Parcella, the file carries the note id ...
    await client.post(f"/notes/{note.id}/edit", data={
        "title": "Mitgliederversammlung", "note_date": "2026-05-01", "category_id": note.category_id,
        "tag_ids": [note.tags[0].id], "body_markdown": "Gewählt wurde ...",
    })
    assert f"id: {note.id}" in cloud.text("protokoll.md")
    # ... so a rename in the cloud keeps the same note.
    cloud.files["2026-05-01-mv.md"] = cloud.files.pop("protokoll.md")
    await _sync(client)
    [renamed] = await _notes()
    assert renamed.id == note.id and renamed.cloud_filename == "2026-05-01-mv.md"

    # Deleted in the cloud: the note goes (soft) ...
    content = cloud.files.pop("2026-05-01-mv.md")
    await _sync(client)
    assert await _notes() == []
    # ... and restoring the file brings the same note back.
    cloud.files["2026-05-01-mv.md"] = content
    await _sync(client)
    assert [n.id for n in await _notes()] == [note.id]


async def test_a_copied_file_becomes_its_own_note(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    note_id = await _create(client)
    [name] = cloud.files
    cloud.put("kopie.md", cloud.text(name))
    await _sync(client)
    notes = await _notes()
    assert len(notes) == 2 and {n.cloud_filename for n in notes} == {name, "kopie.md"}
    assert note_id in {n.id for n in notes}


async def test_edits_while_the_cloud_was_off_are_pushed_or_kept_as_conflict_copy(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    pushed_id = await _create(client, title="Wird hochgeladen")
    conflict_id = await _create(client, title="Konflikt")
    deleted_id = await _create(client, title="Wird gelöscht")
    assert len(cloud.files) == 3

    # Notes folder unset: notes keep working from the database.
    await client.post("/admin/integrations/nextcloud/notes-folder", data={"relative_path": ""})
    for note_id, title in ((pushed_id, "Wird hochgeladen"), (conflict_id, "Konflikt")):
        await client.post(f"/notes/{note_id}/edit", data={
            "title": title, "note_date": "2026-03-04", "body_markdown": "Offline geändert",
        })
    await client.post(f"/notes/{deleted_id}/delete")
    new_id = await _create(client, title="Ganz neu", note_date="2026-06-01")
    assert len(cloud.files) == 3  # nothing written meanwhile

    conflict_file = next(n for n in cloud.files if "konflikt" in n)
    cloud.put(conflict_file, cloud.text(conflict_file).replace("Wasseruhren tauschen.", "In der Cloud geändert"))

    await client.post("/admin/integrations/nextcloud/notes-folder", data={"relative_path": FOLDER})
    await _sync(client)

    by_title = {n.title: n for n in await _notes()}
    assert set(by_title) == {"Wird hochgeladen", "Konflikt", "Konflikt (conflict copy)", "Ganz neu"}
    assert "Offline geändert" in cloud.text(by_title["Wird hochgeladen"].cloud_filename)
    assert by_title["Konflikt"].body_markdown == "# TOP 1\n\nIn der Cloud geändert"  # cloud wins
    assert by_title["Konflikt (conflict copy)"].body_markdown == "Offline geändert"  # nothing lost
    assert by_title["Ganz neu"].id == new_id and by_title["Ganz neu"].cloud_filename == "2026-06-01-ganz-neu.md"
    assert not any("gelöscht" in n or "geloscht" in n for n in cloud.files)
    assert all(not n.cloud_dirty for n in by_title.values())


async def test_cloud_unreachable_on_save_saves_nothing(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)

    async def broken_upload(path, filename, content):
        raise CloudStorageError("Nextcloud is down")

    cloud.upload_file = broken_upload
    response = await client.post("/notes/new", data={"title": "x", "note_date": "2026-01-01", "body_markdown": "Text"})
    assert response.status_code == 502 and "Nextcloud is down" in response.text and "Text" in response.text
    assert await _notes() == []


async def test_failed_listing_deletes_nothing(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    await _create(client)

    async def broken_list(path):
        raise CloudStorageError("Folder 'Vorstand/Notizen' was not found")

    cloud.list_files = broken_list
    response = await client.post("/notes/sync")
    assert "error=" in response.headers["location"]
    assert len(await _notes()) == 1
