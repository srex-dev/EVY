"""lilEVY Tiny LLM Service - Optimized for edge deployment."""
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path

from backend.shared.models import LLMRequest, LLMResponse, ServiceHealth
from backend.shared.deployment_config import NodeType, get_deployment_profile
from backend.shared.logging import setup_logger

logger = setup_logger("lilevy-tiny-llm")


class TinyLLMService:
    """Tiny LLM service optimized for lilEVY edge deployment."""
    
    def __init__(self):
        self.node_type = NodeType.LILEVY
        self.profile = get_deployment_profile(self.node_type)
        self.model_manager = None
        self.current_model = None
        
        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens_generated": 0,
            "model_switches": 0,
            "last_request": None
        }
        
        # SMS-specific configuration
        self.max_response_length = 160  # SMS character limit
        self.system_prompt = """You are EVY, an AI assistant accessible via SMS. 
Your responses MUST be under 160 characters (SMS limit).
Be concise, helpful, and friendly. Focus on the most important information.
If the query is too complex for a short answer, suggest simplifying or breaking it down."""
    
    async def initialize(self) -> bool:
        """Initialize the tiny LLM service."""
        try:
            logger.info("Initializing lilEVY Tiny LLM Service...")
            
            # Import here to avoid circular imports
            from backend.services.llm_inference.tiny_model_manager import TinyModelManager
            
            self.model_manager = TinyModelManager()
            
            # Initialize with lilEVY-specific settings
            if not await self.model_manager.initialize():
                logger.error("Failed to initialize tiny model manager")
                return False
            
            # Load default tiny model based on lilEVY profile
            default_model = "tinyllama"  # 125M parameters, perfect for lilEVY
            if not await self.model_manager.load_model(default_model):
                logger.error(f"Failed to load default model: {default_model}")
                return False
            
            self.current_model = default_model
            logger.info(f"lilEVY Tiny LLM Service initialized with model: {default_model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize lilEVY Tiny LLM Service: {e}")
            return False
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using tiny LLM optimized for SMS."""
        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["last_request"] = time.time()
        
        try:
            # Enforce SMS character limit
            if len(request.prompt) > self.max_response_length * 4:  # Allow longer prompts
                request.prompt = request.prompt[:self.max_response_length * 4]
            
            # Add SMS-specific system prompt
            enhanced_prompt = f"{self.system_prompt}\n\nUser: {request.prompt}\nEVY:"
            
            # Generate response using tiny model
            if self.model_manager:
                response_text = await self._generate_with_tiny_model(enhanced_prompt)
            else:
                response_text = "I'm having trouble processing your request. Please try again."
            
            # Enforce SMS character limit on response
            if len(response_text) > self.max_response_length:
                response_text = response_text[:self.max_response_length - 3] + "..."
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update stats
            self.stats["successful_requests"] += 1
            self.stats["total_tokens_generated"] += len(response_text.split())
            self._update_average_response_time(processing_time)
            
            return LLMResponse(
                response=response_text,
                model_used=f"tiny-{self.current_model}",
                tokens_used=len(response_text.split()),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Tiny LLM generation error: {e}")
            self.stats["failed_requests"] += 1
            
            # Fallback response
            return LLMResponse(
                response="I'm having trouble right now. Please try again in a moment.",
                model_used="fallback",
                tokens_used=0,
                processing_time=time.time() - start_time
            )
    
    async def _generate_with_tiny_model(self, prompt: str) -> str:
        """Generate response using the loaded tiny model."""
        try:
            if not self.model_manager or not self.current_model:
                return "Model not available"
            
            # Use the tiny model manager for generation
            result = await self.model_manager.generate_text(
                prompt=prompt,
                max_tokens=self.profile.llm.max_tokens,
                temperature=0.7
            )
            
            return result if result else "I couldn't generate a response. Please try again."
            
        except Exception as e:
            logger.error(f"Tiny model generation failed: {e}")
            return "I'm having trouble processing your request."
    
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different tiny model."""
        try:
            if not self.model_manager:
                return False
            
            # Check if model is suitable for lilEVY (tiny models only)
            if not self._is_model_suitable_for_lilevy(model_name):
                logger.warning(f"Model {model_name} may not be suitable for lilEVY deployment")
                return False
            
            # Load new model
            if await self.model_manager.load_model(model_name):
                self.current_model = model_name
                self.stats["model_switches"] += 1
                logger.info(f"Switched to model: {model_name}")
                return True
            else:
                logger.error(f"Failed to load model: {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            return False
    
    def _is_model_suitable_for_lilevy(self, model_name: str) -> bool:
        """Check if model is suitable for lilEVY deployment."""
        # lilEVY should only use tiny models (125M-350M parameters)
        suitable_models = [
            "tinyllama", "distilgpt2", "phi-2-mini", "gemma-2b", 
            "qwen1.5-0.5b", "starcoder2-3b", "codegemma-2b"
        ]
        return model_name.lower() in suitable_models
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time."""
        total_requests = self.stats["successful_requests"]
        if total_requests == 1:
            self.stats["average_response_time"] = response_time
        else:
            # Running average
            current_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of loaded models."""
        if self.model_manager:
            return self.model_manager.get_model_status()
        return {"status": "not_initialized"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        model_status = self.get_model_status()
        
        return {
            **self.stats,
            "current_model": self.current_model,
            "model_status": model_status,
            "node_type": self.node_type.value,
            "max_response_length": self.max_response_length,
            "profile": {
                "model_size_range": self.profile.llm.model_size_range,
                "quantization": self.profile.llm.quantization,
                "max_tokens": self.profile.llm.max_tokens,
                "response_time_target": self.profile.llm.response_time_target
            }
        }
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            if self.model_manager:
                await self.model_manager.cleanup()
            logger.info("lilEVY Tiny LLM Service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global service instance
tiny_llm_service = TinyLLMService()
