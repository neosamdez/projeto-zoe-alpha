import uuid


class TestAuthRegister:
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Novo Usuario",
            "email": "novo@test.io",
            "password": "senha2026",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "novo@test.io"
        assert "id" in data

    def test_register_creates_new_tenant(self, client, seed_admin):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Dup",
                "email": seed_admin.email,
                "password": "senha2026",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["tenant_id"] != str(seed_admin.tenant_id)
        assert data["role"] == "TECHNICIAN"


class TestAuthLogin:
    def test_login_success(self, client, seed_admin):
        response = client.post("/api/v1/auth/login", data={
            "username": seed_admin.email,
            "password": "test2026",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, seed_admin):
        response = client.post("/api/v1/auth/login", data={
            "username": seed_admin.email,
            "password": "wrong",
        })
        assert response.status_code == 401


class TestAuthMe:
    def test_me_authenticated(self, client, admin_headers, seed_admin):
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == seed_admin.email
