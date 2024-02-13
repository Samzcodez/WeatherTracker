from django.urls import path
from .views import index, GetCurrentWeather

urlpatterns = [
    path("", index),
    path(
        "current-weather/<str:city>/<str:lang>/",
        GetCurrentWeather.as_view(),
        name="get_current_weather",
    ),
    path(
        "current-weather/<str:city>/",
        GetCurrentWeather.as_view(),
        {"lang": "en"},  # Set the default value for 'lang' to 'en'
        name="get_current_weather_default",
    ),
]
