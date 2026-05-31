class TestRmaCRUD:
    def test_create_rma(self, client, admin_headers):
        lead = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "RMA Client",
            "email": "rma@test.io",
            "phone": "111",
        }).json()
        order = client.post(f"/api/v1/orders/from-lead/{lead['id']}", headers=admin_headers, json={
            "device_info": "Samsung TV 55\"",
        }).json()
        response = client.post("/api/v1/rma/", headers=admin_headers, json={
            "order_id": order["id"],
            "return_code": "805",
            "delivery_code": "DEL-001",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["protocol"].startswith("RMA-")
        assert data["status"] == "PENDING"
        assert data["deadline_days"] == 30

    def test_list_rmas(self, client, admin_headers):
        response = client.get("/api/v1/rma/", headers=admin_headers)
        assert response.status_code == 200

    def test_list_defect_codes(self, client, admin_headers):
        response = client.get("/api/v1/rma/defect-codes", headers=admin_headers)
        assert response.status_code == 200

    def test_rma_unauthenticated(self, client):
        response = client.get("/api/v1/rma/")
        assert response.status_code == 401
