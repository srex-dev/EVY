#!/usr/bin/env python3
"""
Build Offline Knowledge Base for lilEVY
Prioritizes critical information for offline SMS LLM responses
"""

import json
import os
import requests
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OfflineKnowledgeBuilder:
    """Builds prioritized offline knowledge base for lilEVY"""
    
    def __init__(self, location_config: Dict):
        self.location = location_config
        self.knowledge_base = []
        
    def add_emergency_procedures(self):
        """Add critical emergency procedures and contacts"""
        emergency_data = [
            {
                "title": "Emergency Services - 911",
                "text": "Emergency: Call 911 for police, fire, or medical emergencies. Stay calm, provide clear location, describe the situation. Do not hang up until told to do so.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "emergency_procedures",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Medical Emergency - Heart Attack",
                "text": "Heart attack signs: chest pain, shortness of breath, nausea, sweating. Call 911 immediately. Keep patient calm, seated, loosen clothing. If they have heart medication, help them take it.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "heart_attack",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Medical Emergency - Stroke",
                "text": "Stroke signs: facial drooping, arm weakness, speech difficulty. Call 911 immediately. Note time symptoms started. Keep patient calm and comfortable. Do not give food or water.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "stroke",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Poison Control",
                "text": "Poison emergency: Call 1-800-222-1222 immediately. Do not induce vomiting unless instructed. Have product container ready. Provide age and weight if known.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "poison_control",
                    "phone": "1-800-222-1222",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Natural Disaster - Tornado",
                "text": "Tornado warning: Go to lowest floor, interior room, away from windows. Cover head and neck. Avoid mobile homes. Stay in shelter until all clear.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "tornado",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Natural Disaster - Flood",
                "text": "Flood warning: Move to higher ground immediately. Do not walk or drive through flood waters. Turn off utilities if safe. Stay informed via radio.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "flood",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Power Outage Emergency",
                "text": "Power outage: Check if neighbors have power. Report to utility company. Use flashlights, not candles. Keep fridge/freezer closed. Generator: use outdoors only.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "utility_emergency",
                    "utility_type": "power",
                    "response_type": "utility_emergency"
                }
            },
            {
                "title": "Gas Leak Emergency",
                "text": "Gas leak suspected: Evacuate immediately. Do not use phones, lights, or electrical devices. Call 911 from outside. Do not return until cleared by officials.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "utility_emergency",
                    "utility_type": "gas",
                    "response_type": "utility_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_data)
        logger.info(f"Added {len(emergency_data)} emergency procedures")
    
    def add_local_emergency_contacts(self):
        """Add local emergency service contacts"""
        # Generic emergency contacts - should be customized for actual location
        emergency_contacts = [
            {
                "title": "Local Police Department",
                "text": f"Police non-emergency for {self.location['city']}, {self.location['state']}: Contact your local police department. For emergencies, call 911.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "local_contacts",
                    "service": "police",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "contact_info"
                }
            },
            {
                "title": "Local Fire Department",
                "text": f"Fire department for {self.location['city']}, {self.location['state']}: For fires, call 911. For non-emergency fire department services, contact your local fire station.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "local_contacts",
                    "service": "fire",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "contact_info"
                }
            },
            {
                "title": "Local Hospital Emergency Room",
                "text": f"Emergency room for {self.location['city']}, {self.location['state']}: For medical emergencies, call 911 or go to nearest hospital emergency room. Local hospitals available 24/7.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "local_contacts",
                    "service": "hospital",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "contact_info"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_contacts)
        logger.info(f"Added {len(emergency_contacts)} local emergency contacts")
    
    def add_weather_safety_info(self):
        """Add weather-related safety information"""
        weather_safety = [
            {
                "title": "Heat Wave Safety",
                "text": "Heat wave: Stay hydrated, wear light clothing, avoid outdoor activities during peak heat. Watch for heat exhaustion signs: heavy sweating, weakness, nausea. Seek cool shelter.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "weather_safety",
                    "condition": "heat_wave",
                    "response_type": "weather_advice"
                }
            },
            {
                "title": "Cold Weather Safety",
                "text": "Cold weather: Dress in layers, cover exposed skin, avoid prolonged outdoor exposure. Watch for frostbite signs: numbness, white/gray skin. Seek warm shelter immediately.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "weather_safety",
                    "condition": "cold_weather",
                    "response_type": "weather_advice"
                }
            },
            {
                "title": "Lightning Safety",
                "text": "Lightning: When thunder roars, go indoors. Stay inside for 30 minutes after last thunder. Avoid plumbing, electronics, windows. If outside, avoid tall objects, water, metal.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "weather_safety",
                    "condition": "lightning",
                    "response_type": "weather_advice"
                }
            },
            {
                "title": "Winter Storm Safety",
                "text": "Winter storm: Stay indoors if possible. Keep emergency supplies: food, water, blankets, flashlight. Avoid unnecessary travel. Check on neighbors, especially elderly.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "weather_safety",
                    "condition": "winter_storm",
                    "response_type": "weather_advice"
                }
            }
        ]
        
        self.knowledge_base.extend(weather_safety)
        logger.info(f"Added {len(weather_safety)} weather safety procedures")
    
    def add_healthcare_services(self):
        """Add local healthcare service information"""
        healthcare_info = [
            {
                "title": "Urgent Care Centers",
                "text": f"Urgent care in {self.location['city']}, {self.location['state']}: For non-emergency medical needs, visit local urgent care center. Faster than ER, lower cost. Check hours before going.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_services",
                    "service_type": "urgent_care",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "service_info"
                }
            },
            {
                "title": "24-Hour Pharmacies",
                "text": f"24-hour pharmacy in {self.location['city']}, {self.location['state']}: For emergency prescriptions, check local 24-hour pharmacies. Call ahead to confirm availability and hours.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "healthcare_services",
                    "service_type": "pharmacy",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Mental Health Crisis",
                "text": "Mental health crisis: Call 988 (Suicide & Crisis Lifeline) or 911 for immediate help. You are not alone. Help is available 24/7. Stay safe.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "mental_health",
                    "service": "crisis_line",
                    "phone": "988",
                    "response_type": "crisis_support"
                }
            }
        ]
        
        self.knowledge_base.extend(healthcare_info)
        logger.info(f"Added {len(healthcare_info)} healthcare services")
    
    def add_essential_services(self):
        """Add essential local services information"""
        essential_services = [
            {
                "title": "City Hall Services",
                "text": f"City hall in {self.location['city']}, {self.location['state']}: For permits, licenses, city services. Check website for hours and services. Many services available online.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "government_services",
                    "service": "city_hall",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Power Outage Reporting",
                "text": f"Power outage in {self.location['city']}, {self.location['state']}: Report outages to your utility company. Check if neighbors affected. Use flashlights, keep fridge closed.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "utility_services",
                    "utility": "power",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "utility_info"
                }
            },
            {
                "title": "Water Service Issues",
                "text": f"Water problems in {self.location['city']}, {self.location['state']}: Report water issues to local water department. For emergencies, call 911. Boil water if advised.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "utility_services",
                    "utility": "water",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "utility_info"
                }
            }
        ]
        
        self.knowledge_base.extend(essential_services)
        logger.info(f"Added {len(essential_services)} essential services")
    
    def add_transportation_info(self):
        """Add local transportation information"""
        transportation_info = [
            {
                "title": "Public Transportation",
                "text": f"Public transit in {self.location['city']}, {self.location['state']}: Check local transit authority for routes, schedules, fares. Many systems have real-time updates online.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "transportation",
                    "service": "public_transit",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "transportation_info"
                }
            },
            {
                "title": "Road Conditions",
                "text": f"Road conditions in {self.location['city']}, {self.location['state']}: Check local transportation department for road closures, construction, weather-related conditions.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "transportation",
                    "service": "road_conditions",
                    "location": f"{self.location['city']}, {self.location['state']}",
                    "response_type": "transportation_info"
                }
            }
        ]
        
        self.knowledge_base.extend(transportation_info)
        logger.info(f"Added {len(transportation_info)} transportation services")
    
    def add_troubleshooting_guides(self):
        """Add common troubleshooting information"""
        troubleshooting_info = [
            {
                "title": "Internet Connection Issues",
                "text": "Internet problems: Check cables, restart router/modem, check for outages. Contact ISP if issues persist. Use mobile hotspot as backup if available.",
                "category": "troubleshooting",
                "metadata": {
                    "priority": "medium",
                    "source": "troubleshooting",
                    "issue": "internet",
                    "response_type": "tech_support"
                }
            },
            {
                "title": "Phone Service Issues",
                "text": "Phone problems: Check signal strength, restart phone, check account status. Contact carrier for service issues. Use landline or neighbor's phone for emergencies.",
                "category": "troubleshooting",
                "metadata": {
                    "priority": "medium",
                    "source": "troubleshooting",
                    "issue": "phone",
                    "response_type": "tech_support"
                }
            },
            {
                "title": "Home Heating Issues",
                "text": "Heating problems: Check thermostat, circuit breakers, fuel supply. For gas heat, check pilot light. Contact HVAC professional for repairs. Use space heaters safely.",
                "category": "troubleshooting",
                "metadata": {
                    "priority": "high",
                    "source": "home_maintenance",
                    "issue": "heating",
                    "response_type": "home_repair"
                }
            }
        ]
        
        self.knowledge_base.extend(troubleshooting_info)
        logger.info(f"Added {len(troubleshooting_info)} troubleshooting guides")
    
    def build_knowledge_base(self):
        """Build the complete offline knowledge base"""
        logger.info("Building offline knowledge base...")
        
        # Add knowledge in priority order
        self.add_emergency_procedures()
        self.add_local_emergency_contacts()
        self.add_weather_safety_info()
        self.add_healthcare_services()
        self.add_essential_services()
        self.add_transportation_info()
        self.add_troubleshooting_guides()
        
        logger.info(f"Built knowledge base with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_knowledge_base(self, filename: str = None):
        """Save the knowledge base to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"offline_knowledge_{self.location['city']}_{timestamp}.json"
        
        filepath = os.path.join("data", "offline_knowledge", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved offline knowledge base to {filepath}")
        return filepath
    
    def get_priority_stats(self):
        """Get statistics by priority level"""
        priorities = {}
        for entry in self.knowledge_base:
            priority = entry['metadata'].get('priority', 'unknown')
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return priorities

def main():
    """Main function to build offline knowledge base"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build offline knowledge base for lilEVY")
    parser.add_argument("--city", default="New York", help="City name")
    parser.add_argument("--state", default="NY", help="State abbreviation")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Location configuration
    location_config = {
        "city": args.city,
        "state": args.state,
        "latitude": os.getenv('LOCATION_LATITUDE', '40.7128'),
        "longitude": os.getenv('LOCATION_LONGITUDE', '-74.0060'),
        "zip_code": os.getenv('LOCATION_ZIP_CODE', '10001')
    }
    
    # Build knowledge base
    builder = OfflineKnowledgeBuilder(location_config)
    knowledge_base = builder.build_knowledge_base()
    
    # Save to file
    filepath = builder.save_knowledge_base(args.output)
    
    # Print statistics
    stats = builder.get_priority_stats()
    print(f"\n📊 Offline Knowledge Base Statistics:")
    print(f"  Total entries: {len(knowledge_base)}")
    print(f"  Priority breakdown:")
    for priority, count in sorted(stats.items()):
        print(f"    - {priority}: {count} entries")
    
    print(f"\n💾 Saved to: {filepath}")
    print(f"📍 Location: {location_config['city']}, {location_config['state']}")
    
    # Show sample entries
    print(f"\n📋 Sample entries:")
    for i, entry in enumerate(knowledge_base[:3]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
