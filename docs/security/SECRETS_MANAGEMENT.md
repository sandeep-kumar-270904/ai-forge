# Secrets Management

**Implementation Status: DEVELOPMENT ONLY**

## Current Implementation
AIForge currently loads secrets via the `pydantic-settings` module from a local `.env` file or standard environment variables.

| Secret Key | Purpose | Risk if Compromised |
| :--- | :--- | :--- |
| `SECRET_KEY` | Signs all user JWTs | Complete system takeover. Attacker can forge Admin JWTs. |
| `DATABASE_URL` | Connects to Postgres | Total data breach / destruction. |
| `OPENAI_API_KEY`| Accesses OpenAI | Financial drain. |

## Production Architecture Gap
*Storing these variables in plain text or injecting them directly into Kubernetes Pod YAMLs is insecure and violates enterprise compliance.*

### Recommended Fix (Phase 2 Roadmap)
AIForge must be integrated with an external Secrets Manager (e.g., **AWS Secrets Manager** or **HashiCorp Vault**).

1.  **IAM Roles:** The Kubernetes Service Account must be mapped to an AWS IAM Role (IRSA).
2.  **Runtime Injection:** The application should use an init-container or the AWS Secrets Provider CSI driver to mount secrets into memory `/var/run/secrets` rather than passing them via the environment.
3.  **Rotation:** The `SECRET_KEY` should be rotated automatically every 90 days. The FastAPI application must be configured to accept a list of valid keys to gracefully handle rotation windows without invalidating active sessions.
