# 🆓 Free APIs Quick Start Guide

## **Immediate Setup - No API Keys Required**

### **1. National Weather Service (100% Free)**
- **No registration needed**
- **Unlimited requests**
- **Official US weather data**

```python
# Current weather alerts for your area
import requests

def get_weather_alerts(lat, lon):
    url = f"https://api.weather.gov/alerts?point={lat},{lon}"
    response = requests.get(url, headers={"User-Agent": "EVY/1.0"})
    return response.json()

# Usage
alerts = get_weather_alerts(40.7128, -74.0060)  # NYC coordinates
```

### **2. Open Data Portals (City-Specific, Free)**
Many cities provide free APIs without registration:

**Examples:**
- **NYC**: `https://data.cityofnewyork.us/` - Services, events, alerts
- **Chicago**: `https://data.cityofchicago.org/` - City services, transportation
- **Seattle**: `https://data.seattle.gov/` - Municipal data
- **Boston**: `https://data.boston.gov/` - City information

```python
# Generic city data (adjust URL for your city)
def get_city_services(city_portal_url):
    # Example: NYC 311 service requests
    url = f"{city_portal_url}/api/views/erm2-nwe9/rows.json?$limit=10"
    response = requests.get(url)
    return response.json()
```

### **3. Government Services (USA.gov - Free Tier)**
- **1000 requests/hour free**
- **Government agency information**

```python
def get_government_contacts(zip_code):
    url = f"https://api.usa.gov/contacts?zipcode={zip_code}"
    # Note: Requires API key after free tier
    response = requests.get(url)
    return response.json()
```

## **Quick Setup with Minimal Configuration**

### **Step 1: Create Basic Data Collection**
```bash
# Create a simple data collector
cat > simple_data_collector.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def collect_basic_local_data(lat, lon, city, state):
    """Collect basic local data using free APIs"""
    
    data = []
    
    # Weather alerts (free, no API key needed)
    try:
        alerts_url = f"https://api.weather.gov/alerts?point={lat},{lon}"
        response = requests.get(alerts_url, headers={"User-Agent": "EVY/1.0"})
        alerts = response.json()
        
        for alert in alerts.get('features', []):
            alert_data = alert['properties']
            data.append({
                "title": f"Weather Alert: {alert_data.get('event', 'Weather Warning')}",
                "text": f"Weather Alert: {alert_data.get('headline', 'Active weather alert')}. {alert_data.get('description', '')[:200]}",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "national_weather_service",
                    "location": f"{city}, {state}",
                    "last_updated": datetime.now().isoformat()
                }
            })
    except Exception as e:
        print(f"Weather alerts failed: {e}")
    
    # Basic emergency contacts (generic)
    data.append({
        "title": "Emergency Contacts",
        "text": f"For {city}, {state}: Emergency services: 911. For non-emergency police, contact your local police department.",
        "category": "emergency",
        "metadata": {
            "priority": "high",
            "source": "generic",
            "location": f"{city}, {state}",
            "last_updated": datetime.now().isoformat()
        }
    })
    
    # Local government info (generic)
    data.append({
        "title": "Local Government Services",
        "text": f"For {city}, {state} government services, visit your local city hall or check the official city website. Many services are available online.",
        "category": "government",
        "metadata": {
            "priority": "medium",
            "source": "generic",
            "location": f"{city}, {state}",
            "last_updated": datetime.now().isoformat()
        }
    })
    
    return data

if __name__ == "__main__":
    # Replace with your location
    YOUR_LAT = 40.7128
    YOUR_LON = -74.0060
    YOUR_CITY = "New York"
    YOUR_STATE = "NY"
    
    data = collect_basic_local_data(YOUR_LAT, YOUR_LON, YOUR_CITY, YOUR_STATE)
    
    # Save to file
    filename = f"basic_local_data_{YOUR_CITY}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Collected {len(data)} documents")
    print(f"💾 Saved to: {filename}")
EOF

python3 simple_data_collector.py
EOF
```

### **Step 2: Import into RAG Service**
```bash
# Import the collected data
python3 scripts/import_to_rag.py --file basic_local_data_*.json
```

## **Free APIs by Category**

### **🌤️ Weather (Free)**
1. **National Weather Service** - `https://api.weather.gov/`
   - No API key required
   - Official US weather data
   - Alerts, forecasts, current conditions

2. **OpenWeatherMap** - `https://openweathermap.org/api`
   - Free tier: 1000 calls/day
   - Current weather, forecasts
   - Requires free registration

### **🏛️ Government (Free)**
1. **USA.gov** - `https://api.usa.gov/`
   - Free tier: 1000 requests/hour
   - Government agency contacts
   - Requires free registration

