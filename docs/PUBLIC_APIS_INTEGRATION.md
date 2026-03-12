# Public APIs for Local Information Integration

## 🌐 **Available Public APIs for Local Data**

### **1. Government & Municipal APIs**

#### **A. USA.gov APIs**
- **URL**: `https://api.usa.gov/`
- **Data**: Government services, agency information, contact details
- **Authentication**: Free, requires API key
- **Rate Limit**: 1000 requests/hour

```python
# USA.gov Government Services API
async def fetch_government_services(zip_code):
    url = f"https://api.usa.gov/contacts?zipcode={zip_code}"
    headers = {"Authorization": "Bearer YOUR_USA_GOV_API_KEY"}
    
    response = requests.get(url, headers=headers)
    services = response.json()
    
    for service in services:
        await rag_service.add_document(
            text=f"{service['name']}: {service['description']}. Contact: {service['phone']}",
            title=f"Government Service: {service['name']}",
            category="government",
            metadata={
                "priority": "medium",
                "source": "usa_gov_api",
                "location": zip_code
            }
        )
```

#### **B. Open Data Portals**
Many cities have open data portals with APIs:

**Examples:**
- **NYC Open Data**: `https://data.cityofnewyork.us/`
- **Chicago Data Portal**: `https://data.cityofchicago.org/`
- **SF Open Data**: `https://data.sfgov.org/`
- **Seattle Open Data**: `https://data.seattle.gov/`

```python
# Generic Open Data Portal Integration
async def fetch_municipal_data(portal_url, dataset_id):
    url = f"{portal_url}/api/views/{dataset_id}/rows.json"
    
    response = requests.get(url)
    data = response.json()
    
    for record in data['data']:
        await rag_service.add_document(
            text=f"{record[8]}: {record[9]}",  # Adjust indices based on dataset
            title=f"Municipal Service: {record[8]}",
            category="government",
            metadata={
                "priority": "medium",
                "source": "municipal_api",
                "dataset": dataset_id
            }
        )
```

### **2. Weather APIs**

#### **A. OpenWeatherMap (Free Tier)**
- **URL**: `https://api.openweathermap.org/data/2.5/`
- **Data**: Current weather, forecasts, alerts
- **Authentication**: Free tier available (1000 calls/day)
- **Rate Limit**: 60 calls/minute

```python
# OpenWeatherMap Integration
async def update_weather_data(lat, lon, api_key):
    # Current weather
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    current = requests.get(current_url).json()
    
    # Weather alerts
    alerts_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}"
    alerts = requests.get(alerts_url).json()
    
    # Current conditions
    weather_text = f"Current: {current['main']['temp']}°F, {current['weather'][0]['description']}. "
    weather_text += f"Humidity: {current['main']['humidity']}%. Wind: {current['wind']['speed']} mph."
    
    if 'alerts' in alerts:
        weather_text += f" Alerts: {len(alerts['alerts'])} active weather warnings."
    
    await rag_service.add_document(
        text=weather_text,
        title="Current Weather Conditions",
        category="weather",
        metadata={
            "priority": "medium",
            "source": "openweathermap",
            "last_updated": datetime.now().isoformat()
        }
    )
```

#### **B. National Weather Service (Free)**
- **URL**: `https://api.weather.gov/`
- **Data**: Official US weather data, alerts, forecasts
- **Authentication**: None required
- **Rate Limit**: 10 calls/second

```python
# National Weather Service Integration
async def fetch_nws_alerts(lat, lon):
    # Get weather alerts
    alerts_url = f"https://api.weather.gov/alerts?point={lat},{lon}"
    response = requests.get(alerts_url, headers={"User-Agent": "EVY/1.0"})
    alerts = response.json()
    
    for alert in alerts['features']:
        alert_data = alert['properties']
        await rag_service.add_document(
            text=f"Weather Alert: {alert_data['headline']}. {alert_data['description']}",
            title=f"Weather Alert: {alert_data['event']}",
            category="emergency",
            metadata={
                "priority": "high",
                "source": "national_weather_service",
                "alert_type": alert_data['event']
            }
        )
```

### **3. Transportation APIs**

