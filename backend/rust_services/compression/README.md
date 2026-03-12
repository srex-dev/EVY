# EVY Compression Engine (Rust)

Edge-optimized text compression engine for SMS responses, optimized for Raspberry Pi 4 hardware constraints.

## Features

- **Rule-Based Compression**: Fast compression using abbreviations and regex patterns
- **LRU Cache**: Memory-efficient caching of compression results (max 1000 entries)
- **Resource-Aware**: Memory and battery-aware compression
- **High Performance**: <1s compression time target
- **Memory Efficient**: <50MB memory usage (vs 100MB Python)
- **Python Integration**: PyO3 bindings for seamless Python integration

## Architecture

```
CompressionEngine
├── RuleBasedCompressor (abbreviations, regex)
├── CompressionCache (LRU)
└── ResourceMonitor (memory, battery)
```

## Usage

### Rust

```rust
use evy_compression::{CompressionEngine, CompressionConfig};

let config = CompressionConfig::default();
let engine = CompressionEngine::new(config);

// Compress text
let compressed = engine.compress(
    "The emergency medical services are on their way",
    Some(50) // target length
).await?;

// Get statistics
let stats = engine.get_stats().await;
println!("Compression ratio: {:.1}%", stats.average_compression_ratio);
```

### Python

```python
import evy_compression

# Create engine
engine = evy_compression.PyCompressionEngine()

# Compress text
compressed = engine.compress(
    "The emergency medical services are on their way",
    target_length=50
)

# Get statistics
stats = engine.get_stats()
print(f"Compression ratio: {stats.average_compression_ratio:.1}%")
```

## Configuration

Environment variables:
- `COMPRESSION_TARGET_LENGTH`: Target length (default: `160`)
- `COMPRESSION_LEVEL`: Compression level 0.0-1.0 (default: `0.7`)
- `COMPRESSION_CACHE_SIZE`: Cache size (default: `1000`)

## Performance Targets

- **Compression Time**: <1s (target: <2s)
- **Memory**: <50MB (vs 100MB Python)
- **CPU**: <30% (vs 50% Python)
- **Compression Ratio**: 40-50% (vs 20-30% truncation)

## Compression Techniques

1. **Abbreviations**: Common words/phrases (e.g., "thank you" → "ty")
2. **Regex Patterns**: Whitespace compression, contractions
3. **Intelligent Truncation**: Word/sentence boundary aware
4. **Caching**: LRU cache for repeated compressions

## Building

```bash
cd backend/rust_services/compression
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

