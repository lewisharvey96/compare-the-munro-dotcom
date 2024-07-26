from collections.abc import Generator
from pathlib import Path

import numpy as np
from googlemaps.client import Client

SECS_IN_HOUR = 3600

ROOT_FLD = Path(__file__).parent.parent


def _chunks(lst: list, n: int) -> Generator:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_commute_time_hours(googlemaps_client: Client, input_location: tuple, locations: list[tuple]) -> list:
    if len(locations) <= 25:
        distances_result = googlemaps_client.distance_matrix([input_location], locations, mode="driving")
        return [i.get("duration", {}).get("value", np.nan) for i in distances_result["rows"][0]["elements"]]
    else:
        chunks = list(_chunks(locations, 25))
        durations = []
        for chunk in chunks:
            distances_result = googlemaps_client.distance_matrix([input_location], chunk, mode="driving")
            durations.extend(
                [
                    round(2 * i.get("duration", {}).get("value", np.nan) / SECS_IN_HOUR, 1)
                    for i in distances_result["rows"][0]["elements"]
                ]
            )
        return durations
