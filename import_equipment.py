from pathlib import Path
from datetime import datetime

import pandas as pd

from app.database import SessionLocal
from app.models import Equipment, Hub


FILE_PATH = Path("Copy of 2026 Equipment Inventory.xlsx")

# Keep this True until we finish validating the workbook.
DRY_RUN = False


SHEET_TYPE_MAP = {
    "GLS Samplers": "GLS_SAMPLER",
    "NiCad Batteries": "NICAD_BATTERY",
    "5-Port Charging Stations": "FIVE_PORT_CHARGER",
    "Single-Port Charging Stations": "SINGLE_PORT_CHARGER",
}


def clean_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def convert_yes_no(value):
    value = clean_text(value)

    if value is None:
        return False

    value = value.lower()

    if value == "yes":
        return True

    if value == "no":
        return False

    raise ValueError(f"Unexpected Yes/No value: {value}")


def convert_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def get_hub_map(db):
    hubs = db.query(Hub).all()

    return {
        hub.name.strip().lower(): hub.id
        for hub in hubs
    }


def import_equipment():
    db = SessionLocal()

    records_ready = 0
    duplicates = 0
    unknown_hubs = 0
    invalid_statuses = 0
    invalid_dates = 0

    # Tracks serial numbers encountered during this spreadsheet run.
    spreadsheet_serials = set()

    try:
        if not FILE_PATH.exists():
            print(f"ERROR: File not found: {FILE_PATH}")
            return

        hub_map = get_hub_map(db)

        print("=" * 60)
        print("EQUIPMENT IMPORT VALIDATION")
        print("=" * 60)

        if DRY_RUN:
            print("DRY RUN MODE: No database records will be created.\n")

        for sheet_name, equipment_type in SHEET_TYPE_MAP.items():

            print(f"\n--- Reading {sheet_name} ---")

            df = pd.read_excel(
                FILE_PATH,
                sheet_name=sheet_name,
                header=2,
            )

            sheet_ready = 0

            for row_number, row in df.iterrows():

                # +4 converts pandas row index to approximate Excel row.
                excel_row = row_number + 4

                serial_number = clean_text(
                    row.get("Serial Number")
                )

                # Ignore completely blank rows.
                if serial_number is None:
                    continue

                # ---------------------------------------
                # DUPLICATE SERIAL NUMBER CHECK
                # ---------------------------------------

                if serial_number in spreadsheet_serials:
                    print(
                        f"[DUPLICATE IN WORKBOOK] "
                        f"{serial_number} "
                        f"({sheet_name}, row {excel_row})"
                    )

                    duplicates += 1
                    continue

                spreadsheet_serials.add(serial_number)

                existing = (
                    db.query(Equipment)
                    .filter(
                        Equipment.serial_number == serial_number
                    )
                    .first()
                )

                if existing:
                    print(
                        f"[ALREADY IN DATABASE] "
                        f"{serial_number}"
                    )

                    duplicates += 1
                    continue

                # ---------------------------------------
                # HUB VALIDATION
                # ---------------------------------------

                storage_location = clean_text(
                    row.get("Storage Location")
                )

                hub_id = None

                if storage_location:
                    hub_id = hub_map.get(
                        storage_location.lower()
                    )

                    if hub_id is None:
                        print(
                            f"[UNKNOWN HUB] "
                            f"{serial_number}: "
                            f"{storage_location}"
                        )

                        unknown_hubs += 1

                # ---------------------------------------
                # DEPLOYMENT STATUS
                # ---------------------------------------

                if sheet_name == "GLS Samplers":

                    deployment_value = row.get(
                        "Installed?"
                    )

                    deployment_location = clean_text(
                        row.get("Install Location")
                    )

                else:

                    deployment_value = row.get(
                        "In the Field?"
                    )

                    deployment_location = None

                try:
                    is_deployed = convert_yes_no(
                        deployment_value
                    )

                except ValueError:

                    print(
                        f"[INVALID STATUS] "
                        f"{serial_number}: "
                        f"{deployment_value}"
                    )

                    invalid_statuses += 1
                    continue

                # ---------------------------------------
                # DATE VALIDATION
                # ---------------------------------------

                raw_date = row.get("Date")

                last_checked_date = convert_date(
                    raw_date
                )

                if (
                    not pd.isna(raw_date)
                    and last_checked_date is None
                ):
                    print(
                        f"[INVALID DATE] "
                        f"{serial_number}: "
                        f"{raw_date}"
                    )

                    invalid_dates += 1

                # ---------------------------------------
                # BUILD EQUIPMENT RECORD
                # ---------------------------------------

                equipment = Equipment(
                    serial_number=serial_number,
                    equipment_type=equipment_type,
                    hub_id=hub_id,
                    is_deployed=is_deployed,
                    deployment_location=deployment_location,
                    notes=clean_text(
                        row.get("Notes")
                    ),
                    qr_code=clean_text(
                        row.get("QR Code")
                    ),
                    last_checked_by=clean_text(
                        row.get("Initials")
                    ),
                    last_checked_date=last_checked_date,
                )

                # Only write when DRY_RUN is False.
                if not DRY_RUN:
                    db.add(equipment)

                records_ready += 1
                sheet_ready += 1

            print(
                f"{sheet_name}: "
                f"{sheet_ready} records ready"
            )

        # ---------------------------------------
        # FINAL RESULT
        # ---------------------------------------

        if DRY_RUN:
            db.rollback()
        else:
            db.commit()

        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        print(f"Records ready:       {records_ready}")
        print(f"Duplicates:          {duplicates}")
        print(f"Unknown hubs:        {unknown_hubs}")
        print(f"Invalid statuses:    {invalid_statuses}")
        print(f"Invalid dates:       {invalid_dates}")

        if DRY_RUN:
            print("\nNo database changes were made.")

        if (
            duplicates == 0
            and unknown_hubs == 0
            and invalid_statuses == 0
            and invalid_dates == 0
        ):
            print("\nDataset passed validation.")
        else:
            print(
                "\nDataset has items we should review "
                "before importing."
            )

    except Exception as error:

        db.rollback()

        print("\nIMPORT VALIDATION FAILED")
        print(type(error).__name__)
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    import_equipment()