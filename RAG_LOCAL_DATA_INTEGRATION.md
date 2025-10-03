# RAG Local Data Integration Guide

## 📚 **Where to Locate and Integrate Local Information**

### **1. Data Directory Structure**

```
data/
├── lilevy/knowledge/          # lilEVY Local Knowledge
│   ├── emergency/            # Emergency contacts and procedures
│   ├── weather/              # Local weather information
│   ├── local_info/           # Community-specific information
│   ├── health/               # Local health services
│   ├── education/            # Educational resources
│   ├── government/           # Government services
│   ├── transportation/       # Local transport info
│   ├── utilities/            # Utility services
│   └── community/            # Community events and services
└── bigevy/global_knowledge/  # bigEVY Global Knowledge
    ├── general_knowledge/    # General information
    ├── science/              # Scientific knowledge
    ├── technology/           # Technology information
    ├── medicine/             # Medical knowledge
    ├── law/                  # Legal information
    ├── business/             # Business knowledge
    ├── education/            # Educational content
    ├── history/              # Historical information
    └── geography/            # Geographical knowledge
```

### **2. lilEVY Local Information Sources**

#### **Emergency Information** (`data/lilevy/knowledge/emergency/`)
```json
{
  "title": "Emergency Contacts",
  "text": "Emergency: 911. Local Hospital: (555) 123-4567. Police: (555) 987-6543. Fire: (555) 456-7890. Poison Control: (555) 800-222-1222.",
  "category": "emergency",
  "metadata": {
    "priority": "high",
    "source": "local",
    "last_updated": "2024-01-15",
    "location": "Springfield, IL"
  }
}
```

#### **Local Weather** (`data/lilevy/knowledge/weather/`)
```json
{
  "title": "Current Weather Conditions",
  "text": "Current temperature: 72°F, Partly cloudy. Humidity: 45%. Wind: 8 mph NW. UV Index: Moderate. Tomorrow: High 75°F, Low 55°F, 20% chance of rain.",
  "category": "weather",
  "metadata": {
    "priority": "medium",
    "source": "sensor",
    "last_updated": "2024-01-15T14:30:00Z",
    "location": "Springfield, IL"
  }
}
```

#### **Local Services** (`data/lilevy/knowledge/local_info/`)
```json
{
  "title": "City Services Directory",
  "text": "City Hall: 123 Main St, open Mon-Fri 8AM-5PM. Library: 456 Oak Ave, open daily 9AM-8PM. Post Office: 789 Pine St, open Mon-Fri 8AM-5PM.",
  "category": "local_info",
  "metadata": {
    "priority": "medium",
    "source": "local",
    "last_updated": "2024-01-15",
    "location": "Springfield, IL"
  }
}
```

#### **Health Services** (`data/lilevy/knowledge/health/`)
```json
{
  "title": "Local Health Services",
  "text": "Springfield Medical Center: 321 Health Way, appointments (555) 111-2222. Community Clinic: 654 Wellness Blvd, walk-ins welcome. Pharmacy: 987 Medicine St, 24/7 emergency line.",
  "category": "health",
  "metadata": {
    "priority": "high",
    "source": "local",
    "last_updated": "2024-01-15",
    "location": "Springfield, IL"
  }
}
```

### **3. Data Integration Methods**

#### **Method 1: Direct File Upload**
```bash
# Copy local information files to knowledge directory
cp local_emergency_contacts.json data/lilevy/knowledge/emergency/
cp weather_data.json data/lilevy/knowledge/weather/
cp city_services.json data/lilevy/knowledge/local_info/
```

#### **Method 2: API Integration**
```python
# Example: Integrating local weather data
import requests
import json
from datetime import datetime

def update_weather_data():
    # Fetch from local weather API or sensors
    weather_data = requests.get("http://localhost:8080/weather/current")
    
    document = {
        "title": "Current Weather",
        "text": f"Temperature: {weather_data['temp']}°F, {weather_data['condition']}",
        "category": "weather",
        "metadata": {
            "priority": "medium",
            "source": "api",
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Add to RAG service
    await rag_service.add_document(
        text=document["text"],
        title=document["title"],
        category=document["category"],
        metadata=document["metadata"]
    )
```

#### **Method 3: Bulk Import**
```python
# Example: Bulk import from CSV/JSON
import csv
import json

def import_local_data_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            document = {
                "title": row['title'],
                "text": row['content'],
                "category": row['category'],
                "metadata": {
                    "priority": row.get('priority', 'medium'),
                    "source": "csv_import",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            await rag_service.add_document(
                text=document["text"],
                title=document["title"],
                category=document["category"],
                metadata=document["metadata"]
            )
```

### **4. Local Data Sources Integration**

#### **A. Government and Municipal Data**
```bash
# Directory: data/lilevy/knowledge/government/
# Sources: City websites, municipal APIs, public records
```

