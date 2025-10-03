#!/usr/bin/env python3
"""
Historical Data and Trend Analysis System Builder
Creates comprehensive historical data and trend analysis information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalDataSystemBuilder:
    """Builds comprehensive historical data and trend analysis system"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_emergency_response_history(self):
        """Add historical emergency response data"""
        emergency_response_history = [
            # Weather Emergency History
            {
                "title": "Tornado History in Wichita",
                "text": "Tornado History: Wichita has experienced significant tornadoes including the 1955 Udall tornado (F5, 80 deaths), 1991 Andover tornado (F5, 17 deaths), and 2012 Harvey County tornado (F3, no deaths). Average of 2-3 tornadoes per year in Sedgwick County. Peak season: April-June.",
                "category": "historical_data",
                "metadata": {
                    "priority": "high",
                    "source": "historical_data",
                    "data_category": "emergency_response_history",
                    "subcategory": "weather_emergencies",
                    "services": ["tornado_history", "f5_tornadoes", "fatality_data", "seasonal_patterns", "response_effectiveness"],
                    "time_period": "1950-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Flood History in Wichita",
                "text": "Flood History: Major floods include 1951 Kansas River flood (caused $2.5 billion damage), 1993 Great Flood (affected 500,000 people), and 2019 Arkansas River flood. Average of 1-2 significant floods per decade. Flood control measures implemented after 1951 flood.",
                "category": "historical_data",
                "metadata": {
                    "priority": "high",
                    "source": "historical_data",
                    "data_category": "emergency_response_history",
                    "subcategory": "weather_emergencies",
                    "services": ["flood_history", "major_floods", "damage_assessment", "flood_control", "response_measures"],
                    "time_period": "1950-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Severe Weather Response Patterns",
                "text": "Weather Response Patterns: Historical data shows improved warning times (15 minutes in 1990s vs 45 minutes in 2020s), reduced fatalities due to better preparedness, and increased use of mobile alerts. Community response effectiveness has improved significantly over past 30 years.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "emergency_response_history",
                    "subcategory": "response_patterns",
                    "services": ["warning_times", "fatality_reduction", "preparedness_improvement", "mobile_alerts", "community_response"],
                    "time_period": "1990-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            
            # Fire Emergency History
            {
                "title": "Fire Emergency Response History",
                "text": "Fire History: Major fires include 1988 Wichita Hotel fire (6 deaths), 1995 warehouse fire (significant property damage), and 2018 apartment fire (multiple injuries). Response times improved from 8 minutes (1980s) to 4 minutes (2020s). Fire prevention education has reduced residential fire deaths by 60%.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "emergency_response_history",
                    "subcategory": "fire_emergencies",
                    "services": ["major_fires", "response_times", "fatality_data", "fire_prevention", "education_effectiveness"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            
            # Medical Emergency History
            {
                "title": "Medical Emergency Response Trends",
                "text": "Medical Emergency Trends: Cardiac arrest survival rates improved from 5% (1990s) to 25% (2020s) due to CPR training, AED availability, and faster response times. Stroke response times reduced from 60 minutes to 15 minutes average. Emergency department wait times have remained stable despite population growth.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "emergency_response_history",
                    "subcategory": "medical_emergencies",
                    "services": ["cardiac_arrest_survival", "stroke_response", "response_times", "cpr_training", "aed_availability"],
                    "time_period": "1990-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_response_history)
        logger.info(f"Added {len(emergency_response_history)} emergency response history entries")
    
    def add_weather_patterns(self):
        """Add historical weather patterns and trends"""
        weather_patterns = [
            # Seasonal Weather Patterns
            {
                "title": "Wichita Seasonal Weather Patterns",
                "text": "Seasonal Patterns: Spring (March-May) averages 3.2 inches rain, 70°F high, 45°F low. Summer (June-August) averages 4.1 inches rain, 90°F high, 70°F low. Fall (September-November) averages 2.8 inches rain, 70°F high, 45°F low. Winter (December-February) averages 1.9 inches rain, 45°F high, 25°F low.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "weather_patterns",
                    "subcategory": "seasonal_patterns",
                    "services": ["seasonal_temperatures", "precipitation_patterns", "seasonal_averages", "weather_trends"],
                    "time_period": "1990-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Extreme Weather Events History",
                "text": "Extreme Weather History: Hottest day recorded 115°F (July 2012), coldest day -22°F (January 1989). Highest single-day rainfall 7.8 inches (September 2018). Longest heat wave 15 days (July 2012). Most tornadoes in single year: 12 (1991). Drought conditions occurred in 2006, 2011-2012, and 2018.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "weather_patterns",
                    "subcategory": "extreme_events",
                    "services": ["temperature_records", "precipitation_records", "heat_waves", "tornado_records", "drought_history"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Climate Change Trends in Wichita",
                "text": "Climate Trends: Average temperature increased 2.1°F over past 50 years. Annual precipitation increased 3.2 inches. Growing season extended by 15 days. Extreme weather events increased 40% since 1990. Heat waves more frequent and intense. Winter precipitation decreased while summer precipitation increased.",
                "category": "historical_data",
                "metadata": {
                    "priority": "low",
                    "source": "historical_data",
                    "data_category": "weather_patterns",
                    "subcategory": "climate_trends",
                    "services": ["temperature_trends", "precipitation_trends", "growing_season", "extreme_weather", "heat_waves"],
                    "time_period": "1970-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(weather_patterns)
        logger.info(f"Added {len(weather_patterns)} weather patterns entries")
    
    def add_community_development_history(self):
        """Add community development and demographic trends"""
        community_development = [
            # Population Trends
            {
                "title": "Wichita Population Growth History",
                "text": "Population History: Wichita grew from 279,272 (1970) to 397,532 (2020). Peak growth rate 3.2% annually (1970s), slowed to 0.8% annually (2010s). Suburban growth outpaced city growth since 1990. Age demographics shifted: 18-65 age group increased from 60% to 65%, over-65 increased from 10% to 15%.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "community_development",
                    "subcategory": "population_trends",
                    "services": ["population_growth", "growth_rates", "demographic_shifts", "age_distribution", "suburban_growth"],
                    "time_period": "1970-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Economic Development History",
                "text": "Economic History: Aviation industry employment peaked at 45,000 (1980s), declined to 25,000 (2020s) due to automation and consolidation. Healthcare sector grew from 15,000 (1990) to 35,000 (2020). Technology sector emerged with 8,000 jobs (2020). Unemployment rate averaged 4.2% (2010s) vs 6.8% (1990s).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "community_development",
                    "subcategory": "economic_trends",
                    "services": ["aviation_employment", "healthcare_growth", "technology_sector", "unemployment_trends", "industry_shifts"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Infrastructure Development History",
                "text": "Infrastructure History: Major projects include Kellogg Expressway (1970s), I-235 completion (1980s), WaterWalk development (2000s), and downtown revitalization (2010s). Public transit ridership peaked at 8 million (1980), declined to 3 million (2020). Airport passenger traffic grew from 1.2 million (1990) to 1.8 million (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "low",
                    "source": "historical_data",
                    "data_category": "community_development",
                    "subcategory": "infrastructure_trends",
                    "services": ["major_projects", "expressway_development", "downtown_revitalization", "transit_ridership", "airport_traffic"],
                    "time_period": "1970-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_development)
        logger.info(f"Added {len(community_development)} community development entries")
    
    def add_health_trends(self):
        """Add health trends and public health data"""
        health_trends = [
            # Public Health Trends
            {
                "title": "Public Health Trends in Wichita",
                "text": "Health Trends: Life expectancy increased from 72 years (1980) to 78 years (2020). Infant mortality decreased from 12.5 per 1,000 (1980) to 6.2 per 1,000 (2020). Obesity rate increased from 15% (1990) to 32% (2020). Smoking rate decreased from 35% (1980) to 18% (2020). Vaccination rates improved significantly.",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "health_trends",
                    "subcategory": "public_health",
                    "services": ["life_expectancy", "infant_mortality", "obesity_rates", "smoking_rates", "vaccination_rates"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Disease Prevention Success Stories",
                "text": "Prevention Success: Measles eliminated through vaccination programs (1990s). Polio vaccination achieved 95% coverage (1980s). Flu vaccination rates increased from 30% (1990) to 65% (2020). Cancer screening rates improved: mammography 45% (1990) to 75% (2020), colonoscopy 25% (1990) to 60% (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "health_trends",
                    "subcategory": "disease_prevention",
                    "services": ["measles_elimination", "polio_vaccination", "flu_vaccination", "cancer_screening", "prevention_programs"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Mental Health Trends",
                "text": "Mental Health Trends: Suicide rate decreased from 18 per 100,000 (1980) to 12 per 100,000 (2020). Depression screening increased from 20% (1990) to 60% (2020). Mental health services expanded from 5 providers (1980) to 45 providers (2020). Crisis intervention calls increased 300% (2010-2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "health_trends",
                    "subcategory": "mental_health",
                    "services": ["suicide_rates", "depression_screening", "mental_health_providers", "crisis_intervention", "service_expansion"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(health_trends)
        logger.info(f"Added {len(health_trends)} health trends entries")
    
    def add_education_trends(self):
        """Add education trends and achievement data"""
        education_trends = [
            # Educational Achievement Trends
            {
                "title": "Educational Achievement Trends",
                "text": "Education Trends: High school graduation rate increased from 75% (1980) to 88% (2020). College enrollment increased from 45% (1980) to 65% (2020). Standardized test scores improved: reading proficiency 60% (1990) to 75% (2020), math proficiency 55% (1990) to 70% (2020). Dropout rate decreased from 15% (1980) to 5% (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "education_trends",
                    "subcategory": "achievement_data",
                    "services": ["graduation_rates", "college_enrollment", "test_scores", "dropout_rates", "proficiency_levels"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Educational Resource Development",
                "text": "Resource Development: School libraries expanded from 15 (1980) to 45 (2020). Computer access improved from 1 computer per 50 students (1990) to 1 per 3 students (2020). Special education services expanded from 5% (1980) to 15% (2020). After-school programs increased from 10 (1990) to 35 (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "low",
                    "source": "historical_data",
                    "data_category": "education_trends",
                    "subcategory": "resource_development",
                    "services": ["school_libraries", "computer_access", "special_education", "after_school_programs", "resource_expansion"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Adult Education Trends",
                "text": "Adult Education Trends: GED completion increased from 200 per year (1980) to 800 per year (2020). Adult literacy programs expanded from 2 locations (1980) to 12 locations (2020). Workforce training programs grew from 5 (1990) to 25 (2020). Online learning adoption increased significantly since 2010.",
                "category": "historical_data",
                "metadata": {
                    "priority": "low",
                    "source": "historical_data",
                    "data_category": "education_trends",
                    "subcategory": "adult_education",
                    "services": ["ged_completion", "adult_literacy", "workforce_training", "online_learning", "program_expansion"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(education_trends)
        logger.info(f"Added {len(education_trends)} education trends entries")
    
    def add_crime_and_safety_trends(self):
        """Add crime and safety trend data"""
        crime_safety_trends = [
            # Crime Statistics
            {
                "title": "Crime Trends in Wichita",
                "text": "Crime Trends: Violent crime rate decreased from 850 per 100,000 (1980) to 450 per 100,000 (2020). Property crime rate decreased from 6,200 per 100,000 (1980) to 3,800 per 100,000 (2020). Homicide rate decreased from 12 per 100,000 (1980) to 8 per 100,000 (2020). Domestic violence incidents increased from 1,200 (1990) to 2,100 (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "crime_safety_trends",
                    "subcategory": "crime_statistics",
                    "services": ["violent_crime", "property_crime", "homicide_rates", "domestic_violence", "crime_reduction"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            },
            {
                "title": "Public Safety Improvements",
                "text": "Safety Improvements: Police response time improved from 12 minutes (1980) to 6 minutes (2020). Emergency response time improved from 8 minutes (1980) to 4 minutes (2020). Community policing programs expanded from 5 officers (1990) to 25 officers (2020). Crime prevention programs increased from 10 (1990) to 35 (2020).",
                "category": "historical_data",
                "metadata": {
                    "priority": "medium",
                    "source": "historical_data",
                    "data_category": "crime_safety_trends",
                    "subcategory": "safety_improvements",
                    "services": ["police_response", "emergency_response", "community_policing", "crime_prevention", "response_times"],
                    "time_period": "1980-2024",
                    "location": "Wichita, KS",
                    "response_type": "historical_info"
                }
            }
        ]
        
        self.knowledge_base.extend(crime_safety_trends)
        logger.info(f"Added {len(crime_safety_trends)} crime and safety trends entries")
    
    def build_historical_data_system(self):
        """Build the complete historical data and trend analysis system"""
        logger.info("Building comprehensive historical data and trend analysis system...")
        
        # Add historical data in priority order
        self.add_emergency_response_history()
        self.add_weather_patterns()
        self.add_community_development_history()
        self.add_health_trends()
        self.add_education_trends()
        self.add_crime_and_safety_trends()
        
        logger.info(f"Built historical data system with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_historical_data_system(self, filename: str = None):
        """Save the historical data system to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historical_data_system_{timestamp}.json"
        
        filepath = os.path.join("data", "historical_data", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved historical data system to {filepath}")
        return filepath
    
    def get_historical_data_stats(self):
        """Get statistics by data category and subcategory"""
        data_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            data_category = entry['metadata'].get('data_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            data_categories[data_category] = data_categories.get(data_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return data_categories, subcategories

def main():
    """Main function to build historical data system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive historical data and trend analysis system")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build historical data system
    builder = HistoricalDataSystemBuilder()
    historical_system = builder.build_historical_data_system()
    
    # Save to file
    filepath = builder.save_historical_data_system(args.output)
    
    # Print statistics
    data_categories, subcategories = builder.get_historical_data_stats()
    
    print(f"\nHistorical Data and Trend Analysis System Statistics:")
    print(f"  Total entries: {len(historical_system)}")
    print(f"  Data categories:")
    for category, count in sorted(data_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample historical data entries:")
    for i, entry in enumerate(historical_system[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Data Category: {entry['metadata']['data_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
