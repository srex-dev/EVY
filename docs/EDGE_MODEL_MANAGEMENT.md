# Edge Model Management

## Overview

Edge-optimized model management for EVY lilEVY nodes, designed for Raspberry Pi 4 hardware constraints with 4-bit quantization, memory-aware loading, and power-aware management.

## Features

- **llama.cpp Integration**: High-performance C++ inference engine
- **4-bit Quantization**: Reduces model size by 75% (2GB → 500MB)
- **Memory-Aware Loading**: Checks available memory before loading
- **Power-Aware Management**: Unloads models when battery <30%
- **Model Switching**: Fast switching between models
- **Model Caching**: Keeps frequently used models loaded
- **Small Context**: 512 tokens (vs 2048+ for large models)

## Architecture

```
EdgeModelManager
├── ModelRegistry (metadata only)
├── ModelCache (recently used)
├── llama.cpp (inference engine)
└── ResourceMonitor (memory, battery)
```

## Model Registry

Pre-configured edge-optimized models:

1. **tinyllama-4bit**
   - Size: 550MB (quantized)
   - Memory: 600MB when loaded
   - Context: 512 tokens
   - Best for: General queries

2. **phi-2-mini-4bit**
   - Size: 125MB (quantized)
   - Memory: 200MB when loaded
   - Context: 512 tokens
   - Best for: Low-memory scenarios

3. **qwen1.5-0.5b-4bit**
   - Size: 250MB (quantized)
   - Memory: 350MB when loaded
   - Context: 512 tokens
   - Best for: Balanced performance

## Usage

### Basic Model Loading

```python
from backend.services.llm_inference.edge_model_manager import EdgeModelManager

# Initialize manager
config = {
    'max_memory_mb': 2000,  # 2GB limit
    'max_context_tokens': 512,
    'num_threads': 2,
    'battery_threshold': 30,
}
manager = EdgeModelManager(config)

# Load model
success = await manager.load_model('tinyllama-4bit')
if success:
    print("Model loaded successfully")
```

### Generate Response

```python
# Generate response
result = await manager.generate(
    prompt="What's the weather?",
    model_name='tinyllama-4bit',
    max_tokens=100,
    temperature=0.7
)

print(f"Response: {result['response']}")
print(f"Processing time: {result['processing_time']:.2f}s")
```

### Model Switching

```python
# Switch from one model to another
success = await manager.switch_model(
    from_model='tinyllama-4bit',
    to_model='phi-2-mini-4bit'
)
```

### Power-Aware Management

```python
# Update battery level
manager.update_battery_level(25)  # Low battery

# Models will be automatically unloaded if battery <30%
```

### Model Registry

```python
# Get model registry
registry = manager.get_model_registry()

for model_name, info in registry.items():
    print(f"{model_name}: {info['memory_requirement_mb']}MB, Status: {info['status']}")
```

## Configuration

### Environment Variables

```bash
# Model directory
MODEL_DIR=/data/models

# Memory limits
MAX_MEMORY_MB=2000
MAX_CONTEXT_TOKENS=512

# Threading
NUM_THREADS=2

# Power management
BATTERY_THRESHOLD=30
```

### Configuration Dictionary

```python
config = {
    'model_dir': '/data/models',
    'max_memory_mb': 2000,
    'max_context_tokens': 512,
    'num_threads': 2,
    'battery_threshold': 30,
}
```

## Performance Targets

- **Model Loading**: <30s (from microSD)
- **Memory Usage**: <2GB (4-bit quantization)
- **CPU Usage**: <50% (2 threads)
- **Inference Speed**: <5s per response
- **Context Size**: 512 tokens (small, fast)

## Edge Optimizations

1. **4-bit Quantization**: 75% size reduction
2. **Small Context**: 512 tokens (vs 2048+)
3. **2 Threads**: Leave cores for other services
4. **Memory-Mapped I/O**: Faster loading from microSD
5. **Model Caching**: Keep frequently used models loaded
6. **Power-Aware**: Unload when battery low

## llama.cpp Integration

The manager uses llama.cpp for optimal performance:

- **C++ Backend**: Fast inference
- **Memory-Mapped I/O**: Efficient loading
- **CPU Optimized**: No GPU required
- **Quantization Support**: Built-in 4-bit support

If llama.cpp is not available, falls back to transformers/Ollama.

## Model Lifecycle

1. **Available**: Model metadata registered
2. **Loading**: Model being loaded from disk
3. **Loaded**: Model ready for inference
4. **Unloaded**: Model freed from memory
5. **Error**: Model failed to load

## Memory Management

- Checks available memory before loading
- Unloads unused models after 1 hour
- Automatically unloads all models if battery <30%
- Garbage collection after unloading

## Testing

```bash
# Run edge model manager tests
pytest backend/tests/test_edge_model_manager.py -v
```

## Troubleshooting

### Model Not Loading

1. Check model file exists in `MODEL_DIR`
2. Verify sufficient memory available
3. Check battery level (must be >30%)
4. Verify llama.cpp is installed (optional)

### High Memory Usage

1. Use smaller model (phi-2-mini-4bit)
2. Reduce `max_memory_mb` in config
3. Enable automatic model unloading
4. Check for memory leaks

### Slow Inference

1. Check CPU usage (should be <50%)
2. Verify model is quantized (4-bit)
3. Reduce `max_tokens` parameter
4. Check microSD read speed

