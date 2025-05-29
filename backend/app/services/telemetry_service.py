from datetime import datetime
from datetime import timedelta
from datetime import timezone

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


def get_lasts_n(amount: int) -> list[TelemetryDTO]:
    """
    Retrieves the last N telemetry records.

    Args:
        amount (int): The number of telemetry records to retrieve.

    Returns:
        list[TelemetryDTO]: A list of telemetry data transfer objects containing the last N telemetry records.
    """
    telemetry_list: list[TelemetryDb] = telemetry_repo.get(limit=amount)
    return [telemetry_mapper.db_to_dto(telemetry) for telemetry in telemetry_list]


def get_lasts_yonger(minutes: int) -> list[TelemetryDTO]:
    """
    Retrieves telemetry records that are younger than a specified number of minutes.
    Args:
        minutes (int): The age in minutes to filter the telemetry records.
    Returns:
        list[TelemetryDTO]: A list of telemetry data transfer objects containing the telemetry records that are younger than the specified age.
    """

    age_threshold: datetime = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    telemetry_list: list[TelemetryDb] = telemetry_repo.get_younger_than(age_threshold)
    return [telemetry_mapper.db_to_dto(telemetry) for telemetry in telemetry_list]
