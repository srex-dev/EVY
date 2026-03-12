# EVY Edge Implementation Plan
## Comprehensive Plan for Edge Deployment with Hardware Constraints

### Executive Summary
This document provides a detailed, phased implementation plan for EVY focusing on edge hardware limitations (Raspberry Pi 4, 4-8GB RAM, 10-15W power, microSD storage). The plan integrates Rust refactoring, compression engine, and addresses all critical gaps while respecting edge constraints.

---

## 🎯 **Edge Hardware Constraints**

### **lilEVY Hardware Limitations**
```
Raspberry Pi 4:
├── CPU: ARM Cortex-A72 (4 cores, 1.5-1.8 GHz)
├── RAM: 4-8GB LPDDR4 (shared with GPU)
├── Storage: 128GB microSD (slow I/O, ~20MB/s read, ~10MB/s write)
├── Power: 10-15W (solar-powered, battery backup)
├── Network: WiFi/Ethernet (no cellular data plan)
└── GPIO: 40-pin header (GSM/LoRa HATs)

Constraints:
├── Memory: Must fit OS (1GB) + Models (2-3GB) + Services (1-2GB) = 4-6GB
├── CPU: Limited parallelism (4 cores, ARM architecture)
├── Storage: Slow I/O, limited writes (microSD wear)
├── Power: 10-15W budget (solar + battery)
└── Network: No internet (offline-first)
```

### **Design Principles for Edge**
1. **Memory Efficiency**: Minimize RAM usage (target: <4GB total)
2. **CPU Efficiency**: Optimize for ARM, minimize CPU usage
3. **Power Efficiency**: Minimize power consumption (target: <12W)
4. **Storage Efficiency**: Minimize writes, use caching
5. **Offline-First**: No internet dependency
6. **Fault Tolerance**: Handle failures gracefully
7. **Resource Awareness**: Monitor and adapt to constraints

---

## 📋 **Implementation Phases**

### **Phase 1: Critical Foundation (Months 1-3)**
**Goal**: Get basic system working on edge hardware with emergency response capabilities

---

#### **Month 1: Hardware Validation & Rust SMS Gateway**

##### **Week 1-2: Hardware Validation**
**Objective**: Validate hardware works, measure actual resource usage

**Tasks:**
- [ ] **Hardware Setup**
  - [ ] Assemble Raspberry Pi 4 + GSM HAT + LoRa HAT
  - [ ] Install Raspberry Pi OS 64-bit (minimal)
  - [ ] Configure GPIO pins for GSM/LoRa
  - [ ] Test solar power system (50-100W panel)
  - [ ] Measure baseline power consumption

- [ ] **Hardware Testing**
  - [ ] Test GSM HAT (SMS send/receive)
  - [ ] Test LoRa HAT (range, reliability)
  - [ ] Measure power consumption per component
  - [ ] Test battery runtime (24-36h target)
  - [ ] Validate microSD I/O performance

**Deliverables:**
- Working hardware prototype
- Power consumption baseline (target: <12W idle, <15W active)
- Hardware validation report
- Resource usage measurements

**Edge Considerations:**
- Use minimal OS (Raspberry Pi OS Lite)
- Disable unnecessary services
- Optimize boot time (<30s)
- Minimize disk writes (use tmpfs for logs)

---

##### **Week 3-4: Rust SMS Gateway (Critical Path)**
**Objective**: Implement high-performance SMS gateway in Rust

**Why Rust First:**
- SMS gateway is highest frequency component
- Needs low latency (<100ms)
- CPU-intensive (parsing, routing)
- Memory-efficient (handle many messages)

**Implementation:**
```rust
// backend-rust/sms_gateway/src/main.rs
// Edge-optimized SMS gateway

use std::sync::Arc;
use tokio::sync::mpsc;
use gammu_rs; // Rust bindings for Gammu

pub struct EdgeSMSGateway {
    gsm_device: Arc<GsmDevice>,
    message_queue: mpsc::UnboundedReceiver<SMSMessage>,
    power_monitor: PowerMonitor,
    memory_monitor: MemoryMonitor,
}

impl EdgeSMSGateway {
    // Memory-efficient message processing
    pub async fn process_message(&mut self, msg: SMSMessage) -> Result<()> {
        // Check memory before processing
        if self.memory_monitor.available() < 50_000_000 { // 50MB threshold
            return Err(Error::LowMemory);
        }
        
        // Process with minimal allocations
        let response = self.parse_and_route(msg).await?;
        
        // Send response (non-blocking)
        self.send_sms(response).await?;
        
        Ok(())
    }
    
    // Power-aware processing
    pub async fn process_with_power_check(&mut self, msg: SMSMessage) -> Result<()> {
        let battery_level = self.power_monitor.get_battery_level().await?;
        
        if battery_level < 20 {
            // Low power mode: skip non-critical processing
            return self.process_critical_only(msg).await;
        }
        
        self.process_message(msg).await
    }
}
```

