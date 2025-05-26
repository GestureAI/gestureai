from dataclasses import dataclass


@dataclass
class PredictionDTO:
    char: str
    is_recognized: bool
    precision: float

@dataclass
class TelemetryDTO:
    id: int
    precision: float
    letter: str
    prediction_time: int
    response_time: int
    model_name: str
    created_at: str