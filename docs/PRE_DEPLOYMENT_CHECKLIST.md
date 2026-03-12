# EVY Pre-Deployment Checklist

## 🔍 **Critical Items Before Deployment**

### **1. Hardware Requirements Validation**

#### **lilEVY (Edge SMS Node) Requirements:**
- [ ] **Raspberry Pi 4** (4GB+ RAM recommended)
- [ ] **GSM HAT** (SIM800C/SIM7000) with active SIM card
- [ ] **MicroSD Card** (64GB+ Class 10)
- [ ] **Solar Panel** (50-100W) + **Battery** (12V 30Ah)
- [ ] **MPPT Charge Controller**
- [ ] **DC-DC Step-down Converter**
- [ ] **Proper cooling** (heat sinks/fan)

#### **bigEVY (Central Processing) Requirements:**
- [ ] **CPU**: 8+ cores (Intel Xeon/AMD EPYC)
- [ ] **RAM**: 32GB+ (64GB recommended)
- [ ] **Storage**: 2TB+ NVMe SSD
- [ ] **GPU**: RTX 3060+ (for optimal performance)
- [ ] **Network**: High-speed internet connection
- [ ] **Power**: 500-700W PSU
- [ ] **Cooling**: Adequate case cooling

### **2. Software Dependencies**

#### **System Requirements:**
- [ ] **Docker** (20.10+) and **Docker Compose** (2.0+)
- [ ] **NVIDIA Container Toolkit** (for GPU support on bigEVY)
- [ ] **Python 3.9+** (for local development)
- [ ] **Git** (for version control)

#### **Platform-Specific:**
- [ ] **Linux**: Ubuntu 20.04+ or Raspberry Pi OS 64-bit
- [ ] **Windows**: WSL2 with Docker Desktop
- [ ] **macOS**: Docker Desktop for Mac

### **3. Network and Connectivity**

#### **lilEVY Network Setup:**
- [ ] **SIM Card**: Active data plan with sufficient bandwidth
- [ ] **GSM Signal**: Test signal strength at deployment location
- [ ] **Port Access**: Ensure GSM device appears as `/dev/ttyUSB0`
- [ ] **Firewall**: Configure if needed for mesh networking

#### **bigEVY Network Setup:**
- [ ] **Internet Connection**: Stable, high-bandwidth connection
- [ ] **Port Forwarding**: Configure for external access if needed
- [ ] **DNS**: Set up domain names if using custom domains
- [ ] **SSL/TLS**: Configure certificates for HTTPS

### **4. Environment Configuration**

#### **Required Environment Variables:**
```bash
# Core Configuration
NODE_TYPE=lilevy|bigevy|hybrid
NODE_ID=unique-node-identifier
LOG_LEVEL=INFO|DEBUG|WARNING

# lilEVY Specific
LILEVY_GSM_DEVICE=/dev/ttyUSB0
LILEVY_GSM_BAUD_RATE=115200
LILEVY_DEFAULT_MODEL=tinyllama
LILEVY_MAX_TOKENS=512

# bigEVY Specific  
BIGEVY_GPU_ENABLED=true|false
BIGEVY_DEFAULT_MODEL=llama-2-7b
BIGEVY_MAX_TOKENS=2048

# Security (CRITICAL - Change these!)
SECRET_KEY=your-secure-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here  # If using OpenAI

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
CHROMA_PERSIST_DIR=/data/chroma

# Rate Limiting
MAX_SMS_PER_MINUTE=10
MAX_SMS_PER_HOUR=100
```

### **5. Data Directory Setup**

#### **Create Required Directories:**
```bash
# Create data directories
mkdir -p data/{lilevy/{knowledge,chroma,privacy,metrics},bigevy/{global_knowledge,chroma,analytics,sync,updates,metrics,alerts},hybrid/metrics}
mkdir -p models/{tiny,large}
mkdir -p logs

# Set proper permissions
chmod 755 data/
chmod 755 models/
chmod 755 logs/
```

#### **Directory Structure:**
```
data/
├── lilevy/
│   ├── knowledge/          # Local knowledge base
│   ├── chroma/            # Vector database
│   ├── privacy/           # Privacy filter data
│   └── metrics/           # Performance metrics
├── bigevy/
│   ├── global_knowledge/  # Global knowledge base
│   ├── chroma/           # Vector database
│   ├── analytics/        # Analytics data
│   ├── sync/            # Sync data
│   ├── updates/         # Model updates
│   ├── metrics/         # Performance metrics
│   └── alerts/          # Alert data
└── hybrid/
    └── metrics/         # Hybrid system metrics

models/
├── tiny/               # Tiny LLM models (125M-350M)
└── large/             # Large LLM models (7B-13B)
```

