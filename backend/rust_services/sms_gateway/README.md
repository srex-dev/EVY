# EVY SMS Gateway (Rust)

High-performance SMS gateway implementation for EVY edge nodes, optimized for Raspberry Pi 4 hardware constraints.

## Features

- **High Performance**: Rust implementation with <50ms latency target
- **Memory Efficient**: <100MB memory usage (vs 150-200MB Python)
- **Power Aware**: Battery-aware processing with configurable thresholds
- **Rate Limiting**: Built-in per-minute and per-hour rate limiting
- **Priority Queue**: Emergency, High, Normal, Low priority support
- **Python Integration**: PyO3 bindings for seamless Python integration
- **GSM Support**: SIM800C/SIM7000 HAT support via serial AT commands

## Architecture

```
SMSGateway
├── SerialGSMDriver (AT commands)
├── SMSMessageQueue (priority-based)
└── PowerMonitor (battery-aware)
```

## Usage

### Rust

```rust
use evy_sms_gateway::{SMSGateway, GatewayConfig, MessagePriority};

let config = GatewayConfig::from_env();
let mut gateway = SMSGateway::new(config);
gateway.initialize().await?;

// Send SMS
let message_id = gateway.send_sms(
    "+1234567890".to_string(),
    "Hello from EVY!".to_string(),
    MessagePriority::Normal,
).await?;

// Get statistics
let stats = gateway.get_stats().await;
println!("Connected: {}, Pending: {}", stats.connected, stats.queue_stats.pending_messages);
```

### Python

```python
import evy_sms_gateway

# Create gateway
gateway = evy_sms_gateway.PySMSGateway()

# Initialize
gateway.initialize()

# Send SMS
message_id = gateway.send_sms(
    "+1234567890",
    "Hello from EVY!",
    priority=1  # 0=Low, 1=Normal, 2=High, 3=Emergency
)

# Get statistics
stats = gateway.get_stats()
print(f"Connected: {stats.connected}, Pending: {stats.pending_messages}")
```

## Configuration

Environment variables:
- `SMS_DEVICE`: Serial device path (default: `/dev/ttyUSB0`)
- `SMS_BAUD_RATE`: Baud rate (default: `115200`)
- `MAX_SMS_PER_MINUTE`: Rate limit per minute (default: `10`)
- `MAX_SMS_PER_HOUR`: Rate limit per hour (default: `100`)

## Performance Targets

- **Latency**: <50ms (vs <100ms Python)
- **Memory**: <100MB (vs 150-200MB Python)
- **Power**: <2W (vs 2.5W Python)
- **Throughput**: 60-120 SMS/hour per HAT

## Building

```bash
cd backend/rust_services/sms_gateway
cargo build --release

# With Python bindings
cargo build --release --features python
```

## Testing

```bash
cargo test
```

## Integration

The Rust SMS Gateway integrates with the Python services via PyO3 bindings. The Python SMS Gateway service can be updated to use the Rust implementation for improved performance.

## Edge Optimizations

- Pre-allocated buffers, reused allocations
- Minimal logging (errors only)
- In-memory queue (no disk I/O)
- Power-aware processing (reduces frequency when battery <30%)
- Batch operations where possible

## License

Part of the EVY project.

