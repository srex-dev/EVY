# Service Integration Architecture

## Overview

This document describes the integration architecture for EVY services, including Rust-Python integration, service discovery, and end-to-end message flow.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              EVY Service Integration Architecture            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                     │
│  │ SMS Gateway  │───▶│   Message    │                     │
│  │   (Rust)     │    │   Router     │                     │
│  │              │    │   (Rust)     │                     │
│  └──────────────┘    └──────────────┘                     │
│         │                   │                              │
│         │                   ▼                              │
│         │          ┌──────────────┐                        │
│         │          │ Compression  │                        │
│         │          │   Engine     │                        │
│         │          │   (Rust)     │                        │
│         │          └──────────────┘                        │
│         │                   │                              │
│         │                   ▼                              │
│         │          ┌──────────────┐                        │
│         │          │   LLM        │                        │
│         │          │   Service   │                        │
│         │          │   (Python)   │                        │
│         │          └──────────────┘                        │
│         │                   │                              │
│         │                   ▼                              │
│         │          ┌──────────────┐                        │
│         │          │   RAG        │                        │
│         │          │   Service   │                        │
│         │          │   (Python)   │                        │
│         │          └──────────────┘                        │
│         │                                                 │
│         └─────────────────────────────────────────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Rust Services Integration Layer

**Location**: `backend/shared/integration/rust_services.py`

Provides Python wrappers for Rust services:
- `RustSMSService`: Wrapper for Rust SMS Gateway
- `RustCompressionService`: Wrapper for Rust Compression Engine
- `RustMessageRouterService`: Wrapper for Rust Message Router
- `RustServicesManager`: Manager for all Rust services

**Features**:
- PyO3 bindings integration
- Fallback to Python implementations if Rust unavailable
- Unified interface for Rust services
- Statistics and monitoring

### 2. Service Discovery

**Location**: `backend/shared/integration/service_discovery.py`

Lightweight service discovery and health monitoring:
- `ServiceRegistry`: Service registration and discovery
- Health checks with configurable intervals
- Service status tracking (healthy/unhealthy/unreachable)
- Automatic health monitoring

**Features**:
- In-memory service registry (lightweight)
- Periodic health checks (default: 30s interval)
- Service statistics and monitoring
- Automatic failover support

### 3. Message Flow Pipeline

**Location**: `backend/shared/integration/message_flow.py`

End-to-end message processing pipeline:
- `MessageFlowPipeline`: Complete message processing flow
- Integrates Rust and Python services
- Handles emergency messages
- Compression and routing

**Flow**:
1. Receive SMS message
2. Route message (Rust Message Router)
3. Classify intent (Rust Message Router)
4. Handle emergency (immediate response)
5. Get RAG context (if needed)
6. Get LLM response (if needed)
7. Compress response (Rust Compression Engine)
8. Send SMS response (Rust SMS Gateway)

## Usage

### Basic Integration

```python
from backend.shared.integration.message_flow import MessageFlowPipeline
from backend.shared.models import SMSMessage, MessagePriority
from datetime import datetime

# Initialize pipeline
pipeline = MessageFlowPipeline()
await pipeline.initialize()

# Process message
message = SMSMessage(
    sender="+1234567890",
    receiver="+0987654321",
    content="What's the weather?",
    priority=MessagePriority.NORMAL,
    timestamp=datetime.utcnow()
)

result = await pipeline.process_message(message)
print(f"Status: {result['status']}")
print(f"Processing time: {result['processing_time']}s")
```

### Service Discovery

```python
from backend.shared.integration.service_discovery import (
    initialize_service_discovery,
    get_service_registry
)

# Initialize service discovery
config = {
    'sms_gateway_url': 'http://localhost:8001',
    'llm_service_url': 'http://localhost:8003',
    'rag_service_url': 'http://localhost:8004',
}

registry = await initialize_service_discovery(config)

# Get service status
stats = registry.get_service_stats()
print(f"Healthy services: {stats['healthy_services']}")

# Get specific service
llm_service = registry.get_service('llm_service')
if llm_service and llm_service.status.value == 'healthy':
    print(f"LLM service available at {llm_service.url}")
```

### Rust Services Direct Access

```python
from backend.shared.integration.rust_services import RustServicesManager

# Initialize Rust services
manager = RustServicesManager()
await manager.initialize()

# Use individual services
message_id = await manager.sms_service.send_sms(
    phone_number="+1234567890",
    content="Hello!",
    priority=1
)

compressed = await manager.compression_service.compress(
    "Long text here...",
    target_length=160
)

route = await manager.router_service.route(
    sender="+1234567890",
    content="What's the weather?"
)
```

## Configuration

### Environment Variables

```bash
# Rust Services
SMS_DEVICE=/dev/ttyUSB0
SMS_BAUD_RATE=115200
MAX_SMS_PER_MINUTE=10
MAX_SMS_PER_HOUR=100

# Compression
COMPRESSION_TARGET_LENGTH=160
COMPRESSION_LEVEL=0.7
COMPRESSION_CACHE_SIZE=1000

# Message Router
LLM_SERVICE_URL=http://localhost:8003
RAG_SERVICE_URL=http://localhost:8004
ROUTER_CACHE_SIZE=1000
BATTERY_THRESHOLD=50

# Service Discovery
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5.0
```

## Performance Targets

- **End-to-end latency**: <10s (target: <15s)
- **Routing latency**: <50ms (Rust Message Router)
- **Compression time**: <1s (Rust Compression Engine)
- **SMS send latency**: <50ms (Rust SMS Gateway)
- **Service health check**: <5s timeout

## Error Handling

All services include comprehensive error handling:
- Fallback to Python implementations if Rust unavailable
- Service health checks with automatic failover
- Graceful degradation under resource constraints
- Error responses sent to users

## Testing

Integration tests are located in `backend/tests/test_integration_rust_services.py`:

```bash
# Run integration tests
pytest backend/tests/test_integration_rust_services.py -v
```

## Future Enhancements

1. **Shared Memory**: Implement shared memory for message queue (reduce copies)
2. **gRPC**: Add gRPC for inter-service communication (optional)
3. **Service Mesh**: Lightweight service mesh for advanced routing
4. **Load Balancing**: Add load balancing for multiple service instances
5. **Circuit Breaker**: Implement circuit breaker pattern for resilience

## Troubleshooting

### Rust Services Not Available

If Rust services are not built or available, the integration layer automatically falls back to Python implementations. Check:
1. Rust services are built: `cargo build --release` in each service directory
2. PyO3 bindings are installed
3. Environment variables are set correctly

### Service Health Checks Failing

If health checks fail:
1. Verify services are running
2. Check service URLs in configuration
3. Verify network connectivity
4. Check service logs for errors

### High Latency

If processing latency is high:
1. Check service health (unhealthy services add delay)
2. Verify Rust services are being used (check logs)
3. Monitor resource usage (CPU, memory, battery)
4. Check network latency between services

