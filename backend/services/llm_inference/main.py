"""LLM Inference Service - Handles AI model inference."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import time
from openai import AsyncOpenAI

from backend.shared.models import LLMRequest, LLMResponse, ServiceHealth
from backend.shared.config import settings
from backend.shared.logging import setup_logger
from backend.services.llm_inference.tiny_model_manager import TinyModelManager

logger = setup_logger("llm-inference")


class LLMInferenceEngine:
    """Manages LLM inference operations."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.openai_client = None
        self.tiny_model_manager = TinyModelManager()
        
        if self.provider == "openai":
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not set, falling back to tiny models")
                self.provider = "tiny"
            else:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
        
        # SMS-specific system prompt
        self.system_prompt = """You are EVY, an AI assistant accessible via SMS. 
Your responses MUST be under 160 characters (SMS limit).
Be concise, helpful, and friendly. Focus on the most important information.
If the query is too complex for a short answer, suggest simplifying or breaking it down."""
    
    async def initialize(self) -> bool:
        """Initialize the LLM inference engine."""
        try:
            logger.info("Initializing LLM Inference Engine...")
            
            # Initialize tiny model manager
            if not await self.tiny_model_manager.initialize():
                logger.warning("Failed to initialize tiny model manager")
            
            # Load default tiny model if using tiny provider
            if self.provider == "tiny":
                await self.tiny_model_manager.load_model("tinyllama")
            
            logger.info(f"LLM Inference Engine initialized with provider: {self.provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Inference Engine: {e}")
            return False
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using configured LLM provider."""
        start_time = time.time()
        
        try:
            if self.provider == "openai":
                return await self._generate_openai(request, start_time)
            elif self.provider == "tiny":
                return await self._generate_tiny(request, start_time)
            elif self.provider == "ollama":
                return await self._generate_ollama(request, start_time)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM inference error: {e}")
            # Fallback response
            return LLMResponse(
                response="I'm having trouble processing your request. Please try again.",
                model_used=self.provider,
                tokens_used=0,
                processing_time=time.time() - start_time
            )
    
    async def _generate_openai(self, request: LLMRequest, start_time: float) -> LLMResponse:
        """Generate response using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if request.context:
            messages.append({
                "role": "system",
                "content": f"Context: {request.context}"
            })
        
        messages.append({"role": "user", "content": request.prompt})
        
        # Get model
        model = request.model or settings.default_model
        
        logger.info(f"Calling OpenAI with model: {model}")
        
        # Call OpenAI
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100,  # Keep responses short
            temperature=request.temperature
        )
        
        response_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Ensure response fits in SMS
        if len(response_text) > request.max_length:
            response_text = response_text[:request.max_length - 3] + "..."
        
        processing_time = time.time() - start_time
        
        logger.info(f"Response generated in {processing_time:.2f}s, {tokens_used} tokens")
        
        return LLMResponse(
            response=response_text,
            model_used=model,
            tokens_used=tokens_used,
            processing_time=processing_time
        )
    
    async def _generate_tiny(self, request: LLMRequest, start_time: float) -> LLMResponse:
        """Generate response using tiny local model."""
        try:
            model_name = request.model or "tinyllama"
            
            result = await self.tiny_model_manager.generate_response(
                prompt=request.prompt,
                model_name=model_name,
                max_length=request.max_length,
                temperature=request.temperature,
                context=request.context
            )
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                response=result["response"],
                model_used=result["model_used"],
                tokens_used=result["tokens_used"],
                processing_time=processing_time,
                metadata={"provider": "tiny", "memory_usage": result.get("memory_usage")}
            )
            
        except Exception as e:
            logger.error(f"Tiny model generation error: {e}")
            return LLMResponse(
                response="I'm having trouble processing your request. Please try again.",
                model_used="tiny",
                tokens_used=0,
                processing_time=time.time() - start_time
            )
    
    async def _generate_ollama(self, request: LLMRequest, start_time: float) -> LLMResponse:
        """Generate response using Ollama."""
        try:
            # Use tiny model manager's Ollama integration
            result = await self.tiny_model_manager.generate_response(
                prompt=request.prompt,
                model_name="tinyllama",  # Default Ollama model
                max_length=request.max_length,
                temperature=request.temperature,
                context=request.context
            )
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                response=result["response"],
                model_used="ollama",
                tokens_used=result["tokens_used"],
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return LLMResponse(
                response="I'm having trouble processing your request. Please try again.",
                model_used="ollama",
                tokens_used=0,
                processing_time=time.time() - start_time
            )


# Global engine instance
llm_engine = LLMInferenceEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("LLM Inference Service starting up...")
    logger.info(f"Using provider: {settings.llm_provider}")
    
    # Initialize the engine
    if not await llm_engine.initialize():
        logger.error("Failed to initialize LLM Inference Engine")
        raise RuntimeError("LLM Inference Engine initialization failed")
    
    yield
    logger.info("LLM Inference Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="EVY LLM Inference Service",
    description="Handles AI model inference for EVY system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint."""
    model_status = await llm_engine.tiny_model_manager.get_model_status()
    
    return ServiceHealth(
        service_name="llm-inference",
        status="healthy",
        version="1.0.0",
        details={
            "provider": llm_engine.provider,
            "model": settings.default_model,
            "tiny_models": model_status
        }
    )


@app.post("/inference", response_model=LLMResponse)
async def generate_inference(request: LLMRequest):
    """Generate LLM inference."""
    try:
        response = await llm_engine.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available models."""
    available_models = llm_engine.tiny_model_manager.get_available_models()
    
    return {
        "provider": llm_engine.provider,
        "openai_models": [settings.default_model, settings.tiny_model],
        "tiny_models": available_models,
        "current_model": settings.default_model if llm_engine.provider == "openai" else "tinyllama"
    }


@app.get("/tiny-models/status")
async def get_tiny_models_status():
    """Get status of tiny models."""
    return await llm_engine.tiny_model_manager.get_model_status()


@app.post("/tiny-models/load")
async def load_tiny_model(model_name: str, use_quantization: bool = True):
    """Load a specific tiny model."""
    try:
        success = await llm_engine.tiny_model_manager.load_model(model_name, use_quantization)
        if success:
            return {"status": "loaded", "model": model_name}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load model {model_name}")
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tiny-models/unload")
async def unload_tiny_model(model_name: str):
    """Unload a specific tiny model."""
    try:
        success = await llm_engine.tiny_model_manager.unload_model(model_name)
        if success:
            return {"status": "unloaded", "model": model_name}
        else:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found or not loaded")
    except Exception as e:
        logger.error(f"Failed to unload model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/switch-provider")
async def switch_provider(provider: str):
    """Switch LLM provider."""
    try:
        if provider not in ["openai", "tiny", "ollama"]:
            raise HTTPException(status_code=400, detail="Invalid provider. Must be 'openai', 'tiny', or 'ollama'")
        
        old_provider = llm_engine.provider
        llm_engine.provider = provider
        
        # Initialize provider-specific resources
        if provider == "tiny" and not await llm_engine.tiny_model_manager.load_model("tinyllama"):
            logger.warning("Failed to load default tiny model")
        
        return {
            "status": "switched",
            "old_provider": old_provider,
            "new_provider": provider
        }
        
    except Exception as e:
        logger.error(f"Failed to switch provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.llm_inference_port,
        log_level="info"
    )