**Edge Optimizations:**
- **Memory**: Pre-allocate buffers, reuse allocations
- **CPU**: Use SIMD for string processing (if available)
- **Power**: Batch operations, reduce CPU frequency when idle
- **Storage**: Minimal logging (errors only), use in-memory queue

**Expected Results:**
- 2-3x faster SMS processing (vs Python)
- 30% lower memory usage (50-100MB vs 150-200MB)
- 20% lower power consumption (2W vs 2.5W)
- <50ms latency (vs <100ms Python)

**Deliverables:**
- Rust SMS gateway service
- Gammu Rust bindings (or C FFI)
- Power-aware processing
- Memory monitoring
- Performance benchmarks

---

#### **Month 2: Compression Engine & Message Router**

##### **Week 1-2: Lightweight Compression Engine (Rust)**
**Objective**: Implement edge-optimized compression for SMS responses

**Why Rust:**
- CPU-intensive (compression algorithms)
- Needs low latency (<2s)
- Memory-efficient (minimal allocations)
- Power-efficient (faster = less CPU time)

**Edge-Optimized Design:**
```rust
// backend-rust/compression/src/lib.rs
// Edge compression engine - optimized for ARM, low memory

pub struct EdgeCompressionEngine {
    // Rule-based compressor (no model, fast)
    rule_compressor: RuleBasedCompressor,
    
    // Tiny model compressor (125M model, optional)
    tiny_model: Option<TinyCompressionModel>,
    
    // Power/memory monitor
    resource_monitor: ResourceMonitor,
    
    // Cache for common compressions
    compression_cache: LruCache<String, String>,
}

impl EdgeCompressionEngine {
    // Memory-aware compression
    pub async fn compress(
        &mut self,
        text: &str,
        target_length: usize,
    ) -> Result<String> {
        // Check available memory
        if self.resource_monitor.available_memory() < 100_000_000 { // 100MB
            // Low memory: use rule-based only
            return self.rule_compressor.compress(text, target_length);
        }
        
        // Check battery level
        let battery = self.resource_monitor.battery_level();
        if battery < 30 {
            // Low battery: use fast compression only
            return self.rule_compressor.compress(text, target_length);
        }
        
        // Try cache first (memory-efficient)
        if let Some(cached) = self.compression_cache.get(text) {
            if cached.len() <= target_length {
                return Ok(cached.clone());
            }
        }
        
        // Try rule-based first (fast, <0.5s)
        let compressed = self.rule_compressor.compress(text, target_length);
        if compressed.len() <= target_length {
            self.compression_cache.put(text.to_string(), compressed.clone());
            return Ok(compressed);
        }
        
        // Try tiny model if available (moderate, <1.5s)
        if let Some(ref model) = self.tiny_model {
            if self.resource_monitor.available_memory() > 200_000_000 { // 200MB
                let compressed = model.compress(text, target_length).await?;
                if compressed.len() <= target_length {
                    self.compression_cache.put(text.to_string(), compressed.clone());
                    return Ok(compressed);
                }
            }
        }
        
        // Fallback: aggressive rule-based
        self.rule_compressor.compress_aggressive(text, target_length)
    }
}

// Rule-based compressor (no model, very fast)
pub struct RuleBasedCompressor {
    // Pre-compiled regex patterns (efficient)
    patterns: Vec<Regex>,
    
    // Abbreviation dictionary (in-memory, small)
    abbreviations: HashMap<String, String>,
}

impl RuleBasedCompressor {
    pub fn compress(&self, text: &str, target: usize) -> String {
        // Fast string operations (no allocations where possible)
        let mut result = String::with_capacity(target);
        
        // Apply compression rules (CPU-efficient)
        for pattern in &self.patterns {
            // Use regex efficiently (pre-compiled)
            result = pattern.replace_all(&result, |caps: &Captures| {
                // Minimal allocations
                self.abbreviations.get(caps.get(0).unwrap().as_str())
                    .cloned()
                    .unwrap_or_else(|| caps.get(0).unwrap().as_str().to_string())
            }).to_string();
        }
        
        // Truncate if still too long (last resort)
        if result.len() > target {
            result.truncate(target - 3);
            result.push_str("...");
        }
        
        result
    }
}
```

