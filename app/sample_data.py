"""
Sample data generator: lets an admin doing a fresh setup add realistic
demo data across every module with one click, and remove exactly that
data again with another. See ADR 0037.

Every row created here is logged in SampleDataRecord (module,
entity_type, entity_id) as it's inserted -- entity_type is a model
class name, resolved against the fixed _MODEL_BY_ENTITY_TYPE registry
below, never a dynamic import or a name-pattern guess. Removal deletes
exactly what was tracked, in a fixed leaf-to-root order (_DELETION_ORDER)
so it never depends on ON DELETE cascade behavior -- important because
this only ever deletes rows THIS feature created, never anything an
admin entered themselves, even if the admin has since added real
records that happen to reference a sample row.

No fake Users are ever created here -- User accounts are a security
boundary, out of scope for "demo data." Anywhere a module optionally
references a User (ticket assignment, purchase-request approval,
created_by/recorded_by fields), this generator either uses a real
existing account or leaves the field NULL/uses the module's own
external-party fields (e.g. PurchaseRequest.requester_name).
"""
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.insurance_utils import household_grouping
from app.models import (
    AccidentInsuranceAdditionalPerson,
    CalendarEvent,
    CalendarEventType,
    FinanceCategory,
    FinanceCategoryGroup,
    FreescoutConversationLink,
    InsuranceConfiguration,
    InventoryCategory,
    InventoryItem,
    InventoryOwnerType,
    ItemLoan,
    Member,
    MemberEmail,
    MemberParcel,
    Meter,
    MeteringMedium,
    MeteringPoint,
    MeteringPointType,
    MeterReading,
    Parcel,
    ParcelInsurance,
    ParcelStatus,
    PropertyInsurancePackage,
    PurchaseRequest,
    PurchaseRequestApproval,
    PurchaseRequestStatus,
    SampleDataRecord,
    SessionParticipation,
    ParticipationStatus,
    Task,
    TaskList,
    TaskWorkload,
    User,
    UserRole,
    WorkHoursConfiguration,
    WorkHoursMode,
    WorkSession,
    SessionType,
    WorkTask,
    new_uuid,
)
from app.task_board import next_position

# ---------------------------------------------------------------------------
# Tracking helper
# ---------------------------------------------------------------------------


def _track(db: AsyncSession, module: str, obj) -> None:
    db.add(SampleDataRecord(
        id=new_uuid(), module=module, entity_type=type(obj).__name__, entity_id=obj.id,
    ))


# ---------------------------------------------------------------------------
# Deletion registry -- leaf-to-root, so nothing is ever deleted before the
# rows that reference it. See module docstring for why this doesn't just
# rely on ON DELETE cascade.
# ---------------------------------------------------------------------------

_MODEL_BY_ENTITY_TYPE = {
    "FinanceCategory": FinanceCategory,
    "FreescoutConversationLink": FreescoutConversationLink,
    "PurchaseRequestApproval": PurchaseRequestApproval,
    "PurchaseRequest": PurchaseRequest,
    "CalendarEvent": CalendarEvent,
    "ItemLoan": ItemLoan,
    "InventoryItem": InventoryItem,
    "InventoryCategory": InventoryCategory,
    "Task": Task,
    "WorkTask": WorkTask,
    "SessionParticipation": SessionParticipation,
    "WorkSession": WorkSession,
    "WorkHoursConfiguration": WorkHoursConfiguration,
    "MeterReading": MeterReading,
    "Meter": Meter,
    "MeteringPoint": MeteringPoint,
    "AccidentInsuranceAdditionalPerson": AccidentInsuranceAdditionalPerson,
    "ParcelInsurance": ParcelInsurance,
    "PropertyInsurancePackage": PropertyInsurancePackage,
    "InsuranceConfiguration": InsuranceConfiguration,
    "MemberParcel": MemberParcel,
    "MemberEmail": MemberEmail,
    "Parcel": Parcel,
    "Member": Member,
}

_DELETION_ORDER = list(_MODEL_BY_ENTITY_TYPE.keys())

# Module keys, in the order they're generated (core first -- everything
# else references members/parcels).
MODULES = [
    "core", "work_hours", "metering", "insurance",
    "freescout_bridge", "purchase_requests", "calendar", "inventory", "tasks", "finances",
]


class SampleDataBlockedError(Exception):
    """Raised when add_sample_data() is refused because real (non-sample) data already exists."""


# ---------------------------------------------------------------------------
# Status queries (used by the admin page and the guard below)
# ---------------------------------------------------------------------------


