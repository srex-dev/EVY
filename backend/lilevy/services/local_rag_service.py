"""lilEVY Local RAG Service - Optimized for edge deployment."""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.shared.models import RAGQuery, RAGResult, ServiceHealth
from backend.shared.deployment_config import NodeType, get_deployment_profile
from backend.shared.logging import setup_logger

logger = setup_logger("lilevy-local-rag")


class LocalRAGService:
    """Local RAG service optimized for lilEVY edge deployment."""
    
    def __init__(self):
        self.node_type = NodeType.LILEVY
        self.profile = get_deployment_profile(self.node_type)
        
        # Service components
        self.embedding_service = None
        self.document_manager = None
        self.vector_db = None
        
        # Performance tracking
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_search_time": 0.0,
            "total_documents": 0,
            "cache_hits": 0,
            "last_search": None
        }
        
        # lilEVY-specific configuration
        self.max_documents = self.profile.rag.max_documents
        self.cache_size_mb = self.profile.rag.cache_size_mb
        self.search_method = self.profile.rag.search_method
        
        # Local knowledge categories
        self.local_categories = [
            "emergency", "weather", "local_info", "health", "education",
            "government", "transportation", "utilities", "community"
        ]
    
    async def initialize(self) -> bool:
        """Initialize the local RAG service."""
        try:
            logger.info("Initializing lilEVY Local RAG Service...")
            
            # Import here to avoid circular imports
            from backend.services.rag_service.embedding_service import SimpleEmbeddingService
            from backend.services.rag_service.document_manager import DocumentManager
            
            # Use simple embedding service for lilEVY (no heavy dependencies)
            self.embedding_service = SimpleEmbeddingService()
            
            # Initialize embedding service
            if not await self.embedding_service.initialize():
                logger.error("Failed to initialize embedding service")
                return False
            
            # Initialize document manager with lilEVY-specific settings
            data_dir = "/data/lilevy_knowledge"
            self.document_manager = DocumentManager(data_dir)
            
            # Load local knowledge base
            await self._load_local_knowledge()
            
            # Update stats
            doc_stats = self.document_manager.get_statistics()
            self.stats["total_documents"] = doc_stats["total_documents"]
            
            logger.info(f"lilEVY Local RAG Service initialized with {self.stats['total_documents']} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize lilEVY Local RAG Service: {e}")
            return False
    
    async def _load_local_knowledge(self):
        """Load local knowledge base for lilEVY."""
        try:
            # Check if we already have documents
            doc_stats = self.document_manager.get_statistics()
            if doc_stats["total_documents"] > 0:
                logger.info("Local knowledge base already loaded")
                return
            
            # Add lilEVY-specific sample data
            local_documents = [
                {
                    "title": "Emergency Contacts",
                    "text": "For emergencies, call 911. Local hospital: (555) 123-4567. Police: (555) 987-6543. Fire: (555) 456-7890.",
                    "category": "emergency",
                    "metadata": {"priority": "high", "source": "local"}
                },
                {
                    "title": "Weather Information",
                    "text": "Current weather conditions available via local sensors. For detailed forecasts, ask about specific time periods.",
                    "category": "weather",
                    "metadata": {"priority": "medium", "source": "sensor"}
                },
                {
                    "title": "Local Services",
                    "text": "City Hall: 123 Main St, open Mon-Fri 8AM-5PM. Library: 456 Oak Ave, open daily 9AM-8PM. Post Office: 789 Pine St.",
                    "category": "local_info",
                    "metadata": {"priority": "medium", "source": "local"}
                },
                {
                    "title": "Health Services",
                    "text": "Local clinic: 321 Health Way, appointments (555) 111-2222. Pharmacy: 654 Medicine Blvd, 24/7 emergency line.",
                    "category": "health",
                    "metadata": {"priority": "high", "source": "local"}
                },
                {
                    "title": "Education Resources",
                    "text": "School district office: 987 Education Dr. Adult learning center: 147 Study St. Online resources available for basic education.",
                    "category": "education",
                    "metadata": {"priority": "medium", "source": "local"}
                },
                {
                    "title": "Transportation",
                    "text": "Bus routes: Route 1 (Main St), Route 2 (Oak Ave), Route 3 (Pine St). Schedule available by asking for specific routes.",
                    "category": "transportation",
                    "metadata": {"priority": "medium", "source": "local"}
                },
                {
                    "title": "Utilities Information",
                    "text": "Power company: (555) 333-4444. Water department: (555) 555-6666. Gas company: (555) 777-8888. Emergency outages: 24/7 line.",
                    "category": "utilities",
                    "metadata": {"priority": "high", "source": "local"}
                },
                {
                    "title": "Community Events",
                    "text": "Weekly farmers market: Saturdays 8AM-2PM at City Park. Community center events posted monthly. Library programs for all ages.",
                    "category": "community",
                    "metadata": {"priority": "low", "source": "local"}
                }
            ]
            
            # Add documents to local knowledge base
            for doc in local_documents:
                await self.document_manager.add_document(
                    text=doc["text"],
                    title=doc["title"],
                    category=doc["category"],
                    metadata=doc["metadata"]
                )
            
            logger.info(f"Loaded {len(local_documents)} local knowledge documents")
            
        except Exception as e:
            logger.error(f"Failed to load local knowledge: {e}")
    
    async def search(self, query: RAGQuery) -> RAGResult:
        """Search local knowledge base with lilEVY optimizations."""
        import time
        start_time = time.time()
        
        self.stats["total_searches"] += 1
        self.stats["last_search"] = time.time()
        
        try:
            # Limit search scope for lilEVY performance
            limited_top_k = min(query.top_k, 5)  # Limit results for SMS responses
            
            # Perform local search
            search_results = await self.document_manager.search_documents(
                query=query.query,
                category=query.filter_metadata.get('category') if query.filter_metadata else None,
                limit=limited_top_k
            )
            
            # Convert to RAGResult format
            documents = []
            scores = []
            metadata = []
            
            for result in search_results:
                documents.append(result["document"]["text"])
                scores.append(result["score"] / 10.0)  # Normalize score
                metadata.append({
                    "category": result["document"].get("category", "general"),
                    "title": result["document"].get("title", ""),
                    "source": "local"
                })
            
            # Update stats
            self.stats["successful_searches"] += 1
            search_time = time.time() - start_time
            self._update_average_search_time(search_time)
            
            logger.info(f"Local search found {len(documents)} documents for: {query.query[:50]}")
            
            return RAGResult(
                documents=documents,
                scores=scores,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Local RAG search error: {e}")
            self.stats["failed_searches"] += 1
            return RAGResult(documents=[], scores=[], metadata=[])
    
    async def add_local_document(self, text: str, title: str = "", category: str = "general") -> str:
        """Add a document to local knowledge base."""
        try:
            # Validate category
            if category not in self.local_categories:
                category = "general"
            
            # Add document
            doc_id = await self.document_manager.add_document(
                text=text,
                title=title,
                category=category,
                metadata={"source": "local", "added_by": "lilevy"}
            )
            
            # Update stats
            self.stats["total_documents"] += 1
            
            logger.info(f"Added local document: {doc_id} ({category})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add local document: {e}")
            return ""
    
    async def get_local_categories(self) -> List[str]:
        """Get available local knowledge categories."""
        return await self.document_manager.get_all_categories()
    
    async def get_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get documents by category."""
        return await self.document_manager.get_documents_by_category(category)
    
    def _update_average_search_time(self, search_time: float):
        """Update average search time."""
        total_searches = self.stats["successful_searches"]
        if total_searches == 1:
            self.stats["average_search_time"] = search_time
        else:
            # Running average
            current_avg = self.stats["average_search_time"]
            self.stats["average_search_time"] = (
                (current_avg * (total_searches - 1) + search_time) / total_searches
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        doc_stats = self.document_manager.get_statistics() if self.document_manager else {}
        
        return {
            **self.stats,
            "node_type": self.node_type.value,
            "local_categories": self.local_categories,
            "document_manager_stats": doc_stats,
            "profile": {
                "max_documents": self.max_documents,
                "cache_size_mb": self.cache_size_mb,
                "search_method": self.search_method
            }
        }
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            if self.embedding_service:
                await self.embedding_service.cleanup()
            logger.info("lilEVY Local RAG Service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global service instance
local_rag_service = LocalRAGService()
