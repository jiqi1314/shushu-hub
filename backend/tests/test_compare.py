"""Tests for the /api/compare endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app

app = create_app()
client = TestClient(app)


class TestCompareAll:
    def test_compare_all_systems_default(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "datetime": "2026-08-04T14:30:00",
                "timezone": "Asia/Hong_Kong",
                "question": "事業轉職時機",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["results"]) == 4
        systems = sorted(r["system_id"] for r in body["results"])
        assert systems == ["ichingshifa", "liuren", "qimen", "taiyi"]
        assert body["question"] == "事業轉職時機"
        assert "consensus" in body["cross_analysis"]
        assert len(body["cross_analysis"]["entities_by_system"]) == 4

    def test_compare_subset_explicit(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "datetime": "2026-08-04T14:30:00",
                "systems": ["ichingshifa", "qimen"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["results"]) == 2
        ids = sorted(r["system_id"] for r in body["results"])
        assert ids == ["ichingshifa", "qimen"]

    def test_compare_with_per_system_knobs(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "datetime": "2026-08-04T14:30:00",
                "systems": ["qimen", "taiyi"],
                "per_system": {
                    "qimen": {"variant": "zhirun"},
                    "taiyi": {"scope": "nianji", "formula": "jinjing"},
                },
            },
        )
        assert response.status_code == 200
        body = response.json()
        for r in body["results"]:
            if r["system_id"] == "qimen":
                assert r["details"]["variant"] == "zhirun"
            if r["system_id"] == "taiyi":
                assert r["details"]["scope"] == "nianji"
                assert r["details"]["formula"] == "jinjing"

    def test_compare_collects_failures_gracefully(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "datetime": "2026-08-04T14:30:00",
                "systems": ["ichingshifa", "fake_system"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["results"]) == 1
        assert len(body["failures"]) == 1
        assert body["failures"][0]["system"] == "fake_system"

    def test_compare_rejects_invalid_method_for_system(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "datetime": "2026-08-04T14:30:00",
                "systems": ["liuren"],
                "method": "random",
            },
        )
        assert response.status_code == 422

    def test_compare_method_random_only_ichingshifa(self) -> None:
        response = client.post(
            "/api/compare",
            json={
                "method": "random",
                "systems": ["ichingshifa"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["results"]) == 1
        assert body["results"][0]["system_id"] == "ichingshifa"
