from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    OPEN_WEATHER_API_KEY: str
