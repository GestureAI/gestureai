from datetime import datetime

from models.db import TelemetryDb
from models.dto import TelemetryDTO


def db_to_dto(telemetry: TelemetryDb) -> TelemetryDTO:
    """
    Converts a TelemetryDb instance to a TelemetryDTO instance.

    Args:
        telemetry (TelemetryDb): The TelemetryDb instance to convert.

    Returns:
        TelemetryDTO: The converted TelemetryDTO instance.
    """
    created_at: datetime = telemetry.created_at

    return TelemetryDTO(
        id=telemetry.id,
        precision=telemetry.precision,
        letter=telemetry.letter,
        response_time=telemetry.response_time,
        model_name=telemetry.model_name,
        created_at=created_at.isoformat(),
    )
