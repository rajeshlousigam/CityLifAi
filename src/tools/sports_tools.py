from __future__ import annotations

from typing import Any

from services.api_clients import ApiClients


class SportsTools:
    def __init__(self, clients: ApiClients) -> None:
        self._sports = clients.sports

    async def find_slots(self, city: str, sport: str, date: str, limit: int = 5) -> dict[str, Any]:
        payload = await self._sports.search_venues(city=city, sport=sport, date=date)

        source = payload.get("results") or payload.get("venues") or []
        slots: list[dict[str, Any]] = []
        for row in source[:limit]:
            slots.append(
                {
                    "venue": row.get("venue_name") or row.get("name"),
                    "sport": sport,
                    "date": date,
                    "time_slot": row.get("time_slot") or row.get("slot"),
                    "price": row.get("price"),
                    "rating": row.get("rating"),
                    "booking_url": row.get("booking_url") or row.get("url"),
                }
            )

        return {"city": city, "sport": sport, "date": date, "slots": slots}
