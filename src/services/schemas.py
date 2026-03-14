from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TrafficResponse(BaseModel):
    origin: str
    destination: str
    distance: str
    normal_eta: str
    traffic_eta: str
    route_summary: str


class FoodResponse(BaseModel):
    city: str
    cuisine: str | None = None
    restaurants: list[dict[str, Any]] = Field(default_factory=list)


class SportsResponse(BaseModel):
    city: str
    sport: str
    date: str
    slots: list[dict[str, Any]] = Field(default_factory=list)


class EventsResponse(BaseModel):
    city: str
    topic: str
    events: list[dict[str, Any]] = Field(default_factory=list)


class WeekendResponse(BaseModel):
    city: str
    ideas: list[str] = Field(default_factory=list)


class PlannerItinerary(BaseModel):
    morning: str
    lunch: str
    evening: str
    night: str
    routes: str
    details: dict[str, Any] = Field(default_factory=dict)
