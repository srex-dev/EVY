"""Document manager for local knowledge base."""
import asyncio
import logging
import json
import os
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)


class DocumentManager:
    """Manages local documents and knowledge base."""
    
    def __init__(self, data_dir: str = "/data/evy_knowledge"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Document storage
        self.documents_file = self.data_dir / "documents.json"
        self.categories_file = self.data_dir / "categories.json"
        
        # In-memory storage
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.categories: Set[str] = set()
        
        # Statistics
        self.stats = {
            "total_documents": 0,
            "categories_count": 0,
            "last_updated": None,
            "total_words": 0
        }
        
        self._load_documents()
    
    def _load_documents(self) -> None:
        """Load documents from disk."""
        try:
            if self.documents_file.exists():
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded {len(self.documents)} documents")
            
            if self.categories_file.exists():
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    categories_data = json.load(f)
                    self.categories = set(categories_data.get('categories', []))
                logger.info(f"Loaded {len(self.categories)} categories")
            
            self._update_stats()
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            self.documents = {}
            self.categories = set()
    
    def _save_documents(self) -> None:
        """Save documents to disk."""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
            
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'categories': list(self.categories),
                    'last_updated': datetime.utcnow().isoformat()
                }, f, indent=2)
            
            logger.debug("Documents saved to disk")
            
        except Exception as e:
            logger.error(f"Failed to save documents: {e}")
    
    def _update_stats(self) -> None:
        """Update statistics."""
        self.stats["total_documents"] = len(self.documents)
        self.stats["categories_count"] = len(self.categories)
        self.stats["last_updated"] = datetime.utcnow().isoformat()
        
        # Count total words
        total_words = 0
        for doc in self.documents.values():
            total_words += len(doc.get('text', '').split())
        self.stats["total_words"] = total_words
    
    def _generate_doc_id(self, text: str, title: str = "") -> str:
        """Generate a unique document ID."""
        content = f"{title}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'under',
            'over', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself',
            'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Return top 10 most common keywords
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]
    
    async def add_document(
        self, 
        text: str, 
        title: str = "", 
        category: str = "general",
        metadata: Dict[str, Any] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """Add a document to the knowledge base."""
        try:
            # Generate ID if not provided
            if not doc_id:
                doc_id = self._generate_doc_id(text, title)
            
            # Check if document already exists
            if doc_id in self.documents:
                logger.warning(f"Document {doc_id} already exists, updating")
            
            # Extract keywords
            keywords = self._extract_keywords(text)
            
            # Create document
            document = {
                "id": doc_id,
                "title": title,
                "text": text,
                "category": category,
                "keywords": keywords,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "word_count": len(text.split()),
                "char_count": len(text)
            }
            
            # Add to storage
            self.documents[doc_id] = document
            self.categories.add(category)
            
            # Save to disk
            self._save_documents()
            self._update_stats()
            
            logger.info(f"Added document: {doc_id} ({category})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    async def search_documents(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents by text content."""
        try:
            query_lower = query.lower()
            results = []
            
            for doc_id, doc in self.documents.items():
                # Filter by category if specified
                if category and doc.get('category') != category:
                    continue
                
                # Simple text matching
                text = doc.get('text', '').lower()
                title = doc.get('title', '').lower()
                keywords = [kw.lower() for kw in doc.get('keywords', [])]
                
                # Calculate relevance score
                score = 0
                
                # Title matches are most important
                if query_lower in title:
                    score += 10
                
                # Keyword matches
                for keyword in keywords:
                    if keyword in query_lower or query_lower in keyword:
                        score += 5
                
                # Text content matches
                if query_lower in text:
                    # Count occurrences
                    occurrences = text.count(query_lower)
                    score += occurrences * 2
                
                # Partial word matches
                query_words = query_lower.split()
                for word in query_words:
                    if word in text:
                        score += 1
                
                if score > 0:
                    results.append({
                        "document": doc,
                        "score": score
                    })
            
            # Sort by score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    async def get_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all documents in a category."""
        return [
            doc for doc in self.documents.values() 
            if doc.get('category') == category
        ]
    
    async def get_all_categories(self) -> List[str]:
        """Get all categories."""
        return sorted(list(self.categories))
    
    async def update_document(
        self, 
        doc_id: str, 
        text: Optional[str] = None,
        title: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a document."""
        try:
            if doc_id not in self.documents:
                return False
            
            doc = self.documents[doc_id]
            
            # Update fields
            if text is not None:
                doc['text'] = text
                doc['keywords'] = self._extract_keywords(text)
                doc['word_count'] = len(text.split())
                doc['char_count'] = len(text)
            
            if title is not None:
                doc['title'] = title
            
            if category is not None:
                old_category = doc.get('category')
                doc['category'] = category
                
                # Update categories set
                if old_category and old_category != category:
                    # Check if old category is still used
                    other_docs_with_old_category = [
                        d for d in self.documents.values() 
                        if d.get('category') == old_category and d['id'] != doc_id
                    ]
                    if not other_docs_with_old_category:
                        self.categories.discard(old_category)
                
                self.categories.add(category)
            
            if metadata is not None:
                doc['metadata'].update(metadata)
            
            doc['updated_at'] = datetime.utcnow().isoformat()
            
            # Save changes
            self._save_documents()
            self._update_stats()
            
            logger.info(f"Updated document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        try:
            if doc_id not in self.documents:
                return False
            
            doc = self.documents[doc_id]
            category = doc.get('category')
            
            # Remove document
            del self.documents[doc_id]
            
            # Remove category if no other documents use it
            if category:
                other_docs_with_category = [
                    d for d in self.documents.values() 
                    if d.get('category') == category
                ]
                if not other_docs_with_category:
                    self.categories.discard(category)
            
            # Save changes
            self._save_documents()
            self._update_stats()
            
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def bulk_add_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Add multiple documents at once."""
        doc_ids = []
        
        for doc_data in documents:
            try:
                doc_id = await self.add_document(
                    text=doc_data.get('text', ''),
                    title=doc_data.get('title', ''),
                    category=doc_data.get('category', 'general'),
                    metadata=doc_data.get('metadata'),
                    doc_id=doc_data.get('id')
                )
                doc_ids.append(doc_id)
            except Exception as e:
                logger.error(f"Failed to add document in bulk: {e}")
        
        return doc_ids
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get document statistics."""
        self._update_stats()
        
        # Category breakdown
        category_counts = {}
        for doc in self.documents.values():
            category = doc.get('category', 'uncategorized')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            **self.stats,
            "category_breakdown": category_counts,
            "average_words_per_document": (
                self.stats["total_words"] / max(self.stats["total_documents"], 1)
            )
        }
    
    async def export_documents(self, filepath: str) -> bool:
        """Export all documents to a file."""
        try:
            export_data = {
                "documents": self.documents,
                "categories": list(self.categories),
                "statistics": self.get_statistics(),
                "exported_at": datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.documents)} documents to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export documents: {e}")
            return False
    
    async def import_documents(self, filepath: str) -> bool:
        """Import documents from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            documents = import_data.get('documents', {})
            categories = set(import_data.get('categories', []))
            
            # Add documents
            for doc_id, doc in documents.items():
                self.documents[doc_id] = doc
            
            # Add categories
            self.categories.update(categories)
            
            # Save to disk
            self._save_documents()
            self._update_stats()
            
            logger.info(f"Imported {len(documents)} documents from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import documents: {e}")
            return False
    
    async def cleanup_old_documents(self, days_old: int = 365) -> int:
        """Remove documents older than specified days."""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days_old * 24 * 60 * 60)
            removed_count = 0
            
            doc_ids_to_remove = []
            for doc_id, doc in self.documents.items():
                try:
                    created_at = datetime.fromisoformat(doc.get('created_at', ''))
                    if created_at.timestamp() < cutoff_date:
                        doc_ids_to_remove.append(doc_id)
                except ValueError:
                    # Invalid date format, skip
                    continue
            
            # Remove old documents
            for doc_id in doc_ids_to_remove:
                if await self.delete_document(doc_id):
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old documents")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old documents: {e}")
            return 0
