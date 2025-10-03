#!/usr/bin/env python3
"""
Cultural & Entertainment Database Builder
Creates comprehensive cultural and entertainment information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CulturalEntertainmentDatabaseBuilder:
    """Builds comprehensive cultural and entertainment database"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_museums_and_galleries(self):
        """Add museums and art galleries"""
        museums_galleries = [
            # Major Museums
            {
                "title": "Wichita Art Museum",
                "text": "Wichita Art Museum: 1400 W Museum Blvd, Wichita, KS 67203. Phone: (316) 268-4921. Hours: Tue-Sun 10AM-5PM. American art collection, rotating exhibitions, educational programs, family activities. Free admission on Saturdays.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "art_museum",
                    "services": ["american_art", "rotating_exhibitions", "educational_programs", "family_activities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Exploration Place",
                "text": "Exploration Place: 300 N McLean Blvd, Wichita, KS 67203. Phone: (316) 660-0600. Hours: Tue-Sat 9AM-5PM, Sun 12-5PM. Science and discovery center, interactive exhibits, planetarium, traveling exhibitions. Great for families and children.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "science_museum",
                    "services": ["interactive_exhibits", "planetarium", "traveling_exhibitions", "family_friendly"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita-Sedgwick County Historical Museum",
                "text": "Historical Museum: 204 S Main St, Wichita, KS 67202. Phone: (316) 264-0321. Hours: Tue-Sat 11AM-4PM. Local history, pioneer artifacts, aviation history, rotating exhibits. Admission: Adults $6, Seniors $5, Children $3.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "history_museum",
                    "services": ["local_history", "pioneer_artifacts", "aviation_history", "rotating_exhibits"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Mid-America All-Indian Center",
                "text": "All-Indian Center: 650 N Seneca St, Wichita, KS 67203. Phone: (316) 350-3340. Hours: Tue-Sat 10AM-4PM. Native American art, culture, history, educational programs, powwow grounds. Admission: Adults $5, Seniors $4, Children $3.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "cultural_museum",
                    "services": ["native_american_art", "cultural_programs", "educational_programs", "powwow_grounds"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Art Galleries
            {
                "title": "CityArts",
                "text": "CityArts: 334 N Mead St, Wichita, KS 67202. Phone: (316) 303-8655. Hours: Tue-Fri 10AM-5PM, Sat 10AM-3PM. Contemporary art gallery, artist studios, classes, workshops, exhibitions. Free admission.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "art_gallery",
                    "services": ["contemporary_art", "artist_studios", "classes", "workshops", "exhibitions"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Center for the Arts",
                "text": "Center for the Arts: 9112 E Central Ave, Wichita, KS 67206. Phone: (316) 634-2787. Hours: Mon-Fri 9AM-5PM, Sat 10AM-2PM. Art exhibitions, classes, workshops, studio space, gift shop. Membership available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "museums_galleries",
                    "subcategory": "art_gallery",
                    "services": ["art_exhibitions", "classes", "workshops", "studio_space", "gift_shop"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(museums_galleries)
        logger.info(f"Added {len(museums_galleries)} museums and galleries entries")
    
    def add_theaters_and_performing_arts(self):
        """Add theaters and performing arts venues"""
        theaters_performing_arts = [
            # Major Theaters
            {
                "title": "Century II Performing Arts Center",
                "text": "Century II: 225 W Douglas Ave, Wichita, KS 67202. Phone: (316) 264-9121. Major performing arts venue hosting Broadway shows, concerts, ballet, opera, symphony. Multiple performance spaces including Concert Hall, Convention Hall, Mary Jane Teall Theatre.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "performing_arts_center",
                    "services": ["broadway_shows", "concerts", "ballet", "opera", "symphony"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Community Theatre",
                "text": "Community Theatre: 258 N Fountain, Wichita, KS 67208. Phone: (316) 686-1282. Local community theater productions, musicals, dramas, comedies. Volunteer opportunities available. Season tickets and individual show tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "community_theater",
                    "services": ["local_productions", "musicals", "dramas", "comedies", "volunteer_opportunities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Grand Opera",
                "text": "Grand Opera: 225 W Douglas Ave, Wichita, KS 67202. Phone: (316) 262-8054. Professional opera company presenting full-scale productions, educational programs, community outreach. Season subscriptions and individual tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "opera",
                    "services": ["professional_opera", "full_scale_productions", "educational_programs", "community_outreach"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Music Theatre of Wichita",
                "text": "Music Theatre: 225 W Douglas Ave, Wichita, KS 67202. Phone: (316) 265-3107. Professional musical theater company, Broadway-style productions, summer season, educational programs, internships. Season tickets and individual show tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "musical_theater",
                    "services": ["professional_musical_theater", "broadway_style", "summer_season", "educational_programs", "internships"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Concert Venues
            {
                "title": "Intrust Bank Arena",
                "text": "Intrust Bank Arena: 500 E Waterman St, Wichita, KS 67202. Phone: (316) 440-9000. Major concert venue hosting touring artists, sporting events, family shows, conventions. Capacity 15,000. Premium seating, suites, and general admission available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "concert_venue",
                    "services": ["touring_artists", "sporting_events", "family_shows", "conventions", "premium_seating"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Orpheum Theatre",
                "text": "Orpheum Theatre: 200 N Broadway, Wichita, KS 67202. Phone: (316) 263-0884. Historic theater hosting concerts, comedy shows, special events, private rentals. Beautiful architecture, intimate setting. Check website for upcoming events.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "theaters_performing_arts",
                    "subcategory": "historic_theater",
                    "services": ["concerts", "comedy_shows", "special_events", "private_rentals", "historic_architecture"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(theaters_performing_arts)
        logger.info(f"Added {len(theaters_performing_arts)} theaters and performing arts entries")
    
    def add_sports_venues_and_teams(self):
        """Add sports venues and teams"""
        sports_venues_teams = [
            # Professional Sports
            {
                "title": "Wichita Wind Surge (Baseball)",
                "text": "Wind Surge: Riverfront Stadium, 275 S McLean Blvd, Wichita, KS 67213. Phone: (316) 264-4625. Minor league baseball team, Triple-A affiliate of Miami Marlins. Season runs April-September. Family-friendly entertainment, promotions, group tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "professional_sports",
                    "services": ["minor_league_baseball", "family_entertainment", "promotions", "group_tickets"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Thunder (Hockey)",
                "text": "Thunder: Intrust Bank Arena, 500 E Waterman St, Wichita, KS 67202. Phone: (316) 264-4625. Minor league hockey team, ECHL affiliate. Season runs October-March. Fast-paced action, family entertainment, season tickets and individual game tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "professional_sports",
                    "services": ["minor_league_hockey", "fast_paced_action", "family_entertainment", "season_tickets"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # College Sports
            {
                "title": "Wichita State University Athletics",
                "text": "WSU Athletics: Charles Koch Arena, 1845 Fairmount St, Wichita, KS 67260. Phone: (316) 978-3267. NCAA Division I athletics including basketball, baseball, softball, track and field, volleyball. Season tickets and individual game tickets available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "college_sports",
                    "services": ["ncaa_division_i", "basketball", "baseball", "softball", "track_field", "volleyball"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Friends University Athletics",
                "text": "Friends Athletics: Garvey Physical Education Center, 2100 W University St, Wichita, KS 67213. Phone: (316) 295-5000. NAIA athletics including basketball, football, soccer, track and field, volleyball. Affordable family entertainment.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "college_sports",
                    "services": ["naia_athletics", "basketball", "football", "soccer", "track_field", "volleyball"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Recreational Sports
            {
                "title": "Wichita Ice Center",
                "text": "Ice Center: 505 W Maple St, Wichita, KS 67213. Phone: (316) 337-9199. Public skating, figure skating, hockey leagues, learn-to-skate classes, birthday parties, group events. Two ice rinks, pro shop, snack bar.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "recreational_sports",
                    "services": ["public_skating", "figure_skating", "hockey_leagues", "learn_to_skate", "birthday_parties"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Sports Forum",
                "text": "Sports Forum: 2668 N Greenwich Rd, Wichita, KS 67226. Phone: (316) 440-1000. Indoor sports facility with basketball courts, volleyball courts, fitness center, group fitness classes, youth programs, adult leagues.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "sports_venues_teams",
                    "subcategory": "recreational_sports",
                    "services": ["basketball_courts", "volleyball_courts", "fitness_center", "group_fitness", "youth_programs", "adult_leagues"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(sports_venues_teams)
        logger.info(f"Added {len(sports_venues_teams)} sports venues and teams entries")
    
    def add_parks_and_recreation(self):
        """Add parks and recreation facilities"""
        parks_recreation = [
            # Major Parks
            {
                "title": "Sedgwick County Park",
                "text": "Sedgwick County Park: 6501 W 21st St N, Wichita, KS 67205. Phone: (316) 660-7275. Large park with playgrounds, picnic areas, walking trails, fishing pond, disc golf, volleyball courts, shelters for rent. Great for family outings.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "parks_recreation",
                    "subcategory": "major_parks",
                    "services": ["playgrounds", "picnic_areas", "walking_trails", "fishing_pond", "disc_golf", "volleyball_courts"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Riverside Park",
                "text": "Riverside Park: 720 Nims St, Wichita, KS 67203. Phone: (316) 268-4361. Riverfront park with walking trails, playgrounds, picnic areas, boat ramp, fishing, disc golf course, skate park. Beautiful views of Arkansas River.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "parks_recreation",
                    "subcategory": "major_parks",
                    "services": ["walking_trails", "playgrounds", "picnic_areas", "boat_ramp", "fishing", "disc_golf", "skate_park"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Botanica Wichita",
                "text": "Botanica: 701 Amidon St, Wichita, KS 67203. Phone: (316) 264-0448. Hours: Mon-Sat 9AM-5PM, Sun 1-5PM. Botanical gardens with themed gardens, children's garden, butterfly house, educational programs, special events. Admission: Adults $8, Seniors $7, Children $5.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "parks_recreation",
                    "subcategory": "botanical_gardens",
                    "services": ["themed_gardens", "childrens_garden", "butterfly_house", "educational_programs", "special_events"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Recreation Centers
            {
                "title": "Wichita Parks and Recreation Centers",
                "text": "Recreation Centers: Multiple locations throughout Wichita. Fitness centers, swimming pools, basketball courts, volleyball courts, group fitness classes, youth programs, senior programs, summer camps. Membership and daily passes available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "parks_recreation",
                    "subcategory": "recreation_centers",
                    "services": ["fitness_centers", "swimming_pools", "basketball_courts", "group_fitness", "youth_programs", "senior_programs"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "YMCA of Greater Wichita",
                "text": "YMCA: Multiple locations in Wichita. Fitness centers, swimming pools, basketball courts, group fitness classes, youth programs, summer camps, child care, senior programs. Membership required, financial assistance available.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "parks_recreation",
                    "subcategory": "recreation_centers",
                    "services": ["fitness_centers", "swimming_pools", "basketball_courts", "group_fitness", "youth_programs", "child_care"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(parks_recreation)
        logger.info(f"Added {len(parks_recreation)} parks and recreation entries")
    
    def add_events_and_festivals(self):
        """Add events and festivals"""
        events_festivals = [
            # Annual Events
            {
                "title": "Wichita River Festival",
                "text": "River Festival: Annual festival in May celebrating Wichita's riverfront. Features concerts, food vendors, carnival rides, fireworks, parades, sporting events, family activities. Multiple venues along Arkansas River. Free admission to most events.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "annual_events",
                    "services": ["concerts", "food_vendors", "carnival_rides", "fireworks", "parades", "sporting_events"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Asian Festival",
                "text": "Asian Festival: Annual celebration of Asian culture in September. Features cultural performances, food vendors, traditional crafts, martial arts demonstrations, children's activities. Held at Century II and surrounding areas.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "cultural_events",
                    "services": ["cultural_performances", "food_vendors", "traditional_crafts", "martial_arts", "childrens_activities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Jazz Festival",
                "text": "Jazz Festival: Annual music festival featuring local and national jazz artists. Multiple venues throughout Wichita. Workshops, masterclasses, jam sessions, food vendors. Tickets available for individual performances or festival passes.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "music_festivals",
                    "services": ["jazz_artists", "workshops", "masterclasses", "jam_sessions", "food_vendors"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Seasonal Events
            {
                "title": "Wichita Christmas Lights",
                "text": "Christmas Lights: Annual holiday light displays throughout Wichita. Botanica Wichita features illuminated gardens, Century II hosts holiday concerts, Old Town displays festive decorations. Many free events and displays.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "seasonal_events",
                    "services": ["holiday_light_displays", "illuminated_gardens", "holiday_concerts", "festive_decorations"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Fall Festival",
                "text": "Fall Festival: Annual autumn celebration featuring pumpkin patches, corn mazes, hayrides, fall foods, crafts, children's activities. Multiple locations throughout Wichita area. Great family fun for all ages.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "seasonal_events",
                    "services": ["pumpkin_patches", "corn_mazes", "hayrides", "fall_foods", "crafts", "childrens_activities"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Community Events
            {
                "title": "Wichita Farmers Market",
                "text": "Farmers Market: Open Saturdays 7AM-12PM, May-October. Located at 21st and Ridge Rd. Features local produce, baked goods, crafts, live music, food vendors. Fresh, local products from area farmers and artisans.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "community_events",
                    "services": ["local_produce", "baked_goods", "crafts", "live_music", "food_vendors"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Art Crawl",
                "text": "Art Crawl: Monthly event featuring local artists, galleries, studios, and cultural venues. Self-guided tour of participating locations. Meet artists, view new work, enjoy refreshments. Free event, donations welcome.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "events_festivals",
                    "subcategory": "community_events",
                    "services": ["local_artists", "galleries", "studios", "cultural_venues", "self_guided_tour"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(events_festivals)
        logger.info(f"Added {len(events_festivals)} events and festivals entries")
    
    def add_historical_landmarks(self):
        """Add historical landmarks and sites"""
        historical_landmarks = [
            # Historic Sites
            {
                "title": "Old Cowtown Museum",
                "text": "Old Cowtown: 1865 W Museum Blvd, Wichita, KS 67203. Phone: (316) 264-6398. Hours: Tue-Sat 10AM-5PM, Sun 12-5PM. Living history museum depicting 1870s Wichita. Costumed interpreters, historic buildings, demonstrations, special events. Admission: Adults $8, Seniors $7, Children $6.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "historical_landmarks",
                    "subcategory": "historic_sites",
                    "services": ["living_history", "costumed_interpreters", "historic_buildings", "demonstrations", "special_events"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Keeper of the Plains",
                "text": "Keeper of the Plains: Located at confluence of Big and Little Arkansas Rivers. Iconic 44-foot steel sculpture by Native American artist Blackbear Bosin. Lighting ceremony daily at sunset. Free to visit, beautiful riverfront location.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "historical_landmarks",
                    "subcategory": "historic_sites",
                    "services": ["iconic_sculpture", "lighting_ceremony", "riverfront_location", "free_visit"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita-Sedgwick County Historical Museum",
                "text": "Historical Museum: 204 S Main St, Wichita, KS 67202. Phone: (316) 264-0321. Hours: Tue-Sat 11AM-4PM. Local history, pioneer artifacts, aviation history, rotating exhibits. Admission: Adults $6, Seniors $5, Children $3.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "historical_landmarks",
                    "subcategory": "historic_sites",
                    "services": ["local_history", "pioneer_artifacts", "aviation_history", "rotating_exhibits"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Historic Districts
            {
                "title": "Old Town Wichita",
                "text": "Old Town: Historic district featuring restored warehouses, restaurants, bars, shops, entertainment venues. Brick streets, historic architecture, vibrant nightlife. Walking tours available, many events and festivals held here.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "medium",
                    "source": "cultural_entertainment",
                    "entertainment_category": "historical_landmarks",
                    "subcategory": "historic_districts",
                    "services": ["restored_warehouses", "restaurants", "bars", "shops", "entertainment_venues", "walking_tours"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Delano Historic District",
                "text": "Delano District: Historic neighborhood with unique shops, restaurants, bars, entertainment venues. Known for its eclectic mix of businesses and vibrant community. Walking tours, special events, local festivals.",
                "category": "cultural_entertainment",
                "metadata": {
                    "priority": "low",
                    "source": "cultural_entertainment",
                    "entertainment_category": "historical_landmarks",
                    "subcategory": "historic_districts",
                    "services": ["unique_shops", "restaurants", "bars", "entertainment_venues", "walking_tours", "special_events"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(historical_landmarks)
        logger.info(f"Added {len(historical_landmarks)} historical landmarks entries")
    
    def build_cultural_entertainment_database(self):
        """Build the complete cultural and entertainment database"""
        logger.info("Building comprehensive cultural and entertainment database...")
        
        # Add cultural and entertainment information in priority order
        self.add_museums_and_galleries()
        self.add_theaters_and_performing_arts()
        self.add_sports_venues_and_teams()
        self.add_parks_and_recreation()
        self.add_events_and_festivals()
        self.add_historical_landmarks()
        
        logger.info(f"Built cultural and entertainment database with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_cultural_entertainment_database(self, filename: str = None):
        """Save the cultural and entertainment database to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cultural_entertainment_database_{timestamp}.json"
        
        filepath = os.path.join("data", "cultural_entertainment", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved cultural and entertainment database to {filepath}")
        return filepath
    
    def get_cultural_entertainment_stats(self):
        """Get statistics by entertainment category and subcategory"""
        entertainment_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            entertainment_category = entry['metadata'].get('entertainment_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            entertainment_categories[entertainment_category] = entertainment_categories.get(entertainment_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return entertainment_categories, subcategories

def main():
    """Main function to build cultural and entertainment database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive cultural and entertainment database")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build cultural and entertainment database
    builder = CulturalEntertainmentDatabaseBuilder()
    cultural_entertainment_database = builder.build_cultural_entertainment_database()
    
    # Save to file
    filepath = builder.save_cultural_entertainment_database(args.output)
    
    # Print statistics
    entertainment_categories, subcategories = builder.get_cultural_entertainment_stats()
    
    print(f"\nCultural & Entertainment Database Statistics:")
    print(f"  Total entries: {len(cultural_entertainment_database)}")
    print(f"  Entertainment categories:")
    for category, count in sorted(entertainment_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample cultural and entertainment entries:")
    for i, entry in enumerate(cultural_entertainment_database[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Entertainment Category: {entry['metadata']['entertainment_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
