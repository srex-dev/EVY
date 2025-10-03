"""Local embedding service for RAG operations."""
import asyncio
import logging
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

logger = logging.getLogger(__name__)


class LocalEmbeddingService:
    """Local embedding service using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.model_cache_dir = Path("/tmp/evy_models")
        self.model_cache_dir.mkdir(exist_ok=True)
        
        # Embedding cache
        self.embedding_cache = {}
        self.cache_file = self.model_cache_dir / "embedding_cache.json"
        self._load_cache()
        
        # Model configuration
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        self.max_sequence_length = 256
        
    async def initialize(self) -> bool:
        """Initialize the embedding model."""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.error("sentence-transformers not available")
                return False
            
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Load model with caching
            model_path = self.model_cache_dir / self.model_name
            if model_path.exists():
                logger.info(f"Loading cached model from {model_path}")
                self.model = SentenceTransformer(str(model_path))
            else:
                logger.info("Downloading model from Hugging Face")
                self.model = SentenceTransformer(self.model_name)
                
                # Cache the model
                self.model.save(str(model_path))
                logger.info(f"Model cached to {model_path}")
            
            # Get actual embedding dimension
            if self.model:
                # Test embedding to get dimension
                test_embedding = self.model.encode(["test"])
                self.embedding_dim = test_embedding.shape[1]
                logger.info(f"Embedding dimension: {self.embedding_dim}")
            
            logger.info("Embedding service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            return False
    
    def _load_cache(self) -> None:
        """Load embedding cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.embedding_cache = json.load(f)
                logger.info(f"Loaded {len(self.embedding_cache)} cached embeddings")
        except Exception as e:
            logger.warning(f"Failed to load embedding cache: {e}")
            self.embedding_cache = {}
    
    def _save_cache(self) -> None:
        """Save embedding cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.embedding_cache, f)
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
    
    def _get_text_hash(self, text: str) -> str:
        """Get hash for text to use as cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    async def encode_text(self, text: str) -> Optional[List[float]]:
        """Encode text to embedding vector."""
        try:
            if not self.model:
                logger.error("Embedding model not initialized")
                return None
            
            # Check cache first
            text_hash = self._get_text_hash(text)
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]
            
            # Truncate text if too long
            if len(text) > self.max_sequence_length * 4:  # Rough character estimate
                text = text[:self.max_sequence_length * 4] + "..."
            
            # Generate embedding
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                lambda: self.model.encode([text], convert_to_tensor=False)[0]
            )
            
            # Convert to list
            embedding_list = embedding.tolist()
            
            # Cache the result
            self.embedding_cache[text_hash] = embedding_list
            self._save_cache()
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return None
    
    async def encode_texts(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Encode multiple texts to embedding vectors."""
        try:
            if not self.model:
                logger.error("Embedding model not initialized")
                return [None] * len(texts)
            
            # Check cache for each text
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                text_hash = self._get_text_hash(text)
                if text_hash in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[text_hash]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                # Truncate long texts
                truncated_texts = []
                for text in uncached_texts:
                    if len(text) > self.max_sequence_length * 4:
                        truncated_texts.append(text[:self.max_sequence_length * 4] + "...")
                    else:
                        truncated_texts.append(text)
                
                # Generate embeddings
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    None,
                    lambda: self.model.encode(truncated_texts, convert_to_tensor=False)
                )
                
                # Cache results
                for i, embedding in enumerate(embeddings):
                    text_hash = self._get_text_hash(uncached_texts[i])
                    embedding_list = embedding.tolist()
                    self.embedding_cache[text_hash] = embedding_list
                
                self._save_cache()
            
            # Combine cached and new embeddings
            result = [None] * len(texts)
            
            # Add cached embeddings
            for i, embedding in cached_embeddings:
                result[i] = embedding
            
            # Add new embeddings
            if uncached_texts:
                for i, embedding in enumerate(embeddings):
                    result[uncached_indices[i]] = embedding.tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            return [None] * len(texts)
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "max_sequence_length": self.max_sequence_length,
            "cache_size": len(self.embedding_cache),
            "model_loaded": self.model is not None,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "torch_available": TORCH_AVAILABLE
        }
    
    async def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_cache = {}
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            logger.info("Embedding cache cleared")
        except Exception as e:
            logger.warning(f"Failed to delete cache file: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.model and TORCH_AVAILABLE:
                # Clear GPU memory if using CUDA
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            # Save cache before cleanup
            self._save_cache()
            
            logger.info("Embedding service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class SimpleEmbeddingService:
    """Simple embedding service for when sentence-transformers is not available."""
    
    def __init__(self):
        self.embedding_dim = 300  # Fixed dimension
        self.word_embeddings = {}
        self._load_simple_embeddings()
    
    def _load_simple_embeddings(self):
        """Load simple word embeddings."""
        # Simple word frequency-based embeddings
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an',
            'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
            'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some',
            'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look',
            'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after',
            'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
            'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most',
            'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said',
            'each', 'which', 'their', 'said', 'if', 'will', 'up', 'out',
            'many', 'then', 'them', 'can', 'only', 'other', 'new', 'some',
            'time', 'very', 'when', 'much', 'get', 'through', 'back', 'much',
            'before', 'go', 'good', 'little', 'very', 'still', 'here', 'old',
            'every', 'great', 'small', 'large', 'long', 'little', 'own',
            'other', 'another', 'same', 'different', 'right', 'left', 'high',
            'low', 'near', 'far', 'inside', 'outside', 'above', 'below'
        }
        
        # Create simple embeddings for common words
        np.random.seed(42)  # For reproducibility
        for word in common_words:
            self.word_embeddings[word] = np.random.normal(0, 1, self.embedding_dim).tolist()
    
    async def initialize(self) -> bool:
        """Initialize the simple embedding service."""
        logger.info("Simple embedding service initialized")
        return True
    
    async def encode_text(self, text: str) -> Optional[List[float]]:
        """Encode text using simple word embeddings."""
        try:
            words = text.lower().split()
            embeddings = []
            
            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum())
                if word in self.word_embeddings:
                    embeddings.append(self.word_embeddings[word])
            
            if not embeddings:
                # Return zero vector if no known words
                return [0.0] * self.embedding_dim
            
            # Average the word embeddings
            avg_embedding = np.mean(embeddings, axis=0)
            return avg_embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to encode text with simple embeddings: {e}")
            return None
    
    async def encode_texts(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Encode multiple texts."""
        results = []
        for text in texts:
            embedding = await self.encode_text(text)
            results.append(embedding)
        return results
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_name": "simple_word_embeddings",
            "embedding_dim": self.embedding_dim,
            "word_count": len(self.word_embeddings),
            "model_loaded": True,
            "sentence_transformers_available": False,
            "torch_available": False
        }
    
    async def clear_cache(self) -> None:
        """No cache to clear."""
        pass
    
    async def cleanup(self) -> None:
        """No cleanup needed."""
        pass
