class TestKpiCRUD:
    def test_create_kpi_metric(self, client, admin_headers):
        response = client.post("/api/v1/kpi/", headers=admin_headers, json={
            "month": 5,
            "year": 2026,
            "nps_score": 85.5,
            "first_visit_rate": 90.0,
            "ltp_mx_rate": 70.0,
            "crrr_mx_rate": 65.0,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["total_points"] > 0
        assert data["bonus_tier"] is not None

    def test_list_kpi_metrics(self, client, admin_headers):
        response = client.get("/api/v1/kpi/", headers=admin_headers)
        assert response.status_code == 200

    def test_kpi_dashboard(self, client, admin_headers):
        response = client.get("/api/v1/kpi/dashboard?month=5&year=2026", headers=admin_headers)
        assert response.status_code == 200

    def test_kpi_bonus_summary(self, client, admin_headers):
        response = client.get("/api/v1/kpi/bonus-summary?month=5&year=2026", headers=admin_headers)
        assert response.status_code == 200

    def test_create_kpi_requires_admin(self, client, tech_headers):
        response = client.post("/api/v1/kpi/", headers=tech_headers, json={
            "month": 5,
            "year": 2026,
            "nps_score": 50.0,
        })
        assert response.status_code == 403

    def test_kpi_unauthenticated(self, client):
        response = client.get("/api/v1/kpi/")
        assert response.status_code == 401