**Example Integration:**
```python
# Fetch city council meeting schedules
async def update_government_info():
    gov_data = {
        "title": "City Council Schedule",
        "text": "City Council meets every 1st and 3rd Tuesday at 7PM in City Hall. Public comment period: 6:30PM. Next meeting: January 16, 2024.",
        "category": "government",
        "metadata": {
            "priority": "medium",
            "source": "city_website",
            "last_updated": "2024-01-15"
        }
    }
    
    await rag_service.add_document(**gov_data)
```

#### **B. Educational Resources**
```bash
# Directory: data/lilevy/knowledge/education/
# Sources: School districts, libraries, educational programs
```

**Example Integration:**
```python
# Local educational resources
education_data = {
    "title": "Adult Education Programs",
    "text": "Springfield Adult Learning Center offers GED classes Mon-Thu 6-9PM. Computer literacy classes Sat 10AM-12PM. ESL classes Tue/Thu 7-9PM.",
    "category": "education",
    "metadata": {
        "priority": "medium",
        "source": "education_dept",
        "last_updated": "2024-01-15"
    }
}
```

#### **C. Transportation Information**
```bash
# Directory: data/lilevy/knowledge/transportation/
# Sources: Transit authorities, traffic departments
```

**Example Integration:**
```python
# Local bus routes and schedules
transport_data = {
    "title": "Bus Route Information",
    "text": "Route 1 (Main St): Every 30min, 6AM-10PM. Route 2 (Oak Ave): Every 45min, 7AM-9PM. Route 3 (Pine St): Every hour, 8AM-8PM. Fares: $1.50 adult, $0.75 senior.",
    "category": "transportation",
    "metadata": {
        "priority": "medium",
        "source": "transit_auth",
        "last_updated": "2024-01-15"
    }
}
```

#### **D. Community Events**
```bash
# Directory: data/lilevy/knowledge/community/
# Sources: Community centers, event calendars, local organizations
```

**Example Integration:**
```python
# Community events calendar
community_data = {
    "title": "Weekly Community Events",
    "text": "Farmers Market: Saturdays 8AM-2PM at City Park. Library Story Time: Wednesdays 10AM for ages 3-5. Senior Center Bingo: Fridays 2PM.",
    "category": "community",
    "metadata": {
        "priority": "low",
        "source": "community_center",
        "last_updated": "2024-01-15"
    }
}
```

### **5. Automated Data Updates**

#### **Scheduled Updates Script**
```python
# scripts/update_local_data.py
import asyncio
import schedule
import time
from datetime import datetime

async def update_weather():
    """Update weather information every hour"""
    # Fetch from weather API/sensors
    pass

async def update_events():
    """Update community events daily"""
    # Fetch from event calendars
    pass

async def update_services():
    """Update service hours weekly"""
    # Fetch from service websites
    pass

# Schedule updates
schedule.every().hour.do(update_weather)
schedule.every().day.at("06:00").do(update_events)
schedule.every().sunday.at("02:00").do(update_services)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

#### **Real-time Data Integration**
```python
# Webhook integration for real-time updates
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/emergency-update")
async def emergency_update(request: Request):
    """Handle emergency updates via webhook"""
    data = await request.json()
    
    # Update emergency information
    await rag_service.add_document(
        text=data["message"],
        title="Emergency Alert",
        category="emergency",
        metadata={
            "priority": "high",
            "source": "emergency_system",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return {"status": "updated"}
```

### **6. Data Quality and Validation**

#### **Data Validation Schema**
```python
from pydantic import BaseModel, validator

class LocalDocument(BaseModel):
    title: str
    text: str
    category: str
    metadata: dict
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'emergency', 'weather', 'local_info', 'health',
            'education', 'government', 'transportation', 'utilities', 'community'
        ]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of {valid_categories}')
        return v
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v) < 10:
            raise ValueError('Text must be at least 10 characters')
        if len(v) > 1000:
            raise ValueError('Text must be less than 1000 characters')
        return v
