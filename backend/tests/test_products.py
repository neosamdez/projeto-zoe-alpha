class TestProductsCRUD:
    def test_create_product(self, client, admin_headers):
        response = client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "SSD 512GB",
            "sku": "SSD-512",
            "cost_price": 150.00,
            "selling_price": 250.00,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SSD 512GB"
        assert data["sku"] == "SSD-512"

    def test_list_products(self, client, admin_headers):
        client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "RAM 8GB", "sku": "RAM-8", "cost_price": 80, "selling_price": 150,
        })
        response = client.get("/api/v1/products/", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_product_by_id(self, client, admin_headers):
        create = client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "Mouse", "sku": "MOU-1", "cost_price": 30, "selling_price": 60,
        })
        pid = create.json()["id"]
        response = client.get(f"/api/v1/products/{pid}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["sku"] == "MOU-1"

    def test_update_product(self, client, admin_headers):
        create = client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "Teclado", "sku": "TEC-1", "cost_price": 50, "selling_price": 100,
        })
        pid = create.json()["id"]
        response = client.patch(f"/api/v1/products/{pid}", headers=admin_headers, json={
            "selling_price": 120,
        })
        assert response.status_code == 200
        assert float(response.json()["selling_price"]) == 120.0

    def test_delete_product(self, client, admin_headers):
        create = client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "Webcam", "sku": "WBC-1", "cost_price": 40, "selling_price": 80,
        })
        pid = create.json()["id"]
        response = client.delete(f"/api/v1/products/{pid}", headers=admin_headers)
        assert response.status_code == 200

    def test_low_stock_endpoint(self, client, admin_headers):
        client.post("/api/v1/products/", headers=admin_headers, json={
            "name": "Bateria", "sku": "BAT-1", "cost_price": 20, "selling_price": 50,
            "current_stock": 1, "min_stock": 5,
        })
        response = client.get("/api/v1/products/low-stock", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_technician_cannot_create_product(self, client, tech_headers):
        response = client.post("/api/v1/products/", headers=tech_headers, json={
            "name": "Hack", "sku": "HCK-1", "cost_price": 1, "selling_price": 2,
        })
        assert response.status_code == 403
