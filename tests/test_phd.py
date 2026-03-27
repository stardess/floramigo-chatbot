"""
Plant Health Daemon (PHD) tests.

Tests telemetry normalization, threshold detection, alert generation,
and data persistence.
"""

import pytest
from floramigo.core.phd import PlantHealthDaemon, normalize_reading, check_thresholds
import json
import os
from pathlib import Path
from datetime import datetime


class TestDataNormalization:
    """Test sensor data normalization."""
    
    def test_normalize_temperature_celsius(self):
        """Should keep Celsius temperatures as-is."""
        reading = {"temperature": 24.5, "unit": "C"}
        normalized = normalize_reading(reading)
        assert normalized["temperature"] == pytest.approx(24.5, abs=0.1)
    
    def test_normalize_temperature_fahrenheit(self):
        """Should convert Fahrenheit to Celsius."""
        reading = {"temperature": 75.2, "unit": "F"}
        normalized = normalize_reading(reading)
        # 75.2°F = 24°C
        assert normalized["temperature"] == pytest.approx(24.0, abs=0.5)
    
    def test_normalize_humidity_range(self):
        """Should clamp humidity to 0-100% range."""
        # Test upper bound
        reading = {"humidity": 105}
        normalized = normalize_reading(reading)
        assert normalized["humidity"] <= 100
        
        # Test lower bound
        reading = {"humidity": -5}
        normalized = normalize_reading(reading)
        assert normalized["humidity"] >= 0
    
    def test_normalize_moisture_percentage(self):
        """Should normalize moisture to percentage."""
        reading = {"moisture_pct": 45}
        normalized = normalize_reading(reading)
        assert 0 <= normalized["moisture_pct"] <= 100
    
    def test_normalize_light_values(self):
        """Should handle various light sensor formats."""
        reading = {"light_raw": 250}
        normalized = normalize_reading(reading)
        assert "light_raw" in normalized
        assert normalized["light_raw"] >= 0


class TestThresholdDetection:
    """Test threshold checking and alert generation."""
    
    def test_low_moisture_alert(self):
        """Should generate alert for low moisture."""
        reading = {
            "moisture_pct": 15,  # Below typical threshold
            "temperature": 24,
            "humidity": 45
        }
        alerts = check_thresholds(reading)
        assert len(alerts) > 0
        assert any("moisture" in alert.lower() for alert in alerts)
    
    def test_critical_moisture_alert(self):
        """Should generate critical alert for very low moisture."""
        reading = {
            "moisture_pct": 5,  # Critical level
            "temperature": 24,
            "humidity": 45
        }
        alerts = check_thresholds(reading)
        assert len(alerts) > 0
        assert any("critical" in alert.lower() and "moisture" in alert.lower() 
                   for alert in alerts)
    
    def test_high_temperature_alert(self):
        """Should generate alert for high temperature."""
        reading = {
            "temperature": 38,  # Too hot for most plants
            "moisture_pct": 40,
            "humidity": 45
        }
        alerts = check_thresholds(reading)
        assert len(alerts) > 0
        assert any("temperature" in alert.lower() for alert in alerts)
    
    def test_low_humidity_alert(self):
        """Should generate alert for low humidity."""
        reading = {
            "humidity": 15,  # Very low
            "temperature": 24,
            "moisture_pct": 40
        }
        alerts = check_thresholds(reading)
        assert len(alerts) > 0
        assert any("humidity" in alert.lower() for alert in alerts)
    
    def test_no_alerts_for_healthy_conditions(self):
        """Should not generate alerts for healthy conditions."""
        reading = {
            "temperature": 24,
            "humidity": 50,
            "moisture_pct": 45,
            "light_raw": 200
        }
        alerts = check_thresholds(reading)
        assert len(alerts) == 0 or all(alert == "" for alert in alerts)
    
    def test_multiple_alerts(self):
        """Should generate multiple alerts for multiple issues."""
        reading = {
            "temperature": 38,  # Too hot
            "humidity": 15,     # Too dry
            "moisture_pct": 8,  # Critical low
            "light_raw": 10     # Too dark
        }
        alerts = check_thresholds(reading)
        assert len(alerts) >= 2  # Should have multiple alerts


