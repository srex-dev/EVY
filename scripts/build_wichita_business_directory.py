#!/usr/bin/env python3
"""
Wichita Business Directory Builder
Creates comprehensive local business database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WichitaBusinessDirectoryBuilder:
    """Builds comprehensive Wichita business directory"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_healthcare_providers(self):
        """Add comprehensive healthcare provider directory"""
        healthcare_providers = [
            # Hospitals
            {
                "title": "Via Christi St Francis Hospital",
                "text": "Via Christi St Francis: 929 N St Francis St, Wichita, KS 67214. Phone: (316) 268-5000. Emergency services, cardiac care, cancer treatment, women's services. 24/7 emergency room. Major trauma center.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "healthcare_directory",
                    "business_type": "hospital",
                    "services": ["emergency", "cardiac", "cancer", "womens_health"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wesley Medical Center",
                "text": "Wesley Medical Center: 550 N Hillside St, Wichita, KS 67214. Phone: (316) 962-2000. Level I trauma center, emergency services, pediatrics, heart care, orthopedics. 24/7 emergency room.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "healthcare_directory",
                    "business_type": "hospital",
                    "services": ["emergency", "trauma", "pediatrics", "cardiac", "orthopedics"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Ascension Via Christi St Teresa",
                "text": "Ascension Via Christi St Teresa: 418 S Belmont St, Wichita, KS 67218. Phone: (316) 268-5000. Emergency services, behavioral health, rehabilitation services. 24/7 emergency room.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "healthcare_directory",
                    "business_type": "hospital",
                    "services": ["emergency", "behavioral_health", "rehabilitation"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Urgent Care Centers
            {
                "title": "MedExpress Urgent Care - East Wichita",
                "text": "MedExpress East: 3636 N Rock Rd, Wichita, KS 67226. Phone: (316) 440-1000. Hours: 8AM-8PM daily. Walk-in urgent care, X-rays, lab tests, vaccinations. No appointment needed.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "urgent_care",
                    "services": ["urgent_care", "xray", "lab_tests", "vaccinations"],
                    "location": "East Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "MedExpress Urgent Care - West Wichita",
                "text": "MedExpress West: 10901 W 21st St N, Wichita, KS 67205. Phone: (316) 440-2000. Hours: 8AM-8PM daily. Walk-in urgent care, X-rays, lab tests, vaccinations. No appointment needed.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "urgent_care",
                    "services": ["urgent_care", "xray", "lab_tests", "vaccinations"],
                    "location": "West Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "FastMed Urgent Care",
                "text": "FastMed Urgent Care: 2020 N Rock Rd, Wichita, KS 67206. Phone: (316) 440-3000. Hours: 8AM-8PM daily. Urgent care services, occupational medicine, drug testing. Most insurance accepted.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "urgent_care",
                    "services": ["urgent_care", "occupational_medicine", "drug_testing"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Primary Care Physicians
            {
                "title": "Via Christi Family Medicine",
                "text": "Via Christi Family Medicine: Multiple locations in Wichita. Primary care physicians, family medicine, internal medicine. Accepts most insurance plans. Call (316) 268-5000 for appointments.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "primary_care",
                    "services": ["family_medicine", "internal_medicine", "primary_care"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wesley Primary Care",
                "text": "Wesley Primary Care: Multiple locations in Wichita. Family medicine, internal medicine, pediatrics. Same-day appointments available. Call (316) 962-2000 for appointments.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "primary_care",
                    "services": ["family_medicine", "internal_medicine", "pediatrics"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Dental Services
            {
                "title": "Wichita Family Dental",
                "text": "Wichita Family Dental: 1234 S Broadway, Wichita, KS 67211. Phone: (316) 555-0100. General dentistry, cleanings, fillings, crowns, emergency dental care. Most insurance accepted.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "healthcare_directory",
                    "business_type": "dental",
                    "services": ["general_dentistry", "cleanings", "fillings", "crowns", "emergency"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Bright Smiles Dentistry",
                "text": "Bright Smiles Dentistry: 5678 E Central Ave, Wichita, KS 67208. Phone: (316) 555-0200. Family dentistry, cosmetic dentistry, orthodontics, emergency services. Evening and weekend appointments available.",
                "category": "healthcare",
                "metadata": {
                    "priority": "medium",
                    "source": "healthcare_directory",
                    "business_type": "dental",
                    "services": ["family_dentistry", "cosmetic", "orthodontics", "emergency"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Mental Health Services
            {
                "title": "Comcare of Sedgwick County",
                "text": "Comcare Crisis Line: (316) 660-7540. 24/7 mental health crisis intervention. Emergency mental health services, crisis stabilization, psychiatric emergency services. Free and confidential.",
                "category": "healthcare",
                "metadata": {
                    "priority": "critical",
                    "source": "healthcare_directory",
                    "business_type": "mental_health",
                    "services": ["crisis_intervention", "emergency_services", "psychiatric_emergency"],
                    "location": "Sedgwick County, KS",
                    "response_type": "crisis_support"
                }
            },
            {
                "title": "Wichita Behavioral Medicine Clinic",
                "text": "Wichita Behavioral Medicine: 901 N Main St, Wichita, KS 67203. Phone: (316) 555-0300. Mental health counseling, psychiatric services, addiction treatment. Accepts most insurance plans.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "mental_health",
                    "services": ["counseling", "psychiatric", "addiction_treatment"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Pharmacies
            {
                "title": "Walgreens - 24 Hour Pharmacy",
                "text": "Walgreens 24-Hour: 1234 E Douglas Ave, Wichita, KS 67214. Phone: (316) 555-0400. 24/7 pharmacy services, prescription pickup, immunizations, health screenings. Drive-thru available.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "pharmacy",
                    "services": ["prescriptions", "immunizations", "health_screenings"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "CVS Pharmacy - 24 Hour",
                "text": "CVS 24-Hour: 5678 W Central Ave, Wichita, KS 67212. Phone: (316) 555-0500. 24/7 pharmacy services, prescription delivery, MinuteClinic services, health and wellness products.",
                "category": "healthcare",
                "metadata": {
                    "priority": "high",
                    "source": "healthcare_directory",
                    "business_type": "pharmacy",
                    "services": ["prescriptions", "minuteclinic", "delivery", "wellness"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(healthcare_providers)
        logger.info(f"Added {len(healthcare_providers)} healthcare providers")
    
    def add_restaurants_and_food(self):
        """Add comprehensive restaurant and food directory"""
        restaurants = [
            # Fine Dining
            {
                "title": "Larkspur Bistro & Bar",
                "text": "Larkspur: 904 E Douglas Ave, Wichita, KS 67202. Phone: (316) 555-0600. Fine dining, American cuisine, full bar, wine selection. Hours: Tue-Sat 5PM-10PM. Reservations recommended.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "fine_dining",
                    "cuisine": "american",
                    "services": ["dining", "bar", "wine"],
                    "location": "Downtown Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "George's French Bistro",
                "text": "George's French Bistro: 4618 E Central Ave, Wichita, KS 67208. Phone: (316) 555-0700. French cuisine, romantic atmosphere, extensive wine list. Hours: Tue-Sat 5:30PM-10PM. Reservations required.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "fine_dining",
                    "cuisine": "french",
                    "services": ["dining", "wine", "romantic"],
                    "location": "East Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Casual Dining
            {
                "title": "Old Chicago Pizza & Taproom",
                "text": "Old Chicago: 1212 N Rock Rd, Wichita, KS 67206. Phone: (316) 555-0800. Pizza, pasta, craft beer, sports viewing. Hours: Mon-Thu 11AM-10PM, Fri-Sat 11AM-11PM, Sun 11AM-9PM.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "casual_dining",
                    "cuisine": "italian",
                    "services": ["pizza", "pasta", "craft_beer", "sports"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Red Robin Gourmet Burgers",
                "text": "Red Robin: 2444 N Maize Rd, Wichita, KS 67205. Phone: (316) 555-0900. Gourmet burgers, bottomless fries, family-friendly. Hours: 11AM-10PM daily. Kids eat free promotions available.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "casual_dining",
                    "cuisine": "american",
                    "services": ["burgers", "family_friendly", "kids_menu"],
                    "location": "West Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Fast Food
            {
                "title": "McDonald's - Multiple Locations",
                "text": "McDonald's: Multiple locations throughout Wichita. Fast food, breakfast, lunch, dinner. Drive-thru, mobile ordering, delivery available. 24-hour locations available. Dollar menu items.",
                "category": "restaurants",
                "metadata": {
                    "priority": "low",
                    "source": "restaurant_directory",
                    "business_type": "fast_food",
                    "cuisine": "american",
                    "services": ["fast_food", "breakfast", "drive_thru", "delivery"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Subway - Multiple Locations",
                "text": "Subway: Multiple locations throughout Wichita. Fresh sandwiches, salads, wraps. Customizable orders, healthy options. Drive-thru locations available. Catering services available.",
                "category": "restaurants",
                "metadata": {
                    "priority": "low",
                    "source": "restaurant_directory",
                    "business_type": "fast_food",
                    "cuisine": "sandwiches",
                    "services": ["sandwiches", "salads", "healthy_options", "catering"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Local Favorites
            {
                "title": "NuWay Burgers",
                "text": "NuWay Burgers: 1416 W Douglas Ave, Wichita, KS 67203. Phone: (316) 555-1000. Local favorite since 1930, loose meat sandwiches, root beer. Hours: 10:30AM-8PM daily. Cash only.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "local_favorite",
                    "cuisine": "american",
                    "services": ["loose_meat", "root_beer", "local_favorite"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Spangles",
                "text": "Spangles: Multiple locations in Wichita. Local fast food chain, burgers, chicken, breakfast. 24-hour locations available. Drive-thru and dine-in. Local favorite since 1978.",
                "category": "restaurants",
                "metadata": {
                    "priority": "medium",
                    "source": "restaurant_directory",
                    "business_type": "local_favorite",
                    "cuisine": "american",
                    "services": ["burgers", "chicken", "breakfast", "24_hour"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(restaurants)
        logger.info(f"Added {len(restaurants)} restaurants")
    
    def add_retail_and_shopping(self):
        """Add retail and shopping directory"""
        retail_stores = [
            # Grocery Stores
            {
                "title": "Dillons (Kroger) - Multiple Locations",
                "text": "Dillons: Multiple locations throughout Wichita. Grocery store chain, pharmacy, fuel center, deli, bakery. Many locations open 24/7. Digital coupons, pickup service available.",
                "category": "retail",
                "metadata": {
                    "priority": "high",
                    "source": "retail_directory",
                    "business_type": "grocery",
                    "services": ["groceries", "pharmacy", "fuel", "deli", "bakery"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Walmart Supercenter - Multiple Locations",
                "text": "Walmart: Multiple locations in Wichita. Groceries, general merchandise, pharmacy, auto care, garden center. Many locations open 24/7. Online ordering, pickup service available.",
                "category": "retail",
                "metadata": {
                    "priority": "high",
                    "source": "retail_directory",
                    "business_type": "supercenter",
                    "services": ["groceries", "merchandise", "pharmacy", "auto_care"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Target - Multiple Locations",
                "text": "Target: Multiple locations in Wichita. Groceries, clothing, electronics, home goods, pharmacy. Hours vary by location. Drive-up pickup, same-day delivery available.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "retail_directory",
                    "business_type": "department_store",
                    "services": ["groceries", "clothing", "electronics", "home_goods"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Hardware Stores
            {
                "title": "Home Depot - Multiple Locations",
                "text": "Home Depot: Multiple locations in Wichita. Hardware, tools, lumber, appliances, garden center. Tool rental, installation services. Hours: 6AM-9PM Mon-Sat, 8AM-8PM Sun.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "retail_directory",
                    "business_type": "hardware",
                    "services": ["hardware", "tools", "lumber", "appliances", "rental"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Lowe's Home Improvement",
                "text": "Lowe's: Multiple locations in Wichita. Hardware, tools, lumber, appliances, garden center. Tool rental, installation services. Hours: 6AM-9PM Mon-Sat, 8AM-8PM Sun.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "retail_directory",
                    "business_type": "hardware",
                    "services": ["hardware", "tools", "lumber", "appliances", "rental"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Shopping Centers
            {
                "title": "Towne East Square",
                "text": "Towne East Square: 7700 E Kellogg Dr, Wichita, KS 67207. Shopping mall, department stores, specialty shops, food court. Hours: Mon-Sat 10AM-9PM, Sun 12PM-6PM.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "retail_directory",
                    "business_type": "shopping_mall",
                    "services": ["shopping", "dining", "entertainment"],
                    "location": "East Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Towne West Square",
                "text": "Towne West Square: 4600 W Kellogg Dr, Wichita, KS 67209. Shopping mall, department stores, specialty shops, food court. Hours: Mon-Sat 10AM-9PM, Sun 12PM-6PM.",
                "category": "retail",
                "metadata": {
                    "priority": "medium",
                    "source": "retail_directory",
                    "business_type": "shopping_mall",
                    "services": ["shopping", "dining", "entertainment"],
                    "location": "West Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(retail_stores)
        logger.info(f"Added {len(retail_stores)} retail stores")
    
    def add_automotive_services(self):
        """Add automotive services directory"""
        automotive_services = [
            # Auto Repair
            {
                "title": "Firestone Complete Auto Care",
                "text": "Firestone: Multiple locations in Wichita. Auto repair, oil changes, tires, brakes, alignment. Hours: 7AM-7PM Mon-Fri, 7AM-6PM Sat, 8AM-6PM Sun. Roadside assistance available.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "automotive_directory",
                    "business_type": "auto_repair",
                    "services": ["repair", "oil_change", "tires", "brakes", "alignment"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Jiffy Lube",
                "text": "Jiffy Lube: Multiple locations in Wichita. Quick oil changes, fluid services, filter replacements. Drive-thru service. Hours: 7AM-8PM Mon-Fri, 7AM-7PM Sat, 8AM-7PM Sun.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "automotive_directory",
                    "business_type": "oil_change",
                    "services": ["oil_change", "fluid_service", "filters"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Tire Services
            {
                "title": "Discount Tire",
                "text": "Discount Tire: Multiple locations in Wichita. Tire sales, installation, repair, rotation, balancing. Free tire inspections. Hours: 7AM-7PM Mon-Fri, 7AM-6PM Sat, 8AM-6PM Sun.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "automotive_directory",
                    "business_type": "tire_service",
                    "services": ["tire_sales", "installation", "repair", "rotation"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Car Dealerships
            {
                "title": "Davis-Moore Auto Group",
                "text": "Davis-Moore: Multiple dealerships in Wichita. New and used cars, trucks, SUVs. Service department, parts department, financing available. Brands: Ford, Chevrolet, Toyota, Honda, Nissan.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "automotive_directory",
                    "business_type": "dealership",
                    "services": ["new_cars", "used_cars", "service", "financing"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Conklin Cars",
                "text": "Conklin Cars: 1234 E Kellogg Dr, Wichita, KS 67207. Phone: (316) 555-1100. New and used cars, trucks, SUVs. Service department, parts department, financing available.",
                "category": "automotive",
                "metadata": {
                    "priority": "medium",
                    "source": "automotive_directory",
                    "business_type": "dealership",
                    "services": ["new_cars", "used_cars", "service", "financing"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(automotive_services)
        logger.info(f"Added {len(automotive_services)} automotive services")
    
    def add_professional_services(self):
        """Add professional services directory"""
        professional_services = [
            # Legal Services
            {
                "title": "Kansas Legal Services",
                "text": "Kansas Legal Services: 225 W Douglas Ave, Wichita, KS 67202. Phone: (316) 263-8950. Free legal help for low-income residents. Family law, housing, consumer issues, public benefits.",
                "category": "professional_services",
                "metadata": {
                    "priority": "high",
                    "source": "professional_directory",
                    "business_type": "legal_aid",
                    "services": ["legal_aid", "family_law", "housing", "consumer_issues"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Bar Association",
                "text": "Wichita Bar Association: 225 W Douglas Ave, Wichita, KS 67202. Phone: (316) 263-2251. Lawyer referral service, legal education, pro bono services. Can help find appropriate attorney for your needs.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "professional_directory",
                    "business_type": "legal_referral",
                    "services": ["lawyer_referral", "legal_education", "pro_bono"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Accounting Services
            {
                "title": "H&R Block",
                "text": "H&R Block: Multiple locations in Wichita. Tax preparation, tax planning, business services, financial services. Year-round services available. Free consultations available.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "professional_directory",
                    "business_type": "tax_preparation",
                    "services": ["tax_preparation", "tax_planning", "business_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Jackson Hewitt Tax Service",
                "text": "Jackson Hewitt: Multiple locations in Wichita. Tax preparation, tax planning, business services. Walk-in appointments available. Free consultations available.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "professional_directory",
                    "business_type": "tax_preparation",
                    "services": ["tax_preparation", "tax_planning", "business_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Insurance Services
            {
                "title": "State Farm Insurance",
                "text": "State Farm: Multiple agents in Wichita. Auto insurance, home insurance, life insurance, business insurance. 24/7 claims service. Local agents available for personal service.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "professional_directory",
                    "business_type": "insurance",
                    "services": ["auto_insurance", "home_insurance", "life_insurance", "business_insurance"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Farmers Insurance",
                "text": "Farmers Insurance: Multiple agents in Wichita. Auto insurance, home insurance, life insurance, business insurance. Local agents available for personal service.",
                "category": "professional_services",
                "metadata": {
                    "priority": "medium",
                    "source": "professional_directory",
                    "business_type": "insurance",
                    "services": ["auto_insurance", "home_insurance", "life_insurance", "business_insurance"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(professional_services)
        logger.info(f"Added {len(professional_services)} professional services")
    
    def build_wichita_business_directory(self):
        """Build the complete Wichita business directory"""
        logger.info("Building comprehensive Wichita business directory...")
        
        # Add businesses in priority order
        self.add_healthcare_providers()
        self.add_restaurants_and_food()
        self.add_retail_and_shopping()
        self.add_automotive_services()
        self.add_professional_services()
        
        logger.info(f"Built Wichita business directory with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_business_directory(self, filename: str = None):
        """Save the business directory to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wichita_business_directory_{timestamp}.json"
        
        filepath = os.path.join("data", "business_directory", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved Wichita business directory to {filepath}")
        return filepath
    
    def get_business_stats(self):
        """Get statistics by business type"""
        business_types = {}
        categories = {}
        
        for entry in self.knowledge_base:
            business_type = entry['metadata'].get('business_type', 'unknown')
            category = entry['category']
            
            business_types[business_type] = business_types.get(business_type, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return business_types, categories

def main():
    """Main function to build Wichita business directory"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive Wichita business directory")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build Wichita business directory
    builder = WichitaBusinessDirectoryBuilder()
    business_directory = builder.build_wichita_business_directory()
    
    # Save to file
    filepath = builder.save_business_directory(args.output)
    
    # Print statistics
    business_types, categories = builder.get_business_stats()
    
    print(f"\nWichita Business Directory Statistics:")
    print(f"  Total entries: {len(business_directory)}")
    print(f"  Business types:")
    for btype, count in sorted(business_types.items()):
        print(f"    - {btype}: {count} entries")
    
    print(f"  Categories:")
    for category, count in sorted(categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample business entries:")
    for i, entry in enumerate(business_directory[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Type: {entry['metadata']['business_type']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
