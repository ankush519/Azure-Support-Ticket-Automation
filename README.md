# Azure Support Ticket Automation

An ML-powered support ticket automation system built with FastAPI, Scikit-learn, SQLite, Docker, and GitHub Actions. The system classifies incoming tickets, assigns priority and a support team, generates draft responses, and supports a human approval workflow.

## Features

- **Ticket classification:** Predicts Billing, Technical, Access, or General categories using TF-IDF and Logistic Regression.
- **Priority assignment:** Assigns High, Medium, or Low priority using rule-based logic.
- **Team assignment:** Routes tickets to the relevant support team.
- **Draft responses:** Generates an initial response for support agents to review.
- **Confidence monitoring:** Flags low-confidence predictions for human review.
- **Ticket persistence:** Stores ticket details and workflow status in SQLite.
- **Approval workflow:** Supports approval or rejection of pending tickets.
- **Input validation:** Rejects invalid requests and duplicate ticket IDs.
- **Automated tests:** Uses Pytest and GitHub Actions for continuous integration.
- **Containerization:** Includes a Dockerfile for local container execution.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Machine Learning | Scikit-learn, TF-IDF, Logistic Regression |
| Database | SQLite |
| Testing | Pytest |
| Containerization | Docker |
| CI | GitHub Actions |
| Planned Cloud Hosting | Azure App Service |

## Project Structure

```text
Azure-Support-Ticket-Automation/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Backend/
│   ├── app/
│   │   ├── classifier.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── ticket_model.joblib
│   │   └── train_model.py
│   ├── sample_data/
│   │   └── tickets.csv
│   ├── tests/
│   │   └── test_api.py
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
├── docs/
│   └── azure-plan.md
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.12
- pip
- Git
- Docker (optional, for container execution)

## Run Locally

Open a terminal in the `Backend` directory.

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Start the API

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

- API base URL: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/tickets` | Create and classify a ticket |
| GET | `/tickets/{ticket_id}` | Retrieve a stored ticket |
| POST | `/tickets/{ticket_id}/approval` | Approve or reject a pending ticket |

Use the interactive API documentation at `/docs` to submit requests and inspect responses.

## Example Ticket Request

```json
{
  "ticket_id": 101,
  "message": "My payment was deducted but my order was not confirmed"
}
```

The response includes the predicted category, priority, assigned team, summary, draft response, ticket status, confidence score, and review flag.

New tickets begin in `Pending Approval`. The approval endpoint can transition a pending ticket to `Ready for Use` or `Rejected`.

## Machine Learning Approach

1. Prepare labelled sample support tickets.
2. Separate the designated test examples from training data.
3. Convert ticket text into numerical features using TF-IDF.
4. Train a Logistic Regression classifier.
5. Evaluate predictions on the held-out test examples.
6. Use the classifier's confidence score to flag uncertain predictions for review.

Priority assignment and support-team mapping use application rules in addition to the category classifier.

The measured evaluation score should be reported alongside the evaluation procedure and dataset limitations; it should not be interpreted as a guarantee of production performance.

## Run Tests

From the `Backend` directory:

```powershell
python -m pytest -v
```

The current backend test suite contains seven tests covering health checks, invalid inputs, ticket creation and retrieval, duplicate IDs, approval, rejection, and missing tickets.

## Run with Docker

From the `Backend` directory, build the image:

```powershell
docker build -t azure-support-ticket-api .
```

Run the container with persistent storage for the SQLite database:

```powershell
docker volume create ticket-data
docker run --name ticket-api -p 8000:8000 -v ticket-data:/app/data azure-support-ticket-api
```

Open http://localhost:8000/docs to interact with the API.

If a container with the name `ticket-api` already exists, stop and remove that container before recreating it. The named volume can be reused to retain its database contents.

## Continuous Integration

GitHub Actions runs the backend test suite when changes are pushed to `main` or a pull request targets `main`.

Workflow file: `.github/workflows/ci.yml`

## Azure Deployment

The Azure App Service deployment plan, configuration notes, verification checklist, and planned GitHub OIDC setup are documented in [`docs/azure-plan.md`](docs/azure-plan.md).

Azure deployment is not considered complete until the application is deployed and verified in the cloud.

## Limitations and Future Improvements

- Expand and diversify the labelled ticket dataset.
- Evaluate on a fresh, representative test set before production use.
- Improve confidence calibration and review thresholds.
- Add authentication and authorization to sensitive approval operations.
- Consider a managed persistent database for production hosting.
- Add monitoring, structured logs, and production deployment verification.

## License

See the repository's `LICENSE` file.
