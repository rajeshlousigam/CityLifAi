from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import Settings
from services.schemas import WeekendResponse
from tools.events_tools import EventsTools
from tools.restaurant_tools import RestaurantTools


class WeekendAgent:
    SYSTEM_PROMPT = (
        "You are WeekendAgent for Bangalore. "
        "Create fun weekend ideas using real events and food signals."
    )

    def __init__(self, events_tools: EventsTools, food_tools: RestaurantTools, settings: Settings) -> None:
        self._events_tools = events_tools
        self._food_tools = food_tools
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0.3, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    async def run(self, city: str) -> dict:
        events = await self._events_tools.find_events(city=city, topic="weekend")
        food = await self._food_tools.find_restaurants(city=city, cuisine=None, limit=3)

        ideas = []
        for event in events.get("events", [])[:2]:
            title = event.get("title") or "Local meetup"
            ideas.append(f"Attend {title}")
        for restaurant in food.get("restaurants", [])[:2]:
            name = restaurant.get("name") or "a top restaurant"
            ideas.append(f"Try {name} for a relaxed meal")

        base = WeekendResponse(city=city, ideas=ideas)

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                ("human", "City: {city}\nIdeas: {ideas}\nFormat as WeekendResponse."),
            ]
        )
        chain = prompt | self._llm.with_structured_output(WeekendResponse)
        response = await chain.ainvoke({"city": city, "ideas": ideas})
        return response.model_dump()