async def has_real_core_data(db: AsyncSession) -> bool:
    """True if any Member or Parcel exists that this generator didn't create itself."""
    sample_member_ids = select(SampleDataRecord.entity_id).where(SampleDataRecord.entity_type == "Member")
    sample_parcel_ids = select(SampleDataRecord.entity_id).where(SampleDataRecord.entity_type == "Parcel")

    real_member = await db.scalar(select(Member.id).where(Member.id.not_in(sample_member_ids)).limit(1))
    if real_member:
        return True
    real_parcel = await db.scalar(select(Parcel.id).where(Parcel.id.not_in(sample_parcel_ids)).limit(1))
    return real_parcel is not None


async def sample_data_counts(db: AsyncSession) -> dict:
    """Row counts per module currently tracked (0 for every module if none exists)."""
    result = await db.execute(select(SampleDataRecord.module, SampleDataRecord.entity_type))
    rows = result.all()
    counts = {module: 0 for module in MODULES}
    for module, _entity_type in rows:
        counts[module] = counts.get(module, 0) + 1
    return counts


async def has_sample_data(db: AsyncSession) -> bool:
    return await db.scalar(select(SampleDataRecord.id).limit(1)) is not None


# ---------------------------------------------------------------------------
# Removal
# ---------------------------------------------------------------------------


async def remove_sample_data(db: AsyncSession) -> int:
    """Deletes exactly the rows tracked in SampleDataRecord, leaf-to-root. Returns the count removed."""
    total = 0
    for entity_type in _DELETION_ORDER:
        model = _MODEL_BY_ENTITY_TYPE[entity_type]
        result = await db.execute(
            select(SampleDataRecord.entity_id).where(SampleDataRecord.entity_type == entity_type)
        )
        ids = [row[0] for row in result.all()]
        for entity_id in ids:
            obj = await db.get(model, entity_id)
            if obj is not None:
                await db.delete(obj)
        await db.flush()
        await db.execute(delete(SampleDataRecord).where(SampleDataRecord.entity_type == entity_type))
        total += len(ids)

    # Safety net: clear any tracked rows whose entity_type isn't in the
    # fixed order above (shouldn't happen -- every generator below uses
    # only types listed there -- but never leave orphaned tracking rows).
    await db.execute(delete(SampleDataRecord))
    await db.commit()
    return total


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


async def add_sample_data(db: AsyncSession) -> dict:
    """
    Creates sample data across core, every default-on module, and
    Finances (off by default, but seeded here anyway -- issue #67's
    "optional to import SKR42, go with a couple of example data when
    set in /admin/sample-data" -- module flags only govern nav/route
    visibility, not whether sample rows exist). Refuses
    (SampleDataBlockedError) if real member/parcel data already exists,
    so this stays a fresh-install tool.
    """
    if await has_real_core_data(db):
        raise SampleDataBlockedError(
            "Sample data can only be added to a fresh installation -- this club already has real member/parcel data."
        )

    members, parcels, assignments = await _seed_core(db)
    await _seed_work_hours(db, members)
    await _seed_metering(db, parcels)
    await _seed_insurance(db, parcels, assignments)
    await _seed_freescout_bridge(db, members)
    await _seed_purchase_requests(db)
    await _seed_calendar(db)
    await _seed_inventory(db, members)
    await _seed_tasks(db)
    await _seed_finances(db)

    await db.commit()
    return await sample_data_counts(db)


def _member(first_name: str, last_name: str, street: str, postal_code: str, city: str, years_ago: int) -> Member:
    return Member(
        id=new_uuid(),
        first_name=first_name, last_name=last_name,
        street=street, postal_code=postal_code, city=city,
        member_since=date.today() - timedelta(days=365 * years_ago),
    )


