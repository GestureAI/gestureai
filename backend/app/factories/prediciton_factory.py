from models.dto import PredictionDTO


def create(char: str, precision: float, activation: float = 0.5) -> PredictionDTO:
    """
    Create a PredictionDTO object based on the provided character and precision.
    If the precision is greater than the activation threshold, the character is recognized.
    Otherwise, it is not recognized.
    :param char: The character to be recognized.
    :param precision: The precision of the prediction.
    :param activation: The threshold for recognizing the character.
    :return: A PredictionDTO object containing the character, recognition status, and precision.
    """

    recognized_char = ""
    is_recognized = False
    if precision > activation:
        recognized_char = char
        is_recognized = True

    return PredictionDTO(
        char=recognized_char, is_recognized=is_recognized, precision=precision
    )
