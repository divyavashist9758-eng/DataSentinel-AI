def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_user_registration_and_login(client):
    reg_payload = {
        "email": "jane@example.com",
        "username": "janedoe",
        "full_name": "Jane Doe",
        "password": "SecurePassword123!",
        "role": "analyst"
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    assert reg_resp.json()["username"] == "janedoe"

    # Test login with newly created user
    login_resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "janedoe",
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert len(token) > 20

    # Test /me endpoint
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "jane@example.com"

def test_duplicate_registration_fails(client):
    reg_payload = {
        "email": "jane@example.com",
        "username": "janedoe2",
        "password": "SecurePassword123!"
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert resp.status_code == 422
    assert "already registered" in resp.json()["detail"]

