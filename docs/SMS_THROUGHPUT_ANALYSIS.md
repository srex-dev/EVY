# SMS Throughput Analysis
## Message Capacity at Edge (lilEVY Node)

### Executive Summary
This document analyzes the maximum SMS message throughput capacity of a single lilEVY node at the edge, considering hardware constraints, GSM HAT limitations, and processing bottlenecks.

**Key Findings:**
- **Theoretical Maximum**: ~60-120 SMS/hour (hardware-limited)
- **Practical Capacity**: ~30-60 SMS/hour (with processing overhead)
- **Bottleneck**: GSM HAT transmission time (not CPU/memory)
- **Per-User Limits**: 10 SMS/minute, 100 SMS/hour (rate limiting)

---

## 🔧 **Hardware Constraints**

### **GSM HAT Limitations**

**SIM800C/SIM7000 Specifications:**
- **SMS Send Time**: ~2-5 seconds per message
- **SMS Receive Time**: ~1-3 seconds per message
- **Queue Capacity**: Hardware queue (limited)
- **Concurrent Operations**: Single-threaded (one SMS at a time)
- **Power Consumption**: 2-5W (transmitting)

**GSM HAT Bottleneck:**
```
SMS Transmission Process:
1. AT command sent to GSM HAT: ~100ms
2. GSM HAT processes command: ~500ms
3. Message transmission to tower: ~1-3s
4. Acknowledgment received: ~500ms
5. Total: ~2-5 seconds per SMS
```

**Maximum Throughput (GSM HAT):**
- **Sending**: 60-120 SMS/hour (2-5s per message)
- **Receiving**: 120-240 SMS/hour (1-3s per message)
- **Bidirectional**: Limited by sending (slower operation)

---

## ⚙️ **Processing Bottlenecks**

### **1. Message Routing (<50ms)**
- **Latency**: <50ms (Rust implementation)
- **Throughput**: ~20,000 messages/second (not a bottleneck)
- **Impact**: Negligible

### **2. Compression (<1-2s)**
- **Latency**: <1s (rule-based), <2s (with model)
- **Throughput**: ~30-60 messages/minute (if all need compression)
- **Impact**: Moderate (only if responses >160 chars)

### **3. LLM Inference (<10s)**
- **Latency**: <10s (TinyLlama 4-bit, 50 tokens)
- **Throughput**: ~6 messages/minute per core
- **Impact**: **Major bottleneck** (if all queries need LLM)

### **4. RAG Search (<500ms)**
- **Latency**: <500ms
- **Throughput**: ~120 messages/minute
- **Impact**: Low (faster than LLM)

---

## 📊 **Throughput Analysis**

### **Scenario 1: Simple Queries (Template Responses)**

**Processing Flow:**
```
SMS Receive → Route (<50ms) → Template Response (<10ms) → Compress (<1s) → SMS Send
Total: ~1-2 seconds per message
```

**Capacity:**
- **GSM HAT Limit**: 60-120 SMS/hour
- **Processing Limit**: ~1,800 SMS/hour (not bottleneck)
- **Actual Capacity**: **60-120 SMS/hour** (GSM HAT limited)

---

### **Scenario 2: LLM Queries (Most Common)**

**Processing Flow:**
```
SMS Receive → Route (<50ms) → LLM Generate (<10s) → Compress (<1s) → SMS Send
Total: ~11-13 seconds per message
```

**Capacity:**
- **GSM HAT Limit**: 60-120 SMS/hour
- **Processing Limit**: ~5-6 SMS/minute = **300-360 SMS/hour** (theoretical)
- **Actual Capacity**: **60-120 SMS/hour** (GSM HAT limited)

**Note**: Processing can handle more, but GSM HAT is the bottleneck.

---

### **Scenario 3: RAG Queries**

**Processing Flow:**
```
SMS Receive → Route (<50ms) → RAG Search (<500ms) → Format (<100ms) → Compress (<1s) → SMS Send
Total: ~2-3 seconds per message
```

**Capacity:**
- **GSM HAT Limit**: 60-120 SMS/hour
- **Processing Limit**: ~1,200 SMS/hour (not bottleneck)
- **Actual Capacity**: **60-120 SMS/hour** (GSM HAT limited)

---