async def _seed_core(db: AsyncSession):
    people = [
        _member("Anna", "Bergmann", "Gartenweg 3", "12345", "Musterstadt", 4),
        _member("Jonas", "Bergmann", "Gartenweg 3", "12345", "Musterstadt", 4),  # same address as Anna -> household
        _member("Klara", "Hoffmann", "Lindenallee 8", "54321", "Beispielhausen", 2),
        _member("Peter", "Wagner", "Rosenstrasse 2", "67890", "Kleinstadt", 6),
        _member("Sofia", "Keller", "Birkenweg 15", "11223", "Andersdorf", 1),
        _member("Tom", "Fischer", "Ahornallee 21", "33445", "Beispielhausen", 3),
    ]
    for m in people:
        db.add(m)
        _track(db, "core", m)
    anna, jonas, klara, peter, sofia, tom = people

    for m, local_part in [
        (anna, "anna.bergmann"), (jonas, "jonas.bergmann"), (klara, "klara.hoffmann"),
        (peter, "peter.wagner"), (sofia, "sofia.keller"), (tom, "tom.fischer"),
    ]:
        email = MemberEmail(id=new_uuid(), member_id=m.id, address=f"{local_part}@example.invalid", is_primary=True)
        db.add(email)
        _track(db, "core", email)

    today = date.today()
    parcels = [
        Parcel(id=new_uuid(), plot_number="DEMO-01", area_sqm=350, status=ParcelStatus.ACTIVE),
        Parcel(id=new_uuid(), plot_number="DEMO-02", area_sqm=280, status=ParcelStatus.ACTIVE),
        Parcel(id=new_uuid(), plot_number="DEMO-03", area_sqm=400, status=ParcelStatus.ACTIVE),
        Parcel(id=new_uuid(), plot_number="DEMO-04", area_sqm=320, status=ParcelStatus.TERMINATED,
               termination_note="Sample data: terminated for demonstration."),
        Parcel(id=new_uuid(), plot_number="DEMO-05", area_sqm=300, status=ParcelStatus.ACTIVE),
    ]
    for p in parcels:
        db.add(p)
        _track(db, "core", p)
    demo01, demo02, demo03, demo04, demo05 = parcels

    def assign(member: Member, parcel: Parcel, is_invoice_address: bool, assigned_until: Optional[date] = None) -> MemberParcel:
        mp = MemberParcel(
            id=new_uuid(), member_id=member.id, parcel_id=parcel.id,
            is_invoice_address=is_invoice_address,
            assigned_from=today - timedelta(days=365 * 2),
            assigned_until=assigned_until,
        )
        mp.member = member  # populate in-memory for household_grouping(), no DB round-trip needed
        db.add(mp)
        _track(db, "core", mp)
        return mp

    assignments = [
        assign(anna, demo01, is_invoice_address=True),
        assign(jonas, demo01, is_invoice_address=False),
        assign(klara, demo02, is_invoice_address=True),
        assign(peter, demo03, is_invoice_address=True),
        assign(sofia, demo03, is_invoice_address=False),
        # Former tenant: assignment already ended -- must be False per the
        # is_invoice_address CHECK constraint (see ADR 0035).
        assign(tom, demo04, is_invoice_address=False, assigned_until=today - timedelta(days=60)),
        # demo05 stays vacant.
    ]

    return people, parcels, assignments


async def _seed_work_hours(db: AsyncSession, members: list) -> None:
    anna, jonas, klara, peter, sofia, tom = members
    year = date.today().year

    config = WorkHoursConfiguration(
        id=new_uuid(), year=year, hours_required=10, rate_per_hour_eur=15,
        mode=WorkHoursMode.PER_PARCEL, note="Sample data",
    )
    db.add(config)
    _track(db, "work_hours", config)

    past_session = WorkSession(
        id=new_uuid(), title="Spring cleanup", type=SessionType.STANDARD,
        date=date.today() - timedelta(days=30), time_from="09:00", time_until="12:00",
        hours_per_participant=3,
    )
    db.add(past_session)
    _track(db, "work_hours", past_session)

    p1 = SessionParticipation(id=new_uuid(), session_id=past_session.id, member_id=anna.id,
                               status=ParticipationStatus.ATTENDED, hours_completed=3)
    p2 = SessionParticipation(id=new_uuid(), session_id=past_session.id, member_id=klara.id,
                               status=ParticipationStatus.ATTENDED, hours_completed=4)
    p3 = SessionParticipation(id=new_uuid(), session_id=past_session.id, member_id=peter.id,
                               status=ParticipationStatus.NO_SHOW)
    for p in (p1, p2, p3):
        db.add(p)
        _track(db, "work_hours", p)

    upcoming_session = WorkSession(
        id=new_uuid(), title="Fence repair", type=SessionType.STANDARD,
        date=date.today() + timedelta(days=14), time_from="09:00", time_until="13:00",
        max_participants=8, hours_per_participant=4,
    )
    db.add(upcoming_session)
    _track(db, "work_hours", upcoming_session)

    p4 = SessionParticipation(id=new_uuid(), session_id=upcoming_session.id, member_id=jonas.id,
                               status=ParticipationStatus.REGISTERED)
    db.add(p4)
    _track(db, "work_hours", p4)

    backlog_task = WorkTask(id=new_uuid(), title="Trim hedge at the clubhouse", workload=TaskWorkload.MODERATE)
    scheduled_task = WorkTask(id=new_uuid(), title="Sort tool shed", workload=TaskWorkload.LIGHT,
                              session_id=upcoming_session.id)
    assigned_task = WorkTask(id=new_uuid(), title="Buy fence paint", workload=TaskWorkload.LIGHT,
                             session_id=upcoming_session.id, assigned_participation_id=p4.id)
    for t in (backlog_task, scheduled_task, assigned_task):
        db.add(t)
        _track(db, "work_hours", t)


