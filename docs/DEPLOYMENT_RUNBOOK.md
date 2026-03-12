# EVY Deployment Runbook
## Step-by-Step Deployment Guide for Edge Hardware

### Document Purpose
This runbook provides step-by-step instructions for deploying EVY on Raspberry Pi 4 hardware, including hardware setup, software installation, configuration, and validation.

**Last Updated**: [Date]
**Status**: Ready for Implementation
**Target Hardware**: Raspberry Pi 4 (8GB RAM, ARM64)

---

## 📋 **Prerequisites**

### **Hardware Required**
- Raspberry Pi 4 (8GB RAM)
- GSM HAT (SIM800C/SIM7000)
- LoRa HAT (SX1276)
- 128GB microSD card (Class 10 or better)
- Solar panel (50-100W)
- 12V 30Ah Li-ion battery
- MPPT charge controller
- DC-DC converter (12V→5V)
- Cables and mounting hardware

### **Software Required**
- Raspberry Pi OS 64-bit (Lite)
- Docker & Docker Compose
- Rust toolchain (ARM64)
- Python 3.11
- Git

---

## 🔧 **Hardware Setup**

### **Step 1: Assemble Hardware**

1. **Install GSM HAT**
   ```bash
   # Connect GSM HAT to GPIO pins
   # Ensure proper power supply (3.7V-4.2V, 2A peak)
   # Connect antenna
   ```

2. **Install LoRa HAT**
   ```bash
   # Connect LoRa HAT to GPIO pins (SPI)
   # Ensure proper power supply
   # Connect antenna
   ```

3. **Connect Solar Power System**
   ```bash
   # Connect solar panel to charge controller
   # Connect battery to charge controller
   # Connect charge controller to DC-DC converter
   # Connect DC-DC converter to Raspberry Pi
   ```

### **Step 2: Install Operating System**

1. **Flash Raspberry Pi OS**
   ```bash
   # Download Raspberry Pi OS 64-bit Lite
   # Use Raspberry Pi Imager to flash to microSD
   # Enable SSH and configure WiFi (if needed)
   ```

2. **First Boot**
   ```bash
   # Boot Raspberry Pi
   # Login via SSH
   # Update system
   sudo apt update && sudo apt upgrade -y
   ```

---

## 💻 **Software Installation**

### **Step 3: Install Base Software**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Install Rust (ARM64)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup target add aarch64-unknown-linux-gnu

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Git
sudo apt install git -y
```

### **Step 4: Clone Repository**

```bash
# Clone EVY repository
git clone https://github.com/srex-dev/EVY.git
cd EVY

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

---

## 🏗️ **Build Rust Components**

### **Step 5: Build Rust Services**

```bash
# Navigate to Rust project
cd backend-rust

# Build SMS Gateway
cd sms_gateway
cargo build --release --target aarch64-unknown-linux-gnu
cd ..

# Build Message Router
cd message_router
cargo build --release --target aarch64-unknown-linux-gnu
cd ..

# Build Compression Engine
cd compression
cargo build --release --target aarch64-unknown-linux-gnu
cd ..

# Build Mesh Network
cd mesh_network
cargo build --release --target aarch64-unknown-linux-gnu
cd ..

# Build PyO3 bindings
cd pyo3_bindings
cargo build --release --target aarch64-unknown-linux-gnu
cd ../..
```

---

## ⚙️ **Configuration**

### **Step 6: Configure Environment**

```bash
# Copy environment template
cp env.template .env

# Edit .env file
nano .env
```

**Required Configuration:**
```bash
# Node Configuration
NODE_TYPE=lilevy
NODE_ID=node-001
NODE_LOCATION=Wichita,KS

# SMS Configuration
SMS_DEVICE=/dev/ttyUSB1
GSM_ENABLED=true
GSM_BAUD_RATE=9600

# LoRa Configuration
LORA_ENABLED=true
LORA_FREQUENCY=433.0
LORA_POWER=14
MESH_NETWORK_ENABLED=true

# LLM Configuration
LLM_MODEL_PATH=/models/tinyllama-4bit.gguf
LLM_N_CTX=512
LLM_N_THREADS=2

# Resource Limits
MAX_MEMORY_MB=7000
MAX_CPU_PERCENT=80
BATTERY_THRESHOLD=0.2
MEMORY_THRESHOLD_MB=100

# Emergency Configuration
EMERGENCY_ENABLED=true
EMERGENCY_PRIORITY=true
```

