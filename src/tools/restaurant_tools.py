from __future__ import annotations

from typing import Any

from services.api_clients import ApiClients


class RestaurantTools:
    def __init__(self, clients: ApiClients) -> None:
        self._places = clients.places

    async def find_restaurants(self, city: str, cuisine: str | None = None, limit: int = 5) -> dict[str, Any]:
        cuisine_hint = f" {cuisine}" if cuisine else ""
        query = f"best{cuisine_hint} restaurants in {city}"
        payload = await self._places.search(query=query)

        restaurants: list[dict[str, Any]] = []
        for result in payload.get("results", [])[:limit]:
            restaurants.append(
                {
                    "name": result.get("name"),
                    "rating": result.get("rating"),
                    "address": result.get("formatted_address"),
                    "price_level": result.get("price_level"),
                    "open_now": result.get("opening_hours", {}).get("open_now"),
                    "place_id": result.get("place_id"),
                }
            )

        return {"city": city, "cuisine": cuisine, "restaurants": restaurants}