**Edge Optimizations:**
- **Memory**: Pre-compile regex patterns, reuse buffers
- **CPU**: Use SIMD for string operations (if available)
- **Power**: Skip model compression if battery <30%
- **Storage**: Cache in memory (LRU, max 1000 entries)
- **Fallback**: Rule-based only if memory <100MB

**Expected Results:**
- 2-3x faster compression (vs Python)
- 50% lower memory usage (50MB vs 100MB)
- 30% lower CPU usage
- <1s compression time (target: <2s)

**Deliverables:**
- Rust compression engine
- Rule-based compressor
- Tiny model integration (optional)
- Resource-aware compression
- Performance benchmarks

---

##### **Week 3-4: Rust Message Router**
**Objective**: Implement high-performance message routing in Rust

**Why Rust:**
- Critical path (every message goes through router)
- Needs low latency (<50ms)
- CPU-intensive (classification, routing)
- Memory-efficient (handle many concurrent messages)

**Implementation:**
```rust
// backend-rust/message_router/src/main.rs
// Edge-optimized message router

use std::sync::Arc;
use tokio::sync::mpsc;

pub struct EdgeMessageRouter {
    // Lightweight intent classifier (no ML model, rule-based)
    intent_classifier: RuleBasedClassifier,
    
    // Service registry (in-memory, lightweight)
    service_registry: Arc<ServiceRegistry>,
    
    // Routing cache (LRU, memory-efficient)
    routing_cache: LruCache<String, Route>,
    
    // Resource monitor
    resource_monitor: ResourceMonitor,
}

impl EdgeMessageRouter {
    // Fast routing with resource awareness
    pub async fn route(&mut self, message: SMSMessage) -> Result<Route> {
        // Check cache first (fast path)
        if let Some(cached) = self.routing_cache.get(&message.content) {
            return Ok(cached.clone());
        }
        
        // Classify intent (rule-based, fast)
        let intent = self.intent_classifier.classify(&message.content)?;
        
        // Select service (resource-aware)
        let route = self.select_service(intent, &message).await?;
        
        // Cache route (memory-efficient)
        self.routing_cache.put(message.content.clone(), route.clone());
        
        Ok(route)
    }
    
    // Resource-aware service selection
    async fn select_service(
        &self,
        intent: Intent,
        message: &SMSMessage,
    ) -> Result<Route> {
        let available_memory = self.resource_monitor.available_memory();
        let battery_level = self.resource_monitor.battery_level();
        
        match intent {
            Intent::Emergency => {
                // Emergency: always route to local LLM (fastest)
                Route::LocalLLM
            }
            Intent::SimpleQuery => {
                // Simple: local LLM if memory available
                if available_memory > 200_000_000 { // 200MB
                    Route::LocalLLM
                } else {
                    Route::TemplateResponse // Fallback to templates
                }
            }
            Intent::ComplexQuery => {
                // Complex: try bigEVY if battery >50%, else local
                if battery_level > 50 {
                    Route::BigEVY
                } else {
                    Route::LocalLLM // Low battery: use local
                }
            }
            Intent::RAGQuery => {
                // RAG: local if memory available
                if available_memory > 300_000_000 { // 300MB
                    Route::LocalRAG
                } else {
                    Route::TemplateResponse
                }
            }
        }
    }
}
```

**Edge Optimizations:**
- **Memory**: In-memory service registry, LRU cache (max 1000 routes)
- **CPU**: Rule-based classification (no ML model)
- **Power**: Battery-aware routing (skip bigEVY if battery <50%)
- **Latency**: Cache routes, fast path for common queries

**Expected Results:**
- <50ms routing latency (vs <100ms Python)
- 40% lower CPU usage
- 30% lower memory usage (20MB vs 30MB)
- Battery-aware routing

**Deliverables:**
- Rust message router
- Rule-based intent classifier
- Resource-aware routing
- Performance benchmarks

---

#### **Month 3: Service Integration & Emergency Features**

