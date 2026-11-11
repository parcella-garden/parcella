"""
Notes module (issue #286, docs/module-notes.md, ADR 0122/0123). Focus:
the happy path in the database only, search/filter/sort, sanitized
rendering, permissions, the REST API -- and the cloud file being the
master: external edits pulled in, a save refused when the file changed
meanwhile, renamed/deleted files, and edits made while the cloud was
off pushed (or kept as a conflict copy) later. Since issue #311 (ADR
0127) the file holds only the text: metadata edits never touch the
cloud, old headers are stripped, renamed files are relinked by content.
"""
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import hash_password
from app.cloud_storage import CloudFileEntry, CloudStorageError
from app.database import AsyncSessionLocal
from app.models import (
    ClubSetting, Group, GroupMembership, GroupModulePermission, Note, TaxonomyCategory, TaxonomyTag, User, UserRole,
)
from app.note_files import date_from_filename, note_filename, parse_note_file, render_note_body, render_note_file
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
    data = {"title": "Vorstandssitzung März", "note_date": "2026-03-04",
            "body_markdown": "# TOP 1\n\nWasseruhren tauschen.", **fields}
    response = await client.post("/notes/new", data=data)
    assert response.status_code == 303, response.text
    return response.headers["location"].rsplit("/", 1)[1]


# ---------------------------------------------------------------------------
# File format (pure)
# ---------------------------------------------------------------------------

