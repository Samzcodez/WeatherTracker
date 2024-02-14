from django.urls import path
from .views import index, GetCurrentWeather

urlpatterns = [
    path("", index, name="get_weather_app_ui"),
    path(
        "<str:city>/<str:lang>/<int:cache_timeout>/",
        GetCurrentWeather.as_view(),
        name="get_current_weather",
    ),
    path(
        "<str:city>/",
        GetCurrentWeather.as_view(),
        kwargs={
            "lang": "en",
            "cache_timeout": 10,
        },  # Set the default value for 'language' and caching timeout in minutes
        name="get_current_weather_default_lang",
    ),
    path(
        "<str:city>/<str:lang>/",
        GetCurrentWeather.as_view(),
        {"cache_timeout": 10},  # Default caching timeout in minutes
        name="get_current_weather_without_timeout",
    ),
]
