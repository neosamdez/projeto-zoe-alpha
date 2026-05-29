class TestTechniciansCRUD:
    def test_create_technician(self, client, admin_headers):
        response = client.post("/api/v1/technicians/", headers=admin_headers, json={
            "name": "Mestre Goku",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Mestre Goku"

    def test_list_technicians(self, client, admin_headers):
        client.post("/api/v1/technicians/", headers=admin_headers, json={
            "name": "Mestre Vegeta",
        })
        response = client.get("/api/v1/technicians/", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_update_technician(self, client, admin_headers):
        create = client.post("/api/v1/technicians/", headers=admin_headers, json={
            "name": "Mestre Piccolo",
        })
        tid = create.json()["id"]
        response = client.patch(f"/api/v1/technicians/{tid}", headers=admin_headers, json={
            "specialization": "Solda BGA",
        })
        assert response.status_code == 200
        assert response.json()["specialization"] == "Solda BGA"

    def test_delete_technician(self, client, admin_headers):
        create = client.post("/api/v1/technicians/", headers=admin_headers, json={
            "name": "Mestre Kuririn",
        })
        tid = create.json()["id"]
        response = client.delete(f"/api/v1/technicians/{tid}", headers=admin_headers)
        assert response.status_code == 204

    def test_technician_cannot_create(self, client, tech_headers):
        response = client.post("/api/v1/technicians/", headers=tech_headers, json={
            "name": "Hacker",
        })
        assert response.status_code == 403
