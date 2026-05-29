class TestLeadsCRUD:
    def test_create_lead(self, client, admin_headers):
        response = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Cliente Teste",
            "email": "cliente@test.io",
            "phone": "11999999999",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cliente Teste"
        assert data["email"] == "cliente@test.io"

    def test_list_leads(self, client, admin_headers):
        client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead A", "email": "a@test.io", "phone": "111",
        })
        response = client.get("/api/v1/leads/", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_lead_by_id(self, client, admin_headers):
        create = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead B", "email": "b@test.io", "phone": "222",
        })
        lead_id = create.json()["id"]
        response = client.get(f"/api/v1/leads/{lead_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["id"] == lead_id

    def test_update_lead(self, client, admin_headers):
        create = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead C", "email": "c@test.io", "phone": "333",
        })
        lead_id = create.json()["id"]
        response = client.patch(f"/api/v1/leads/{lead_id}", headers=admin_headers, json={
            "name": "Lead C Atualizado",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Lead C Atualizado"

    def test_delete_lead(self, client, admin_headers):
        create = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead D", "email": "d@test.io", "phone": "444",
        })
        lead_id = create.json()["id"]
        response = client.delete(f"/api/v1/leads/{lead_id}", headers=admin_headers)
        assert response.status_code == 204

    def test_duplicate_email_per_tenant(self, client, admin_headers):
        client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead E1", "email": "dup@test.io", "phone": "555",
        })
        response = client.post("/api/v1/leads/", headers=admin_headers, json={
            "name": "Lead E2", "email": "dup@test.io", "phone": "666",
        })
        assert response.status_code == 409