### **Scenario 4: Mixed Workload (Realistic)**

**Assumptions:**
- 30% Simple queries (template responses)
- 50% LLM queries
- 20% RAG queries

**Average Processing Time:**
```
(0.3 × 2s) + (0.5 × 12s) + (0.2 × 3s) = 0.6s + 6s + 0.6s = 7.2s per message
```

**Capacity:**
- **GSM HAT Limit**: 60-120 SMS/hour
- **Processing Limit**: ~500 SMS/hour (theoretical)
- **Actual Capacity**: **60-120 SMS/hour** (GSM HAT limited)

---

## 🎯 **Real-World Capacity**

### **Single lilEVY Node**

**Conservative Estimate:**
- **30-60 SMS/hour** (accounting for retries, errors, overhead)
- **0.5-1 SMS/minute** average
- **12-24 SMS/hour** sustained

**Optimistic Estimate:**
- **60-120 SMS/hour** (ideal conditions)
- **1-2 SMS/minute** average
- **24-48 SMS/hour** sustained

**Peak Capacity:**
- **Up to 10 SMS/minute** (burst, rate-limited)
- **Sustained: 1-2 SMS/minute**

---

## 📈 **Scaling Considerations**

### **Concurrent Users**

**Per-User Rate Limits:**
- **10 SMS/minute** per user
- **100 SMS/hour** per user

**Concurrent Capacity:**
- **1 user**: 10 SMS/minute (rate-limited)
- **5 users**: 10 SMS/minute total (GSM HAT limited)
- **10 users**: 10 SMS/minute total (GSM HAT limited)
- **20+ users**: 10 SMS/minute total (GSM HAT limited)

**Key Insight**: GSM HAT is the bottleneck, not per-user limits.

---

### **Queue Management**

**In-Memory Queue:**
- **Max Queue Size**: 1000 messages (configurable)
- **Queue Processing**: FIFO with priority (emergency first)
- **Queue Overflow**: Messages rejected if queue full

**Queue Capacity:**
```
If processing: 1 SMS/minute
Queue size: 1000 messages
Time to drain: ~1000 minutes = ~16.7 hours
```

**Recommendation**: Queue size should match expected backlog (e.g., 100-200 messages for 2-4 hour backlog).

---

## 🔋 **Power Constraints**

### **Power Consumption**

**Idle State:**
- Raspberry Pi: 5W
- GSM HAT (idle): 2W
- Services: 2W
- **Total: ~9W**

**Active State (Sending SMS):**
- Raspberry Pi: 10W
- GSM HAT (transmitting): 5W
- Services: 4W
- **Total: ~19W**

**Power Budget:**
- **Target**: <15W average
- **Peak**: <20W acceptable
- **Battery**: 0.36kWh (30Ah × 12V)

**Runtime Impact:**
- **Idle**: ~40 hours (0.36kWh / 9W)
- **Active (1 SMS/minute)**: ~19 hours (0.36kWh / 19W)
- **Active (2 SMS/minute)**: ~19 hours (same, GSM HAT limited)

---

## 💾 **Memory Constraints**

### **Memory Usage Per Message**

**Message Processing:**
- SMS message: ~1KB
- Route decision: ~0.1KB
- LLM context: ~2-4KB (if LLM used)
- Response: ~1KB
- **Total: ~4-6KB per message**

**Concurrent Messages:**
- **In queue**: 1000 messages × 6KB = 6MB
- **Processing**: 10 messages × 6KB = 60KB
- **Total: ~6MB** (negligible)

**Memory Bottleneck**: Not a limiting factor.

---

## 🚀 **Optimization Strategies**

### **1. Batch Processing**

**Current**: Process one message at a time
**Optimized**: Batch multiple messages

**Impact:**
- **GSM HAT**: Still limited (one SMS at a time)
- **LLM**: Can batch (but responses need individual SMS)
- **Benefit**: Minimal (GSM HAT is bottleneck)

---

### **2. Response Caching**

**Cache common responses:**
- Template responses: 100% cache hit
- Common queries: 50-70% cache hit
- **Benefit**: Reduces LLM processing, but GSM HAT still bottleneck

---

### **3. Priority Queue**

**Emergency messages first:**
- **Benefit**: Ensures critical messages processed quickly
- **Impact**: Doesn't increase capacity, just prioritization

