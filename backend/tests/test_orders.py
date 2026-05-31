class TestOrdersCRUD:
    def test_create_order_from_lead(self, client, admin_headers):
        lead = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "OS Client", "email": "os@test.io", "phone": "111",
        }).json()
        response = client.post(f"/api/v1/orders/from-lead/{lead['id']}", headers=admin_headers, json={
            "device_info": "MacBook Pro M2",
            "technical_notes": "Tela quebrada",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["protocol"].startswith("ASI-")
        assert data["status"] == "OPEN"

    def test_list_orders(self, client, admin_headers):
        response = client.get("/api/v1/orders/", headers=admin_headers)
        assert response.status_code == 200

    def test_order_stats(self, client, admin_headers):
        response = client.get("/api/v1/orders/stats", headers=admin_headers)
        assert response.status_code == 200

    def test_order_analytics(self, client, admin_headers):
        response = client.get("/api/v1/orders/analytics?days=30", headers=admin_headers)
        assert response.status_code == 200

    def test_delete_order_admin_only(self, client, admin_headers):
        lead = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Del OS Client", "email": "delos@test.io", "phone": "222",
        }).json()
        order = client.post(f"/api/v1/orders/from-lead/{lead['id']}", headers=admin_headers, json={
            "device_info": "iPhone 15",
        }).json()
        response = client.delete(f"/api/v1/orders/{order['id']}", headers=admin_headers)
        assert response.status_code == 200

    def test_delete_order_technician_forbidden(self, client, tech_headers):
        response = client.delete("/api/v1/orders/00000000-0000-0000-0000-000000000000", headers=tech_headers)
        assert response.status_code in (403, 404)