##### **Week 1-2: Service Integration (Python + Rust)**
**Objective**: Integrate Rust services with Python services

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│              EVY Edge Service Architecture            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │ SMS Gateway  │───▶│   Message    │                 │
│  │   (Rust)     │    │   Router     │                 │
│  │              │    │   (Rust)     │                 │
│  └──────────────┘    └──────────────┘                 │
│         │                   │                          │
│         │                   ▼                          │
│         │          ┌──────────────┐                    │
│         │          │ Compression  │                    │
│         │          │   Engine     │                    │
│         │          │   (Rust)     │                    │
│         │          └──────────────┘                    │
│         │                   │                          │
│         │                   ▼                          │
│         │          ┌──────────────┐                    │
│         │          │   LLM        │                    │
│         │          │   Service   │                    │
│         │          │   (Python)   │                    │
│         │          └──────────────┘                    │
│         │                   │                          │
│         │                   ▼                          │
│         │          ┌──────────────┐                    │
│         │          │   RAG        │                    │
│         │          │   Service   │                    │
│         │          │   (Python)   │                    │
│         │          └──────────────┘                    │
│         │                   │                          │
│         └───────────────────┘                          │
│                   │                                     │
│                   ▼                                     │
│          ┌──────────────┐                              │
│          │   Response   │                              │
│          │   (Rust)     │                              │
│          └──────────────┘                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Integration Approach:**
- **PyO3**: Rust-Python bindings for service communication
- **gRPC**: Lightweight RPC for inter-service communication
- **Shared Memory**: For high-frequency data (message queue)

**Implementation:**
```python
# backend/shared/rust_bridge.py
# Python bridge to Rust services

import ctypes
from ctypes import CDLL, c_char_p, c_int

# Load Rust library
rust_lib = CDLL('./target/release/libevy_rust.so')

# SMS Gateway
rust_lib.sms_send.argtypes = [c_char_p, c_char_p]
rust_lib.sms_send.restype = c_int

def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Rust gateway."""
    result = rust_lib.sms_send(
        phone.encode('utf-8'),
        message.encode('utf-8')
    )
    return result == 0

# Message Router
rust_lib.route_message.argtypes = [c_char_p]
rust_lib.route_message.restype = c_char_p

def route_message(content: str) -> str:
    """Route message via Rust router."""
    result = rust_lib.route_message(content.encode('utf-8'))
    return result.decode('utf-8')

# Compression Engine
rust_lib.compress_text.argtypes = [c_char_p, c_int]
rust_lib.compress_text.restype = c_char_p

def compress_text(text: str, target_length: int) -> str:
    """Compress text via Rust engine."""
    result = rust_lib.compress_text(
        text.encode('utf-8'),
        target_length
    )
    return result.decode('utf-8')
```

**Edge Considerations:**
- **Memory**: Shared memory for message queue (avoid copies)
- **CPU**: Minimize Python-Rust boundary crossings
- **Power**: Batch operations, reduce context switches
- **Latency**: Direct function calls (no network overhead)

**Deliverables:**
- PyO3 bindings for Rust services
- Python service integration
- End-to-end message flow
- Performance benchmarks

---

##### **Week 3-4: Emergency Response Features**
**Objective**: Implement emergency response capabilities

**Edge-Optimized Emergency System:**
```python
# backend/lilevy/services/emergency_service.py
# Edge-optimized emergency response

class EdgeEmergencyService:
    """Emergency response service optimized for edge."""
    
    def __init__(self):
        # Pre-loaded emergency templates (memory-efficient)
        self.emergency_templates = self._load_templates()
        
        # Emergency contacts (in-memory, small)
        self.emergency_contacts = self._load_contacts()
        
        # Compression engine (Rust, via bridge)
        self.compressor = RustCompressionBridge()
        
        # Resource monitor
        self.resource_monitor = ResourceMonitor()
    
    async def handle_emergency(self, message: SMSMessage) -> SMSMessage:
        """Handle emergency message with resource awareness."""
        
        # Check if emergency (fast pattern matching)
        if not self._is_emergency(message.content):
            return None
        
        # Get emergency response (pre-loaded, fast)
        response = self._get_emergency_response(message.content)
        
        # Compress if needed (resource-aware)
        if len(response) > 160:
            battery = await self.resource_monitor.get_battery_level()
            if battery > 20:  # Only compress if battery available
                response = await self.compressor.compress(
                    response,
                    target_length=160
                )
            else:
                # Low battery: truncate (faster)
                response = response[:157] + "..."
        
        # Send immediately (priority queue)
        return SMSMessage(
            phone_number=message.phone_number,
            content=response,
            priority=Priority.EMERGENCY,
            timestamp=datetime.now()
        )
    
    def _load_templates(self) -> Dict[str, str]:
        """Load emergency templates (memory-efficient)."""
        # Pre-compiled templates (small, <1MB)
        templates = {
            "hurricane": "URGENT: Hurricane warning. Evacuate now to shelters. Bring: water, food, meds, docs. Contact: 911.",
            "earthquake": "URGENT: Earthquake. Drop, cover, hold. Stay indoors. Avoid windows. Contact: 911.",
            "fire": "URGENT: Fire alert. Evacuate immediately. Use stairs, not elevators. Contact: 911.",
            # ... more templates
        }
        return templates
    
    def _is_emergency(self, content: str) -> bool:
        """Fast emergency detection (pattern matching)."""
        # Pre-compiled regex patterns (efficient)
        emergency_keywords = [
            r'\b(emergency|urgent|help|911|fire|hurricane|earthquake)\b',
            r'\b(evacuate|danger|dangerous|critical)\b',
        ]
        
        content_lower = content.lower()
        for pattern in emergency_keywords:
            if re.search(pattern, content_lower):
                return True
        return False
```

