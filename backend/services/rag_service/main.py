"""RAG Service - Retrieval-Augmented Generation with vector database."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import AsyncOpenAI
import os
import asyncio
import hashlib
from datetime import datetime

from backend.shared.models import RAGQuery, RAGResult, ServiceHealth
from backend.shared.config import settings
from backend.shared.logging import setup_logger
from backend.services.rag_service.embedding_service import LocalEmbeddingService, SimpleEmbeddingService
from backend.services.rag_service.document_manager import DocumentManager

logger = setup_logger("rag-service")


class RAGService:
    """Manages RAG operations with vector database."""
    
    def __init__(self):
        self.collection_name = "evy_knowledge"
        self.client = None
        self.collection = None
        self.openai_client = None
        
        # Initialize services
        self.embedding_service = LocalEmbeddingService()
        self.simple_embedding_service = SimpleEmbeddingService()
        self.document_manager = DocumentManager()
        
        # Statistics
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "total_documents_added": 0,
            "last_search": None,
            "embedding_service_available": False,
            "chromadb_available": False
        }
        
        # Initialize OpenAI for embeddings if available
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        self._initialize_database()
    
    async def initialize(self) -> bool:
        """Initialize the RAG service."""
        try:
            logger.info("Initializing RAG Service...")
            
            # Initialize embedding service
            embedding_initialized = await self.embedding_service.initialize()
            if not embedding_initialized:
                logger.warning("Failed to initialize local embedding service, trying simple service")
                embedding_initialized = await self.simple_embedding_service.initialize()
                if embedding_initialized:
                    self.embedding_service = self.simple_embedding_service
            
            self.stats["embedding_service_available"] = embedding_initialized
            
            # Initialize ChromaDB
            self._initialize_database()
            
            # Add local documents to ChromaDB if needed
            await self._sync_local_documents()
            
            logger.info("RAG Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            return False
    
    def _initialize_database(self):
        """Initialize ChromaDB."""
        try:
            # Ensure data directory exists
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "EVY knowledge base"}
            )
            
            logger.info(f"ChromaDB initialized with {self.collection.count()} documents")
            self.stats["chromadb_available"] = True
            
            # Add sample data if empty
            if self.collection.count() == 0:
                self._add_sample_data()
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
            self.stats["chromadb_available"] = False
    
    async def _sync_local_documents(self):
        """Sync local documents with ChromaDB."""
        try:
            # Get all documents from document manager
            doc_stats = self.document_manager.get_statistics()
            local_doc_count = doc_stats["total_documents"]
            chroma_doc_count = self.collection.count() if self.collection else 0
            
            if local_doc_count > 0 and local_doc_count != chroma_doc_count:
                logger.info(f"Syncing {local_doc_count} local documents to ChromaDB")
                
                # Get all categories
                categories = await self.document_manager.get_all_categories()
                
                for category in categories:
                    documents = await self.document_manager.get_documents_by_category(category)
                    
                    for doc in documents:
                        doc_id = doc["id"]
                        text = doc["text"]
                        metadata = {
                            "category": doc.get("category", "general"),
                            "title": doc.get("title", ""),
                            "created_at": doc.get("created_at", ""),
                            "keywords": ",".join(doc.get("keywords", [])),
                            **doc.get("metadata", {})
                        }
                        
                        # Add to ChromaDB
                        try:
                            self.collection.add(
                                documents=[text],
                                ids=[doc_id],
                                metadatas=[metadata]
                            )
                        except Exception as e:
                            logger.warning(f"Failed to add document {doc_id} to ChromaDB: {e}")
                
                logger.info("Local documents synced to ChromaDB")
                
        except Exception as e:
            logger.error(f"Failed to sync local documents: {e}")
    
    def _add_sample_data(self):
        """Add sample knowledge to the database."""
        sample_documents = [
            {
                "id": "doc1",
                "text": "EVY is an SMS-based AI assistant that works offline. It helps people access information without internet.",
                "metadata": {"category": "about", "priority": "high"}
            },
            {
                "id": "doc2",
                "text": "To use EVY, simply send an SMS with your question. You'll receive a response within 15 seconds.",
                "metadata": {"category": "usage", "priority": "high"}
            },
            {
                "id": "doc3",
                "text": "EVY can answer questions, provide local information, and help in emergencies. It runs on solar power.",
                "metadata": {"category": "features", "priority": "medium"}
            },
            {
                "id": "doc4",
                "text": "For emergencies, include words like 'emergency', 'help', or 'urgent' in your message for priority handling.",
                "metadata": {"category": "emergency", "priority": "high"}
            },
            {
                "id": "doc5",
                "text": "EVY respects your privacy. All messages are processed locally and not shared with third parties.",
                "metadata": {"category": "privacy", "priority": "high"}
            },
            {
                "id": "doc6",
                "text": "Weather information is available through local sensors and cached forecasts. Ask 'What's the weather?' for current conditions.",
                "metadata": {"category": "weather", "priority": "medium"}
            },
            {
                "id": "doc7",
                "text": "Local news and events are updated daily. Ask 'What's happening?' or 'Any news?' for the latest information.",
                "metadata": {"category": "news", "priority": "medium"}
            },
            {
                "id": "doc8",
                "text": "Educational content includes basic math, science, and language learning. Ask 'Teach me about...' for lessons.",
                "metadata": {"category": "education", "priority": "medium"}
            }
        ]
        
        try:
            # Add to both document manager and ChromaDB
            for doc in sample_documents:
                # Add to document manager
                asyncio.create_task(self.document_manager.add_document(
                    text=doc["text"],
                    title=doc["metadata"].get("title", ""),
                    category=doc["metadata"]["category"],
                    metadata=doc["metadata"],
                    doc_id=doc["id"]
                ))
                
                # Add to ChromaDB if available
                if self.collection:
                    self.collection.add(
                        documents=[doc["text"]],
                        ids=[doc["id"]],
                        metadatas=[doc["metadata"]]
                    )
            
            logger.info(f"Added {len(sample_documents)} sample documents to knowledge base")
            
        except Exception as e:
            logger.error(f"Failed to add sample data: {e}")
    
    async def search(self, query: RAGQuery) -> RAGResult:
        """Search for relevant documents using hybrid approach."""
        self.stats["total_searches"] += 1
        self.stats["last_search"] = datetime.utcnow().isoformat()
        
        try:
            results = await self._hybrid_search(query)
            self.stats["successful_searches"] += 1
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.stats["failed_searches"] += 1
            return RAGResult(documents=[], scores=[], metadata=[])
    
    async def _hybrid_search(self, query: RAGQuery) -> RAGResult:
        """Perform hybrid search combining vector and text search."""
        vector_results = []
        text_results = []
        
        # Try vector search with ChromaDB if available
        if self.collection and self.stats["chromadb_available"]:
            vector_results = await self._vector_search(query)
        
        # Always try text search with document manager
        text_results = await self._text_search(query)
        
        # Combine and rank results
        return await self._combine_search_results(vector_results, text_results, query.top_k)
    
    async def _vector_search(self, query: RAGQuery) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        try:
            results = self.collection.query(
                query_texts=[query.query],
                n_results=min(query.top_k, 10),
                where=query.filter_metadata if query.filter_metadata else None
            )
            
            documents = results['documents'][0] if results['documents'] else []
            distances = results['distances'][0] if results['distances'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            # Convert to standard format
            vector_results = []
            for i, doc in enumerate(documents):
                vector_results.append({
                    "document": doc,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "score": 1 / (1 + distances[i]) if i < len(distances) else 0.5,
                    "source": "vector"
                })
            
            logger.info(f"Vector search found {len(vector_results)} documents")
            return vector_results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    async def _text_search(self, query: RAGQuery) -> List[Dict[str, Any]]:
        """Perform text-based search."""
        try:
            # Search using document manager
            results = await self.document_manager.search_documents(
                query=query.query,
                category=query.filter_metadata.get('category') if query.filter_metadata else None,
                limit=query.top_k
            )
            
            # Convert to standard format
            text_results = []
            for result in results:
                text_results.append({
                    "document": result["document"]["text"],
                    "metadata": {
                        "category": result["document"].get("category", "general"),
                        "title": result["document"].get("title", ""),
                        "keywords": ",".join(result["document"].get("keywords", [])),
                        **result["document"].get("metadata", {})
                    },
                    "score": result["score"] / 10.0,  # Normalize score
                    "source": "text"
                })
            
            logger.info(f"Text search found {len(text_results)} documents")
            return text_results
            
        except Exception as e:
            logger.error(f"Text search error: {e}")
            return []
    
    async def _combine_search_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        text_results: List[Dict[str, Any]], 
        top_k: int
    ) -> RAGResult:
        """Combine and rank search results."""
        try:
            # Create combined results with deduplication
            combined_results = {}
            
            # Add vector results with higher weight
            for result in vector_results:
                doc_id = hashlib.md5(result["document"].encode()).hexdigest()[:8]
                if doc_id not in combined_results:
                    combined_results[doc_id] = {
                        "document": result["document"],
                        "metadata": result["metadata"],
                        "score": result["score"] * 1.2,  # Boost vector results
                        "sources": [result["source"]]
                    }
                else:
                    # Combine scores from different sources
                    existing = combined_results[doc_id]
                    existing["score"] = max(existing["score"], result["score"] * 1.2)
                    existing["sources"].append(result["source"])
            
            # Add text results
            for result in text_results:
                doc_id = hashlib.md5(result["document"].encode()).hexdigest()[:8]
                if doc_id not in combined_results:
                    combined_results[doc_id] = {
                        "document": result["document"],
                        "metadata": result["metadata"],
                        "score": result["score"],
                        "sources": [result["source"]]
                    }
                else:
                    # Combine scores from different sources
                    existing = combined_results[doc_id]
                    existing["score"] = max(existing["score"], result["score"])
                    existing["sources"].append(result["source"])
            
            # Sort by score and take top results
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x["score"],
                reverse=True
            )[:top_k]
            
            # Extract components for RAGResult
            documents = [result["document"] for result in sorted_results]
            scores = [result["score"] for result in sorted_results]
            metadatas = [result["metadata"] for result in sorted_results]
            
            logger.info(f"Combined search found {len(documents)} unique documents")
            
            return RAGResult(
                documents=documents,
                scores=scores,
                metadata=metadatas
            )
            
        except Exception as e:
            logger.error(f"Failed to combine search results: {e}")
            return RAGResult(documents=[], scores=[], metadata=[])
    
    async def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a document to the knowledge base."""
        try:
            # Add to document manager first
            doc_metadata = metadata or {}
            category = doc_metadata.get("category", "general")
            title = doc_metadata.get("title", "")
            
            await self.document_manager.add_document(
                text=text,
                title=title,
                category=category,
                metadata=doc_metadata,
                doc_id=doc_id
            )
            
            # Add to ChromaDB if available
            if self.collection:
                self.collection.add(
                    documents=[text],
                    ids=[doc_id],
                    metadatas=[doc_metadata]
                )
            
            self.stats["total_documents_added"] += 1
            logger.info(f"Added document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        try:
            doc_stats = self.document_manager.get_statistics()
            embedding_info = self.embedding_service.get_model_info()
            
            chromadb_stats = {
                "status": "unavailable",
                "document_count": 0
            }
            
            if self.collection:
                try:
                    chromadb_stats = {
                        "status": "available",
                        "document_count": self.collection.count(),
                        "collection_name": self.collection_name
                    }
                except Exception as e:
                    chromadb_stats = {"status": "error", "error": str(e)}
            
            return {
                **self.stats,
                "document_manager": doc_stats,
                "chromadb": chromadb_stats,
                "embedding_service": embedding_info,
                "services": {
                    "chromadb_available": self.stats["chromadb_available"],
                    "embedding_service_available": self.stats["embedding_service_available"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"status": "error", "error": str(e)}


# Global service instance
rag_service = RAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("RAG Service starting up...")
    
    # Initialize the service
    if not await rag_service.initialize():
        logger.error("Failed to initialize RAG Service")
        raise RuntimeError("RAG Service initialization failed")
    
    yield
    logger.info("RAG Service shutting down...")
    
    # Cleanup embedding service
    await rag_service.embedding_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title="EVY RAG Service",
    description="Retrieval-Augmented Generation service for EVY system",
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
    stats = rag_service.get_stats()
    return ServiceHealth(
        service_name="rag-service",
        status="healthy",
        version="1.0.0",
        details=stats
    )


@app.post("/search", response_model=RAGResult)
async def search_knowledge(query: RAGQuery):
    """Search the knowledge base."""
    try:
        result = await rag_service.search(query)
        return result
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add")
async def add_document(doc_id: str, text: str, metadata: Dict[str, Any] = None):
    """Add a document to the knowledge base."""
    success = await rag_service.add_document(doc_id, text, metadata)
    if success:
        return {"status": "added", "doc_id": doc_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to add document")


@app.get("/stats")
async def get_statistics():
    """Get comprehensive statistics."""
    return rag_service.get_stats()


@app.get("/categories")
async def get_categories():
    """Get all document categories."""
    categories = await rag_service.document_manager.get_all_categories()
    return {"categories": categories}


@app.get("/documents/category/{category}")
async def get_documents_by_category(category: str):
    """Get documents by category."""
    documents = await rag_service.document_manager.get_documents_by_category(category)
    return {"category": category, "documents": documents}


@app.post("/documents/bulk-add")
async def bulk_add_documents(documents: List[Dict[str, Any]]):
    """Add multiple documents at once."""
    try:
        doc_ids = await rag_service.document_manager.bulk_add_documents(documents)
        
        # Also add to ChromaDB if available
        if rag_service.collection:
            for doc_data, doc_id in zip(documents, doc_ids):
                if doc_id:  # Only if document was successfully added
                    try:
                        rag_service.collection.add(
                            documents=[doc_data.get('text', '')],
                            ids=[doc_id],
                            metadatas=[doc_data.get('metadata', {})]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to add document {doc_id} to ChromaDB: {e}")
        
        return {"status": "added", "doc_ids": doc_ids}
    except Exception as e:
        logger.error(f"Failed to bulk add documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document."""
    try:
        # Remove from document manager
        success = await rag_service.document_manager.delete_document(doc_id)
        
        if success and rag_service.collection:
            try:
                # Remove from ChromaDB
                rag_service.collection.delete(ids=[doc_id])
            except Exception as e:
                logger.warning(f"Failed to delete document {doc_id} from ChromaDB: {e}")
        
        if success:
            return {"status": "deleted", "doc_id": doc_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/export")
async def export_documents(filepath: str):
    """Export all documents to a file."""
    try:
        success = await rag_service.document_manager.export_documents(filepath)
        if success:
            return {"status": "exported", "filepath": filepath}
        else:
            raise HTTPException(status_code=500, detail="Export failed")
    except Exception as e:
        logger.error(f"Failed to export documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/import")
async def import_documents(filepath: str):
    """Import documents from a file."""
    try:
        success = await rag_service.document_manager.import_documents(filepath)
        if success:
            # Sync with ChromaDB
            await rag_service._sync_local_documents()
            return {"status": "imported", "filepath": filepath}
        else:
            raise HTTPException(status_code=500, detail="Import failed")
    except Exception as e:
        logger.error(f"Failed to import documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embedding/test")
async def test_embedding(text: str):
    """Test embedding generation."""
    try:
        embedding = await rag_service.embedding_service.encode_text(text)
        if embedding:
            return {
                "text": text,
                "embedding_dim": len(embedding),
                "embedding": embedding[:10]  # Return first 10 dimensions
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")
    except Exception as e:
        logger.error(f"Failed to test embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/advanced")
async def advanced_search(
    query: str,
    category: Optional[str] = None,
    top_k: int = 5,
    min_score: float = 0.1
):
    """Advanced search with filters."""
    try:
        rag_query = RAGQuery(
            query=query,
            top_k=top_k,
            filter_metadata={"category": category} if category else None
        )
        
        result = await rag_service.search(rag_query)
        
        # Filter by minimum score
        filtered_docs = []
        filtered_scores = []
        filtered_metadata = []
        
        for i, score in enumerate(result.scores):
            if score >= min_score:
                filtered_docs.append(result.documents[i])
                filtered_scores.append(score)
                filtered_metadata.append(result.metadata[i])
        
        return {
            "query": query,
            "category": category,
            "total_found": len(filtered_docs),
            "documents": filtered_docs,
            "scores": filtered_scores,
            "metadata": filtered_metadata
        }
        
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.rag_service_port,
        log_level="info"
    )


