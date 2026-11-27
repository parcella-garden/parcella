"""Finances: categories, budget, accounts, invoice runs, invoices, payments."""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models._common import new_uuid


# ---------------------------------------------------------------------------
# Finances: annual invoices (issues #55/#56/#57/#58), bookkeeping
# categories (issue #67)
# ---------------------------------------------------------------------------

class FinanceCategoryGroup(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    FIXED_ASSETS = "FIXED_ASSETS"
    EQUITY_LIABILITIES = "EQUITY_LIABILITIES"
    OTHER = "OTHER"


class FinanceCategory(Base):
    """
    A bookkeeping category (issue #67): a short code (e.g. "40000") and
    title (e.g. "Membership fees"), grouped into a small set of
    accounting-style buckets. Loosely inspired by German chart-of-
    accounts conventions (the issue references SKR42) without claiming
    to reproduce one -- SKR42 itself is DATEV's copyrighted structure,
    so this app doesn't ship any of its actual codes; a club imports
    its own real chart via CSV instead (see the import route in
    app/routers/finances/bookkeeping.py) or types categories in by hand.
    """
    __tablename__ = "finance_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(5), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    group: Mapped[FinanceCategoryGroup] = mapped_column(SAEnum(FinanceCategoryGroup), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<FinanceCategory {self.code} {self.title!r}>"


class FinanceBudgetLine(Base):
    """The planned amount for one category in one year (issue #248's
    budget plan). Only plans are stored; the past and current years'
    actuals next to them come from the cash accounting statement
    (app/accounting_statement.py) every time -- see docs/ADR/0113.
    No row = nothing planned."""
    __tablename__ = "finance_budget_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("finance_categories.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    category: Mapped["FinanceCategory"] = relationship("FinanceCategory")

    __table_args__ = (
        UniqueConstraint("year", "category_id", name="uq_finance_budget_line_year_category"),
    )


class FinanceAccountType(str, enum.Enum):
    BANK = "BANK"
    CASH = "CASH"


class FinanceAccount(Base):
    """
    A club's real-world bank or cash account (issue #156), e.g. an old
    and a new giro account plus a deposit account, or a cash box.
    Started as purely a tag on InvoicePayment -- no manual transactions,
    no opening balance, just a sum of the payments recorded against it
    -- but issue #174 deliberately reopened that "not a ledger" stance:
    an account's booking list now also includes AccountTransaction rows
    (any money movement that isn't tied to a specific invoice -- a
    refund, a purchase, a bank fee), manually entered or CSV-imported.
    See ADR 0059. Still freely hard-deletable like FinanceCategory
    (InvoicePayment.account_id is ON DELETE SET NULL, so a payment
    record itself is never lost, only its account attribution --
    AccountTransaction rows, which only exist *for* this account, are
    CASCADE-deleted instead).

    `is_active` lets an old/closed account (the user's own "one old and
    one new giro account" example) stay around for its already-recorded
    bookings' sake without still being offered when recording a new one.
    """
    __tablename__ = "finance_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[FinanceAccountType] = mapped_column(SAEnum(FinanceAccountType), nullable=False)
    account_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<FinanceAccount {self.name!r} ({self.account_type})>"


class InvoiceRunStatus(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class InvoicePricingMode(str, enum.Enum):
    FIXED_PER_PARCEL = "fixed_per_parcel"
    FIXED_PER_PERSON = "fixed_per_person"
    PER_SQM = "per_sqm"
    WATER_USAGE = "water_usage"
    ELECTRICITY_USAGE = "electricity_usage"
    INSURANCE_COST = "insurance_cost"
    COMMUNAL_AREA_SHARE = "communal_area_share"
    WORK_HOURS_SHORTFALL = "work_hours_shortfall"
    PUBLIC_BURDENS = "public_burdens"
    GENERAL_LEVY = "general_levy"


class InvoiceRun(Base):
    """
    A single "annual invoices" batch (issue #55). Item definitions are
    configured while the run is DRAFT; generating invoices assigns
    permanent invoice numbers and moves it to FINALIZED (see
    app/invoice_generation.py) -- regenerating a still-DRAFT run must
    not skip or reuse numbers, which is why numbering only happens once,
    at finalization.
    """
    __tablename__ = "invoice_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Free text below the line-item table. Supports {invoice_number},
    # {parcel_number}, {invoice_address}, {due_date} placeholders,
    # substituted per-invoice at PDF render time (see app/invoice_pdf.py).
    footer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[InvoiceRunStatus] = mapped_column(
        SAEnum(InvoiceRunStatus), default=InvoiceRunStatus.DRAFT, nullable=False, index=True
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    item_definitions: Mapped[List["InvoiceItemDefinition"]] = relationship(
        "InvoiceItemDefinition", back_populates="invoice_run",
        cascade="all, delete-orphan", order_by="InvoiceItemDefinition.order_number",
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="invoice_run", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InvoiceRun {self.year} ({self.status.value})>"


class InvoiceItemTemplate(Base):
    """
    A reusable catalog of billable line items (e.g. "Membership fee",
    "Water usage") a board member curates once, so building a new
    run's items means picking from a visible, known-good list instead
    of blindly copying everything from a specific past run (which may
    have included one-off items). Fields mirror InvoiceItemDefinition,
    including specific per-parcel scoping (parcel_scopes, used when
    applies_to_all_parcels=False) -- copied verbatim onto the new
    InvoiceItemDefinition when applied to a run (see
    app/routers/finances/runs.py's items_add_from_catalog) and freely
    editable on the template itself at any time, same as on a run's
    own item.
    """
    __tablename__ = "invoice_item_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    order_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pricing_mode: Mapped[InvoicePricingMode] = mapped_column(SAEnum(InvoicePricingMode), nullable=False)
    unit_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # Same meaning as InvoiceItemDefinition.applies_to_all_parcels --
    # defaults to True to match this catalog's original behavior
    # (every item applied to all parcels, unconditionally) before this
    # toggle existed, so existing templates keep working exactly as
    # before until someone deliberately unchecks it.
    applies_to_all_parcels: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Only meaningful for FIXED_PER_PERSON, mirroring
    # applies_to_all_parcels/parcel_scopes above but over members
    # instead of parcels -- a person-scoped fee (e.g. annual dues) is
    # billed to targeted members directly, regardless of whether they
    # currently have a parcel. Defaults to True to keep the picker
    # simple by default (mirrors applies_to_all_parcels' own default),
    # and is meaningless/ignored for every other pricing mode. See
    # app/invoice_generation.py's _compute_member_invoices.
    applies_to_all_members: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_categories.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    category: Mapped[Optional["FinanceCategory"]] = relationship("FinanceCategory")
    parcel_scopes: Mapped[List["InvoiceItemTemplateParcel"]] = relationship(
        "InvoiceItemTemplateParcel", back_populates="item_template", cascade="all, delete-orphan",
    )
    member_scopes: Mapped[List["InvoiceItemTemplateMember"]] = relationship(
        "InvoiceItemTemplateMember", back_populates="item_template", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InvoiceItemTemplate {self.name!r} ({self.pricing_mode.value})>"


class InvoiceItemTemplateParcel(Base):
    """Explicit parcel inclusion for an InvoiceItemTemplate where
    applies_to_all_parcels=False -- mirrors InvoiceItemDefinitionParcel."""
    __tablename__ = "invoice_item_template_parcels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_item_template_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_item_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )

    item_template: Mapped["InvoiceItemTemplate"] = relationship(
        "InvoiceItemTemplate", back_populates="parcel_scopes"
    )
    parcel: Mapped["Parcel"] = relationship("Parcel")

    __table_args__ = (
        UniqueConstraint("invoice_item_template_id", "parcel_id", name="uq_invoice_item_template_parcel"),
    )


class InvoiceItemTemplateMember(Base):
    """Explicit member inclusion for an InvoiceItemTemplate where
    applies_to_all_members=False (FIXED_PER_PERSON only) -- mirrors
    InvoiceItemTemplateParcel, but over members instead of parcels."""
    __tablename__ = "invoice_item_template_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_item_template_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_item_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )

    item_template: Mapped["InvoiceItemTemplate"] = relationship(
        "InvoiceItemTemplate", back_populates="member_scopes"
    )
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("invoice_item_template_id", "member_id", name="uq_invoice_item_template_member"),
    )


class InvoiceItemDefinition(Base):
    """
    One line-item type within an InvoiceRun (e.g. "Membership fee",
    "Water usage 2026"), applied to every in-scope parcel when the run
    is generated. `pricing_mode` decides where quantity/price come from
    -- WATER_USAGE/ELECTRICITY_USAGE pull quantity from
    app/meter_utils.py's calculate_consumption() and price from
    MeteringPriceConfiguration (per medium/year), ignoring unit_price
    entirely, same as WORK_HOURS_SHORTFALL/INSURANCE_COST already do;
    INSURANCE_COST pulls its whole amount from app/insurance_utils.py's
    calculate_insurance_cost().
    """
    __tablename__ = "invoice_item_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pricing_mode: Mapped[InvoicePricingMode] = mapped_column(
        SAEnum(InvoicePricingMode), nullable=False
    )
    unit_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # "assign all or specific parcels to be accounted or not" (issue #56):
    # True = every currently-occupied parcel; False = only the parcels
    # explicitly listed in `parcel_scopes`.
    applies_to_all_parcels: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Only meaningful for FIXED_PER_PERSON, mirroring
    # applies_to_all_parcels/parcel_scopes above but over members --
    # a person-scoped fee (e.g. annual dues, honorary membership) is
    # billed to targeted members directly, regardless of whether they
    # currently have a parcel. FIXED_PER_PERSON items are excluded from
    # the parcel loop entirely (see compute_invoices_for_run) and
    # handled solely via this + member_scopes in
    # _compute_member_invoices. Meaningless/ignored for every other
    # pricing mode. Defaults to True, mirroring applies_to_all_parcels.
    applies_to_all_members: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Optional bookkeeping category (issue #67) -- purely for the
    # club's own accounting/reporting, doesn't affect invoice
    # generation. SET NULL rather than blocking deletion, so removing
    # a category never blocks removing/editing an item that used it.
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_categories.id", ondelete="SET NULL"), nullable=True
    )

    invoice_run: Mapped["InvoiceRun"] = relationship("InvoiceRun", back_populates="item_definitions")
    parcel_scopes: Mapped[List["InvoiceItemDefinitionParcel"]] = relationship(
        "InvoiceItemDefinitionParcel", back_populates="item_definition", cascade="all, delete-orphan",
    )
    member_scopes: Mapped[List["InvoiceItemDefinitionMember"]] = relationship(
        "InvoiceItemDefinitionMember", back_populates="item_definition", cascade="all, delete-orphan",
    )
    category: Mapped[Optional["FinanceCategory"]] = relationship("FinanceCategory")

    def __repr__(self) -> str:
        return f"<InvoiceItemDefinition {self.name!r} ({self.pricing_mode.value})>"


class InvoiceItemDefinitionParcel(Base):
    """Explicit parcel inclusion for an InvoiceItemDefinition where
    applies_to_all_parcels=False."""
    __tablename__ = "invoice_item_definition_parcels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_item_definition_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_item_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )

    item_definition: Mapped["InvoiceItemDefinition"] = relationship(
        "InvoiceItemDefinition", back_populates="parcel_scopes"
    )
    parcel: Mapped["Parcel"] = relationship("Parcel")

    __table_args__ = (
        UniqueConstraint("invoice_item_definition_id", "parcel_id", name="uq_invoice_item_definition_parcel"),
    )


class InvoiceItemDefinitionMember(Base):
    """Explicit member inclusion for an InvoiceItemDefinition where
    applies_to_all_members=False (FIXED_PER_PERSON only) -- mirrors
    InvoiceItemDefinitionParcel, but over members instead of parcels."""
    __tablename__ = "invoice_item_definition_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_item_definition_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_item_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True
    )

    item_definition: Mapped["InvoiceItemDefinition"] = relationship(
        "InvoiceItemDefinition", back_populates="member_scopes"
    )
    member: Mapped["Member"] = relationship("Member")

    __table_args__ = (
        UniqueConstraint("invoice_item_definition_id", "member_id", name="uq_invoice_item_definition_member"),
    )


class Invoice(Base):
    """
    One invoice for one parcel, OR (for a fixed_per_person item) one
    directly-targeted club member -- e.g. annual dues or a supporting
    membership fee, regardless of current parcel status -- within an
    InvoiceRun (issue #57). Exactly one of parcel_id/member_id is set,
    enforced by ck_invoice_exactly_one_subject. recipient_names/
    recipient_address are snapshotted at generation time -- a member
    moving (or losing their parcel, or being deleted) later must not
    silently rewrite a historical invoice. The four *_at timestamps
    track delivery (issue #58): emailed, included in a print bundle,
    uploaded to the parcel's cloud folder (member invoices have no
    cloud-folder concept, see app/invoice_delivery.py). Payment status
    is derived from `payments` rather than stored, so it can never go
    stale.
    """
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoice_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("parcels.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # SET NULL (not CASCADE) since recipient_names/recipient_address are
    # already a full snapshot -- an invoice must survive its member
    # being deleted later, same as parcel invoices already survive a
    # member move.
    member_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("members.id", ondelete="SET NULL"), nullable=True, index=True
    )

    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    # The raw, unformatted sequence number within invoice_run.year --
    # numbering (app/invoice_generation.py) reads MAX(sequence_number)
    # scoped to the year to find the next one, rather than parsing it
    # back out of invoice_number, since invoice_number's *display*
    # format is club-configurable (issue #65) and a past invoice's
    # format must never change once assigned.
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient_names: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_address: Mapped[str] = mapped_column(Text, nullable=False)
    # Issue #396: one copy per address the parcel's invoice-address
    # tenants live at -- [{"names", "address", "member_ids"}], largest
    # group first. Same invoice (number, amount, debt); only the address
    # window differs. recipient_names then lists everyone, and
    # recipient_address is the first copy's. NULL for member invoices
    # and invoices from before #396: one copy, the two columns above.
    # See app/invoice_delivery.py's invoice_copies().
    recipient_copies: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    pdf_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    emailed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_to_cloud_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    invoice_run: Mapped["InvoiceRun"] = relationship("InvoiceRun", back_populates="invoices")
    parcel: Mapped[Optional["Parcel"]] = relationship("Parcel")
    member: Mapped[Optional["Member"]] = relationship("Member")
    line_items: Mapped[List["InvoiceLineItem"]] = relationship(
        "InvoiceLineItem", back_populates="invoice",
        cascade="all, delete-orphan", order_by="InvoiceLineItem.order_number",
    )
    payments: Mapped[List["InvoicePayment"]] = relationship(
        "InvoicePayment", back_populates="invoice",
        cascade="all, delete-orphan", order_by="InvoicePayment.paid_on",
    )
    reminders: Mapped[List["InvoiceReminder"]] = relationship(
        "InvoiceReminder", back_populates="invoice",
        cascade="all, delete-orphan", order_by="InvoiceReminder.level",
    )

    __table_args__ = (
        CheckConstraint(
            "(parcel_id IS NOT NULL AND member_id IS NULL) OR (parcel_id IS NULL AND member_id IS NOT NULL)",
            name="ck_invoice_exactly_one_subject",
        ),
    )

    @property
    def paid_total(self) -> float:
        return float(sum((p.amount for p in self.payments), 0))

    @property
    def reminder_fees_total(self) -> float:
        return float(sum((r.fee_amount or 0 for r in self.reminders), 0))

    @property
    def total_owed(self) -> float:
        """Original subtotal plus any reminder fees -- what "paid"
        actually requires (issue #59)."""
        return float(self.subtotal) + self.reminder_fees_total

    @property
    def amount_due(self) -> float:
        """What's still owed, including any reminder fees on top of
        the original subtotal (issue #59) -- never goes negative for
        display purposes even if overpaid."""
        return max(0.0, self.total_owed - self.paid_total)

    @property
    def payment_status(self) -> str:
        """One of "open" / "partially_paid" / "paid", derived from
        payments vs. subtotal + any reminder fees (issue #58's "let me
        filter which outgoing invoice is open/paid/partially paid";
        extended by issue #59 so a reminder fee actually counts toward
        what "paid" requires)."""
        paid = self.paid_total
        if paid <= 0:
            return "open"
        if paid < self.total_owed:
            return "partially_paid"
        return "paid"

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number}>"


class InvoiceLineItem(Base):
    """One priced line on an Invoice, generated from an InvoiceItemDefinition.

    category_id is copied from the originating InvoiceItemDefinition at
    finalize time (issue #179's cash-based accounting statement needs
    it to attribute income by category) -- nullable, `ON DELETE
    SET NULL` since a category disappearing later must never invalidate
    a historical, already-finalized invoice. This field didn't exist
    before issue #179, so line items on invoices finalized earlier are
    permanently uncategorized; there was never a link back to the
    originating definition to backfill from."""
    __tablename__ = "invoice_line_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="line_items")
    category: Mapped[Optional["FinanceCategory"]] = relationship("FinanceCategory")


class InvoicePayment(Base):
    """A single (possibly partial) payment recorded against an Invoice
    (issue #58's "system for partial payment, more than one date")."""
    __tablename__ = "invoice_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_on: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    recorded_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    recorded_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recorded_by_id])
    account: Mapped[Optional["FinanceAccount"]] = relationship("FinanceAccount")

    def __repr__(self) -> str:
        return f"<InvoicePayment {self.amount} on {self.paid_on}>"


class AccountTransaction(Base):
    """A manual or CSV-imported ledger entry against a FinanceAccount
    (issue #174) -- unlike InvoicePayment (always tied to a specific
    invoice), this covers any other money movement on the account (a
    refund, a purchase, a bank fee, interest, etc.). Deliberately
    reopens FinanceAccount's original "not a ledger" stance (issue
    #156) -- confirmed with the reporter; see ADR 0059.

    amount is signed (positive = credit/deposit, negative = debit/
    withdrawal), matching how a bank statement CSV export normally
    represents it -- there's no separate "type" field to keep in sync
    with the sign.
    """
    __tablename__ = "account_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("finance_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Who sent or received the money (issue #185) -- entered by hand or
    # via an optional CSV column, free text since a bank statement's
    # counterparty name has no fixed structure to validate against.
    counterparty: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # "manual" (entered by hand) or "csv_import" -- kept for internal
    # bookkeeping (e.g. only non-invoice rows are deletable from the
    # bookings list) but no longer shown or filterable in the UI itself
    # (issue #184: "it does not matter").
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    recorded_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    account: Mapped["FinanceAccount"] = relationship("FinanceAccount")
    recorded_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recorded_by_id])

    def __repr__(self) -> str:
        return f"<AccountTransaction {self.amount} on {self.booking_date}>"