**Edge Optimizations:**
- **Memory**: Pre-loaded templates (no database queries)
- **CPU**: Pattern matching (no ML model)
- **Power**: Skip compression if battery <20%
- **Latency**: Direct template lookup (<10ms)

**Deliverables:**
- Emergency response service
- Emergency templates (pre-loaded)
- Emergency detection (pattern-based)
- Priority routing
- Performance benchmarks

---

### **Phase 2: Core Infrastructure (Months 4-6)**

#### **Month 4: Model Management & Database**

##### **Week 1-2: Edge-Optimized Model Loading**
**Objective**: Implement actual model loading with edge constraints

**Edge Model Management:**
```python
# backend/services/llm_inference/edge_model_manager.py
# Edge-optimized model management

class EdgeModelManager:
    """Model manager optimized for edge hardware."""
    
    def __init__(self):
        # Model registry (metadata only, small)
        self.model_registry = {
            "tinyllama": {
                "size_mb": 500,
                "memory_mb": 2000,
                "quantization": "4bit",
                "path": "/models/tinyllama-4bit.gguf"
            },
            # ... more models
        }
        
        # Currently loaded model
        self.loaded_model = None
        
        # Memory monitor
        self.memory_monitor = MemoryMonitor()
        
        # Model cache (in-memory, limited)
        self.model_cache = None
    
    async def load_model(self, model_name: str) -> bool:
        """Load model with edge constraints."""
        
        # Check available memory
        available = self.memory_monitor.available_memory()
        required = self.model_registry[model_name]["memory_mb"] * 1024 * 1024
        
        if available < required:
            logger.warning(f"Insufficient memory: {available} < {required}")
            return False
        
        # Unload current model if different
        if self.loaded_model != model_name:
            await self.unload_model()
        
        # Load model (quantized, memory-efficient)
        try:
            # Use llama.cpp (C++, efficient)
            self.model_cache = await self._load_with_llamacpp(
                self.model_registry[model_name]["path"]
            )
            self.loaded_model = model_name
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    async def _load_with_llamacpp(self, model_path: str):
        """Load model using llama.cpp (memory-efficient)."""
        # Use llama.cpp Python bindings (C++ backend)
        from llama_cpp import Llama
        
        # Load with quantization (4-bit, memory-efficient)
        llm = Llama(
            model_path=model_path,
            n_ctx=512,  # Small context (edge constraint)
            n_threads=2,  # 2 threads (leave cores for other services)
            n_gpu_layers=0,  # No GPU on edge
            verbose=False
        )
        
        return llm
    
    async def generate(self, prompt: str, max_tokens: int = 50) -> str:
        """Generate response with edge constraints."""
        
        if not self.model_cache:
            raise RuntimeError("No model loaded")
        
        # Check memory before generation
        if self.memory_monitor.available_memory() < 100_000_000:  # 100MB
            raise RuntimeError("Insufficient memory for generation")
        
        # Generate (limited tokens for edge)
        response = self.model_cache(
            prompt,
            max_tokens=min(max_tokens, 50),  # Limit tokens (edge constraint)
            temperature=0.7,
            stop=["\n\n", "User:", "EVY:"]
        )
        
        return response["choices"][0]["text"]
```

**Edge Optimizations:**
- **Memory**: 4-bit quantization, small context (512 tokens)
- **CPU**: 2 threads (leave cores for other services)
- **Storage**: Load from microSD (slow, but acceptable for startup)
- **Power**: Unload model when idle (save memory/power)

