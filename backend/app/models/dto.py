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
    response_time: int
    model_name: str
    created_at: str


@dataclass
class LoginDTO:
    password: str


@dataclass
class AnalyzeDTO:
    response_times_avg: float
    response_times_min: float
    response_times_max: float
    precision_avg: float
    precision_min: float
    precision_max: float
    most_common_char: str
