class TestDiscardsCRUD:
    def test_create_discard(self, client, admin_headers):
        response = client.post("/api/v1/discards/", headers=admin_headers, json={
            "serial": "SN12345678",
            "product_type": "TV",
            "discard_type": "DESCARTE",
            "reason": "Defeito irreparável",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["serial"] == "SN12345678"

    def test_list_discards(self, client, admin_headers):
        response = client.get("/api/v1/discards/", headers=admin_headers)
        assert response.status_code == 200

    def test_discard_report(self, client, admin_headers):
        response = client.get("/api/v1/discards/report", headers=admin_headers)
        assert response.status_code == 200

    def test_authorize_discard_admin_only(self, client, tech_headers):
        response = client.patch("/api/v1/discards/00000000-0000-0000-0000-000000000000/authorize", headers=tech_headers, json={})
        assert response.status_code in (403, 404)

    def test_discards_unauthenticated(self, client):
        response = client.get("/api/v1/discards/")
        assert response.status_code == 401
