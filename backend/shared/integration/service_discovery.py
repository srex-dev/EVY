"""Service Discovery and Health Checks

Lightweight service discovery and health monitoring for EVY services.
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Service information"""
    name: str
    url: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    error_count: int = 0
    consecutive_failures: int = 0
    metadata: Dict[str, any] = field(default_factory=dict)


class ServiceRegistry:
    """Lightweight service registry"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5.0  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
    
    def register(
        self,
        name: str,
        url: str,
        metadata: Optional[Dict[str, any]] = None
    ) -> None:
        """Register a service"""
        self.services[name] = ServiceInfo(
            name=name,
            url=url,
            metadata=metadata or {}
        )
        logger.info(f"Registered service: {name} at {url}")
    
    def unregister(self, name: str) -> None:
        """Unregister a service"""
        if name in self.services:
            del self.services[name]
            logger.info(f"Unregistered service: {name}")
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        return self.services.get(name)
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        return list(self.services.values())
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """Get all healthy services"""
        return [
            s for s in self.services.values()
            if s.status == ServiceStatus.HEALTHY
        ]
    
    async def check_health(self, name: str) -> bool:
        """Check health of a specific service"""
        service = self.services.get(name)
        if not service:
            logger.warning(f"Service not found: {name}")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                start_time = datetime.utcnow()
                response = await client.get(f"{service.url}/health")
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    service.status = ServiceStatus.HEALTHY
                    service.response_time_ms = response_time
                    service.last_check = datetime.utcnow()
                    service.consecutive_failures = 0
                    return True
                else:
                    service.status = ServiceStatus.UNHEALTHY
                    service.consecutive_failures += 1
                    service.error_count += 1
                    return False
                    
        except httpx.TimeoutException:
            service.status = ServiceStatus.UNREACHABLE
            service.consecutive_failures += 1
            service.error_count += 1
            logger.warning(f"Service {name} timeout")
            return False
        except Exception as e:
            service.status = ServiceStatus.UNREACHABLE
            service.consecutive_failures += 1
            service.error_count += 1
            logger.error(f"Service {name} health check failed: {e}")
            return False
    
    async def check_all_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        results = {}
        tasks = [
            self.check_health(name) for name in self.services.keys()
        ]
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.services.keys(), health_results):
            if isinstance(result, Exception):
                logger.error(f"Health check error for {name}: {result}")
                results[name] = False
            else:
                results[name] = result
        
        return results
    
    async def start_health_checks(self) -> None:
        """Start periodic health checks"""
        if self._running:
            logger.warning("Health checks already running")
            return
        
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started health check monitoring")
    
    async def stop_health_checks(self) -> None:
        """Stop periodic health checks"""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped health check monitoring")
    
    async def _health_check_loop(self) -> None:
        """Health check loop"""
        while self._running:
            try:
                await self.check_all_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    def get_service_stats(self) -> Dict[str, any]:
        """Get statistics about all services"""
        total = len(self.services)
        healthy = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        unhealthy = sum(1 for s in self.services.values() if s.status == ServiceStatus.UNHEALTHY)
        unreachable = sum(1 for s in self.services.values() if s.status == ServiceStatus.UNREACHABLE)
        
        return {
            'total_services': total,
            'healthy_services': healthy,
            'unhealthy_services': unhealthy,
            'unreachable_services': unreachable,
            'services': {
                name: {
                    'status': service.status.value,
                    'response_time_ms': service.response_time_ms,
                    'error_count': service.error_count,
                    'consecutive_failures': service.consecutive_failures,
                    'last_check': service.last_check.isoformat() if service.last_check else None,
                }
                for name, service in self.services.items()
            }
        }


# Global service registry instance
_service_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """Get or create global service registry"""
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry()
    return _service_registry


async def initialize_service_discovery(config: Dict[str, any]) -> ServiceRegistry:
    """Initialize service discovery with default services"""
    registry = get_service_registry()
    
    # Register default services from config
    default_services = {
        'sms_gateway': config.get('sms_gateway_url', 'http://localhost:8001'),
        'message_router': config.get('message_router_url', 'http://localhost:8002'),
        'llm_service': config.get('llm_service_url', 'http://localhost:8003'),
        'rag_service': config.get('rag_service_url', 'http://localhost:8004'),
        'privacy_filter': config.get('privacy_filter_url', 'http://localhost:8005'),
    }
    
    for name, url in default_services.items():
        registry.register(name, url)
    
    # Start health checks
    await registry.start_health_checks()
    
    logger.info(f"Service discovery initialized with {len(default_services)} services")
    return registry