### **6. Security Configuration**

#### **Critical Security Items:**
- [ ] **Change default passwords** in all configuration files
- [ ] **Generate secure SECRET_KEY** (32+ characters)
- [ ] **Set up API keys** for external services
- [ ] **Configure firewall rules** for exposed ports
- [ ] **Enable SSL/TLS** for production deployments
- [ ] **Set up monitoring** and alerting
- [ ] **Configure backup** strategies

#### **API Keys Required:**
- [ ] **OpenAI API Key** (if using OpenAI models)
- [ ] **Hugging Face Token** (for model downloads)
- [ ] **SIM Card credentials** (for GSM connectivity)

### **7. Model Preparation**

#### **lilEVY Models (Tiny):**
- [ ] **TinyLlama** (125M parameters)
- [ ] **DistilGPT2** (82M parameters)
- [ ] **Phi-2 Mini** (350M parameters)
- [ ] **Embedding Model**: all-MiniLM-L6-v2

#### **bigEVY Models (Large):**
- [ ] **Llama-2-7B** (7B parameters)
- [ ] **Llama-2-13B** (13B parameters)
- [ ] **Mistral-7B** (7B parameters)
- [ ] **Embedding Model**: all-mpnet-base-v2

### **8. Testing and Validation**

#### **Pre-Deployment Tests:**
- [ ] **Docker build** all images successfully
- [ ] **Health checks** pass for all services
- [ ] **GSM connectivity** test (for lilEVY)
- [ ] **GPU detection** test (for bigEVY)
- [ ] **Network connectivity** between services
- [ ] **Model loading** and inference tests
- [ ] **Database connectivity** tests

#### **Integration Tests:**
- [ ] **SMS send/receive** functionality
- [ ] **LLM inference** with both tiny and large models
- [ ] **RAG search** with sample queries
- [ ] **Inter-node communication** (for hybrid)
- [ ] **Fallback mechanisms** (when services unavailable)

### **9. Monitoring and Logging**

#### **Monitoring Setup:**
- [ ] **Prometheus** configuration
- [ ] **Grafana** dashboards
- [ ] **Log aggregation** (ELK stack or similar)
- [ ] **Alert rules** for critical failures
- [ ] **Health check endpoints** configured

#### **Logging Configuration:**
- [ ] **Log levels** set appropriately
- [ ] **Log rotation** configured
- [ ] **Error tracking** enabled
- [ ] **Performance metrics** collection

### **10. Backup and Recovery**

#### **Backup Strategy:**
- [ ] **Configuration backups** (environment files, docker-compose)
- [ ] **Data backups** (knowledge bases, vector databases)
- [ ] **Model backups** (downloaded models)
- [ ] **Automated backup** scheduling
- [ ] **Recovery procedures** documented

## 🚨 **Critical Warnings**

### **⚠️ Security Warnings:**
1. **NEVER** commit API keys or secrets to version control
2. **ALWAYS** use strong, unique passwords
3. **ENSURE** proper firewall configuration
4. **REGULARLY** update dependencies and models

### **⚠️ Performance Warnings:**
1. **lilEVY** requires adequate cooling for 24/7 operation
2. **bigEVY** GPU memory requirements are significant
3. **Network latency** affects inter-node communication
4. **Storage I/O** can be a bottleneck for large models

### **⚠️ Operational Warnings:**
1. **Test thoroughly** before production deployment
2. **Monitor resources** continuously
3. **Plan for failures** with proper fallback mechanisms
4. **Document procedures** for maintenance and updates

## ✅ **Final Deployment Checklist**

Before running deployment scripts:

- [ ] All hardware requirements met
- [ ] All software dependencies installed
- [ ] Environment variables configured
- [ ] Data directories created with proper permissions
- [ ] Security measures implemented
- [ ] Models downloaded and tested
- [ ] Network connectivity verified
- [ ] Monitoring configured
- [ ] Backup procedures in place
- [ ] Documentation reviewed

## 🚀 **Ready for Deployment!**

Once all items are checked, you can proceed with deployment:

```bash
# lilEVY only
./deploy-lilevy.sh

# bigEVY only  
./deploy-bigevy.sh

# Hybrid system
./deploy-hybrid.sh
```
