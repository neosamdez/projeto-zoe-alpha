class TestDeliveriesCRUD:
    def test_create_delivery(self, client, admin_headers):
        response = client.post("/api/v1/deliveries/", headers=admin_headers, json={
            "delivery_number": "DEL-2026-001",
            "pending_qty": 10,
            "reference_date": "2026-05-15",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["delivery_number"] == "DEL-2026-001"

    def test_list_deliveries(self, client, admin_headers):
        response = client.get("/api/v1/deliveries/", headers=admin_headers)
        assert response.status_code == 200

    def test_list_overdue(self, client, admin_headers):
        response = client.get("/api/v1/deliveries/overdue", headers=admin_headers)
        assert response.status_code == 200

    def test_mark_overdue_admin_only(self, client, tech_headers):
        response = client.post("/api/v1/deliveries/mark-overdue", headers=tech_headers)
        assert response.status_code == 403

    def test_deliveries_unauthenticated(self, client):
        response = client.get("/api/v1/deliveries/")
        assert response.status_code == 401
