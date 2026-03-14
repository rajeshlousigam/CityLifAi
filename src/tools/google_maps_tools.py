from __future__ import annotations

from typing import Any

from services.api_clients import ApiClients


class GoogleMapsTools:
    def __init__(self, clients: ApiClients) -> None:
        self._maps = clients.google_maps

    async def route(self, origin: str, destination: str) -> dict[str, Any]:
        payload = await self._maps.get_directions(origin=origin, destination=destination)
        routes = payload.get("routes", [])
        if not routes:
            return {"summary": "No route found", "distance": "Unknown", "duration": "Unknown"}

        leg = routes[0].get("legs", [{}])[0]
        return {
            "summary": routes[0].get("summary", ""),
            "distance": leg.get("distance", {}).get("text", "Unknown"),
            "duration": leg.get("duration", {}).get("text", "Unknown"),
        }

    async def traffic(self, origin: str, destination: str) -> dict[str, Any]:
        payload = await self._maps.get_traffic(origin=origin, destination=destination)
        rows = payload.get("rows", [])
        if not rows or not rows[0].get("elements"):
            return {"distance": "Unknown", "normal_eta": "Unknown", "traffic_eta": "Unknown"}

        cell = rows[0]["elements"][0]
        return {
            "distance": cell.get("distance", {}).get("text", "Unknown"),
            "normal_eta": cell.get("duration", {}).get("text", "Unknown"),
            "traffic_eta": cell.get("duration_in_traffic", {}).get("text", "Unknown"),
        }
