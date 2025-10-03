"""Integration tests for EVY system."""
import pytest
import asyncio
import httpx
from unittest.mock import patch, AsyncMock
import json

from backend.shared.models import SMSMessage, MessagePriority, LLMRequest


class TestSMSGatewayIntegration:
    """Integration tests for SMS Gateway."""
    
    @pytest.mark.asyncio
    async def test_sms_gateway_health_check(self, sms_client):
        """Test SMS gateway health check endpoint."""
        response = sms_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "sms-gateway"
        assert data["status"] == "healthy"
        assert "gsm_status" in data["details"]
        assert "queue_stats" in data["details"]
    
    @pytest.mark.asyncio
    async def test_send_sms_endpoint(self, sms_client, sample_sms_message):
        """Test SMS sending endpoint."""
        with patch('backend.services.sms_gateway.main.sms_gateway.send_sms', AsyncMock(return_value=True)):
            response = sms_client.post("/sms/send", json=sample_sms_message.model_dump())
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "sent"
            assert "message_id" in data
    
    @pytest.mark.asyncio
    async def test_receive_sms_endpoint(self, sms_client, sample_sms_message):
        """Test SMS receiving endpoint."""
        with patch('backend.services.sms_gateway.main.sms_gateway.receive_sms', AsyncMock()):
            response = sms_client.post("/sms/receive", json=sample_sms_message.model_dump())
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"
    
    @pytest.mark.asyncio
    async def test_parse_message_endpoint(self, sms_client):
        """Test message parsing endpoint."""
        response = sms_client.post("/parse-message", json={
            "text": "What's the weather like today?",
            "sender": "+1234567890"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "parsed" in data
        assert "validation" in data
        assert data["parsed"]["intent"] == "question"
        assert data["parsed"]["category"] == "weather"
        assert data["validation"]["valid"] is True
    
    @pytest.mark.asyncio
    async def test_gsm_status_endpoint(self, sms_client):
        """Test GSM status endpoint."""
        response = sms_client.get("/gsm/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        assert "driver" in data
    
    @pytest.mark.asyncio
    async def test_queue_stats_endpoint(self, sms_client):
        """Test queue statistics endpoint."""
        response = sms_client.get("/queue/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "processing" in data
        assert "sent" in data
        assert "failed" in data


class TestLLMInferenceIntegration:
    """Integration tests for LLM Inference service."""
    
    @pytest.mark.asyncio
    async def test_llm_health_check(self, llm_client):
        """Test LLM inference health check endpoint."""
        response = llm_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "llm-inference"
        assert data["status"] == "healthy"
        assert "provider" in data["details"]
        assert "tiny_models" in data["details"]
    
    @pytest.mark.asyncio
    async def test_inference_endpoint(self, llm_client):
        """Test LLM inference endpoint."""
        with patch('backend.services.llm_inference.main.llm_engine.generate_response', AsyncMock(return_value={
            "response": "This is a test response.",
            "model_used": "test-model",
            "tokens_used": 10,
            "processing_time": 1.5
        })):
            request_data = {
                "prompt": "What is 2+2?",
                "max_length": 160,
                "temperature": 0.7
            }
            
            response = llm_client.post("/inference", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "This is a test response."
            assert data["model_used"] == "test-model"
            assert data["tokens_used"] == 10
    
    @pytest.mark.asyncio
    async def test_models_endpoint(self, llm_client):
        """Test models listing endpoint."""
        response = llm_client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "tiny_models" in data
        assert "current_model" in data
    
    @pytest.mark.asyncio
    async def test_tiny_models_status_endpoint(self, llm_client):
        """Test tiny models status endpoint."""
        response = llm_client.get("/tiny-models/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_models" in data
        assert "loaded_models" in data
        assert "available_models" in data
    
    @pytest.mark.asyncio
    async def test_load_tiny_model_endpoint(self, llm_client):
        """Test load tiny model endpoint."""
        with patch('backend.services.llm_inference.main.llm_engine.tiny_model_manager.load_model', AsyncMock(return_value=True)):
            response = llm_client.post("/tiny-models/load?model_name=tinyllama&use_quantization=true")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "loaded"
            assert data["model"] == "tinyllama"
    
    @pytest.mark.asyncio
    async def test_switch_provider_endpoint(self, llm_client):
        """Test switch provider endpoint."""
        with patch('backend.services.llm_inference.main.llm_engine.tiny_model_manager.load_model', AsyncMock(return_value=True)):
            response = llm_client.post("/switch-provider", json={"provider": "tiny"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "switched"
            assert data["new_provider"] == "tiny"


class TestEndToEndFlow:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_sms_to_llm_to_sms_flow(self, http_client):
        """Test complete SMS → LLM → SMS flow."""
        # This test simulates the complete flow
        
        # 1. Receive SMS
        sms_data = {
            "sender": "+1234567890",
            "receiver": "+0987654321",
            "content": "What's the weather like?",
            "priority": "normal"
        }
        
        # Mock the services
        with patch('backend.services.sms_gateway.main.sms_gateway.receive_sms', AsyncMock()) as mock_receive:
            with patch('backend.services.sms_gateway.main.sms_gateway.send_sms', AsyncMock(return_value=True)) as mock_send:
                with patch('backend.services.llm_inference.main.llm_engine.generate_response', AsyncMock(return_value={
                    "response": "The weather is sunny with 75°F.",
                    "model_used": "tinyllama",
                    "tokens_used": 15,
                    "processing_time": 1.2
                })) as mock_llm:
                    
                    # Send SMS to gateway
                    sms_response = await http_client.post(
                        "http://localhost:8001/sms/receive",
                        json=sms_data
                    )
                    
                    assert sms_response.status_code == 200
                    
                    # Verify SMS was processed
                    mock_receive.assert_called_once()
                    
                    # Simulate LLM processing
                    llm_request = {
                        "prompt": "What's the weather like?",
                        "max_length": 160,
                        "temperature": 0.7
                    }
                    
                    llm_response = await http_client.post(
                        "http://localhost:8003/inference",
                        json=llm_request
                    )
                    
                    assert llm_response.status_code == 200
                    llm_data = llm_response.json()
                    assert "The weather is sunny" in llm_data["response"]
                    
                    # Simulate sending response SMS
                    response_sms = SMSMessage(
                        sender="+0987654321",
                        receiver="+1234567890",
                        content=llm_data["response"],
                        priority=MessagePriority.NORMAL
                    )
                    
                    send_response = await http_client.post(
                        "http://localhost:8001/sms/send",
                        json=response_sms.model_dump()
                    )
                    
                    assert send_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_emergency_message_priority_flow(self, http_client):
        """Test emergency message priority handling."""
        emergency_sms = {
            "sender": "+1234567890",
            "receiver": "+0987654321",
            "content": "EMERGENCY! Fire in building!",
            "priority": "emergency"
        }
        
        with patch('backend.services.sms_gateway.main.sms_gateway.receive_sms', AsyncMock()) as mock_receive:
            # Send emergency SMS
            response = await http_client.post(
                "http://localhost:8001/sms/receive",
                json=emergency_sms
            )
            
            assert response.status_code == 200
            
            # Verify emergency message was processed
            mock_receive.assert_called_once()
            received_call = mock_receive.call_args[0][0]
            assert received_call.priority == MessagePriority.EMERGENCY
    
    @pytest.mark.asyncio
    async def test_message_parsing_integration(self, http_client):
        """Test message parsing integration."""
        test_messages = [
            {
                "text": "Hello, how are you?",
                "sender": "+1234567890",
                "expected_intent": "greeting"
            },
            {
                "text": "What time does the bus arrive?",
                "sender": "+1234567890",
                "expected_intent": "question"
            },
            {
                "text": "HELP! Emergency situation!",
                "sender": "+1234567890",
                "expected_intent": "emergency"
            }
        ]
        
        for test_case in test_messages:
            response = await http_client.post(
                "http://localhost:8001/parse-message",
                json={
                    "text": test_case["text"],
                    "sender": test_case["sender"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["parsed"]["intent"] == test_case["expected_intent"]
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, http_client):
        """Test error handling across services."""
        # Test invalid SMS data
        invalid_sms = {
            "sender": "invalid_phone",
            "content": "x" * 300  # Too long
        }
        
        response = await http_client.post(
            "http://localhost:8001/sms/send",
            json=invalid_sms
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]  # Either processed or validation error
        
        # Test invalid LLM request
        invalid_llm = {
            "prompt": "",  # Empty prompt
            "max_length": -1  # Invalid length
        }
        
        response = await http_client.post(
            "http://localhost:8003/inference",
            json=invalid_llm
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]


class TestPerformanceIntegration:
    """Performance integration tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_sms_processing(self, http_client):
        """Test concurrent SMS processing."""
        import time
        
        # Create multiple SMS messages
        messages = []
        for i in range(10):
            messages.append({
                "sender": f"+123456789{i}",
                "receiver": "+0987654321",
                "content": f"Test message {i}",
                "priority": "normal"
            })
        
        start_time = time.time()
        
        # Send all messages concurrently
        tasks = []
        for message in messages:
            with patch('backend.services.sms_gateway.main.sms_gateway.receive_sms', AsyncMock()):
                task = http_client.post(
                    "http://localhost:8001/sms/receive",
                    json=message
                )
                tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Should process reasonably quickly (less than 10 seconds for 10 messages)
        assert total_time < 10.0
    
    @pytest.mark.asyncio
    async def test_llm_response_time(self, http_client):
        """Test LLM response time."""
        import time
        
        request = {
            "prompt": "What is artificial intelligence?",
            "max_length": 160,
            "temperature": 0.7
        }
        
        start_time = time.time()
        
        with patch('backend.services.llm_inference.main.llm_engine.generate_response', AsyncMock(return_value={
            "response": "AI is the simulation of human intelligence in machines.",
            "model_used": "tinyllama",
            "tokens_used": 20,
            "processing_time": 1.0
        })):
            response = await http_client.post(
                "http://localhost:8003/inference",
                json=request
            )
        
        total_time = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within reasonable time (less than 5 seconds)
        assert total_time < 5.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, http_client):
        """Test memory usage stability under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Send many requests
        for i in range(50):
            with patch('backend.services.llm_inference.main.llm_engine.generate_response', AsyncMock(return_value={
                "response": f"Response {i}",
                "model_used": "tinyllama",
                "tokens_used": 10,
                "processing_time": 0.5
            })):
                response = await http_client.post(
                    "http://localhost:8003/inference",
                    json={
                        "prompt": f"Test prompt {i}",
                        "max_length": 100
                    }
                )
                assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 50 requests)
        assert memory_increase < 100