```

#### **Data Quality Checks**
```python
async def validate_and_add_document(document_data):
    """Validate and add document with quality checks"""
    try:
        # Validate document structure
        document = LocalDocument(**document_data)
        
        # Check for duplicates
        existing = await rag_service.search(
            RAGQuery(query=document.text[:50], top_k=1)
        )
        
        if existing.documents and existing.scores[0] > 0.9:
            logger.warning(f"Potential duplicate document: {document.title}")
            return False
        
        # Add validated document
        await rag_service.add_document(
            text=document.text,
            title=document.title,
            category=document.category,
            metadata=document.metadata
        )
        
        logger.info(f"Added document: {document.title}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        return False
```

### **7. Integration with External Systems**

#### **A. Municipal APIs**
```python
# Example: Integration with city open data portal
import requests

async def sync_municipal_data():
    """Sync data from municipal open data portal"""
    api_url = "https://data.springfield.gov/api/records/1.0/search/"
    
    # Fetch city services data
    response = requests.get(f"{api_url}?dataset=city-services")
    data = response.json()
    
    for record in data['records']:
        await rag_service.add_document(
            text=record['fields']['description'],
            title=record['fields']['name'],
            category="government",
            metadata={
                "priority": "medium",
                "source": "municipal_api",
                "last_updated": datetime.now().isoformat()
            }
        )
```

#### **B. Weather APIs**
```python
# Example: Integration with weather services
async def sync_weather_data():
    """Sync weather data from multiple sources"""
    # Local weather station
    local_weather = requests.get("http://weather-station:8080/current")
    
    # National Weather Service
    nws_weather = requests.get("https://api.weather.gov/alerts")
    
    # Combine and add to knowledge base
    weather_text = f"Local: {local_weather.json()['temp']}°F. NWS Alerts: {len(nws_weather.json()['features'])} active."
    
    await rag_service.add_document(
        text=weather_text,
        title="Weather Update",
        category="weather",
        metadata={
            "priority": "medium",
            "source": "weather_apis",
            "last_updated": datetime.now().isoformat()
        }
    )
```

#### **C. Social Services**
```python
# Example: Integration with social services databases
async def sync_social_services():
    """Sync social services information"""
    services = [
        {
            "title": "Food Assistance",
            "text": "Springfield Food Bank: 123 Food St, open Mon-Fri 9AM-3PM. Emergency food boxes available. Call (555) FOOD-123.",
            "category": "utilities"
        },
        {
            "title": "Housing Assistance",
            "text": "Housing Authority: 456 Home Ave. Section 8 applications accepted 1st-15th of each month. Emergency shelter: (555) SHELTER.",
            "category": "utilities"
        }
    ]
    
    for service in services:
        await rag_service.add_document(**service)
```

### **8. Testing Local Data Integration**

#### **Test Script**
```python
# tests/test_local_data_integration.py
import pytest
from backend.lilevy.services.local_rag_service import local_rag_service

@pytest.mark.asyncio
async def test_local_data_search():
    """Test searching local data"""
    # Add test document
    await local_rag_service.add_local_document(
        text="Emergency contact: 911. Hospital: (555) 123-4567.",
        title="Emergency Contacts",
        category="emergency"
    )
    
    # Search for emergency info
    result = await local_rag_service.search(
        RAGQuery(query="emergency contact", top_k=1)
    )
    
    assert len(result.documents) > 0
    assert "911" in result.documents[0]

@pytest.mark.asyncio
async def test_category_filtering():
    """Test category-based filtering"""
    result = await local_rag_service.search(
        RAGQuery(
            query="help",
            top_k=5,
            filter_metadata={"category": "emergency"}
        )
    )
    
    # All results should be emergency category
    for metadata in result.metadata:
        assert metadata["category"] == "emergency"
```

### **9. Monitoring and Maintenance**

#### **Data Health Monitoring**
```python
# Monitor data quality and freshness
async def monitor_data_health():
    """Monitor local data health"""
    stats = await local_rag_service.get_statistics()
    
    # Check for stale data
    stale_threshold = datetime.now() - timedelta(days=30)
    
    for category in ["emergency", "health", "government"]:
        docs = await local_rag_service.get_documents_by_category(category)
        
        for doc in docs:
            last_updated = datetime.fromisoformat(doc["metadata"].get("last_updated", ""))
            if last_updated < stale_threshold:
                logger.warning(f"Stale data in {category}: {doc['title']}")
```

## 🎯 **Quick Start: Adding Your Local Data**

### **Step 1: Create Local Data Files**
```bash
# Create your local information files
mkdir -p data/lilevy/knowledge/{emergency,weather,local_info,health}

# Add your emergency contacts
cat > data/lilevy/knowledge/emergency/contacts.json << EOF
{
  "title": "Emergency Contacts",
  "text": "Emergency: 911. Local Hospital: YOUR_HOSPITAL_PHONE. Police: YOUR_POLICE_PHONE. Fire: YOUR_FIRE_PHONE.",
  "category": "emergency",
  "metadata": {
    "priority": "high",
    "source": "local",
    "location": "YOUR_LOCATION"
  }
}
EOF
```

### **Step 2: Import Data via API**
```bash
# Use the RAG service API to add documents
curl -X POST "http://localhost:8003/add" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "emergency_contacts_001",
    "text": "Emergency: 911. Local Hospital: YOUR_HOSPITAL_PHONE.",
    "metadata": {
      "category": "emergency",
      "priority": "high",
      "source": "manual"
    }
  }'
```

### **Step 3: Verify Integration**
```bash
# Search for your local data
curl -X POST "http://localhost:8003/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "emergency contact",
    "top_k": 5
  }'
```

## 📋 **Local Data Integration Checklist**

- [ ] **Identify local information sources** (government, services, events)
- [ ] **Create data directory structure** with appropriate categories
- [ ] **Prepare local data** in JSON format with proper metadata
- [ ] **Set up automated updates** for dynamic information (weather, events)
- [ ] **Configure data validation** to ensure quality
- [ ] **Test search functionality** with sample queries
- [ ] **Monitor data freshness** and update stale information
- [ ] **Document data sources** and update procedures
- [ ] **Set up backup** for local knowledge base
- [ ] **Train community members** on data contribution

---

**Your local information is now ready to power EVY's SMS-based AI assistance with relevant, up-to-date local knowledge!**
