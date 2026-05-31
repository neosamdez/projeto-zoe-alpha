class TestInventoryCRUD:
    def test_inventory_dashboard(self, client, admin_headers):
        response = client.get("/api/v1/inventory/dashboard", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "low_stock_count" in data

    def test_list_low_stock(self, client, admin_headers):
        response = client.get("/api/v1/inventory/low-stock", headers=admin_headers)
        assert response.status_code == 200

    def test_list_movements(self, client, admin_headers):
        response = client.get("/api/v1/inventory/movements", headers=admin_headers)
        assert response.status_code == 200

    def test_create_movement_requires_product(self, client, admin_headers):
        response = client.post("/api/v1/inventory/movements", headers=admin_headers, json={
            "product_id": "00000000-0000-0000-0000-000000000000",
            "movement_type": "IN",
            "quantity": 5,
        })
        assert response.status_code == 404

    def test_inventory_unauthenticated(self, client):
        response = client.get("/api/v1/inventory/dashboard")
        assert response.status_code == 401
