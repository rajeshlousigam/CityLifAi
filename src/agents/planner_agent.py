from __future__ import annotations

import asyncio
import re
from datetime import date

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.events_agent import EventsAgent
from agents.food_agent import FoodAgent
from agents.sports_agent import SportsAgent
from agents.traffic_agent import TrafficAgent
from agents.weekend_agent import WeekendAgent
from config.settings import Settings
from services.schemas import PlannerItinerary


class PlannerAgent:
    SYSTEM_PROMPT = (
        "You are PlannerAgent, the orchestrator for CityLife AI in Bangalore. "
        "Synthesize traffic, food, sports, events, and weekend data into one day plan."
    )

    def __init__(
        self,
        traffic_agent: TrafficAgent,
        food_agent: FoodAgent,
        sports_agent: SportsAgent,
        events_agent: EventsAgent,
        weekend_agent: WeekendAgent,
        settings: Settings,
    ) -> None:
        self._traffic_agent = traffic_agent
        self._food_agent = food_agent
        self._sports_agent = sports_agent
        self._events_agent = events_agent
        self._weekend_agent = weekend_agent
        self._settings = settings
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0.2, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    def _extract_city(self, user_query: str) -> str:
        # Lightweight city extraction with safe fallback for Bangalore-centric planning.
        match = re.search(r"in\s+([A-Za-z\s]+)$", user_query.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return self._settings.default_city

    async def run(self, user_query: str) -> dict:
        city = self._extract_city(user_query)
        planning_date = date.today().isoformat()

        food_task = self._food_agent.run(city=city, cuisine=None)
        sports_task = self._sports_agent.run(city=city, sport="badminton", date=planning_date)
        events_task = self._events_agent.run(city=city, topic="tech")
        weekend_task = self._weekend_agent.run(city=city)
        traffic_task = self._traffic_agent.run(origin=f"MG Road, {city}", destination=f"Koramangala, {city}")

        food, sports, events, weekend, traffic = await asyncio.gather(
            food_task, sports_task, events_task, weekend_task, traffic_task
        )

        lunch_spot = (
            (food.get("restaurants") or [{}])[0].get("name")
            if food.get("restaurants")
            else "Popular lunch spot in Bangalore"
        )
        evening_sport = (
            (sports.get("slots") or [{}])[0].get("venue")
            if sports.get("slots")
            else "Nearby turf session"
        )
        night_event = (
            (events.get("events") or [{}])[0].get("title")
            if events.get("events")
            else "Local community meetup"
        )
        morning_idea = (weekend.get("ideas") or ["Sunrise walk at Cubbon Park"])[0]

        base = PlannerItinerary(
            morning=morning_idea,
            lunch=f"{lunch_spot}",
            evening=f"Play at {evening_sport}",
            night=f"Attend {night_event}",
            routes=(
                f"MG Road -> Koramangala | Distance: {traffic.get('distance')} | "
                f"ETA: {traffic.get('traffic_eta')}"
            ),
            details={
                "city": city,
                "query": user_query,
                "traffic": traffic,
                "food": food,
                "sports": sports,
                "events": events,
                "weekend": weekend,
            },
        )

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                (
                    "human",
                    "User query: {query}\n"
                    "City: {city}\n"
                    "Signals: {signals}\n"
                    "Return PlannerItinerary as final output.",
                ),
            ]
        )
        chain = prompt | self._llm.with_structured_output(PlannerItinerary)
        response = await chain.ainvoke(
            {"query": user_query, "city": city, "signals": base.model_dump()}
        )
        return response.model_dump()
