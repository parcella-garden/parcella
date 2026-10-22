"""Rename the legacy German index and constraint names

Revision ID: 0108_rename_legacy_indexes
Revises: 0107_helpdesk_providers
Create Date: 2026-10-23

The early migrations created indexes under German names
(ix_mitglied_email_mitglied_id, ...). The tables and columns were later
renamed to English (ADRs 0008-0011), the indexes weren't, so every
`alembic check` reported them as "remove + add". This renames them to
exactly the names SQLAlchemy derives from the models -- same table,
same columns, same uniqueness, so ALTER INDEX ... RENAME only changes
the name: no rebuild, no lock beyond a moment, no data touched.
IF EXISTS keeps it safe on an installation where one is already renamed.

Primary keys, unique keys and foreign keys kept their German
auto-generated names too (mitglieder_pkey, einkaufswuensche_..._fkey).
Alembic doesn't compare those, but they show up in every error message
and pg_dump. They get the names PostgreSQL generates today
(<table>_pkey, <table>_<columns>_key, <table>_<column>_fkey); explicitly
named ones (uq_..., ck_..., fk_...) are left alone. Renaming a
constraint renames its index with it and changes nothing else.
"""
from typing import Union

from alembic import op

revision: str = "0108_rename_legacy_indexes"
down_revision: Union[str, None] = "0107_helpdesk_providers"
branch_labels = None
depends_on = None

RENAMES = (
    ("ix_unfallversicherung_zusatzpersonen_mitglied_id", "ix_accident_insurance_additional_persons_member_id"),
    ("ix_unfallversicherung_zusatzpersonen_pv_id", "ix_accident_insurance_additional_persons_parcel_insurance_id"),
    ("ix_versicherungs_konfiguration_jahr", "ix_insurance_configuration_year"),
    ("ix_invoice_item_definition_parcels_definition_id", "ix_invoice_item_definition_parcels_invoice_item_definition_id"),
    ("ix_mitglied_vereinsrolle_mitglied_id", "ix_member_club_roles_member_id"),
    ("ix_mitglied_vereinsrolle_vereinsrolle_id", "ix_member_club_roles_club_role_id"),
    ("ix_mitglied_email_mitglied_id", "ix_member_emails_member_id"),
    ("ix_mitglied_parzelle_mitglied_id", "ix_member_parcels_member_id"),
    ("ix_mitglied_parzelle_parzelle_id", "ix_member_parcels_parcel_id"),
    ("ix_mitglied_telefon_mitglied_id", "ix_member_phones_member_id"),
    ("ix_zaehlerstaende_wasseruhr_id", "ix_meter_readings_meter_id"),
    ("ix_wasseranschluesse_parzelle_id", "ix_metering_points_parcel_id"),
    ("ix_wasseruhren_anschluss_id", "ix_meters_metering_point_id"),
    ("ix_wasseruhren_nummer", "ix_meters_number"),
    ("ix_parzelle_versicherung_parzelle_id", "ix_parcel_insurance_parcel_id"),
    ("ix_parzellen_gartennummer", "ix_parcels_plot_number"),
    ("ix_sachversicherung_pakete_jahr", "ix_property_insurance_packages_year"),
    ("ix_einsatz_teilnahmen_einsatz_id", "ix_session_participations_session_id"),
    ("ix_einsatz_teilnahmen_mitglied_id", "ix_session_participations_member_id"),
    ("ix_patenschaften_mitglied_id", "ix_sponsorships_member_id"),
    ("ix_pflichtstunden_konfiguration_jahr", "ix_work_hours_configuration_year"),
    ("ix_arbeitseinsaetze_datum", "ix_work_sessions_date"),
)

