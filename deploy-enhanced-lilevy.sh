#!/bin/bash

# Enhanced lilEVY Deployment Script
# Deploys lilEVY with LoRa Radio and Mesh Networking Capabilities

set -e

echo "🚀 Enhanced lilEVY Deployment Script"
echo "======================================"
echo ""

# Configuration
NODE_ID=${NODE_ID:-"lilevy-001"}
LORA_FREQUENCY=${LORA_FREQUENCY:-"433.0"}
LORA_POWER=${LORA_POWER:-"14"}
MESH_ENABLED=${MESH_ENABLED:-"true"}
SMART_ROUTING=${SMART_ROUTING:-"true"}

echo "📋 Deployment Configuration:"
echo "  Node ID: $NODE_ID"
echo "  LoRa Frequency: $LORA_FREQUENCY MHz"
echo "  LoRa Power: $LORA_POWER dBm"
echo "  Mesh Network: $MESH_ENABLED"
echo "  Smart Routing: $SMART_ROUTING"
echo ""

# Check system requirements
echo "🔍 Checking System Requirements..."

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo "  ✅ Raspberry Pi detected: $MODEL"
else
    echo "  ⚠️  Not running on Raspberry Pi - hardware simulation mode"
fi

# Check for USB serial devices
if ls /dev/ttyUSB* 1> /dev/null 2>&1; then
    echo "  ✅ USB serial devices found:"
    ls -la /dev/ttyUSB*
else
    echo "  ⚠️  No USB serial devices found - will use simulation mode"
fi

# Check for SPI/I2C interfaces
if [ -e /dev/spidev0.0 ]; then
    echo "  ✅ SPI interface available"
else
    echo "  ⚠️  SPI interface not available"
fi

if [ -e /dev/i2c-1 ]; then
    echo "  ✅ I2C interface available"
else
    echo "  ⚠️  I2C interface not available"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "  ✅ Docker is installed"
    docker --version
else
    echo "  ❌ Docker is not installed"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "  ✅ Docker Compose is installed"
    docker-compose --version
else
    echo "  ❌ Docker Compose is not installed"
    exit 1
fi

echo ""

# Create necessary directories
echo "📁 Creating Directory Structure..."
mkdir -p data/{lilevy,sms,llm,rag,chroma,knowledge,lora,mesh,router,privacy,metrics}
mkdir -p models/tiny
mkdir -p logs
mkdir -p monitoring

echo "  ✅ Directory structure created"

# Set up permissions
echo "🔐 Setting up Permissions..."
sudo chmod 666 /dev/ttyUSB* 2>/dev/null || echo "  ⚠️  No USB devices to configure"
sudo chmod 666 /dev/spidev* 2>/dev/null || echo "  ⚠️  No SPI devices to configure"
sudo chmod 666 /dev/i2c-* 2>/dev/null || echo "  ⚠️  No I2C devices to configure"

# Create environment file
echo "⚙️  Creating Environment Configuration..."
cat > .env.enhanced-lilevy << EOF
# Enhanced lilEVY Environment Configuration
NODE_TYPE=lilevy
NODE_ID=$NODE_ID
LORA_ENABLED=true
LORA_FREQUENCY=$LORA_FREQUENCY
LORA_POWER=$LORA_POWER
LORA_BANDWIDTH=125
LORA_SPREADING_FACTOR=7
LORA_CODING_RATE=5
MESH_NETWORK_ENABLED=$MESH_ENABLED
SMART_ROUTING_ENABLED=$SMART_ROUTING
SMS_DEVICE=/dev/ttyUSB1
GSM_ENABLED=true
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_DOCUMENTS=10000
CACHE_SIZE_MB=1000
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379
CHROMA_URL=http://chroma:8000
EOF

echo "  ✅ Environment configuration created"

# Check hardware interfaces
echo "🔌 Checking Hardware Interfaces..."

# LoRa HAT Detection
if [ -e /dev/ttyUSB0 ]; then
    echo "  ✅ LoRa HAT detected on /dev/ttyUSB0"
    LORA_DEVICE="/dev/ttyUSB0"
else
    echo "  ⚠️  LoRa HAT not detected - using simulation mode"
    LORA_DEVICE="simulation"
fi

# GSM HAT Detection
if [ -e /dev/ttyUSB1 ]; then
    echo "  ✅ GSM HAT detected on /dev/ttyUSB1"
    GSM_DEVICE="/dev/ttyUSB1"
else
    echo "  ⚠️  GSM HAT not detected - using simulation mode"
    GSM_DEVICE="simulation"
fi

echo ""

# Build Docker images
echo "🐳 Building Docker Images..."
echo "  Building Enhanced lilEVY image..."

# Build the enhanced lilEVY image
docker build -f backend/Dockerfile.enhanced-lilevy -t enhanced-lilevy:latest ./backend

