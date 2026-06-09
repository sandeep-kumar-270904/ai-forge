from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    email = "testqa@aiforge.com"
    password = "testpassword"
    
    # Register
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code in [200, 400] # 400 if already exists
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
