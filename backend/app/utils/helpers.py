from models.dto import TelemetryDTO
from models.dto import AnalyzeDTO


def get_avg_min_max(dataset: list[TelemetryDTO]) -> AnalyzeDTO:
    if not dataset:
        return AnalyzeDTO(0, 0, 0, 0, 0, 0, "")

    response_times = [t.response_time for t in dataset]
    precision_values = [t.precision for t in dataset]
    characters = [t.letter for t in dataset]

    # Calculate averages, min, and max for response times
    response_times_avg = sum(response_times) / len(response_times)
    response_times_min = min(response_times)
    response_times_max = max(response_times)

    # Calculate averages, min, and max for precision values
    precision_avg = sum(precision_values) / len(precision_values)
    precision_min = min(precision_values)
    precision_max = max(precision_values)

    # Find the most common character
    most_common_char = max(set(characters), key=characters.count)

    return AnalyzeDTO(
        response_times_avg=round(response_times_avg, 4),
        response_times_min=round(response_times_min, 4),
        response_times_max=round(response_times_max, 4),
        precision_avg=round(precision_avg, 4),
        precision_min=round(precision_min, 4),
        precision_max=round(precision_max, 4),
        most_common_char=most_common_char,
    )
