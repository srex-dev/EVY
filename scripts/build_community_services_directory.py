#!/usr/bin/env python3
"""
Community Services Directory Builder
Creates comprehensive community services and social services database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunityServicesDirectoryBuilder:
    """Builds comprehensive community services directory"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_social_services(self):
        """Add social services and assistance programs"""
        social_services = [
            # Food Assistance
            {
                "title": "Kansas Food Bank",
                "text": "Kansas Food Bank: 1919 E Douglas Ave, Wichita, KS 67211. Phone: (316) 265-3663. Emergency food assistance, food pantry locations, mobile food distributions. Serves Sedgwick County and surrounding areas. No income verification required for emergency assistance.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "food_assistance",
                    "services": ["emergency_food", "food_pantries", "mobile_distributions", "emergency_assistance"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "SNAP (Food Stamps) Benefits",
                "text": "SNAP Benefits: Apply online at dcf.ks.gov or visit local DCF office. Provides monthly food assistance for eligible families. Income limits apply. Expedited benefits available for emergency situations. Benefits loaded on EBT card.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "food_assistance",
                    "services": ["online_application", "monthly_assistance", "emergency_benefits", "ebt_card"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "WIC (Women, Infants, Children)",
                "text": "WIC Program: Nutrition assistance for pregnant women, new mothers, and children under 5. Provides healthy foods, nutrition education, breastfeeding support. Income limits apply. Apply at local health department or WIC clinic.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "food_assistance",
                    "services": ["nutrition_assistance", "healthy_foods", "nutrition_education", "breastfeeding_support"],
                    "response_type": "service_info"
                }
            },
            
            # Housing Assistance
            {
                "title": "Wichita Housing Authority",
                "text": "Wichita Housing Authority: 332 E 1st St N, Wichita, KS 67202. Phone: (316) 263-3300. Section 8 housing vouchers, public housing, housing choice voucher program. Income limits apply. Waiting lists for some programs.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "housing_assistance",
                    "services": ["section_8", "public_housing", "housing_vouchers", "income_limits"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Emergency Rental Assistance",
                "text": "Emergency Rental Assistance: Available through United Way, Salvation Army, Catholic Charities. Helps with rent, utilities, security deposits. Income limits and documentation required. One-time assistance available for qualifying emergencies.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "housing_assistance",
                    "services": ["rent_assistance", "utility_assistance", "security_deposits", "emergency_assistance"],
                    "response_type": "service_info"
                }
            },
            
            # Utility Assistance
            {
                "title": "Low Income Energy Assistance Program (LIEAP)",
                "text": "LIEAP: Helps with winter heating bills for low-income households. Apply through local community action agency. One-time assistance per heating season. Income limits apply. Applications accepted October through March.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "utility_assistance",
                    "services": ["heating_assistance", "winter_bills", "income_limits", "seasonal_application"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Water and Sewer Assistance",
                "text": "Water/Sewer Assistance: Available through City of Wichita for qualifying low-income residents. Payment plans, emergency assistance, weatherization programs. Contact City of Wichita Utilities: (316) 268-4000.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "utility_assistance",
                    "services": ["payment_plans", "emergency_assistance", "weatherization", "low_income_programs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Healthcare Assistance
            {
                "title": "Medicaid and KanCare",
                "text": "KanCare: Kansas Medicaid program providing health coverage for low-income individuals and families. Apply online at dcf.ks.gov or visit local DCF office. Covers doctor visits, prescriptions, hospital care, mental health services.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "healthcare_assistance",
                    "services": ["health_coverage", "doctor_visits", "prescriptions", "hospital_care", "mental_health"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Health Insurance Marketplace",
                "text": "Health Insurance Marketplace: Apply for affordable health insurance at healthcare.gov. Open enrollment November-December, special enrollment for qualifying events. Premium tax credits and cost-sharing reductions available for eligible individuals.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "social_services",
                    "subcategory": "healthcare_assistance",
                    "services": ["health_insurance", "premium_credits", "cost_sharing", "special_enrollment"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(social_services)
        logger.info(f"Added {len(social_services)} social services entries")
    
    def add_mental_health_services(self):
        """Add mental health and substance abuse services"""
        mental_health_services = [
            # Crisis Services
            {
                "title": "Comcare Crisis Services",
                "text": "Comcare Crisis Line: (316) 660-7540. 24/7 mental health crisis intervention, emergency psychiatric services, crisis stabilization. Free and confidential. Mobile crisis team available for on-site response.",
                "category": "community_services",
                "metadata": {
                    "priority": "critical",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "crisis_services",
                    "services": ["crisis_intervention", "emergency_psychiatric", "crisis_stabilization", "mobile_crisis"],
                    "response_type": "crisis_support"
                }
            },
            {
                "title": "National Suicide Prevention Lifeline",
                "text": "Suicide Prevention Lifeline: 988 (24/7). Free, confidential crisis counseling for anyone in emotional distress or suicidal crisis. Trained crisis counselors available. Spanish language services available.",
                "category": "community_services",
                "metadata": {
                    "priority": "critical",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "crisis_services",
                    "services": ["suicide_prevention", "crisis_counseling", "confidential", "spanish_services"],
                    "response_type": "crisis_support"
                }
            },
            
            # Counseling Services
            {
                "title": "Community Mental Health Centers",
                "text": "Mental Health Centers: Multiple locations in Wichita providing individual therapy, group therapy, psychiatric services, medication management. Accept Medicaid, Medicare, private insurance. Sliding fee scale available.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "counseling_services",
                    "services": ["individual_therapy", "group_therapy", "psychiatric_services", "medication_management", "sliding_fee"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Family Therapy Services",
                "text": "Family Therapy: Available through community mental health centers, private practitioners, family service agencies. Helps with family conflicts, communication, parenting, relationship issues. Insurance and sliding fee options available.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "counseling_services",
                    "services": ["family_conflicts", "communication", "parenting", "relationship_issues"],
                    "response_type": "service_info"
                }
            },
            
            # Substance Abuse Services
            {
                "title": "Substance Abuse Treatment",
                "text": "Substance Abuse Treatment: Inpatient and outpatient treatment programs, detoxification services, counseling, support groups. Accept Medicaid, private insurance, sliding fee scale. Multiple treatment providers in Wichita area.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "substance_abuse",
                    "services": ["inpatient_treatment", "outpatient_treatment", "detoxification", "counseling", "support_groups"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Alcoholics Anonymous (AA)",
                "text": "Alcoholics Anonymous: Free 12-step program for alcohol recovery. Multiple meetings throughout Wichita daily. No cost, anonymous, peer support. Find meetings at aa.org or call (316) 264-0074.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "substance_abuse",
                    "services": ["12_step_program", "peer_support", "free_meetings", "anonymous"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Narcotics Anonymous (NA)",
                "text": "Narcotics Anonymous: Free 12-step program for drug addiction recovery. Multiple meetings throughout Wichita daily. No cost, anonymous, peer support. Find meetings at na.org or call (316) 264-0074.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "mental_health",
                    "subcategory": "substance_abuse",
                    "services": ["12_step_program", "peer_support", "free_meetings", "anonymous"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(mental_health_services)
        logger.info(f"Added {len(mental_health_services)} mental health services entries")
    
    def add_children_and_youth_services(self):
        """Add children and youth services"""
        children_youth_services = [
            # Child Care
            {
                "title": "Child Care Assistance Program",
                "text": "Child Care Assistance: Helps low-income families pay for child care while working or attending school. Apply through Kansas Department for Children and Families. Income limits apply. Must use licensed or registered child care providers.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "child_care",
                    "services": ["child_care_payment", "working_families", "school_attendance", "licensed_providers"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Head Start and Early Head Start",
                "text": "Head Start: Free early childhood education and development services for low-income families. Ages 3-5 for Head Start, birth-3 for Early Head Start. Includes health, nutrition, social services. Multiple locations in Wichita.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "child_care",
                    "services": ["early_childhood_education", "health_services", "nutrition", "social_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Youth Programs
            {
                "title": "Boys & Girls Clubs of South Central Kansas",
                "text": "Boys & Girls Clubs: 2400 E 9th St N, Wichita, KS 67214. Phone: (316) 263-8833. After-school programs, summer camps, educational support, sports, arts, leadership development. Membership fees apply, scholarships available.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "youth_programs",
                    "services": ["afterschool_programs", "summer_camps", "educational_support", "sports", "arts", "leadership"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "YMCA Youth Programs",
                "text": "YMCA Youth Programs: Multiple locations in Wichita. After-school care, summer camps, sports leagues, swimming lessons, teen programs, leadership development. Membership required, financial assistance available.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "youth_programs",
                    "services": ["afterschool_care", "summer_camps", "sports_leagues", "swimming_lessons", "teen_programs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Foster Care and Adoption
            {
                "title": "Foster Care Services",
                "text": "Foster Care: Temporary care for children who cannot live with their families. Foster parent training and support provided. Financial assistance available. Contact Kansas Department for Children and Families for information and application.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "foster_care",
                    "services": ["temporary_care", "foster_parent_training", "financial_assistance", "support_services"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Adoption Services",
                "text": "Adoption Services: Public and private adoption agencies in Wichita. Domestic and international adoption. Home studies, training, support services. Financial assistance may be available for special needs adoptions.",
                "category": "community_services",
                "metadata": {
                    "priority": "low",
                    "source": "community_services",
                    "service_category": "children_youth",
                    "subcategory": "adoption_services",
                    "services": ["domestic_adoption", "international_adoption", "home_studies", "training", "support_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(children_youth_services)
        logger.info(f"Added {len(children_youth_services)} children and youth services entries")
    
    def add_senior_services(self):
        """Add senior services and aging support"""
        senior_services = [
            # Senior Centers
            {
                "title": "Wichita Senior Services",
                "text": "Senior Services: Multiple senior centers throughout Wichita. Meals, activities, health programs, transportation, case management. Ages 60+. Some services have income limits. Contact: (316) 660-7290.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "senior_services",
                    "subcategory": "senior_centers",
                    "services": ["meals", "activities", "health_programs", "transportation", "case_management"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Meals on Wheels",
                "text": "Meals on Wheels: Home-delivered meals for homebound seniors. Nutritious meals delivered Monday-Friday. Income-based fees, no one denied for inability to pay. Volunteer delivery drivers needed. Contact: (316) 267-5052.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "senior_services",
                    "subcategory": "nutrition_services",
                    "services": ["home_delivered_meals", "nutritious_meals", "income_based_fees", "volunteer_opportunities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Transportation
            {
                "title": "Senior Transportation Services",
                "text": "Senior Transportation: Door-to-door transportation for medical appointments, shopping, senior center activities. Reduced fares for seniors. Wheelchair accessible vehicles available. Reservations required. Contact: (316) 660-7290.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "senior_services",
                    "subcategory": "transportation",
                    "services": ["door_to_door", "medical_appointments", "shopping", "wheelchair_accessible", "reduced_fares"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Care Management
            {
                "title": "Senior Care Management",
                "text": "Senior Care Management: Help navigating healthcare, benefits, housing, legal issues. Care coordination, family support, advocacy services. Free assessment and care planning. Available through Area Agency on Aging.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "senior_services",
                    "subcategory": "care_management",
                    "services": ["healthcare_navigation", "benefits_assistance", "housing_assistance", "care_coordination", "family_support"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Adult Day Care Services",
                "text": "Adult Day Care: Supervised care for seniors during the day. Activities, meals, health monitoring, socialization. Respite for family caregivers. Some programs specialize in dementia care. Insurance and private pay options available.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "senior_services",
                    "subcategory": "adult_day_care",
                    "services": ["supervised_care", "activities", "health_monitoring", "socialization", "respite_care", "dementia_care"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(senior_services)
        logger.info(f"Added {len(senior_services)} senior services entries")
    
    def add_religious_organizations(self):
        """Add religious organizations and faith-based services"""
        religious_organizations = [
            # Christian Churches
            {
                "title": "Catholic Charities",
                "text": "Catholic Charities: 437 N Topeka St, Wichita, KS 67202. Phone: (316) 264-8344. Emergency assistance, food pantry, counseling, immigration services, refugee resettlement. Services available regardless of religious affiliation.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "religious_organizations",
                    "subcategory": "christian_services",
                    "services": ["emergency_assistance", "food_pantry", "counseling", "immigration_services", "refugee_resettlement"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Salvation Army",
                "text": "Salvation Army: Multiple locations in Wichita. Emergency shelter, food assistance, utility assistance, disaster relief, addiction recovery programs. Services available to all regardless of religious affiliation.",
                "category": "community_services",
                "metadata": {
                    "priority": "high",
                    "source": "community_services",
                    "service_category": "religious_organizations",
                    "subcategory": "christian_services",
                    "services": ["emergency_shelter", "food_assistance", "utility_assistance", "disaster_relief", "addiction_recovery"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "United Methodist Church - Open Door",
                "text": "Open Door: 3033 E 2nd St, Wichita, KS 67214. Phone: (316) 683-4020. Food pantry, clothing closet, emergency assistance, community meals. Open to all community members regardless of religious affiliation.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "religious_organizations",
                    "subcategory": "christian_services",
                    "services": ["food_pantry", "clothing_closet", "emergency_assistance", "community_meals"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Interfaith Services
            {
                "title": "Interfaith Ministries",
                "text": "Interfaith Ministries: 829 N Market St, Wichita, KS 67214. Phone: (316) 264-9303. Emergency assistance, food pantry, community meals, volunteer opportunities. Serves people of all faiths and backgrounds.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "religious_organizations",
                    "subcategory": "interfaith_services",
                    "services": ["emergency_assistance", "food_pantry", "community_meals", "volunteer_opportunities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Jewish Services
            {
                "title": "Jewish Community Services",
                "text": "Jewish Community Services: 400 N Woodlawn St, Wichita, KS 67208. Phone: (316) 686-4741. Food assistance, emergency aid, senior services, cultural programs. Services available to all community members.",
                "category": "community_services",
                "metadata": {
                    "priority": "low",
                    "source": "community_services",
                    "service_category": "religious_organizations",
                    "subcategory": "jewish_services",
                    "services": ["food_assistance", "emergency_aid", "senior_services", "cultural_programs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(religious_organizations)
        logger.info(f"Added {len(religious_organizations)} religious organizations entries")
    
    def add_volunteer_opportunities(self):
        """Add volunteer opportunities and civic engagement"""
        volunteer_opportunities = [
            # Volunteer Organizations
            {
                "title": "United Way Volunteer Center",
                "text": "United Way Volunteer Center: 245 N Waco Ave, Wichita, KS 67202. Phone: (316) 267-1321. Connects volunteers with opportunities in education, health, financial stability. Volunteer matching, group volunteer projects, skills-based volunteering.",
                "category": "community_services",
                "metadata": {
                    "priority": "medium",
                    "source": "community_services",
                    "service_category": "volunteer_opportunities",
                    "subcategory": "volunteer_organizations",
                    "services": ["volunteer_matching", "group_projects", "skills_based_volunteering", "education", "health", "financial_stability"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Volunteer Match Wichita",
                "text": "Volunteer Match: Online platform connecting volunteers with local opportunities. Search by interest, time commitment, location. Opportunities in healthcare, education, environment, animals, arts, community development.",
                "category": "community_services",
                "metadata": {
                    "priority": "low",
                    "source": "community_services",
                    "service_category": "volunteer_opportunities",
                    "subcategory": "volunteer_organizations",
                    "services": ["online_platform", "interest_matching", "time_commitment", "location_search"],
                    "response_type": "service_info"
                }
            },
            
            # Civic Engagement
            {
                "title": "City of Wichita Volunteer Opportunities",
                "text": "City Volunteer Opportunities: Parks and recreation, library programs, special events, community boards, neighborhood associations. Various time commitments and skill levels. Contact City of Wichita Volunteer Coordinator.",
                "category": "community_services",
                "metadata": {
                    "priority": "low",
                    "source": "community_services",
                    "service_category": "volunteer_opportunities",
                    "subcategory": "civic_engagement",
                    "services": ["parks_recreation", "library_programs", "special_events", "community_boards", "neighborhood_associations"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Sedgwick County Volunteer Opportunities",
                "text": "County Volunteer Opportunities: Emergency services, health department, parks, library, senior services, animal shelter. Various opportunities for different interests and availability. Background checks may be required for some positions.",
                "category": "community_services",
                "metadata": {
                    "priority": "low",
                    "source": "community_services",
                    "service_category": "volunteer_opportunities",
                    "subcategory": "civic_engagement",
                    "services": ["emergency_services", "health_department", "parks", "library", "senior_services", "animal_shelter"],
                    "location": "Sedgwick County, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(volunteer_opportunities)
        logger.info(f"Added {len(volunteer_opportunities)} volunteer opportunities entries")
    
    def build_community_services_directory(self):
        """Build the complete community services directory"""
        logger.info("Building comprehensive community services directory...")
        
        # Add community services in priority order
        self.add_social_services()
        self.add_mental_health_services()
        self.add_children_and_youth_services()
        self.add_senior_services()
        self.add_religious_organizations()
        self.add_volunteer_opportunities()
        
        logger.info(f"Built community services directory with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_community_services_directory(self, filename: str = None):
        """Save the community services directory to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"community_services_directory_{timestamp}.json"
        
        filepath = os.path.join("data", "community_services", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved community services directory to {filepath}")
        return filepath
    
    def get_community_stats(self):
        """Get statistics by service category and subcategory"""
        service_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            service_category = entry['metadata'].get('service_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            service_categories[service_category] = service_categories.get(service_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return service_categories, subcategories

def main():
    """Main function to build community services directory"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive community services directory")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build community services directory
    builder = CommunityServicesDirectoryBuilder()
    community_directory = builder.build_community_services_directory()
    
    # Save to file
    filepath = builder.save_community_services_directory(args.output)
    
    # Print statistics
    service_categories, subcategories = builder.get_community_stats()
    
    print(f"\nCommunity Services Directory Statistics:")
    print(f"  Total entries: {len(community_directory)}")
    print(f"  Service categories:")
    for category, count in sorted(service_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample community services entries:")
    for i, entry in enumerate(community_directory[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Service Category: {entry['metadata']['service_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
