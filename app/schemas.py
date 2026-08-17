"""
Pydantic schemas for the REST API.

The separation from DB models (app/models.py) is deliberate: it lets
us keep API contracts stable even as internal models change, and have
different fields for creation vs. response.
"""
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from app.models import ParcelStatus, UserRole, TaskPriority


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    name: str
    role: UserRole
    is_active: bool
    avatar_filename: Optional[str] = None
    # True while the account is still on the initial-setup password and
    # can neither use the web UI nor obtain an API token (see
    # app/routers/api_auth.py).
    must_change_password: bool = False


# ---------------------------------------------------------------------------
# Phone / Email (sub-objects of Member)
# ---------------------------------------------------------------------------

class PhoneBase(BaseModel):
    number: str = Field(..., max_length=50)
    label: Optional[str] = Field(None, max_length=50)
    is_primary: bool = False


class PhoneCreate(PhoneBase):
    pass


class PhoneOut(PhoneBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class EmailAddressBase(BaseModel):
    address: EmailStr
    label: Optional[str] = Field(None, max_length=50)
    is_primary: bool = False


class EmailAddressCreate(EmailAddressBase):
    pass


class EmailAddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    address: str
    label: Optional[str] = None
    is_primary: bool


# ---------------------------------------------------------------------------
# Member
# ---------------------------------------------------------------------------

class MemberBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: Optional[date] = None
    street: Optional[str] = Field(None, max_length=255)
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    iban: Optional[str] = Field(None, max_length=34)
    member_since: Optional[date] = None
    member_until: Optional[date] = None
    email_notifications: bool = True
    notes: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    """All fields optional -- for PATCH-style partial updates via PUT."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    street: Optional[str] = Field(None, max_length=255)
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    iban: Optional[str] = Field(None, max_length=34)
    member_since: Optional[date] = None
    member_until: Optional[date] = None
    email_notifications: Optional[bool] = None
    notes: Optional[str] = None


class MemberAssignmentBrief(BaseModel):
    """Compact parcel info nested inside a member response."""
    model_config = ConfigDict(from_attributes=True)
    parcel_id: str
    plot_number: str
    is_invoice_address: bool


class MemberOut(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    phone_numbers: List[PhoneOut] = []
    email_addresses: List[EmailAddressOut] = []


class MemberDetailOut(MemberOut):
    """Extended view including assigned parcels, for GET /members/{id}."""
    parcels: List[MemberAssignmentBrief] = []


# ---------------------------------------------------------------------------
# Parcel
# ---------------------------------------------------------------------------

class ParcelBase(BaseModel):
    plot_number: str = Field(..., max_length=20)
    area_sqm: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    notes: Optional[str] = None


class ParcelCreate(ParcelBase):
    pass


class ParcelUpdate(BaseModel):
    plot_number: Optional[str] = Field(None, max_length=20)
    area_sqm: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: Optional[ParcelStatus] = None
    termination_note: Optional[str] = None
    notes: Optional[str] = None


class ParcelAssignmentBrief(BaseModel):
    """Kompakte Member-Info innerhalb einer Parcel-Antwort."""
    model_config = ConfigDict(from_attributes=True)
    member_id: str
    name: str
    is_invoice_address: bool


class ParcelOut(ParcelBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: ParcelStatus
    termination_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ParcelDetailOut(ParcelOut):
    members: List[ParcelAssignmentBrief] = []


# ---------------------------------------------------------------------------
# Member-Parcel assignment
# ---------------------------------------------------------------------------

class AssignmentCreate(BaseModel):
    member_id: str
    parcel_id: str
    is_invoice_address: bool = True
    assigned_from: Optional[date] = None
    assigned_until: Optional[date] = None


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    member_id: str
    parcel_id: str
    is_invoice_address: bool
    assigned_from: Optional[date] = None
    assigned_until: Optional[date] = None


# ---------------------------------------------------------------------------
# ClubSetting
# ---------------------------------------------------------------------------

class ClubSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class ClubSettingUpdate(BaseModel):
    value: Optional[str] = None


# ---------------------------------------------------------------------------
# ClubBoardMember (issue #111)
# ---------------------------------------------------------------------------

class BoardMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    member_id: str
    full_name: str


# ---------------------------------------------------------------------------
# Generic list response (pagination-ready)
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    gesamt: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Work Hours
# ---------------------------------------------------------------------------

class WorkHoursConfigurationBase(BaseModel):
    year: int
    hours_required: Decimal
    rate_per_hour_eur: Decimal
    mode: str = Field("PER_PARCEL", description="PER_PARCEL or PER_MEMBER")
    note: Optional[str] = None


class WorkHoursConfigurationCreate(WorkHoursConfigurationBase):
    pass


class WorkHoursConfigurationOut(WorkHoursConfigurationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ClubRoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    hours_exempt: bool = False
    exemption_reason: Optional[str] = None


class ClubRoleCreate(ClubRoleBase):
    pass


class ClubRoleOut(ClubRoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class MemberClubRoleCreate(BaseModel):
    member_id: str
    club_role_id: str
    year: int
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    note: Optional[str] = None


class MemberClubRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    member_id: str
    club_role_id: str
    year: int
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    note: Optional[str] = None


class WorkSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = Field("STANDARD", description="STANDARD or SPECIAL")
    date: date
    time_from: Optional[str] = None
    time_until: Optional[str] = None
    max_participants: Optional[int] = None
    hours_per_participant: Optional[Decimal] = None


class WorkSessionCreate(WorkSessionBase):
    pass


class WorkSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    date: Optional[date] = None
    time_from: Optional[str] = None
    time_until: Optional[str] = None
    max_participants: Optional[int] = None
    hours_per_participant: Optional[Decimal] = None


class WorkSessionOut(WorkSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class SessionParticipationCreate(BaseModel):
    member_id: str
    status: str = Field("ATTENDED", description="REGISTERED, ATTENDED or NO_SHOW")
    hours_completed: Optional[Decimal] = None
    note: Optional[str] = None


class SessionParticipationUpdate(BaseModel):
    status: Optional[str] = None
    hours_completed: Optional[Decimal] = None
    note: Optional[str] = None


class SessionParticipationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    member_id: str
    status: str
    hours_completed: Optional[Decimal] = None
    note: Optional[str] = None


class SponsorshipBase(BaseModel):
    area: str
    description: Optional[str] = None
    credited_hours: Decimal
    valid_from: date
    valid_until: Optional[date] = None


class SponsorshipCreate(SponsorshipBase):
    member_id: Optional[str] = None


class SponsorshipUpdate(BaseModel):
    member_id: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None
    credited_hours: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class SponsorshipOut(SponsorshipBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    member_id: Optional[str] = None


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    workload: str = "MODERATE"  # LIGHT | MODERATE | DEMANDING


class TaskCreate(TaskBase):
    session_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    workload: Optional[str] = None
    session_id: Optional[str] = None
    assigned_participation_id: Optional[str] = None
    is_done: Optional[bool] = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: Optional[str] = None
    assigned_participation_id: Optional[str] = None
    is_done: bool


class EvaluationRowOut(BaseModel):
    """One row of the work-hours annual evaluation."""
    label: str
    hours_required: Decimal
    hours_completed: Decimal
    hours_open: Decimal
    amount_due_eur: Decimal
    exempt: bool
    fulfilled: bool


# ---------------------------------------------------------------------------
# Metering (water & electricity) -- medium-agnostic schemas
# ---------------------------------------------------------------------------

class MeteringPointBase(BaseModel):
    type: str = Field(..., description="MAIN_METER, PARCEL or CLUB")
    parcel_id: Optional[str] = None
    label: Optional[str] = None
    notes: Optional[str] = None


class MeteringPointCreate(MeteringPointBase):
    # First meter is created directly alongside it
    number: str
    calibrated_until: Optional[int] = None
    installed_at: Optional[date] = None
    initial_reading: Decimal = Decimal("0")


class MeteringPointUpdate(BaseModel):
    label: Optional[str] = None
    notes: Optional[str] = None


class MeterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    number: str
    is_active: bool
    calibrated_until: Optional[int] = None
    installed_at: Optional[date] = None
    removed_at: Optional[date] = None
    initial_reading: Decimal


class MeteringPointOut(MeteringPointBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    medium: str


class MeteringPointDetailOut(MeteringPointOut):
    current_meter: Optional[MeterOut] = None
    former_meters: List[MeterOut] = []


class MeteringPriceConfigurationBase(BaseModel):
    medium: str = Field(..., description="WATER or ELECTRICITY")
    year: int
    price_per_unit: Decimal
    note: Optional[str] = None


class MeteringPriceConfigurationCreate(MeteringPriceConfigurationBase):
    pass


class MeteringPriceConfigurationOut(MeteringPriceConfigurationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class MeterSwapRequest(BaseModel):
    new_number: str
    removed_at: date
    installed_at: date
    calibrated_until: Optional[int] = None
    initial_reading: Decimal = Decimal("0")


class MeterReadingCreate(BaseModel):
    year: int
    date: date
    reading: Decimal
    note: Optional[str] = None


class MeterReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    meter_id: str
    year: int
    date: date
    reading: Decimal
    note: Optional[str] = None


class ConsumptionRowOut(BaseModel):
    """One row of the consumption evaluation (MeteringPoint + calculated consumption)."""
    metering_point_id: str
    label: str
    meter_number: Optional[str] = None
    consumption: Optional[Decimal] = None


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

class PropertyInsurancePackageBase(BaseModel):
    year: int
    name: str
    amount_eur: Decimal
    sort_order: int = 0


class PropertyInsurancePackageCreate(PropertyInsurancePackageBase):
    pass


class PropertyInsurancePackageOut(PropertyInsurancePackageBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class InsuranceConfigurationBase(BaseModel):
    year: int
    accident_base_amount_eur: Decimal
    accident_additional_amount_eur: Decimal


class InsuranceConfigurationCreate(InsuranceConfigurationBase):
    pass


class InsuranceConfigurationOut(InsuranceConfigurationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ParcelInsuranceUpdate(BaseModel):
    has_property_insurance: bool = False
    property_package_id: Optional[str] = None
    has_accident_insurance: bool = False
    additional_person_member_ids: List[str] = []


class ParcelInsuranceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    parcel_id: str
    year: int
    has_property_insurance: bool
    property_package_id: Optional[str] = None
    has_accident_insurance: bool


class ParcelInsuranceCostOut(ParcelInsuranceOut):
    additional_person_member_ids: List[str] = []
    property_cost_eur: Decimal
    accident_cost_eur: Decimal
    total_cost_eur: Decimal


# ---------------------------------------------------------------------------
# Ticket system
# ---------------------------------------------------------------------------

class TicketMessageCreate(BaseModel):
    direction: str = Field("OUTGOING", description="INCOMING, OUTGOING oder INTERNAL")
    content: str


class TicketMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    ticket_id: str
    direction: str
    content: str
    authored_by_id: Optional[str] = None
    created_at: datetime


class TicketCreate(BaseModel):
    subject: str
    sender_email: EmailStr
    sender_name: Optional[str] = None
    message: str = Field(..., description="First message of the ticket (stored as INCOMING)")


class TicketStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="ACTIVE, WAITING, POSTPONED, CLOSED or DELETED. "
        "ASSIGNED is set automatically via PUT /{ticket_id}/assignment and cannot be set directly.",
    )
    postponed_until: Optional[date] = None


class TicketAssignmentUpdate(BaseModel):
    assigned_to_id: Optional[str] = Field(None, description="Empty/None = clear assignment")


class TicketMemberUpdate(BaseModel):
    member_id: Optional[str] = None


class TicketSpamUpdate(BaseModel):
    spam_suspected: bool = Field(..., description="false to clear a spam suspicion (false positive)")


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subject: str
    status: str
    assigned_to_id: Optional[str] = None
    postponed_until: Optional[date] = None
    member_id: Optional[str] = None
    sender_email: str
    sender_name: Optional[str] = None
    spam_suspected: bool
    spam_score: Optional[Decimal] = None
    spam_reasoning: Optional[str] = None
    spam_reviewed_by_id: Optional[str] = None
    spam_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None


class TicketDetailOut(TicketOut):
    messages: List[TicketMessageOut] = []


# ---------------------------------------------------------------------------
# Purchase Requests
# ---------------------------------------------------------------------------

class PurchaseRequestCreate(BaseModel):
    title: str
    justification: str
    link: Optional[str] = None
    estimated_cost_eur: Optional[Decimal] = None
    requester_name: Optional[str] = Field(None, description="Only when created for an external person")
    requester_email: Optional[EmailStr] = Field(None, description="Only when created for an external person")


class PurchaseRequestRejectRequest(BaseModel):
    rejection_reason: str


class PurchaseRequestApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    approved_at: datetime


class PurchaseRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    justification: str
    link: Optional[str] = None
    estimated_cost_eur: Optional[Decimal] = None
    status: str
    requested_by_id: Optional[str] = None
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    created_by_id: Optional[str] = None
    confirmed_by_requester: bool
    rejection_reason: Optional[str] = None
    rejected_by_id: Optional[str] = None
    rejected_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime


class PurchaseRequestDetailOut(PurchaseRequestOut):
    approvals: List[PurchaseRequestApprovalOut] = []


# ---------------------------------------------------------------------------
# Public signup API (see app/routers/api_public.py) -- deliberately its own
# small schema set, independent from WorkSessionOut/ParcelOut above: this is
# an external, CMS-agnostic contract, so it should keep changing on its own
# terms rather than accidentally following internal-API refactors.
# ---------------------------------------------------------------------------

class PublicWorkSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    date: date
    time_from: Optional[str] = None
    time_until: Optional[str] = None
    spots_left: Optional[int] = Field(None, description="null = no capacity limit")


class PublicParcelOut(BaseModel):
    """No 'id' field, deliberately: this is the unauthenticated public
    signup endpoint, matched by plot_number string (see
    PublicSignupCreate) -- the reference WordPress connector never uses
    the parcel's internal UUID, so there's no reason to hand it to every
    unauthenticated caller (flagged by an external pentest as IDOR
    reconnaissance value)."""
    model_config = ConfigDict(from_attributes=True)
    plot_number: str


class PublicSignupCreate(BaseModel):
    parcel_number: str = Field(..., description="Plot number, e.g. 'G042', as shown on the parcel dropdown")
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    remarks: Optional[str] = None
    session_ids: List[str] = Field(..., min_length=1, description="One or more work session IDs from the upcoming-sessions listing")
    # Honeypot: real visitors never see or fill this field (hidden via CSS
    # in the reference WordPress connector). Left non-empty by simple bots
    # that fill in every field they find. Not documented in the public API
    # docs' example payload on purpose.
    website: Optional[str] = Field(None, description="Leave empty")

    @field_validator("name", "phone", "email", "remarks", "website", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        # HTML forms send empty optional fields as "", not absent -- most
        # visibly a problem for `email`, where EmailStr rejects "" outright
        # (a real bug hit via the WordPress connector: an untouched email
        # field caused a 422 on every submission). Treating blank strings
        # as "not provided" here fixes it for every connector, not just
        # that one.
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


class PublicSignupSessionResult(BaseModel):
    session_id: str
    accepted: bool
    reason: Optional[str] = Field(None, description="Set when accepted=false, e.g. session full")


class PublicSignupResult(BaseModel):
    results: List[PublicSignupSessionResult]


class PublicContactCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    message: str = Field(..., min_length=1)
    consent: bool = Field(..., description="Must be true -- data-protection consent given at submission")
    # Honeypot, same convention as PublicSignupCreate.website above.
    website: Optional[str] = Field(None, description="Leave empty")

    @field_validator("website", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


class PublicContactResult(BaseModel):
    accepted: bool
    reason: Optional[str] = Field(None, description="Set when accepted=false, e.g. missing consent")


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class InventoryCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryOut(InventoryCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class InventoryItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    owner_type: str = Field("CLUB", description="CLUB or MEMBER")
    owner_member_id: Optional[str] = Field(None, description="Required when owner_type = MEMBER")
    storage_location: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    current_value_updated_at: Optional[date] = None
    replacement_cost: Optional[Decimal] = None
    quantity_total: int = 1
    is_borrowable: bool = False
    default_loan_fee: Optional[Decimal] = None
    notes: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(InventoryItemBase):
    pass


class InventoryItemOut(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    retired_at: Optional[datetime] = None
    quantity_on_loan: int
    available_quantity: int
    created_at: datetime
    updated_at: datetime


class ItemLoanCreate(BaseModel):
    member_id: str
    quantity: int = 1
    borrowed_date: date
    fee_charged: Optional[Decimal] = None
    note: Optional[str] = None


class ItemLoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    item_id: str
    member_id: str
    quantity: int
    borrowed_date: date
    returned_date: Optional[date] = None
    fee_charged: Optional[Decimal] = None
    note: Optional[str] = None
    created_at: datetime


class ItemLoanReturn(BaseModel):
    returned_date: Optional[date] = Field(None, description="Defaults to today if not given")


# ---------------------------------------------------------------------------
# Task board (kanban) -- deliberately prefixed KanbanTask*, not Task*: the
# work-hours module above already defines Task{Base,Create,Update,Out} for
# WorkTask, and Python would silently let this section's classes shadow
# those (same names, later definition wins) instead of raising an error.
# ---------------------------------------------------------------------------

class KanbanTaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    tags: List[str] = Field(default_factory=list)
    assigned_to_ids: List[str] = Field(default_factory=list)


class KanbanTaskCreate(KanbanTaskBase):
    list_id: Optional[str] = Field(None, description="Defaults to the first list on the board")


class KanbanTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = None
    assigned_to_ids: Optional[List[str]] = None


class KanbanTaskMove(BaseModel):
    list_id: str
    position: int = Field(..., ge=0, description="Target index within the list (0-based)")


class KanbanTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    description: Optional[str] = None
    list_id: str
    position: int
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    tags: List[str] = Field(default_factory=list)
    assigned_to_ids: List[str] = Field(default_factory=list)
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class KanbanTaskListCreate(BaseModel):
    name: str = Field(..., max_length=100)


class KanbanTaskListUpdate(BaseModel):
    name: str = Field(..., max_length=100)


class KanbanTaskListMove(BaseModel):
    position: int = Field(..., ge=0, description="Target index among all lists (0-based)")


class KanbanTaskListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    position: int
    created_at: datetime


class KanbanTaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class KanbanTaskCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    task_id: str
    content: str
    created_by_id: Optional[str] = None
    created_at: datetime
