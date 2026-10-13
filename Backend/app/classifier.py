from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).with_name("ticket_model.joblib")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at {MODEL_PATH}. "
        "Run: python -m app.train_model"
    )

model = joblib.load(MODEL_PATH)

TEAM_BY_CATEGORY = {
    "Billing": "Billing Support",
    "Technical": "Technical Support",
    "Access": "Account Support",
    "General": "General Support",
}

RESPONSE_BY_CATEGORY = {
    "Billing": (
        "Thank you for contacting us about a billing issue. "
        "Our billing support team will review your request."
    ),
    "Technical": (
        "Thank you for reporting this technical issue. "
        "Our technical support team will investigate it."
    ),
    "Access": (
        "Thank you for contacting us about account access. "
        "Our account support team will help you."
    ),
    "General": (
        "Thank you for contacting support. "
        "Our team will review your question and assist you."
    ),
}


def classify_ticket(message: str) -> dict:
    text = message.lower()

    
    # Predict the category using the trained ML model.
    probabilities = model.predict_proba([message])[0]
    best_index = probabilities.argmax()

    category = str(model.classes_[best_index])
    confidence = float(probabilities[best_index])

    # Keep the model prediction, but flag uncertain tickets for review.
    review_required = confidence < 0.55
   
    # Priority remains rule-based for now.
    if any(word in text for word in [
        "urgent", "critical", "completely down",
        "emergency", "entire service is down"
    ]):
        priority = "High"
    elif any(word in text for word in [
        "cannot", "can't", "unable", "failed", "error",
        "crash", "crashes", "crashing", "freezing",
        "frozen", "not responding"
    ]):
        priority = "Medium"
    else:
        priority = "Low"

    assigned_team = TEAM_BY_CATEGORY[category]
    draft_response = RESPONSE_BY_CATEGORY[category]

    # Keep the summary simple for this first version.
    summary = message.strip()
    if len(summary) > 120:
        summary = summary[:117] + "..."

    return {
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
        "summary": summary,
        "draft_response": draft_response,
        "status": "Pending Approval",
        "confidence": round(confidence, 3),
        "review_required": review_required,
    }
