"""Tests for registration, login, and the authenticated /me endpoint."""

CREDS = {"email": "user@example.com", "password": "password123"}


def test_register_returns_user_without_password(client):
    r = client.post("/auth/register", json=CREDS)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == CREDS["email"]
    assert "id" in body
    assert "password" not in body and "hashed_password" not in body


def test_register_rejects_duplicate_email(client):
    client.post("/auth/register", json=CREDS)
    r = client.post("/auth/register", json=CREDS)
    assert r.status_code == 400


def test_register_rejects_short_password(client):
    r = client.post(
        "/auth/register", json={"email": "x@example.com", "password": "short"}
    )
    assert r.status_code == 422


def test_register_rejects_bad_email(client):
    r = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "password123"}
    )
    assert r.status_code == 422


def test_login_returns_token(client):
    client.post("/auth/register", json=CREDS)
    r = client.post("/auth/login", json=CREDS)
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    client.post("/auth/register", json=CREDS)
    r = client.post(
        "/auth/login", json={"email": CREDS["email"], "password": "wrongpass1"}
    )
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    r = client.get("/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "organizer@example.com"


def test_me_rejects_garbage_token(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401
