#!/usr/bin/env python3
"""
Health & Wellness Database Builder
Creates comprehensive health and wellness information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthWellnessDatabaseBuilder:
    """Builds comprehensive health and wellness database"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_preventive_health(self):
        """Add preventive health information"""
        preventive_health = [
            # Vaccination Information
            {
                "title": "Adult Vaccination Schedule",
                "text": "Adult Vaccines: Flu vaccine annually, Tdap every 10 years, shingles vaccine at 50+, pneumonia vaccine at 65+, COVID-19 vaccines as recommended. Check with healthcare provider for personalized schedule.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "vaccinations",
                    "services": ["flu_vaccine", "tdap", "shingles", "pneumonia", "covid19"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Child Vaccination Schedule",
                "text": "Child Vaccines: Follow CDC recommended schedule for infants, toddlers, and school-age children. DTaP, MMR, varicella, hepatitis, meningitis vaccines. Required for school enrollment. Keep vaccination records updated.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "vaccinations",
                    "services": ["dtap", "mmr", "varicella", "hepatitis", "meningitis"],
                    "response_type": "health_info"
                }
            },
            
            # Health Screenings
            {
                "title": "Adult Health Screenings",
                "text": "Health Screenings: Blood pressure annually, cholesterol every 4-6 years, diabetes screening at 45+, mammograms at 40+, colonoscopy at 50+, bone density at 65+. Ask doctor about personalized screening schedule.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "screenings",
                    "services": ["blood_pressure", "cholesterol", "diabetes", "mammogram", "colonoscopy", "bone_density"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Cancer Screening Guidelines",
                "text": "Cancer Screenings: Breast cancer (mammogram 40+), cervical cancer (Pap test 21+), colorectal cancer (colonoscopy 50+), prostate cancer (PSA test 50+), skin cancer (annual dermatology exam). Early detection saves lives.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "cancer_screening",
                    "services": ["breast_cancer", "cervical_cancer", "colorectal_cancer", "prostate_cancer", "skin_cancer"],
                    "response_type": "health_info"
                }
            },
            
            # Wellness and Lifestyle
            {
                "title": "Healthy Lifestyle Guidelines",
                "text": "Healthy Living: 150 minutes moderate exercise weekly, 7-9 hours sleep nightly, balanced diet with fruits/vegetables, limit alcohol, avoid smoking, manage stress, maintain healthy weight, stay hydrated.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "lifestyle",
                    "services": ["exercise", "sleep", "nutrition", "alcohol", "smoking_cessation", "stress_management"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Mental Health Prevention",
                "text": "Mental Health: Practice stress management, maintain social connections, get regular exercise, adequate sleep, seek help when needed. Mental health is as important as physical health. Early intervention is key.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "preventive",
                    "subcategory": "mental_health",
                    "services": ["stress_management", "social_connections", "exercise", "sleep", "early_intervention"],
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(preventive_health)
        logger.info(f"Added {len(preventive_health)} preventive health entries")
    
    def add_chronic_disease_management(self):
        """Add chronic disease management information"""
        chronic_disease = [
            # Diabetes Management
            {
                "title": "Diabetes Management",
                "text": "Diabetes Care: Monitor blood glucose regularly, take medications as prescribed, follow meal plan, exercise regularly, maintain healthy weight, check feet daily, see doctor every 3-6 months, manage stress.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "diabetes",
                    "services": ["glucose_monitoring", "medications", "meal_planning", "exercise", "foot_care"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Diabetes Emergency Signs",
                "text": "Diabetes Emergency: High blood sugar (confusion, nausea, vomiting, fruity breath), low blood sugar (shaking, sweating, confusion, hunger). Have emergency contacts, medical ID, glucose tablets. Call 911 if severe.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "critical",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "diabetes_emergency",
                    "services": ["high_blood_sugar", "low_blood_sugar", "emergency_contacts", "medical_id"],
                    "response_type": "emergency_info"
                }
            },
            
            # Heart Disease Management
            {
                "title": "Heart Disease Management",
                "text": "Heart Disease Care: Take medications as prescribed, follow heart-healthy diet (low sodium, low fat), exercise as approved by doctor, manage stress, quit smoking, control blood pressure and cholesterol, regular checkups.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "heart_disease",
                    "services": ["medications", "heart_healthy_diet", "exercise", "stress_management", "smoking_cessation"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Heart Disease Warning Signs",
                "text": "Heart Disease Warning: Chest pain/pressure, shortness of breath, fatigue, irregular heartbeat, swelling in legs, dizziness. If symptoms worsen or new symptoms appear, contact doctor immediately or call 911.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "critical",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "heart_disease_warning",
                    "services": ["chest_pain", "shortness_breath", "fatigue", "irregular_heartbeat", "swelling"],
                    "response_type": "emergency_info"
                }
            },
            
            # Hypertension Management
            {
                "title": "High Blood Pressure Management",
                "text": "Blood Pressure Control: Take medications as prescribed, limit sodium intake, maintain healthy weight, exercise regularly, limit alcohol, quit smoking, manage stress, monitor blood pressure at home.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "hypertension",
                    "services": ["medications", "sodium_limitation", "weight_management", "exercise", "stress_management"],
                    "response_type": "health_info"
                }
            },
            
            # COPD Management
            {
                "title": "COPD Management",
                "text": "COPD Care: Take medications as prescribed, use oxygen if prescribed, avoid triggers (smoke, pollution, cold air), exercise as tolerated, eat well, get flu/pneumonia vaccines, pulmonary rehabilitation if available.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "copd",
                    "services": ["medications", "oxygen_therapy", "trigger_avoidance", "exercise", "nutrition", "vaccines"],
                    "response_type": "health_info"
                }
            },
            
            # Arthritis Management
            {
                "title": "Arthritis Management",
                "text": "Arthritis Care: Take medications as prescribed, gentle exercise (swimming, walking), maintain healthy weight, use heat/cold therapy, joint protection techniques, assistive devices if needed, physical therapy.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "chronic_disease",
                    "subcategory": "arthritis",
                    "services": ["medications", "exercise", "weight_management", "heat_cold_therapy", "physical_therapy"],
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(chronic_disease)
        logger.info(f"Added {len(chronic_disease)} chronic disease management entries")
    
    def add_special_populations(self):
        """Add health information for special populations"""
        special_populations = [
            # Pediatric Health
            {
                "title": "Pediatric Health Guidelines",
                "text": "Child Health: Regular well-child visits, immunizations on schedule, developmental milestones, safety (car seats, helmets, childproofing), nutrition, sleep schedules, dental care, mental health awareness.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "pediatric",
                    "services": ["well_child_visits", "immunizations", "developmental_milestones", "safety", "nutrition"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Pediatric Emergency Signs",
                "text": "Child Emergency: High fever (104°F+), difficulty breathing, severe dehydration, unconsciousness, severe allergic reaction, signs of abuse, persistent vomiting, severe pain. When in doubt, call 911 or go to ER.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "critical",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "pediatric_emergency",
                    "services": ["high_fever", "breathing_difficulty", "dehydration", "unconsciousness", "allergic_reaction"],
                    "response_type": "emergency_info"
                }
            },
            
            # Senior Health
            {
                "title": "Senior Health Management",
                "text": "Senior Health: Regular health checkups, medication management, fall prevention, vision/hearing checks, dental care, social connections, mental health, advance directives, safety at home, transportation assistance.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "senior",
                    "services": ["health_checkups", "medication_management", "fall_prevention", "vision_hearing", "advance_directives"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Senior Fall Prevention",
                "text": "Fall Prevention: Remove tripping hazards, adequate lighting, handrails on stairs, non-slip surfaces, regular exercise, vision/hearing checks, medication review, assistive devices, emergency response system.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "fall_prevention",
                    "services": ["hazard_removal", "lighting", "handrails", "exercise", "vision_hearing", "assistive_devices"],
                    "response_type": "health_info"
                }
            },
            
            # Women's Health
            {
                "title": "Women's Health Guidelines",
                "text": "Women's Health: Annual well-woman exams, mammograms 40+, Pap tests, bone density screening, heart health, mental health, contraception, pregnancy planning, menopause management, breast self-exams.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "womens_health",
                    "services": ["well_woman_exams", "mammograms", "pap_tests", "bone_density", "contraception", "menopause"],
                    "response_type": "health_info"
                }
            },
            
            # Men's Health
            {
                "title": "Men's Health Guidelines",
                "text": "Men's Health: Annual physical exams, prostate screening 50+, heart health, mental health awareness, testicular self-exams, colon cancer screening, blood pressure/cholesterol monitoring, healthy lifestyle choices.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "mens_health",
                    "services": ["physical_exams", "prostate_screening", "heart_health", "mental_health", "testicular_exams"],
                    "response_type": "health_info"
                }
            },
            
            # Mental Health
            {
                "title": "Mental Health Resources",
                "text": "Mental Health: Recognize signs of depression/anxiety, seek professional help when needed, maintain social connections, practice self-care, stress management techniques, crisis hotlines available 24/7.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "special_populations",
                    "subcategory": "mental_health",
                    "services": ["depression_anxiety", "professional_help", "social_connections", "self_care", "crisis_hotlines"],
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(special_populations)
        logger.info(f"Added {len(special_populations)} special population entries")
    
    def add_health_education(self):
        """Add health education and literacy information"""
        health_education = [
            # Health Literacy
            {
                "title": "Health Literacy Basics",
                "text": "Health Literacy: Ask questions during medical visits, bring medication list, understand prescriptions, keep health records, know emergency numbers, understand insurance coverage, seek second opinions when needed.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "health_literacy",
                    "services": ["medical_visits", "medication_list", "prescriptions", "health_records", "insurance"],
                    "response_type": "health_info"
                }
            },
            {
                "title": "Medication Safety",
                "text": "Medication Safety: Take medications as prescribed, don't share medications, keep current medication list, understand side effects, store medications safely, dispose of expired medications properly, use one pharmacy.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "medication_safety",
                    "services": ["prescription_adherence", "medication_list", "side_effects", "safe_storage", "proper_disposal"],
                    "response_type": "health_info"
                }
            },
            
            # First Aid Education
            {
                "title": "Basic First Aid Knowledge",
                "text": "First Aid Basics: Learn CPR, how to stop bleeding, treat burns, manage choking, recognize stroke/heart attack signs, use first aid supplies, when to call 911. Take first aid class for certification.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "high",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "first_aid",
                    "services": ["cpr", "bleeding_control", "burn_treatment", "choking_management", "emergency_recognition"],
                    "response_type": "health_info"
                }
            },
            
            # Nutrition Education
            {
                "title": "Healthy Nutrition Guidelines",
                "text": "Healthy Eating: Balance of fruits, vegetables, whole grains, lean proteins, healthy fats. Limit processed foods, added sugars, sodium. Portion control, regular meal times, stay hydrated with water.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "nutrition",
                    "services": ["balanced_diet", "whole_grains", "lean_proteins", "portion_control", "hydration"],
                    "response_type": "health_info"
                }
            },
            
            # Exercise Education
            {
                "title": "Physical Activity Guidelines",
                "text": "Exercise Guidelines: 150 minutes moderate exercise weekly, 75 minutes vigorous exercise weekly, muscle strengthening 2+ days weekly. Start slowly, choose activities you enjoy, consult doctor before starting new program.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "exercise",
                    "services": ["moderate_exercise", "vigorous_exercise", "muscle_strengthening", "gradual_progression", "doctor_consultation"],
                    "response_type": "health_info"
                }
            },
            
            # Health Insurance
            {
                "title": "Health Insurance Navigation",
                "text": "Health Insurance: Understand your coverage, in-network providers, copays/deductibles, pre-authorization requirements, prescription coverage, emergency coverage, marketplace options, Medicaid/Medicare if eligible.",
                "category": "health_wellness",
                "metadata": {
                    "priority": "medium",
                    "source": "health_wellness",
                    "health_category": "education",
                    "subcategory": "health_insurance",
                    "services": ["coverage_understanding", "network_providers", "copays_deductibles", "prescription_coverage", "marketplace_options"],
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(health_education)
        logger.info(f"Added {len(health_education)} health education entries")
    
    def build_health_wellness_database(self):
        """Build the complete health and wellness database"""
        logger.info("Building comprehensive health and wellness database...")
        
        # Add health information in priority order
        self.add_preventive_health()
        self.add_chronic_disease_management()
        self.add_special_populations()
        self.add_health_education()
        
        logger.info(f"Built health and wellness database with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_health_wellness_database(self, filename: str = None):
        """Save the health and wellness database to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_wellness_database_{timestamp}.json"
        
        filepath = os.path.join("data", "health_wellness", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved health and wellness database to {filepath}")
        return filepath
    
    def get_health_stats(self):
        """Get statistics by health category and subcategory"""
        health_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            health_category = entry['metadata'].get('health_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            health_categories[health_category] = health_categories.get(health_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return health_categories, subcategories

def main():
    """Main function to build health and wellness database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive health and wellness database")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build health and wellness database
    builder = HealthWellnessDatabaseBuilder()
    health_database = builder.build_health_wellness_database()
    
    # Save to file
    filepath = builder.save_health_wellness_database(args.output)
    
    # Print statistics
    health_categories, subcategories = builder.get_health_stats()
    
    print(f"\nHealth & Wellness Database Statistics:")
    print(f"  Total entries: {len(health_database)}")
    print(f"  Health categories:")
    for category, count in sorted(health_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample health and wellness entries:")
    for i, entry in enumerate(health_database[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Health Category: {entry['metadata']['health_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
