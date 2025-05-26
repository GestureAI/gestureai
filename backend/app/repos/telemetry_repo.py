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
            .limit(limit)
            .offset(offset)
            .order_by(TelemetryDb.created_at.desc())
            .all()
        )
