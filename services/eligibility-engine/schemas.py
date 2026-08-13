# Import shared types - do not redefine these locally.
from pydantic import BaseModel


class EligibilityCheckRequest(BaseModel):
    case_id: str


class EligibilityOverrideRequest(BaseModel):
    case_id: str
    actor_user_id: str
    reason: str


class ErrorResponse(BaseModel):
    code: str
    message: str
