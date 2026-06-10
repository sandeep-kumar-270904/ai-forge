# Authentication Architecture

AIForge utilizes stateless JSON Web Tokens (JWT) for authentication, relying on the OAuth2 Password Bearer flow.

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant DB
    
    Client->>AuthRouter: POST /login (username, password)
    AuthRouter->>DB: Fetch User
    DB-->>AuthRouter: User Record + Hashed Password
    Note over AuthRouter: Verify passlib hash
    
    alt Success
        Note over AuthRouter: Sign JWT with SECRET_KEY
        AuthRouter-->>Client: 200 OK { access_token }
    else Failure
        AuthRouter-->>Client: 401 Unauthorized
    end
    
    Client->>AuthRouter: GET /protected (Bearer Token)
    Note over AuthRouter: Verify JWT Signature
    AuthRouter-->>Client: 200 OK
```

## JWT Payload Structure
The JWT payload inherently binds the user to a specific tenant to prevent multi-tenant data leaks.
```json
{
  "sub": "user_id_uuid",
  "tenant_id": "tenant_id_uuid",
  "role": "admin",
  "exp": 1718000000
}
```

## Security Posture
*   **Algorithms:** RS256 or HS256 (configurable).
*   **Expirations:** Access tokens expire every 30 minutes. Refresh tokens expire in 7 days.
*   **Revocation:** Stateless JWTs cannot be easily revoked. A Redis-based JWT blocklist is planned for Phase 3 to handle immediate user terminations.
