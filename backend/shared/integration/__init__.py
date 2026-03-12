"""Service Integration Module

Provides integration between Rust and Python services, service discovery,
and end-to-end message flow.
"""

from backend.shared.integration.rust_services import (
    RustSMSService,
    RustCompressionService,
    RustMessageRouterService,
    RustServicesManager,
)

from backend.shared.integration.service_discovery import (
    ServiceRegistry,
    ServiceStatus,
    ServiceInfo,
    get_service_registry,
    initialize_service_discovery,
)

__all__ = [
    'RustSMSService',
    'RustCompressionService',
    'RustMessageRouterService',
    'RustServicesManager',
    'ServiceRegistry',
    'ServiceStatus',
    'ServiceInfo',
    'get_service_registry',
    'initialize_service_discovery',
]

