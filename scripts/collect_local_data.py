#!/usr/bin/env python3
"""
EVY Local Data Collection Script
Automatically collects local information from public APIs
"""

import asyncio
import os
import json
import logging
import requests
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LocationConfig:
    """Location configuration for data collection"""
    latitude: float
    longitude: float
    zip_code: str
    city: str
    state: str
    country: str = "US"

class LocalDataCollector:
    """Collects local data from various public APIs"""
    
    def __init__(self, location: LocationConfig):
        self.location = location
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EVY-Local-Data-Collector/1.0'
        })
        
        # API Keys (load from environment)
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        self.usa_gov_key = os.getenv('USA_GOV_API_KEY')
        self.yelp_key = os.getenv('YELP_API_KEY')
        
        # Data storage
        self.collected_data = []
        
    async def collect_weather_data(self) -> List[Dict]:
        """Collect weather data from OpenWeatherMap"""
        if not self.openweather_key:
            logger.warning("OpenWeatherMap API key not provided")
            return []
        
        try:
            # Current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.location.latitude}&lon={self.location.longitude}&appid={self.openweather_key}&units=imperial"
            current_response = self.session.get(current_url)
            current_data = current_response.json()
            
            # 5-day forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.location.latitude}&lon={self.location.longitude}&appid={self.openweather_key}&units=imperial"
            forecast_response = self.session.get(forecast_url)
            forecast_data = forecast_response.json()
            
            weather_docs = []
            
            # Current conditions
            current_temp = current_data['main']['temp']
            current_desc = current_data['weather'][0]['description']
            humidity = current_data['main']['humidity']
            wind_speed = current_data['wind']['speed']
            
            current_text = f"Current weather: {current_temp}°F, {current_desc}. Humidity: {humidity}%. Wind: {wind_speed} mph."
            
            weather_docs.append({
                "title": "Current Weather Conditions",
                "text": current_text,
                "category": "weather",
                "metadata": {
                    "priority": "medium",
                    "source": "openweathermap",
                    "location": f"{self.location.city}, {self.location.state}",
                    "last_updated": datetime.now().isoformat()
                }
            })
            
            # Tomorrow's forecast
            tomorrow_forecast = forecast_data['list'][8]  # 24 hours from now
            tomorrow_temp = tomorrow_forecast['main']['temp']
            tomorrow_desc = tomorrow_forecast['weather'][0]['description']
            
            forecast_text = f"Tomorrow's forecast: {tomorrow_temp}°F, {tomorrow_desc}."
            
            weather_docs.append({
                "title": "Tomorrow's Weather Forecast",
                "text": forecast_text,
                "category": "weather",
                "metadata": {
                    "priority": "medium",
                    "source": "openweathermap",
                    "location": f"{self.location.city}, {self.location.state}",
                    "last_updated": datetime.now().isoformat()
                }
            })
            
            logger.info(f"Collected weather data for {self.location.city}")
            return weather_docs
            
        except Exception as e:
            logger.error(f"Failed to collect weather data: {e}")
            return []
    
    async def collect_nws_alerts(self) -> List[Dict]:
        """Collect weather alerts from National Weather Service"""
        try:
            alerts_url = f"https://api.weather.gov/alerts?point={self.location.latitude},{self.location.longitude}"
            response = self.session.get(alerts_url)
            alerts_data = response.json()
            
            alert_docs = []
            
            for alert in alerts_data.get('features', []):
                alert_props = alert['properties']
                
                alert_text = f"Weather Alert: {alert_props.get('headline', 'Active weather alert')}. {alert_props.get('description', '')[:200]}..."
                
                alert_docs.append({
                    "title": f"Weather Alert: {alert_props.get('event', 'Weather Warning')}",
                    "text": alert_text,
                    "category": "emergency",
                    "metadata": {
                        "priority": "high",
                        "source": "national_weather_service",
                        "alert_type": alert_props.get('event'),
                        "severity": alert_props.get('severity'),
                        "location": f"{self.location.city}, {self.location.state}",
                        "last_updated": datetime.now().isoformat()
                    }
                })
            
            logger.info(f"Collected {len(alert_docs)} weather alerts for {self.location.city}")
            return alert_docs
            
        except Exception as e:
            logger.error(f"Failed to collect NWS alerts: {e}")
            return []
    
    async def collect_government_services(self) -> List[Dict]:
        """Collect government services information"""
        try:
            # USA.gov API for government services
            if self.usa_gov_key:
                gov_url = f"https://api.usa.gov/contacts?zipcode={self.location.zip_code}"
                headers = {"Authorization": f"Bearer {self.usa_gov_key}"}
                response = self.session.get(gov_url, headers=headers)
                gov_data = response.json()
                
                gov_docs = []
                for service in gov_data.get('results', [])[:10]:  # Limit to first 10
                    service_text = f"Government Service: {service.get('name', 'Unknown')}. {service.get('description', '')[:150]}..."
                    if service.get('phone'):
                        service_text += f" Phone: {service['phone']}"
                    
                    gov_docs.append({
                        "title": f"Government Service: {service.get('name', 'Unknown')}",
                        "text": service_text,
                        "category": "government",
                        "metadata": {
                            "priority": "medium",
                            "source": "usa_gov_api",
                            "location": self.location.zip_code,
                            "last_updated": datetime.now().isoformat()
                        }
                    })
                
                logger.info(f"Collected {len(gov_docs)} government services")
                return gov_docs
            
            # Fallback: Generic government services info
            return [{
                "title": "Government Services Directory",
                "text": f"For {self.location.city}, {self.location.state} government services, visit your local city hall or check the official city website. Emergency services: 911.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "generic",
                    "location": f"{self.location.city}, {self.location.state}",
                    "last_updated": datetime.now().isoformat()
                }
            }]
            
        except Exception as e:
            logger.error(f"Failed to collect government services: {e}")
            return []
    
    async def collect_hospitals(self) -> List[Dict]:
        """Collect local hospital information"""
        try:
            # CMS Hospital Compare API (simplified)
            # Note: This is a simplified version - actual CMS API requires more complex queries
            
            hospital_docs = []
            
            # Generic hospital information based on location
            hospital_text = f"For {self.location.city}, {self.location.state}: Emergency services available at local hospitals. Call 911 for medical emergencies. For non-emergency medical care, contact your nearest hospital or urgent care center."
            
            hospital_docs.append({
                "title": "Local Hospital Information",
                "text": hospital_text,
                "category": "health",
                "metadata": {
                    "priority": "high",
                    "source": "generic",
                    "location": f"{self.location.city}, {self.location.state}",
                    "last_updated": datetime.now().isoformat()
                }
            })
            
            # Emergency contacts
            emergency_text = f"Emergency Services for {self.location.city}, {self.location.state}: Call 911 for police, fire, or medical emergencies. For poison control: 1-800-222-1222. For non-emergency police: contact your local police department."
            
            hospital_docs.append({
                "title": "Emergency Services Contacts",
                "text": emergency_text,
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "generic",
                    "location": f"{self.location.city}, {self.location.state}",
                    "last_updated": datetime.now().isoformat()
                }
            })
            
            logger.info(f"Collected hospital and emergency information for {self.location.city}")
            return hospital_docs
            
        except Exception as e:
            logger.error(f"Failed to collect hospital information: {e}")
            return []
    
    async def collect_local_businesses(self) -> List[Dict]:
        """Collect local business information using Yelp API"""
        if not self.yelp_key:
            logger.warning("Yelp API key not provided")
            return []
        
        try:
            business_categories = [
                "restaurants",
                "health",
                "shopping",
                "financialservices",
                "education"
            ]
            
            business_docs = []
            
            for category in business_categories:
                yelp_url = f"https://api.yelp.com/v3/businesses/search"
                params = {
                    "location": f"{self.location.city}, {self.location.state}",
                    "categories": category,
                    "limit": 5
                }
                headers = {"Authorization": f"Bearer {self.yelp_key}"}
                
                response = self.session.get(yelp_url, params=params, headers=headers)
                yelp_data = response.json()
                
                for business in yelp_data.get('businesses', []):
                    business_text = f"{business['name']}: {business.get('categories', [{}])[0].get('title', 'Local business')}. "
                    if business.get('phone'):
                        business_text += f"Phone: {business['phone']}. "
                    if business.get('location', {}).get('address1'):
                        business_text += f"Address: {business['location']['address1']}. "
                    business_text += f"Rating: {business.get('rating', 'N/A')}/5 stars."
                    
                    business_docs.append({
                        "title": f"Local Business: {business['name']}",
                        "text": business_text,
                        "category": "local_info",
                        "metadata": {
                            "priority": "medium",
                            "source": "yelp_api",
                            "business_category": business.get('categories', [{}])[0].get('title', ''),
                            "location": f"{self.location.city}, {self.location.state}",
                            "last_updated": datetime.now().isoformat()
                        }
                    })
            
            logger.info(f"Collected {len(business_docs)} local businesses for {self.location.city}")
            return business_docs
            
        except Exception as e:
            logger.error(f"Failed to collect local businesses: {e}")
            return []
    
    async def collect_all_data(self) -> List[Dict]:
        """Collect data from all available sources"""
        logger.info(f"Starting data collection for {self.location.city}, {self.location.state}")
        
        all_data = []
        
        # Collect from all sources
        tasks = [
            self.collect_weather_data(),
            self.collect_nws_alerts(),
            self.collect_government_services(),
            self.collect_hospitals(),
            self.collect_local_businesses()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Data collection task failed: {result}")
        
        logger.info(f"Collected {len(all_data)} documents total")
        return all_data
    
    def save_data_to_file(self, data: List[Dict], filename: str = None):
        """Save collected data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"local_data_{self.location.city}_{timestamp}.json"
        
        filepath = os.path.join("data", "collected", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} documents to {filepath}")
        return filepath

async def main():
    """Main data collection function"""
    # Load location from environment or use defaults
    location = LocationConfig(
        latitude=float(os.getenv('LOCATION_LATITUDE', '40.7128')),
        longitude=float(os.getenv('LOCATION_LONGITUDE', '-74.0060')),
        zip_code=os.getenv('LOCATION_ZIP_CODE', '10001'),
        city=os.getenv('LOCATION_CITY', 'New York'),
        state=os.getenv('LOCATION_STATE', 'NY')
    )
    
    collector = LocalDataCollector(location)
    
    # Collect all data
    data = await collector.collect_all_data()
    
    # Save to file
    filepath = collector.save_data_to_file(data)
    
    print(f"\n🎉 Data collection completed!")
    print(f"📊 Collected {len(data)} documents")
    print(f"💾 Saved to: {filepath}")
    print(f"📍 Location: {location.city}, {location.state}")
    
    # Print summary
    categories = {}
    for doc in data:
        category = doc['category']
        categories[category] = categories.get(category, 0) + 1
    
    print(f"\n📋 Data by category:")
    for category, count in categories.items():
        print(f"  - {category}: {count} documents")

if __name__ == "__main__":
    # Run the data collection
    asyncio.run(main())
