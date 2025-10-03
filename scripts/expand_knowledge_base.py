#!/usr/bin/env python3
"""
Knowledge Base Expansion Script
Builds comprehensive local knowledge base for lilEVY
"""

import json
import os
import requests
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseExpander:
    """Expands the knowledge base with comprehensive local information"""
    
    def __init__(self, location_config: Dict):
        self.location = location_config
        self.knowledge_base = []
        
    def add_comprehensive_emergency_procedures(self):
        """Add comprehensive emergency procedures database"""
        emergency_procedures = [
            # Medical Emergencies
            {
                "title": "Heart Attack Emergency Response",
                "text": "Heart attack signs: chest pain, shortness of breath, nausea, sweating, arm/jaw pain. Call 911 immediately. Keep patient calm, seated, loosen clothing. If they have heart medication, help them take it. Do not drive them - wait for ambulance.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "heart_attack",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Stroke Emergency Response",
                "text": "Stroke signs: facial drooping, arm weakness, speech difficulty (FAST). Call 911 immediately. Note time symptoms started. Keep patient calm and comfortable. Do not give food or water. If stroke medication available, do not give without medical supervision.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "stroke",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Choking Emergency Response",
                "text": "Choking: If person can cough or speak, encourage coughing. If cannot breathe, perform Heimlich maneuver. Stand behind person, hands above navel, quick upward thrusts. For unconscious person, start CPR. Call 911 immediately.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "choking",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Allergic Reaction Emergency",
                "text": "Severe allergic reaction signs: difficulty breathing, swelling of face/throat, hives, nausea, dizziness. Call 911 immediately. If person has epinephrine auto-injector, help them use it. Keep person calm and lying down with legs elevated.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "allergic_reaction",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Seizure Emergency Response",
                "text": "Seizure: Do not restrain person. Clear area of dangerous objects. Place person on side if possible. Do not put anything in mouth. Time the seizure. Call 911 if seizure lasts more than 5 minutes or person is injured. Stay with person until fully conscious.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "seizure",
                    "response_type": "medical_emergency"
                }
            },
            
            # Natural Disasters
            {
                "title": "Tornado Emergency - Home",
                "text": "Tornado at home: Go to basement or lowest floor. Interior room without windows. Bathroom or closet. Cover head and neck. Stay away from windows and doors. Avoid mobile homes - go to nearest sturdy building.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "tornado",
                    "location": "home",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Tornado Emergency - Vehicle",
                "text": "Tornado in vehicle: Do not try to outrun tornado. Park vehicle, get out, find lowest area nearby. Lie flat, cover head with hands. Avoid overpasses and bridges. Do not stay in vehicle.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "tornado",
                    "location": "vehicle",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Flood Emergency Response",
                "text": "Flood warning: Move to higher ground immediately. Do not walk or drive through flood waters. Turn around, don't drown. Turn off utilities if safe to do so. Stay informed via weather radio or local news.",
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
                "text": "Power outage: Check if neighbors have power. Report to utility company. Use flashlights, not candles. Keep refrigerator and freezer closed. Generator: use outdoors only, away from windows. Check on elderly neighbors.",
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
                "text": "Gas leak suspected: Evacuate immediately. Do not use phones, lights, or electrical devices. Call 911 from outside. Do not return until cleared by officials. If you smell gas, leave immediately.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "utility_emergency",
                    "utility_type": "gas",
                    "response_type": "utility_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_procedures)
        logger.info(f"Added {len(emergency_procedures)} emergency procedures")
    
    def add_comprehensive_business_directory(self):
        """Add comprehensive local business directory"""
        business_categories = [
            # Healthcare Providers
            {
                "title": "Wichita Primary Care Doctors",
                "text": "Primary care doctors in Wichita: Check with Via Christi, Wesley, and Ascension networks. Many accept most insurance plans. Call ahead for appointments. Urgent care available for non-emergencies.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "business_directory",
                    "business_type": "healthcare",
                    "subcategory": "primary_care",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Dentists",
                "text": "Dentists in Wichita: Many general and specialty dentists available. Check with dental insurance for covered providers. Emergency dental services available. Regular cleanings recommended every 6 months.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "healthcare",
                    "subcategory": "dental",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Pharmacies",
                "text": "Pharmacies in Wichita: Walgreens, CVS, Walmart, and local pharmacies available throughout the city. Many offer 24-hour service. Prescription delivery available from some locations.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "business_directory",
                    "business_type": "pharmacy",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Professional Services
            {
                "title": "Wichita Legal Services",
                "text": "Legal services in Wichita: Private attorneys, legal aid organizations, and pro bono services available. Kansas Legal Services provides free legal help for low-income residents. Check with local bar association for referrals.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "legal",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Accounting Services",
                "text": "Accounting services in Wichita: CPAs, tax preparers, and bookkeeping services available. Many offer year-round services beyond tax season. Check credentials and reviews before hiring.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "accounting",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Insurance Agents",
                "text": "Insurance agents in Wichita: Auto, home, health, and life insurance available. Independent agents can compare multiple companies. Check ratings and get multiple quotes before purchasing.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "insurance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Retail & Shopping
            {
                "title": "Wichita Grocery Stores",
                "text": "Grocery stores in Wichita: Dillons (Kroger), Walmart, Target, Aldi, and local markets available. Many offer online ordering and pickup. Check store hours and sales flyers for best deals.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "grocery",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Hardware Stores",
                "text": "Hardware stores in Wichita: Home Depot, Lowe's, and local hardware stores available. Many offer tool rental and project advice. Check for seasonal sales and local contractor discounts.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "hardware",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Auto Services",
                "text": "Auto services in Wichita: Oil changes, tire shops, auto repair, and car dealerships available throughout the city. Check reviews and get multiple estimates for major repairs.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "business_directory",
                    "business_type": "automotive",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(business_categories)
        logger.info(f"Added {len(business_categories)} business directory entries")
    
    def add_educational_resources(self):
        """Add comprehensive educational resources"""
        educational_resources = [
            # K-12 Education
            {
                "title": "Wichita Public Schools",
                "text": "Wichita Public Schools: USD 259 serves Wichita area. Multiple elementary, middle, and high schools available. Special education services, gifted programs, and extracurricular activities offered. Contact district office for enrollment information.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "k12",
                    "district": "USD 259",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Private Schools",
                "text": "Private schools in Wichita: Catholic, Christian, and independent private schools available. Many offer smaller class sizes and specialized programs. Contact individual schools for admission requirements and tuition information.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "private",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Charter Schools",
                "text": "Charter schools in Wichita: Alternative public schools with specialized curricula available. Many focus on specific areas like STEM, arts, or college preparation. Contact individual schools for application processes.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "charter",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Higher Education
            {
                "title": "Wichita State University",
                "text": "Wichita State University: Public research university offering undergraduate and graduate programs. Strong engineering, business, and health sciences programs. Contact admissions office for application information and financial aid.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "higher",
                    "institution_type": "university",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Area Technical College",
                "text": "Wichita Area Technical College: Offers technical and vocational programs, certifications, and workforce training. Programs in healthcare, manufacturing, technology, and skilled trades. Contact for program information and enrollment.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "technical",
                    "institution_type": "community_college",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Adult Education
            {
                "title": "Adult Education in Wichita",
                "text": "Adult education in Wichita: GED preparation, English as Second Language (ESL), basic skills, and workforce training available. Many programs are free or low-cost. Contact local adult education centers for enrollment information.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "adult",
                    "program_type": "basic_skills",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(educational_resources)
        logger.info(f"Added {len(educational_resources)} educational resources")
    
    def add_community_services(self):
        """Add comprehensive community services"""
        community_services = [
            # Social Services
            {
                "title": "Wichita Food Assistance",
                "text": "Food assistance in Wichita: Kansas Food Bank, local food pantries, and meal programs available. Many locations offer emergency food assistance. Contact United Way 211 for referrals to food assistance programs.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_resources",
                    "service_type": "food_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Housing Assistance",
                "text": "Housing assistance in Wichita: Section 8 housing, emergency shelter, and housing counseling services available. Contact Wichita Housing Authority or local homeless service providers for assistance.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_resources",
                    "service_type": "housing_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Utility Assistance",
                "text": "Utility assistance in Wichita: LIHEAP (energy assistance), water bill assistance, and weatherization programs available. Contact local social services or utility companies for program information and eligibility requirements.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_resources",
                    "service_type": "utility_assistance",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Senior Services
            {
                "title": "Wichita Senior Services",
                "text": "Senior services in Wichita: Meals on Wheels, senior centers, transportation assistance, and health programs available. Contact Senior Services Inc or local senior centers for program information and eligibility.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_resources",
                    "service_type": "senior_services",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Youth Services
            {
                "title": "Wichita Youth Programs",
                "text": "Youth programs in Wichita: Boys & Girls Clubs, YMCA, 4-H, and after-school programs available. Many offer sports, arts, education, and leadership development. Contact individual organizations for program schedules and registration.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_resources",
                    "service_type": "youth_programs",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_services)
        logger.info(f"Added {len(community_services)} community services")
    
    def add_legal_resources(self):
        """Add legal resources and information"""
        legal_resources = [
            {
                "title": "Kansas Legal Services",
                "text": "Kansas Legal Services: Free legal help for low-income residents. Services include family law, housing, consumer issues, and public benefits. Contact (316) 263-8950 for intake and eligibility screening.",
                "category": "legal",
                "metadata": {
                    "priority": "high",
                    "source": "legal_resources",
                    "service_type": "legal_aid",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Court Services",
                "text": "Wichita court services: Sedgwick County District Court handles civil and criminal cases. Court clerk's office provides forms and filing assistance. Check court website for procedures, fees, and self-help resources.",
                "category": "legal",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_resources",
                    "service_type": "court_services",
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Consumer Protection Resources",
                "text": "Consumer protection in Kansas: Kansas Attorney General's office handles consumer complaints and fraud reports. Better Business Bureau provides business ratings and complaint resolution. Contact for consumer rights information and complaint filing.",
                "category": "legal",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_resources",
                    "service_type": "consumer_protection",
                    "location": "Kansas",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(legal_resources)
        logger.info(f"Added {len(legal_resources)} legal resources")
    
    def build_expanded_knowledge_base(self):
        """Build the complete expanded knowledge base"""
        logger.info("Building expanded knowledge base...")
        
        # Add knowledge in priority order
        self.add_comprehensive_emergency_procedures()
        self.add_comprehensive_business_directory()
        self.add_educational_resources()
        self.add_community_services()
        self.add_legal_resources()
        
        logger.info(f"Built expanded knowledge base with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_expanded_knowledge_base(self, filename: str = None):
        """Save the expanded knowledge base to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expanded_knowledge_{self.location['city']}_{timestamp}.json"
        
        filepath = os.path.join("data", "expanded_knowledge", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved expanded knowledge base to {filepath}")
        return filepath
    
    def get_category_stats(self):
        """Get statistics by category"""
        categories = {}
        for entry in self.knowledge_base:
            category = entry['category']
            categories[category] = categories.get(category, 0) + 1
        
        return categories

def main():
    """Main function to build expanded knowledge base"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build expanded knowledge base for lilEVY")
    parser.add_argument("--city", default="Wichita", help="City name")
    parser.add_argument("--state", default="KS", help="State abbreviation")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Location configuration
    location_config = {
        "city": args.city,
        "state": args.state,
        "latitude": "37.6872",
        "longitude": "-97.3301",
        "zip_code": "67205"
    }
    
    # Build expanded knowledge base
    expander = KnowledgeBaseExpander(location_config)
    knowledge_base = expander.build_expanded_knowledge_base()
    
    # Save to file
    filepath = expander.save_expanded_knowledge_base(args.output)
    
    # Print statistics
    categories = expander.get_category_stats()
    print(f"\nExpanded Knowledge Base Statistics:")
    print(f"  Total entries: {len(knowledge_base)}")
    print(f"  Categories:")
    for category, count in sorted(categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    print(f"Location: {location_config['city']}, {location_config['state']}")
    
    # Show sample entries
    print(f"\nSample entries:")
    for i, entry in enumerate(knowledge_base[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
