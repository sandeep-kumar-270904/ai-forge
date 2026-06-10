# CI/CD Pipelines

**STATUS: INCOMPLETE (Implementation Not Found During Analysis)**

## Missing Pipeline Automation
The repository does not currently contain GitHub Actions, GitLab CI, or CircleCI configurations.

## Proposed Pipeline Workflow

### 1. Continuous Integration (PR Trigger)
1.  **Linting:** Execute `flake8` and `black`.
2.  **Type Checking:** Execute `mypy` for static typing validation.
3.  **Unit Tests:** Run `pytest` against mocked LLM endpoints.
4.  **AI Evaluations:** Trigger the `/api/v1/evaluations` framework against a lightweight smoke-test Golden Dataset to ensure prompt changes haven't degraded logic.

### 2. Continuous Deployment (Main Branch Trigger)
1.  **Build:** Build the Docker image.
2.  **Tag:** Tag with git SHA and Semantic Version.
3.  **Push:** Push to Elastic Container Registry (ECR).
4.  **Deploy:** Trigger ArgoCD sync or execute `helm upgrade` against the Staging cluster.

## Rollback Procedures
Because AIForge strictly versions Prompts, an AI logic rollback does not require a code deployment. A Tenant Admin can simply update the active `PromptDeployment` to point to a previous `PromptVersion` via the API.
Database rollbacks must be handled via standard PostgreSQL Point-in-Time-Recovery (PITR).
