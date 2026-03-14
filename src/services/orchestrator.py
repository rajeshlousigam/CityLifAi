from __future__ import annotations

from agents.events_agent import EventsAgent
from agents.food_agent import FoodAgent
from agents.planner_agent import PlannerAgent
from agents.sports_agent import SportsAgent
from agents.traffic_agent import TrafficAgent
from agents.weekend_agent import WeekendAgent
from config.settings import get_settings
from services.api_clients import build_api_clients
from tools.events_tools import EventsTools
from tools.google_maps_tools import GoogleMapsTools
from tools.restaurant_tools import RestaurantTools
from tools.sports_tools import SportsTools


class CityLifeOrchestrator:
    """Builds and exposes the CityLife multi-agent execution graph."""

    def __init__(self) -> None:
        settings = get_settings()
        clients = build_api_clients(settings)

        maps_tools = GoogleMapsTools(clients)
        food_tools = RestaurantTools(clients)
        events_tools = EventsTools(clients)
        sports_tools = SportsTools(clients)

        traffic_agent = TrafficAgent(maps_tools, settings)
        food_agent = FoodAgent(food_tools, settings)
        sports_agent = SportsAgent(sports_tools, settings)
        events_agent = EventsAgent(events_tools, settings)
        weekend_agent = WeekendAgent(events_tools, food_tools, settings)

        self._planner = PlannerAgent(
            traffic_agent=traffic_agent,
            food_agent=food_agent,
            sports_agent=sports_agent,
            events_agent=events_agent,
            weekend_agent=weekend_agent,
            settings=settings,
        )

    async def plan_day(self, user_query: str) -> dict:
        return await self._planner.run(user_query=user_query)