# (table, old constraint name, new constraint name)
CONSTRAINT_RENAMES = (
    ("accident_insurance_additional_persons", "unfallversicherung_zusatzpersonen_mitglied_id_fkey", "accident_insurance_additional_persons_member_id_fkey"),
    ("accident_insurance_additional_persons", "unfallversicherung_zusatzpersonen_parzelle_versicherung_id_fkey", "accident_insurance_additional_persons_parcel_insurance_id_fkey"),
    ("accident_insurance_additional_persons", "unfallversicherung_zusatzpersonen_pkey", "accident_insurance_additional_persons_pkey"),
    ("change_history", "aenderungshistorie_geaendert_von_id_fkey", "change_history_changed_by_id_fkey"),
    ("change_history", "aenderungshistorie_pkey", "change_history_pkey"),
    ("club_roles", "vereinsrollen_pkey", "club_roles_pkey"),
    ("club_roles", "vereinsrollen_name_key", "club_roles_name_key"),
    ("club_settings", "vereinseinstellungen_pkey", "club_settings_pkey"),
    ("insurance_configuration", "versicherungs_konfiguration_pkey", "insurance_configuration_pkey"),
    ("invitations", "einladungen_eingeladen_von_id_fkey", "invitations_invited_by_id_fkey"),
    ("invitations", "einladungen_pkey", "invitations_pkey"),
    ("invitations", "einladungen_token_key", "invitations_token_key"),
    ("member_club_roles", "mitglied_vereinsrolle_mitglied_id_fkey", "member_club_roles_member_id_fkey"),
    ("member_club_roles", "mitglied_vereinsrolle_vereinsrolle_id_fkey", "member_club_roles_club_role_id_fkey"),
    ("member_club_roles", "mitglied_vereinsrolle_pkey", "member_club_roles_pkey"),
    ("member_emails", "mitglied_email_mitglied_id_fkey", "member_emails_member_id_fkey"),
    ("member_emails", "mitglied_email_pkey", "member_emails_pkey"),
    ("member_parcels", "mitglied_parzelle_mitglied_id_fkey", "member_parcels_member_id_fkey"),
    ("member_parcels", "mitglied_parzelle_parzelle_id_fkey", "member_parcels_parcel_id_fkey"),
    ("member_parcels", "mitglied_parzelle_pkey", "member_parcels_pkey"),
    ("member_phones", "mitglied_telefon_mitglied_id_fkey", "member_phones_member_id_fkey"),
    ("member_phones", "mitglied_telefon_pkey", "member_phones_pkey"),
    ("members", "mitglieder_pkey", "members_pkey"),
    ("meter_readings", "zaehlerstaende_erfasst_von_id_fkey", "meter_readings_recorded_by_id_fkey"),
    ("meter_readings", "zaehlerstaende_wasseruhr_id_fkey", "meter_readings_meter_id_fkey"),
    ("meter_readings", "zaehlerstaende_pkey", "meter_readings_pkey"),
    ("metering_points", "wasseranschluesse_parzelle_id_fkey", "metering_points_parcel_id_fkey"),
    ("metering_points", "wasseranschluesse_pkey", "metering_points_pkey"),
    ("meters", "wasseruhren_anschluss_id_fkey", "meters_metering_point_id_fkey"),
    ("meters", "wasseruhren_pkey", "meters_pkey"),
    ("parcel_insurance", "parzelle_versicherung_parzelle_id_fkey", "parcel_insurance_parcel_id_fkey"),
    ("parcel_insurance", "parzelle_versicherung_sach_paket_id_fkey", "parcel_insurance_property_package_id_fkey"),
    ("parcel_insurance", "parzelle_versicherung_pkey", "parcel_insurance_pkey"),
    ("parcels", "parzellen_pkey", "parcels_pkey"),
    ("property_insurance_packages", "sachversicherung_pakete_pkey", "property_insurance_packages_pkey"),
    ("purchase_request_approvals", "einkaufswunsch_freigaben_benutzer_id_fkey", "purchase_request_approvals_user_id_fkey"),
    ("purchase_request_approvals", "einkaufswunsch_freigaben_einkaufswunsch_id_fkey", "purchase_request_approvals_purchase_request_id_fkey"),
    ("purchase_request_approvals", "einkaufswunsch_freigaben_pkey", "purchase_request_approvals_pkey"),
    ("purchase_requests", "einkaufswuensche_abgelehnt_von_id_fkey", "purchase_requests_rejected_by_id_fkey"),
    ("purchase_requests", "einkaufswuensche_angefragt_von_id_fkey", "purchase_requests_requested_by_id_fkey"),
    ("purchase_requests", "einkaufswuensche_erstellt_von_id_fkey", "purchase_requests_created_by_id_fkey"),
    ("purchase_requests", "einkaufswuensche_pkey", "purchase_requests_pkey"),
    ("purchase_requests", "einkaufswuensche_bestaetigungs_token_key", "purchase_requests_confirmation_token_key"),
    ("session_participations", "einsatz_teilnahmen_einsatz_id_fkey", "session_participations_session_id_fkey"),
    ("session_participations", "einsatz_teilnahmen_mitglied_id_fkey", "session_participations_member_id_fkey"),
    ("session_participations", "einsatz_teilnahmen_pkey", "session_participations_pkey"),
    ("sponsorships", "patenschaften_mitglied_id_fkey", "sponsorships_member_id_fkey"),
    ("sponsorships", "patenschaften_pkey", "sponsorships_pkey"),
    ("users", "benutzer_pkey", "users_pkey"),
    ("work_hours_configuration", "pflichtstunden_konfiguration_pkey", "work_hours_configuration_pkey"),
    ("work_sessions", "arbeitseinsaetze_erstellt_von_id_fkey", "work_sessions_created_by_id_fkey"),
    ("work_sessions", "arbeitseinsaetze_pkey", "work_sessions_pkey"),
)


def _rename_constraint(table: str, old: str, new: str) -> None:
    # Constraints have no RENAME ... IF EXISTS; check first.
    op.execute(
        f"DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{old}' "
        f"AND conrelid = '{table}'::regclass) THEN "
        f"ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new}; END IF; END $$"
    )


def upgrade() -> None:
    for old, new in RENAMES:
        op.execute(f"ALTER INDEX IF EXISTS {old} RENAME TO {new}")
    for table, old, new in CONSTRAINT_RENAMES:
        _rename_constraint(table, old, new)


def downgrade() -> None:
    for table, old, new in CONSTRAINT_RENAMES:
        _rename_constraint(table, new, old)
    for old, new in RENAMES:
        op.execute(f"ALTER INDEX IF EXISTS {new} RENAME TO {old}")
