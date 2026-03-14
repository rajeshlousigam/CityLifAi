from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import Settings
from services.schemas import EventsResponse
from tools.events_tools import EventsTools


class EventsAgent:
    SYSTEM_PROMPT = (
        "You are EventsAgent for Bangalore. "
        "Pick useful community and tech events for the requested day window."
    )

    def __init__(self, tools: EventsTools, settings: Settings) -> None:
        self._tools = tools
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0.1, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    async def run(self, city: str, topic: str = "tech") -> dict:
        data = await self._tools.find_events(city=city, topic=topic)
        base = EventsResponse(city=city, topic=topic, events=data.get("events", []))

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                ("human", "City: {city}\nTopic: {topic}\nEvents: {events}\nFormat as EventsResponse."),
            ]
        )
        chain = prompt | self._llm.with_structured_output(EventsResponse)
        response = await chain.ainvoke({"city": city, "topic": topic, "events": data.get("events", [])})
        return response.model_dump()
