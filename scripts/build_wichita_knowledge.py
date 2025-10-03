#!/usr/bin/env python3
"""
Build Wichita, KS 67205 Offline Knowledge Base for lilEVY
Location-specific emergency and service information
"""

import json
import os
import requests
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WichitaKnowledgeBuilder:
    """Builds Wichita, KS specific offline knowledge base"""
    
    def __init__(self):
        self.location = {
            "city": "Wichita",
            "state": "KS",
            "zip_code": "67205",
            "latitude": "37.6872",
            "longitude": "-97.3301",
            "county": "Sedgwick County"
        }
        self.knowledge_base = []
        
    def add_wichita_emergency_contacts(self):
        """Add Wichita-specific emergency contacts and procedures"""
        emergency_data = [
            {
                "title": "Wichita Police Department",
                "text": "Wichita Police: Emergency 911. Non-emergency: (316) 268-4401. Address: 455 N Main St, Wichita, KS 67202. Available 24/7.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_police",
                    "service": "police",
                    "location": "Wichita, KS",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Wichita Fire Department",
                "text": "Wichita Fire: Emergency 911. Non-emergency: (316) 268-4441. Address: 455 N Main St, Wichita, KS 67202. 24/7 emergency response.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_fire",
                    "service": "fire",
                    "location": "Wichita, KS",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Wichita Area Hospitals",
                "text": "Major hospitals: Via Christi St Francis (929 N St Francis St), Wesley Medical Center (550 N Hillside St), Ascension Via Christi St Teresa (418 S Belmont St). All have 24/7 ER.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_hospitals",
                    "service": "hospital",
                    "location": "Wichita, KS",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Sedgwick County Emergency Management",
                "text": "Sedgwick County Emergency: (316) 660-5959. Address: 714 N Main St, Wichita, KS 67203. Coordinates disaster response for Wichita area.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "sedgwick_emergency",
                    "service": "emergency_management",
                    "location": "Sedgwick County, KS",
                    "response_type": "emergency"
                }
            },
            {
                "title": "Kansas Poison Control",
                "text": "Kansas Poison Control: 1-800-222-1222. Available 24/7. For poisoning emergencies, medication questions, or exposure concerns.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "kansas_poison_control",
                    "service": "poison_control",
                    "phone": "1-800-222-1222",
                    "response_type": "emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_data)
        logger.info(f"Added {len(emergency_data)} Wichita emergency contacts")
    
    def add_wichita_weather_safety(self):
        """Add Wichita-specific weather safety information"""
        weather_data = [
            {
                "title": "Tornado Safety - Wichita Area",
                "text": "Tornado season: March-July. Warning signs: dark green sky, large hail, wall cloud. Take shelter in basement or interior room. Avoid mobile homes and vehicles.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_weather",
                    "condition": "tornado",
                    "location": "Wichita, KS",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Severe Weather - Wichita",
                "text": "Wichita weather: Hot summers (90°F+), cold winters (20°F-). Severe storms common spring/summer. Flash floods possible. Stay weather aware.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_weather",
                    "condition": "severe_weather",
                    "location": "Wichita, KS",
                    "response_type": "weather_advice"
                }
            },
            {
                "title": "Heat Safety - Wichita Summers",
                "text": "Wichita summers: High humidity, 90-100°F common. Heat index often 100-110°F. Stay hydrated, avoid outdoor activities 10AM-4PM, seek air conditioning.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_weather",
                    "condition": "heat_wave",
                    "location": "Wichita, KS",
                    "response_type": "weather_advice"
                }
            },
            {
                "title": "Winter Weather - Wichita",
                "text": "Wichita winters: Cold snaps, ice storms, occasional snow. Wind chill can drop to -20°F. Dress in layers, avoid travel during ice storms.",
                "category": "weather_safety",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_weather",
                    "condition": "winter_weather",
                    "location": "Wichita, KS",
                    "response_type": "weather_advice"
                }
            }
        ]
        
        self.knowledge_base.extend(weather_data)
        logger.info(f"Added {len(weather_data)} Wichita weather safety procedures")
    
    def add_wichita_healthcare_services(self):
        """Add Wichita healthcare services information"""
        healthcare_data = [
            {
                "title": "Wichita Urgent Care Centers",
                "text": "Wichita urgent care: MedExpress (multiple locations), FastMed (multiple locations), CareNow (multiple locations). Faster than ER, lower cost. Check hours before going.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_healthcare",
                    "service_type": "urgent_care",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita 24-Hour Pharmacies",
                "text": "24-hour pharmacies in Wichita: Walgreens (multiple locations), CVS (multiple locations). Call ahead to confirm availability and prescription services.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_healthcare",
                    "service_type": "pharmacy",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Mental Health Crisis",
                "text": "Mental health crisis: Comcare of Sedgwick County (316) 660-7540. 24/7 crisis intervention. National Suicide Prevention: 988. You are not alone.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_mental_health",
                    "service": "crisis_line",
                    "phone": "(316) 660-7540",
                    "response_type": "crisis_support"
                }
            },
            {
                "title": "Wichita VA Medical Center",
                "text": "Wichita VA Medical Center: 5500 E Kellogg Dr, Wichita, KS 67218. Phone: (316) 685-2221. Emergency services available. Veterans healthcare services.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_va",
                    "service": "veterans_healthcare",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(healthcare_data)
        logger.info(f"Added {len(healthcare_data)} Wichita healthcare services")
    
    def add_wichita_government_services(self):
        """Add Wichita government services information"""
        government_data = [
            {
                "title": "Wichita City Hall",
                "text": "Wichita City Hall: 455 N Main St, Wichita, KS 67202. Phone: (316) 268-4000. Hours: Mon-Fri 8AM-5PM. Services: permits, licenses, city services.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_city_hall",
                    "service": "city_hall",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Sedgwick County Courthouse",
                "text": "Sedgwick County Courthouse: 525 N Main St, Wichita, KS 67203. Phone: (316) 660-9100. Hours: Mon-Fri 8AM-5PM. Services: court, records, licenses.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "sedgwick_courthouse",
                    "service": "county_services",
                    "location": "Sedgwick County, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Kansas DMV - Wichita",
                "text": "Kansas DMV Wichita: 130 S Market St, Wichita, KS 67202. Phone: (316) 337-9000. Hours: Mon-Fri 8AM-5PM. Services: driver licenses, vehicle registration, ID cards.",
                "category": "government",
                "metadata": {
                    "priority": "medium",
                    "source": "kansas_dmv",
                    "service": "dmv",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Public Library",
                "text": "Wichita Public Library: Central Library at 223 S Main St, Wichita, KS 67202. Phone: (316) 261-8500. Hours: Mon-Thu 9AM-9PM, Fri-Sat 9AM-6PM, Sun 1-5PM.",
                "category": "government",
                "metadata": {
                    "priority": "low",
                    "source": "wichita_library",
                    "service": "library",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(government_data)
        logger.info(f"Added {len(government_data)} Wichita government services")
    
    def add_wichita_utilities(self):
        """Add Wichita utility services information"""
        utilities_data = [
            {
                "title": "Evergy Power Outages - Wichita",
                "text": "Evergy power outages: Report at 1-800-EVERGY (383-7491) or online. Wichita area served by Evergy. Check outage map for updates and restoration times.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "evergy_wichita",
                    "utility": "power",
                    "location": "Wichita, KS",
                    "response_type": "utility_info"
                }
            },
            {
                "title": "Wichita Water Service",
                "text": "Wichita Water: Emergency (316) 303-8000, Customer service (316) 303-8000. Address: 119 E 1st St, Wichita, KS 67202. Report water emergencies immediately.",
                "category": "utilities",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_water",
                    "utility": "water",
                    "location": "Wichita, KS",
                    "response_type": "utility_info"
                }
            },
            {
                "title": "Kansas Gas Service - Wichita",
                "text": "Kansas Gas Service: Emergency (316) 943-3000, Customer service (316) 943-3000. For gas leaks, evacuate immediately and call from outside.",
                "category": "utilities",
                "metadata": {
                    "priority": "critical",
                    "source": "kansas_gas",
                    "utility": "gas",
                    "location": "Wichita, KS",
                    "response_type": "utility_info"
                }
            },
            {
                "title": "Cox Communications - Wichita",
                "text": "Cox Communications: Customer service (316) 722-4444, Technical support (316) 722-4444. Internet and cable services for Wichita area.",
                "category": "utilities",
                "metadata": {
                    "priority": "medium",
                    "source": "cox_wichita",
                    "utility": "internet",
                    "location": "Wichita, KS",
                    "response_type": "utility_info"
                }
            }
        ]
        
        self.knowledge_base.extend(utilities_data)
        logger.info(f"Added {len(utilities_data)} Wichita utility services")
    
    def add_wichita_transportation(self):
        """Add Wichita transportation information"""
        transportation_data = [
            {
                "title": "Wichita Transit (Wichita Area Rapid Transit)",
                "text": "Wichita Transit: Phone (316) 265-7221. Fixed route buses, paratransit services. Fares: $1.75 adult, $0.85 reduced. Routes cover Wichita area.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_transit",
                    "service": "public_transit",
                    "location": "Wichita, KS",
                    "response_type": "transportation_info"
                }
            },
            {
                "title": "Wichita Eisenhower National Airport",
                "text": "Wichita Airport (ICT): 2173 S Airport Rd, Wichita, KS 67209. Phone: (316) 946-4700. Commercial flights, general aviation. 24/7 operations.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_airport",
                    "service": "airport",
                    "location": "Wichita, KS",
                    "response_type": "transportation_info"
                }
            },
            {
                "title": "Wichita Road Conditions",
                "text": "Wichita road conditions: Check Kansas Department of Transportation (511) or Wichita Public Works (316) 268-4000. Winter weather can affect roads.",
                "category": "transportation",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_roads",
                    "service": "road_conditions",
                    "location": "Wichita, KS",
                    "response_type": "transportation_info"
                }
            }
        ]
        
        self.knowledge_base.extend(transportation_data)
        logger.info(f"Added {len(transportation_data)} Wichita transportation services")
    
    def add_wichita_specific_emergencies(self):
        """Add Wichita-specific emergency scenarios"""
        wichita_emergencies = [
            {
                "title": "Wichita Tornado Emergency",
                "text": "Wichita tornado: Go to basement or interior room. Avoid windows. If in mobile home, go to nearest sturdy building. Listen to weather radio for updates.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_tornado",
                    "disaster_type": "tornado",
                    "location": "Wichita, KS",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Wichita Flood Safety",
                "text": "Wichita flooding: Avoid driving through flood waters. Turn around, don't drown. Move to higher ground. Stay informed via weather radio or local news.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "wichita_flood",
                    "disaster_type": "flood",
                    "location": "Wichita, KS",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Wichita Heat Emergency",
                "text": "Wichita heat emergency: Stay hydrated, avoid outdoor activities 10AM-4PM. Seek air conditioning. Check on elderly neighbors. Heat index often exceeds 100°F.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "wichita_heat",
                    "condition": "heat_emergency",
                    "location": "Wichita, KS",
                    "response_type": "weather_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(wichita_emergencies)
        logger.info(f"Added {len(wichita_emergencies)} Wichita-specific emergencies")
    
    def add_wichita_community_resources(self):
        """Add Wichita community resources"""
        community_data = [
            {
                "title": "Wichita Food Bank",
                "text": "Kansas Food Bank: 1919 E Douglas Ave, Wichita, KS 67211. Phone: (316) 265-3663. Emergency food assistance for those in need.",
                "category": "local_info",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_food_bank",
                    "service": "food_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Homeless Services",
                "text": "Wichita homeless services: Union Rescue Mission (316) 263-3441, Catholic Charities (316) 264-8344. Emergency shelter and assistance available.",
                "category": "local_info",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_homeless_services",
                    "service": "homeless_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Senior Services",
                "text": "Wichita senior services: Senior Services Inc (316) 267-0302. Meals on Wheels, transportation, health services for seniors in Wichita area.",
                "category": "local_info",
                "metadata": {
                    "priority": "medium",
                    "source": "wichita_senior_services",
                    "service": "senior_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_data)
        logger.info(f"Added {len(community_data)} Wichita community resources")
    
    def build_wichita_knowledge_base(self):
        """Build the complete Wichita-specific knowledge base"""
        logger.info("Building Wichita, KS offline knowledge base...")
        
        # Add knowledge in priority order
        self.add_wichita_emergency_contacts()
        self.add_wichita_specific_emergencies()
        self.add_wichita_weather_safety()
        self.add_wichita_healthcare_services()
        self.add_wichita_government_services()
        self.add_wichita_utilities()
        self.add_wichita_transportation()
        self.add_wichita_community_resources()
        
        logger.info(f"Built Wichita knowledge base with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_wichita_knowledge_base(self, filename: str = None):
        """Save the Wichita knowledge base to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wichita_knowledge_{timestamp}.json"
        
        filepath = os.path.join("data", "offline_knowledge", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved Wichita knowledge base to {filepath}")
        return filepath
    
    def get_priority_stats(self):
        """Get statistics by priority level"""
        priorities = {}
        for entry in self.knowledge_base:
            priority = entry['metadata'].get('priority', 'unknown')
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return priorities

def main():
    """Main function to build Wichita knowledge base"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Wichita, KS offline knowledge base for lilEVY")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build Wichita knowledge base
    builder = WichitaKnowledgeBuilder()
    knowledge_base = builder.build_wichita_knowledge_base()
    
    # Save to file
    filepath = builder.save_wichita_knowledge_base(args.output)
    
    # Print statistics
    stats = builder.get_priority_stats()
    print(f"\n📊 Wichita, KS Offline Knowledge Base Statistics:")
    print(f"  Total entries: {len(knowledge_base)}")
    print(f"  Priority breakdown:")
    for priority, count in sorted(stats.items()):
        print(f"    - {priority}: {count} entries")
    
    print(f"\n💾 Saved to: {filepath}")
    print(f"📍 Location: Wichita, KS 67205")
    
    # Show sample entries
    print(f"\n📋 Sample Wichita entries:")
    for i, entry in enumerate(knowledge_base[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()
    
    print(f"\n🎯 Wichita-Specific Features:")
    print(f"  ✅ Tornado safety procedures")
    print(f"  ✅ Local emergency contacts")
    print(f"  ✅ Wichita hospitals and healthcare")
    print(f"  ✅ Sedgwick County services")
    print(f"  ✅ Local utility companies")
    print(f"  ✅ Wichita Transit information")
    print(f"  ✅ Community resources")

if __name__ == "__main__":
    main()
