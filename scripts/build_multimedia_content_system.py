#!/usr/bin/env python3
"""
Multimedia Content System Builder
Creates comprehensive multimedia content information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultimediaContentSystemBuilder:
    """Builds comprehensive multimedia content system"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_emergency_video_content(self):
        """Add emergency procedure video content"""
        emergency_video_content = [
            # CPR and First Aid Videos
            {
                "title": "CPR Training Video",
                "text": "CPR Training Video: Step-by-step video demonstration of adult, child, and infant CPR. Shows proper hand placement, compression rate (100-120 per minute), rescue breaths, and use of AED. Available in English and Spanish. Duration: 15 minutes. Watch before emergency situations.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "cpr_first_aid",
                    "services": ["adult_cpr", "child_cpr", "infant_cpr", "hand_placement", "compression_rate", "rescue_breaths", "aed_use"],
                    "languages": ["english", "spanish"],
                    "duration": "15_minutes",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "First Aid for Choking Video",
                "text": "Choking First Aid Video: Demonstrates abdominal thrusts (Heimlich maneuver) for adults, back blows and chest thrusts for children, and infant choking response. Shows when to call 911, positioning techniques, and follow-up care. Available in multiple languages.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "cpr_first_aid",
                    "services": ["heimlich_maneuver", "back_blows", "chest_thrusts", "infant_choking", "positioning", "follow_up_care"],
                    "languages": ["multiple"],
                    "duration": "12_minutes",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Bleeding Control Video",
                "text": "Bleeding Control Video: Shows direct pressure technique, elevation, pressure points, and when to use tourniquets. Demonstrates proper bandaging, wound care, and recognizing when bleeding is life-threatening. Includes stop-the-bleed techniques.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "cpr_first_aid",
                    "services": ["direct_pressure", "elevation", "pressure_points", "tourniquets", "bandaging", "wound_care", "stop_the_bleed"],
                    "languages": ["english"],
                    "duration": "10_minutes",
                    "response_type": "emergency_info"
                }
            },
            
            # Natural Disaster Videos
            {
                "title": "Tornado Safety Video",
                "text": "Tornado Safety Video: Demonstrates proper tornado shelter locations, protective positions, and safety measures for different situations (home, vehicle, mobile home). Shows how to identify safe rooms, avoid windows, and protect against flying debris.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "natural_disasters",
                    "services": ["shelter_locations", "protective_positions", "safe_rooms", "window_avoidance", "debris_protection"],
                    "languages": ["english", "spanish"],
                    "duration": "8_minutes",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Flood Safety Video",
                "text": "Flood Safety Video: Shows flood evacuation procedures, driving safety in flood conditions, and post-flood safety measures. Demonstrates how to avoid flood waters, recognize flash flood warnings, and protect property from flood damage.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "natural_disasters",
                    "services": ["evacuation_procedures", "driving_safety", "post_flood_safety", "flood_water_avoidance", "flash_flood_warnings"],
                    "languages": ["english"],
                    "duration": "10_minutes",
                    "response_type": "emergency_info"
                }
            },
            
            # Fire Safety Videos
            {
                "title": "Fire Safety and Evacuation Video",
                "text": "Fire Safety Video: Demonstrates fire prevention, smoke detector maintenance, fire escape planning, and evacuation procedures. Shows stop-drop-roll technique, fire extinguisher use, and how to help others evacuate safely.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "high",
                    "source": "multimedia_content",
                    "content_category": "emergency_videos",
                    "subcategory": "fire_safety",
                    "services": ["fire_prevention", "smoke_detectors", "escape_planning", "evacuation_procedures", "stop_drop_roll", "fire_extinguisher"],
                    "languages": ["english"],
                    "duration": "12_minutes",
                    "response_type": "emergency_info"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_video_content)
        logger.info(f"Added {len(emergency_video_content)} emergency video content entries")
    
    def add_health_education_videos(self):
        """Add health education video content"""
        health_education_videos = [
            # Preventive Health Videos
            {
                "title": "Healthy Living Video Series",
                "text": "Healthy Living Videos: Series covering nutrition basics, exercise routines, stress management, and sleep hygiene. Demonstrates proper exercise techniques, healthy meal preparation, and relaxation methods. Available in multiple languages.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "health_videos",
                    "subcategory": "preventive_health",
                    "services": ["nutrition_basics", "exercise_routines", "stress_management", "sleep_hygiene", "meal_preparation", "relaxation_methods"],
                    "languages": ["multiple"],
                    "duration": "20_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Diabetes Management Video",
                "text": "Diabetes Management Video: Shows blood glucose monitoring, insulin injection techniques, meal planning, exercise guidelines, and foot care. Demonstrates proper use of glucose meters, insulin pens, and recognition of warning signs.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "high",
                    "source": "multimedia_content",
                    "content_category": "health_videos",
                    "subcategory": "chronic_disease_management",
                    "services": ["glucose_monitoring", "insulin_injection", "meal_planning", "exercise_guidelines", "foot_care", "warning_signs"],
                    "languages": ["english", "spanish"],
                    "duration": "25_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Medication Safety Video",
                "text": "Medication Safety Video: Demonstrates proper medication storage, timing, dosage, and interaction awareness. Shows how to read prescription labels, use pill organizers, and recognize side effects. Includes medication disposal guidelines.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "high",
                    "source": "multimedia_content",
                    "content_category": "health_videos",
                    "subcategory": "medication_safety",
                    "services": ["medication_storage", "timing", "dosage", "interactions", "prescription_labels", "pill_organizers", "side_effects"],
                    "languages": ["english"],
                    "duration": "15_minutes",
                    "response_type": "health_info"
                }
            },
            
            # Mental Health Videos
            {
                "title": "Mental Health Awareness Video",
                "text": "Mental Health Video: Covers recognizing signs of depression and anxiety, stress management techniques, when to seek help, and available resources. Demonstrates relaxation exercises, breathing techniques, and healthy coping strategies.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "high",
                    "source": "multimedia_content",
                    "content_category": "health_videos",
                    "subcategory": "mental_health",
                    "services": ["depression_anxiety_signs", "stress_management", "help_seeking", "relaxation_exercises", "breathing_techniques", "coping_strategies"],
                    "languages": ["english", "spanish"],
                    "duration": "18_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Senior Health and Safety Video",
                "text": "Senior Health Video: Covers fall prevention, medication management, nutrition for seniors, and maintaining independence. Demonstrates home safety modifications, exercise routines for seniors, and recognizing health changes.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "health_videos",
                    "subcategory": "senior_health",
                    "services": ["fall_prevention", "medication_management", "senior_nutrition", "independence", "home_safety", "senior_exercise"],
                    "languages": ["english"],
                    "duration": "22_minutes",
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(health_education_videos)
        logger.info(f"Added {len(health_education_videos)} health education video entries")
    
    def add_community_announcements(self):
        """Add community announcements and public service content"""
        community_announcements = [
            # Emergency Alerts
            {
                "title": "Emergency Alert System Audio",
                "text": "Emergency Alert Audio: Standard emergency alert tones and messages for tornado warnings, severe weather, and other emergencies. Includes evacuation instructions, shelter locations, and emergency contact information. Available in multiple languages.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "critical",
                    "source": "multimedia_content",
                    "content_category": "community_announcements",
                    "subcategory": "emergency_alerts",
                    "services": ["tornado_warnings", "severe_weather", "evacuation_instructions", "shelter_locations", "emergency_contacts"],
                    "languages": ["multiple"],
                    "duration": "varies",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Public Health Announcements",
                "text": "Health Announcements: Audio announcements about vaccination clinics, health screenings, disease prevention, and public health updates. Includes information about flu shots, COVID-19 updates, and community health programs.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "community_announcements",
                    "subcategory": "public_health",
                    "services": ["vaccination_clinics", "health_screenings", "disease_prevention", "health_updates", "flu_shots", "community_programs"],
                    "languages": ["english", "spanish"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            },
            
            # Community Events
            {
                "title": "Community Event Announcements",
                "text": "Event Announcements: Audio announcements about community events, festivals, meetings, and activities. Includes information about dates, times, locations, and registration requirements for community programs.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "community_announcements",
                    "subcategory": "community_events",
                    "services": ["community_events", "festivals", "meetings", "activities", "registration", "programs"],
                    "languages": ["english"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            },
            {
                "title": "City Services Announcements",
                "text": "City Services Audio: Announcements about city services, utility updates, road closures, construction projects, and public meetings. Includes information about trash pickup schedules, water service, and city council meetings.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "community_announcements",
                    "subcategory": "city_services",
                    "services": ["city_services", "utility_updates", "road_closures", "construction", "public_meetings", "trash_pickup"],
                    "languages": ["english"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_announcements)
        logger.info(f"Added {len(community_announcements)} community announcements entries")
    
    def add_multilingual_resources(self):
        """Add multilingual content and resources"""
        multilingual_resources = [
            # Spanish Language Content
            {
                "title": "Spanish Emergency Procedures Audio",
                "text": "Spanish Emergency Audio: Emergency procedures and instructions in Spanish including CPR, first aid, tornado safety, and fire safety. Essential for Spanish-speaking community members during emergencies.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "high",
                    "source": "multimedia_content",
                    "content_category": "multilingual_resources",
                    "subcategory": "spanish_content",
                    "services": ["spanish_cpr", "spanish_first_aid", "spanish_tornado_safety", "spanish_fire_safety", "emergency_instructions"],
                    "languages": ["spanish"],
                    "duration": "varies",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Spanish Health Information Audio",
                "text": "Spanish Health Audio: Health information and instructions in Spanish including medication safety, diabetes management, mental health resources, and preventive care. Important for Spanish-speaking community members.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "multilingual_resources",
                    "subcategory": "spanish_content",
                    "services": ["spanish_medication_safety", "spanish_diabetes_management", "spanish_mental_health", "spanish_preventive_care"],
                    "languages": ["spanish"],
                    "duration": "varies",
                    "response_type": "health_info"
                }
            },
            
            # Other Languages
            {
                "title": "Vietnamese Community Resources",
                "text": "Vietnamese Resources: Emergency procedures, health information, and community services in Vietnamese. Essential for Vietnamese-speaking community members in Wichita area.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "multilingual_resources",
                    "subcategory": "vietnamese_content",
                    "services": ["vietnamese_emergency", "vietnamese_health", "vietnamese_community_services"],
                    "languages": ["vietnamese"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            },
            {
                "title": "American Sign Language Resources",
                "text": "ASL Resources: Emergency procedures, health information, and community services in American Sign Language. Essential for deaf and hard-of-hearing community members.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "multilingual_resources",
                    "subcategory": "asl_content",
                    "services": ["asl_emergency", "asl_health", "asl_community_services", "deaf_community"],
                    "languages": ["asl"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(multilingual_resources)
        logger.info(f"Added {len(multilingual_resources)} multilingual resources entries")
    
    def add_educational_media(self):
        """Add educational media content"""
        educational_media = [
            # Computer Literacy Videos
            {
                "title": "Basic Computer Skills Video Series",
                "text": "Computer Skills Videos: Step-by-step video tutorials covering computer basics, internet navigation, email setup, Microsoft Office, and online safety. Designed for beginners with no prior computer experience.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "educational_media",
                    "subcategory": "computer_literacy",
                    "services": ["computer_basics", "internet_navigation", "email_setup", "microsoft_office", "online_safety"],
                    "languages": ["english"],
                    "duration": "30_minutes",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Smartphone and Tablet Tutorial Videos",
                "text": "Mobile Device Videos: Tutorial videos covering smartphone and tablet basics, app usage, internet access, photo management, and security settings. Helpful for seniors and new users.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "educational_media",
                    "subcategory": "mobile_device_training",
                    "services": ["smartphone_basics", "tablet_basics", "app_usage", "internet_access", "photo_management", "security_settings"],
                    "languages": ["english"],
                    "duration": "25_minutes",
                    "response_type": "service_info"
                }
            },
            
            # Financial Literacy
            {
                "title": "Financial Literacy Video Series",
                "text": "Financial Literacy Videos: Educational videos covering budgeting, banking, credit management, saving strategies, and financial planning. Designed to help community members improve their financial knowledge and skills.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "educational_media",
                    "subcategory": "financial_literacy",
                    "services": ["budgeting", "banking", "credit_management", "saving_strategies", "financial_planning"],
                    "languages": ["english", "spanish"],
                    "duration": "35_minutes",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Job Search and Resume Building Videos",
                "text": "Job Search Videos: Tutorial videos covering online job searching, resume building, cover letter writing, interview preparation, and professional networking. Helpful for job seekers in the community.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "medium",
                    "source": "multimedia_content",
                    "content_category": "educational_media",
                    "subcategory": "job_search_training",
                    "services": ["online_job_searching", "resume_building", "cover_letters", "interview_preparation", "professional_networking"],
                    "languages": ["english"],
                    "duration": "40_minutes",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(educational_media)
        logger.info(f"Added {len(educational_media)} educational media entries")
    
    def add_community_cultural_content(self):
        """Add community cultural and historical content"""
        community_cultural_content = [
            # Local History
            {
                "title": "Wichita History Audio Tours",
                "text": "Wichita History Audio: Audio tours covering Wichita's history, from its founding as a trading post to its development as an aviation center. Includes information about historic buildings, notable residents, and cultural landmarks.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "community_cultural",
                    "subcategory": "local_history",
                    "services": ["wichita_history", "trading_post", "aviation_center", "historic_buildings", "notable_residents", "cultural_landmarks"],
                    "languages": ["english"],
                    "duration": "45_minutes",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Community Stories and Oral Histories",
                "text": "Community Stories Audio: Recorded oral histories from long-time Wichita residents, community leaders, and cultural figures. Preserves community memory and shares diverse perspectives on local history and culture.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "community_cultural",
                    "subcategory": "oral_histories",
                    "services": ["oral_histories", "community_memory", "diverse_perspectives", "local_culture", "community_leaders"],
                    "languages": ["english", "spanish"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            },
            
            # Cultural Events
            {
                "title": "Cultural Festival Recordings",
                "text": "Festival Recordings: Audio and video recordings of cultural festivals, performances, and community celebrations. Includes music, dance, storytelling, and cultural demonstrations from various community groups.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "community_cultural",
                    "subcategory": "cultural_events",
                    "services": ["cultural_festivals", "performances", "celebrations", "music", "dance", "storytelling", "cultural_demonstrations"],
                    "languages": ["multiple"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Local Music and Art Showcase",
                "text": "Local Arts Media: Showcase of local musicians, artists, and performers from Wichita area. Includes interviews, performances, and behind-the-scenes content featuring community talent.",
                "category": "multimedia_content",
                "metadata": {
                    "priority": "low",
                    "source": "multimedia_content",
                    "content_category": "community_cultural",
                    "subcategory": "local_arts",
                    "services": ["local_musicians", "local_artists", "performers", "interviews", "performances", "community_talent"],
                    "languages": ["english"],
                    "duration": "varies",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_cultural_content)
        logger.info(f"Added {len(community_cultural_content)} community cultural content entries")
    
    def build_multimedia_content_system(self):
        """Build the complete multimedia content system"""
        logger.info("Building comprehensive multimedia content system...")
        
        # Add multimedia content in priority order
        self.add_emergency_video_content()
        self.add_health_education_videos()
        self.add_community_announcements()
        self.add_multilingual_resources()
        self.add_educational_media()
        self.add_community_cultural_content()
        
        logger.info(f"Built multimedia content system with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_multimedia_content_system(self, filename: str = None):
        """Save the multimedia content system to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multimedia_content_system_{timestamp}.json"
        
        filepath = os.path.join("data", "multimedia_content", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved multimedia content system to {filepath}")
        return filepath
    
    def get_multimedia_stats(self):
        """Get statistics by content category and subcategory"""
        content_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            content_category = entry['metadata'].get('content_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            content_categories[content_category] = content_categories.get(content_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return content_categories, subcategories

def main():
    """Main function to build multimedia content system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive multimedia content system")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build multimedia content system
    builder = MultimediaContentSystemBuilder()
    multimedia_system = builder.build_multimedia_content_system()
    
    # Save to file
    filepath = builder.save_multimedia_content_system(args.output)
    
    # Print statistics
    content_categories, subcategories = builder.get_multimedia_stats()
    
    print(f"\nMultimedia Content System Statistics:")
    print(f"  Total entries: {len(multimedia_system)}")
    print(f"  Content categories:")
    for category, count in sorted(content_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample multimedia content entries:")
    for i, entry in enumerate(multimedia_system[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Content Category: {entry['metadata']['content_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