async def _seed_metering(db: AsyncSession, parcels: list) -> None:
    demo01, demo02 = parcels[0], parcels[1]
    year = date.today().year

    water_point = MeteringPoint(id=new_uuid(), medium=MeteringMedium.WATER,
                                type=MeteringPointType.PARCEL, parcel_id=demo01.id)
    db.add(water_point)
    _track(db, "metering", water_point)

    water_meter = Meter(id=new_uuid(), metering_point_id=water_point.id, number="W-DEMO-01",
                        initial_reading=0, installed_at=date.today() - timedelta(days=365 * 2))
    db.add(water_meter)
    _track(db, "metering", water_meter)

    for offset_year, reading in ((1, 120.5), (0, 145.0)):
        r = MeterReading(id=new_uuid(), meter_id=water_meter.id, year=year - offset_year,
                          date=date(year - offset_year, 10, 1), reading=reading)
        db.add(r)
        _track(db, "metering", r)

    electricity_point = MeteringPoint(id=new_uuid(), medium=MeteringMedium.ELECTRICITY,
                                      type=MeteringPointType.PARCEL, parcel_id=demo02.id)
    db.add(electricity_point)
    _track(db, "metering", electricity_point)

    electricity_meter = Meter(id=new_uuid(), metering_point_id=electricity_point.id, number="E-DEMO-02",
                              initial_reading=0, installed_at=date.today() - timedelta(days=365 * 2))
    db.add(electricity_meter)
    _track(db, "metering", electricity_meter)

    for offset_year, reading in ((1, 800), (0, 950)):
        r = MeterReading(id=new_uuid(), meter_id=electricity_meter.id, year=year - offset_year,
                          date=date(year - offset_year, 10, 1), reading=reading)
        db.add(r)
        _track(db, "metering", r)


async def _seed_insurance(db: AsyncSession, parcels: list, assignments: list) -> None:
    demo01, demo03 = parcels[0], parcels[2]
    year = date.today().year

    config = InsuranceConfiguration(id=new_uuid(), year=year,
                                    accident_base_amount_eur=25.00, accident_additional_amount_eur=8.00)
    db.add(config)
    _track(db, "insurance", config)

    basic_pkg = PropertyInsurancePackage(id=new_uuid(), year=year, name="Basic cover", amount_eur=40.00, sort_order=0)
    extended_pkg = PropertyInsurancePackage(id=new_uuid(), year=year, name="Extended cover", amount_eur=65.00, sort_order=1)
    db.add(basic_pkg)
    db.add(extended_pkg)
    _track(db, "insurance", basic_pkg)
    _track(db, "insurance", extended_pkg)

    pi1 = ParcelInsurance(id=new_uuid(), parcel_id=demo01.id, year=year,
                          has_property_insurance=True, property_package_id=basic_pkg.id,
                          has_accident_insurance=True)
    pi2 = ParcelInsurance(id=new_uuid(), parcel_id=demo03.id, year=year,
                          has_property_insurance=True, property_package_id=extended_pkg.id,
                          has_accident_insurance=True)
    db.add(pi1)
    db.add(pi2)
    _track(db, "insurance", pi1)
    _track(db, "insurance", pi2)

    # demo03 = Peter + Sofia at different addresses -- whichever
    # household_grouping() calls "external" needs an explicit additional-
    # person row for the accident insurance to actually cover them (see
    # app/insurance_utils.py; deliberately not assumed here, computed).
    demo03_assignments = [a for a in assignments if a.parcel_id == demo03.id]
    grouping = household_grouping(demo03_assignments)
    for member in grouping["external"]:
        additional = AccidentInsuranceAdditionalPerson(id=new_uuid(), parcel_insurance_id=pi2.id, member_id=member.id)
        db.add(additional)
        _track(db, "insurance", additional)


