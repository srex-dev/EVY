#!/usr/bin/env python3
"""
Educational Resources Hub Builder
Creates comprehensive educational resources database for Wichita
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EducationalResourcesHubBuilder:
    """Builds comprehensive educational resources hub"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_k12_education(self):
        """Add K-12 education information"""
        k12_education = [
            # Wichita Public Schools (USD 259)
            {
                "title": "Wichita Public Schools - USD 259",
                "text": "Wichita Public Schools: USD 259 serves Wichita area with 50+ schools. Elementary (K-5), Middle (6-8), High (9-12), and specialty schools. Special education, gifted programs, ESL services. Contact: (316) 973-4500.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "k12",
                    "district": "USD 259",
                    "school_type": "public",
                    "services": ["special_education", "gifted_programs", "esl"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita High Schools",
                "text": "Wichita High Schools: East High, West High, North High, South High, Southeast High, Northwest High, Heights High. Advanced placement, career academies, athletics, fine arts. Graduation requirements and college prep programs available.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "high_school",
                    "district": "USD 259",
                    "school_type": "public",
                    "services": ["ap_courses", "career_academies", "athletics", "fine_arts"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Middle Schools",
                "text": "Wichita Middle Schools: Multiple locations serving grades 6-8. Core subjects, electives, athletics, band, choir. Transition programs to high school. Special education services available. Contact individual schools for enrollment.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "middle_school",
                    "district": "USD 259",
                    "school_type": "public",
                    "services": ["core_subjects", "electives", "athletics", "special_education"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Elementary Schools",
                "text": "Wichita Elementary Schools: Multiple locations serving grades K-5. Reading, math, science, social studies, art, music, PE. Early childhood programs, special education, gifted programs. Before/after school care available.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "elementary",
                    "district": "USD 259",
                    "school_type": "public",
                    "services": ["early_childhood", "special_education", "gifted_programs", "childcare"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Private Schools
            {
                "title": "Catholic Schools - Diocese of Wichita",
                "text": "Catholic Schools: Multiple elementary and high schools in Wichita. Faith-based education, academic excellence, small class sizes. Kapaun Mt. Carmel High School, Bishop Carroll Catholic High School. Contact: (316) 269-3900.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "private",
                    "religious_affiliation": "catholic",
                    "services": ["faith_based", "academic_excellence", "small_classes"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Collegiate School",
                "text": "Wichita Collegiate: 9115 E 13th St N, Wichita, KS 67206. Phone: (316) 634-0433. Independent college-preparatory school, PreK-12. Small class sizes, advanced curriculum, athletics, fine arts. Financial aid available.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "private",
                    "services": ["college_prep", "small_classes", "advanced_curriculum", "financial_aid"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "The Independent School",
                "text": "The Independent School: 8317 E Douglas Ave, Wichita, KS 67207. Phone: (316) 686-0152. Independent college-preparatory school, K-12. Rigorous academics, character development, community service. Scholarships available.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "private",
                    "services": ["college_prep", "character_development", "community_service", "scholarships"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Charter Schools
            {
                "title": "Wichita Charter Schools",
                "text": "Charter Schools in Wichita: Alternative public schools with specialized curricula. STEM focus, arts integration, project-based learning. Open enrollment, no tuition. Contact individual schools for application processes and programs.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "school_type": "charter",
                    "services": ["stem_focus", "arts_integration", "project_based_learning", "open_enrollment"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Special Education
            {
                "title": "Special Education Services - USD 259",
                "text": "Special Education USD 259: Comprehensive services for students with disabilities. Individualized Education Programs (IEPs), resource rooms, inclusion services, transition planning. Contact: (316) 973-4500 for evaluation and services.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "k12",
                    "service_type": "special_education",
                    "services": ["ieps", "resource_rooms", "inclusion", "transition_planning"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Gifted Programs
            {
                "title": "Gifted Education Programs",
                "text": "Gifted Education: Advanced academic programs for gifted and talented students. Enrichment activities, accelerated coursework, competitions. Identification and testing available. Contact individual schools or district office for program information.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "k12",
                    "service_type": "gifted_education",
                    "services": ["enrichment", "accelerated_coursework", "competitions", "identification"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(k12_education)
        logger.info(f"Added {len(k12_education)} K-12 education entries")
    
    def add_higher_education(self):
        """Add higher education information"""
        higher_education = [
            # Universities
            {
                "title": "Wichita State University",
                "text": "Wichita State University: 1845 Fairmount St, Wichita, KS 67260. Phone: (316) 978-3456. Public research university offering undergraduate and graduate programs. Strong in engineering, business, health sciences, liberal arts. Admissions: (316) 978-3085.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "higher",
                    "institution_type": "university",
                    "services": ["undergraduate", "graduate", "engineering", "business", "health_sciences"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "WSU Applied Learning",
                "text": "WSU Applied Learning: Internships, co-ops, service learning, undergraduate research. Career services, job placement assistance. Strong connections with local industry. Contact Career Services: (316) 978-3688.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "higher",
                    "institution_type": "university",
                    "service_type": "applied_learning",
                    "services": ["internships", "coops", "service_learning", "research", "career_services"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Community Colleges
            {
                "title": "Wichita Area Technical College",
                "text": "Wichita Area Technical College: 4004 N Webb Rd, Wichita, KS 67226. Phone: (316) 677-9400. Technical and vocational programs, certifications, workforce training. Programs in healthcare, manufacturing, technology, skilled trades.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "technical",
                    "institution_type": "community_college",
                    "services": ["technical_programs", "certifications", "workforce_training", "healthcare", "manufacturing"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Butler Community College",
                "text": "Butler Community College: Multiple campuses including Wichita area. Associate degrees, technical programs, transfer programs. Affordable tuition, flexible scheduling. Contact: (316) 322-3166.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "higher",
                    "institution_type": "community_college",
                    "services": ["associate_degrees", "technical_programs", "transfer_programs", "flexible_scheduling"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Professional Schools
            {
                "title": "University of Kansas School of Medicine - Wichita",
                "text": "KU School of Medicine - Wichita: 1010 N Kansas St, Wichita, KS 67214. Phone: (316) 293-2600. Medical education, residency programs, continuing medical education. Community-based medical education.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "professional",
                    "institution_type": "medical_school",
                    "services": ["medical_education", "residency_programs", "continuing_education"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Friends University",
                "text": "Friends University: 2100 W University St, Wichita, KS 67213. Phone: (316) 295-5000. Private university offering undergraduate and graduate programs. Business, education, arts and sciences, professional studies.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "higher",
                    "institution_type": "private_university",
                    "services": ["undergraduate", "graduate", "business", "education", "professional_studies"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(higher_education)
        logger.info(f"Added {len(higher_education)} higher education entries")
    
    def add_adult_education(self):
        """Add adult education and workforce development"""
        adult_education = [
            # Adult Basic Education
            {
                "title": "Adult Education - USD 259",
                "text": "Adult Education USD 259: GED preparation, English as Second Language (ESL), basic skills, workforce training. Free classes, flexible scheduling, childcare available. Contact: (316) 973-4500.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "adult",
                    "service_type": "basic_skills",
                    "services": ["ged_preparation", "esl", "basic_skills", "workforce_training", "childcare"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Kansas Adult Education",
                "text": "Kansas Adult Education: Multiple providers in Wichita area. GED preparation, high school equivalency, English language learning, workforce readiness. Free or low-cost programs available.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "adult",
                    "service_type": "basic_skills",
                    "services": ["ged_preparation", "high_school_equivalency", "english_learning", "workforce_readiness"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Workforce Development
            {
                "title": "Workforce Development - WSU Tech",
                "text": "Workforce Development WSU Tech: Customized training for businesses, short-term certificate programs, apprenticeship programs. Healthcare, manufacturing, technology, construction trades. Contact: (316) 677-9400.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "education_level": "workforce",
                    "service_type": "workforce_development",
                    "services": ["customized_training", "certificate_programs", "apprenticeships", "healthcare", "manufacturing"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Goodwill Industries Workforce Development",
                "text": "Goodwill Workforce Development: Job training, career services, resume assistance, interview preparation. Programs for individuals with barriers to employment. Contact: (316) 267-6201.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "workforce",
                    "service_type": "workforce_development",
                    "services": ["job_training", "career_services", "resume_assistance", "interview_prep"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Professional Development
            {
                "title": "WSU Professional Development",
                "text": "WSU Professional Development: Continuing education, professional certificates, executive education, online courses. Business, healthcare, education, technology programs. Contact: (316) 978-3688.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "education_level": "professional",
                    "service_type": "professional_development",
                    "services": ["continuing_education", "certificates", "executive_education", "online_courses"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Community Education Programs",
                "text": "Community Education: Various providers offer classes for personal enrichment, hobbies, life skills. Art classes, cooking, fitness, technology, language learning. Check with libraries, community centers, and colleges.",
                "category": "education",
                "metadata": {
                    "priority": "low",
                    "source": "education_resources",
                    "education_level": "community",
                    "service_type": "personal_enrichment",
                    "services": ["art_classes", "cooking", "fitness", "technology", "language_learning"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(adult_education)
        logger.info(f"Added {len(adult_education)} adult education entries")
    
    def add_library_services(self):
        """Add library services and resources"""
        library_services = [
            # Wichita Public Library System
            {
                "title": "Wichita Public Library - Central Library",
                "text": "Central Library: 223 S Main St, Wichita, KS 67202. Phone: (316) 261-8500. Hours: Mon-Thu 9AM-9PM, Fri-Sat 9AM-6PM, Sun 1-5PM. Books, e-books, digital resources, computers, meeting rooms.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "institution_type": "library",
                    "services": ["books", "ebooks", "digital_resources", "computers", "meeting_rooms"],
                    "location": "Downtown Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Public Library - Branch Locations",
                "text": "Library Branches: Multiple locations throughout Wichita. Books, movies, music, e-resources, computers, Wi-Fi, children's programs, adult programs. Free library cards available to Wichita residents.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "institution_type": "library",
                    "services": ["books", "movies", "music", "eresources", "computers", "wifi", "programs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Library Digital Resources",
                "text": "Library Digital Resources: E-books, audiobooks, digital magazines, online databases, research tools, language learning programs. Access from home with library card. OverDrive, Hoopla, and other platforms available.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "institution_type": "library",
                    "service_type": "digital_resources",
                    "services": ["ebooks", "audiobooks", "magazines", "databases", "language_learning"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Library Programs and Events",
                "text": "Library Programs: Children's storytimes, teen programs, adult education, computer classes, book clubs, cultural events. Free programs for all ages. Check library website or call for current schedule.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "institution_type": "library",
                    "service_type": "programs",
                    "services": ["storytimes", "teen_programs", "adult_education", "computer_classes", "book_clubs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # University Libraries
            {
                "title": "WSU Ablah Library",
                "text": "WSU Ablah Library: 1845 Fairmount St, Wichita, KS 67260. Academic library with research resources, study spaces, computer labs, group study rooms. Open to students, faculty, and community members.",
                "category": "education",
                "metadata": {
                    "priority": "low",
                    "source": "education_resources",
                    "institution_type": "university_library",
                    "services": ["research_resources", "study_spaces", "computer_labs", "group_study"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(library_services)
        logger.info(f"Added {len(library_services)} library services entries")
    
    def add_tutoring_and_support(self):
        """Add tutoring and educational support services"""
        tutoring_services = [
            # Tutoring Services
            {
                "title": "Kumon Math and Reading Center",
                "text": "Kumon Centers: Multiple locations in Wichita. Math and reading tutoring for students of all ages. Self-paced learning, individualized instruction. Contact individual centers for enrollment and schedules.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "tutoring",
                    "services": ["math_tutoring", "reading_tutoring", "self_paced", "individualized"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Sylvan Learning Center",
                "text": "Sylvan Learning: Multiple locations in Wichita. Tutoring in math, reading, writing, study skills, test preparation. Personalized learning plans, progress tracking. Contact individual centers for programs and pricing.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "tutoring",
                    "services": ["math_tutoring", "reading_tutoring", "writing_tutoring", "test_prep", "study_skills"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "WSU Tutoring Services",
                "text": "WSU Tutoring: Free tutoring services for WSU students. Math, science, writing, study skills. Peer tutoring, professional tutoring, online tutoring available. Contact: (316) 978-3688.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "tutoring",
                    "services": ["math_tutoring", "science_tutoring", "writing_tutoring", "peer_tutoring", "online_tutoring"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Test Preparation
            {
                "title": "ACT/SAT Test Preparation",
                "text": "ACT/SAT Prep: Various providers in Wichita offer test preparation courses. Kaplan, Princeton Review, local tutors, online courses. Practice tests, study materials, strategies for college entrance exams.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "test_preparation",
                    "services": ["act_prep", "sat_prep", "practice_tests", "study_materials", "strategies"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "GED Test Preparation",
                "text": "GED Prep: Multiple providers in Wichita offer GED preparation classes. Adult education centers, community colleges, nonprofit organizations. Free or low-cost classes, practice tests, testing centers.",
                "category": "education",
                "metadata": {
                    "priority": "high",
                    "source": "education_resources",
                    "service_type": "test_preparation",
                    "services": ["ged_prep", "practice_tests", "testing_centers", "free_classes"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Educational Support
            {
                "title": "Boys & Girls Clubs Educational Programs",
                "text": "Boys & Girls Clubs: Educational programs, homework help, tutoring, STEM activities, college prep. After-school and summer programs. Contact: (316) 263-8833.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "educational_support",
                    "services": ["homework_help", "tutoring", "stem_activities", "college_prep", "afterschool"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "YMCA Educational Programs",
                "text": "YMCA Educational Programs: After-school programs, summer camps, tutoring, leadership development, college prep. Academic support and character development. Contact: (316) 267-7000.",
                "category": "education",
                "metadata": {
                    "priority": "medium",
                    "source": "education_resources",
                    "service_type": "educational_support",
                    "services": ["afterschool", "summer_camps", "tutoring", "leadership", "college_prep"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(tutoring_services)
        logger.info(f"Added {len(tutoring_services)} tutoring and support entries")
    
    def build_educational_resources_hub(self):
        """Build the complete educational resources hub"""
        logger.info("Building comprehensive educational resources hub...")
        
        # Add educational resources in priority order
        self.add_k12_education()
        self.add_higher_education()
        self.add_adult_education()
        self.add_library_services()
        self.add_tutoring_and_support()
        
        logger.info(f"Built educational resources hub with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_educational_hub(self, filename: str = None):
        """Save the educational resources hub to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"educational_resources_hub_{timestamp}.json"
        
        filepath = os.path.join("data", "educational_resources", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved educational resources hub to {filepath}")
        return filepath
    
    def get_education_stats(self):
        """Get statistics by education level and type"""
        education_levels = {}
        service_types = {}
        
        for entry in self.knowledge_base:
            education_level = entry['metadata'].get('education_level', 'unknown')
            service_type = entry['metadata'].get('service_type', 'general')
            
            education_levels[education_level] = education_levels.get(education_level, 0) + 1
            service_types[service_type] = service_types.get(service_type, 0) + 1
        
        return education_levels, service_types

def main():
    """Main function to build educational resources hub"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive educational resources hub")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build educational resources hub
    builder = EducationalResourcesHubBuilder()
    educational_hub = builder.build_educational_resources_hub()
    
    # Save to file
    filepath = builder.save_educational_hub(args.output)
    
    # Print statistics
    education_levels, service_types = builder.get_education_stats()
    
    print(f"\nEducational Resources Hub Statistics:")
    print(f"  Total entries: {len(educational_hub)}")
    print(f"  Education levels:")
    for level, count in sorted(education_levels.items()):
        print(f"    - {level}: {count} entries")
    
    print(f"  Service types:")
    for stype, count in sorted(service_types.items()):
        print(f"    - {stype}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample educational resources:")
    for i, entry in enumerate(educational_hub[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Level: {entry['metadata']['education_level']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
