# EVY Quick Start Guide
## Get Started with EVY in 30 Minutes

### Prerequisites
- Raspberry Pi 4 (8GB RAM)
- GSM HAT + LoRa HAT
- 128GB microSD card
- Basic Linux knowledge

---

## 🚀 **Quick Start (30 Minutes)**

### **1. Flash OS (5 min)**
```bash
# Download Raspberry Pi OS 64-bit Lite
# Flash to microSD using Raspberry Pi Imager
# Enable SSH, configure WiFi
```

### **2. Install Software (10 min)**
```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install dependencies
sudo apt install python3.11 python3-pip git -y
```

### **3. Clone & Deploy (10 min)**
```bash
# Clone repository
git clone https://github.com/srex-dev/EVY.git
cd EVY

# Configure environment
cp env.template .env
nano .env  # Edit configuration

# Deploy
./deploy-enhanced-lilevy.sh
```

### **4. Test (5 min)**
```bash
# Check health
curl http://localhost:8000/health

# Send test SMS (via GSM HAT)
# Receive response
```

---

## ✅ **Verification Checklist**

- [ ] Hardware assembled
- [ ] OS installed
- [ ] Docker running
- [ ] Services deployed
- [ ] Health check passing
- [ ] SMS working
- [ ] Power consumption OK

---

**END OF QUICK START GUIDE**

---

*Use this guide for rapid deployment. See DEPLOYMENT_RUNBOOK.md for detailed instructions.*