async def _seed_freescout_bridge(db: AsyncSession, members: list) -> None:
    """
    Demo FreescoutConversationLink rows -- deliberately no live FreeScout
    API call (sample data must work on a fresh install with no external
    services configured). These are cross-reference rows only, same as
    the real poller writes; there's no local message content to seed
    since the actual transcript is always fetched live from FreeScout.
    """
    anna, jonas, klara, peter, sofia, tom = members

    def make(freescout_conversation_id: int, subject: str, customer_email: str, customer_name: str,
              member_id: Optional[str], status: str, **extra) -> FreescoutConversationLink:
        link = FreescoutConversationLink(
            id=new_uuid(), freescout_conversation_id=freescout_conversation_id, freescout_mailbox_id=1,
            subject=subject, customer_email=customer_email, customer_name=customer_name,
            member_id=member_id, freescout_status=status,
            freescout_updated_at=datetime.now(timezone.utc), **extra,
        )
        db.add(link)
        _track(db, "freescout_bridge", link)
        return link

    make(
        9001, "Question about the fence height on plot DEMO-01", "anna.bergmann@example.invalid", "Anna Bergmann",
        anna.id, "active", message_count=1,
    )
    make(
        9002, "Leaking tap near plot DEMO-03", "sofia.keller@example.invalid", "Sofia Keller",
        sofia.id, "active", message_count=3,
    )
    make(
        9003, "Replacement membership card", "klara.hoffmann@example.invalid", "Klara Hoffmann",
        klara.id, "pending", message_count=2,
    )
    make(
        9004, "Compost delivery schedule", "unknown.visitor@example.invalid", None,
        None, "pending", message_count=1,
    )
    make(
        9005, "Thanks for the quick repair", "tom.fischer@example.invalid", "Tom Fischer",
        tom.id, "closed", message_count=2,
    )


async def _seed_purchase_requests(db: AsyncSession) -> None:
    board_users_result = await db.execute(
        select(User).where(User.role.in_([UserRole.ADMIN, UserRole.BOARD]), User.is_active == True)
    )
    board_users = board_users_result.scalars().all()

    open_request = PurchaseRequest(
        id=new_uuid(), title="Replacement locks for the tool shed",
        justification="Current locks are rusted and hard to open.",
        estimated_cost_eur=45.00, requester_name="Peter Wagner", requester_email="peter.wagner@example.invalid",
        status=PurchaseRequestStatus.OPEN,
    )
    db.add(open_request)
    _track(db, "purchase_requests", open_request)

    rejected_request = PurchaseRequest(
        id=new_uuid(), title="Branded club merchandise (T-shirts)",
        justification="Requested by several members for the summer festival.",
        estimated_cost_eur=600.00, requester_name="Klara Hoffmann", requester_email="klara.hoffmann@example.invalid",
        status=PurchaseRequestStatus.REJECTED,
        rejected_by_id=board_users[0].id if board_users else None,
        rejected_at=datetime.now(timezone.utc),
        rejection_reason="Budget already allocated for this year -- revisit next season.",
    )
    db.add(rejected_request)
    _track(db, "purchase_requests", rejected_request)

    if len(board_users) >= 2:
        approved_request = PurchaseRequest(
            id=new_uuid(), title="New wheelbarrows for communal use",
            justification="Current wheelbarrows are broken; members have been lending personal ones.",
            estimated_cost_eur=250.00, requester_name="Anna Bergmann", requester_email="anna.bergmann@example.invalid",
            status=PurchaseRequestStatus.APPROVED, approved_at=datetime.now(timezone.utc),
        )
        db.add(approved_request)
        _track(db, "purchase_requests", approved_request)
        for user in board_users[:2]:
            approval = PurchaseRequestApproval(id=new_uuid(), purchase_request_id=approved_request.id, user_id=user.id)
            db.add(approval)
            _track(db, "purchase_requests", approval)


async def _seed_calendar(db: AsyncSession) -> None:
    events = [
        CalendarEvent(id=new_uuid(), event_type=CalendarEventType.OTHER, title="Winter general meeting",
                      start_date=date.today() - timedelta(days=200), start_time="18:00", location="Clubhouse"),
        CalendarEvent(id=new_uuid(), event_type=CalendarEventType.PARCEL_INSPECTION, title="Spring parcel inspection round",
                      start_date=date.today() + timedelta(days=20), start_time="10:00"),
        CalendarEvent(id=new_uuid(), event_type=CalendarEventType.MEMBER_MEETING, title="Annual General Meeting",
                      start_date=date.today() + timedelta(days=60), start_time="18:00", location="Clubhouse"),
        CalendarEvent(id=new_uuid(), event_type=CalendarEventType.OTHER, title="Summer Festival",
                      start_date=date.today() + timedelta(days=90),
                      end_date=date.today() + timedelta(days=91), location="Club grounds"),
    ]
    for e in events:
        db.add(e)
        _track(db, "calendar", e)


