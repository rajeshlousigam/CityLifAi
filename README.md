# CityLife AI

CityLife AI is a multi-agent planning system for Bangalore that runs on FastAPI + LangChain and calls real external APIs for traffic, restaurants, events, and sports booking.

## Architecture

- Python 3.11
- FastAPI server (A2A JSON-RPC compatible)
- LangChain-powered agents
- Async API calls with `httpx`
- Modular code in `src/agents`, `src/tools`, `src/services`, `src/config`, `src/api`

## Agents

- `PlannerAgent`: orchestrates all sub-agents and builds final itinerary JSON
- `TrafficAgent`: route planning + traffic ETA via Google Maps APIs
- `FoodAgent`: restaurant discovery + rating signals via Google Places API
- `SportsAgent`: Playo-style sports slot discovery via configurable sports API
- `EventsAgent`: tech/community event discovery via Meetup GraphQL API
- `WeekendAgent`: weekend idea synthesis from food + event signals

## Project Structure

```text
src/
    agents/
        planner_agent.py
        traffic_agent.py
        food_agent.py
        sports_agent.py
        events_agent.py
        weekend_agent.py
    tools/
        google_maps_tools.py
        restaurant_tools.py
        sports_tools.py
        events_tools.py
    services/
        orchestrator.py
        api_clients.py
        schemas.py
    api/
        server.py
    config/
        settings.py
    agent.py
    main.py
    __main__.py
    models.py

requirements.txt
.env.example
README.md
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and fill keys:

- `OPENAI_API_KEY`
- `GOOGLE_MAPS_API_KEY`
- `GOOGLE_PLACES_API_KEY`
- `MEETUP_API_TOKEN`
- `SPORTS_API_BASE_URL`
- `SPORTS_API_KEY`
- `SPORTS_API_ENDPOINT` (default: `/activity-public/list/location`)

3. Start the server:

```bash
python src/__main__.py --host 0.0.0.0 --port 8000
```

## API

- `GET /health`: health check
- `POST /`: A2A JSON-RPC endpoint (`message/send`)

Example user message text:

`Plan my Saturday in Bangalore`

The planner returns itinerary JSON shaped like:

```json
{
    "morning": "Sunrise trip",
    "lunch": "Restaurant recommendation",
    "evening": "Sports activity",
    "night": "Event",
    "routes": "Best routes between places",
    "details": {}
}
```

