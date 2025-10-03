#!/usr/bin/env python3
"""
Technology & Digital Resources System Builder
Creates comprehensive technology and digital resources information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnologyDigitalResourcesBuilder:
    """Builds comprehensive technology and digital resources system"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_internet_and_connectivity(self):
        """Add internet and connectivity services"""
        internet_connectivity = [
            # Internet Service Providers
            {
                "title": "Cox Communications",
                "text": "Cox Communications: High-speed internet, cable TV, home phone services. Plans from 25 Mbps to 1 Gbps. Installation and technical support available. Contact: (316) 269-5000. Service area covers most of Wichita and surrounding areas.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "internet_service_providers",
                    "services": ["high_speed_internet", "cable_tv", "home_phone", "installation", "technical_support"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "AT&T Internet",
                "text": "AT&T Internet: DSL and fiber internet services. Plans from 25 Mbps to 1 Gbps. Bundled services with TV and phone available. Contact: (316) 269-5000. Service availability varies by location in Wichita area.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "internet_service_providers",
                    "services": ["dsl_internet", "fiber_internet", "bundled_services", "tv_phone"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Verizon Internet",
                "text": "Verizon Internet: DSL and fiber internet services. Plans from 25 Mbps to 1 Gbps. Mobile hotspot options available. Contact: (316) 269-5000. Limited service area in Wichita, primarily fiber in select neighborhoods.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "low",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "internet_service_providers",
                    "services": ["dsl_internet", "fiber_internet", "mobile_hotspot"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Public Internet Access
            {
                "title": "Wichita Public Library Internet Access",
                "text": "Library Internet: Free public computers and Wi-Fi at all Wichita Public Library locations. High-speed internet, printing services, basic software. Time limits apply. Library card required for computer use. Wi-Fi available 24/7 outside library buildings.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "public_internet_access",
                    "services": ["free_computers", "wifi", "printing_services", "basic_software", "library_card"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Community Internet Centers",
                "text": "Community Centers: Free internet access at various community centers, senior centers, and recreation centers throughout Wichita. Computers available for public use during center hours. Basic assistance available from staff.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "public_internet_access",
                    "services": ["free_internet", "public_computers", "staff_assistance", "community_centers"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Mobile Internet
            {
                "title": "Mobile Internet Options",
                "text": "Mobile Internet: Verizon, AT&T, T-Mobile, and other carriers offer mobile internet through smartphones, tablets, and mobile hotspots. 5G coverage available in most of Wichita. Data plans vary by carrier and usage needs.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "internet_connectivity",
                    "subcategory": "mobile_internet",
                    "services": ["mobile_internet", "smartphones", "tablets", "mobile_hotspots", "5g_coverage"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(internet_connectivity)
        logger.info(f"Added {len(internet_connectivity)} internet and connectivity entries")
    
    def add_digital_literacy_programs(self):
        """Add digital literacy and computer training programs"""
        digital_literacy = [
            # Computer Training
            {
                "title": "Wichita Public Library Computer Classes",
                "text": "Library Computer Classes: Free basic computer classes for beginners. Topics include internet basics, email, Microsoft Office, social media, online safety. Classes held at various library branches. Registration required. No prior experience necessary.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "computer_training",
                    "services": ["basic_computer_classes", "internet_basics", "email", "microsoft_office", "online_safety"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "WSU Tech Computer Training",
                "text": "WSU Tech Training: Computer skills training for adults. Basic computer literacy, Microsoft Office, internet skills, job search assistance. Classes available during day and evening. Some programs may have fees. Contact: (316) 677-9400.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "computer_training",
                    "services": ["computer_literacy", "microsoft_office", "internet_skills", "job_search", "day_evening_classes"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Senior Computer Training",
                "text": "Senior Computer Training: Specialized computer classes for seniors at senior centers and community centers. Patient instruction, small class sizes, basic skills focus. Topics include internet basics, email, social media, online banking safety.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "computer_training",
                    "services": ["senior_focused", "patient_instruction", "small_classes", "basic_skills", "online_safety"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Online Safety
            {
                "title": "Internet Safety Education",
                "text": "Internet Safety: Educational programs on online safety, identity theft prevention, phishing awareness, secure passwords, social media safety. Available through libraries, community centers, and senior centers. Free resources and training materials available.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "online_safety",
                    "services": ["online_safety", "identity_theft_prevention", "phishing_awareness", "secure_passwords", "social_media_safety"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Cybersecurity Awareness",
                "text": "Cybersecurity Awareness: Programs on protecting personal information online, recognizing scams, secure online shopping, safe social media use. Available through various community organizations and libraries. Free educational materials and workshops.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "online_safety",
                    "services": ["personal_information_protection", "scam_recognition", "secure_shopping", "safe_social_media"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Job Search Technology
            {
                "title": "Online Job Search Training",
                "text": "Job Search Training: Classes on using online job boards, creating professional profiles, online applications, resume building software, LinkedIn basics. Available through libraries, workforce development centers, and community organizations.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "digital_literacy",
                    "subcategory": "job_search_technology",
                    "services": ["online_job_boards", "professional_profiles", "online_applications", "resume_software", "linkedin_basics"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(digital_literacy)
        logger.info(f"Added {len(digital_literacy)} digital literacy entries")
    
    def add_online_services(self):
        """Add online services and digital resources"""
        online_services = [
            # Government Services
            {
                "title": "Online Government Services",
                "text": "Government Services Online: Many government services available online including vehicle registration, property tax payments, business licenses, court records, permits. Visit cityofwichita.org, sedgwickcounty.org, or kansas.gov for specific services.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "online_services",
                    "subcategory": "government_services",
                    "services": ["vehicle_registration", "property_tax_payments", "business_licenses", "court_records", "permits"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Online Banking and Financial Services",
                "text": "Online Banking: Most banks and credit unions offer online banking services including account management, bill payment, transfers, mobile deposits. Online investment services, insurance quotes, and financial planning tools also available.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "online_services",
                    "subcategory": "financial_services",
                    "services": ["account_management", "bill_payment", "transfers", "mobile_deposits", "investment_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Healthcare Services
            {
                "title": "Telehealth and Online Healthcare",
                "text": "Telehealth Services: Many healthcare providers offer virtual appointments, online prescription refills, patient portals, health records access. Major insurance plans cover telehealth services. Available through hospitals, clinics, and private practices.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "online_services",
                    "subcategory": "healthcare_services",
                    "services": ["virtual_appointments", "online_prescriptions", "patient_portals", "health_records", "insurance_coverage"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Education Services
            {
                "title": "Online Education Resources",
                "text": "Online Education: Free online courses, tutorials, and educational resources available through libraries, community colleges, and online platforms. Topics include computer skills, job training, academic subjects, personal enrichment.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "online_services",
                    "subcategory": "education_services",
                    "services": ["free_online_courses", "tutorials", "educational_resources", "computer_skills", "job_training"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Shopping and Services
            {
                "title": "Online Shopping and Delivery",
                "text": "Online Shopping: Local businesses offer online ordering and delivery services for groceries, restaurants, retail items. Major retailers provide online shopping with local pickup or delivery options. Compare prices and read reviews before purchasing.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "low",
                    "source": "technology_digital",
                    "tech_category": "online_services",
                    "subcategory": "shopping_services",
                    "services": ["online_ordering", "delivery_services", "local_pickup", "price_comparison", "reviews"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(online_services)
        logger.info(f"Added {len(online_services)} online services entries")
    
    def add_technology_support(self):
        """Add technology support and assistance services"""
        technology_support = [
            # Computer Repair
            {
                "title": "Computer Repair Services",
                "text": "Computer Repair: Local computer repair shops offer services for desktop computers, laptops, tablets, smartphones. Services include virus removal, hardware repair, data recovery, software installation. Compare prices and check reviews before choosing a service provider.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "technology_support",
                    "subcategory": "computer_repair",
                    "services": ["desktop_repair", "laptop_repair", "tablet_repair", "smartphone_repair", "virus_removal", "data_recovery"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Geek Squad Services",
                "text": "Geek Squad: Best Buy's technical support service. In-store and in-home services for computers, tablets, smartphones, home theater, appliances. Services include setup, repair, troubleshooting, data transfer. Extended warranties and protection plans available.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "low",
                    "source": "technology_digital",
                    "tech_category": "technology_support",
                    "subcategory": "computer_repair",
                    "services": ["in_store_services", "in_home_services", "setup", "repair", "troubleshooting", "data_transfer"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Technical Support
            {
                "title": "Free Technical Support Resources",
                "text": "Free Tech Support: Many technology companies offer free technical support through online chat, phone, or email. Libraries and community centers may offer basic technical assistance. Online forums and help centers provide free troubleshooting guides.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "technology_support",
                    "subcategory": "technical_support",
                    "services": ["online_chat", "phone_support", "email_support", "basic_assistance", "online_forums"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Senior Technology Support",
                "text": "Senior Tech Support: Specialized technology support for seniors at senior centers, libraries, and community organizations. Patient instruction, one-on-one assistance, basic troubleshooting. Help with smartphones, tablets, computers, and internet safety.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "technology_support",
                    "subcategory": "technical_support",
                    "services": ["senior_focused", "patient_instruction", "one_on_one_assistance", "basic_troubleshooting", "internet_safety"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Device Setup and Training
            {
                "title": "Device Setup and Training",
                "text": "Device Setup: Help setting up new computers, tablets, smartphones, smart home devices. Training on basic functions, apps, internet connectivity, security settings. Available through retail stores, libraries, and community organizations.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "technology_support",
                    "subcategory": "device_setup",
                    "services": ["device_setup", "basic_functions", "apps", "internet_connectivity", "security_settings"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(technology_support)
        logger.info(f"Added {len(technology_support)} technology support entries")
    
    def add_digital_accessibility(self):
        """Add digital accessibility and assistive technology"""
        digital_accessibility = [
            # Assistive Technology
            {
                "title": "Assistive Technology Resources",
                "text": "Assistive Technology: Resources for individuals with disabilities including screen readers, voice recognition software, adaptive keyboards, large print displays, audio books. Available through libraries, disability services, and specialized organizations.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "digital_accessibility",
                    "subcategory": "assistive_technology",
                    "services": ["screen_readers", "voice_recognition", "adaptive_keyboards", "large_print", "audio_books"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Accessibility Services at Libraries",
                "text": "Library Accessibility: Wichita Public Library offers accessibility services including large print books, audio books, screen readers, adaptive computer equipment, sign language interpreters for programs. Specialized training and assistance available.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "medium",
                    "source": "technology_digital",
                    "tech_category": "digital_accessibility",
                    "subcategory": "assistive_technology",
                    "services": ["large_print_books", "audio_books", "screen_readers", "adaptive_equipment", "sign_language_interpreters"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Digital Inclusion
            {
                "title": "Digital Inclusion Programs",
                "text": "Digital Inclusion: Programs to ensure everyone has access to technology and digital skills. Low-cost internet programs, computer donation programs, digital literacy training, community technology centers. Available through various organizations.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "digital_accessibility",
                    "subcategory": "digital_inclusion",
                    "services": ["low_cost_internet", "computer_donations", "digital_literacy", "community_centers"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Low-Income Internet Programs",
                "text": "Low-Income Internet: Internet service providers offer discounted internet services for qualifying low-income households. Programs include Cox Connect2Compete, AT&T Access, and others. Eligibility based on income and participation in assistance programs.",
                "category": "technology_digital",
                "metadata": {
                    "priority": "high",
                    "source": "technology_digital",
                    "tech_category": "digital_accessibility",
                    "subcategory": "digital_inclusion",
                    "services": ["discounted_internet", "connect2compete", "att_access", "income_based_eligibility"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(digital_accessibility)
        logger.info(f"Added {len(digital_accessibility)} digital accessibility entries")
    
    def build_technology_digital_resources(self):
        """Build the complete technology and digital resources system"""
        logger.info("Building comprehensive technology and digital resources system...")
        
        # Add technology information in priority order
        self.add_internet_and_connectivity()
        self.add_digital_literacy_programs()
        self.add_online_services()
        self.add_technology_support()
        self.add_digital_accessibility()
        
        logger.info(f"Built technology and digital resources system with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_technology_digital_resources(self, filename: str = None):
        """Save the technology and digital resources system to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"technology_digital_resources_{timestamp}.json"
        
        filepath = os.path.join("data", "technology_digital", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved technology and digital resources system to {filepath}")
        return filepath
    
    def get_technology_stats(self):
        """Get statistics by technology category and subcategory"""
        tech_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            tech_category = entry['metadata'].get('tech_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            tech_categories[tech_category] = tech_categories.get(tech_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return tech_categories, subcategories

def main():
    """Main function to build technology and digital resources system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive technology and digital resources system")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build technology and digital resources system
    builder = TechnologyDigitalResourcesBuilder()
    technology_system = builder.build_technology_digital_resources()
    
    # Save to file
    filepath = builder.save_technology_digital_resources(args.output)
    
    # Print statistics
    tech_categories, subcategories = builder.get_technology_stats()
    
    print(f"\nTechnology & Digital Resources System Statistics:")
    print(f"  Total entries: {len(technology_system)}")
    print(f"  Technology categories:")
    for category, count in sorted(tech_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample technology and digital resources entries:")
    for i, entry in enumerate(technology_system[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Technology Category: {entry['metadata']['tech_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
