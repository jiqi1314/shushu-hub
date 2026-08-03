"""API integration tests."""

from fastapi.testclient import TestClient

from app.main import create_app

app = create_app()
client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body


class TestSystems:
    def test_lists_systems(self) -> None:
        response = client.get("/api/systems")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body["systems"], list)
        assert any(s["system_id"] == "ichingshifa" for s in body["systems"])


class TestDivination:
    def test_random_divination(self) -> None:
        response = client.post(
            "/api/divination",
            json={"system": "ichingshifa", "method": "random"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["system_id"] == "ichingshifa"

    def test_datetime_divination(self) -> None:
        response = client.post(
            "/api/divination",
            json={
                "system": "ichingshifa",
                "method": "datetime",
                "datetime": "2026-08-04T14:30:00",
                "timezone": "Asia/Hong_Kong",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["ganzhi"]["year"]
        assert body["ganzhi"]["day"]

    def test_unsupported_system_returns_error(self) -> None:
        response = client.post(
            "/api/divination",
            json={"system": "fake_system", "method": "random"},
        )
        assert response.status_code == 422
        body = response.json()
        assert "error_code" in body["detail"]
        assert body["detail"]["error_code"] == "UNSUPPORTED_SYSTEM"

    def test_invalid_datetime_returns_error(self) -> None:
        response = client.post(
            "/api/divination",
            json={"system": "ichingshifa", "method": "datetime"},
        )
        assert response.status_code == 422
