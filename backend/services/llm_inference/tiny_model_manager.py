"""Tiny model manager for local LLM inference."""
import asyncio
import logging
import os
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import ollama
from backend.shared.config import settings

logger = logging.getLogger(__name__)


class TinyModelManager:
    """Manages tiny LLM models for local inference."""
    
    def __init__(self):
        self.model_cache_dir = Path("/tmp/evy_models")
        self.model_cache_dir.mkdir(exist_ok=True)
        
        self.loaded_models: Dict[str, Any] = {}
        self.ollama_client = None
        
        # Tiny model configurations
        self.tiny_models = {
            "tinyllama": {
                "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                "size": "1.1B",
                "memory_requirement": "2GB",
                "quantized": True
            },
            "phi-2-mini": {
                "model_id": "microsoft/DialoGPT-small",
                "size": "117M", 
                "memory_requirement": "500MB",
                "quantized": True
            },
            "distilgpt2": {
                "model_id": "distilgpt2",
                "size": "82M",
                "memory_requirement": "300MB",
                "quantized": False
            }
        }
        
        # Default tiny model
        self.default_tiny_model = "tinyllama"
        
    async def initialize(self) -> bool:
        """Initialize the tiny model manager."""
        try:
            logger.info("Initializing Tiny Model Manager...")
            
            # Initialize Ollama client
            try:
                self.ollama_client = ollama.AsyncClient(host=settings.ollama_base_url)
                logger.info("Ollama client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama client: {e}")
                self.ollama_client = None
            
            # Check available models
            await self._check_available_models()
            
            logger.info("Tiny Model Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Tiny Model Manager: {e}")
            return False
    
    async def _check_available_models(self) -> None:
        """Check which models are available."""
        try:
            if self.ollama_client:
                # Check Ollama models
                models = await self.ollama_client.list()
                ollama_models = [model['name'] for model in models.get('models', [])]
                logger.info(f"Available Ollama models: {ollama_models}")
                
                # Pull tiny models if not available
                await self._ensure_tiny_models_available()
            
            # Check local transformers models
            for model_name, config in self.tiny_models.items():
                model_path = self.model_cache_dir / model_name
                if model_path.exists():
                    logger.info(f"Local model available: {model_name}")
                else:
                    logger.info(f"Local model not cached: {model_name}")
                    
        except Exception as e:
            logger.error(f"Error checking available models: {e}")
    
    async def _ensure_tiny_models_available(self) -> None:
        """Ensure tiny models are available in Ollama."""
        if not self.ollama_client:
            return
            
        tiny_ollama_models = {
            "tinyllama": "tinyllama:latest",
            "phi": "phi:latest",
            "gemma": "gemma:2b"
        }
        
        for model_name, ollama_name in tiny_ollama_models.items():
            try:
                # Check if model exists
                models = await self.ollama_client.list()
                model_names = [model['name'] for model in models.get('models', [])]
                
                if ollama_name not in model_names:
                    logger.info(f"Pulling Ollama model: {ollama_name}")
                    await self.ollama_client.pull(ollama_name)
                    logger.info(f"Successfully pulled {ollama_name}")
                else:
                    logger.info(f"Model {ollama_name} already available")
                    
            except Exception as e:
                logger.warning(f"Failed to pull model {ollama_name}: {e}")
    
    async def load_model(self, model_name: str, use_quantization: bool = True) -> bool:
        """Load a tiny model for inference."""
        try:
            if model_name in self.loaded_models:
                logger.info(f"Model {model_name} already loaded")
                return True
            
            logger.info(f"Loading tiny model: {model_name}")
            
            # Try Ollama first if available
            if self.ollama_client and model_name in ["tinyllama", "phi", "gemma"]:
                if await self._load_ollama_model(model_name):
                    return True
            
            # Fallback to transformers
            if model_name in self.tiny_models:
                return await self._load_transformers_model(model_name, use_quantization)
            
            logger.error(f"Unknown model: {model_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    async def _load_ollama_model(self, model_name: str) -> bool:
        """Load model via Ollama."""
        try:
            model_map = {
                "tinyllama": "tinyllama:latest",
                "phi": "phi:latest", 
                "gemma": "gemma:2b"
            }
            
            ollama_name = model_map.get(model_name)
            if not ollama_name:
                return False
            
            # Test the model
            response = await self.ollama_client.generate(
                model=ollama_name,
                prompt="Hello",
                options={"temperature": 0.7, "max_tokens": 10}
            )
            
            self.loaded_models[model_name] = {
                "type": "ollama",
                "name": ollama_name,
                "client": self.ollama_client
            }
            
            logger.info(f"Successfully loaded Ollama model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Ollama model {model_name}: {e}")
            return False
    
    async def _load_transformers_model(self, model_name: str, use_quantization: bool) -> bool:
        """Load model via transformers library."""
        try:
            config = self.tiny_models[model_name]
            model_id = config["model_id"]
            
            logger.info(f"Loading transformers model: {model_id}")
            
            # Configure quantization if requested
            quantization_config = None
            if use_quantization and config.get("quantized", False):
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True
                )
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=self.model_cache_dir / model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                cache_dir=self.model_cache_dir / model_name,
                quantization_config=quantization_config,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=200,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
            
            self.loaded_models[model_name] = {
                "type": "transformers",
                "pipeline": pipe,
                "tokenizer": tokenizer,
                "model": model
            }
            
            logger.info(f"Successfully loaded transformers model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load transformers model {model_name}: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        model_name: Optional[str] = None,
        max_length: int = 160,
        temperature: float = 0.7,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using loaded model."""
        try:
            model_name = model_name or self.default_tiny_model
            
            if model_name not in self.loaded_models:
                # Try to load the model
                if not await self.load_model(model_name):
                    raise ValueError(f"Model {model_name} not available")
            
            model_info = self.loaded_models[model_name]
            start_time = time.time()
            
            # Prepare prompt
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Generate response based on model type
            if model_info["type"] == "ollama":
                response = await self._generate_ollama_response(
                    model_info, full_prompt, max_length, temperature
                )
            else:
                response = await self._generate_transformers_response(
                    model_info, full_prompt, max_length, temperature
                )
            
            processing_time = time.time() - start_time
            
            return {
                "response": response,
                "model_used": model_name,
                "processing_time": processing_time,
                "tokens_used": len(response.split()),  # Approximate
                "provider": "local"
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm having trouble processing your request. Please try again.",
                "model_used": model_name or "unknown",
                "processing_time": 0.0,
                "tokens_used": 0,
                "provider": "local",
                "error": str(e)
            }
    
    async def _generate_ollama_response(
        self, 
        model_info: Dict[str, Any], 
        prompt: str, 
        max_length: int, 
        temperature: float
    ) -> str:
        """Generate response using Ollama."""
        try:
            response = await model_info["client"].generate(
                model=model_info["name"],
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "max_tokens": min(max_length, 100),  # Ollama limit
                    "stop": ["\n\n", "User:", "Human:"]
                }
            )
            
            response_text = response["response"]
            
            # Ensure response fits in SMS
            if len(response_text) > max_length:
                response_text = response_text[:max_length - 3] + "..."
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return "I'm having trouble responding right now."
    
    async def _generate_transformers_response(
        self, 
        model_info: Dict[str, Any], 
        prompt: str, 
        max_length: int, 
        temperature: float
    ) -> str:
        """Generate response using transformers."""
        try:
            pipe = model_info["pipeline"]
            
            # Generate response
            result = pipe(
                prompt,
                max_length=len(prompt.split()) + min(max_length, 50),
                temperature=temperature,
                do_sample=True,
                pad_token_id=model_info["tokenizer"].eos_token_id,
                eos_token_id=model_info["tokenizer"].eos_token_id
            )
            
            # Extract response text
            generated_text = result[0]["generated_text"]
            response_text = generated_text[len(prompt):].strip()
            
            # Clean up response
            response_text = self._clean_response(response_text)
            
            # Ensure response fits in SMS
            if len(response_text) > max_length:
                response_text = response_text[:max_length - 3] + "..."
            
            return response_text
            
        except Exception as e:
            logger.error(f"Transformers generation error: {e}")
            return "I'm having trouble responding right now."
    
    def _prepare_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Prepare prompt for generation."""
        system_prompt = "You are EVY, a helpful AI assistant accessible via SMS. Keep responses under 160 characters. Be concise and helpful."
        
        full_prompt = system_prompt + "\n\n"
        
        if context:
            full_prompt += f"Context: {context}\n\n"
        
        full_prompt += f"User: {prompt}\nEVY:"
        
        return full_prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean up generated response."""
        # Remove extra whitespace
        response = " ".join(response.split())
        
        # Remove common generation artifacts
        artifacts = ["User:", "Human:", "Assistant:", "EVY:", "\n\n"]
        for artifact in artifacts:
            response = response.replace(artifact, "")
        
        # Remove trailing punctuation if response is too long
        if len(response) > 150:
            response = response.rstrip(".,!?;")
        
        return response.strip()
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        models = []
        
        for model_name, config in self.tiny_models.items():
            models.append({
                "name": model_name,
                "model_id": config["model_id"],
                "size": config["size"],
                "memory_requirement": config["memory_requirement"],
                "loaded": model_name in self.loaded_models
            })
        
        return models
    
    async def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory."""
        try:
            if model_name in self.loaded_models:
                model_info = self.loaded_models[model_name]
                
                if model_info["type"] == "transformers":
                    # Clear model from memory
                    del model_info["model"]
                    del model_info["pipeline"]
                    del model_info["tokenizer"]
                
                del self.loaded_models[model_name]
                
                # Force garbage collection
                import gc
                gc.collect()
                
                logger.info(f"Unloaded model: {model_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {e}")
            return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {
            "total_models": len(self.tiny_models),
            "loaded_models": len(self.loaded_models),
            "available_models": [],
            "memory_usage": self._get_memory_usage()
        }
        
        for model_name in self.tiny_models:
            status["available_models"].append({
                "name": model_name,
                "loaded": model_name in self.loaded_models,
                "type": self.loaded_models.get(model_name, {}).get("type", "not_loaded")
            })
        
        return status
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
