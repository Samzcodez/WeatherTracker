from django.shortcuts import render
from django.conf import settings
import requests
import pycountry

open_weather_api_key = settings.OPEN_WEATHER_API_KEY
current_weather_url = (
    "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"
)


# Create your views here.
def index(request):
    if request.method == "POST":

        city = request.POST["city"]
        # retrieve imformation from weather api = https://api.openweathermap.org/api
        weather_data = fetch_weather_and_forecast(
            city, open_weather_api_key, current_weather_url
        )
        context = {
            "weather_data": weather_data,
        }
        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")


def convert_wind_direction(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def fetch_weather_and_forecast(city, api_key, current_weather_url):
    response_data = requests.get(current_weather_url.format(city, api_key)).json()
    # convert  json file into python dectionary
    country_code = str(response_data["sys"]["country"])
    country_name = (
        pycountry.countries.get(alpha_2=country_code).name
        if country_code
        else "Unknown Country"
    )
    weather_data = {
        "city": str(response_data["name"]),
        "country": country_name,
        "temperature": str(response_data["main"]["temp"]),
        "temperature_min": str(response_data["main"]["temp_min"]),
        "temperature_max": str(response_data["main"]["temp_max"]),
        "humidity": str(response_data["main"]["humidity"]),
        "pressure": str(response_data["main"]["pressure"]),
        "wind_speed": str(response_data["wind"]["speed"]),
        "wind_direction": convert_wind_direction(float(response_data["wind"]["deg"])),
        "description": str(response_data["weather"][0]["description"]),
        "icon": response_data["weather"][0]["icon"],
    }

    return weather_data
