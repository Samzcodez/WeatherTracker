from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import pycountry
import warnings

warnings.filterwarnings("ignore", category=Warning, module="django.core.cache")
open_weather_api_key = settings.OPEN_WEATHER_API_KEY
current_weather_url = (
    "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang={}"
)
# Keyword translations for English, German, and French
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
def index(request):
    if request.method == "POST":
        try:
            city = request.POST["city"]
            # retrieve imformation from weather api = https://api.openweathermap.org/api
            weather_data = fetch_weather_and_forecast(
                city, "en", open_weather_api_key, current_weather_url
            )
        except Exception as e:
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
    def get(self, request, city, lang, cache_timeout):
        try:
            # Check if data is in cache
            valid_cache_timeouts = [5, 10, 60]
            if cache_timeout not in valid_cache_timeouts:
                return Response(
                    {"error": "Invalid cache_timeout value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cache_key = f"{city}_{lang}"
            cached_data = cache.get(cache_key)
            if cached_data:
                print("Cache hit for:", cache_key)
                return Response(cached_data, status=status.HTTP_200_OK)
            print("Cache miss for:", cache_key)
            weather_data = fetch_weather_and_forecast(
                city, lang, open_weather_api_key, current_weather_url
            )
            modified_weather_data = {
                key: value
                for key, value in weather_data.items()
                if key not in keyword_translations["icon"].values()
            }
            cache.set(cache_key, modified_weather_data, cache_timeout * 60)
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
            return Response(
                {"error": f"Error fetching weather data for the city {city}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def convert_wind_direction(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def get_response_value(response_data, key):
    if key == "city":
        return str(response_data.get("name"))
    elif key == "country":
        country_code = str(response_data["sys"]["country"])
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


def fetch_weather_and_forecast(city, language, api_key, current_weather_url):
    response_data = requests.get(
        current_weather_url.format(city, api_key, language)
    ).json()

    # convert  json file into python dectionary
    weather_data = {
        keyword_translations[key][language]: get_response_value(response_data, key)
        for key in keyword_translations
        if key != "current_weather"
    }
    return weather_data
