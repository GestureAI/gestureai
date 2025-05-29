from datetime import datetime

from core.db_context import session_maker
from models.db import TelemetryDb


def add(telemetry: TelemetryDb) -> TelemetryDb:
    """
    Adds a new telemetry record to the database.

    Returns:
        TelemetryDb: The newly created telemetry record.
    """
    with session_maker.begin() as session:
        session.add(telemetry)

    return telemetry


def get(limit: int = 100, offset: int = 0) -> list[TelemetryDb]:
    """
    Retrieves telemetry records from the database.

    Args:
        limit (int): The maximum number of records to retrieve.
        offset (int): The number of records to skip before starting to collect the result set.

    Returns:
        list[TelemetryDb]: A list of telemetry records.
    """
    with session_maker() as session:
        return (
            session.query(TelemetryDb)
            .order_by(TelemetryDb.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )


def get_younger_than(age: datetime) -> list[TelemetryDb]:
    """
    Retrieves telemetry records that are younger than a specified age in minutes.

    Args:
        age (int): The age in minutes to filter the telemetry records.

    Returns:
        list[TelemetryDb]: A list of telemetry records that are younger than the specified age.
    """

    with session_maker() as session:
        return (
            session.query(TelemetryDb)
            .filter(TelemetryDb.created_at >= age)
            .order_by(TelemetryDb.created_at.desc())
            .all()
        )
