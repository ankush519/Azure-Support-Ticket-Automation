# Azure Deployment Plan — Azure Support Ticket Automation

## 1. Project Overview

Azure Support Ticket Automation is a FastAPI-based application that automatically classifies customer support tickets into categories such as Billing, Technical, Access, and General.

The application predicts ticket categories using a trained TF-IDF and Logistic Regression model, assigns a priority using rule-based logic, identifies the responsible support team, generates a draft response, and flags low-confidence predictions for human review.

Ticket information and approval status are stored in SQLite.

## 2. Architecture

The application follows this flow:

1. A user submits a support ticket through the API.
2. FastAPI validates the incoming request.
3. The trained machine learning model predicts the ticket category.
4. Rule-based logic assigns the priority and support team.
5. The application generates a summary and draft response.
6. Low-confidence predictions are flagged for review.
7. The ticket and its status are saved in the database.
8. An authorized approval action can mark a pending ticket as `Ready for Use` or `Rejected`.

### Technology Stack

- **Backend:** Python and FastAPI
- **Machine Learning:** Scikit-learn, TF-IDF, Logistic Regression
- **Database:** SQLite
- **Testing:** Pytest
- **Containerization:** Docker
- **Continuous Integration:** GitHub Actions
- **Cloud Hosting:** Azure App Service (planned deployment)

## 3. Azure Hosting Plan

The backend will be hosted on Azure App Service using a Linux-based Python environment.

### Configuration

- **Operating system:** Linux
- **Application framework:** FastAPI
- **Python version:** A version supported by the selected App Service runtime and the project's dependencies
- **Startup command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Application entry point:** `app.main:app`
- **Health endpoint:** `/health`
- **API documentation:** `/docs`

The deployment package must include the application source code, trained model file, and `requirements.txt`.

The startup command assumes the deployed application root contains the `app/` directory. If deploying from the repository root, configure the deployment package or startup command to account for the `Backend/` directory.

## 4. Application Settings

The following settings should be configured in Azure App Service under **Settings → Environment variables**.

| Setting | Purpose |
|---|---|
| `DATABASE_PATH` | Path used to store the SQLite database |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | Set to `1` when using supported code-deployment build automation |

The database path must point to a writable location. For production, SQLite persistence must be planned carefully because local application storage may not provide the durability expected across deployments or instances. A persistent storage solution or managed database should be considered for production use.

No credentials, passwords, or private keys should be committed to the repository.

## 5. GitHub Actions Continuous Integration

The repository contains a workflow at `.github/workflows/ci.yml`.

The CI workflow:

1. Checks out the repository.
2. Sets up Python.
3. Installs backend dependencies.
4. Runs the automated tests using Pytest.

The workflow has been executed successfully, with all seven backend tests passing.

This verifies the automated test workflow; it does not by itself verify deployment to Azure.

## 6. Manual Azure Deployment Procedure

The planned deployment procedure is:

1. Sign in to the Azure portal.
2. Create or select an Azure resource group.
3. Create an Azure App Service plan and a Linux web app with a compatible Python runtime.
4. Configure the application startup command and required environment variables.
5. Configure deployment from GitHub using the App Service Deployment Center or a GitHub Actions deployment workflow.
6. Configure GitHub-to-Azure authentication using OpenID Connect (OIDC).
7. Grant the deployment identity only the permissions required to deploy the application.
8. Configure the repository's GitHub Actions workflow with the App Service name and the required Azure identity settings.
9. Deploy the backend package.
10. Check the application logs and verify the deployed health endpoint.

The actual deployment is complete only after the application has been deployed and verified in Azure.

## 7. GitHub OIDC Authentication

OpenID Connect allows GitHub Actions to authenticate to Azure using short-lived tokens instead of storing a long-lived Azure client secret in the repository.

The planned configuration requires:

- An Azure identity configured for federation with the GitHub repository.
- A federated credential matching the repository and workflow's trusted GitHub context.
- Appropriate Azure role assignments for deployment.
- GitHub Actions secrets or variables for the required non-secret identifiers, such as the Azure client ID, tenant ID, subscription ID, and App Service name, according to the chosen workflow configuration.
- `id-token: write` permission in the deployment workflow.

The deployment workflow should run only for the intended branch and should deploy only after the required checks pass.

The OIDC setup and deployment workflow must be configured and tested before claiming that automated Azure deployment is operational.

## 8. Verification Checklist

After deployment, verify the following:

- [ ] The deployed application starts without errors.
- [ ] `/health` returns a successful response.
- [ ] `/docs` loads the FastAPI API documentation.
- [ ] A valid ticket is classified and persisted.
- [ ] Invalid requests are rejected.
- [ ] Duplicate ticket IDs are rejected.
- [ ] Low-confidence predictions are flagged for review.
- [ ] Ticket approval and rejection behave as expected.
- [ ] Application logs do not expose secrets.
- [ ] Database persistence behaves as expected across restarts and deployments.

## 9. Current Status

- Backend API implemented.
- Machine learning classification and priority logic implemented.
- SQLite ticket persistence implemented.
- Approval workflow implemented.
- Seven automated backend tests passing locally.
- GitHub Actions CI workflow configured and successfully executed.
- Azure App Service deployment documented as a plan; actual cloud deployment and OIDC configuration remain to be completed and verified.