**Deliverables:**
- Edge model manager
- Actual model loading (llama.cpp)
- Memory-aware loading
- Model switching
- Performance benchmarks

---

##### **Week 3-4: Lightweight Database (SQLite)**
**Objective**: Add persistent storage without heavy database

**Why SQLite:**
- Lightweight (no server process)
- File-based (works with microSD)
- ACID compliant
- Low memory footprint (<10MB)
- Perfect for edge

**Implementation:**
```python
# backend/shared/edge_database.py
# Edge-optimized database (SQLite)

import sqlite3
import aiosqlite
from pathlib import Path

class EdgeDatabase:
    """SQLite database optimized for edge."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = None
        
        # Optimize SQLite for edge
        self.optimize_for_edge()
    
    def optimize_for_edge(self):
        """Optimize SQLite for edge hardware."""
        # Set pragmas for edge optimization
        self.pragmas = {
            "journal_mode": "WAL",  # Write-Ahead Logging (faster writes)
            "synchronous": "NORMAL",  # Balance safety/speed (not FULL)
            "cache_size": "-32000",  # 32MB cache (memory-efficient)
            "temp_store": "MEMORY",  # Use memory for temp tables
            "mmap_size": "268435456",  # 256MB memory-mapped I/O
        }
    
    async def initialize(self):
        """Initialize database with edge optimizations."""
        self.connection = await aiosqlite.connect(
            str(self.db_path),
            check_same_thread=False
        )
        
        # Apply optimizations
        for pragma, value in self.pragmas.items():
            await self.connection.execute(f"PRAGMA {pragma} = {value}")
        
        # Create tables (minimal schema)
        await self.create_tables()
    
    async def create_tables(self):
        """Create minimal tables for edge."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                response TEXT,
                INDEX idx_phone (phone_number),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                INDEX idx_metric (metric),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        await self.connection.commit()
    
    async def insert_message(self, phone: str, content: str, response: str):
        """Insert message (batch writes for efficiency)."""
        await self.connection.execute(
            "INSERT INTO messages (phone_number, content, timestamp, response) VALUES (?, ?, ?, ?)",
            (phone, content, int(time.time()), response)
        )
        # Batch commits (every 10 messages or 60s)
        await self.connection.commit()
```

**Edge Optimizations:**
- **Memory**: 32MB cache, memory-mapped I/O
- **Storage**: WAL mode (faster writes, less wear)
- **CPU**: Normal sync (not FULL, faster)
- **Writes**: Batch commits (reduce microSD wear)

**Deliverables:**
- SQLite database integration
- Edge-optimized configuration
- Minimal schema
- Batch operations
- Performance benchmarks

---

#### **Month 5: Mesh Network & Monitoring**

##### **Week 1-2: Rust Mesh Network**
**Objective**: Implement high-performance mesh networking in Rust

**Why Rust:**
- Network-intensive (LoRa transmission)
- Needs low latency (<5s)
- Power-efficient (faster = less transmission time)
- Memory-efficient (handle many messages)

**Implementation:**
```rust
// backend-rust/mesh_network/src/main.rs
// Edge-optimized mesh networking

pub struct EdgeMeshNetwork {
    // LoRa radio (C bindings)
    lora_radio: LoRaRadio,
    
    // Routing table (in-memory, lightweight)
    routing_table: Arc<RwLock<RoutingTable>>,
    
    // Message queue (memory-efficient)
    message_queue: mpsc::UnboundedReceiver<MeshMessage>,
    
    // Compression (for mesh messages)
    compressor: Arc<CompressionEngine>,
    
    // Resource monitor
    resource_monitor: ResourceMonitor,
}

impl EdgeMeshNetwork {
    // Send message with compression
    pub async fn send(&mut self, message: MeshMessage) -> Result<()> {
        // Compress message (reduce transmission time)
        let compressed = self.compressor.compress(
            &message.content,
            target_length=200  // LoRa limit
        ).await?;
        
        // Check battery before transmission
        let battery = self.resource_monitor.battery_level();
        if battery < 20 {
            // Low battery: skip non-critical messages
            if message.priority != Priority::Emergency {
                return Err(Error::LowBattery);
            }
        }
        
        // Route message (find best path)
        let route = self.find_route(&message.destination).await?;
        
        // Transmit via LoRa (power-efficient)
        self.lora_radio.transmit(&compressed, &route).await?;
        
        Ok(())
    }
    
    // Find route (Dijkstra's algorithm, memory-efficient)
    async fn find_route(&self, destination: &str) -> Result<Route> {
        let table = self.routing_table.read().await;
        
        // Simple routing (memory-efficient, no complex algorithms)
        if let Some(route) = table.get(destination) {
            return Ok(route.clone());
        }
        
        // Broadcast discovery (if route unknown)
        self.broadcast_discovery(destination).await?;
        
        // Wait for route response (timeout: 5s)
        tokio::time::timeout(
            Duration::from_secs(5),
            self.wait_for_route(destination)
        ).await?
    }
}
```

