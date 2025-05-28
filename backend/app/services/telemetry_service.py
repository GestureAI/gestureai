from repos import telemetry_repo
from models.dto import TelemetryDTO
from models.db import TelemetryDb
from mappers import telemetry_mapper
from factories import telemetry_factory


def register(char: str, precision: float, response_ms: int) -> TelemetryDTO:
    """
    Registers telemetry data for a character recognition event.

    Args:
        char (str): The character that was recognized.
        precision (float): The precision of the recognition.
        response_ms (int): The response time in milliseconds.

    Returns:
        TelemetryDTO: The telemetry data transfer object containing the recorded telemetry information.
    """
    telemetry: TelemetryDb = telemetry_factory.create(
        precision=precision, letter=char, response_time=response_ms
    )
    telemetry_repo.add(telemetry)
    return telemetry_mapper.db_to_dto(telemetry)