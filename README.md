# WeatherTracker Readme

## Overview
WeatherTracker is a Django web application designed to provide current weather information for any city. The application utilizes data from [OpenWeatherMap](https://openweathermap.org/current).

## Features
Users can input a city to retrieve detailed weather information, including:
- [x] Requested city name
- [x] Current temperature, minimum temperature, and maximum temperature
- [x] Humidity and pressure levels
- [x] Wind speed and direction (north, south, west, east)
- [x] Weather description

## Installation
Prerequisite : Docker compose installed in your system. [docker-compose](https://docs.docker.com/compose/install/)
Follow these steps to set up the WeatherTracker application:
1. **API Key**: Create a free account on [OpenWeatherMap](https://openweathermap.org) and obtain an API key.
2. **Docker Compose**: Run the following command, replacing `<your_api_key>` with the obtained API key:
    ```bash
    docker-compose run --publish 8000:8000 -e OPEN_WEATHER_API_KEY='<your_api_key>' weather_app
    ```

## Schema
The API description can be accessed at http://127.0.0.1:8000/api/schema.

## Swagger UI
Explore the API using Swagger UI at http://127.0.0.1:8000/api/schema/swagger-ui/.

## API Endpoints
Retrieve current weather information using the following API endpoints:
1. **Get current weather:**

    Get current weather for a specific city in three different languages, allowing you to configure the cache timeout.
    Endpoint: http://127.0.0.1:8000/weather/<str:city>/<str:lang>/<int:cache_timeout>/ .

    - [x] Supported Languages: English (en), German (de), French (fr) .
    - [x] Cache Timeout Options: [5/10/60] minutes.

2. **Get current weather without cache configuration (default: 10 minutes):**

    Retrieve current weather for any city in above three languages without explicitly configuring the cache timeout.
    Endpoint: http://127.0.0.1:8000/weather/<str:city>/<str:lang>/

3. **Get current weather in English without cache configuration:**

    Retrieve current weather for any city in English without specifying cache settings.
    Endpoint: http://127.0.0.1:8000/weather/<str:city>/


## User Interface
Access a simple UI at http://127.0.0.1:8000/weather/, where you can enter the desired city name to view detailed weather information.

Feel free to explore and enjoy WeatherTracker!
