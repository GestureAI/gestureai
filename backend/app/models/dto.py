from dataclasses import dataclass


@dataclass
class PredictionDTO:
    char: str
    is_recognized: bool
    precision: float