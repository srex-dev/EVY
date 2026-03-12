# EVY Architecture Guide
## lilEVY vs bigEVY - Clear Separation of Concerns

This document explains the clear architectural separation between lilEVY (edge nodes) and bigEVY (central processing nodes) in the EVY system.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               EVY System Architecture                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   lilEVY Node   │    │   lilEVY Node   │    │   lilEVY Node   │              │
│  │   (Edge SMS)    │    │   (Edge SMS)    │    │   (Edge SMS)    │              │
│  │                 │    │                 │    │                 │              │
│  │ • Raspberry Pi  │    │ • Raspberry Pi  │    │ • Raspberry Pi  │              │
│  │ • GSM HAT       │    │ • GSM HAT       │    │ • GSM HAT       │              │
│  │ • Solar Power   │    │ • Solar Power   │    │ • Solar Power   │              │
│  │ • Tiny LLM      │    │ • Tiny LLM      │    │ • Tiny LLM      │              │
│  │ • Local RAG     │    │ • Local RAG     │    │ • Local RAG     │              │
│  │ • Offline Cap   │    │ • Offline Cap   │    │ • Offline Cap   │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│           │                       │                       │                      │
│           └───────────────────────┼───────────────────────┘                      │
│                                   │                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        bigEVY Node                                       │ │
│  │                    (Central Processing)                                    │ │
│  │                                                                           │ │
│  │ • High-performance Server                                                  │ │
│  │ • GPU Acceleration                                                        │ │
│  │ • Large LLM Models                                                        │ │
│  │ • Global Knowledge Base                                                   │ │
│  │ • Analytics & Monitoring                                                  │ │
│  │ • Model Management                                                        │ │
│  │ • Sync & Updates                                                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Cloud Services                                      │ │
│  │                    (Optional Updates/Sync)                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📱 lilEVY (Edge SMS Node)

### **Purpose**
lilEVY nodes are distributed edge devices designed to provide SMS-based AI assistance in areas with limited or no internet connectivity.

### **Hardware Requirements**
- **CPU**: Raspberry Pi 4 (4 cores, 8GB RAM)
- **Storage**: 128GB microSD + optional 120GB SSD
- **Power**: 50-100W solar panel + 12V 30Ah Li-ion battery
- **Connectivity**: GSM HAT (SIM800C/SIM7000)
- **Consumption**: 10-15W typical

### **Software Architecture**
```
lilEVY Services:
├── SMS Gateway Service
│   ├── GSM HAT Driver
│   ├── Message Queue
│   └── Message Parser
├── Message Router Service
│   ├── Intent Classification
│   ├── Context Management
│   └── Service Selection
├── Tiny LLM Service
│   ├── 125M-350M parameter models
│   ├── 4-bit quantization
│   └── SMS-optimized responses
├── Local RAG Service
│   ├── Simple embeddings
│   ├── Local knowledge base
│   └── Hybrid search
├── Privacy Filter Service
│   ├── Data sanitization
│   ├── Consent management
│   └── Rate limiting
└── Node Communication Service
    ├── Peer discovery
    ├── Mesh networking
    └── Sync coordination
```

### **Key Features**
- ✅ **Offline Operation**: Works without internet connectivity
- ✅ **SMS Interface**: Direct GSM communication
- ✅ **Solar Powered**: Self-sustaining energy system
- ✅ **Local Processing**: Tiny LLM inference on-device
- ✅ **Local Knowledge**: Community-specific information
- ✅ **Privacy First**: All processing happens locally
- ✅ **Emergency Ready**: Critical during disasters

### **Performance Characteristics**
- **Response Time**: 6-15 seconds per SMS
- **Model Size**: 125M-350M parameters
- **Knowledge Base**: 10,000 documents max
- **Concurrent Users**: 10-50 simultaneous
- **Uptime**: 24/7 with solar backup

## 🖥️ bigEVY (Central Processing Node)

### **Purpose**
bigEVY nodes are high-performance central processing units designed to handle complex AI tasks and manage global knowledge systems.

### **Hardware Requirements**
- **CPU**: 8+ cores (Intel Xeon/AMD EPYC)
- **RAM**: 32-64GB
- **Storage**: 2-4TB NVMe SSD
- **GPU**: RTX 3060-4070 or equivalent
- **Power**: 500-700W (grid-connected)
- **Network**: High-speed internet connection

### **Software Architecture**
```
bigEVY Services:
├── Model Manager Service
│   ├── Large model loading
│   ├── GPU optimization
│   └── Model updates
├── Large LLM Service
│   ├── 7B-13B parameter models
│   ├── Batch processing
│   └── Complex reasoning
├── Global RAG Service
│   ├── Advanced embeddings
│   ├── Global knowledge base
│   └── Vector search
├── Analytics Service
│   ├── Usage analytics
│   ├── Performance metrics
│   └── Insights generation
├── Sync Service
│   ├── lilEVY coordination
│   ├── Knowledge distribution
│   └── Update management
├── Load Balancer Service
│   ├── Request routing
│   ├── Health monitoring
│   └── Failover management
└── Monitoring Service
    ├── System health
    ├── Alerting
    └── Logging
```

### **Key Features**
- ✅ **Heavy Processing**: Complex AI tasks and reasoning
- ✅ **Global Knowledge**: Comprehensive knowledge base
- ✅ **Model Management**: Large model hosting and updates
- ✅ **Analytics**: System-wide insights and monitoring
- ✅ **Scalability**: Handle multiple lilEVY nodes
- ✅ **Online Operation**: Internet-dependent for full functionality
- ✅ **GPU Acceleration**: High-performance inference

