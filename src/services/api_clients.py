from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from config.settings import Settings


class BaseApiClient:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout = httpx.Timeout(timeout_seconds)

    async def _get(self, url: str, params: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _post(self, url: str, json_body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=json_body, headers=headers)
            response.raise_for_status()
            return response.json()


class GoogleMapsClient(BaseApiClient):
    DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
    DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.request_timeout_seconds)
        self._api_key = settings.google_maps_api_key

    async def get_directions(self, origin: str, destination: str, mode: str = "driving") -> dict[str, Any]:
        return await self._get(
            self.DIRECTIONS_URL,
            params={"origin": origin, "destination": destination, "mode": mode, "key": self._api_key},
        )

    async def get_traffic(self, origin: str, destination: str) -> dict[str, Any]:
        return await self._get(
            self.DISTANCE_MATRIX_URL,
            params={
                "origins": origin,
                "destinations": destination,
                "departure_time": "now",
                "traffic_model": "best_guess",
                "key": self._api_key,
            },
        )


class PlacesClient(BaseApiClient):
    TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.request_timeout_seconds)
        self._api_key = settings.google_places_api_key or settings.google_maps_api_key

    async def search(self, query: str) -> dict[str, Any]:
        return await self._get(self.TEXT_SEARCH_URL, params={"query": query, "key": self._api_key})


class MeetupClient(BaseApiClient):
    GQL_URL = "https://api.meetup.com/gql"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.request_timeout_seconds)
        self._token = settings.meetup_api_token

    async def search_events(self, city: str, topic: str, first: int = 5) -> dict[str, Any]:
        query = """
        query SearchEvents($filter: EventSearchFilter!, $first: Int!) {
          keywordSearch(filter: $filter, first: $first) {
            edges {
              node {
                result {
                  ... on Event {
                    id
                    title
                    dateTime
                    eventUrl
                    venue { name }
                    group { name }
                  }
                }
              }
            }
          }
        }
        """
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        variables = {"filter": {"query": f"{topic} {city}"}, "first": first}
        return await self._post(self.GQL_URL, json_body={"query": query, "variables": variables}, headers=headers)


class SportsClient(BaseApiClient):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings.request_timeout_seconds)
        self._base_url = settings.sports_api_base_url.rstrip("/")
        self._api_key = settings.sports_api_key
        self._endpoint = settings.sports_api_endpoint

    async def search_venues(self, city: str, sport: str, date: str) -> dict[str, Any]:
        url = f"{self._base_url}{self._endpoint}"
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        return await self._get(url, params={"city": city, "sport": sport, "date": date}, headers=headers)


@dataclass
class ApiClients:
    google_maps: GoogleMapsClient
    places: PlacesClient
    meetup: MeetupClient
    sports: SportsClient


def build_api_clients(settings: Settings) -> ApiClients:
    return ApiClients(
        google_maps=GoogleMapsClient(settings),
        places=PlacesClient(settings),
        meetup=MeetupClient(settings),
        sports=SportsClient(settings),
    )
