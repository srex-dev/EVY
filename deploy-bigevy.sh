#!/bin/bash

# bigEVY Deployment Script
# Deploys central processing node optimized for high-performance servers

set -e

echo "🚀 Deploying bigEVY Central Processing Node..."

# Check if GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)"
else
    echo "⚠️  Warning: No GPU detected. bigEVY will run in CPU mode (slower performance)"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/bigevy/{global_knowledge,chroma,analytics,sync,updates,metrics,alerts}
mkdir -p models/large
mkdir -p logs

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env.bigevy << EOF
# bigEVY Configuration
NODE_TYPE=bigevy
NODE_ID=bigevy-001
GPU_ENABLED=true
LOG_LEVEL=INFO

# Model Configuration
DEFAULT_MODEL=llama-2-7b
MAX_TOKENS=2048
BATCH_PROCESSING=true
RESPONSE_TIME_TARGET=30

# RAG Configuration
EMBEDDING_MODEL=all-mpnet-base-v2
MAX_DOCUMENTS=1000000
CACHE_SIZE_MB=10000

# Analytics Configuration
ANALYTICS_ENABLED=true
DATA_RETENTION_DAYS=365

# Sync Configuration
SYNC_INTERVAL_HOURS=1
LILEVY_NODES_DISCOVERY=true

# Update Configuration
MODEL_UPDATES_ENABLED=true
UPDATE_CHECK_INTERVAL_HOURS=24

# Load Balancing
LOAD_BALANCING_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Monitoring
METRICS_ENABLED=true
ALERTING_ENABLED=true
EOF

# Pull or build images
echo "🐳 Building bigEVY Docker images..."
docker-compose -f docker-compose.bigevy.yml -f docker-compose.override.yml build

# Start services
echo "🔄 Starting bigEVY services..."
docker-compose -f docker-compose.bigevy.yml -f docker-compose.override.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60  # Longer wait for bigEVY services

# Health check
echo "🏥 Performing health checks..."
services=("model-manager:9000" "large-llm:9001" "global-rag:9002" "analytics-service:9003" "sync-service:9004" "update-manager:9005" "load-balancer:9006")

for service_port in "${services[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
    fi
done

# Display status
echo "📊 bigEVY Deployment Status:"
docker-compose -f docker-compose.bigevy.yml ps

echo ""
echo "🎉 bigEVY deployment completed!"
echo ""
echo "📋 Service URLs:"
echo "  Model Manager:    http://localhost:9000"
echo "  Large LLM:        http://localhost:9001"
echo "  Global RAG:       http://localhost:9002"
echo "  Analytics:        http://localhost:9003"
echo "  Sync Service:     http://localhost:9004"
echo "  Update Manager:   http://localhost:9005"
echo "  Load Balancer:    http://localhost:9006"
echo "  Monitoring:       http://localhost:9091"
echo "  Web Interface:    http://localhost:3001"
echo ""
echo "💾 Resource Usage:"
echo "  CPU:              16+ cores recommended"
echo "  RAM:              64GB recommended"
echo "  Storage:          2TB+ recommended"
echo "  GPU:              RTX 3060+ recommended"
echo ""
echo "🔧 Management Commands:"
echo "  View logs:        docker-compose -f docker-compose.bigevy.yml logs -f"
echo "  Stop services:    docker-compose -f docker-compose.bigevy.yml down"
echo "  Restart:          docker-compose -f docker-compose.bigevy.yml restart"
echo "  GPU status:       nvidia-smi"
echo ""
echo "📖 For more information, see README.md"
