#!/bin/bash

# EVY Local Data Setup Script
# Sets up local data collection and imports it into the RAG service

set -e  # Exit on any error

echo "🚀 EVY Local Data Setup"
echo "======================="

# Check if we're in the right directory
if [ ! -f "docker-compose.lilevy.yml" ]; then
    echo "❌ Please run this script from the EVY project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if required Python packages are installed
echo "📦 Checking Python dependencies..."
python3 -c "import requests, schedule" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip3 install requests schedule
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/collected
mkdir -p data/lilevy/knowledge
mkdir -p data/bigevy/global_knowledge

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "📝 Created .env file from template"
        echo "🔧 Please edit .env file with your actual API keys and location"
    else
        echo "❌ No env.template file found"
        exit 1
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo "✅ Loaded environment variables"
else
    echo "❌ No .env file found"
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking configuration..."

if [ -z "$LOCATION_LATITUDE" ] || [ -z "$LOCATION_LONGITUDE" ] || [ -z "$LOCATION_CITY" ]; then
    echo "⚠️  Location not configured. Please set in .env file:"
    echo "   LOCATION_LATITUDE=40.7128"
    echo "   LOCATION_LONGITUDE=-74.0060"
    echo "   LOCATION_CITY=New York"
    echo "   LOCATION_STATE=NY"
    echo "   LOCATION_ZIP_CODE=10001"
    echo ""
    echo "Continuing with default location (New York)..."
fi

# Start RAG service if not running
echo "🔧 Starting RAG service..."
if ! curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "Starting RAG service..."
    docker-compose -f docker-compose.lilevy.yml up -d local-rag
    
    # Wait for service to be ready
    echo "⏳ Waiting for RAG service to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8003/health > /dev/null 2>&1; then
            echo "✅ RAG service is ready"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
    
    if ! curl -s http://localhost:8003/health > /dev/null 2>&1; then
        echo "❌ RAG service failed to start"
        exit 1
    fi
else
    echo "✅ RAG service is already running"
fi

# Collect local data
echo "📊 Collecting local data..."
python3 scripts/collect_local_data.py

# Find the latest collected data file
LATEST_FILE=$(ls -t data/collected/local_data_*.json 2>/dev/null | head -n1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ No collected data files found"
    exit 1
fi

echo "📁 Found latest data file: $LATEST_FILE"

# Import data into RAG service
echo "📥 Importing data into RAG service..."
python3 scripts/import_to_rag.py --file "$LATEST_FILE"

# Test the import
echo "🧪 Testing RAG service..."
python3 scripts/import_to_rag.py --test

echo ""
echo "🎉 Local data setup completed!"
echo ""
echo "📋 What was set up:"
echo "  ✅ Local data collection from public APIs"
echo "  ✅ Data imported into RAG service"
echo "  ✅ RAG service tested and working"
echo ""
echo "🔍 Next steps:"
echo "  1. Test SMS functionality: docker-compose -f docker-compose.lilevy.yml up -d"
echo "  2. Send test SMS to your GSM device"
echo "  3. Check logs: docker-compose -f docker-compose.lilevy.yml logs -f"
echo ""
echo "📚 For more information, see:"
echo "  - PUBLIC_APIS_INTEGRATION.md (API integration guide)"
echo "  - RAG_LOCAL_DATA_INTEGRATION.md (RAG setup guide)"
echo "  - PRE_DEPLOYMENT_CHECKLIST.md (deployment checklist)"
