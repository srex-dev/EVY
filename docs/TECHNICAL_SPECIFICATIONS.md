# EVY Technical Specifications
## Detailed Component Specifications for Implementation

### Document Purpose
This document provides detailed technical specifications for all EVY components, enabling developers to implement without ambiguity. Each specification includes interfaces, data structures, algorithms, and edge constraints.

**Last Updated**: [Date]
**Status**: Ready for Implementation
**Target Hardware**: Raspberry Pi 4 (8GB RAM, ARM64)

---

## 📋 **Table of Contents**

1. [Rust SMS Gateway](#rust-sms-gateway)
2. [Rust Message Router](#rust-message-router)
3. [Rust Compression Engine](#rust-compression-engine)
4. [Rust Mesh Network](#rust-mesh-network)
5. [Python LLM Service](#python-llm-service)
6. [Python RAG Service](#python-rag-service)
7. [Python Emergency Service](#python-emergency-service)
8. [SQLite Database](#sqlite-database)
9. [Service Integration](#service-integration)
10. [Resource Monitoring](#resource-monitoring)

---

## 📱 **Rust SMS Gateway**

### **Component Overview**
High-performance SMS gateway implemented in Rust for edge deployment. Handles SMS send/receive with minimal latency and memory usage.

### **Interface Specification**

```rust
// backend-rust/sms_gateway/src/lib.rs

use std::sync::Arc;
use tokio::sync::mpsc;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SMSMessage {
    pub phone_number: String,      // E.164 format: +1234567890
    pub content: String,           // Max 160 characters (GSM 7-bit)
    pub timestamp: u64,            // Unix timestamp
    pub priority: MessagePriority, // Normal, High, Emergency
    pub id: Option<String>,        // Optional message ID
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessagePriority {
    Normal,
    High,
    Emergency,
}

#[derive(Debug, Clone)]
pub struct SMSGatewayConfig {
    pub device_path: String,           // e.g., "/dev/ttyUSB1"
    pub baud_rate: u32,                // Default: 9600
    pub max_queue_size: usize,         // Default: 1000
    pub retry_attempts: u8,            // Default: 3
    pub retry_delay_ms: u64,           // Default: 1000
    pub power_threshold: f32,          // Battery threshold (0.0-1.0)
    pub memory_threshold_mb: usize,    // Memory threshold in MB
}

pub struct EdgeSMSGateway {
    config: SMSGatewayConfig,
    gsm_device: Arc<GsmDevice>,
    message_queue: mpsc::UnboundedReceiver<SMSMessage>,
    power_monitor: Arc<PowerMonitor>,
    memory_monitor: Arc<MemoryMonitor>,
    stats: Arc<Mutex<GatewayStats>>,
}

#[derive(Debug, Default)]
pub struct GatewayStats {
    pub messages_sent: u64,
    pub messages_received: u64,
    pub messages_failed: u64,
    pub average_latency_ms: f64,
    pub last_message_time: Option<u64>,
}

impl EdgeSMSGateway {
    /// Initialize SMS gateway with configuration
    pub async fn new(config: SMSGatewayConfig) -> Result<Self, GatewayError>;
    
    /// Send SMS message (non-blocking)
    pub async fn send(&mut self, message: SMSMessage) -> Result<String, GatewayError>;
    
    /// Receive SMS message (non-blocking)
    pub async fn receive(&mut self) -> Result<Option<SMSMessage>, GatewayError>;
    
    /// Check if gateway is ready (power, memory checks)
    pub async fn is_ready(&self) -> Result<bool, GatewayError>;
    
    /// Get gateway statistics
    pub fn get_stats(&self) -> GatewayStats;
    
    /// Shutdown gateway gracefully
    pub async fn shutdown(&mut self) -> Result<(), GatewayError>;
}
```

### **Data Structures**

```rust
// Message format (GSM 7-bit encoding)
pub struct GSMMessage {
    pub phone_number: [u8; 20],  // BCD encoded
    pub content: [u8; 160],       // GSM 7-bit encoded
    pub length: u8,               // Actual length
}

// Error types
#[derive(Debug)]
pub enum GatewayError {
    DeviceNotFound,
    DeviceBusy,
    LowMemory,
    LowBattery,
    InvalidPhoneNumber,
    MessageTooLong,
    TransmissionFailed,
    Timeout,
}
```

### **Algorithms**

#### **Message Queue Management**
```rust
// Priority queue implementation (binary heap)
use std::collections::BinaryHeap;
use std::cmp::Ordering;

#[derive(Eq, PartialEq)]
struct QueuedMessage {
    message: SMSMessage,
    priority: u8,  // 0=Normal, 1=High, 2=Emergency
    timestamp: u64,
}

impl Ord for QueuedMessage {
    fn cmp(&self, other: &Self) -> Ordering {
        // Emergency messages first, then by timestamp
        match self.priority.cmp(&other.priority) {
            Ordering::Equal => other.timestamp.cmp(&self.timestamp),
            other => other,
        }
    }
}

impl PartialOrd for QueuedMessage {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
```

#### **Power-Aware Processing**
```rust
impl EdgeSMSGateway {
    async fn send_with_power_check(&mut self, message: SMSMessage) -> Result<String> {
        // Check battery level
        let battery = self.power_monitor.get_battery_level().await?;
        
        if battery < self.config.power_threshold {
            // Low battery: only send emergency messages
            if message.priority != MessagePriority::Emergency {
                return Err(GatewayError::LowBattery);
            }
        }
        
        // Check memory
        let available_memory = self.memory_monitor.available_memory().await?;
        if available_memory < self.config.memory_threshold_mb * 1024 * 1024 {
            return Err(GatewayError::LowMemory);
        }
        
        // Send message
        self.send(message).await
    }
}
```

### **Edge Constraints**

- **Memory**: Max 100MB heap allocation
- **CPU**: Process messages in batches (max 10 at a time)
- **Power**: Skip non-emergency if battery <20%
- **Latency**: Target <50ms per message
- **Storage**: No persistent queue (in-memory only)

### **Performance Targets**

- **Latency**: <50ms (send), <100ms (receive)
- **Throughput**: 10 messages/second
- **Memory**: <100MB
- **CPU**: <25% (one core)
- **Power**: <2W (idle), <5W (transmitting)

---

## 🧭 **Rust Message Router**

### **Component Overview**
High-performance message router with rule-based intent classification and resource-aware service selection.

### **Interface Specification**

```rust
// backend-rust/message_router/src/lib.rs

use std::sync::Arc;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Route {
    pub service: ServiceType,
    pub priority: RoutePriority,
    pub estimated_latency_ms: u64,
    pub resource_cost: ResourceCost,
}

#[derive(Debug, Clone)]
pub enum ServiceType {
    LocalLLM,        // Tiny LLM on edge
    LocalRAG,        // Local RAG service
    TemplateResponse, // Pre-loaded templates
    BigEVY,          // Forward to bigEVY (if available)
}

#[derive(Debug, Clone)]
pub struct ResourceCost {
    pub memory_mb: usize,
    pub cpu_percent: f32,
    pub power_w: f32,
}

#[derive(Debug, Clone)]
pub struct Intent {
    pub category: IntentCategory,
    pub confidence: f32,
    pub keywords: Vec<String>,
}

#[derive(Debug, Clone)]
pub enum IntentCategory {
    Emergency,
    SimpleQuery,
    ComplexQuery,
    RAGQuery,
    Unknown,
}

pub struct EdgeMessageRouter {
    intent_classifier: RuleBasedClassifier,
    service_registry: Arc<ServiceRegistry>,
    routing_cache: Arc<RwLock<LruCache<String, Route>>>,
    resource_monitor: Arc<ResourceMonitor>,
}

impl EdgeMessageRouter {
    /// Route message to appropriate service
    pub async fn route(&mut self, message: &str) -> Result<Route, RouterError>;
    
    /// Classify message intent
    pub fn classify_intent(&self, message: &str) -> Intent;
    
    /// Select service based on intent and resources
    pub async fn select_service(&self, intent: &Intent) -> Result<Route, RouterError>;
    
    /// Get router statistics
    pub fn get_stats(&self) -> RouterStats;
}
```

### **Intent Classification Algorithm**

```rust
// Rule-based classifier (no ML model, fast)
pub struct RuleBasedClassifier {
    patterns: Vec<CompiledPattern>,
    emergency_keywords: Vec<String>,
    simple_keywords: Vec<String>,
    complex_keywords: Vec<String>,
}

impl RuleBasedClassifier {
    pub fn classify(&self, message: &str) -> Intent {
        let message_lower = message.to_lowercase();
        
        // Check for emergency (highest priority)
        if self.is_emergency(&message_lower) {
            return Intent {
                category: IntentCategory::Emergency,
                confidence: 1.0,
                keywords: self.extract_keywords(&message_lower),
            };
        }
        
        // Check for simple query
        if self.is_simple_query(&message_lower) {
            return Intent {
                category: IntentCategory::SimpleQuery,
                confidence: 0.8,
                keywords: self.extract_keywords(&message_lower),
            };
        }
        
        // Check for complex query
        if self.is_complex_query(&message_lower) {
            return Intent {
                category: IntentCategory::ComplexQuery,
                confidence: 0.7,
                keywords: self.extract_keywords(&message_lower),
            };
        }
        
        // Default: unknown
        Intent {
            category: IntentCategory::Unknown,
            confidence: 0.5,
            keywords: vec![],
        }
    }
    
    fn is_emergency(&self, message: &str) -> bool {
        self.emergency_keywords.iter()
            .any(|keyword| message.contains(keyword))
    }
    
    fn is_simple_query(&self, message: &str) -> bool {
        // Simple queries: short, common words, yes/no questions
        message.len() < 50 && 
        (message.contains("?") || 
         self.simple_keywords.iter().any(|k| message.contains(k)))
    }
    
    fn is_complex_query(&self, message: &str) -> bool {
        // Complex queries: long, multiple clauses, technical terms
        message.len() > 50 ||
        self.complex_keywords.iter().any(|k| message.contains(k))
    }
}
```

### **Resource-Aware Routing**

```rust
impl EdgeMessageRouter {
    async fn select_service(&self, intent: &Intent) -> Result<Route> {
        let resources = self.resource_monitor.get_resources().await?;
        
        match intent.category {
            IntentCategory::Emergency => {
                // Emergency: always use local LLM (fastest)
                Ok(Route {
                    service: ServiceType::LocalLLM,
                    priority: RoutePriority::Emergency,
                    estimated_latency_ms: 5000,  // 5s
                    resource_cost: ResourceCost {
                        memory_mb: 200,
                        cpu_percent: 50.0,
                        power_w: 3.0,
                    },
                })
            }
            
            IntentCategory::SimpleQuery => {
                // Simple: use templates if memory low, else local LLM
                if resources.available_memory_mb < 200 {
                    Ok(Route {
                        service: ServiceType::TemplateResponse,
                        priority: RoutePriority::Normal,
                        estimated_latency_ms: 100,  // 100ms
                        resource_cost: ResourceCost {
                            memory_mb: 10,
                            cpu_percent: 5.0,
                            power_w: 0.5,
                        },
                    })
                } else {
                    Ok(Route {
                        service: ServiceType::LocalLLM,
                        priority: RoutePriority::Normal,
                        estimated_latency_ms: 5000,
                        resource_cost: ResourceCost {
                            memory_mb: 200,
                            cpu_percent: 50.0,
                            power_w: 3.0,
                        },
                    })
                }
            }
            
            IntentCategory::ComplexQuery => {
                // Complex: try bigEVY if battery >50%, else local
                if resources.battery_level > 0.5 {
                    Ok(Route {
                        service: ServiceType::BigEVY,
                        priority: RoutePriority::Normal,
                        estimated_latency_ms: 30000,  // 30s
                        resource_cost: ResourceCost {
                            memory_mb: 50,
                            cpu_percent: 10.0,
                            power_w: 1.0,
                        },
                    })
                } else {
                    Ok(Route {
                        service: ServiceType::LocalLLM,
                        priority: RoutePriority::Normal,
                        estimated_latency_ms: 10000,  // 10s
                        resource_cost: ResourceCost {
                            memory_mb: 200,
                            cpu_percent: 50.0,
                            power_w: 3.0,
                        },
                    })
                }
            }
            
            _ => {
                // Unknown: use template response
                Ok(Route {
                    service: ServiceType::TemplateResponse,
                    priority: RoutePriority::Low,
                    estimated_latency_ms: 100,
                    resource_cost: ResourceCost {
                        memory_mb: 10,
                        cpu_percent: 5.0,
                        power_w: 0.5,
                    },
                })
            }
        }
    }
}
```

### **Edge Constraints**

- **Memory**: Max 30MB (routing cache: 1000 entries)
- **CPU**: Classification <10ms
- **Latency**: Routing <50ms
- **Storage**: No persistent storage (in-memory only)

### **Performance Targets**

- **Routing Latency**: <50ms
- **Classification Time**: <10ms
- **Memory Usage**: <30MB
- **CPU Usage**: <25% (one core)

---

## 🗜️ **Rust Compression Engine**

### **Component Overview**
Edge-optimized compression engine for SMS responses, using rule-based compression with optional tiny model support.

### **Interface Specification**

```rust
// backend-rust/compression/src/lib.rs

use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct CompressionConfig {
    pub target_length: usize,           // Target length (default: 160)
    pub compression_level: f32,          // 0.0-1.0 (aggressiveness)
    pub use_model: bool,                 // Use tiny model if available
    pub memory_threshold_mb: usize,      // Memory threshold for model
    pub battery_threshold: f32,          // Battery threshold for model
}

pub struct EdgeCompressionEngine {
    rule_compressor: RuleBasedCompressor,
    tiny_model: Option<Arc<TinyCompressionModel>>,
    compression_cache: Arc<RwLock<LruCache<String, String>>>,
    resource_monitor: Arc<ResourceMonitor>,
    config: CompressionConfig,
}

impl EdgeCompressionEngine {
    /// Compress text to target length
    pub async fn compress(
        &mut self,
        text: &str,
        target_length: usize,
    ) -> Result<String, CompressionError>;
    
    /// Compress with resource awareness
    pub async fn compress_with_resources(
        &mut self,
        text: &str,
        target_length: usize,
    ) -> Result<String, CompressionError>;
    
    /// Get compression statistics
    pub fn get_stats(&self) -> CompressionStats;
}
```

### **Compression Algorithms**

#### **Rule-Based Compressor**
```rust
pub struct RuleBasedCompressor {
    // Pre-compiled regex patterns
    patterns: Vec<Regex>,
    
    // Abbreviation dictionary
    abbreviations: HashMap<String, String>,
    
    // Common phrase replacements
    phrases: HashMap<String, String>,
}

impl RuleBasedCompressor {
    pub fn compress(&self, text: &str, target: usize) -> String {
        let mut result = String::with_capacity(target);
        result.push_str(text);
        
        // Apply phrase replacements
        for (phrase, replacement) in &self.phrases {
            result = result.replace(phrase, replacement);
        }
        
        // Apply abbreviations
        for (word, abbrev) in &self.abbreviations {
            result = result.replace(word, abbrev);
        }
        
        // Apply regex patterns
        for pattern in &self.patterns {
            result = pattern.replace_all(&result, |caps: &Captures| {
                self.abbreviations.get(caps.get(0).unwrap().as_str())
                    .cloned()
                    .unwrap_or_else(|| caps.get(0).unwrap().as_str().to_string())
            }).to_string();
        }
        
        // Remove extra whitespace
        result = result.split_whitespace().collect::<Vec<_>>().join(" ");
        
        // Truncate if still too long
        if result.len() > target {
            result.truncate(target - 3);
            result.push_str("...");
        }
        
        result
    }
}

// Example abbreviations
lazy_static! {
    static ref ABBREVIATIONS: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        m.insert("emergency", "EMERG");
        m.insert("immediately", "NOW");
        m.insert("hospital", "HOSP");
        m.insert("contact", "CONT");
        m.insert("information", "INFO");
        m.insert("procedure", "PROC");
        m.insert("evacuate", "EVAC");
        m.insert("shelter", "SHEL");
        // ... more abbreviations
        m
    };
}

// Example phrase replacements
lazy_static! {
    static ref PHRASES: HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        m.insert("call 911", "911");
        m.insert("for more information", "more info");
        m.insert("as soon as possible", "ASAP");
        m.insert("in case of emergency", "if EMERG");
        // ... more phrases
        m
    };
}
```

#### **Resource-Aware Compression**
```rust
impl EdgeCompressionEngine {
    async fn compress_with_resources(
        &mut self,
        text: &str,
        target_length: usize,
    ) -> Result<String> {
        // Check cache first
        if let Some(cached) = self.compression_cache.read().await.get(text) {
            if cached.len() <= target_length {
                return Ok(cached.clone());
            }
        }
        
        // Check available memory
        let available_memory = self.resource_monitor.available_memory().await?;
        if available_memory < self.config.memory_threshold_mb * 1024 * 1024 {
            // Low memory: use rule-based only
            let compressed = self.rule_compressor.compress(text, target_length);
            self.compression_cache.write().await.put(
                text.to_string(),
                compressed.clone()
            );
            return Ok(compressed);
        }
        
        // Check battery level
        let battery = self.resource_monitor.battery_level().await?;
        if battery < self.config.battery_threshold {
            // Low battery: use rule-based only
            let compressed = self.rule_compressor.compress(text, target_length);
            self.compression_cache.write().await.put(
                text.to_string(),
                compressed.clone()
            );
            return Ok(compressed);
        }
        
        // Try rule-based first (fast, <0.5s)
        let compressed = self.rule_compressor.compress(text, target_length);
        if compressed.len() <= target_length {
            self.compression_cache.write().await.put(
                text.to_string(),
                compressed.clone()
            );
            return Ok(compressed);
        }
        
        // Try tiny model if available (moderate, <1.5s)
        if let Some(ref model) = self.tiny_model {
            if self.config.use_model && available_memory > 200_000_000 {
                match model.compress(text, target_length).await {
                    Ok(compressed) => {
                        if compressed.len() <= target_length {
                            self.compression_cache.write().await.put(
                                text.to_string(),
                                compressed.clone()
                            );
                            return Ok(compressed);
                        }
                    }
                    Err(_) => {
                        // Model failed, fall back to rule-based
                    }
                }
            }
        }
        
        // Final fallback: aggressive rule-based
        let compressed = self.rule_compressor.compress_aggressive(text, target_length);
        self.compression_cache.write().await.put(
            text.to_string(),
            compressed.clone()
        );
        Ok(compressed)
    }
}
```

### **Edge Constraints**

- **Memory**: Max 50MB (compression cache: 1000 entries)
- **CPU**: Compression <2s (target: <1s)
- **Power**: Skip model if battery <30%
- **Storage**: No persistent storage (in-memory cache only)

### **Performance Targets**

- **Compression Time**: <1s (rule-based), <1.5s (with model)
- **Compression Ratio**: 40-50% (vs 20-30% truncation)
- **Memory Usage**: <50MB
- **CPU Usage**: <30% (one core)

---

## 📡 **Rust Mesh Network**

### **Component Overview**
High-performance mesh networking over LoRa radio, with compression and resource-aware routing.

### **Interface Specification**

```rust
// backend-rust/mesh_network/src/lib.rs

use std::sync::Arc;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshMessage {
    pub source_node: String,
    pub destination_node: String,
    pub message_type: MessageType,
    pub content: Vec<u8>,           // Compressed content
    pub priority: MessagePriority,
    pub timestamp: u64,
    pub hop_count: u8,
    pub max_hops: u8,
}

#[derive(Debug, Clone)]
pub enum MessageType {
    Data,
    RouteRequest,
    RouteReply,
    Heartbeat,
    Emergency,
}

pub struct EdgeMeshNetwork {
    lora_radio: Arc<LoRaRadio>,
    routing_table: Arc<RwLock<RoutingTable>>,
    message_queue: mpsc::UnboundedReceiver<MeshMessage>,
    compressor: Arc<CompressionEngine>,
    resource_monitor: Arc<ResourceMonitor>,
    node_id: String,
}

impl EdgeMeshNetwork {
    /// Send message via mesh network
    pub async fn send(&mut self, message: MeshMessage) -> Result<(), MeshError>;
    
    /// Receive message from mesh network
    pub async fn receive(&mut self) -> Result<Option<MeshMessage>, MeshError>;
    
    /// Find route to destination
    pub async fn find_route(&self, destination: &str) -> Result<Route, MeshError>;
    
    /// Update routing table
    pub async fn update_routing_table(&mut self, updates: Vec<RouteUpdate>);
    
    /// Get network statistics
    pub fn get_stats(&self) -> MeshStats;
}
```

### **Routing Algorithm**

```rust
// Simple routing table (memory-efficient)
pub struct RoutingTable {
    routes: HashMap<String, RouteEntry>,
    max_entries: usize,  // Default: 100
}

pub struct RouteEntry {
    destination: String,
    next_hop: String,
    hop_count: u8,
    last_update: u64,
    quality: f32,  // 0.0-1.0 (signal quality)
}

impl EdgeMeshNetwork {
    async fn find_route(&self, destination: &str) -> Result<Route> {
        let table = self.routing_table.read().await;
        
        // Check routing table
        if let Some(entry) = table.routes.get(destination) {
            // Check if route is still valid (within 60s)
            if entry.last_update + 60 > current_timestamp() {
                return Ok(Route {
                    next_hop: entry.next_hop.clone(),
                    hop_count: entry.hop_count,
                    quality: entry.quality,
                });
            }
        }
        
        // Route not found: broadcast discovery
        drop(table);
        self.broadcast_route_request(destination).await?;
        
        // Wait for route reply (timeout: 5s)
        tokio::time::timeout(
            Duration::from_secs(5),
            self.wait_for_route_reply(destination)
        ).await?
    }
}
```

### **Edge Constraints**

- **Memory**: Max 50MB (routing table: 100 nodes)
- **CPU**: Routing <100ms
- **Power**: Skip non-critical if battery <20%
- **Latency**: Transmission <5s (with compression)

### **Performance Targets**

- **Transmission Time**: <2.5s (compressed)
- **Routing Time**: <100ms
- **Memory Usage**: <50MB
- **Power Consumption**: <1W (transmitting)

---

## 🤖 **Python LLM Service**

### **Component Overview**
Edge-optimized LLM inference service using llama.cpp with 4-bit quantization.

### **Interface Specification**

```python
# backend/services/llm_inference/edge_llm_service.py

from typing import Optional, Dict, Any
from dataclasses import dataclass
from llama_cpp import Llama

@dataclass
class LLMConfig:
    model_path: str
    n_ctx: int = 512          # Context window (edge constraint)
    n_threads: int = 2        # Threads (leave cores for other services)
    n_gpu_layers: int = 0     # No GPU on edge
    verbose: bool = False
    use_mmap: bool = True     # Memory-mapped I/O
    use_mlock: bool = False   # Don't lock memory (save RAM)

@dataclass
class GenerationConfig:
    max_tokens: int = 50       # Max tokens (edge constraint)
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    stop: list[str] = None

class EdgeLLMService:
    """Edge-optimized LLM service."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model: Optional[Llama] = None
        self.memory_monitor = MemoryMonitor()
        self.stats = LLMStats()
    
    async def initialize(self) -> bool:
        """Initialize LLM model with edge constraints."""
        # Check available memory
        available = await self.memory_monitor.available_memory()
        required = 2_000_000_000  # 2GB for 4-bit model
        
        if available < required:
            logger.error(f"Insufficient memory: {available} < {required}")
            return False
        
        try:
            # Load model with edge optimizations
            self.model = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                verbose=self.config.verbose,
                use_mmap=self.config.use_mmap,
                use_mlock=self.config.use_mlock,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """Generate response with edge constraints."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        # Check memory before generation
        available = await self.memory_monitor.available_memory()
        if available < 100_000_000:  # 100MB threshold
            raise RuntimeError("Insufficient memory for generation")
        
        # Use default config if not provided
        if config is None:
            config = GenerationConfig()
        
        # Generate (limited tokens for edge)
        response = self.model(
            prompt,
            max_tokens=min(config.max_tokens, 50),  # Edge constraint
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            stop=config.stop or ["\n\n", "User:", "EVY:"],
        )
        
        # Extract text from response
        text = response["choices"][0]["text"].strip()
        
        # Update statistics
        self.stats.total_generations += 1
        self.stats.total_tokens += len(text.split())
        
        return text
```

### **Edge Constraints**

- **Memory**: 2GB for model (4-bit quantization)
- **CPU**: 2 threads (leave cores for other services)
- **Context**: 512 tokens (small context window)
- **Tokens**: Max 50 tokens per generation

### **Performance Targets**

- **Generation Time**: <10s (target: <15s)
- **Memory Usage**: <2GB (model)
- **CPU Usage**: <50% (2 threads)
- **Tokens/Second**: ~5-10 tokens/s

---

## 📚 **Python RAG Service**

### **Component Overview**
Edge-optimized RAG service using FAISS with local knowledge base.

### **Interface Specification**

```python
# backend/services/rag_service/edge_rag_service.py

from typing import List, Optional
from dataclasses import dataclass
import faiss
import numpy as np

@dataclass
class RAGConfig:
    knowledge_base_path: str
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight model
    max_documents: int = 10000                 # Edge constraint
    cache_size_mb: int = 500                   # Memory cache
    top_k: int = 3                             # Results to return

class EdgeRAGService:
    """Edge-optimized RAG service."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.index: Optional[faiss.Index] = None
        self.documents: List[str] = []
        self.embedding_model = None
        self.memory_monitor = MemoryMonitor()
    
    async def initialize(self) -> bool:
        """Initialize RAG service with edge constraints."""
        # Check available memory
        available = await self.memory_monitor.available_memory()
        required = self.config.cache_size_mb * 1024 * 1024
        
        if available < required:
            logger.error(f"Insufficient memory: {available} < {required}")
            return False
        
        try:
            # Load embedding model (lightweight)
            self.embedding_model = SentenceTransformer(
                self.config.embedding_model
            )
            
            # Load knowledge base
            await self.load_knowledge_base()
            
            # Create FAISS index
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add documents to index
            await self.build_index()
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            return False
    
    async def search(self, query: str, top_k: Optional[int] = None) -> List[str]:
        """Search knowledge base."""
        if not self.index:
            raise RuntimeError("RAG service not initialized")
        
        # Check memory
        available = await self.memory_monitor.available_memory()
        if available < 100_000_000:  # 100MB threshold
            return []  # Return empty if low memory
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search index
        k = top_k or self.config.top_k
        distances, indices = self.index.search(query_embedding, k)
        
        # Return documents
        results = [self.documents[i] for i in indices[0] if i < len(self.documents)]
        return results
```

### **Edge Constraints**

- **Memory**: 500MB cache
- **Documents**: Max 10,000 documents
- **Embeddings**: Lightweight model (all-MiniLM-L6-v2)
- **Search**: Top 3 results only

### **Performance Targets**

- **Search Time**: <500ms
- **Memory Usage**: <500MB
- **CPU Usage**: <25% (one core)

---

## 🚨 **Python Emergency Service**

### **Component Overview**
Emergency response service with pre-loaded templates and pattern matching.

### **Interface Specification**

```python
# backend/lilevy/services/emergency_service.py

from typing import Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class EmergencyTemplate:
    keyword: str
    response: str
    priority: int
    compression_needed: bool

class EdgeEmergencyService:
    """Edge-optimized emergency response service."""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.emergency_keywords = self._load_keywords()
        self.compressor = None  # Set after initialization
        self.resource_monitor = ResourceMonitor()
    
    def _load_templates(self) -> Dict[str, EmergencyTemplate]:
        """Load emergency templates (pre-loaded, memory-efficient)."""
        return {
            "hurricane": EmergencyTemplate(
                keyword="hurricane",
                response="URGENT: Hurricane warning. Evacuate now to shelters. Bring: water, food, meds, docs. Contact: 911.",
                priority=1,
                compression_needed=False,
            ),
            "earthquake": EmergencyTemplate(
                keyword="earthquake",
                response="URGENT: Earthquake. Drop, cover, hold. Stay indoors. Avoid windows. Contact: 911.",
                priority=1,
                compression_needed=False,
            ),
            # ... more templates
        }
    
    def _load_keywords(self) -> List[str]:
        """Load emergency keywords (pre-compiled regex)."""
        return [
            r'\b(emergency|urgent|help|911|fire|hurricane|earthquake)\b',
            r'\b(evacuate|danger|dangerous|critical)\b',
            r'\b(medical|ambulance|hospital|injured)\b',
        ]
    
    async def handle_emergency(self, message: str) -> Optional[str]:
        """Handle emergency message."""
        # Check if emergency (fast pattern matching)
        if not self._is_emergency(message):
            return None
        
        # Get emergency response (pre-loaded, fast)
        response = self._get_emergency_response(message)
        
        # Compress if needed (resource-aware)
        if len(response) > 160:
            battery = await self.resource_monitor.get_battery_level()
            if battery > 0.2 and self.compressor:  # Only compress if battery available
                response = await self.compressor.compress(response, 160)
            else:
                # Low battery: truncate (faster)
                response = response[:157] + "..."
        
        return response
    
    def _is_emergency(self, message: str) -> bool:
        """Fast emergency detection (pattern matching)."""
        message_lower = message.lower()
        for pattern in self.emergency_keywords:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _get_emergency_response(self, message: str) -> str:
        """Get emergency response from templates."""
        message_lower = message.lower()
        
        # Check templates in priority order
        for keyword, template in sorted(
            self.templates.items(),
            key=lambda x: x[1].priority
        ):
            if keyword in message_lower:
                return template.response
        
        # Default emergency response
        return "EMERGENCY: Call 911 immediately. Stay safe. Follow local emergency procedures."
```

### **Edge Constraints**

- **Memory**: <1MB (templates)
- **CPU**: Detection <10ms
- **Latency**: Response <5s
- **Storage**: Pre-loaded (no database queries)

### **Performance Targets**

- **Detection Time**: <10ms
- **Response Time**: <5s
- **Memory Usage**: <1MB
- **CPU Usage**: <5%

---

## 💾 **SQLite Database**

### **Component Overview**
Lightweight SQLite database optimized for edge constraints.

### **Schema Specification**

```sql
-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    response TEXT,
    priority INTEGER DEFAULT 0,
    INDEX idx_phone (phone_number),
    INDEX idx_timestamp (timestamp),
    INDEX idx_priority (priority)
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    INDEX idx_metric (metric),
    INDEX idx_timestamp (timestamp)
);

-- Emergency logs table
CREATE TABLE IF NOT EXISTS emergency_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    INDEX idx_timestamp (timestamp)
);
```

### **Edge Optimizations**

```python
# SQLite pragmas for edge optimization
PRAGMA journal_mode = WAL;           # Write-Ahead Logging (faster writes)
PRAGMA synchronous = NORMAL;        # Balance safety/speed (not FULL)
PRAGMA cache_size = -32000;         # 32MB cache (memory-efficient)
PRAGMA temp_store = MEMORY;         # Use memory for temp tables
PRAGMA mmap_size = 268435456;       # 256MB memory-mapped I/O
PRAGMA page_size = 4096;            # 4KB pages (efficient)
```

### **Edge Constraints**

- **Size**: <2GB (with growth)
- **Writes**: Batch commits (every 10 messages or 60s)
- **Memory**: 32MB cache, 256MB mmap
- **Sync**: NORMAL (not FULL, faster)

---

## 🔗 **Service Integration**

### **PyO3 Bindings**

```rust
// backend-rust/pyo3_bindings/src/lib.rs

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn send_sms(phone: String, message: String) -> PyResult<String> {
    // Call Rust SMS gateway
    let gateway = EdgeSMSGateway::new(config)?;
    let msg = SMSMessage { phone_number: phone, content: message, ... };
    gateway.send(msg).await?;
    Ok("sent".to_string())
}

#[pyfunction]
fn route_message(message: String) -> PyResult<String> {
    // Call Rust message router
    let router = EdgeMessageRouter::new()?;
    let route = router.route(&message).await?;
    Ok(route.service.to_string())
}

#[pyfunction]
fn compress_text(text: String, target_length: usize) -> PyResult<String> {
    // Call Rust compression engine
    let compressor = EdgeCompressionEngine::new()?;
    let compressed = compressor.compress(&text, target_length).await?;
    Ok(compressed)
}

#[pymodule]
fn evy_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(send_sms, m)?)?;
    m.add_function(wrap_pyfunction!(route_message, m)?)?;
    m.add_function(wrap_pyfunction!(compress_text, m)?)?;
    Ok(())
}
```

### **Python Integration**

```python
# backend/shared/rust_bridge.py

import evy_rust  # PyO3 module

class RustBridge:
    """Bridge to Rust services."""
    
    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """Send SMS via Rust gateway."""
        try:
            result = evy_rust.send_sms(phone, message)
            return result == "sent"
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False
    
    @staticmethod
    def route_message(message: str) -> str:
        """Route message via Rust router."""
        try:
            return evy_rust.route_message(message)
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return "local_llm"  # Fallback
    
    @staticmethod
    def compress_text(text: str, target_length: int) -> str:
        """Compress text via Rust engine."""
        try:
            return evy_rust.compress_text(text, target_length)
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return text[:target_length]  # Fallback to truncation
```

---

## 📊 **Resource Monitoring**

### **Component Overview**
Lightweight resource monitoring for edge constraints.

### **Interface Specification**

```python
# backend/shared/resource_monitor.py

from dataclasses import dataclass
import psutil

@dataclass
class ResourceStatus:
    memory_total: int
    memory_available: int
    memory_percent: float
    cpu_percent: float
    battery_level: Optional[float]  # 0.0-1.0
    power_consumption: Optional[float]  # Watts

class ResourceMonitor:
    """Edge resource monitor."""
    
    def __init__(self):
        self.thresholds = {
            "memory": 0.9,      # 90% memory usage
            "cpu": 0.8,         # 80% CPU usage
            "battery": 0.2,     # 20% battery
        }
    
    async def get_resources(self) -> ResourceStatus:
        """Get current resource status."""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        battery = self.get_battery_level()
        power = self.get_power_consumption()
        
        return ResourceStatus(
            memory_total=memory.total,
            memory_available=memory.available,
            memory_percent=memory.percent / 100.0,
            cpu_percent=cpu / 100.0,
            battery_level=battery,
            power_consumption=power,
        )
    
    async def available_memory(self) -> int:
        """Get available memory in bytes."""
        return psutil.virtual_memory().available
    
    async def battery_level(self) -> Optional[float]:
        """Get battery level (0.0-1.0)."""
        # Implementation depends on hardware
        # Return None if not available
        return None
    
    def is_resource_available(self, resource: str) -> bool:
        """Check if resource is available."""
        status = asyncio.run(self.get_resources())
        
        if resource == "memory":
            return status.memory_percent < self.thresholds["memory"]
        elif resource == "cpu":
            return status.cpu_percent < self.thresholds["cpu"]
        elif resource == "battery":
            if status.battery_level is None:
                return True  # Assume available if not monitored
            return status.battery_level > self.thresholds["battery"]
        
        return False
```

---

## 🎯 **Performance Specifications**

### **Component Performance Targets**

| Component | Latency | Memory | CPU | Power |
|-----------|---------|--------|-----|-------|
| **SMS Gateway** | <50ms | <100MB | <25% | <2W |
| **Message Router** | <50ms | <30MB | <25% | <0.5W |
| **Compression** | <1s | <50MB | <30% | <1W |
| **Mesh Network** | <2.5s | <50MB | <25% | <1W |
| **LLM Service** | <10s | <2GB | <50% | <3W |
| **RAG Service** | <500ms | <500MB | <25% | <1W |
| **Emergency** | <5s | <1MB | <5% | <0.5W |

### **System-Wide Targets**

- **Total Memory**: <7GB (87.5% of 8GB)
- **Total CPU**: <150% (overlap acceptable)
- **Total Power**: <12W idle, <15W active
- **Response Time**: <15s (target: <10s)

---

## 📝 **Implementation Notes**

### **Edge-Specific Considerations**

1. **Memory Management**
   - Pre-allocate buffers where possible
   - Use memory pools for frequent allocations
   - Monitor memory usage continuously
   - Unload unused components

2. **Power Management**
   - Check battery level before operations
   - Skip non-critical features if battery low
   - Batch operations to reduce CPU spikes
   - Use CPU frequency scaling

3. **Storage Management**
   - Minimize writes (use WAL mode)
   - Batch commits (reduce microSD wear)
   - Use tmpfs for temporary files
   - Rotate logs aggressively

4. **Error Handling**
   - Graceful degradation under constraints
   - Fallback to simpler algorithms if resources low
   - Cache results to reduce computation
   - Monitor and alert on resource issues

---

**END OF TECHNICAL SPECIFICATIONS**

---

*This document provides detailed specifications for all EVY components. Use this as the reference for implementation.*

