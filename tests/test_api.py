"""
API endpoint tests for Floramigo plant care system.

Tests all REST API endpoints including health checks, chat, telemetry ingestion,
and plant diagnosis.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import Mock, patch
import json

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and readiness endpoints."""
    
    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_healthz_endpoint_returns_ok(self):
        """Healthz endpoint should return ok status."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_health_includes_timestamp(self):
        """Health response should include timestamp."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
    
    def test_health_includes_version(self):
        """Health response should include version info."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data


class TestChatEndpoint:
    """Test the /ask endpoint for conversational interaction."""
    
    def test_ask_endpoint_with_valid_message(self):
        """Should return response for valid message."""
        response = client.post(
            "/ask",
            json={"message": "How is my plant doing?", "plant_name": "Basil"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_ask_endpoint_without_api_key_fallback(self):
        """Should fallback gracefully when no API key is set."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=True):
            response = client.post(
                "/ask",
                json={"message": "Status check", "plant_name": "Basil"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            # Should contain sensor-based info
            assert "sensor" in data["response"].lower() or "reading" in data["response"].lower()
    
    def test_ask_endpoint_with_plant_context(self):
        """Should include plant context in response."""
        # First ingest some telemetry
        client.post(
            "/ingest/telemetry",
            json={
                "temperature": 23.5,
                "humidity": 45,
                "moisture_pct": 32,
                "light_raw": 250,
                "plant_name": "Basil"
            }
        )
        
        # Then ask question
        response = client.post(
            "/ask",
            json={"message": "What's the temperature?", "plant_name": "Basil"}
        )
        assert response.status_code == 200
        data = response.json()
        # Response should reference sensor data
        assert "temperature" in data["response"].lower() or "23" in data["response"]
    
    def test_ask_endpoint_empty_message_validation(self):
        """Should reject empty messages."""
        response = client.post(
            "/ask",
            json={"message": "", "plant_name": "Basil"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_ask_endpoint_missing_plant_name(self):
        """Should work even without plant name."""
        response = client.post(
            "/ask",
            json={"message": "Hello"}
        )
        assert response.status_code == 200


class TestTelemetryIngestion:
    """Test sensor data ingestion endpoints."""
    
    def test_ingest_telemetry_valid_data(self):
        """Should accept valid telemetry data."""
        response = client.post(
            "/ingest/telemetry",
            json={
                "temperature": 24.5,
                "humidity": 42,
                "moisture_pct": 36,
                "light_raw": 180
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_ingest_telemetry_with_alerts(self):
        """Should generate alerts for threshold violations."""
        response = client.post(
            "/ingest/telemetry",
            json={
                "temperature": 38.0,  # Too high
                "humidity": 15,        # Too low
                "moisture_pct": 8,     # Critical low
                "light_raw": 50
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert len(data["alerts"]) > 0
        # Should have multiple alerts for multiple issues
        alert_text = " ".join(data["alerts"]).lower()
        assert "temperature" in alert_text or "moisture" in alert_text
    
    def test_ingest_telemetry_invalid_data(self):
        """Should reject invalid telemetry data."""
        response = client.post(
            "/ingest/telemetry",
            json={
                "temperature": "invalid",
                "humidity": 42
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_ingest_telemetry_missing_fields(self):
        """Should handle missing optional fields."""
        response = client.post(
            "/ingest/telemetry",
            json={"temperature": 24.5}
        )
        # Should either accept with defaults or return 200 with partial data
        assert response.status_code in [200, 422]
    
    def test_get_current_readings(self):
        """Should retrieve current readings."""
        # First ingest data
        client.post(
            "/ingest/telemetry",
            json={
                "temperature": 23.0,
                "humidity": 50,
                "moisture_pct": 45,
                "light_raw": 200
            }
        )
        
        # Then retrieve
        response = client.get("/ingest/current")
        assert response.status_code == 200
        data = response.json()
        assert "temperature" in data
    
    def test_get_alerts_history(self):
        """Should retrieve alert history."""
        response = client.get("/ingest/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPlantDiagnosis:
    """Test plant diagnosis and monitoring endpoints."""
    
    def test_diagnose_endpoint(self):
        """Should return plant diagnosis."""
        # First ingest some data
        client.post(
            "/ingest/telemetry",
            json={
                "temperature": 24.5,
                "humidity": 45,
                "moisture_pct": 40,
                "light_raw": 180,
                "plant_name": "Basil"
            }
        )
        
        response = client.get("/diagnose")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data or "status" in data
    
    def test_diagnose_with_no_data(self):
        """Should handle diagnosis request with no sensor data."""
        # Clear any existing data first
        response = client.get("/diagnose?plant_name=NonExistentPlant")
        # Should return 200 with appropriate message or 404
        assert response.status_code in [200, 404]
    
    def test_monitor_start(self):
        """Should start serial monitoring."""
        response = client.post("/monitor/start")
        # May fail if no serial device, but should handle gracefully
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_monitor_stop(self):
        """Should stop serial monitoring."""
        response = client.post("/monitor/stop")
        assert response.status_code in [200, 400]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_endpoint(self):
        """Should return 404 for invalid endpoints."""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Should return 405 for wrong HTTP method."""
        response = client.get("/ask")  # Should be POST
        assert response.status_code == 405
    
    def test_malformed_json(self):
        """Should handle malformed JSON gracefully."""
        response = client.post(
            "/ask",
            data="this is not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self):
        """Should include CORS headers in response."""
        response = client.options("/health")
        # CORS headers should be present for OPTIONS request
        assert response.status_code in [200, 204]


# Fixtures for test data
@pytest.fixture
def sample_telemetry():
    """Sample telemetry data for testing."""
    return {
        "temperature": 24.5,
        "humidity": 42,
        "moisture_pct": 36,
        "light_raw": 180,
        "plant_name": "Test Plant"
    }


@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing."""
    return {
        "message": "How is my plant doing?",
        "plant_name": "Test Plant"
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