2. **Data.gov** - `https://api.data.gov/`
   - Various government datasets
   - Free tier available
   - Requires free registration

3. **City Open Data Portals**
   - Many cities offer free APIs
   - No registration required
   - Municipal services, events, alerts

### **🏥 Health (Free)**
1. **CMS Hospital Compare** - `https://data.medicare.gov/`
   - Hospital information
   - No API key required
   - Quality ratings, locations

2. **CDC Data** - `https://data.cdc.gov/`
   - Health statistics
   - Public health data
   - No API key required

### **🚌 Transportation (Free)**
1. **City Transit APIs**
   - Many cities have free transit APIs
   - Real-time bus/train information
   - Routes and schedules

2. **Google Transit** - `https://developers.google.com/transit`
   - Free tier available
   - Transit directions
   - Requires API key

### **🎓 Education (Free)**
1. **College Scorecard** - `https://api.data.gov/ed/collegescorecard/v1/`
   - College information
   - Free tier: 1000 requests/hour
   - Programs, costs, outcomes

### **🏢 Business (Free Tiers)**
1. **Yelp** - `https://api.yelp.com/`
   - Free tier: 500 requests/day
   - Local businesses
   - Reviews and ratings

## **Quick Start Commands**

### **1. Set Your Location**
```bash
# Edit your .env file
LOCATION_LATITUDE=40.7128
LOCATION_LONGITUDE=-74.0060
LOCATION_CITY="New York"
LOCATION_STATE="NY"
LOCATION_ZIP_CODE="10001"
```

### **2. Collect Free Data**
```bash
# Run the simple collector
python3 simple_data_collector.py

# Or use the full collector (requires some API keys)
python3 scripts/collect_local_data.py
```

### **3. Import to RAG**
```bash
# Import collected data
python3 scripts/import_to_rag.py --latest

# Test the RAG service
python3 scripts/import_to_rag.py --test
```

### **4. Start EVY System**
```bash
# Start lilEVY with local data
./deploy-lilevy.sh

# Or start hybrid system
./deploy-hybrid.sh
```

## **No-Code Setup (Copy & Paste)**

### **Minimal Working Example**
```python
#!/usr/bin/env python3
import requests
import json

# Your location (replace with your coordinates)
LAT = 40.7128
LON = -74.0060
CITY = "New York"
STATE = "NY"

# Collect weather alerts (free, no API key)
alerts_url = f"https://api.weather.gov/alerts?point={LAT},{LON}"
response = requests.get(alerts_url, headers={"User-Agent": "EVY/1.0"})
alerts = response.json()

# Create basic local knowledge
local_data = [
    {
        "title": "Emergency Contacts",
        "text": f"For {CITY}, {STATE}: Emergency services: 911. Local police, fire, and medical services available 24/7.",
        "category": "emergency",
        "metadata": {"priority": "high", "source": "local"}
    },
    {
        "title": "Weather Information",
        "text": f"Current weather for {CITY}, {STATE}: Check weather.gov for official forecasts and alerts.",
        "category": "weather", 
        "metadata": {"priority": "medium", "source": "local"}
    }
]

# Add weather alerts if any
for alert in alerts.get('features', []):
    alert_data = alert['properties']
    local_data.append({
        "title": f"Weather Alert: {alert_data.get('event', 'Warning')}",
        "text": f"Weather Alert: {alert_data.get('headline', 'Active alert')}",
        "category": "emergency",
        "metadata": {"priority": "high", "source": "national_weather_service"}
    })

# Save data
with open('local_data.json', 'w') as f:
    json.dump(local_data, f, indent=2)

print(f"✅ Created {len(local_data)} local knowledge entries")
print("💾 Saved to: local_data.json")
```

### **Import to RAG Service**
```bash
# Start RAG service
docker-compose -f docker-compose.lilevy.yml up -d local-rag

# Import data
python3 scripts/import_to_rag.py --file local_data.json

# Test
python3 scripts/import_to_rag.py --test
```

## **🎯 Recommended Free APIs to Start With**

1. **National Weather Service** (100% free, no registration)
2. **Your City's Open Data Portal** (usually free, no registration)
3. **CMS Hospital Compare** (free, no registration)
4. **College Scorecard** (free tier, registration required)
5. **USA.gov** (free tier, registration required)

## **💡 Pro Tips**

1. **Start Simple**: Begin with weather alerts and basic emergency contacts
2. **Use City Data**: Most cities have free open data APIs
3. **Cache Results**: Don't hit APIs too frequently
4. **Fallback Data**: Always have generic local information as backup
5. **Test Regularly**: APIs change, so test your data collection regularly

This setup gives you a working local knowledge base with zero cost and minimal configuration!