### **Step 7: Download Models**

```bash
# Create models directory
mkdir -p /data/models

# Download TinyLlama (4-bit quantized)
# Place model file at /data/models/tinyllama-4bit.gguf

# Verify model file
ls -lh /data/models/tinyllama-4bit.gguf
```

---

## 🚀 **Deployment**

### **Step 8: Deploy Services**

```bash
# Use deployment script
./deploy-enhanced-lilevy.sh

# Or manually with Docker Compose
docker-compose -f docker-compose.enhanced-lilevy.yml up -d

# Check service status
docker-compose -f docker-compose.enhanced-lilevy.yml ps

# View logs
docker-compose -f docker-compose.enhanced-lilevy.yml logs -f
```

### **Step 9: Verify Deployment**

```bash
# Check SMS Gateway
curl http://localhost:8000/health/sms-gateway

# Check Message Router
curl http://localhost:8000/health/message-router

# Check LLM Service
curl http://localhost:8000/health/llm-service

# Check all services
curl http://localhost:8000/health
```

---

## ✅ **Validation**

### **Step 10: Hardware Validation**

```bash
# Test GSM HAT
python3 scripts/test_gsm.py

# Test LoRa HAT
python3 scripts/test_lora.py

# Test power system
python3 scripts/test_power.py

# Measure power consumption
python3 scripts/measure_power.py
```

### **Step 11: Functional Testing**

```bash
# Run unit tests
pytest backend/tests/ -v

# Run integration tests
pytest backend/tests/test_integration.py -v

# Run hardware tests
pytest tests/hardware/ -v

# Run full test suite
pytest backend/tests/ tests/ -v --cov=backend
```

### **Step 12: Performance Testing**

```bash
# Test SMS processing
python3 scripts/test_sms_performance.py

# Test response time
python3 scripts/test_response_time.py

# Test resource usage
python3 scripts/test_resource_usage.py
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **GSM HAT Not Detected**
```bash
# Check device
ls -l /dev/ttyUSB*

# Check permissions
sudo chmod 666 /dev/ttyUSB1

# Test connection
gammu identify
```

#### **LoRa HAT Not Working**
```bash
# Check SPI
lsmod | grep spi

# Enable SPI
sudo raspi-config
# Interface Options → SPI → Enable

# Reboot
sudo reboot
```

#### **High Memory Usage**
```bash
# Check memory
free -h

# Check processes
ps aux --sort=-%mem | head

# Restart services
docker-compose restart
```

#### **High Power Consumption**
```bash
# Check CPU frequency
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# Reduce CPU frequency
sudo cpufreq-set -g powersave

# Check power
python3 scripts/measure_power.py
```

---

## 📊 **Monitoring**

### **Step 13: Setup Monitoring**

```bash
# Start Prometheus
docker-compose -f docker-compose.enhanced-lilevy.yml up -d prometheus

# Start Grafana
docker-compose -f docker-compose.enhanced-lilevy.yml up -d grafana

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

---

## 🔄 **Maintenance**

### **Daily Tasks**
- Check service health
- Review logs for errors
- Monitor resource usage
- Check battery level

### **Weekly Tasks**
- Update knowledge base
- Review performance metrics
- Check disk space
- Backup database

### **Monthly Tasks**
- Update models (if available)
- Security updates
- Hardware inspection
- Performance optimization

---

**END OF DEPLOYMENT RUNBOOK**

---

*This runbook provides step-by-step deployment instructions. Follow in order for successful deployment.*

## Addendum: Pi Bring-up Acceptance Checks

Use these checks after each cold boot to validate hardware + offline mode:

```bash
# Service health chain
curl -f http://localhost:8000/health
curl -f http://localhost:8001/health
curl -f http://localhost:8002/health
curl -f http://localhost:8003/health

# Device presence
ls -l /dev/ttyUSB0 /dev/ttyUSB1 /dev/spidev0.0

# SPI enabled
grep -E "^dtparam=spi=on" /boot/config.txt || echo "SPI not enabled"
```

## Addendum: Operator SMS Status

The router supports a lightweight operator status command over SMS:

- Send `!status` or `/status`
- Response includes processed message count, RAG usage, and battery value (if telemetry file is present)

Power telemetry source (optional):

- `/data/telemetry/power.json`
- Example payload: `{"battery_level": 78.2}`

