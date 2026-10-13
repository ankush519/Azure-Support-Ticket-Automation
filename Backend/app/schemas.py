from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    ticket_id: int = Field(gt=0)
    message: str = Field(min_length=5, max_length=2000)


class TicketResponse(BaseModel):
    ticket_id: int
    category: str
    priority: str
    assigned_team: str
    summary: str
    draft_response: str
    status: str
    confidence: float
    review_required: bool


class ApprovalRequest(BaseModel):
    approved: bool
