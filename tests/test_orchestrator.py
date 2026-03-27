"""
Orchestrator tests for context building and LLM integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from floramigo.core.orchestrator import Orchestrator, build_context
from floramigo.core.llm_client import LLMClient


class TestContextBuilding:
    """Test system prompt and context building."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return Orchestrator()
    
    def test_build_system_prompt_with_sensor_context(self, orchestrator):
        """Should include sensor data in context."""
        sensor_data = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "light_raw": 180
        }
        context = orchestrator.build_context(sensor_data=sensor_data)
        
        assert "temperature" in context.lower()
        assert "24.5" in context or "24" in context
        assert "moisture" in context.lower()
    
    def test_build_system_prompt_without_sensors(self, orchestrator):
        """Should build context even without sensor data."""
        context = orchestrator.build_context()
        
        assert len(context) > 0
        assert "floramigo" in context.lower() or "plant" in context.lower()
    
    def test_add_plant_care_snippets(self, orchestrator):
        """Should include plant care tips in context."""
        context = orchestrator.build_context(plant_type="basil")
        
        # Should contain care information
        assert len(context) > 100  # Should have substantial content
    
    def test_context_includes_recent_alerts(self, orchestrator):
        """Should include recent alerts in context."""
        alerts = ["Soil moisture is low", "Temperature is high"]
        context = orchestrator.build_context(alerts=alerts)
        
        assert "low" in context.lower() or "alert" in context.lower()
    
    def test_context_token_limit(self, orchestrator):
        """Should respect token limits for context."""
        # Generate large sensor data
        large_data = {
            "temperature": 24.5,
            "humidity": 45,
            "moisture_pct": 40,
            "history": ["Reading " + str(i) for i in range(1000)]
        }
        context = orchestrator.build_context(sensor_data=large_data)
        
        # Should be reasonable size (rough token estimate: ~4 chars per token)
        assert len(context) < 16000  # ~4000 tokens


class TestLLMIntegration:
    """Test LLM orchestration."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mocked LLM."""
        orch = Orchestrator()
        orch.llm_client = Mock(spec=LLMClient)
        return orch
    
    def test_orchestrate_with_llm_success(self, orchestrator):
        """Should process query with LLM successfully."""
        orchestrator.llm_client.chat.return_value = {
            "response": "Your plant is doing well! The moisture level is good.",
            "model": "gpt-4"
        }
        
        result = orchestrator.process_query(
            message="How is my plant?",
            sensor_data={"moisture_pct": 45}
        )
        
        assert result["response"]
        assert "plant" in result["response"].lower()
        orchestrator.llm_client.chat.assert_called_once()
    
    def test_orchestrate_fallback_no_api_key(self, orchestrator):
        """Should fallback when no API key available."""
        orchestrator.llm_client = None  # Simulate no LLM client
        
        result = orchestrator.process_query(
            message="Status check",
            sensor_data={"temperature": 24, "moisture_pct": 40}
        )
        
        assert result["response"]
        assert "sensor" in result["response"].lower() or "reading" in result["response"].lower()
    
    def test_orchestrate_error_handling(self, orchestrator):
        """Should handle LLM errors gracefully."""
        orchestrator.llm_client.chat.side_effect = Exception("API Error")
        
        result = orchestrator.process_query(
            message="How is my plant?",
            sensor_data={"moisture_pct": 45}
        )
        
        # Should fallback to sensor-based response
        assert result["response"]
        assert result.get("error") or result.get("fallback")
    
    def test_streaming_response_handling(self, orchestrator):
        """Should handle streaming LLM responses."""
        # Mock streaming response
        def mock_stream():
            yield {"delta": "Your"}
            yield {"delta": " plant"}
            yield {"delta": " looks"}
            yield {"delta": " great!"}
        
        orchestrator.llm_client.stream = Mock(return_value=mock_stream())
        
        result = orchestrator.process_query_stream(
            message="How is my plant?",
            sensor_data={"moisture_pct": 45}
        )
        
        # Should combine chunks
        full_response = "".join([chunk["delta"] for chunk in result])
        assert "plant" in full_response.lower()


class TestPlantSpecificLogic:
    """Test plant-specific care recommendations."""
    
    @pytest.fixture
    def orchestrator(self):
        return Orchestrator()
    
    def test_basil_specific_advice(self, orchestrator):
        """Should provide basil-specific care tips."""
        context = orchestrator.build_context(plant_type="basil")
        assert "basil" in context.lower()
    
    def test_succulent_specific_advice(self, orchestrator):
        """Should provide succulent-specific care tips."""
        context = orchestrator.build_context(plant_type="succulent")
        # Succulents need less water
        assert "succulent" in context.lower() or "less water" in context.lower()
    
    def test_generic_plant_advice(self, orchestrator):
        """Should provide generic advice for unknown plants."""
        context = orchestrator.build_context(plant_type="unknown_plant")
        assert len(context) > 0


class TestMessageProcessing:
    """Test message parsing and intent detection."""
    
    @pytest.fixture
    def orchestrator(self):
        return Orchestrator()
    
    def test_status_query_detection(self, orchestrator):
        """Should detect status queries."""
        messages = [
            "How is my plant?",
            "What's the status?",
            "Is my plant healthy?"
        ]
        
        for msg in messages:
            result = orchestrator.detect_intent(msg)
            assert result == "status_query" or result in ["query", "question"]
    
    def test_watering_question_detection(self, orchestrator):
        """Should detect watering questions."""
        messages = [
            "Should I water my plant?",
            "Does it need water?",
            "When should I water?"
        ]
        
        for msg in messages:
            result = orchestrator.detect_intent(msg)
            assert "water" in result.lower() or result in ["query", "question"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
