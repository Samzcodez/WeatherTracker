from django.urls import path
from .views import index, GetCurrentWeather

urlpatterns = [
    path("", index),
    path(
        "current-weather/<str:city>/",
        GetCurrentWeather.as_view(),
        name="get_current_weather",
    ),
]
