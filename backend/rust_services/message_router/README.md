# EVY Message Router (Rust)

High-performance message routing with resource awareness, optimized for Raspberry Pi 4 hardware constraints.

## Features

- **Rule-Based Classification**: Fast intent classification (no ML model)
- **Service Registry**: Lightweight in-memory service registry
- **Routing Cache**: LRU cache for route decisions (max 1000 entries)
- **Resource-Aware**: Battery and memory-aware service selection
- **High Performance**: <50ms routing latency target
- **Memory Efficient**: <30MB memory usage (vs 50MB Python)
- **Python Integration**: PyO3 bindings for seamless Python integration

## Architecture

```
MessageRouter
├── IntentClassifier (rule-based)
├── ServiceRegistry (in-memory)
├── RoutingCache (LRU)
└── ResourceMonitor (battery, memory)
```

## Usage

### Rust

```rust
use evy_message_router::{MessageRouter, RouterConfig, Message};

let config = RouterConfig::default();
let router = MessageRouter::new(config);
router.initialize().await?;

// Route message
let message = Message {
    id: "msg1".to_string(),
    sender: "+1234567890".to_string(),
    content: "What's the weather?".to_string(),
    timestamp: chrono::Utc::now(),
};

let route = router.route(&message).await?;
println!("Route to: {:?}", route.service_type);
```

### Python

```python
import evy_message_router

# Create router
router = evy_message_router.PyMessageRouter()
router.initialize()

# Route message
route = router.route("+1234567890", "What's the weather?")
print(f"Route to: {route.service_type}")

# Classify message
classification = router.classify("EMERGENCY! Help!")
print(f"Intent: {classification.intent}, Priority: {classification.priority}")
```

## Configuration

Environment variables:
- `LLM_SERVICE_URL`: LLM service URL (default: `http://localhost:8003`)
- `RAG_SERVICE_URL`: RAG service URL (default: `http://localhost:8004`)
- `SMS_GATEWAY_URL`: SMS gateway URL (default: `http://localhost:8001`)
- `ROUTER_CACHE_SIZE`: Cache size (default: `1000`)
- `BATTERY_THRESHOLD`: Battery threshold for bigEVY (default: `50`)

## Performance Targets

- **Routing Latency**: <50ms (vs <100ms Python)
- **Memory**: <30MB (vs 50MB Python)
- **CPU**: <40% (vs 60% Python)
- **Battery-Aware**: Skip bigEVY if battery <50%

## Intent Classification

- **Emergency**: Keywords like "emergency", "help", "911", "fire"
- **Command**: Messages starting with "/"
- **Query**: Questions (what, where, when, who, why, how)
- **Greeting**: Hello, hi, thanks, etc.
- **Unknown**: Default fallback

## Building

```bash
cd backend/rust_services/message_router
cargo build --release

# With Python bindings
cargo build --release --features python
```

## Testing

```bash
cargo test
```

## License

Part of the EVY project.

