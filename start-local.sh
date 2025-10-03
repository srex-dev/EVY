#!/bin/bash

echo "🚀 Starting EVY Services Locally (Development Mode)"
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js not found. Please install Node.js 20+"
    exit 1
fi

# Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Check for .env file
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env not found. Please create one!"
    exit 1
fi

# Start services in background
echo ""
echo "🚀 Starting backend services..."

python -m backend.services.sms_gateway.main &
SMS_PID=$!
echo "   ✅ SMS Gateway (PID: $SMS_PID) on port 8001"

sleep 2

python -m backend.services.message_router.main &
ROUTER_PID=$!
echo "   ✅ Message Router (PID: $ROUTER_PID) on port 8002"

sleep 2

python -m backend.services.llm_inference.main &
LLM_PID=$!
echo "   ✅ LLM Inference (PID: $LLM_PID) on port 8003"

sleep 2

python -m backend.services.rag_service.main &
RAG_PID=$!
echo "   ✅ RAG Service (PID: $RAG_PID) on port 8004"

sleep 2

python -m backend.services.privacy_filter.main &
PRIVACY_PID=$!
echo "   ✅ Privacy Filter (PID: $PRIVACY_PID) on port 8005"

sleep 2

python -m backend.api_gateway.main &
API_PID=$!
echo "   ✅ API Gateway (PID: $API_PID) on port 8000"

# Start frontend
echo ""
echo "🚀 Starting frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Service Endpoints:"
echo "   - Frontend Dashboard: http://localhost:3000"
echo "   - API Gateway:        http://localhost:8000"
echo "   - API Docs:           http://localhost:8000/docs"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo ""

# Save PIDs to file for cleanup
echo "$SMS_PID $ROUTER_PID $LLM_PID $RAG_PID $PRIVACY_PID $API_PID $FRONTEND_PID" > .pids

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $SMS_PID $ROUTER_PID $LLM_PID $RAG_PID $PRIVACY_PID $API_PID $FRONTEND_PID 2>/dev/null; rm .pids; exit" INT

wait