### **Performance Characteristics**
- **Response Time**: 30+ seconds for complex queries
- **Model Size**: 7B-13B parameters
- **Knowledge Base**: 1,000,000+ documents
- **Concurrent Users**: 100-1000 simultaneous
- **Throughput**: High-volume batch processing

## 🔄 Inter-Node Communication

### **Communication Patterns**
1. **lilEVY → bigEVY**: Complex query offloading
2. **bigEVY → lilEVY**: Knowledge updates and model sync
3. **lilEVY ↔ lilEVY**: Peer-to-peer mesh networking
4. **bigEVY ↔ Cloud**: Model updates and analytics

### **Hybrid Orchestration**
```
SMS Request Flow:
1. SMS → lilEVY SMS Gateway
2. Message Router analyzes complexity
3. Simple queries → Local Tiny LLM
4. Complex queries → Forward to bigEVY
5. Response → SMS back to user
```

### **Fallback Mechanisms**
- **lilEVY Offline**: Continue with local processing only
- **bigEVY Unavailable**: lilEVY falls back to local models
- **Network Issues**: Graceful degradation to offline mode
- **Service Failures**: Automatic failover and recovery

## 🚀 Deployment Options

### **1. lilEVY Only (Edge-Only)**
```bash
./deploy-lilevy.sh
```
- **Use Case**: Remote areas, disaster zones, offline communities
- **Capabilities**: Basic SMS AI assistance, local knowledge
- **Limitations**: No complex reasoning, limited knowledge base

### **2. bigEVY Only (Central-Only)**
```bash
./deploy-bigevy.sh
```
- **Use Case**: Centralized processing, no SMS interface
- **Capabilities**: Complex AI processing, global knowledge
- **Limitations**: No direct SMS access, requires internet

### **3. Hybrid (Recommended)**
```bash
./deploy-hybrid.sh
```
- **Use Case**: Complete EVY system with both edge and central processing
- **Capabilities**: Full SMS AI assistance with complex reasoning
- **Benefits**: Best of both worlds, automatic fallback

## 📊 Performance Comparison

| Feature | lilEVY | bigEVY | Hybrid |
|---------|--------|--------|--------|
| **Response Time** | 6-15s | 30+s | 6-30s |
| **Model Size** | 125M-350M | 7B-13B | Both |
| **Knowledge Base** | 10K docs | 1M+ docs | Combined |
| **Offline Capable** | ✅ | ❌ | ✅ |
| **SMS Interface** | ✅ | ❌ | ✅ |
| **Complex Reasoning** | ❌ | ✅ | ✅ |
| **Power Consumption** | 10-15W | 500-700W | Combined |
| **Internet Required** | ❌ | ✅ | Optional |
| **Cost per Node** | $390-420 | $4,000-5,000 | Combined |

## 🔧 Development and Testing

### **Service Development**
- **lilEVY Services**: `backend/lilevy/services/`
- **bigEVY Services**: `backend/bigevy/services/`
- **Shared Components**: `backend/shared/`

### **Configuration Management**
- **lilEVY Config**: `docker-compose.lilevy.yml`
- **bigEVY Config**: `docker-compose.bigevy.yml`
- **Hybrid Config**: `docker-compose.hybrid.yml`

### **Testing**
```bash
# Test lilEVY services
docker-compose -f docker-compose.lilevy.yml up -d
pytest backend/tests/test_lilevy/

# Test bigEVY services
docker-compose -f docker-compose.bigevy.yml up -d
pytest backend/tests/test_bigevy/

# Test hybrid system
docker-compose -f docker-compose.hybrid.yml up -d
pytest backend/tests/test_hybrid/
```

## 📈 Scaling Considerations

### **Horizontal Scaling (lilEVY)**
- Deploy multiple lilEVY nodes in different locations
- Each node handles local SMS traffic
- Mesh networking for peer coordination
- Independent operation with optional bigEVY sync

### **Vertical Scaling (bigEVY)**
- Increase CPU cores and RAM
- Add more GPUs for parallel processing
- Expand storage for larger knowledge bases
- Improve network connectivity

### **Hybrid Scaling**
- Scale lilEVY nodes based on geographic coverage
- Scale bigEVY nodes based on processing demand
- Implement load balancing across multiple bigEVY nodes
- Use cloud services for additional bigEVY capacity

## 🛡️ Security and Privacy

### **lilEVY Security**
- All processing happens locally
- No data leaves the device
- GSM encryption for SMS
- Local consent management

### **bigEVY Security**
- Encrypted inter-node communication
- Secure model storage
- Access control and authentication
- Audit logging and monitoring

### **Hybrid Security**
- End-to-end encryption
- Privacy-preserving sync protocols
- Secure fallback mechanisms
- Comprehensive audit trails

## 📚 Additional Resources

- **Specification**: `EVY_Specification_Script.md`
- **Technical Architecture**: `EVY_Technical_Architecture.md`
- **Cost Analysis**: `EVY_Cost_Analysis.md`
- **Roadmap**: `EVY_Roadmap.md`
- **Todo List**: `EVY_Todo_List.md`

## 🤝 Contributing

When contributing to the EVY system:

1. **Identify the target node type** (lilEVY or bigEVY)
2. **Follow the appropriate service patterns**
3. **Consider inter-node communication needs**
4. **Test both individual and hybrid deployments**
5. **Update relevant documentation**

---

**Remember**: The clear separation between lilEVY and bigEVY is fundamental to the EVY architecture. Each serves a specific purpose and together they create a robust, scalable, and resilient AI assistance system accessible via SMS.
