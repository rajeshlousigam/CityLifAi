"""
Tools for a data.gov.in assistant agent.
"""
import os
from typing import Any, Dict, List

from datagovindia import data
from langchain_core.tools import tool

API_KEY = os.getenv("DATAGOVINDIA_API_KEY")
if API_KEY:
    data.set_api_key(API_KEY)

CATEGORY_HINTS: Dict[str, List[str]] = {
    "agriculture": ["crop", "farmer", "soil", "irrigation", "mandi", "rainfall"],
    "health": ["hospital", "disease", "vaccination", "public health", "medicine"],
    "education": ["school", "college", "enrollment", "literacy", "teacher"],
    "transport": ["road", "railway", "metro", "traffic", "vehicle", "mobility"],
    "environment": ["air quality", "water quality", "pollution", "climate", "forest"],
    "economy": ["gdp", "inflation", "industry", "trade", "finance", "budget"],
    "employment": ["jobs", "unemployment", "labor", "skill", "workforce"],
    "energy": ["electricity", "power", "renewable", "solar", "coal", "fuel"],
    "housing": ["housing", "urban", "rural development", "construction", "real estate"],
    "demographics": ["population", "census", "gender", "age", "migration"],
    "crime": ["crime", "police", "offence", "safety", "law and order"],
    "tourism": ["tourism", "visitor", "hotel", "destination", "travel"],
}


def _guess_category(text: str) -> str:
    text_lower = text.lower()
    scores: Dict[str, int] = {}
    for category, hints in CATEGORY_HINTS.items():
        scores[category] = sum(1 for hint in hints if hint in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def _pick_str(record: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "N/A"


def _normalize_records(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return [row for row in raw if isinstance(row, dict)]

    if isinstance(raw, dict):
        for key in ["records", "results", "data", "items"]:
            if key in raw and isinstance(raw[key], list):
                return [row for row in raw[key] if isinstance(row, dict)]
        return [raw]

    return []


@tool
def list_data_categories() -> str:
    """List supported high-level categories to help users pick the right domain."""
    categories = sorted(CATEGORY_HINTS.keys())
    return "Available categories:\n" + "\n".join(f"- {category}" for category in categories)


@tool
def get_category_questions(user_goal: str, category: str = "") -> str:
    """
    Generate category-wise clarifying questions so users can ask context-rich queries.

    Args:
        user_goal: User's objective in plain language
        category: Optional category selected by user
    """
    chosen = category.strip().lower() if category else _guess_category(user_goal)

    common_questions = [
        "Which state, district, or city should I focus on?",
        "What time period do you need (year/month/range)?",
        "Do you need latest data or historical trends?",
        "Do you need dataset metadata only, or actual records too?",
    ]

    category_specific_questions: Dict[str, List[str]] = {
        "agriculture": [
            "Which crop or commodity are you interested in?",
            "Do you need production, yield, area, or price data?",
        ],
        "health": [
            "Which health topic: disease burden, hospitals, vaccination, or mortality?",
            "Do you need facility-wise data or district/state aggregates?",
        ],
        "education": [
            "Which level: primary, secondary, or higher education?",
            "Do you need enrollment, outcomes, or infrastructure data?",
        ],
        "transport": [
            "Which mode: road, rail, metro, aviation, or waterways?",
            "Do you need traffic volume, accidents, or infrastructure indicators?",
        ],
        "environment": [
            "Which indicator: air, water, waste, climate, or forest cover?",
            "Do you need station-level readings or regional aggregates?",
        ],
    }

    category_questions = category_specific_questions.get(
        chosen,
        [
            "Which exact topic or indicator should I search for?",
            "Do you have a preferred ministry or department?",
        ],
    )

    lines = [f"Suggested category: {chosen}", "Ask the user these questions first:"]
    lines.extend(f"- {question}" for question in category_questions + common_questions)
    return "\n".join(lines)


@tool
def search_data_gov_datasets(query: str, category: str = "", limit: int = 8) -> str:
    """
    Search data.gov.in datasets using datagovindia wrapper.

    Args:
        query: Search phrase
        category: Optional category to refine search
        limit: Max result rows to format
    """
    if not API_KEY:
        return "DATAGOVINDIA_API_KEY is not set. Set it in environment and retry."

    if limit < 1:
        limit = 1
    if limit > 20:
        limit = 20

    category_clean = category.strip().lower()
    guessed = category_clean if category_clean else _guess_category(query)
    final_query = f"{guessed} {query}".strip() if guessed != "general" else query

    try:
        raw = data.get_data(final_query)
        records = _normalize_records(raw)

        if not records:
            return (
                f"No dataset results found for query='{final_query}'. "
                "Try a narrower location, timeframe, or indicator."
            )

        lines = [f"Top {min(limit, len(records))} datasets for '{final_query}':"]
        for index, record in enumerate(records[:limit], start=1):
            title = _pick_str(record, ["title", "name", "dataset_title", "resource_title"])
            description = _pick_str(record, ["description", "desc", "dataset_desc"])
            source = _pick_str(record, ["organization", "org", "ministry", "source"])
            url = _pick_str(record, ["url", "dataset_url", "resource_url", "link"])

            lines.append(f"{index}. {title}")
            lines.append(f"   Source: {source}")
            lines.append(f"   Description: {description[:220]}")
            lines.append(f"   URL: {url}")

        return "\n".join(lines)
    except Exception as exc:
        return f"Error while searching data.gov.in: {exc}"