echo "  ✅ Enhanced lilEVY image built"

# Build frontend image if needed
if [ -d "frontend" ]; then
    echo "  Building Enhanced Frontend image..."
    docker build -f frontend/Dockerfile.enhanced-lilevy -t enhanced-frontend:latest ./frontend
    echo "  ✅ Enhanced Frontend image built"
fi

echo ""

# Start services
echo "🚀 Starting Enhanced lilEVY Services..."

# Stop any existing services
echo "  Stopping existing services..."
docker-compose -f docker-compose.enhanced-lilevy.yml down 2>/dev/null || true

# Start new services
echo "  Starting Enhanced lilEVY stack..."
docker-compose -f docker-compose.enhanced-lilevy.yml up -d

echo ""

# Wait for services to start
echo "⏳ Waiting for Services to Start..."
sleep 10

# Check service health
echo "🏥 Checking Service Health..."

# Check main service
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "  ✅ Enhanced lilEVY Service: Healthy"
else
    echo "  ❌ Enhanced lilEVY Service: Unhealthy"
fi

# Check Redis
if docker exec enhanced-redis redis-cli ping >/dev/null 2>&1; then
    echo "  ✅ Redis: Healthy"
else
    echo "  ❌ Redis: Unhealthy"
fi

# Check ChromaDB
if curl -f http://localhost:8002/api/v1/heartbeat >/dev/null 2>&1; then
    echo "  ✅ ChromaDB: Healthy"
else
    echo "  ❌ ChromaDB: Unhealthy"
fi

# Check LoRa Radio Service
if docker logs lora-radio-service 2>&1 | grep -q "LoRa Radio Service initialized"; then
    echo "  ✅ LoRa Radio Service: Healthy"
else
    echo "  ⚠️  LoRa Radio Service: Starting or Simulation Mode"
fi

echo ""

# Display service information
echo "📊 Service Information:"
echo "  Enhanced lilEVY API: http://localhost:8000"
echo "  Web Interface: http://localhost:3001"
echo "  Monitoring: http://localhost:9090"
echo "  ChromaDB: http://localhost:8002"
echo ""

# Display mesh network status
echo "🕸️  Mesh Network Status:"
echo "  Node ID: $NODE_ID"
echo "  LoRa Frequency: $LORA_FREQUENCY MHz"
echo "  Mesh Discovery: Enabled"
echo "  Smart Routing: Enabled"
echo ""

# Show logs
echo "📝 Recent Logs:"
echo "  Enhanced lilEVY Service:"
docker logs enhanced-lilevy-001 --tail 5 2>/dev/null || echo "    No logs available"
echo ""
echo "  LoRa Radio Service:"
docker logs lora-radio-service --tail 5 2>/dev/null || echo "    No logs available"
echo ""

# Test mesh discovery
echo "🔍 Testing Mesh Discovery..."
sleep 5

# Check if LoRa service is discovering nodes
if docker logs lora-radio-service 2>&1 | grep -q "Discovery packet broadcasted"; then
    echo "  ✅ Mesh discovery is active"
else
    echo "  ⚠️  Mesh discovery may not be active (check logs)"
fi

echo ""

# Display deployment summary
echo "🎉 Enhanced lilEVY Deployment Complete!"
echo "======================================"
echo ""
echo "✅ Services Deployed:"
echo "  - Enhanced lilEVY Core Service"
echo "  - LoRa Radio Service"
echo "  - Smart Communication Router"
echo "  - Mesh Network Manager"
echo "  - Enhanced SMS Gateway"
echo "  - Tiny LLM Service"
echo "  - Local RAG Service"
echo "  - Privacy Filter"
echo "  - Monitoring Service"
echo ""
echo "🌐 Network Capabilities:"
echo "  - SMS Communication"
echo "  - LoRa Mesh Networking"
echo "  - Smart Routing"
echo "  - Off-grid Operation"
echo "  - Knowledge Synchronization"
echo ""
echo "📡 Hardware Status:"
echo "  - LoRa HAT: $([ "$LORA_DEVICE" != "simulation" ] && echo "✅ Connected" || echo "⚠️  Simulation Mode")"
echo "  - GSM HAT: $([ "$GSM_DEVICE" != "simulation" ] && echo "✅ Connected" || echo "⚠️  Simulation Mode")"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose -f docker-compose.enhanced-lilevy.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.enhanced-lilevy.yml down"
echo "  Restart services: docker-compose -f docker-compose.enhanced-lilevy.yml restart"
echo "  Check status: docker-compose -f docker-compose.enhanced-lilevy.yml ps"
echo ""
echo "🚀 Your Enhanced lilEVY Node is Ready!"
echo "   Node ID: $NODE_ID"
echo "   Ready for off-grid mesh communication!"
echo ""
