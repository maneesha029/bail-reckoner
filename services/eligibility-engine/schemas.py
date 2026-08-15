# Import shared types - do not redefine these locally.
from pydantic import BaseModel


class EligibilityCheckRequest(BaseModel):
    case_id: str


class EligibilityOverrideRequest(BaseModel):
    case_id: str
    actor_user_id: str
    reason: str
    expected_version: int | None = None
    # Optimistic locking: if the caller supplies expected_version and it
    # no longer matches the case's current version, the write is rejected
    # with 409 rather than silently overwriting a decision made in
    # between the caller's read and this write.


class ErrorResponse(BaseModel):
    code: str
    message: str
