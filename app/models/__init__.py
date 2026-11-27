"""Database models for the allotment garden association management app.

Design principles:
- All tables use UUID as primary key (production-ready, no rate-guessing)
- Soft-delete where sensible (deleted_at instead of a real delete)
- Audit fields (created_at, updated_at) everywhere

The models are a package by domain (issue #416, ADR 0146). Add a new model
to its domain's module, or a new module, and re-export it here: the rest
of the app imports everything from `app.models`.
"""

from app.models._common import (  # noqa: F401
    new_uuid,
)
from app.models.parcels import (  # noqa: F401
    ParcelStatus,
    Parcel,
    MemberParcel,
    ParcelCloudFolder,
)
from app.models.users import (  # noqa: F401
    UserRole,
    InvitationStatus,
    User,
    ApiToken,
    Invitation,
    Group,
    GroupMembership,
    InvitationGroupTarget,
    GroupModulePermission,
)
from app.models.members import (  # noqa: F401
    Member,
    MemberTag,
    member_tag_links,
    MemberPhone,
    MemberEmail,
)
from app.models.contacts import (  # noqa: F401
    ExternalContactKind,
    ExternalContact,
    ExternalContactTag,
    external_contact_tag_links,
    ExternalContactPhone,
    ExternalContactEmail,
)
from app.models.club import (  # noqa: F401
    ClubSetting,
    ClubBoardMember,
    SampleDataRecord,
    ChangeHistory,
    EmailLogStatus,
    EmailLog,
)
from app.models.work_hours import (  # noqa: F401
    WorkHoursMode,
    WorkHoursConfiguration,
    ExemptionReason,
    ClubRole,
    MemberClubRole,
    Sponsorship,
    SessionType,
    HoursTransfer,
    ParticipationStatus,
    WorkSession,
    SessionParticipation,
    TaskWorkload,
    WorkTask,
)
from app.models.metering import (  # noqa: F401
    MeteringMedium,
    MeteringPointType,
    MeteringPoint,
    Meter,
    MeterReading,
    MeteringPriceConfiguration,
)
from app.models.insurance import (  # noqa: F401
    PropertyInsurancePackage,
    InsuranceConfiguration,
    ParcelInsurance,
    AccidentInsuranceHouseholdMember,
    AccidentInsuranceAdditionalPerson,
)
from app.models.helpdesk import (  # noqa: F401
    HelpdeskConversationLink,
    HelpdeskCustomerId,
)
from app.models.purchase_requests import (  # noqa: F401
    PurchaseRequestStatus,
    PurchaseRequest,
    PurchaseRequestApproval,
    PurchaseRequestComment,
)
from app.models.calendars import (  # noqa: F401
    CalendarEventType,
    CalendarEvent,
    CustomCalendar,
    CouncilPresence,
    CouncilAbsence,
)
from app.models.announcements import (  # noqa: F401
    AnnouncementChannel,
    AnnouncementDeliveryStatus,
    Announcement,
    AnnouncementDelivery,
)
from app.models.inventory import (  # noqa: F401
    InventoryOwnerType,
    InventoryCategory,
    InventoryItem,
    ItemLoan,
)
from app.models.tasks import (  # noqa: F401
    TaskPriority,
    TaskList,
    Task,
    TASK_TAG_COLORS,
    TASK_TAG_DEFAULT_COLOR,
    TaskTag,
    task_tag_links,
    TaskAssignee,
    TaskComment,
    ExternalTaskLink,
)
from app.models.finances import (  # noqa: F401
    FinanceCategoryGroup,
    FinanceCategory,
    FinanceBudgetLine,
    FinanceAccountType,
    FinanceAccount,
    InvoiceRunStatus,
    InvoicePricingMode,
    InvoiceRun,
    InvoiceItemTemplate,
    InvoiceItemTemplateParcel,
    InvoiceItemTemplateMember,
    InvoiceItemDefinition,
    InvoiceItemDefinitionParcel,
    InvoiceItemDefinitionMember,
    Invoice,
    InvoiceLineItem,
    InvoicePayment,
    AccountTransaction,
    IncomingInvoice,
    IncomingInvoiceLineItem,
    IncomingInvoicePayment,
    InvoiceReminder,
)
from app.models.applicants import (  # noqa: F401
    ApplicantStatus,
    APPLICANT_OPEN_STATUSES,
    ApplicantSource,
    Applicant,
)
from app.models.notes import (  # noqa: F401
    TaxonomyCategory,
    TaxonomyTag,
    note_tag_links,
    Note,
)
from app.models.processes import (  # noqa: F401
    ProcessSubjectKind,
    ProcessFieldKind,
    ProcessStatus,
    ProcessEventKind,
    ProcessFileStorage,
    ProcessTemplate,
    ProcessTemplateStage,
    ProcessTemplateField,
    Process,
    ProcessStage,
    ProcessField,
    ProcessFile,
    ProcessEvent,
)
