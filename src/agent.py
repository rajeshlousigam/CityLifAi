"""Template-compatible entry class for CityLife AI."""

from services.orchestrator import CityLifeOrchestrator


class Agent:
    def __init__(self) -> None:
        self.name = "CityLife AI"
        self._orchestrator = CityLifeOrchestrator()

    async def process_message(self, message_text: str) -> dict:
        """Process the incoming message via PlannerAgent orchestration."""
        return await self._orchestrator.plan_day(user_query=message_text)
