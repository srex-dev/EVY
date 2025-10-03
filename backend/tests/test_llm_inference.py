"""Unit tests for LLM Inference service."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import time

from backend.services.llm_inference.main import LLMInferenceEngine
from backend.services.llm_inference.tiny_model_manager import TinyModelManager
from backend.shared.models import LLMRequest, LLMResponse


class TestLLMInferenceEngine:
    """Test LLM Inference Engine functionality."""
    
    @pytest.fixture
    def llm_engine(self):
        """Create LLM engine instance for testing."""
        return LLMInferenceEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization_openai(self, llm_engine):
        """Test engine initialization with OpenAI."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('backend.services.llm_inference.main.AsyncOpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                engine = LLMInferenceEngine()
                result = await engine.initialize()
                
                assert result is True
                assert engine.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_engine_initialization_tiny_fallback(self, llm_engine):
        """Test engine initialization with tiny model fallback."""
        # No OpenAI key
        with patch.dict('os.environ', {}, clear=True):
            with patch.object(llm_engine.tiny_model_manager, 'initialize', AsyncMock(return_value=True)):
                with patch.object(llm_engine.tiny_model_manager, 'load_model', AsyncMock(return_value=True)):
                    result = await llm_engine.initialize()
                    
                    assert result is True
                    assert llm_engine.provider == "tiny"
    
    @pytest.mark.asyncio
    async def test_generate_response_openai(self, llm_engine, mock_llm_response):
        """Test response generation with OpenAI."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 10
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        llm_engine.openai_client = mock_openai_client
        llm_engine.provider = "openai"
        
        request = LLMRequest(
            prompt="Test prompt",
            max_length=100,
            temperature=0.7
        )
        
        response = await llm_engine.generate_response(request)
        
        assert isinstance(response, LLMResponse)
        assert response.response == "Test response"
        assert response.model_used == "gpt-4"
        assert response.tokens_used == 10
        assert response.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_tiny(self, llm_engine, mock_llm_response):
        """Test response generation with tiny models."""
        llm_engine.provider = "tiny"
        
        with patch.object(llm_engine.tiny_model_manager, 'generate_response', AsyncMock(return_value=mock_llm_response)):
            request = LLMRequest(
                prompt="Test prompt",
                max_length=100,
                temperature=0.7
            )
            
            response = await llm_engine.generate_response(request)
            
            assert isinstance(response, LLMResponse)
            assert response.response == mock_llm_response["response"]
            assert response.model_used == mock_llm_response["model_used"]
    
    @pytest.mark.asyncio
    async def test_generate_response_error_handling(self, llm_engine):
        """Test error handling in response generation."""
        llm_engine.provider = "invalid_provider"
        
        request = LLMRequest(
            prompt="Test prompt",
            max_length=100,
            temperature=0.7
        )
        
        response = await llm_engine.generate_response(request)
        
        # Should return fallback response
        assert isinstance(response, LLMResponse)
        assert "trouble processing" in response.response.lower()
        assert response.model_used == "invalid_provider"
    
    @pytest.mark.asyncio
    async def test_response_length_limiting(self, llm_engine):
        """Test response length limiting for SMS."""
        mock_openai_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        # Long response that exceeds SMS limit
        mock_response.choices[0].message.content = "x" * 200
        mock_response.usage.total_tokens = 50
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        llm_engine.openai_client = mock_openai_client
        llm_engine.provider = "openai"
        
        request = LLMRequest(
            prompt="Test prompt",
            max_length=160,  # SMS limit
            temperature=0.7
        )
        
        response = await llm_engine.generate_response(request)
        
        # Response should be truncated
        assert len(response.response) <= 160
        assert response.response.endswith("...")


class TestTinyModelManager:
    """Test Tiny Model Manager functionality."""
    
    @pytest.fixture
    def model_manager(self):
        """Create model manager instance."""
        return TinyModelManager()
    
    @pytest.mark.asyncio
    async def test_model_manager_initialization(self, model_manager):
        """Test model manager initialization."""
        with patch.object(model_manager, '_check_available_models', AsyncMock()):
            with patch.object(model_manager, '_ensure_tiny_models_available', AsyncMock()):
                result = await model_manager.initialize()
                assert result is True
    
    @pytest.mark.asyncio
    async def test_load_ollama_model(self, model_manager):
        """Test loading Ollama model."""
        mock_ollama_client = Mock()
        mock_ollama_client.generate = AsyncMock(return_value={"response": "Test"})
        model_manager.ollama_client = mock_ollama_client
        
        with patch.object(model_manager, '_ensure_tiny_models_available', AsyncMock()):
            result = await model_manager.load_model("tinyllama")
            
            assert result is True
            assert "tinyllama" in model_manager.loaded_models
    
    @pytest.mark.asyncio
    async def test_load_transformers_model(self, model_manager):
        """Test loading transformers model."""
        mock_pipeline = Mock()
        mock_tokenizer = Mock()
        mock_model = Mock()
        
        with patch('backend.services.llm_inference.tiny_model_manager.AutoTokenizer') as mock_tokenizer_class:
            with patch('backend.services.llm_inference.tiny_model_manager.AutoModelForCausalLM') as mock_model_class:
                with patch('backend.services.llm_inference.tiny_model_manager.pipeline') as mock_pipeline_func:
                    mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                    mock_model_class.from_pretrained.return_value = mock_model
                    mock_pipeline_func.return_value = mock_pipeline
                    
                    result = await model_manager.load_model("tinyllama")
                    
                    assert result is True
                    assert "tinyllama" in model_manager.loaded_models
    
    @pytest.mark.asyncio
    async def test_generate_response_ollama(self, model_manager):
        """Test response generation with Ollama."""
        mock_ollama_client = Mock()
        mock_ollama_client.generate = AsyncMock(return_value={
            "response": "This is a test response from Ollama."
        })
        
        model_manager.loaded_models["tinyllama"] = {
            "type": "ollama",
            "name": "tinyllama:latest",
            "client": mock_ollama_client
        }
        
        result = await model_manager.generate_response(
            prompt="Test prompt",
            model_name="tinyllama",
            max_length=100
        )
        
        assert result["response"] == "This is a test response from Ollama."
        assert result["model_used"] == "tinyllama"
        assert result["provider"] == "local"
        assert result["processing_time"] > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_transformers(self, model_manager):
        """Test response generation with transformers."""
        mock_pipeline = Mock()
        mock_pipeline.return_value = [{
            "generated_text": "User: Test prompt\nEVY: This is a test response."
        }]
        
        mock_tokenizer = Mock()
        mock_tokenizer.eos_token_id = 50256
        
        model_manager.loaded_models["tinyllama"] = {
            "type": "transformers",
            "pipeline": mock_pipeline,
            "tokenizer": mock_tokenizer,
            "model": Mock()
        }
        
        result = await model_manager.generate_response(
            prompt="Test prompt",
            model_name="tinyllama",
            max_length=100
        )
        
        assert "test response" in result["response"].lower()
        assert result["model_used"] == "tinyllama"
        assert result["provider"] == "local"
    
    def test_prepare_prompt(self, model_manager):
        """Test prompt preparation."""
        prompt = "What's the weather?"
        context = "User is asking about weather"
        
        prepared = model_manager._prepare_prompt(prompt, context)
        
        assert "EVY" in prepared
        assert prompt in prepared
        assert context in prepared
        assert "Context:" in prepared
    
    def test_clean_response(self, model_manager):
        """Test response cleaning."""
        dirty_response = "  User: Hello  \n\n  EVY: Hi there!  \n\n  "
        
        cleaned = model_manager._clean_response(dirty_response)
        
        assert cleaned == "Hi there!"
        assert "User:" not in cleaned
        assert "EVY:" not in cleaned
    
    def test_get_available_models(self, model_manager):
        """Test getting available models list."""
        models = model_manager.get_available_models()
        
        assert len(models) > 0
        assert any(model["name"] == "tinyllama" for model in models)
        assert all("size" in model for model in models)
        assert all("memory_requirement" in model for model in models)
    
    @pytest.mark.asyncio
    async def test_unload_model(self, model_manager):
        """Test unloading model."""
        model_manager.loaded_models["test_model"] = {
            "type": "transformers",
            "model": Mock(),
            "pipeline": Mock(),
            "tokenizer": Mock()
        }
        
        result = await model_manager.unload_model("test_model")
        
        assert result is True
        assert "test_model" not in model_manager.loaded_models
    
    @pytest.mark.asyncio
    async def test_get_model_status(self, model_manager):
        """Test getting model status."""
        model_manager.loaded_models["tinyllama"] = {"type": "ollama"}
        
        status = await model_manager.get_model_status()
        
        assert status["total_models"] > 0
        assert status["loaded_models"] == 1
        assert len(status["available_models"]) > 0
        assert "memory_usage" in status


@pytest.mark.asyncio
async def test_llm_integration_flow():
    """Test complete LLM integration flow."""
    # Create engine
    engine = LLMInferenceEngine()
    
    # Mock dependencies
    with patch.object(engine.tiny_model_manager, 'initialize', AsyncMock(return_value=True)):
        with patch.object(engine.tiny_model_manager, 'load_model', AsyncMock(return_value=True)):
            with patch.object(engine.tiny_model_manager, 'generate_response', AsyncMock(return_value={
                "response": "This is a helpful response.",
                "model_used": "tinyllama",
                "tokens_used": 10,
                "processing_time": 1.5
            })):
                
                # Initialize engine
                await engine.initialize()
                
                # Create request
                request = LLMRequest(
                    prompt="What is 2+2?",
                    max_length=160,
                    temperature=0.7
                )
                
                # Generate response
                response = await engine.generate_response(request)
                
                # Verify response
                assert isinstance(response, LLMResponse)
                assert response.response == "This is a helpful response."
                assert response.model_used == "tinyllama"
                assert response.tokens_used == 10
                assert response.processing_time > 0


@pytest.mark.asyncio
async def test_performance_benchmark():
    """Test LLM inference performance."""
    engine = LLMInferenceEngine()
    
    with patch.object(engine.tiny_model_manager, 'initialize', AsyncMock(return_value=True)):
        with patch.object(engine.tiny_model_manager, 'load_model', AsyncMock(return_value=True)):
            with patch.object(engine.tiny_model_manager, 'generate_response', AsyncMock(return_value={
                "response": "Test response",
                "model_used": "tinyllama",
                "tokens_used": 5,
                "processing_time": 0.5
            })):
                
                await engine.initialize()
                
                # Test multiple requests
                start_time = time.time()
                requests = []
                
                for i in range(5):
                    request = LLMRequest(
                        prompt=f"Test prompt {i}",
                        max_length=100
                    )
                    requests.append(engine.generate_response(request))
                
                responses = await asyncio.gather(*requests)
                total_time = time.time() - start_time
                
                # Verify all responses
                assert len(responses) == 5
                assert all(isinstance(r, LLMResponse) for r in responses)
                
                # Performance should be reasonable (less than 10 seconds for 5 requests)
                assert total_time < 10.0