#### **A. Google Maps API (Paid)**
- **URL**: `https://maps.googleapis.com/maps/api/`
- **Data**: Transit routes, schedules, traffic
- **Authentication**: API key required
- **Rate Limit**: Varies by service

```python
# Google Transit API
async def fetch_transit_routes(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=transit&key={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    for route in data['routes']:
        for leg in route['legs']:
            for step in leg['steps']:
                if step['travel_mode'] == 'TRANSIT':
                    transit = step['transit_details']
                    await rag_service.add_document(
                        text=f"Route {transit['line']['short_name']}: {transit['departure_stop']['name']} to {transit['arrival_stop']['name']}. Departure: {transit['departure_time']['text']}",
                        title=f"Transit Route: {transit['line']['short_name']}",
                        category="transportation",
                        metadata={
                            "priority": "medium",
                            "source": "google_maps_transit"
                        }
                    )
```

#### **B. Transit APIs (City-Specific)**
Many cities have their own transit APIs:

**Examples:**
- **MBTA (Boston)**: `https://api-v3.mbta.com/`
- **CTA (Chicago)**: `https://www.transitchicago.com/developers/`
- **MTA (NYC)**: `https://api.mta.info/`
- **TTC (Toronto)**: `https://ttc.ca/ttcapi/`

```python
# MBTA (Boston) Transit API Example
async def fetch_mbta_routes():
    routes_url = "https://api-v3.mbta.com/routes"
    response = requests.get(routes_url)
    routes = response.json()
    
    for route in routes['data']:
        await rag_service.add_document(
            text=f"MBTA {route['attributes']['long_name']}: {route['attributes']['description']}",
            title=f"Transit Route: {route['attributes']['long_name']}",
            category="transportation",
            metadata={
                "priority": "medium",
                "source": "mbta_api",
                "route_type": route['attributes']['type']
            }
        )
```

### **4. Health & Emergency Services**

#### **A. Hospital Compare API (CMS)**
- **URL**: `https://data.medicare.gov/api/`
- **Data**: Hospital information, quality ratings
- **Authentication**: None required
- **Rate Limit**: None specified

```python
# CMS Hospital Compare API
async def fetch_local_hospitals(zip_code):
    url = f"https://data.medicare.gov/api/views/9bhg-hcku/rows.json?$where=ZIP_CODE={zip_code}"
    
    response = requests.get(url)
    hospitals = response.json()
    
    for hospital in hospitals['data']:
        await rag_service.add_document(
            text=f"Hospital: {hospital[9]}. Address: {hospital[10]}. Phone: {hospital[11]}. Emergency Services: Available.",
            title=f"Hospital: {hospital[9]}",
            category="health",
            metadata={
                "priority": "high",
                "source": "cms_hospital_compare",
                "location": zip_code
            }
        )
```

#### **B. Emergency Services Data**
```python
# Generic emergency services lookup
async def fetch_emergency_services(zip_code):
    # This would integrate with local emergency services databases
    # Many counties have public APIs for emergency services
    
    emergency_services = [
        {
            "title": "Emergency Contacts",
            "text": f"Emergency: 911. For {zip_code} area: Local dispatch center available 24/7.",
            "category": "emergency",
            "metadata": {"priority": "high", "source": "emergency_services"}
        }
    ]
    
    for service in emergency_services:
        await rag_service.add_document(**service)
```

### **5. Education APIs**

#### **A. College Scorecard API (US Dept of Education)**
- **URL**: `https://api.data.gov/ed/collegescorecard/v1/`
- **Data**: College information, programs, costs
- **Authentication**: API key required
- **Rate Limit**: 1000 requests/hour

```python
# College Scorecard API
async def fetch_local_colleges(zip_code):
    url = f"https://api.data.gov/ed/collegescorecard/v1/schools?zip={zip_code}&api_key=YOUR_API_KEY"
    
    response = requests.get(url)
    colleges = response.json()
    
    for college in colleges['results']:
        await rag_service.add_document(
            text=f"College: {college['school.name']}. Programs: {college['programs']}. Location: {college['school.city']}, {college['school.state']}",
            title=f"College: {college['school.name']}",
            category="education",
            metadata={
                "priority": "medium",
                "source": "college_scorecard",
                "location": zip_code
            }
        )
```

### **6. Community & Events APIs**

