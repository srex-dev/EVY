#!/bin/bash

# EVY Hybrid Deployment Script
# Deploys both lilEVY and bigEVY nodes with inter-node communication

set -e

echo "🚀 Deploying EVY Hybrid System (lilEVY + bigEVY)..."

# Check system requirements
echo "🔍 Checking system requirements..."

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)"
    GPU_AVAILABLE=true
else
    echo "⚠️  Warning: No GPU detected. bigEVY will run in CPU mode"
    GPU_AVAILABLE=false
fi

# Check for GSM device (for lilEVY)
if [ -e /dev/ttyUSB0 ]; then
    echo "📱 GSM device detected: /dev/ttyUSB0"
    GSM_AVAILABLE=true
else
    echo "⚠️  Warning: No GSM device detected. lilEVY SMS functionality will be limited"
    GSM_AVAILABLE=false
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/{lilevy/{knowledge,chroma,privacy,metrics},bigevy/{global_knowledge,chroma,analytics,sync,updates,metrics,alerts},hybrid/metrics}
mkdir -p models/{tiny,large}
mkdir -p logs

# Set permissions for GSM device access
if [ "$GSM_AVAILABLE" = true ]; then
    echo "📱 Configuring GSM device permissions..."
    sudo chmod 666 /dev/ttyUSB0
    sudo usermod -a -G dialout $USER
fi

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env.hybrid << EOF
# Hybrid EVY Configuration
HYBRID_MODE=true
LOG_LEVEL=INFO

# lilEVY Configuration
LILEVY_NODE_ID=lilevy-001
LILEVY_GSM_DEVICE=/dev/ttyUSB0
LILEVY_GSM_BAUD_RATE=115200
LILEVY_DEFAULT_MODEL=bitnet-b1.58-2B-4T
LLM_PROVIDER=bitnet
BITNET_MODEL=bitnet-b1.58-2B-4T
BITNET_CPP_DIR=/opt/bitnet.cpp
BITNET_MODEL_PATH=/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf
LILEVY_MAX_TOKENS=512
LILEVY_EMBEDDING_MODEL=all-MiniLM-L6-v2
LILEVY_MAX_DOCUMENTS=10000

# bigEVY Configuration
BIGEVY_NODE_ID=bigevy-001
BIGEVY_GPU_ENABLED=$GPU_AVAILABLE
BIGEVY_DEFAULT_MODEL=llama-2-7b
BIGEVY_MAX_TOKENS=2048
BIGEVY_BATCH_PROCESSING=true
BIGEVY_EMBEDDING_MODEL=all-mpnet-base-v2
BIGEVY_MAX_DOCUMENTS=1000000

# Hybrid Communication
COMPLEXITY_THRESHOLD=0.7
FALLBACK_ENABLED=true
SYNC_INTERVAL_HOURS=1
DISCOVERY_ENABLED=true
MESH_NETWORK=true

# Privacy Configuration
MAX_SMS_PER_MINUTE=10
MAX_SMS_PER_HOUR=100

# Analytics and Monitoring
ANALYTICS_ENABLED=true
METRICS_ENABLED=true
ALERTING_ENABLED=true
EOF

# Pull or build images
echo "🐳 Building hybrid Docker images..."
docker-compose -f docker-compose.hybrid.yml -f docker-compose.override.yml build

# Start services in order
echo "🔄 Starting hybrid services..."

# Start bigEVY services first (they take longer to initialize)
echo "📊 Starting bigEVY services..."
docker-compose -f docker-compose.hybrid.yml up -d bigevy-large-llm bigevy-global-rag bigevy-load-balancer

# Wait for bigEVY to be ready
echo "⏳ Waiting for bigEVY services to initialize..."
sleep 90

# Start lilEVY services
echo "📱 Starting lilEVY services..."
docker-compose -f docker-compose.hybrid.yml up -d lilevy-sms-gateway lilevy-tiny-llm lilevy-local-rag

# Start communication and orchestration services
echo "🔗 Starting hybrid communication services..."
docker-compose -f docker-compose.hybrid.yml up -d lilevy-hybrid-orchestrator bigevy-sync-service hybrid-communication

# Start monitoring and web interface
echo "📊 Starting monitoring and web interface..."
docker-compose -f docker-compose.hybrid.yml up -d hybrid-monitoring hybrid-web-interface

# Wait for all services to be ready
echo "⏳ Waiting for all services to start..."
sleep 60

# Health check
echo "🏥 Performing comprehensive health checks..."

# Check lilEVY services
echo "📱 Checking lilEVY services..."
lilevy_services=("lilevy-sms-gateway:8000" "lilevy-tiny-llm:8002" "lilevy-local-rag:8003" "lilevy-hybrid-orchestrator:8005")

for service_port in "${lilevy_services[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
    fi
done

# Check bigEVY services
echo "📊 Checking bigEVY services..."
bigevy_services=("bigevy-large-llm:9001" "bigevy-global-rag:9002" "bigevy-load-balancer:9006" "bigevy-sync-service:9004")

for service_port in "${bigevy_services[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
    fi
done

# Check hybrid services
echo "🔗 Checking hybrid services..."
hybrid_services=("hybrid-communication:8500" "hybrid-monitoring:9092" "hybrid-web-interface:3002")

for service_port in "${hybrid_services[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
    fi
done

# Display status
echo "📊 EVY Hybrid Deployment Status:"
docker-compose -f docker-compose.hybrid.yml ps

echo ""
echo "🎉 EVY Hybrid deployment completed!"
echo ""
echo "📋 Service URLs:"
echo ""
echo "📱 lilEVY Services:"
echo "  SMS Gateway:         http://localhost:8000"
echo "  Tiny LLM:            http://localhost:8002"
echo "  Local RAG:           http://localhost:8003"
echo "  Hybrid Orchestrator: http://localhost:8005"
echo ""
echo "📊 bigEVY Services:"
echo "  Large LLM:           http://localhost:9001"
echo "  Global RAG:          http://localhost:9002"
echo "  Sync Service:        http://localhost:9004"
echo "  Load Balancer:       http://localhost:9006"
echo ""
echo "🔗 Hybrid Services:"
echo "  Communication:       http://localhost:8500"
echo "  Monitoring:          http://localhost:9092"
echo "  Web Interface:       http://localhost:3002"
echo ""
echo "🚀 System Capabilities:"
echo "  ✅ SMS Interface (lilEVY)"
echo "  ✅ Local AI Processing (lilEVY)"
echo "  ✅ Complex AI Processing (bigEVY)"
echo "  ✅ Global Knowledge Base (bigEVY)"
echo "  ✅ Inter-node Communication"
echo "  ✅ Automatic Fallback"
echo "  ✅ Knowledge Synchronization"
echo ""
echo "🔧 Management Commands:"
echo "  View all logs:       docker-compose -f docker-compose.hybrid.yml logs -f"
echo "  Stop all services:   docker-compose -f docker-compose.hybrid.yml down"
echo "  Restart services:    docker-compose -f docker-compose.hybrid.yml restart"
echo "  Scale services:      docker-compose -f docker-compose.hybrid.yml up -d --scale lilevy-sms-gateway=3"
echo ""
echo "📖 For more information, see README.md"
