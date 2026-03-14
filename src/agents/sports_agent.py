from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import Settings
from services.schemas import SportsResponse
from tools.sports_tools import SportsTools


class SportsAgent:
    SYSTEM_PROMPT = (
        "You are SportsAgent for Bangalore. "
        "Suggest playable sports slots from booking API results and keep output concise."
    )

    def __init__(self, tools: SportsTools, settings: Settings) -> None:
        self._tools = tools
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0.1, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    async def run(self, city: str, sport: str, date: str) -> dict:
        data = await self._tools.find_slots(city=city, sport=sport, date=date)
        base = SportsResponse(city=city, sport=sport, date=date, slots=data.get("slots", []))

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                ("human", "City: {city}\nSport: {sport}\nDate: {date}\nSlots: {slots}\nFormat as SportsResponse."),
            ]
        )
        chain = prompt | self._llm.with_structured_output(SportsResponse)
        response = await chain.ainvoke(
            {"city": city, "sport": sport, "date": date, "slots": data.get("slots", [])}
        )
        return response.model_dump()