---

### **4. Multiple GSM HATs**

**Add second GSM HAT:**
- **Capacity**: 2× (120-240 SMS/hour)
- **Cost**: +$50 per node
- **Power**: +2-5W
- **Complexity**: Higher (dual HAT management)

**Recommendation**: Only if needed for high-traffic nodes.

---

## 📊 **Capacity Summary**

### **Single lilEVY Node Capacity**

| Metric | Value | Notes |
|--------|-------|-------|
| **Theoretical Max** | 60-120 SMS/hour | GSM HAT limited |
| **Practical Capacity** | 30-60 SMS/hour | With overhead |
| **Sustained Rate** | 1-2 SMS/minute | Long-term average |
| **Peak Rate** | 10 SMS/minute | Burst (rate-limited) |
| **Per-User Limit** | 10 SMS/minute | Rate limiting |
| **Concurrent Users** | Unlimited* | *GSM HAT limited |
| **Queue Capacity** | 1000 messages | In-memory |

### **Bottleneck Analysis**

| Component | Limit | Status |
|-----------|-------|--------|
| **GSM HAT** | 60-120 SMS/hour | ⚠️ **Bottleneck** |
| **LLM Processing** | 300-360 SMS/hour | ✅ Not bottleneck |
| **RAG Processing** | 1,200 SMS/hour | ✅ Not bottleneck |
| **Routing** | 20,000 SMS/hour | ✅ Not bottleneck |
| **Memory** | Unlimited* | ✅ Not bottleneck |
| **CPU** | Unlimited* | ✅ Not bottleneck |
| **Power** | 19W peak | ✅ Within budget |

*Within reasonable limits

---

## 🎯 **Recommendations**

### **For Typical Deployment**

**Single Node:**
- **Expected Load**: 20-40 SMS/hour
- **Capacity**: 30-60 SMS/hour
- **Headroom**: 50-100% (comfortable)

**Multiple Nodes:**
- **Load Distribution**: Spread across nodes
- **Mesh Routing**: Route to less-loaded nodes
- **Capacity**: Scales linearly with node count

---

### **For High-Traffic Scenarios**

**Options:**
1. **Add Second GSM HAT**: 2× capacity (+$50, +2-5W)
2. **Deploy More Nodes**: Linear scaling
3. **Use WiFi/Bluetooth**: Bypass SMS for local users
4. **Optimize Processing**: Cache, batch, prioritize

---

## 📝 **Configuration Recommendations**

### **Rate Limiting**

```yaml
Current Settings:
  MAX_SMS_PER_MINUTE: 10  # Per user
  MAX_SMS_PER_HOUR: 100   # Per user

Recommended:
  MAX_SMS_PER_MINUTE: 10  # Keep (matches GSM capacity)
  MAX_SMS_PER_HOUR: 60    # Reduce to match GSM capacity
  MAX_QUEUE_SIZE: 200     # 2-4 hour backlog
```

### **Queue Configuration**

```yaml
Queue Settings:
  max_queue_size: 200        # 2-4 hour backlog
  priority_queue: true        # Emergency first
  batch_size: 1              # One at a time (GSM HAT)
  retry_attempts: 3          # Retry failed messages
  retry_delay_ms: 5000       # 5 second delay
```

---

## ✅ **Conclusion**

**Single lilEVY Node Capacity:**
- **30-60 SMS/hour** (practical)
- **60-120 SMS/hour** (theoretical maximum)
- **Bottleneck**: GSM HAT transmission time
- **Scaling**: Add more nodes or GSM HATs

**Key Insights:**
1. GSM HAT is the primary bottleneck (not CPU/memory)
2. Processing can handle more than GSM HAT can transmit
3. Capacity scales linearly with node count
4. Power consumption acceptable (<20W peak)
5. Memory usage negligible (<10MB for queue)

**For Community Deployment:**
- **Single node**: Supports 20-40 users (1-2 SMS/hour each)
- **Multiple nodes**: Scales linearly (mesh routing)
- **High-traffic**: Add GSM HATs or more nodes

---

**END OF SMS THROUGHPUT ANALYSIS**

---

*This analysis provides realistic capacity estimates for edge deployment. Actual capacity may vary based on network conditions, message complexity, and hardware variations.*

