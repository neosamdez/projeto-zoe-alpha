class TestUsersAdmin:
    def test_list_users(self, client, admin_headers):
        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200

    def test_update_user(self, client, admin_headers, seed_technician):
        response = client.patch(f"/api/v1/users/{seed_technician.id}", headers=admin_headers, json={
            "full_name": "Tech Updated",
        })
        assert response.status_code == 200
        assert response.json()["full_name"] == "Tech Updated"

    def test_delete_user(self, client, admin_headers, seed_technician):
        response = client.delete(f"/api/v1/users/{seed_technician.id}", headers=admin_headers)
        assert response.status_code == 204

    def test_technician_cannot_list_users(self, client, tech_headers):
        response = client.get("/api/v1/users/", headers=tech_headers)
        assert response.status_code == 403
