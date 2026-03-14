from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import Settings
from services.schemas import TrafficResponse
from tools.google_maps_tools import GoogleMapsTools


class TrafficAgent:
    SYSTEM_PROMPT = (
        "You are TrafficAgent for Bangalore commuting. "
        "Return only structured route and ETA insights for urban travel planning."
    )

    def __init__(self, tools: GoogleMapsTools, settings: Settings) -> None:
        self._tools = tools
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    async def run(self, origin: str, destination: str) -> dict:
        route = await self._tools.route(origin=origin, destination=destination)
        traffic = await self._tools.traffic(origin=origin, destination=destination)

        base = TrafficResponse(
            origin=origin,
            destination=destination,
            distance=traffic.get("distance", "Unknown"),
            normal_eta=traffic.get("normal_eta", "Unknown"),
            traffic_eta=traffic.get("traffic_eta", "Unknown"),
            route_summary=route.get("summary", ""),
        )

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                (
                    "human",
                    "Origin: {origin}\nDestination: {destination}\nRoute: {route}\nTraffic: {traffic}\n"
                    "Format as TrafficResponse.",
                ),
            ]
        )
        chain = prompt | self._llm.with_structured_output(TrafficResponse)
        response = await chain.ainvoke({"origin": origin, "destination": destination, "route": route, "traffic": traffic})
        return response.model_dump()
