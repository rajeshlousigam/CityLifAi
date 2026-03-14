from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import Settings
from services.schemas import FoodResponse
from tools.restaurant_tools import RestaurantTools


class FoodAgent:
    SYSTEM_PROMPT = (
        "You are FoodAgent for Bangalore. "
        "Recommend practical restaurant options with ratings and location context."
    )

    def __init__(self, tools: RestaurantTools, settings: Settings) -> None:
        self._tools = tools
        self._llm = (
            ChatOpenAI(model=settings.openai_model, temperature=0.1, api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )

    async def run(self, city: str, cuisine: str | None = None) -> dict:
        data = await self._tools.find_restaurants(city=city, cuisine=cuisine)
        base = FoodResponse(city=city, cuisine=cuisine, restaurants=data.get("restaurants", []))

        if not self._llm:
            return base.model_dump()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                ("human", "City: {city}\nCuisine: {cuisine}\nRestaurants: {restaurants}\nFormat as FoodResponse."),
            ]
        )
        chain = prompt | self._llm.with_structured_output(FoodResponse)
        response = await chain.ainvoke({"city": city, "cuisine": cuisine, "restaurants": data.get("restaurants", [])})
        return response.model_dump()
