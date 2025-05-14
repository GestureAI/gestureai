from random import random
from random import choice
from string import ascii_lowercase

from models import dto


def fake_response() -> dto.PredictionDTO:
    precision = random()
    letter = choice(ascii_lowercase) if precision > 0.5 else ""
    return dto.PredictionDTO(
        char=letter,
        is_recognized=precision > 0.5,
        precision=precision,
    )