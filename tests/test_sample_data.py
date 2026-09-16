from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import (
    Member, Parcel, MemberParcel, SampleDataRecord,
    FreescoutConversationLink, PurchaseRequest, PurchaseRequestStatus,
    Task, TaskList, User,
)
from app.sample_data import (
    add_sample_data, remove_sample_data, has_real_core_data,
    has_sample_data, sample_data_counts, SampleDataBlockedError,
    _MODEL_BY_ENTITY_TYPE, _DELETION_ORDER,
)


def test_deletion_order_covers_every_registered_entity_type():
    assert set(_DELETION_ORDER) == set(_MODEL_BY_ENTITY_TYPE.keys())


async def _seed_task_lists(db):
    """Mirrors migration 0054_task_lists's seed data -- the test DB is
    built straight from models via create_all (see conftest.py), not
    Alembic, so tests seed their own lists before _seed_tasks() (which
    looks them up by name) runs."""
    for position, name in enumerate(["To Do", "In Progress", "Done"]):
        db.add(TaskList(name=name, position=position))
    await db.commit()


async def test_add_sample_data_populates_every_module(board_user, second_board_user):
    async with AsyncSessionLocal() as db:
        await _seed_task_lists(db)
        counts = await add_sample_data(db)

        assert all(count > 0 for count in counts.values()), counts

        member_count = await db.scalar(select(Member.id).limit(1))
        assert member_count is not None

        # Core: one parcel (DEMO-01) should have a member marked as
        # invoice address and one not, per app/sample_data.py.
        result = await db.execute(
            select(MemberParcel).join(Parcel).where(Parcel.plot_number == "DEMO-01")
        )
        demo01_assignments = result.scalars().all()
        assert len(demo01_assignments) == 2
        assert sum(1 for a in demo01_assignments if a.is_invoice_address) == 1

        # The former tenant on DEMO-04 must not hold the invoice-address
        # flag (see the CHECK constraint from ADR 0035/0036).
        result = await db.execute(
            select(MemberParcel).join(Parcel).where(Parcel.plot_number == "DEMO-04")
        )
        demo04_assignment = result.scalars().one()
        assert demo04_assignment.assigned_until is not None
        assert demo04_assignment.is_invoice_address is False

        # FreeScout bridge: every demo conversation status should be
        # represented, and the unmatched one should have no member.
        result = await db.execute(select(FreescoutConversationLink.freescout_status, FreescoutConversationLink.member_id))
        rows = result.all()
        statuses = {status for status, _ in rows}
        assert "active" in statuses
        assert "pending" in statuses
        assert "closed" in statuses
        assert any(member_id is None for _, member_id in rows)

        # Purchase requests: with 2 distinct board users available, all
        # three states should exist.
        result = await db.execute(select(PurchaseRequest.status))
        pr_statuses = [row[0] for row in result.all()]
        assert PurchaseRequestStatus.OPEN in pr_statuses
        assert PurchaseRequestStatus.REJECTED in pr_statuses
        assert PurchaseRequestStatus.APPROVED in pr_statuses

        # Task board: positions must be a gapless 0..n-1 sequence per list.
        result = await db.execute(select(TaskList.id))
        for (list_id,) in result.all():
            result = await db.execute(
                select(Task.position).where(Task.list_id == list_id).order_by(Task.position)
            )
            positions = [row[0] for row in result.all()]
            assert positions == list(range(len(positions))), (list_id, positions)

        assert await has_sample_data(db) is True


async def test_add_sample_data_blocked_when_real_member_exists():
    async with AsyncSessionLocal() as db:
        db.add(Member(id="real-member-1", first_name="Real", last_name="Member"))
        await db.commit()

        assert await has_real_core_data(db) is True
        try:
            await add_sample_data(db)
            assert False, "expected SampleDataBlockedError"
        except SampleDataBlockedError:
            pass

        # Nothing should have been created.
        assert await has_sample_data(db) is False


async def test_add_sample_data_blocked_when_real_parcel_exists():
    async with AsyncSessionLocal() as db:
        db.add(Parcel(id="real-parcel-1", plot_number="R001"))
        await db.commit()

        try:
            await add_sample_data(db)
            assert False, "expected SampleDataBlockedError"
        except SampleDataBlockedError:
            pass


async def test_remove_sample_data_deletes_everything_and_only_that(admin_user):
    async with AsyncSessionLocal() as db:
        await _seed_task_lists(db)
        await add_sample_data(db)

        removed = await remove_sample_data(db)
        assert removed > 0

        assert await has_sample_data(db) is False
        for module, count in (await sample_data_counts(db)).items():
            assert count == 0, (module, count)

        # Nothing tracked remains in the source tables either.
        assert await db.scalar(select(Member.id).limit(1)) is None
        assert await db.scalar(select(Parcel.id).limit(1)) is None
        assert await db.scalar(select(FreescoutConversationLink.id).limit(1)) is None
        assert await db.scalar(select(SampleDataRecord.id).limit(1)) is None

        # The real admin user (used as a purchase-request approver
        # candidate) must survive untouched.
        user = await db.get(User, admin_user.id)
        assert user is not None
