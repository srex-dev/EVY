"""bigEVY Global RAG Service - Optimized for central processing."""
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.shared.models import RAGQuery, RAGResult, ServiceHealth
from backend.shared.deployment_config import NodeType, get_deployment_profile
from backend.shared.logging import setup_logger

logger = setup_logger("bigevy-global-rag")


class GlobalRAGService:
    """Global RAG service optimized for bigEVY central processing."""
    
    def __init__(self):
        self.node_type = NodeType.BIGEVY
        self.profile = get_deployment_profile(self.node_type)
        
        # Service components
        self.embedding_service = None
        self.document_manager = None
        self.vector_db = None
        self.knowledge_sync_manager = None
        
        # Performance tracking
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_search_time": 0.0,
            "total_documents": 0,
            "cache_hits": 0,
            "sync_operations": 0,
            "last_search": None,
            "last_sync": None
        }
        
        # bigEVY-specific configuration
        self.max_documents = self.profile.rag.max_documents
        self.cache_size_mb = self.profile.rag.cache_size_mb
        self.search_method = self.profile.rag.search_method
        
        # Global knowledge categories
        self.global_categories = [
            "general_knowledge", "science", "technology", "medicine", "law",
            "business", "education", "history", "geography", "culture",
            "news", "research", "academic", "reference", "encyclopedia"
        ]
        
        # Knowledge sources
        self.knowledge_sources = {
            "wikipedia": {"enabled": True, "priority": "high"},
            "academic": {"enabled": True, "priority": "high"},
            "news": {"enabled": True, "priority": "medium"},
            "government": {"enabled": True, "priority": "medium"},
            "medical": {"enabled": True, "priority": "high"},
            "legal": {"enabled": True, "priority": "medium"}
        }
    
    async def initialize(self) -> bool:
        """Initialize the global RAG service."""
        try:
            logger.info("Initializing bigEVY Global RAG Service...")
            
            # Import here to avoid circular imports
            from backend.services.rag_service.embedding_service import LocalEmbeddingService
            from backend.services.rag_service.document_manager import DocumentManager
            
            # Use advanced embedding service for bigEVY
            self.embedding_service = LocalEmbeddingService(model_name="all-mpnet-base-v2")
            
            # Initialize embedding service
            if not await self.embedding_service.initialize():
                logger.error("Failed to initialize embedding service")
                return False
            
            # Initialize document manager with bigEVY-specific settings
            data_dir = "/data/bigevy_global_knowledge"
            self.document_manager = DocumentManager(data_dir)
            
            # Initialize knowledge sync manager
            await self._initialize_knowledge_sync()
            
            # Load global knowledge base
            await self._load_global_knowledge()
            
            # Update stats
            doc_stats = self.document_manager.get_statistics()
            self.stats["total_documents"] = doc_stats["total_documents"]
            
            logger.info(f"bigEVY Global RAG Service initialized with {self.stats['total_documents']} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bigEVY Global RAG Service: {e}")
            return False
    
    async def _initialize_knowledge_sync(self):
        """Initialize knowledge synchronization manager."""
        try:
            # This would handle syncing with lilEVY nodes and external sources
            self.knowledge_sync_manager = {
                "initialized": True,
                "sync_sources": list(self.knowledge_sources.keys()),
                "last_full_sync": None,
                "incremental_sync_enabled": True
            }
            logger.info("Knowledge sync manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge sync: {e}")
            raise
    
    async def _load_global_knowledge(self):
        """Load global knowledge base for bigEVY."""
        try:
            # Check if we already have documents
            doc_stats = self.document_manager.get_statistics()
            if doc_stats["total_documents"] > 100:  # More comprehensive than lilEVY
                logger.info("Global knowledge base already loaded")
                return
            
            # Add bigEVY-specific comprehensive data
            global_documents = [
                {
                    "title": "General Science Knowledge",
                    "text": "Comprehensive scientific knowledge covering physics, chemistry, biology, and mathematics. Includes fundamental principles, laws, and recent discoveries.",
                    "category": "science",
                    "metadata": {"priority": "high", "source": "academic", "comprehensiveness": "high"}
                },
                {
                    "title": "Technology and Computing",
                    "text": "Advanced technology knowledge including programming, AI, machine learning, cybersecurity, and emerging technologies.",
                    "category": "technology",
                    "metadata": {"priority": "high", "source": "academic", "comprehensiveness": "high"}
                },
                {
                    "title": "Medical and Health Information",
                    "text": "Comprehensive medical knowledge including anatomy, physiology, diseases, treatments, medications, and health guidelines.",
                    "category": "medicine",
                    "metadata": {"priority": "high", "source": "medical", "comprehensiveness": "high"}
                },
                {
                    "title": "Legal and Regulatory Information",
                    "text": "Legal knowledge covering laws, regulations, rights, responsibilities, and legal procedures across different jurisdictions.",
                    "category": "law",
                    "metadata": {"priority": "medium", "source": "legal", "comprehensiveness": "medium"}
                },
                {
                    "title": "Business and Economics",
                    "text": "Business knowledge including economics, finance, management, marketing, entrepreneurship, and market analysis.",
                    "category": "business",
                    "metadata": {"priority": "medium", "source": "academic", "comprehensiveness": "high"}
                },
                {
                    "title": "Historical Information",
                    "text": "Comprehensive historical knowledge covering world history, major events, historical figures, and historical context.",
                    "category": "history",
                    "metadata": {"priority": "medium", "source": "academic", "comprehensiveness": "high"}
                },
                {
                    "title": "Geographical Knowledge",
                    "text": "Geographical information including countries, cities, physical geography, climate, and geographical features.",
                    "category": "geography",
                    "metadata": {"priority": "medium", "source": "reference", "comprehensiveness": "high"}
                },
                {
                    "title": "Educational Resources",
                    "text": "Educational content covering various subjects, learning methodologies, academic resources, and educational systems.",
                    "category": "education",
                    "metadata": {"priority": "high", "source": "academic", "comprehensiveness": "high"}
                },
                {
                    "title": "Cultural and Social Information",
                    "text": "Cultural knowledge including traditions, customs, languages, social structures, and cultural practices worldwide.",
                    "category": "culture",
                    "metadata": {"priority": "medium", "source": "reference", "comprehensiveness": "medium"}
                },
                {
                    "title": "Current Events and News",
                    "text": "Recent news and current events across various categories including politics, science, technology, and global affairs.",
                    "category": "news",
                    "metadata": {"priority": "medium", "source": "news", "comprehensiveness": "medium"}
                }
            ]
            
            # Add documents to global knowledge base
            for doc in global_documents:
                await self.document_manager.add_document(
                    text=doc["text"],
                    title=doc["title"],
                    category=doc["category"],
                    metadata=doc["metadata"]
                )
            
            logger.info(f"Loaded {len(global_documents)} global knowledge documents")
            
        except Exception as e:
            logger.error(f"Failed to load global knowledge: {e}")
    
    async def search(self, query: RAGQuery) -> RAGResult:
        """Search global knowledge base with advanced capabilities."""
        start_time = time.time()
        
        self.stats["total_searches"] += 1
        self.stats["last_search"] = time.time()
        
        try:
            # Use full top_k for bigEVY (more comprehensive results)
            search_results = await self.document_manager.search_documents(
                query=query.query,
                category=query.filter_metadata.get('category') if query.filter_metadata else None,
                limit=query.top_k
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
                    "source": result["document"].get("metadata", {}).get("source", "global"),
                    "comprehensiveness": result["document"].get("metadata", {}).get("comprehensiveness", "medium")
                })
            
            # Update stats
            self.stats["successful_searches"] += 1
            search_time = time.time() - start_time
            self._update_average_search_time(search_time)
            
            logger.info(f"Global search found {len(documents)} documents for: {query.query[:50]}")
            
            return RAGResult(
                documents=documents,
                scores=scores,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Global RAG search error: {e}")
            self.stats["failed_searches"] += 1
            return RAGResult(documents=[], scores=[], metadata=[])
    
    async def sync_knowledge_from_lilevy(self, lilevy_documents: List[Dict[str, Any]]) -> bool:
        """Sync knowledge from lilEVY nodes."""
        try:
            self.stats["sync_operations"] += 1
            self.stats["last_sync"] = time.time()
            
            # Process documents from lilEVY nodes
            synced_count = 0
            for doc in lilevy_documents:
                try:
                    # Add with bigEVY-specific metadata
                    doc_id = await self.document_manager.add_document(
                        text=doc.get("text", ""),
                        title=doc.get("title", ""),
                        category=doc.get("category", "synced"),
                        metadata={
                            **doc.get("metadata", {}),
                            "source": "lilevy_sync",
                            "synced_at": time.time(),
                            "node_type": "lilevy"
                        }
                    )
                    if doc_id:
                        synced_count += 1
                except Exception as e:
                    logger.warning(f"Failed to sync document: {e}")
            
            logger.info(f"Synced {synced_count} documents from lilEVY nodes")
            return synced_count > 0
            
        except Exception as e:
            logger.error(f"Failed to sync knowledge from lilEVY: {e}")
            return False
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get global analytics and insights."""
        try:
            doc_stats = self.document_manager.get_statistics()
            
            return {
                "total_documents": doc_stats["total_documents"],
                "category_breakdown": doc_stats.get("category_breakdown", {}),
                "search_statistics": self.stats,
                "knowledge_sources": self.knowledge_sources,
                "sync_status": {
                    "last_sync": self.stats["last_sync"],
                    "total_sync_operations": self.stats["sync_operations"]
                },
                "performance_metrics": {
                    "average_search_time": self.stats["average_search_time"],
                    "cache_hit_rate": self.stats["cache_hits"] / max(self.stats["total_searches"], 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {}
    
    async def add_global_document(self, text: str, title: str = "", category: str = "general", source: str = "manual") -> str:
        """Add a document to global knowledge base."""
        try:
            # Validate category
            if category not in self.global_categories:
                category = "general_knowledge"
            
            # Add document
            doc_id = await self.document_manager.add_document(
                text=text,
                title=title,
                category=category,
                metadata={"source": source, "added_by": "bigevy", "comprehensiveness": "high"}
            )
            
            # Update stats
            self.stats["total_documents"] += 1
            
            logger.info(f"Added global document: {doc_id} ({category})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add global document: {e}")
            return ""
    
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
            "global_categories": self.global_categories,
            "document_manager_stats": doc_stats,
            "knowledge_sources": self.knowledge_sources,
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
            logger.info("bigEVY Global RAG Service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global service instance
global_rag_service = GlobalRAGService()
