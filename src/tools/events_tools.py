from __future__ import annotations

from typing import Any

from services.api_clients import ApiClients


class EventsTools:
    def __init__(self, clients: ApiClients) -> None:
        self._meetup = clients.meetup

    async def find_events(self, city: str, topic: str = "tech", limit: int = 5) -> dict[str, Any]:
        payload = await self._meetup.search_events(city=city, topic=topic, first=limit)
        edges = payload.get("data", {}).get("keywordSearch", {}).get("edges", [])

        events: list[dict[str, Any]] = []
        for edge in edges:
            event = edge.get("node", {}).get("result", {})
            if not event:
                continue
            events.append(
                {
                    "id": event.get("id"),
                    "title": event.get("title"),
                    "date_time": event.get("dateTime"),
                    "event_url": event.get("eventUrl"),
                    "group": (event.get("group") or {}).get("name"),
                    "venue": (event.get("venue") or {}).get("name"),
                }
            )

        return {"city": city, "topic": topic, "events": events}