**Edge Optimizations:**
- **Memory**: In-memory routing table (max 100 nodes)
- **CPU**: Simple routing (no complex algorithms)
- **Power**: Skip non-critical if battery <20%
- **Latency**: Compression reduces transmission time

**Deliverables:**
- Rust mesh network service
- LoRa integration
- Compression for mesh
- Resource-aware routing
- Performance benchmarks

---

##### **Week 3-4: Lightweight Monitoring**
**Objective**: Implement edge-optimized monitoring

**Edge Monitoring Design:**
```python
# backend/shared/edge_monitoring.py
# Edge-optimized monitoring (minimal overhead)

class EdgeMonitoring:
    """Lightweight monitoring for edge."""
    
    def __init__(self):
        # In-memory metrics (no external service)
        self.metrics = {
            "memory_usage": [],
            "cpu_usage": [],
            "power_consumption": [],
            "response_times": [],
        }
        
        # Alert thresholds
        self.thresholds = {
            "memory_usage": 0.9,  # 90% memory usage
            "cpu_usage": 0.8,  # 80% CPU usage
            "battery_level": 0.2,  # 20% battery
        }
    
    async def collect_metrics(self):
        """Collect metrics (lightweight, <10ms)."""
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics["memory_usage"].append(memory.percent)
        
        # CPU usage (1s average)
        cpu = psutil.cpu_percent(interval=1)
        self.metrics["cpu_usage"].append(cpu)
        
        # Power (if available)
        battery = self.get_battery_level()
        if battery:
            self.metrics["power_consumption"].append(battery)
        
        # Check thresholds
        await self.check_alerts()
    
    async def check_alerts(self):
        """Check for alerts (memory-efficient)."""
        if self.metrics["memory_usage"][-1] > self.thresholds["memory_usage"] * 100:
            await self.alert("High memory usage")
        
        if self.metrics["cpu_usage"][-1] > self.thresholds["cpu_usage"] * 100:
            await self.alert("High CPU usage")
        
        battery = self.metrics.get("power_consumption", [0])[-1]
        if battery < self.thresholds["battery_level"] * 100:
            await self.alert("Low battery")
```

**Edge Optimizations:**
- **Memory**: In-memory metrics (max 1000 samples)
- **CPU**: Lightweight collection (<10ms)
- **Storage**: No persistent logging (memory only)
- **Power**: Minimal overhead

**Deliverables:**
- Edge monitoring service
- Lightweight metrics collection
- Alert system
- Resource monitoring
- Performance benchmarks

---

#### **Month 6: Testing & Optimization**

##### **Week 1-2: Edge Testing Infrastructure**
**Objective**: Create testing framework for edge hardware

**Edge Testing Approach:**
- **Hardware-in-the-loop**: Test on real Raspberry Pi
- **Resource constraints**: Test with memory/CPU limits
- **Power testing**: Test with battery simulation
- **Performance testing**: Measure actual performance

**Deliverables:**
- Edge testing framework
- Hardware test suite
- Resource constraint tests
- Performance benchmarks
- Test reports

---

##### **Week 3-4: Optimization & Tuning**
**Objective**: Optimize for edge constraints

**Optimization Areas:**
- **Memory**: Reduce allocations, reuse buffers
- **CPU**: Optimize hot paths, reduce context switches
- **Power**: Reduce CPU frequency, batch operations
- **Storage**: Minimize writes, use caching

**Deliverables:**
- Optimization report
- Performance improvements
- Resource usage reduction
- Power consumption reduction

---

### **Phase 3: Production Readiness (Months 7-9)**

#### **Month 7: Security & Authentication**

##### **Week 1-2: Edge-Optimized Security**
**Objective**: Implement security without heavy overhead

**Edge Security Design:**
- **Lightweight auth**: Token-based (no heavy crypto)
- **Minimal encryption**: AES-128 (not AES-256, faster)
- **No external services**: Self-contained
- **Resource-aware**: Skip non-critical security if low resources

**Deliverables:**
- Edge security implementation
- Lightweight authentication
- Minimal encryption
- Security testing

