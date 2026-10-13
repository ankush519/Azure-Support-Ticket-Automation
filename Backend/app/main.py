import sqlite3
from fastapi import FastAPI, HTTPException

from app.schemas import TicketRequest, TicketResponse, ApprovalRequest
from app.classifier import classify_ticket
from app.database import init_db, save_ticket, get_ticket, update_ticket_status

app = FastAPI(
    title="Azure Support Ticket Automation",
    description="AI-assisted support ticket processing API",
    version="1.0.0",
)
init_db() # Initialize the database when the app starts


@app.get("/")
def home():
    return {
        "message": "Support Ticket Automation API is running!"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket: TicketRequest):
    result = classify_ticket(ticket.message)

    try:
        save_ticket(ticket, result)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A ticket with this ID already exists.",
        )

    return {
        "ticket_id": ticket.ticket_id,
        **result,
    }


@app.get("/tickets/{ticket_id}")
def read_ticket(ticket_id: int):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    return ticket


@app.post("/tickets/{ticket_id}/approval")
def approve_ticket(
    ticket_id: int,
    approval: ApprovalRequest,
):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    if ticket["status"] != "Pending Approval":
        raise HTTPException(
            status_code=409,
            detail="This ticket has already been reviewed.",
        )

    new_status = (
        "Ready for Use"
        if approval.approved
        else "Rejected"
    )

    updated = update_ticket_status(ticket_id, new_status)

    if not updated:
        raise HTTPException(
            status_code=409,
            detail="Ticket status changed. Please review it again.",
        )

    return {
        "ticket_id": ticket_id,
        "status": new_status,
        "message": (
            "Draft approved successfully."
            if approval.approved
            else "Draft rejected."
        ),
    }
