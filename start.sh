#!/bin/bash

echo "🚀 Starting EVY - Everyone's Voice, Everywhere, Everytime"
echo "=========================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env not found. Creating from example..."
    cat > backend/.env << EOF
# Environment Configuration
ENV=development

# Service Ports
SMS_GATEWAY_PORT=8001
MESSAGE_ROUTER_PORT=8002
LLM_INFERENCE_PORT=8003
RAG_SERVICE_PORT=8004
PRIVACY_FILTER_PORT=8005
API_GATEWAY_PORT=8000

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_MODEL=gpt-4
TINY_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Database Configuration
DATABASE_URL=postgresql://evy:evy_password@postgres:5432/evy_db

# Vector Database
CHROMA_PERSIST_DIR=/data/chroma

# Rate Limiting
MAX_SMS_PER_MINUTE=10
MAX_SMS_PER_HOUR=100
EOF
    echo "✅ Created backend/.env - Please set your OPENAI_API_KEY!"
fi

# Build and start services
echo ""
echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🚢 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ EVY is starting up!"
echo ""
echo "📍 Service Endpoints:"
echo "   - Frontend Dashboard: http://localhost:3000"
echo "   - API Gateway:        http://localhost:8000"
echo "   - API Docs:           http://localhost:8000/docs"
echo "   - Prometheus:         http://localhost:9090"
echo "   - Grafana:            http://localhost:3001"
echo ""
echo "📊 View logs:    docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
echo "🎉 Happy coding!"


