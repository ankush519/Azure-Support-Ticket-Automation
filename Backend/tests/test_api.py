import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_ticket_id():
    return uuid.uuid4().int % 1_000_000_000 + 1


def create_ticket(ticket_id=None):
    ticket_id = ticket_id or unique_ticket_id()
    response = client.post(
        "/tickets",
        json={
            "ticket_id": ticket_id,
            "message": "I need help with my account and billing question",
        },
    )
    return ticket_id, response


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200


def test_invalid_ticket_input():
    response = client.post(
        "/tickets",
        json={"ticket_id": -1, "message": "Hi"},
    )
    assert response.status_code == 422


def test_create_and_retrieve_ticket():
    ticket_id, response = create_ticket()

    assert response.status_code == 200
    body = response.json()
    assert body["ticket_id"] == ticket_id
    assert body["status"] == "Pending Approval"
    assert 0 <= body["confidence"] <= 1
    assert isinstance(body["review_required"], bool)

    retrieved = client.get(f"/tickets/{ticket_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["ticket_id"] == ticket_id
    assert retrieved.json()["confidence"] == body["confidence"]


def test_duplicate_ticket_id_is_rejected():
    ticket_id, first = create_ticket()
    assert first.status_code == 200

    duplicate = client.post(
        "/tickets",
        json={
            "ticket_id": ticket_id,
            "message": "A different message for the same ID",
        },
    )
    assert duplicate.status_code == 409


def test_approval_and_repeat_approval():
    ticket_id, created = create_ticket()
    assert created.status_code == 200

    approved = client.post(
        f"/tickets/{ticket_id}/approval",
        json={"approved": True},
    )
    assert approved.status_code == 200

    retrieved = client.get(f"/tickets/{ticket_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["status"] == "Ready for Use"

    repeated = client.post(
        f"/tickets/{ticket_id}/approval",
        json={"approved": True},
    )
    assert repeated.status_code == 409


def test_reject_ticket():
    ticket_id, created = create_ticket()
    assert created.status_code == 200

    rejected = client.post(
        f"/tickets/{ticket_id}/approval",
        json={"approved": False},
    )
    assert rejected.status_code == 200

    retrieved = client.get(f"/tickets/{ticket_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["status"] == "Rejected"


def test_missing_ticket_returns_404():
    response = client.get(f"/tickets/{unique_ticket_id()}")
    assert response.status_code == 404
