def test_register_returns_the_user_without_any_password(client):
    response = client.post("/auth/register", json={
        "email": "Sidd@Example.com", "password": "password-123", "full_name": "Sidd"})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "sidd@example.com"
    assert body["full_name"] == "Sidd"
    assert "password" not in body
    assert "hashed_password" not in body


def test_registering_the_same_email_twice_is_409(client, make_user):
    make_user(email="sidd@example.com")

    response = client.post("/auth/register", json={
        "email": "SIDD@example.com", "password": "another-password"})

    assert response.status_code == 409


def test_login_with_the_wrong_password_is_401(client, make_user):
    user = make_user()

    response = client.post("/auth/token", data={
        "username": user["email"], "password": "wrong-password"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_needs_a_valid_token(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/users/me", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


def test_me_returns_the_logged_in_user(client, make_user):
    user = make_user(email="ana@example.com")

    response = client.get("/users/me", headers=user["headers"])

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_updating_my_name(client, make_user):
    user = make_user()

    response = client.patch("/users/me", json={"full_name": "Ana Lopez"}, headers=user["headers"])

    assert response.status_code == 200
    assert client.get("/users/me", headers=user["headers"]).json()["full_name"] == "Ana Lopez"


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
