#!/bin/bash

# lilEVY Deployment Script
# Deploys edge SMS node optimized for Raspberry Pi 4 + GSM HAT

set -e

echo "🚀 Deploying lilEVY Edge SMS Node..."

# Check if running on supported hardware
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo "⚠️  Warning: This script is optimized for ARM-based systems (Raspberry Pi)"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/lilevy/{knowledge,chroma,privacy,metrics}
mkdir -p models/tiny
mkdir -p logs

# Set permissions for GSM device access
if [ -e /dev/ttyUSB0 ]; then
    echo "📱 Configuring GSM device permissions..."
    sudo chmod 666 /dev/ttyUSB0
    sudo usermod -a -G dialout $USER
fi

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env.lilevy << EOF
# lilEVY Configuration
NODE_TYPE=lilevy
NODE_ID=lilevy-001
GSM_DEVICE=/dev/ttyUSB0
GSM_BAUD_RATE=115200
LOG_LEVEL=INFO

# Model Configuration
DEFAULT_MODEL=tinyllama
MAX_TOKENS=512
RESPONSE_TIME_TARGET=10

# RAG Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_DOCUMENTS=10000
CACHE_SIZE_MB=500

# Privacy Configuration
MAX_SMS_PER_MINUTE=10
MAX_SMS_PER_HOUR=100

# Network Configuration
PEER_DISCOVERY=true
MESH_NETWORK=true
SYNC_INTERVAL_HOURS=24
EOF

# Pull or build images
echo "🐳 Building lilEVY Docker images..."
docker-compose -f docker-compose.lilevy.yml -f docker-compose.override.yml build

# Start services
echo "🔄 Starting lilEVY services..."
docker-compose -f docker-compose.lilevy.yml -f docker-compose.override.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Performing health checks..."
for service in sms-gateway message-router tiny-llm local-rag privacy-filter; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
    fi
done

# Display status
echo "📊 lilEVY Deployment Status:"
docker-compose -f docker-compose.lilevy.yml ps

echo ""
echo "🎉 lilEVY deployment completed!"
echo ""
echo "📋 Service URLs:"
echo "  SMS Gateway:     http://localhost:8000"
echo "  Message Router:  http://localhost:8001"
echo "  Tiny LLM:        http://localhost:8002"
echo "  Local RAG:       http://localhost:8003"
echo "  Privacy Filter:  http://localhost:8004"
echo "  Communication:   http://localhost:8005"
echo "  Monitoring:      http://localhost:9090"
echo ""
echo "📱 SMS Configuration:"
echo "  Device:          /dev/ttyUSB0"
echo "  Baud Rate:       115200"
echo "  Power:           Solar + Battery"
echo ""
echo "🔧 Management Commands:"
echo "  View logs:       docker-compose -f docker-compose.lilevy.yml logs -f"
echo "  Stop services:   docker-compose -f docker-compose.lilevy.yml down"
echo "  Restart:         docker-compose -f docker-compose.lilevy.yml restart"
echo ""
echo "📖 For more information, see README.md"
