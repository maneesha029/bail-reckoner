"""Request and local response schemas for the precedent engine."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, validator

# FIX: same root cause as routes.py - docker-compose mounts individual
# shared_schemas files flat into /app, not as a `shared_schemas` package.
# This needs models.py mounted too (see docker-compose-patch.txt) and
# imported flat, matching how audit_client.py is already imported.
from models import PrecedentCitation, PrecedentResult


OFFENSE_CATEGORIES = {
    "cyber_crimes", "crimes_against_sc_st", "crimes_against_women",
    "crimes_against_children", "offences_against_state", "economic_offences",
    "crimes_against_foreigners", "general",
}
DISCRETION_FACTORS = {"flight_risk", "witness_influence", "general_precedent"}


class QueryContext(BaseModel):
    offense_category: str
    discretion_factors: list[str] = Field(default_factory=list)

    @validator("offense_category")
    def valid_category(cls, value: str) -> str:
        if value not in OFFENSE_CATEGORIES:
            raise ValueError("unsupported offense_category")
        return value

    @validator("discretion_factors", each_item=True)
    def valid_factor(cls, value: str) -> str:
        if value not in DISCRETION_FACTORS:
            raise ValueError("unsupported discretion factor")
        return value


class PrecedentSearchRequest(BaseModel):
    case_id: str = Field(..., min_length=1)
    query_context: QueryContext


class ChargeSummaryInput(BaseModel):
    act: str = Field(..., min_length=1)
    section: str = Field(..., min_length=1)
    offense_category: str = Field(..., min_length=1)

    @validator("act", "section", "offense_category")
    def no_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value.strip()


class CaseSummaryRequest(BaseModel):
    case_id: str = Field(..., min_length=1)
    charges: list[ChargeSummaryInput] = Field(..., min_items=1)
    case_notes: str | None = None


class CitedSection(BaseModel):
    section: str
    act: str
    description: str


class CaseSummaryResponse(BaseModel):
    case_id: str
    summary: str = Field(..., min_length=1)
    cited_sections: list[CitedSection]
    generated_at: str


def model_dump(model: Any) -> dict[str, Any]:
    """Support the Pydantic v1 and v2 versions used by repository services."""
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


def envelope(data: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
    return {"success": error is None, "data": data, "error": error}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


__all__ = [
    "CaseSummaryRequest", "CaseSummaryResponse", "ChargeSummaryInput",
    "CitedSection", "DISCRETION_FACTORS", "OFFENSE_CATEGORIES",
    "PrecedentCitation", "PrecedentResult", "PrecedentSearchRequest",
    "envelope", "model_dump", "utc_now",
]