def test_note_file_round_trip_and_lenient_parsing():
    text = render_note_file(
        note_id="abc", title='Board: "March"', note_date=date(2026, 3, 4),
        category="Board meeting", tags=["Wasser", "Budget"], body="Hello\n\n| a | b |\n|---|---|\n| 1 | 2 |",
    )
    parsed = parse_note_file(text.encode(), "x.md")
    assert (parsed.note_id, parsed.title, parsed.category) == ("abc", 'Board: "March"', "Board meeting")
    assert (parsed.note_date, parsed.tags) == (date(2026, 3, 4), ["Wasser", "Budget"])
    assert "date: 2026-03-04" + chr(10) in text
    assert parsed.body.startswith("Hello") and parsed.body.endswith("| 1 | 2 |")

    # Hand-written YAML: unquoted values, single quotes, block list, a time (ignored).
    hand = "---\ntitle: Mitgliederversammlung 2026\ndate: 2026-05-01T10:30:00+02:00 # Samstag\ncategory: 'Sonstiges'\ntags:\n  - Wahl\n  - Satzung\n---\nText"
    parsed = parse_note_file(hand.encode("utf-8"), "irrelevant.md")
    assert parsed.title == "Mitgliederversammlung 2026" and parsed.note_date == date(2026, 5, 1)
    assert parsed.category == "Sonstiges"
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
    await _create(client, title="Gespräch Stadtwerke", note_date="2026-01-10", category_id=other,
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
    assert "<h1>TOP 1</h1>" in detail.text and "04.03.2026" in detail.text

    edited = await client.post(f"/notes/{first}/edit", data={
        "title": "Vorstandssitzung März (Protokoll)", "note_date": "2026-03-04",
        "category_id": board, "tag_ids": [budget.id], "body_markdown": "Neu",
    })
    assert edited.status_code == 303
    note = next(n for n in await _notes() if n.id == first)
    assert note.title == "Vorstandssitzung März (Protokoll)"
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
        "title": "API-Notiz", "note_date": "2026-04-01", "category_id": category["id"],
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
    """An in-memory notes folder with subfolders. `files` is keyed by the
    path relative to the notes folder; every write bumps last_modified."""

    def __init__(self):
        self.files = {}
        self.folders = {"Anhänge"}  # an empty folder, no notes in it
        self.clock = 0
        self.uploads = 0

    def put(self, rel, text, last_modified=None):
        self.clock += 1
        self.files[rel] = (text.encode("utf-8"), last_modified or f"t{self.clock}")

    def text(self, rel):
        return self.files[rel][0].decode("utf-8")

    @staticmethod
    def _rel(path, filename=""):
        assert path == FOLDER or path.startswith(FOLDER + "/"), path
        folder = path[len(FOLDER) + 1:]
        return "/".join(p for p in (folder, filename) if p)

    async def list_files(self, path):
        folder = self._rel(path)
        prefix = f"{folder}/" if folder else ""
        entries, seen = [], set()
        for rel, (content, modified) in self.files.items():
            if not rel.startswith(prefix):
                continue
            rest = rel[len(prefix):]
            if "/" in rest:
                seen.add(rest.split("/", 1)[0])
            else:
                entries.append(CloudFileEntry(name=rest, is_directory=False, size=len(content), last_modified=modified))
        for known in self.folders:
            if known.startswith(prefix) and "/" not in known[len(prefix):]:
                seen.add(known[len(prefix):])
        return entries + [CloudFileEntry(name=n, is_directory=True) for n in sorted(seen) if n]

    async def create_folder(self, path):
        self.folders.add(self._rel(path))

    async def upload_file(self, path, filename, content):
        self.uploads += 1
        self.clock += 1
        self.files[self._rel(path, filename)] = (content, f"t{self.clock}")

    async def download_file(self, path, filename):
        rel = self._rel(path, filename)
        if rel not in self.files:
            raise CloudStorageError("not found")
        return self.files[rel][0]

    async def delete_file(self, path, filename):
        self.files.pop(self._rel(path, filename), None)

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
    assert name == "Board meeting/2026-03-04-vorstandssitzung-marz.md"  # its category's folder
    text = cloud.text(name)
    assert text == "# TOP 1\n\nWasseruhren tauschen.\n"  # the text only: metadata stays in Parcella (ADR 0127)

    # Edited in the cloud: the next sync (or opening the note) shows it;
    # the metadata Parcella holds is untouched.
    cloud.put(name, text.replace("Wasseruhren tauschen.", "Wasseruhren bis Mai tauschen."))
    await _sync(client)
    [note] = await _notes()
    assert "bis Mai" in note.body_markdown and [t.name for t in note.tags] == ["Wasser"]
    assert note.title == "Vorstandssitzung März" and note.category.name == "Board meeting"

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
    cloud.put("Vorstandssitzung/protokoll.md", "---\ntitle: Mitgliederversammlung\ndate: 2026-05-01\n"
                                               "tags: [Wahl]\n---\nGewählt wurde ...")
    cloud.put("readme.txt", "not a note")
    await _sync(client)
    [note] = await _notes()
    assert note.title == "Mitgliederversammlung" and note.category.name == "Board meeting"  # matched via translation
    assert [t.name for t in note.tags] == ["Wahl"] and note.cloud_filename == "Vorstandssitzung/protokoll.md"

    # Adopted with its header's metadata, the header is stripped right away.
    assert cloud.text("Vorstandssitzung/protokoll.md") == "Gewählt wurde ...\n"  # stays in its matching folder
    # A rename in the cloud keeps the same note: relinked by its content.
    cloud.files["Vorstandssitzung/2026-05-01-mv.md"] = cloud.files.pop("Vorstandssitzung/protokoll.md")
    await _sync(client)
    [renamed] = await _notes()
    assert renamed.id == note.id and renamed.cloud_filename == "Vorstandssitzung/2026-05-01-mv.md"
    assert renamed.title == "Mitgliederversammlung" and [t.name for t in renamed.tags] == ["Wahl"]

    # Deleted in the cloud: the note goes (soft) ...
    content = cloud.files.pop("Vorstandssitzung/2026-05-01-mv.md")
    await _sync(client)
    assert await _notes() == []
    # ... and restoring the file brings the same note back.
    cloud.files["Vorstandssitzung/2026-05-01-mv.md"] = content
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


async def test_subfolders_are_categories_and_deeper_folders_are_kept(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    board = await _category("Board meeting", de="Vorstandssitzung")
    # The folder wins over the header; deeper folders are read too.
    cloud.put("Vorstandssitzung/2026/maerz.md", "---\ntitle: März\ndate: 2026-03-04\ncategory: Sonstiges\n---\nText")
    cloud.put("Gartenbegehung/rundgang.md", "# Rundgang\nAlles grün")  # a folder nobody created as category yet
    cloud.put("lose.md", "---\ntitle: Lose Notiz\ndate: 2026-01-01\ncategory: Board meeting\n---\n")
    cloud.put(".papierkorb/alt.md", "# Alt")  # hidden: ignored
    await _sync(client)
    by_title = {n.title: n for n in await _notes()}
    assert set(by_title) == {"März", "Rundgang", "Lose Notiz"}
    assert by_title["März"].category_id == board  # "Vorstandssitzung" is board's German name
    assert by_title["Rundgang"].category.name == "Gartenbegehung"
    assert by_title["Lose Notiz"].category_id == board  # no folder: the header decides
    assert not any(c.name == "Sonstiges" for c in (await _all_categories()))

    def form(note, **fields):
        return {"title": note.title, "note_date": note.note_date.isoformat(), "body_markdown": note.body_markdown,
                "category_id": note.category_id or "", **fields}

    # Saving with the same category keeps the file where it is, deep folder included.
    await client.post(f"/notes/{by_title['März'].id}/edit", data=form(by_title["März"], body_markdown="Neu"))
    assert "Neu" in cloud.text("Vorstandssitzung/2026/maerz.md")
    # Another category: the file moves into that category's folder (created if needed).
    await client.post(f"/notes/{by_title['März'].id}/edit", data=form(by_title["März"], category_id=by_title["Rundgang"].category_id))
    assert "Vorstandssitzung/2026/maerz.md" not in cloud.files and "Gartenbegehung/maerz.md" in cloud.files
    other = await _category("Other")
    await client.post(f"/notes/{by_title['März'].id}/edit", data=form(by_title["März"], category_id=other))
    assert "Other/maerz.md" in cloud.files and "Other" in cloud.folders
    # No category: back to the notes folder itself.
    await client.post(f"/notes/{by_title['März'].id}/edit", data=form(by_title["März"], category_id=""))
    assert "maerz.md" in cloud.files and "Other/maerz.md" not in cloud.files
    # The header category of a loose file moved it into the category's
    # (existing, German-named) folder when the header was stripped.
    assert "Vorstandssitzung/lose.md" in cloud.files and "lose.md" not in cloud.files

    await _sync(client)
    notes = await _notes()
    assert len(notes) == 3 and all(not n.cloud_dirty for n in notes)  # moves didn't create copies


async def test_imported_note_keeps_its_original_date(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    cloud.put("protokoll.md", "# Ohne Datum", last_modified="Wed, 04 Mar 2026 18:00:00 GMT")  # WebDAV style
    cloud.put("s3.md", "# Auch ohne", last_modified="2025-11-30T08:00:00.000Z")  # S3 style
    cloud.put("2024-06-01-sommerfest.md", "# Sommerfest", last_modified="Wed, 04 Mar 2026 18:00:00 GMT")
    await _sync(client)
    dates = {n.title: n.note_date for n in await _notes()}
    assert dates == {"Ohne Datum": date(2026, 3, 4), "Auch ohne": date(2025, 11, 30), "Sommerfest": date(2024, 6, 1)}

    # A later edit in the cloud without a date header doesn't move it to today.
    cloud.put("protokoll.md", "# Ohne Datum\nergänzt")
    await _sync(client)
    [note] = [n for n in await _notes() if n.title == "Ohne Datum"]
    assert note.note_date == date(2026, 3, 4)


def test_date_from_filename_formats():
    """Issue #302: the date forms clubs put in front of file names."""
    assert date_from_filename("2026-11-08-vorstand.md") == date(2026, 11, 8)
    assert date_from_filename("20261108 Vorstandssitzung.md") == date(2026, 11, 8)
    assert date_from_filename("20250730_Ergebnise_Gartenbegehung.md") == date(2025, 7, 30)
    assert date_from_filename("202506_gartenbegehungen.md") == date(2025, 6, 1)  # month only: the 1st
    assert date_from_filename("Protokolle Vorstandssitzung/20261025 Vorstandssitzung.md") == date(2026, 10, 25)
    for not_a_date in ("Technik.md", "template_vorstandssitzungen.md", "2026110812 Zahl.md",
                       "20261340 falsch.md", "202613_falsch.md", "2026 Jahresplan.md"):
        assert date_from_filename(not_a_date) is None, not_a_date
    # A date header still wins over the file name.
    parsed = parse_note_file(b"---\ndate: 2026-01-02\n---\n# X", "20261108 X.md")
    assert parsed.note_date == date(2026, 1, 2)


async def test_copied_template_gets_its_file_name_date_not_the_template_timestamp(client, admin_user, monkeypatch):
    """Bug #302: a protocol created in Nextcloud by copying a template
    keeps the template's last-modified time. Its file name says
    20261108, but only YYYY-MM-DD was read, so the note landed on the
    template's date, buried among last year's protocols."""
    cloud = await _enable_cloud(client, monkeypatch)
    template = "# Vorstandssitzung\n\n- Datum:"
    old = "Mon, 27 Oct 2025 20:10:48 GMT"
    cloud.put("Protokolle Vorstandssitzung/template_vorstandssitzungen.md", template, last_modified=old)
    cloud.put("Protokolle Vorstandssitzung/20261108 Vorstandssitzung.md", template, last_modified=old)
    cloud.put("Gartenbegehungen/202506_gartenbegehungen.md", "# Begehung", last_modified=old)
    await _sync(client)
    dates = {n.cloud_filename: n.note_date for n in await _notes()}
    assert dates == {
        "Protokolle Vorstandssitzung/template_vorstandssitzungen.md": date(2025, 10, 27),
        "Protokolle Vorstandssitzung/20261108 Vorstandssitzung.md": date(2026, 11, 8),
        "Gartenbegehungen/202506_gartenbegehungen.md": date(2025, 6, 1),
    }


async def test_migration_0119_makes_the_next_sync_redate_existing_notes(client, admin_user, monkeypatch):
    """Notes imported before #302 kept the wrong date; migration 0119
    forgets the stored hash so the next sync re-reads each file once
    (never for a note with an unpushed local edit), and once moves notes
    stuck on their import day to the file's last-modified date."""
    import importlib.util
    from pathlib import Path
    from sqlalchemy import text, update

    cloud = await _enable_cloud(client, monkeypatch)
    cloud.put("20261108 Vorstandssitzung.md", "# Vorstandssitzung", last_modified="Mon, 27 Oct 2025 20:10:48 GMT")
    cloud.put("Technik.md", "# Technik", last_modified="Sat, 13 Dec 2025 16:37:04 GMT")
    cloud.put("Ohne Datum.md", "# Ohne Datum", last_modified="Sat, 13 Dec 2025 16:37:04 GMT")
    await _sync(client)
    by_file = {n.cloud_filename: n for n in await _notes()}
    # Simulate the pre-#302 state: the template's timestamp as date, and
    # the very first imports' "import day" for files without any date.
    async with AsyncSessionLocal() as db:
        await db.execute(update(Note).where(Note.id == by_file["20261108 Vorstandssitzung.md"].id)
                         .values(note_date=date(2025, 10, 27)))
        for name in ("Technik.md",):
            await db.execute(update(Note).where(Note.id == by_file[name].id)
                             .values(created_at=datetime(2026, 11, 8, 2, 2, tzinfo=timezone.utc),
                                     note_date=date(2026, 11, 8)))
        # Not on its import day: a date someone set on purpose, kept.
        await db.execute(update(Note).where(Note.id == by_file["Ohne Datum.md"].id)
                         .values(created_at=datetime(2026, 11, 8, 2, 2, tzinfo=timezone.utc),
                                 note_date=date(2026, 1, 15)))
        await db.commit()
    reset_sync_throttle()
    await _sync(client)
    dates = {n.cloud_filename: n.note_date for n in await _notes()}
    assert dates["20261108 Vorstandssitzung.md"] == date(2025, 10, 27)  # unchanged file: not re-read
    assert dates["Technik.md"] == date(2026, 11, 8)  # no fix without the migration's marker

    path = Path(__file__).resolve().parent.parent / "migrations" / "versions" / "0119_notes_reread_dates.py"
    spec = importlib.util.spec_from_file_location("migration_0119", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    statements = []
    monkeypatch.setattr(migration, "op", type("Op", (), {"execute": staticmethod(statements.append)}))
    migration.upgrade()
    async with AsyncSessionLocal() as db:
        for statement in statements:
            await db.execute(text(statement))
        await db.commit()

    reset_sync_throttle()
    await _sync(client)
    dates = {n.cloud_filename: n.note_date for n in await _notes()}
    assert dates == {
        "20261108 Vorstandssitzung.md": date(2026, 11, 8),  # file-name date
        "Technik.md": date(2025, 12, 13),  # import day -> the file's own date
        "Ohne Datum.md": date(2026, 1, 15),  # not the import day: kept
    }  # (a header date is taken on import and the header stripped, ADR 0127)
    async with AsyncSessionLocal() as db:  # one-time: the marker is gone
        assert await db.get(ClubSetting, "notes_redate_import_day_pending") is None
async def test_list_category_badge_filters_like_tags(client, admin_user):
    """Clicking a note's category in the list filters by it, the same
    way a tag badge already does (and the detail page already did)."""
    board = await _category("Board meeting")
    other = await _category("Other")
    await web_login(client, "admin@example.com")
    await _create(client, title="Im Vorstand", category_id=board)
    await _create(client, title="Woanders", category_id=other)

    page = await client.get("/notes/")
    assert f'href="/notes/?category={board}"' in page.text

    filtered = await client.get(f"/notes/?category={board}")
    assert "Im Vorstand" in filtered.text and "Woanders" not in filtered.text


async def _all_categories():
    async with AsyncSessionLocal() as db:
        return (await db.scalars(select(TaxonomyCategory))).all()


# ---------------------------------------------------------------------------
# Issue #305: a bookmark is a note with a source URL; one-time import of a
# bookmark export file (Nextcloud Bookmarks, any browser).
# ---------------------------------------------------------------------------

_BOOKMARK_FILE = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><A HREF="https://www.gesetze-im-internet.de/bkleingg/" ADD_DATE="1712246400" TAGS="Gesetz,Bund">BKleinGG</A>
    <DD>Bundeskleingartengesetz &amp; Kommentar
    <DT><H3 ADD_DATE="1700000000">Rechtliches</H3>
    <DL><p>
        <DT><A HREF="https://example.org/urteil" ADD_DATE="1704067200000" TAGS="">Urteil zur Laube</A>
        <DT><H3>Leipzig</H3>
        <DL><p>
            <DT><A HREF="https://example.org/slk" ADD_DATE="1704067200">SLK Recht</A>
            <DD>Mehrzeilige
            Beschreibung
        </DL><p>
        <DT><A HREF="javascript:alert(1)">Böser Link</A>
    </DL><p>
    <DT><A HREF="https://www.gesetze-im-internet.de/bkleingg/" TAGS="Wichtig">BKleinGG doppelt</A>
</DL><p>
"""


def test_source_url_in_note_file_and_url_safety():
    from app.note_files import clean_source_url

    text = render_note_file(note_id="a", title="Link", note_date=date(2026, 1, 2), category=None, tags=[],
                            body="x", source="https://example.org/a?b=1")
    assert 'source: "https://example.org/a?b=1"' in text
    assert parse_note_file(text.encode(), "x.md").source == "https://example.org/a?b=1"
    # "url:" (web clippers) works too; anything but http(s) is dropped.
    assert parse_note_file(b"---\nurl: https://example.org\n---\nx", "x.md").source == "https://example.org"
    for bad in ("javascript:alert(1)", "data:text/html,x", "ftp://example.org", "https://", "/relative",
                "https://exa mple.org", "https://example.org/\tx", "x" * 3000):
        assert clean_source_url(bad) is None, bad
        assert parse_note_file(f"---\nsource: {bad}\n---\nx".encode(), "x.md").source is None
    # render never writes an unsafe value
    assert "source:" not in render_note_file(note_id="a", title="L", note_date=date(2026, 1, 2), category=None,
                                             tags=[], body="", source="javascript:alert(1)")


def test_parse_bookmark_file_folders_tags_dates_duplicates():
    from app.bookmark_import import parse_bookmark_file

    bookmarks = parse_bookmark_file(_BOOKMARK_FILE.encode())
    by_title = {b.title: b for b in bookmarks}
    assert set(by_title) == {"BKleinGG", "Urteil zur Laube", "SLK Recht", "Böser Link"}  # duplicate merged
    law = by_title["BKleinGG"]
    assert law.url == "https://www.gesetze-im-internet.de/bkleingg/"
    assert law.added == date(2024, 4, 4) and law.description == "Bundeskleingartengesetz & Kommentar"
    assert law.tags == ["Gesetz", "Bund", "Wichtig"]  # the duplicate's tag merged in
    assert by_title["Urteil zur Laube"].tags == ["Rechtliches"]  # folder -> tag
    assert by_title["Urteil zur Laube"].added == date(2024, 1, 1)  # milliseconds
    slk = by_title["SLK Recht"]
    assert slk.tags == ["Rechtliches", "Leipzig"] and slk.description == "Mehrzeilige\nBeschreibung"
    assert by_title["Böser Link"].url is None


async def test_bookmark_import_creates_notes_in_root_and_is_safe_to_rerun(client, admin_user, monkeypatch):
    import base64 as b64
    import re

    cloud = await _enable_cloud(client, monkeypatch)
    preview = await client.post("/notes/import/bookmarks/preview",
                                files={"file": ("bookmarks.html", _BOOKMARK_FILE.encode(), "text/html")})
    assert preview.status_code == 200
    assert "3 new, 0 already exist" in preview.text
    assert "javascript:alert" in preview.text  # shown as text (autoescaped), never as a link
    assert 'href="javascript:' not in preview.text
    content_b64 = re.search(r'name="content_b64" value="([^"]+)"', preview.text).group(1)
    assert b64.b64decode(content_b64) == _BOOKMARK_FILE.encode()

    done = await client.post("/notes/import/bookmarks/finalize", data={"content_b64": content_b64})
    assert done.status_code == 303 and "error=" not in done.headers["location"]
    notes = {n.title: n for n in await _notes()}
    assert set(notes) == {"BKleinGG", "Urteil zur Laube", "SLK Recht"}
    slk = notes["SLK Recht"]
    assert slk.source_url == "https://example.org/slk" and slk.category is None
    assert slk.note_date == date(2024, 1, 1)
    assert sorted(t.name for t in slk.tags) == ["Leipzig", "Rechtliches"]
    # Files land in the notes folder root, holding just the text; the
    # source stays in Parcella (ADR 0127).
    assert all("/" not in n.cloud_filename for n in notes.values())
    assert cloud.text(slk.cloud_filename) == "Mehrzeilige\nBeschreibung\n"

    # The list links the source; re-running the import changes nothing.
    page = await client.get("/notes/")
    assert 'href="https://example.org/slk"' in page.text
    again = await client.post("/notes/import/bookmarks/finalize", data={"content_b64": content_b64})
    assert again.status_code == 303
    assert len(await _notes()) == 3


async def test_note_form_and_api_reject_non_http_source(client, admin_user):
    await web_login(client, "admin@example.com")
    response = await client.post("/notes/new", data={
        "title": "Böse", "note_date": "2026-03-04", "source_url": "javascript:alert(1)",
    })
    assert response.status_code == 400 and "http:// or https://" in response.text
    assert await _notes() == []

    note_id = await _create(client, title="Gut", source_url="https://example.org/x")
    detail = await client.get(f"/notes/{note_id}")
    assert 'href="https://example.org/x"' in detail.text and 'rel="noopener noreferrer nofollow"' in detail.text

    token = await login(client, "admin@example.com")
    api = await client.post("/api/v1/notes", headers=auth_header(token), json={
        "title": "API", "note_date": "2026-04-01", "source_url": "data:text/html,x",
    })
    assert api.status_code == 422
    api = await client.post("/api/v1/notes", headers=auth_header(token), json={
        "title": "API", "note_date": "2026-04-01", "source_url": "https://example.org/api",
    })
    assert api.status_code == 201 and api.json()["source_url"] == "https://example.org/api"


async def test_bookmark_import_needs_write_permission(client, admin_user):
    """Read-only users can't import (every import route checks 'write')."""
    import base64 as b64

    async with AsyncSessionLocal() as db:
        reader = User(email="reader@example.com", name="Reader", password_hash=hash_password("testpasswort123"),
                      role=UserRole.READONLY)
        group = Group(name="Note readers")
        db.add_all([reader, group])
        await db.flush()
        db.add(GroupModulePermission(group_id=group.id, module="notes", can_read=True))
        db.add(GroupMembership(user_id=reader.id, group_id=group.id))
        await db.commit()
    await web_login(client, "reader@example.com")
    assert (await client.get("/notes/import/bookmarks")).status_code == 403
    assert (await client.post("/notes/import/bookmarks/preview",
                              files={"file": ("b.html", _BOOKMARK_FILE.encode(), "text/html")})).status_code == 403
    assert (await client.post("/notes/import/bookmarks/finalize",
                              data={"content_b64": b64.b64encode(_BOOKMARK_FILE.encode()).decode()})).status_code == 403
    assert await _notes() == []
    assert "/notes/import/bookmarks" not in (await client.get("/notes/")).text


# ---------------------------------------------------------------------------
# Issue #311 (ADR 0127): metadata lives in Parcella, the cloud file holds
# only the text.
# ---------------------------------------------------------------------------

def _locked(*args, **kwargs):
    raise CloudStorageError("The file is locked in Nextcloud (HTTP 423)")


def _form(note, **fields):
    return {"title": note.title, "note_date": note.note_date.isoformat(), "body_markdown": note.body_markdown,
            "category_id": note.category_id or "", "tag_ids": [t.id for t in note.tags], **fields}


async def test_metadata_only_edit_never_touches_the_cloud(client, admin_user, monkeypatch):
    """The prod bug: changing title/tags/date/source of a note whose file
    was locked in a Nextcloud editor failed with HTTP 423."""
    cloud = await _enable_cloud(client, monkeypatch)
    category = await _category("Board meeting")
    note_id = await _create(client, category_id=category)
    [note] = await _notes()
    [name] = cloud.files
    before = cloud.files[name]

    async def locked(*args, **kwargs):
        _locked()

    cloud.upload_file = cloud.download_file = cloud.delete_file = cloud.list_files = locked
    saved = await client.post(f"/notes/{note_id}/edit", data=_form(
        note, title="Neuer Titel", note_date="2026-04-01", new_tags="Frist", source_url="https://example.org/x",
    ))
    assert saved.status_code == 303, saved.text
    [note] = await _notes()
    assert note.title == "Neuer Titel" and note.note_date == date(2026, 4, 1)
    assert [t.name for t in note.tags] == ["Frist"] and note.source_url == "https://example.org/x"
    assert not note.cloud_dirty and cloud.files[name] == before

    # Text changes do need the file: then the lock is reported, nothing saved.
    refused = await client.post(f"/notes/{note_id}/edit", data=_form(note, body_markdown="Neu"))
    assert refused.status_code == 502 and "locked" in refused.text
    [note] = await _notes()
    assert note.body_markdown == "# TOP 1\n\nWasseruhren tauschen."


async def test_category_move_with_a_locked_old_file_changes_nothing(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    board = await _category("Board meeting")
    other = await _category("Other")
    note_id = await _create(client, category_id=board)
    [note] = await _notes()
    real_delete = cloud.delete_file

    async def delete_unless_old(path, filename):
        if path.endswith("/Board meeting"):  # the old file is open in an editor
            _locked()
        await real_delete(path, filename)

    cloud.delete_file = delete_unless_old

    refused = await client.post(f"/notes/{note_id}/edit", data=_form(note, category_id=other))
    assert refused.status_code == 502
    # No second copy left behind: the new upload was taken back.
    assert list(cloud.files) == ["Board meeting/2026-03-04-vorstandssitzung-marz.md"]
    [note] = await _notes()
    assert note.category_id == board and note.cloud_filename == "Board meeting/2026-03-04-vorstandssitzung-marz.md"


async def test_only_category_changes_move_files(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    board = await _category("Board meeting")
    await _create(client, category_id=board, new_tags="Wasser")
    [note] = await _notes()
    tag_id = note.tags[0].id
    uploads = cloud.uploads

    await client.post(f"/notes/taxonomy/tags/{tag_id}/rename", data={"name": "Wasserleitung"})
    await client.post(f"/notes/taxonomy/categories/{board}/translations", data={"name_de": "Vorstand"})
    [note] = await _notes()
    assert not note.cloud_dirty  # the folder "Board meeting" still matches
    await client.post(f"/notes/taxonomy/categories/{board}/rename", data={"name": "Vorstandssitzung"})
    [note] = await _notes()
    assert note.cloud_dirty  # "Board meeting/" doesn't match any more
    await _sync(client)
    [note] = await _notes()
    assert note.cloud_filename == "Vorstandssitzung/2026-03-04-vorstandssitzung-marz.md" and not note.cloud_dirty
    assert cloud.uploads == uploads + 1


async def test_header_strip_after_migration_0122(client, admin_user, monkeypatch):
    """Files written before ADR 0127 carry a header. Migration 0122 sets a
    marker; the next sync reads every file, takes over header edits made
    in the cloud since the last sync once, and rewrites each as text."""
    import importlib.util
    from pathlib import Path
    from sqlalchemy import text, update

    cloud = await _enable_cloud(client, monkeypatch)
    await _create(client, title="Unverändert")
    await _create(client, title="In der Cloud geändert")
    by_title = {n.title: n for n in await _notes()}
    # Simulate pre-0127 files: a header in front of the text, hash matching.
    from app.note_files import content_hash
    async with AsyncSessionLocal() as db:
        for title, note in by_title.items():
            legacy = render_note_file(note_id=note.id, title=title, note_date=note.note_date, category=None,
                                      tags=["Alt"], body=note.body_markdown).encode()
            cloud.files[note.cloud_filename] = (legacy, f"legacy-{title}")
            await db.execute(update(Note).where(Note.id == note.id).values(
                cloud_hash=content_hash(legacy), cloud_fingerprint=f"legacy-{title}|{len(legacy)}"))
        await db.commit()
    changed = by_title["In der Cloud geändert"].cloud_filename
    cloud.put(changed, cloud.text(changed).replace('title: "In der Cloud geändert"', 'title: "Neu benannt"'))

    path = Path(__file__).resolve().parent.parent / "migrations" / "versions" / "0122_notes_strip_headers.py"
    spec = importlib.util.spec_from_file_location("migration_0122", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    statements = []
    monkeypatch.setattr(migration, "op", type("Op", (), {"execute": staticmethod(statements.append)}))
    migration.upgrade()
    async with AsyncSessionLocal() as db:
        for statement in statements:
            await db.execute(text(statement))
        await db.commit()

    await _sync(client)
    notes = {n.title: n for n in await _notes()}
    assert set(notes) == {"Unverändert", "Neu benannt"}
    assert [t.name for t in notes["Unverändert"].tags] == []  # unchanged file: Parcella's metadata kept
    assert [t.name for t in notes["Neu benannt"].tags] == ["Alt"]  # edited in the cloud: taken over once
    for note in notes.values():
        assert cloud.text(note.cloud_filename) == "# TOP 1\n\nWasseruhren tauschen.\n" and not note.cloud_dirty
    async with AsyncSessionLocal() as db:
        assert await db.get(ClubSetting, "notes_strip_headers_pending") is None


async def test_header_in_a_linked_file_is_ignored_and_stripped(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    await _create(client, new_tags="Wasser")
    [name] = cloud.files
    cloud.put(name, '---\ntitle: "Anders"\ntags: [Fremd]\n---\nNeuer Text')
    await _sync(client)
    [note] = await _notes()
    assert note.title == "Vorstandssitzung März" and [t.name for t in note.tags] == ["Wasser"]
    assert note.body_markdown == "Neuer Text" and cloud.text(name) == "Neuer Text\n"


async def test_relink_by_content_needs_one_non_empty_match(client, admin_user, monkeypatch):
    cloud = await _enable_cloud(client, monkeypatch)
    await _create(client, title="Leer A", body_markdown="")
    await _create(client, title="Leer B", body_markdown="")
    await _create(client, title="Gleich 1", body_markdown="Gleich")
    await _create(client, title="Gleich 2", body_markdown="Gleich")
    by_title = {n.title: n for n in await _notes()}
    for title in by_title:
        rel = by_title[title].cloud_filename
        cloud.files["umbenannt-" + rel] = cloud.files.pop(rel)
    await _sync(client)
    notes = await _notes()
    # Nothing could be told apart: the old notes go, the files come in as new.
    assert {n.id for n in notes}.isdisjoint({n.id for n in by_title.values()})
    assert len(notes) == 4


def test_body_file_keeps_a_leading_horizontal_rule():
    body = "---\n\nText\n\n---\nEnde"
    assert render_note_body(body) == body + "\n"
    parsed = parse_note_file(render_note_body(body).encode(), "x.md")
    assert not parsed.had_header and parsed.body == body
    assert render_note_body("") == "" and render_note_body("a\r\nb\n\n") == "a\nb\n"
