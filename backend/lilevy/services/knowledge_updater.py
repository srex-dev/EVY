"""
lilEVY Knowledge Updater Service
Receives and processes knowledge updates from bigEVY
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib

from backend.shared.communication.knowledge_sync import (
    KnowledgeEntry, SyncRequest, SyncResponse, SyncStatus, DataSource
)

logger = logging.getLogger(__name__)

@dataclass
class LocalKnowledgeEntry:
    """Local knowledge entry stored on lilEVY"""
    id: str
    title: str
    text: str
    category: str
    metadata: Dict[str, Any]
    source: str
    priority: str
    location_specific: bool
    created_at: datetime
    updated_at: datetime
    version: int
    checksum: str
    last_accessed: Optional[datetime] = None
    access_count: int = 0

class KnowledgeUpdater:
    """Manages knowledge updates on lilEVY nodes"""
    
    def __init__(self, node_id: str, rag_service_url: str = "http://localhost:8004"):
        self.node_id = node_id
        self.rag_service_url = rag_service_url
        self.local_knowledge = {}  # id -> LocalKnowledgeEntry
        self.update_queue = asyncio.Queue()
        self.last_full_sync = None
        self.sync_status = {}
        
        # Configuration
        self.max_local_entries = 10000
        self.emergency_priority_entries = 1000  # Reserve space for emergency entries
        self.cleanup_threshold = 0.9  # Cleanup when 90% full
        
        # Update frequencies for different priorities
        self.update_frequencies = {
            "critical": 300,      # 5 minutes
            "high": 1800,         # 30 minutes
            "medium": 3600,       # 1 hour
            "low": 14400          # 4 hours
        }
    
    async def process_sync_request(self, sync_request: SyncRequest) -> SyncResponse:
        """Process a synchronization request from bigEVY"""
        logger.info(f"Processing sync request {sync_request.request_id}: {len(sync_request.entries)} entries")
        
        processed_entries = 0
        failed_entries = 0
        errors = []
        
        try:
            # Process each entry in the sync request
            for entry in sync_request.entries:
                try:
                    await self._process_knowledge_entry(entry)
                    processed_entries += 1
                except Exception as e:
                    failed_entries += 1
                    error_msg = f"Failed to process entry {entry.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Update sync status
            self.sync_status[sync_request.request_id] = {
                "status": "completed",
                "processed": processed_entries,
                "failed": failed_entries,
                "timestamp": datetime.now()
            }
            
            # Cleanup if needed
            if len(self.local_knowledge) > self.max_local_entries * self.cleanup_threshold:
                await self._cleanup_old_entries()
            
            logger.info(f"Sync completed: {processed_entries} processed, {failed_entries} failed")
            
            return SyncResponse(
                request_id=sync_request.request_id,
                status=SyncStatus.COMPLETED,
                message=f"Successfully processed {processed_entries} entries",
                processed_entries=processed_entries,
                failed_entries=failed_entries,
                errors=errors,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Sync request processing failed: {e}")
            return SyncResponse(
                request_id=sync_request.request_id,
                status=SyncStatus.FAILED,
                message=f"Sync processing failed: {str(e)}",
                processed_entries=processed_entries,
                failed_entries=failed_entries,
                errors=errors + [str(e)],
                completed_at=datetime.now()
            )
    
    async def _process_knowledge_entry(self, entry: KnowledgeEntry):
        """Process a single knowledge entry"""
        
        # Check if entry already exists
        existing_entry = self.local_knowledge.get(entry.id)
        
        if existing_entry:
            # Check if update is needed
            if existing_entry.checksum != entry.checksum or existing_entry.version < entry.version:
                logger.info(f"Updating existing entry: {entry.id}")
                await self._update_existing_entry(existing_entry, entry)
            else:
                logger.debug(f"Entry {entry.id} is already up to date")
        else:
            # Add new entry
            logger.info(f"Adding new entry: {entry.id}")
            await self._add_new_entry(entry)
    
    async def _add_new_entry(self, entry: KnowledgeEntry):
        """Add a new knowledge entry to local storage"""
        
        # Check storage capacity
        if len(self.local_knowledge) >= self.max_local_entries:
            await self._cleanup_old_entries()
        
        # Create local entry
        local_entry = LocalKnowledgeEntry(
            id=entry.id,
            title=entry.title,
            text=entry.text,
            category=entry.category,
            metadata=entry.metadata,
            source=entry.source.value,
            priority=entry.priority,
            location_specific=entry.location_specific,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            version=entry.version,
            checksum=entry.checksum
        )
        
        # Store locally
        self.local_knowledge[entry.id] = local_entry
        
        # Add to RAG service
        await self._add_to_rag_service(local_entry)
        
        logger.info(f"Added entry {entry.id} to local knowledge base")
    
    async def _update_existing_entry(self, existing_entry: LocalKnowledgeEntry, new_entry: KnowledgeEntry):
        """Update an existing knowledge entry"""
        
        # Update local entry
        existing_entry.title = new_entry.title
        existing_entry.text = new_entry.text
        existing_entry.category = new_entry.category
        existing_entry.metadata = new_entry.metadata
        existing_entry.priority = new_entry.priority
        existing_entry.updated_at = new_entry.updated_at
        existing_entry.version = new_entry.version
        existing_entry.checksum = new_entry.checksum
        
        # Update in RAG service
        await self._update_in_rag_service(existing_entry)
        
        logger.info(f"Updated entry {new_entry.id} in local knowledge base")
    
    async def _add_to_rag_service(self, entry: LocalKnowledgeEntry):
        """Add entry to the local RAG service"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": entry.text,
                    "metadata": {
                        **entry.metadata,
                        "title": entry.title,
                        "category": entry.category,
                        "priority": entry.priority,
                        "source": entry.source,
                        "entry_id": entry.id,
                        "version": entry.version
                    }
                }
                
                async with session.post(f"{self.rag_service_url}/add", json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Added entry {entry.id} to RAG service")
                    else:
                        logger.error(f"Failed to add entry {entry.id} to RAG service: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error adding entry {entry.id} to RAG service: {e}")
    
    async def _update_in_rag_service(self, entry: LocalKnowledgeEntry):
        """Update entry in the local RAG service"""
        try:
            import aiohttp
            
            # For updates, we might need to remove and re-add, or use an update endpoint
            # This depends on the RAG service implementation
            async with aiohttp.ClientSession() as session:
                # Try to update first (if RAG service supports it)
                payload = {
                    "entry_id": entry.id,
                    "text": entry.text,
                    "metadata": {
                        **entry.metadata,
                        "title": entry.title,
                        "category": entry.category,
                        "priority": entry.priority,
                        "source": entry.source,
                        "version": entry.version
                    }
                }
                
                # This would be an update endpoint if available
                async with session.put(f"{self.rag_service_url}/update/{entry.id}", json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Updated entry {entry.id} in RAG service")
                    else:
                        # Fallback: remove and re-add
                        await self._remove_from_rag_service(entry.id)
                        await self._add_to_rag_service(entry)
                        
        except Exception as e:
            logger.error(f"Error updating entry {entry.id} in RAG service: {e}")
    
    async def _remove_from_rag_service(self, entry_id: str):
        """Remove entry from the local RAG service"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(f"{self.rag_service_url}/documents/{entry_id}") as response:
                    if response.status == 200:
                        logger.debug(f"Removed entry {entry_id} from RAG service")
                    else:
                        logger.error(f"Failed to remove entry {entry_id} from RAG service: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error removing entry {entry_id} from RAG service: {e}")
    
    async def _cleanup_old_entries(self):
        """Clean up old, unused entries to make space"""
        logger.info("Starting knowledge base cleanup...")
        
        # Sort entries by priority and last access
        entries_to_cleanup = []
        
        for entry_id, entry in self.local_knowledge.items():
            # Skip critical entries
            if entry.priority == "critical":
                continue
            
            # Calculate cleanup score (lower is more likely to be cleaned up)
            cleanup_score = 0
            
            # Priority weight (higher priority = lower score)
            priority_weights = {"high": 1, "medium": 2, "low": 3}
            cleanup_score += priority_weights.get(entry.priority, 3)
            
            # Age weight (newer = lower score)
            age_days = (datetime.now() - entry.updated_at).days
            cleanup_score += age_days * 0.1
            
            # Access count weight (more accessed = lower score)
            cleanup_score -= entry.access_count * 0.1
            
            entries_to_cleanup.append((entry_id, cleanup_score))
        
        # Sort by cleanup score (highest scores first)
        entries_to_cleanup.sort(key=lambda x: x[1], reverse=True)
        
        # Remove entries until we're under the threshold
        target_size = int(self.max_local_entries * 0.8)  # Clean to 80% capacity
        current_size = len(self.local_knowledge)
        
        entries_removed = 0
        for entry_id, _ in entries_to_cleanup:
            if current_size - entries_removed <= target_size:
                break
            
            # Remove from local storage
            if entry_id in self.local_knowledge:
                await self._remove_from_rag_service(entry_id)
                del self.local_knowledge[entry_id]
                entries_removed += 1
        
        logger.info(f"Cleanup completed: removed {entries_removed} entries")
    
    async def emergency_update(self, critical_entries: List[KnowledgeEntry]):
        """Process emergency updates with highest priority"""
        logger.info(f"Processing emergency update: {len(critical_entries)} critical entries")
        
        # Emergency updates bypass normal storage limits
        for entry in critical_entries:
            try:
                # Force update even if storage is full
                await self._process_knowledge_entry(entry)
            except Exception as e:
                logger.error(f"Failed to process emergency entry {entry.id}: {e}")
    
    def get_knowledge_statistics(self) -> Dict:
        """Get statistics about the local knowledge base"""
        total_entries = len(self.local_knowledge)
        
        # Count by priority
        priority_counts = {}
        for entry in self.local_knowledge.values():
            priority_counts[entry.priority] = priority_counts.get(entry.priority, 0) + 1
        
        # Count by category
        category_counts = {}
        for entry in self.local_knowledge.values():
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1
        
        # Count by source
        source_counts = {}
        for entry in self.local_knowledge.values():
            source_counts[entry.source] = source_counts.get(entry.source, 0) + 1
        
        return {
            "total_entries": total_entries,
            "max_capacity": self.max_local_entries,
            "utilization_percent": (total_entries / self.max_local_entries) * 100,
            "priority_breakdown": priority_counts,
            "category_breakdown": category_counts,
            "source_breakdown": source_counts,
            "last_full_sync": self.last_full_sync,
            "active_syncs": len(self.sync_status)
        }
    
    def get_entry_by_id(self, entry_id: str) -> Optional[LocalKnowledgeEntry]:
        """Get a knowledge entry by ID"""
        entry = self.local_knowledge.get(entry_id)
        if entry:
            # Update access statistics
            entry.last_accessed = datetime.now()
            entry.access_count += 1
        return entry
    
    async def search_local_knowledge(self, query: str, category: Optional[str] = None) -> List[LocalKnowledgeEntry]:
        """Search local knowledge base"""
        results = []
        
        query_lower = query.lower()
        
        for entry in self.local_knowledge.values():
            # Skip if category filter doesn't match
            if category and entry.category != category:
                continue
            
            # Simple text search
            if (query_lower in entry.title.lower() or 
                query_lower in entry.text.lower() or 
                query_lower in entry.category.lower()):
                
                results.append(entry)
                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1
        
        # Sort by priority and relevance
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        results.sort(key=lambda x: (priority_order.get(x.priority, 4), -x.access_count))
        
        return results
    
    async def start_update_listener(self):
        """Start listening for knowledge updates from bigEVY"""
        logger.info("Starting knowledge update listener...")
        
        # This would integrate with the actual communication system
        # For now, we'll simulate periodic updates
        
        while True:
            try:
                # Wait for updates in the queue
                if not self.update_queue.empty():
                    sync_request = await self.update_queue.get()
                    await self.process_sync_request(sync_request)
                else:
                    # Check for pending updates (this would be from network)
                    await asyncio.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error in update listener: {e}")
                await asyncio.sleep(60)
    
    def queue_sync_request(self, sync_request: SyncRequest):
        """Queue a sync request for processing"""
        self.update_queue.put_nowait(sync_request)
        logger.info(f"Queued sync request {sync_request.request_id}")

# Example usage
async def main():
    """Example usage of the knowledge updater"""
    
    # Create a lilEVY knowledge updater
    updater = KnowledgeUpdater("wichita-lilevy-001")
    
    # Start the update listener
    listener_task = asyncio.create_task(updater.start_update_listener())
    
    # Get statistics
    stats = updater.get_knowledge_statistics()
    print(f"Knowledge base statistics: {stats}")
    
    # Search local knowledge
    results = await updater.search_local_knowledge("emergency")
    print(f"Found {len(results)} emergency-related entries")
    
    # Cancel the listener task
    listener_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
