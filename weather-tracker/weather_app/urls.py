from django.urls import path, re_path
from .views import weather_index, weather_error_view, GetCurrentWeather

urlpatterns = [
    path("", weather_index, name="get_weather_app_ui"),
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
    re_path(r"^.*/$", weather_error_view, name="weather_error_view"),
    path(
        "<str:city>/<str:lang>/<int:cache>/<path:undefined_path>/",
        weather_error_view,
        name="weather_error_view",
    ),
]
