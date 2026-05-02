"""Edge-Optimized Model Manager

Manages LLM models with edge constraints:
- 4-bit quantization
- Memory-aware loading
- Power-aware management
- Model switching and caching
- llama.cpp integration for performance
"""

import asyncio
import logging
import os
import time
import gc
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model status enumeration"""
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"


@dataclass
class ModelMetadata:
    """Model metadata"""
    name: str
    model_id: str
    size_mb: int
    quantized_size_mb: int  # 4-bit quantized size
    memory_requirement_mb: int  # RAM needed when loaded
    context_size: int  # Max context tokens
    supports_quantization: bool
    file_path: Optional[str] = None
    status: ModelStatus = ModelStatus.AVAILABLE
    loaded_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    use_count: int = 0


class EdgeModelManager:
    """Edge-optimized model manager with llama.cpp integration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Model storage
        self.model_dir = Path(self.config.get('model_dir', '/data/models'))
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry (metadata only, lightweight)
        self.model_registry: Dict[str, ModelMetadata] = {}
        
        # Loaded models (actual model instances)
        self.loaded_models: Dict[str, Any] = {}
        
        # Model cache (track recently used models)
        self.model_cache: Dict[str, datetime] = {}
        self.cache_ttl = timedelta(hours=1)  # Keep models loaded for 1 hour
        
        # Resource constraints
        self.max_memory_mb = self.config.get('max_memory_mb', 2000)  # 2GB for model
        self.max_context_tokens = self.config.get('max_context_tokens', 512)  # Small context
        self.num_threads = self.config.get('num_threads', 2)  # 2 threads (leave cores for other services)
        
        # Power management
        self.battery_threshold = self.config.get('battery_threshold', 30)
        self.current_battery_level = 100
        
        # llama.cpp integration (will use if available)
        self.llama_cpp_available = self._check_llama_cpp()
        
        # Initialize model registry
        self._initialize_model_registry()
        
        logger.info(f"Edge Model Manager initialized (llama.cpp: {self.llama_cpp_available})")
    
    def _check_llama_cpp(self) -> bool:
        """Check if llama.cpp Python bindings are available"""
        try:
            import llama_cpp
            return True
        except ImportError:
            logger.warning("llama.cpp not available, will use fallback")
            return False
    
    def _initialize_model_registry(self) -> None:
        """Initialize model registry with edge-optimized models"""
        # Edge-optimized model configurations
        edge_models = {
            "tinyllama-4bit": {
                "model_id": "TinyLlama-1.1B-Chat-v1.0",
                "size_mb": 2200,  # Original size
                "quantized_size_mb": 550,  # 4-bit quantized
                "memory_requirement_mb": 600,  # RAM needed when loaded
                "context_size": 512,
                "supports_quantization": True,
            },
            "phi-2-mini-4bit": {
                "model_id": "phi-2-mini",
                "size_mb": 500,
                "quantized_size_mb": 125,
                "memory_requirement_mb": 200,
                "context_size": 512,
                "supports_quantization": True,
            },
            "qwen1.5-0.5b-4bit": {
                "model_id": "Qwen/Qwen1.5-0.5B-Chat",
                "size_mb": 1000,
                "quantized_size_mb": 250,
                "memory_requirement_mb": 350,
                "context_size": 512,
                "supports_quantization": True,
            },
            "bitnet-b1.58-2B-4T": {
                "model_id": "microsoft/bitnet-b1.58-2B-4T",
                "size_mb": 2400,
                "quantized_size_mb": 1200,
                "memory_requirement_mb": 1536,
                "context_size": 4096,
                "supports_quantization": True,
            },
        }
        
        for model_name, model_info in edge_models.items():
            metadata = ModelMetadata(
                name=model_name,
                **model_info
            )
            self.model_registry[model_name] = metadata
        
        logger.info(f"Initialized model registry with {len(self.model_registry)} models")
    
    async def load_model(
        self,
        model_name: str,
        force_reload: bool = False
    ) -> bool:
        """Load a model with memory and power awareness"""
        try:
            # Check if model exists in registry
            if model_name not in self.model_registry:
                logger.error(f"Model not in registry: {model_name}")
                return False
            
            metadata = self.model_registry[model_name]
            
            # Check if already loaded
            if model_name in self.loaded_models and not force_reload:
                logger.info(f"Model {model_name} already loaded")
                metadata.status = ModelStatus.LOADED
                metadata.last_used = datetime.utcnow()
                metadata.use_count += 1
                return True
            
            # Check memory availability
            if not self._check_memory_available(metadata.memory_requirement_mb):
                logger.warning(f"Insufficient memory for {model_name} ({metadata.memory_requirement_mb}MB needed)")
                # Try unloading other models
                await self._unload_unused_models()
                if not self._check_memory_available(metadata.memory_requirement_mb):
                    return False
            
            # Check power level
            if self.current_battery_level < self.battery_threshold:
                logger.warning(f"Low battery ({self.current_battery_level}%), skipping model load")
                return False
            
            # Update status
            metadata.status = ModelStatus.LOADING
            
            # Load model
            start_time = time.time()
            if self.llama_cpp_available:
                success = await self._load_llama_cpp_model(metadata)
            else:
                success = await self._load_fallback_model(metadata)
            
            load_time = time.time() - start_time
            
            if success:
                metadata.status = ModelStatus.LOADED
                metadata.loaded_at = datetime.utcnow()
                metadata.last_used = datetime.utcnow()
                metadata.use_count += 1
                self.model_cache[model_name] = datetime.utcnow()
                logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
                return True
            else:
                metadata.status = ModelStatus.ERROR
                logger.error(f"Failed to load model {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            if model_name in self.model_registry:
                self.model_registry[model_name].status = ModelStatus.ERROR
            return False
    
    async def _load_llama_cpp_model(self, metadata: ModelMetadata) -> bool:
        """Load model using llama.cpp (optimal for edge)"""
        try:
            import llama_cpp
            
            # Find model file
            model_file = self._find_model_file(metadata.name)
            if not model_file:
                logger.error(f"Model file not found for {metadata.name}")
                return False
            
            # Create llama.cpp model with edge optimizations
            llm = llama_cpp.Llama(
                model_path=str(model_file),
                n_ctx=self.max_context_tokens,  # Small context
                n_threads=self.num_threads,  # 2 threads
                n_gpu_layers=0,  # CPU only (edge constraint)
                verbose=False,
                use_mmap=True,  # Memory-mapped I/O (faster)
                use_mlock=False,  # Don't lock memory (save resources)
            )
            
            self.loaded_models[metadata.name] = {
                'type': 'llama_cpp',
                'llm': llm,
                'metadata': metadata,
            }
            
            return True
            
        except Exception as e:
            logger.error(f"llama.cpp load error: {e}")
            return False
    
    async def _load_fallback_model(self, metadata: ModelMetadata) -> bool:
        """Fallback model loading (if llama.cpp not available)"""
        try:
            # Use existing TinyModelManager as fallback
            from backend.services.llm_inference.tiny_model_manager import TinyModelManager
            
            fallback_manager = TinyModelManager()
            success = await fallback_manager.load_model(
                metadata.name.replace('-4bit', ''),  # Remove quantization suffix
                use_quantization=True
            )
            
            if success:
                self.loaded_models[metadata.name] = {
                    'type': 'fallback',
                    'manager': fallback_manager,
                    'metadata': metadata,
                }
            
            return success
            
        except Exception as e:
            logger.error(f"Fallback load error: {e}")
            return False
    
    def _find_model_file(self, model_name: str) -> Optional[Path]:
        """Find model file on disk"""
        # Check common locations
        possible_paths = [
            self.model_dir / model_name / "model.gguf",
            self.model_dir / f"{model_name}.gguf",
            Path(f"/data/models/{model_name}.gguf"),
            Path(f"/tmp/evy_models/{model_name}.gguf"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _check_memory_available(self, required_mb: int) -> bool:
        """Check if enough memory is available"""
        try:
            import psutil
            available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            return available_memory >= required_mb
        except ImportError:
            # If psutil not available, assume memory is available
            return True
    
    async def _unload_unused_models(self) -> None:
        """Unload models that haven't been used recently"""
        now = datetime.utcnow()
        models_to_unload = []
        
        for model_name, last_used in self.model_cache.items():
            if now - last_used > self.cache_ttl:
                models_to_unload.append(model_name)
        
        for model_name in models_to_unload:
            await self.unload_model(model_name)
    
    async def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory"""
        try:
            if model_name not in self.loaded_models:
                return False
            
            model_info = self.loaded_models[model_name]
            
            # Unload based on type
            if model_info['type'] == 'llama_cpp':
                del model_info['llm']
            elif model_info['type'] == 'fallback':
                if 'manager' in model_info:
                    await model_info['manager'].unload_model(model_name)
            
            del self.loaded_models[model_name]
            
            if model_name in self.model_cache:
                del self.model_cache[model_name]
            
            if model_name in self.model_registry:
                self.model_registry[model_name].status = ModelStatus.UNLOADED
            
            # Force garbage collection
            gc.collect()
            
            logger.info(f"Unloaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {e}")
            return False
    
    async def switch_model(
        self,
        from_model: str,
        to_model: str
    ) -> bool:
        """Switch from one model to another"""
        try:
            # Unload current model
            if from_model in self.loaded_models:
                await self.unload_model(from_model)
            
            # Load new model
            return await self.load_model(to_model)
            
        except Exception as e:
            logger.error(f"Error switching models: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using loaded model"""
        try:
            # Select model
            if not model_name:
                # Use default model (smallest that fits in memory)
                model_name = self._select_default_model()
            
            if not model_name:
                return {
                    'response': "No model available. Please try again later.",
                    'error': 'no_model_available'
                }
            
            # Ensure model is loaded
            if model_name not in self.loaded_models:
                if not await self.load_model(model_name):
                    return {
                        'response': "Failed to load model. Please try again later.",
                        'error': 'model_load_failed'
                    }
            
            model_info = self.loaded_models[model_name]
            metadata = self.model_registry[model_name]
            
            # Update usage
            metadata.last_used = datetime.utcnow()
            metadata.use_count += 1
            
            # Generate response
            start_time = time.time()
            
            if model_info['type'] == 'llama_cpp':
                response = await self._generate_llama_cpp(
                    model_info['llm'],
                    prompt,
                    max_tokens,
                    temperature,
                    context
                )
            else:
                # Fallback generation
                response = await self._generate_fallback(
                    model_info,
                    prompt,
                    max_tokens,
                    temperature,
                    context
                )
            
            processing_time = time.time() - start_time
            
            return {
                'response': response,
                'model_used': model_name,
                'processing_time': processing_time,
                'tokens_used': len(response.split()),  # Approximate
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                'response': "I'm having trouble processing your request.",
                'error': str(e)
            }
    
    async def _generate_llama_cpp(
        self,
        llm: Any,
        prompt: str,
        max_tokens: int,
        temperature: float,
        context: Optional[str] = None
    ) -> str:
        """Generate using llama.cpp"""
        try:
            # Prepare prompt
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Generate
            response = llm(
                full_prompt,
                max_tokens=min(max_tokens, 100),  # Limit tokens
                temperature=temperature,
                stop=["\n\n", "User:", "Human:"],
            )
            
            # Extract text
            if isinstance(response, dict):
                text = response.get('choices', [{}])[0].get('text', '')
            else:
                text = str(response)
            
            # Clean and truncate to SMS limit
            text = self._clean_response(text)
            if len(text) > 160:
                text = text[:157] + "..."
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"llama.cpp generation error: {e}")
            return "I'm having trouble responding right now."
    
    async def _generate_fallback(
        self,
        model_info: Dict[str, Any],
        prompt: str,
        max_tokens: int,
        temperature: float,
        context: Optional[str] = None
    ) -> str:
        """Fallback generation"""
        if 'manager' in model_info:
            result = await model_info['manager'].generate_response(
                prompt,
                max_length=min(max_tokens, 160),
                temperature=temperature,
                context=context
            )
            return result.get('response', '')
        return "Generation not available."
    
    def _prepare_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Prepare prompt for generation"""
        system_prompt = "You are EVY, a helpful AI assistant. Keep responses under 160 characters. Be concise."
        
        full_prompt = f"{system_prompt}\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += f"User: {prompt}\nEVY:"
        
        return full_prompt
    
    def _clean_response(self, text: str) -> str:
        """Clean generated response"""
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove artifacts
        artifacts = ["User:", "Human:", "Assistant:", "EVY:", "\n\n"]
        for artifact in artifacts:
            text = text.replace(artifact, "")
        
        return text.strip()
    
    def _select_default_model(self) -> Optional[str]:
        """Select default model based on available memory"""
        # Sort models by memory requirement
        available_models = [
            (name, meta) for name, meta in self.model_registry.items()
            if meta.memory_requirement_mb <= self.max_memory_mb
        ]
        
        if not available_models:
            return None
        
        # Select smallest model that fits
        available_models.sort(key=lambda x: x[1].memory_requirement_mb)
        return available_models[0][0]
    
    def update_battery_level(self, level: int) -> None:
        """Update battery level for power-aware management"""
        self.current_battery_level = level
        
        # Unload models if battery too low
        if level < self.battery_threshold:
            logger.warning(f"Low battery ({level}%), unloading models")
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                if self.loaded_models:
                    asyncio.run(self._unload_all_models())
            else:
                loop.create_task(self._unload_all_models())
    
    async def _unload_all_models(self) -> None:
        """Unload all models (for power saving)"""
        model_names = list(self.loaded_models.keys())
        for model_name in model_names:
            await self.unload_model(model_name)
    
    def get_model_registry(self) -> Dict[str, Dict[str, Any]]:
        """Get model registry information"""
        return {
            name: {
                'name': meta.name,
                'model_id': meta.model_id,
                'size_mb': meta.size_mb,
                'quantized_size_mb': meta.quantized_size_mb,
                'memory_requirement_mb': meta.memory_requirement_mb,
                'context_size': meta.context_size,
                'status': meta.status.value,
                'loaded': name in self.loaded_models,
                'use_count': meta.use_count,
            }
            for name, meta in self.model_registry.items()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        return {
            'llama_cpp_available': self.llama_cpp_available,
            'loaded_models': len(self.loaded_models),
            'total_models': len(self.model_registry),
            'max_memory_mb': self.max_memory_mb,
            'current_battery_level': self.current_battery_level,
            'battery_threshold': self.battery_threshold,
            'models': self.get_model_registry(),
        }

