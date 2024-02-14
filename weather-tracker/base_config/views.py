from django.shortcuts import render


def home_view(request):
    return render(request, "base_config/home.html")


def error_view(request):
    return render(request, "base_config/error.html")