async def _seed_inventory(db: AsyncSession, members: list) -> None:
    _anna, _jonas, klara, _peter, sofia, _tom = members

    tools_cat = InventoryCategory(id=new_uuid(), name="Garden Tools")
    furniture_cat = InventoryCategory(id=new_uuid(), name="Furniture & Structures")
    db.add(tools_cat)
    db.add(furniture_cat)
    _track(db, "inventory", tools_cat)
    _track(db, "inventory", furniture_cat)

    wheelbarrow = InventoryItem(
        id=new_uuid(), category_id=tools_cat.id, name="Wheelbarrow (blue)",
        owner_type=InventoryOwnerType.CLUB, quantity_total=2, is_borrowable=True, default_loan_fee=0,
        storage_location="Tool shed", purchase_price=80.00,
    )
    tables = InventoryItem(
        id=new_uuid(), category_id=furniture_cat.id, name="Folding tables (set of 4)",
        owner_type=InventoryOwnerType.CLUB, quantity_total=1, is_borrowable=True, default_loan_fee=5.00,
        storage_location="Clubhouse storage",
    )
    mower = InventoryItem(
        id=new_uuid(), category_id=tools_cat.id, name="Lawn mower",
        owner_type=InventoryOwnerType.CLUB, quantity_total=1, is_borrowable=False,
        storage_location="Tool shed", purchase_price=350.00, current_value=250.00,
        current_value_updated_at=date.today(),
    )
    greenhouse = InventoryItem(
        id=new_uuid(), name="Small greenhouse (member-owned, stored on-site)",
        owner_type=InventoryOwnerType.MEMBER, owner_member_id=klara.id,
        quantity_total=1, storage_location="Behind plot DEMO-02",
    )
    for item in (wheelbarrow, tables, mower, greenhouse):
        db.add(item)
        _track(db, "inventory", item)

    loan = ItemLoan(
        id=new_uuid(), item_id=wheelbarrow.id, member_id=sofia.id, quantity=1,
        borrowed_date=date.today() - timedelta(days=5),
    )
    db.add(loan)
    _track(db, "inventory", loan)


async def _seed_tasks(db: AsyncSession) -> None:
    # The migration seeds "To Do"/"In Progress"/"Done" as the default
    # lists -- looked up by name here since sample data always runs
    # after migrations.
    result = await db.execute(
        select(TaskList).where(TaskList.name.in_(["To Do", "In Progress", "Done"]))
    )
    list_ids = {task_list.name: task_list.id for task_list in result.scalars().all()}

    cards = [
        ("To Do", "Order new signage for the entrance"),
        ("To Do", "Schedule tree trimming with contractor"),
        ("In Progress", "Repair clubhouse roof leak"),
        ("Done", "Renew public liability insurance"),
        ("Done", "Update website contact page"),
    ]
    for list_name, title in cards:
        list_id = list_ids[list_name]
        position = await next_position(db, list_id)
        task = Task(id=new_uuid(), title=title, list_id=list_id, position=position)
        db.add(task)
        _track(db, "tasks", task)


async def _seed_finances(db: AsyncSession) -> None:
    """A handful of clearly-illustrative bookkeeping categories (issue
    #67) -- NOT a transcription of DATEV's copyrighted SKR42 chart
    (see FinanceCategory's docstring in app/models.py), just enough of
    a starting point across the three groups the issue itself named
    (income/expenses/fixed assets) that the feature isn't empty on
    first use. A club replaces or extends these with its own real
    chart via CSV import."""
    categories = [
        FinanceCategory(id=new_uuid(), code="40000", title="Membership fees", group=FinanceCategoryGroup.INCOME),
        FinanceCategory(id=new_uuid(), code="60020", title="Ehrenamtspauschale", group=FinanceCategoryGroup.EXPENSE),
        FinanceCategory(id=new_uuid(), code="00100", title="Garden equipment", group=FinanceCategoryGroup.FIXED_ASSETS),
    ]
    for c in categories:
        db.add(c)
        _track(db, "finances", c)
