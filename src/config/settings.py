from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CityLife AI"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    google_maps_api_key: str = ""
    google_places_api_key: str = ""

    meetup_api_token: str = ""
    sports_api_base_url: str = "https://api.playo.io/api"
    sports_api_key: str = ""
    sports_api_endpoint: str = "/activity-public/list/location"

    default_city: str = "Bangalore"
    request_timeout_seconds: float = 20.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