class IncomingInvoice(Base):
    """A bill the club received from a supplier/vendor (issue #178) --
    the mirror image of Invoice (which the club sends out), but far
    simpler: recorded directly by hand, no generation/finalization
    phases. May have several cost positions, each tagged with its own
    FinanceCategory (IncomingInvoiceLineItem) -- e.g. one bill covering
    both insurance and maintenance costs.

    The actual scanned/photographed bill, if any, is never stored in
    this app's own database or filesystem (per CLAUDE.md's "the app
    itself does not store any media" constraint) -- cloud_filename
    just names a file inside the single shared cloud folder configured
    for incoming invoices (ClubSetting "incoming_invoices_cloud_folder"),
    same Nextcloud connection ParcelCloudFolder already uses.
    """
    __tablename__ = "incoming_invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cloud_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Optional link to the external contact who sent it (ADR 0096) --
    # alongside `sender`, not instead of it: search, the accounting
    # statement and bank matching all read the free-text sender.
    external_contact_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("external_contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    external_contact: Mapped[Optional["ExternalContact"]] = relationship("ExternalContact")
    line_items: Mapped[List["IncomingInvoiceLineItem"]] = relationship(
        "IncomingInvoiceLineItem", back_populates="incoming_invoice",
        cascade="all, delete-orphan", order_by="IncomingInvoiceLineItem.created_at",
    )
    payments: Mapped[List["IncomingInvoicePayment"]] = relationship(
        "IncomingInvoicePayment", back_populates="incoming_invoice",
        cascade="all, delete-orphan", order_by="IncomingInvoicePayment.paid_on",
    )
    created_by: Mapped[Optional["User"]] = relationship("User")

    @property
    def total_amount(self) -> float:
        return float(sum((li.amount for li in self.line_items), 0))

    @property
    def paid_total(self) -> float:
        return float(sum((p.amount for p in self.payments), 0))

    @property
    def payment_status(self) -> str:
        """One of "open" / "partially_paid" / "paid" -- same derivation
        as Invoice.payment_status (issue #181: "could be the same
        method as in outgoing invoices"), just without a reminder-fee
        concept since incoming invoices have none."""
        paid = self.paid_total
        if paid <= 0:
            return "open"
        if paid < self.total_amount:
            return "partially_paid"
        return "paid"

    def __repr__(self) -> str:
        return f"<IncomingInvoice {self.sender} {self.invoice_number or ''}>"


class IncomingInvoiceLineItem(Base):
    """One categorized cost position on an IncomingInvoice -- category_id
    is nullable (`ON DELETE SET NULL`) so deleting a FinanceCategory
    later never destroys a historical bookkeeping record, same
    historization-over-deletion precedent as InvoiceItemDefinition/
    InvoiceItemTemplate.category_id."""
    __tablename__ = "incoming_invoice_line_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    incoming_invoice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incoming_invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    incoming_invoice: Mapped["IncomingInvoice"] = relationship("IncomingInvoice", back_populates="line_items")
    category: Mapped[Optional["FinanceCategory"]] = relationship("FinanceCategory")

    def __repr__(self) -> str:
        return f"<IncomingInvoiceLineItem {self.amount}>"


class IncomingInvoicePayment(Base):
    """A single (possibly partial) payment recorded against an
    IncomingInvoice (issue #181) -- same shape as InvoicePayment,
    mirrored deliberately per that issue's "could be the same method as
    in outgoing invoices"."""
    __tablename__ = "incoming_invoice_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    incoming_invoice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incoming_invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_on: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("finance_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    recorded_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    incoming_invoice: Mapped["IncomingInvoice"] = relationship("IncomingInvoice", back_populates="payments")
    account: Mapped[Optional["FinanceAccount"]] = relationship("FinanceAccount")

    def __repr__(self) -> str:
        return f"<IncomingInvoicePayment {self.amount}>"


class InvoiceReminder(Base):
    """
    A dunning/collection reminder sent for an unpaid Invoice (issue
    #59). `level` is a simple incrementing counter (1st reminder, 2nd,
    ...) computed at creation time from how many already exist for
    this invoice -- deliberately no fixed/named stages, so a club can
    run whatever process it wants. `fee_amount` is optional and
    club-entered per reminder (not a configured default) since not
    every club wants to charge a Mahngebühr; when set it's added to
    what the invoice still owes (see Invoice.reminder_fees_total /
    amount_due). `delivery_method` mirrors how the reminder actually
    went out -- resolved the same way as the original invoice's own
    delivery (email if the recipient has notifications enabled and a
    stored address, otherwise a PDF for manual/postal sending -- see
    app/invoice_delivery.py's deliver_reminder).
    """
    __tablename__ = "invoice_reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    invoice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_method: Mapped[str] = mapped_column(String(10), nullable=False)  # "email" | "print"
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="reminders")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<InvoiceReminder level {self.level} for invoice {self.invoice_id}>"
