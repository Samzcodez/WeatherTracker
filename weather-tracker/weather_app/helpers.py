from rest_framework.response import Response
from rest_framework import status
from typing import List, Union


def validate_input(
    valid_list: List, input_value: Union[str, int], input_type: str, logger
) -> Response:
    """
    Validates input against a list of valid values.
    """
    if input_value not in valid_list:
        logger.error(f"Invalid language value. Accepted values are: {valid_list}")
        return Response(
            {"error": f"Invalid {input_type} value. Accepted values are: {valid_list}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


def convert_wind_direction(degrees: float) -> str:
    """
    Convert wind direction in degrees to a compass direction.
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]
