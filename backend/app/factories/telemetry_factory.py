from models.db import TelemetryDb
from utils.config import CONFIG


def create(
    precision: float,
    letter: str,
    prediction_time: int,
    response_time: int,
) -> TelemetryDb:
    """
    Creates a new instance of TelemetryDb with default values.

    Returns:
        TelemetryDb: A new instance of TelemetryDb.
    """
    return TelemetryDb(
        precision=precision,
        letter=letter,
        prediction_time=prediction_time,
        response_time=response_time,
        model_name=CONFIG.TF_MODEL_NAME,
    )
