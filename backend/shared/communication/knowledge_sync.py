"""
Knowledge Synchronization System
Handles data flow between bigEVY (central) and lilEVY (edge) nodes
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSource(Enum):
    BIGEVY = "bigevy"
    LILEVY = "lilevy"
    EXTERNAL_API = "external_api"
    USER_INPUT = "user_input"

@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry for synchronization"""
    id: str
    title: str
    text: str
    category: str
    metadata: Dict[str, Any]
    source: DataSource
    priority: str
    location_specific: bool
    created_at: datetime
    updated_at: datetime
    version: int
    checksum: str

@dataclass
class SyncRequest:
    """Synchronization request between nodes"""
    request_id: str
    source_node: str
    target_node: str
    sync_type: str  # "full", "incremental", "emergency", "location_update"
    priority: str
    entries: List[KnowledgeEntry]
    created_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class SyncResponse:
    """Response to synchronization request"""
    request_id: str
    status: SyncStatus
    message: str
    processed_entries: int
    failed_entries: int
    errors: List[str]
    completed_at: datetime

class KnowledgeSyncManager:
    """Manages knowledge synchronization between bigEVY and lilEVY nodes"""
    
    def __init__(self, node_id: str, node_type: str):
        self.node_id = node_id
        self.node_type = node_type  # "bigevy" or "lilevy"
        self.sync_queue = asyncio.Queue()
        self.active_syncs = {}
        self.sync_history = []
        
        # Configuration
        self.sync_intervals = {
            "emergency": 300,      # 5 minutes
            "critical": 1800,      # 30 minutes
            "high": 3600,         # 1 hour
            "medium": 14400,      # 4 hours
            "low": 86400          # 24 hours
        }
        
        # Data sources and their update frequencies
        self.data_sources = {
            "weather_alerts": {"frequency": 300, "priority": "critical"},
            "emergency_contacts": {"frequency": 86400, "priority": "medium"},
            "government_services": {"frequency": 14400, "priority": "medium"},
            "healthcare_services": {"frequency": 3600, "priority": "high"},
            "utility_services": {"frequency": 3600, "priority": "high"},
            "transportation": {"frequency": 1800, "priority": "medium"},
            "community_events": {"frequency": 3600, "priority": "low"},
            "local_businesses": {"frequency": 14400, "priority": "low"}
        }
    
    async def collect_bigevy_data(self) -> List[KnowledgeEntry]:
        """Collect data from various sources for bigEVY"""
        logger.info("Collecting data from bigEVY sources...")
        
        collected_entries = []
        
        # Weather data collection
        weather_entries = await self._collect_weather_data()
        collected_entries.extend(weather_entries)
        
        # Government services data
        gov_entries = await self._collect_government_data()
        collected_entries.extend(gov_entries)
        
        # Healthcare services data
        health_entries = await self._collect_healthcare_data()
        collected_entries.extend(health_entries)
        
        # Utility services data
        utility_entries = await self._collect_utility_data()
        collected_entries.extend(utility_entries)
        
        # Transportation data
        transport_entries = await self._collect_transportation_data()
        collected_entries.extend(transport_entries)
        
        # Community events and local businesses
        community_entries = await self._collect_community_data()
        collected_entries.extend(community_entries)
        
        logger.info(f"Collected {len(collected_entries)} entries from bigEVY sources")
        return collected_entries
    
    async def _collect_weather_data(self) -> List[KnowledgeEntry]:
        """Collect weather data from National Weather Service and other sources"""
        entries = []
        
        try:
            # National Weather Service API
            import requests
            
            # For Wichita, KS coordinates
            lat, lon = 37.6872, -97.3301
            alerts_url = f"https://api.weather.gov/alerts?point={lat},{lon}"
            
            response = requests.get(alerts_url, headers={"User-Agent": "EVY-Wichita/1.0"})
            if response.status_code == 200:
                alerts_data = response.json()
                
                for alert in alerts_data.get('features', []):
                    alert_props = alert['properties']
                    
                    entry = KnowledgeEntry(
                        id=f"weather_alert_{alert_props.get('id', 'unknown')}",
                        title=f"Weather Alert: {alert_props.get('event', 'Weather Warning')}",
                        text=f"Weather Alert: {alert_props.get('headline', 'Active weather alert')}. {alert_props.get('description', '')[:200]}...",
                        category="weather_safety",
                        metadata={
                            "priority": "critical",
                            "source": "national_weather_service",
                            "alert_type": alert_props.get('event'),
                            "severity": alert_props.get('severity'),
                            "location": "Wichita, KS",
                            "expires": alert_props.get('expires')
                        },
                        source=DataSource.EXTERNAL_API,
                        priority="critical",
                        location_specific=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        version=1,
                        checksum=self._calculate_checksum(alert_props)
                    )
                    entries.append(entry)
            
            logger.info(f"Collected {len(entries)} weather alerts")
            
        except Exception as e:
            logger.error(f"Failed to collect weather data: {e}")
        
        return entries
    
    async def _collect_government_data(self) -> List[KnowledgeEntry]:
        """Collect government services data"""
        entries = []
        
        # Wichita-specific government services
        gov_services = [
            {
                "title": "Wichita City Hall Services",
                "text": "Wichita City Hall: 455 N Main St, Wichita, KS 67202. Phone: (316) 268-4000. Hours: Mon-Fri 8AM-5PM. Services: permits, licenses, city services.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_city_hall",
                    "service": "city_hall",
                    "location": "Wichita, KS"
                }
            },
            {
                "title": "Sedgwick County Services",
                "text": "Sedgwick County Courthouse: 525 N Main St, Wichita, KS 67203. Phone: (316) 660-9100. Hours: Mon-Fri 8AM-5PM. Services: court, records, licenses.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "sedgwick_courthouse",
                    "service": "county_services",
                    "location": "Sedgwick County, KS"
                }
            }
        ]
        
        for service in gov_services:
            entry = KnowledgeEntry(
                id=f"gov_{hashlib.md5(service['title'].encode()).hexdigest()[:8]}",
                title=service['title'],
                text=service['text'],
                category=service['category'],
                metadata=service['metadata'],
                source=DataSource.BIGEVY,
                priority=service['metadata']['priority'],
                location_specific=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(service)
            )
            entries.append(entry)
        
        logger.info(f"Collected {len(entries)} government services")
        return entries
    
    async def _collect_healthcare_data(self) -> List[KnowledgeEntry]:
        """Collect healthcare services data"""
        entries = []
        
        # Wichita healthcare services
        health_services = [
            {
                "title": "Wichita Emergency Rooms",
                "text": "Major hospitals: Via Christi St Francis (929 N St Francis St), Wesley Medical Center (550 N Hillside St), Ascension Via Christi St Teresa (418 S Belmont St). All have 24/7 ER.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_hospitals",
                    "service": "hospital",
                    "location": "Wichita, KS"
                }
            },
            {
                "title": "Wichita Mental Health Crisis",
                "text": "Mental health crisis: Comcare of Sedgwick County (316) 660-7540. 24/7 crisis intervention. National Suicide Prevention: 988. You are not alone.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_mental_health",
                    "service": "crisis_line",
                    "phone": "(316) 660-7540"
                }
            }
        ]
        
        for service in health_services:
            entry = KnowledgeEntry(
                id=f"health_{hashlib.md5(service['title'].encode()).hexdigest()[:8]}",
                title=service['title'],
                text=service['text'],
                category=service['category'],
                metadata=service['metadata'],
                source=DataSource.BIGEVY,
                priority=service['metadata']['priority'],
                location_specific=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(service)
            )
            entries.append(entry)
        
        logger.info(f"Collected {len(entries)} healthcare services")
        return entries
    
    async def _collect_utility_data(self) -> List[KnowledgeEntry]:
        """Collect utility services data"""
        entries = []
        
        # Wichita utility services
        utility_services = [
            {
                "title": "Evergy Power Outages - Wichita",
                "text": "Evergy power outages: Report at 1-800-EVERGY (383-7491) or online. Wichita area served by Evergy. Check outage map for updates and restoration times.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "evergy_wichita",
                    "utility": "power",
                    "location": "Wichita, KS"
                }
            },
            {
                "title": "Wichita Water Service",
                "text": "Wichita Water: Emergency (316) 303-8000, Customer service (316) 303-8000. Address: 119 E 1st St, Wichita, KS 67202. Report water emergencies immediately.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_water",
                    "utility": "water",
                    "location": "Wichita, KS"
                }
            }
        ]
        
        for service in utility_services:
            entry = KnowledgeEntry(
                id=f"utility_{hashlib.md5(service['title'].encode()).hexdigest()[:8]}",
                title=service['title'],
                text=service['text'],
                category=service['category'],
                metadata=service['metadata'],
                source=DataSource.BIGEVY,
                priority=service['metadata']['priority'],
                location_specific=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(service)
            )
            entries.append(entry)
        
        logger.info(f"Collected {len(entries)} utility services")
        return entries
    
    async def _collect_transportation_data(self) -> List[KnowledgeEntry]:
        """Collect transportation data"""
        entries = []
        
        # Wichita transportation services
        transport_services = [
            {
                "title": "Wichita Transit (Wichita Area Rapid Transit)",
                "text": "Wichita Transit: Phone (316) 265-7221. Fixed route buses, paratransit services. Fares: $1.75 adult, $0.85 reduced. Routes cover Wichita area.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_transit",
                    "service": "public_transit",
                    "location": "Wichita, KS"
                }
            }
        ]
        
        for service in transport_services:
            entry = KnowledgeEntry(
                id=f"transport_{hashlib.md5(service['title'].encode()).hexdigest()[:8]}",
                title=service['title'],
                text=service['text'],
                category=service['category'],
                metadata=service['metadata'],
                source=DataSource.BIGEVY,
                priority=service['metadata']['priority'],
                location_specific=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(service)
            )
            entries.append(entry)
        
        logger.info(f"Collected {len(entries)} transportation services")
        return entries
    
    async def _collect_community_data(self) -> List[KnowledgeEntry]:
        """Collect community events and local business data"""
        entries = []
        
        # This would integrate with various APIs for community data
        # For now, we'll add some static Wichita community resources
        
        community_services = [
            {
                "title": "Wichita Food Bank",
                "text": "Kansas Food Bank: 1919 E Douglas Ave, Wichita, KS 67211. Phone: (316) 265-3663. Emergency food assistance for those in need.",
                "category": "local_info",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_food_bank",
                    "service": "food_assistance",
                    "location": "Wichita, KS"
                }
            }
        ]
        
        for service in community_services:
            entry = KnowledgeEntry(
                id=f"community_{hashlib.md5(service['title'].encode()).hexdigest()[:8]}",
                title=service['title'],
                text=service['text'],
                category=service['category'],
                metadata=service['metadata'],
                source=DataSource.BIGEVY,
                priority=service['metadata']['priority'],
                location_specific=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                checksum=self._calculate_checksum(service)
            )
            entries.append(entry)
        
        logger.info(f"Collected {len(entries)} community services")
        return entries
    
    async def sync_to_lilevy(self, lilevy_node_id: str, entries: List[KnowledgeEntry], 
                           sync_type: str = "incremental") -> SyncResponse:
        """Sync knowledge entries to a lilEVY node"""
        request_id = f"sync_{self.node_id}_{lilevy_node_id}_{int(datetime.now().timestamp())}"
        
        sync_request = SyncRequest(
            request_id=request_id,
            source_node=self.node_id,
            target_node=lilevy_node_id,
            sync_type=sync_type,
            priority="high",
            entries=entries,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        logger.info(f"Starting sync to lilEVY node {lilevy_node_id}: {len(entries)} entries")
        
        try:
            # Send sync request to lilEVY node
            response = await self._send_sync_request(sync_request)
            
            # Track the sync
            self.active_syncs[request_id] = sync_request
            self.sync_history.append({
                "request_id": request_id,
                "timestamp": datetime.now(),
                "entries_count": len(entries),
                "status": "completed"
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return SyncResponse(
                request_id=request_id,
                status=SyncStatus.FAILED,
                message=str(e),
                processed_entries=0,
                failed_entries=len(entries),
                errors=[str(e)],
                completed_at=datetime.now()
            )
    
    async def _send_sync_request(self, sync_request: SyncRequest) -> SyncResponse:
        """Send synchronization request to target node"""
        # This would integrate with the actual node communication system
        # For now, we'll simulate the response
        
        processed_entries = 0
        failed_entries = 0
        errors = []
        
        for entry in sync_request.entries:
            try:
                # Simulate processing the entry
                await asyncio.sleep(0.01)  # Simulate network delay
                processed_entries += 1
            except Exception as e:
                failed_entries += 1
                errors.append(f"Failed to process {entry.id}: {str(e)}")
        
        return SyncResponse(
            request_id=sync_request.request_id,
            status=SyncStatus.COMPLETED,
            message=f"Successfully synced {processed_entries} entries",
            processed_entries=processed_entries,
            failed_entries=failed_entries,
            errors=errors,
            completed_at=datetime.now()
        )
    
    async def schedule_periodic_sync(self):
        """Schedule periodic synchronization based on data source priorities"""
        logger.info("Starting periodic synchronization scheduler...")
        
        while True:
            try:
                # Check each data source for updates
                for source_name, config in self.data_sources.items():
                    last_sync = self._get_last_sync_time(source_name)
                    next_sync = last_sync + timedelta(seconds=config['frequency'])
                    
                    if datetime.now() >= next_sync:
                        logger.info(f"Triggering sync for {source_name}")
                        await self._trigger_source_sync(source_name, config['priority'])
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in periodic sync scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _trigger_source_sync(self, source_name: str, priority: str):
        """Trigger synchronization for a specific data source"""
        try:
            # Collect data from the source
            if source_name == "weather_alerts":
                entries = await self._collect_weather_data()
            elif source_name == "government_services":
                entries = await self._collect_government_data()
            elif source_name == "healthcare_services":
                entries = await self._collect_healthcare_data()
            elif source_name == "utility_services":
                entries = await self._collect_utility_data()
            elif source_name == "transportation":
                entries = await self._collect_transportation_data()
            elif source_name == "community_events":
                entries = await self._collect_community_data()
            else:
                logger.warning(f"Unknown data source: {source_name}")
                return
            
            # Sync to all connected lilEVY nodes
            if entries:
                # This would get actual lilEVY node IDs from the node registry
                lilevy_nodes = ["wichita-lilevy-001", "wichita-lilevy-002"]  # Example
                
                for node_id in lilevy_nodes:
                    await self.sync_to_lilevy(node_id, entries, "incremental")
                
                # Update last sync time
                self._update_last_sync_time(source_name)
                
        except Exception as e:
            logger.error(f"Failed to sync {source_name}: {e}")
    
    def _get_last_sync_time(self, source_name: str) -> datetime:
        """Get the last synchronization time for a data source"""
        # This would be stored in a database or cache
        # For now, return a default time
        return datetime.now() - timedelta(hours=24)
    
    def _update_last_sync_time(self, source_name: str):
        """Update the last synchronization time for a data source"""
        # This would update a database or cache
        logger.info(f"Updated last sync time for {source_name}")
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def emergency_sync(self, lilevy_node_id: str, critical_data: List[KnowledgeEntry]):
        """Perform emergency synchronization with high priority"""
        logger.info(f"Emergency sync to {lilevy_node_id}: {len(critical_data)} critical entries")
        
        # Emergency sync bypasses normal scheduling
        response = await self.sync_to_lilevy(lilevy_node_id, critical_data, "emergency")
        
        if response.status == SyncStatus.COMPLETED:
            logger.info(f"Emergency sync completed: {response.processed_entries} entries")
        else:
            logger.error(f"Emergency sync failed: {response.message}")
        
        return response
    
    def get_sync_status(self, request_id: str) -> Optional[Dict]:
        """Get the status of a synchronization request"""
        # Check active syncs
        if request_id in self.active_syncs:
            return {
                "request_id": request_id,
                "status": "in_progress",
                "created_at": self.active_syncs[request_id].created_at,
                "entries_count": len(self.active_syncs[request_id].entries)
            }
        
        # Check sync history
        for sync in self.sync_history:
            if sync["request_id"] == request_id:
                return sync
        
        return None
    
    def get_sync_statistics(self) -> Dict:
        """Get synchronization statistics"""
        total_syncs = len(self.sync_history)
        successful_syncs = sum(1 for sync in self.sync_history if sync["status"] == "completed")
        total_entries = sum(sync["entries_count"] for sync in self.sync_history)
        
        return {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "failed_syncs": total_syncs - successful_syncs,
            "total_entries_synced": total_entries,
            "active_syncs": len(self.active_syncs),
            "last_sync": self.sync_history[-1]["timestamp"] if self.sync_history else None
        }

# Example usage and testing
async def main():
    """Example usage of the knowledge sync system"""
    
    # Create a bigEVY sync manager
    bigevy_sync = KnowledgeSyncManager("wichita-bigevy-001", "bigevy")
    
    # Start periodic synchronization
    sync_task = asyncio.create_task(bigevy_sync.schedule_periodic_sync())
    
    # Collect data from various sources
    all_data = await bigevy_sync.collect_bigevy_data()
    print(f"Collected {len(all_data)} entries from bigEVY sources")
    
    # Sync to lilEVY node
    response = await bigevy_sync.sync_to_lilevy("wichita-lilevy-001", all_data[:5])
    print(f"Sync response: {response.status.value}, {response.processed_entries} entries processed")
    
    # Get statistics
    stats = bigevy_sync.get_sync_statistics()
    print(f"Sync statistics: {stats}")
    
    # Cancel the periodic sync task
    sync_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