---

##### **Week 3-4: Emergency Response Hardening**
**Objective**: Harden emergency response features

**Deliverables:**
- Emergency response testing
- Disaster scenario validation
- Performance under load
- Reliability testing

---

#### **Month 8: API Gateway & Integration**

##### **Week 1-2: Edge API Gateway**
**Objective**: Implement lightweight API gateway

**Edge API Gateway:**
- **Minimal overhead**: Direct routing (no heavy processing)
- **Resource-aware**: Skip non-critical features if low resources
- **Caching**: In-memory cache (reduce processing)

**Deliverables:**
- Edge API gateway
- Service integration
- API documentation
- Performance benchmarks

---

##### **Week 3-4: End-to-End Integration**
**Objective**: Complete end-to-end integration

**Deliverables:**
- Complete integration
- End-to-end testing
- Performance validation
- Documentation

---

#### **Month 9: Deployment & Validation**

##### **Week 1-2: Deployment Automation**
**Objective**: Automate edge deployment

**Edge Deployment:**
- **Minimal setup**: Automated hardware configuration
- **Resource validation**: Check hardware before deployment
- **Configuration**: Automated edge-specific config

**Deliverables:**
- Deployment automation
- Hardware validation
- Configuration management
- Deployment scripts

---

##### **Week 3-4: Production Validation**
**Objective**: Validate production readiness

**Deliverables:**
- Production testing
- Performance validation
- Resource usage validation
- Production readiness report

---

## 📊 **Resource Usage Targets**

### **Memory Budget (8GB RAM)**
```
OS & System:        1.0GB
Rust Services:      0.5GB (SMS, Router, Compression, Mesh)
Python Services:    1.5GB (LLM, RAG)
Models:             2.0GB (TinyLlama 4-bit)
Database Cache:     0.5GB (SQLite)
Monitoring:         0.1GB
Buffer:             1.4GB (headroom)
─────────────────────────
Total:              7.0GB (87.5% utilization)
```

### **CPU Budget (4 cores)**
```
SMS Gateway:        Core 0 (25%)
Message Router:     Core 1 (25%)
LLM Inference:      Core 2 (50%)
RAG Service:         Core 3 (25%)
Other Services:      Shared (25%)
─────────────────────────
Total:              150% (some overlap, acceptable)
```

### **Power Budget (15W)**
```
Raspberry Pi:       5-10W (idle-active)
GSM HAT:            2-5W (idle-transmitting)
LoRa HAT:           0.5-1W (idle-transmitting)
Services:           2-4W (idle-active)
─────────────────────────
Total:              9.5-20W (within 15W target with headroom)
```

### **Storage Budget (128GB)**
```
OS:                 8GB
Models:             5GB (compressed, quantized)
Database:           2GB (SQLite, with growth)
Logs:               1GB (rotated, minimal)
Services:           2GB
Buffer:             110GB (headroom)
─────────────────────────
Total:              18GB (14% utilization)
```

---

## 🎯 **Success Metrics**

### **Performance Targets**
- **SMS Response Time**: <10s (target: <15s)
- **Memory Usage**: <7GB (target: <8GB)
- **Power Consumption**: <12W idle, <15W active
- **CPU Usage**: <80% average
- **Storage Usage**: <20GB

### **Reliability Targets**
- **Uptime**: >99% (24/7 operation)
- **Message Delivery**: >95% success rate
- **Emergency Response**: <5s latency
- **Battery Runtime**: >24h (with solar backup)

---

## 🏆 **Conclusion**

This implementation plan provides a comprehensive, edge-focused approach to building EVY with:
- ✅ **Rust refactoring** for critical path components
- ✅ **Compression engine** for SMS optimization
- ✅ **Edge constraints** respected throughout
- ✅ **Resource awareness** built into every component
- ✅ **Emergency response** features prioritized
- ✅ **Realistic timeline** (9 months to production)

**Key Principles:**
1. **Memory Efficiency**: Every component optimized for memory
2. **Power Awareness**: Battery-aware operations throughout
3. **Resource Monitoring**: Continuous monitoring and adaptation
4. **Fault Tolerance**: Graceful degradation under constraints
5. **Edge-First**: Designed for edge, not adapted from cloud

**Next Steps:**
1. Begin Phase 1 (Hardware Validation)
2. Implement Rust SMS Gateway
3. Build Compression Engine
4. Integrate services
5. Test on real hardware

---

*Last Updated: Edge Implementation Plan - Focused on Hardware Constraints*