#### **A. Eventbrite API**
- **URL**: `https://www.eventbriteapi.com/v3/`
- **Data**: Local events, community gatherings
- **Authentication**: API key required
- **Rate Limit**: 1000 requests/hour

```python
# Eventbrite Events API
async def fetch_local_events(lat, lon, radius=25):
    url = f"https://www.eventbriteapi.com/v3/events/search/?location.latitude={lat}&location.longitude={lon}&location.within={radius}mi"
    headers = {"Authorization": "Bearer YOUR_EVENTBRITE_TOKEN"}
    
    response = requests.get(url, headers=headers)
    events = response.json()
    
    for event in events['events']:
        await rag_service.add_document(
            text=f"Event: {event['name']['text']}. Date: {event['start']['local']}. Location: {event['venue']['address']['city']}",
            title=f"Community Event: {event['name']['text']}",
            category="community",
            metadata={
                "priority": "low",
                "source": "eventbrite",
                "event_date": event['start']['local']
            }
        )
```

#### **B. Meetup API**
- **URL**: `https://api.meetup.com/`
- **Data**: Local meetups, groups, events
- **Authentication**: API key required
- **Rate Limit**: 200 requests/hour

```python
# Meetup API
async def fetch_meetup_events(lat, lon):
    url = f"https://api.meetup.com/find/upcoming_events?lat={lat}&lon={lon}&radius=25"
    headers = {"Authorization": "Bearer YOUR_MEETUP_TOKEN"}
    
    response = requests.get(url, headers=headers)
    events = response.json()
    
    for event in events:
        await rag_service.add_document(
            text=f"Meetup: {event['name']}. Group: {event['group']['name']}. Date: {event['local_date']}",
            title=f"Meetup: {event['name']}",
            category="community",
            metadata={
                "priority": "low",
                "source": "meetup",
                "group_name": event['group']['name']
            }
        )
```

### **7. Business & Services APIs**

#### **A. Yelp API**
- **URL**: `https://api.yelp.com/v3/`
- **Data**: Local businesses, services, reviews
- **Authentication**: API key required
- **Rate Limit**: 5000 requests/day

```python
# Yelp Business API
async def fetch_local_businesses(location, category):
    url = f"https://api.yelp.com/v3/businesses/search?location={location}&categories={category}"
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    businesses = response.json()
    
    for business in businesses['businesses']:
        await rag_service.add_document(
            text=f"{business['name']}: {business['categories'][0]['title']}. Rating: {business['rating']}/5. Phone: {business['phone']}",
            title=f"Local Business: {business['name']}",
            category="local_info",
            metadata={
                "priority": "medium",
                "source": "yelp_api",
                "category": business['categories'][0]['title']
            }
        )
```

### **8. Automated Data Collection System**

#### **Data Collection Scheduler**
```python
import asyncio
import schedule
import time
from datetime import datetime

class LocalDataCollector:
    def __init__(self, rag_service, location_config):
        self.rag_service = rag_service
        self.location = location_config
        
    async def collect_all_data(self):
        """Collect data from all available APIs"""
        tasks = [
            self.update_weather_data(),
            self.fetch_government_services(),
            self.fetch_transit_routes(),
            self.fetch_hospitals(),
            self.fetch_emergency_services(),
            self.fetch_community_events(),
            self.fetch_local_businesses()
        ]
        
        await asyncio.gather(*tasks)
        print(f"Data collection completed at {datetime.now()}")
    
    async def update_weather_data(self):
        """Update weather information every hour"""
        await fetch_weather_data(
            self.location['lat'], 
            self.location['lon'], 
            OPENWEATHER_API_KEY
        )
    
    async def fetch_government_services(self):
        """Update government services daily"""
        await fetch_government_services(self.location['zip_code'])
    
    # ... other collection methods

# Schedule data collection
def schedule_data_collection():
    collector = LocalDataCollector(rag_service, {
        'lat': YOUR_LATITUDE,
        'lon': YOUR_LONGITUDE,
        'zip_code': YOUR_ZIP_CODE
    })
    
    # Schedule updates
    schedule.every().hour.do(lambda: asyncio.run(collector.update_weather_data()))
    schedule.every().day.at("06:00").do(lambda: asyncio.run(collector.fetch_government_services()))
    schedule.every().week.do(lambda: asyncio.run(collector.collect_all_data()))
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_data_collection()
```