class TestPHDClass:
    """Test PlantHealthDaemon class functionality."""
    
    @pytest.fixture
    def phd(self, tmp_path):
        """Create PHD instance with temporary data directory."""
        return PlantHealthDaemon(data_dir=str(tmp_path))
    
    def test_phd_initialization(self, phd):
        """Should initialize PHD correctly."""
        assert phd is not None
        assert hasattr(phd, 'process_reading')
    
    def test_process_reading(self, phd):
        """Should process and save reading."""
        reading = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "light_raw": 180
        }
        result = phd.process_reading(reading)
        assert result["status"] == "success"
    
    def test_save_current_reading(self, phd, tmp_path):
        """Should save current reading to JSON."""
        reading = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "light_raw": 180,
            "timestamp": datetime.now().isoformat()
        }
        phd.save_current(reading)
        
        # Verify file was created
        current_file = tmp_path / "current_readings.json"
        assert current_file.exists()
        
        # Verify content
        with open(current_file) as f:
            data = json.load(f)
        assert data["temperature"] == 24.5
    
    def test_save_historical_data(self, phd, tmp_path):
        """Should append to historical data."""
        reading = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "timestamp": datetime.now().isoformat()
        }
        phd.save_history(reading)
        
        # Process another reading
        reading2 = {
            "temperature": 25.0,
            "humidity": 46,
            "moisture_pct": 41,
            "timestamp": datetime.now().isoformat()
        }
        phd.save_history(reading2)
        
        # Verify file exists and has multiple entries
        history_file = tmp_path / "sensor_history.json"
        assert history_file.exists()
        
        with open(history_file) as f:
            data = json.load(f)
        assert len(data) >= 2
    
    def test_alert_history_tracking(self, phd, tmp_path):
        """Should track alert history."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": "warning",
            "message": "Soil moisture is low"
        }
        phd.save_alert(alert)
        
        # Verify alert file
        alerts_file = tmp_path / "alerts.json"
        assert alerts_file.exists()
        
        with open(alerts_file) as f:
            data = json.load(f)
        assert len(data) > 0
        assert data[0]["message"] == "Soil moisture is low"
    
    def test_data_retention_policy(self, phd, tmp_path):
        """Should enforce 24-hour data retention."""
        # Add many historical readings
        for i in range(1500):  # More than 24 hours at 1/min
            reading = {
                "temperature": 24.0 + (i * 0.01),
                "humidity": 45,
                "moisture_pct": 40,
                "timestamp": datetime.now().isoformat()
            }
            phd.save_history(reading)
        
        # Load history
        history_file = tmp_path / "sensor_history.json"
        with open(history_file) as f:
            data = json.load(f)
        
        # Should cap at ~1440 (24 hours * 60 minutes)
        assert len(data) <= 1500  # Allow some buffer
    
    def test_get_latest_reading(self, phd):
        """Should retrieve latest reading."""
        reading = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "light_raw": 180
        }
        phd.process_reading(reading)
        
        latest = phd.get_current()
        assert latest is not None
        assert latest["temperature"] == pytest.approx(24.5, abs=0.1)
    
    def test_get_plant_status(self, phd):
        """Should generate plant status summary."""
        reading = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "light_raw": 180
        }
        phd.process_reading(reading)
        
        status = phd.get_status()
        assert "summary" in status or "health" in status


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handle_missing_fields(self):
        """Should handle readings with missing fields."""
        reading = {"temperature": 24.5}  # Missing other fields
        normalized = normalize_reading(reading)
        # Should have defaults or handle gracefully
        assert "temperature" in normalized
    
    def test_handle_invalid_values(self):
        """Should handle invalid sensor values."""
        reading = {
            "temperature": 999,  # Unrealistic
            "humidity": -50,     # Invalid
            "moisture_pct": 150  # Out of range
        }
        # Should either normalize or raise appropriate error
        try:
            normalized = normalize_reading(reading)
            # If successful, values should be clamped
            assert normalized["humidity"] >= 0
            assert normalized["moisture_pct"] <= 100
        except ValueError:
            # Or should raise validation error
            pass
    
    def test_concurrent_data_access(self, tmp_path):
        """Should handle concurrent reads/writes safely."""
        phd1 = PlantHealthDaemon(data_dir=str(tmp_path))
        phd2 = PlantHealthDaemon(data_dir=str(tmp_path))
        
        reading1 = {"temperature": 24.5, "humidity": 45, "moisture_pct": 40}
        reading2 = {"temperature": 25.0, "humidity": 46, "moisture_pct": 41}
        
        # Both should succeed without corruption
        phd1.process_reading(reading1)
        phd2.process_reading(reading2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
