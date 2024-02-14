from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from typing import Optional, Any
import httpx
import asyncio
import pycountry
import logging

logger = logging.getLogger(__name__)

open_weather_api_key = settings.OPEN_WEATHER_API_KEY
current_weather_url = (
    "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang={}"
)

# Keyword translations for response in English, German, and French
keyword_translations = {
    "current_weather": {
        "en": "current_weather",
        "de": "aktuelles_Wetter",
        "fr": "temps_courant",
    },
    "city": {"en": "city", "de": "stadt", "fr": "ville"},
    "country": {"en": "country", "de": "land", "fr": "pays"},
    "temperature": {"en": "temperature", "de": "temperatur", "fr": "température"},
    "temperature_min": {
        "en": "temperature_min",
        "de": "temperatur_min",
        "fr": "température_min",
    },
    "temperature_max": {
        "en": "temperature_max",
        "de": "temperatur_max",
        "fr": "température_max",
    },
    "humidity": {"en": "humidity", "de": "luftfeuchtigkeit", "fr": "humidité"},
    "pressure": {"en": "pressure", "de": "druck", "fr": "pression"},
    "wind_speed": {
        "en": "wind_speed",
        "de": "wind_geschwindigkeit",
        "fr": "vitesse_vent",
    },
    "wind_direction": {
        "en": "wind_direction",
        "de": "wind_richtung",
        "fr": "direction_vent",
    },
    "description": {"en": "description", "de": "beschreibung", "fr": "description"},
    "icon": {"en": "icon", "de": "symbol", "fr": "icône"},
}


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    """
    Handle the index page, fetching and displaying weather data through UI.
    """
    if request.method == "POST":
        try:
            city = request.POST["city"]

            # retrieve imformation from weather api "https://api.openweathermap.org/api"
            weather_data = fetch_weather_and_forecast(
                city, "en", open_weather_api_key, current_weather_url
            )
            logging.debug(f"Received weather info for city: {city} from UI")
        except Exception as e:
            logging.error(f"An error occurred while fetching weather data from UI: {e}")
            weather_data = {
                "city": f"Weather details not found for: {city}",
            }
        context = {
            "weather_data": weather_data,
        }
        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")


class GetCurrentWeather(APIView):
    """
    Class for retrieving current weather and forecast data for a specified city and language.
    Handles caching of data to improve response time and reduce external API requests.
    """

    def get(
        self, request: HttpRequest, city: str, lang: str, cache_timeout: int
    ) -> HttpResponse:
        """
        Handles requests from endpoint: GET weather/{city}/{lang}/{cache_timeout}/
        """
        try:
            # Check if cahe_timeout given is valid
            valid_cache_timeouts = [5, 10, 60]
            if cache_timeout not in valid_cache_timeouts:
                logging.error(
                    f"Invalid cache_timeout value. Accepted values are : {valid_cache_timeouts}"
                )
                return Response(
                    {
                        "error": f"Invalid cache_timeout value. Accepted values are : {valid_cache_timeouts}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cache_key = f"{city}_{lang}"
            cached_data = cache.get(cache_key)

            # Fetch weather data from cache
            if cached_data:
                logger.info(f"Cache hit for: {cache_key}")
                return Response(cached_data, status=status.HTTP_200_OK)

            # Fetch weather data from open_weather api
            logger.debug(f"Cache miss for: {cache_key}")
            weather_data = fetch_weather_and_forecast(
                city, lang, open_weather_api_key, current_weather_url
            )
            modified_weather_data = {
                key: value
                for key, value in weather_data.items()
                if key not in keyword_translations["icon"].values()
            }  # Modify the weather data by excluding the 'icon' key used in UI

            cache.set(
                cache_key, modified_weather_data, cache_timeout * 60
            )  # Set the new data in the cache with the specified timeout
            logging.debug(
                f"Received weather info for city: {city} , weather_data : {modified_weather_data}"
            )
            return Response(
                {
                    keyword_translations["city"][lang]: city,
                    keyword_translations["current_weather"][
                        lang
                    ]: modified_weather_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logging.error(f"Error fetching weather data for the city {city}: {str(e)}")
            return Response(
                {"error": f"Error fetching weather data for the city {city}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def convert_wind_direction(degrees: float) -> str:
    """
    Convert wind direction in degrees to a compass direction.
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def get_response_value(response_data: dict, key: str) -> Optional[str]:
    """
    Extract a specific value from the response_data based on the provided key.
    """
    if key == "city":
        return str(response_data.get("name"))
    elif key == "country":
        country_code = str(response_data["sys"]["country"])
        # Return the country name from the provided ISO 3166-1 alpha-2 country code
        return str(
            pycountry.countries.get(alpha_2=country_code).name
            if country_code
            else "Unknown Country"
        )
    elif key == "temperature":
        return str(response_data["main"].get("temp", None))
    elif key == "temperature_min":
        return str(response_data["main"].get("temp_min", None))
    elif key == "temperature_max":
        return str(response_data["main"].get("temp_max", None))
    elif key == "humidity":
        return str(response_data["main"].get("humidity", None))
    elif key == "pressure":
        return str(response_data["main"].get("pressure", None))
    elif key == "wind_speed":
        return str(response_data["wind"].get("speed", None))
    elif key == "wind_direction":
        return convert_wind_direction(float(response_data["wind"].get("deg", None)))
    elif key == "description":
        return str(response_data["weather"][0].get("description", None))
    elif key == "icon":
        return response_data["weather"][0].get("icon", None)
    else:
        return None


def fetch_weather_and_forecast(
    city: str, language: str, api_key: str, current_weather_url: str
) -> dict[str, Any]:
    """
    Fetch current weather and forecast data for the given city using open weather api.
    """

    async def async_fetch() -> dict[str, Any]:
        async with httpx.AsyncClient() as client:  # Asynchronously fetch weather data using coroutine-based client
            response = await client.get(
                current_weather_url.format(city, api_key, language)
            )
            response_data = response.json()

            # Convert json response into python dectionary
            return {
                keyword_translations[key][language]: get_response_value(
                    response_data, key
                )
                for key in keyword_translations
                if key != "current_weather"
            }

    return asyncio.run(async_fetch())