### **9. API Configuration Template**

#### **Environment Variables for APIs**
```bash
# Weather APIs
OPENWEATHER_API_KEY=your_openweather_api_key
NWS_API_USER_AGENT=EVY/1.0

# Government APIs
USA_GOV_API_KEY=your_usa_gov_api_key
MUNICIPAL_API_URL=https://data.yourcity.gov/api
MUNICIPAL_API_KEY=your_municipal_api_key

# Transportation APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
TRANSIT_API_URL=https://api.yourcity.gov/transit
TRANSIT_API_KEY=your_transit_api_key

# Health APIs
CMS_API_KEY=your_cms_api_key
HEALTH_DEPARTMENT_API=your_health_dept_api

# Education APIs
COLLEGE_SCORECARD_API_KEY=your_college_scorecard_key
SCHOOL_DISTRICT_API=your_school_district_api

# Community APIs
EVENTBRITE_TOKEN=your_eventbrite_token
MEETUP_API_KEY=your_meetup_api_key
YELP_API_KEY=your_yelp_api_key

# Location Configuration
LOCATION_LATITUDE=40.7128
LOCATION_LONGITUDE=-74.0060
LOCATION_ZIP_CODE=10001
LOCATION_CITY=New York
LOCATION_STATE=NY
```

### **10. Free vs Paid APIs**

#### **Free APIs (No Cost):**
- ✅ National Weather Service (US)
- ✅ USA.gov Government Services
- ✅ CMS Hospital Compare
- ✅ College Scorecard
- ✅ Open Data Portals (many cities)
- ✅ Transit APIs (many cities)

#### **Paid APIs (Subscription Required):**
- 💰 OpenWeatherMap ($0.0015/call after free tier)
- 💰 Google Maps API ($0.005-0.02 per request)
- 💰 Yelp API ($0.01 per request)
- 💰 Eventbrite API ($0.01 per request)
- 💰 Meetup API (Free tier: 200 requests/hour)

### **11. Rate Limiting & Best Practices**

#### **Rate Limiting Strategy:**
```python
import time
from functools import wraps

def rate_limit(calls_per_hour):
    def decorator(func):
        last_called = [0.0]
        calls_made = [0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Reset counter every hour
            if now - last_called[0] >= 3600:
                calls_made[0] = 0
                last_called[0] = now
            
            if calls_made[0] >= calls_per_hour:
                sleep_time = 3600 - (now - last_called[0])
                time.sleep(sleep_time)
                calls_made[0] = 0
                last_called[0] = time.time()
            
            calls_made[0] += 1
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@rate_limit(1000)  # 1000 calls per hour
async def fetch_government_data():
    # API call here
    pass
```

### **12. Error Handling & Fallbacks**

```python
async def safe_api_call(api_func, *args, **kwargs):
    """Safely call API with error handling and fallbacks"""
    try:
        result = await api_func(*args, **kwargs)
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

# Usage with fallback
async def get_weather_data():
    # Try primary API
    weather = await safe_api_call(fetch_openweather_data)
    if weather:
        return weather
    
    # Fallback to secondary API
    weather = await safe_api_call(fetch_nws_data)
    if weather:
        return weather
    
    # Last resort: cached data
    return get_cached_weather_data()
```

## 🚀 **Quick Start: Set Up API Integration**

### **Step 1: Get API Keys**
```bash
# Sign up for free APIs
# - OpenWeatherMap: https://openweathermap.org/api
# - USA.gov: https://api.usa.gov/
# - College Scorecard: https://api.data.gov/signup/
```

### **Step 2: Configure Location**
```bash
# Add to your .env file
LOCATION_LATITUDE=40.7128
LOCATION_LONGITUDE=-74.0060
LOCATION_ZIP_CODE=10001
LOCATION_CITY=New York
LOCATION_STATE=NY
```

### **Step 3: Run Data Collection**
```bash
# Start the data collection service
python scripts/collect_local_data.py

# Or integrate with your deployment
docker-compose -f docker-compose.hybrid.yml up -d data-collector
```

This comprehensive API integration will automatically populate your local RAG knowledge base with current, relevant local information from multiple public sources!
