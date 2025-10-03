#!/usr/bin/env python3
"""
Comprehensive Emergency Procedures Database Builder
Creates extensive emergency response knowledge base
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveEmergencyBuilder:
    """Builds comprehensive emergency procedures database"""
    
    def __init__(self, location_config: Dict):
        self.location = location_config
        self.knowledge_base = []
        
    def add_medical_emergencies(self):
        """Add comprehensive medical emergency procedures"""
        medical_emergencies = [
            # Cardiac Emergencies
            {
                "title": "Heart Attack - Detailed Response",
                "text": "Heart attack signs: chest pain/pressure, shortness of breath, nausea, cold sweat, arm/jaw/back pain. Call 911 immediately. Keep patient calm, seated, loosen clothing. If they have nitroglycerin, help them take it. Monitor breathing. Do not drive them - wait for ambulance. Time is critical.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "heart_attack",
                    "subcategory": "cardiac",
                    "response_type": "medical_emergency",
                    "time_critical": True
                }
            },
            {
                "title": "Cardiac Arrest Response",
                "text": "Cardiac arrest: Person unresponsive, not breathing normally. Call 911 immediately. Start CPR: 30 compressions, 2 breaths. Use AED if available. Continue until EMS arrives. Every minute counts - immediate action required.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "cardiac_arrest",
                    "subcategory": "cardiac",
                    "response_type": "medical_emergency",
                    "time_critical": True
                }
            },
            {
                "title": "Angina Emergency",
                "text": "Angina (chest pain): Rest immediately. If prescribed, take nitroglycerin. If pain persists after 5 minutes, take second dose. If pain continues, call 911. Do not ignore chest pain - could indicate heart attack.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "angina",
                    "subcategory": "cardiac",
                    "response_type": "medical_emergency"
                }
            },
            
            # Neurological Emergencies
            {
                "title": "Stroke - FAST Recognition",
                "text": "Stroke signs: Face drooping, Arm weakness, Speech difficulty, Time to call 911. Note time symptoms started - critical for treatment. Keep patient calm, lying down. Do not give food/water. Do not drive - call ambulance immediately.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "stroke",
                    "subcategory": "neurological",
                    "response_type": "medical_emergency",
                    "time_critical": True
                }
            },
            {
                "title": "Seizure Response - Detailed",
                "text": "Seizure: Do not restrain person. Clear area of dangerous objects. Place person on side if possible. Do not put anything in mouth. Time the seizure. Call 911 if seizure lasts >5 minutes, person is injured, or multiple seizures occur. Stay with person until fully conscious.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "seizure",
                    "subcategory": "neurological",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Head Injury Emergency",
                "text": "Head injury: If unconscious, call 911 immediately. If conscious, watch for: confusion, nausea, vomiting, severe headache, unequal pupils, slurred speech. Do not move person unless in danger. Apply ice to reduce swelling. Seek medical attention for any head injury.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "head_injury",
                    "subcategory": "neurological",
                    "response_type": "medical_emergency"
                }
            },
            
            # Respiratory Emergencies
            {
                "title": "Choking - Adult Response",
                "text": "Choking adult: If person can cough/speak, encourage coughing. If cannot breathe: Stand behind person, hands above navel, quick upward thrusts. For unconscious person: Start CPR. Call 911 immediately. Continue until object is expelled or person becomes unconscious.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "choking_adult",
                    "subcategory": "respiratory",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Choking - Child Response",
                "text": "Choking child: If child can cough, encourage coughing. If cannot breathe: Kneel behind child, hands above navel, quick upward thrusts. For infant: Hold face down on forearm, support head, give 5 back blows, then 5 chest thrusts. Call 911 immediately.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "choking_child",
                    "subcategory": "respiratory",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Asthma Attack Emergency",
                "text": "Asthma attack: Help person sit upright. Use rescue inhaler if available. If no improvement after 10 minutes, call 911. Watch for: severe difficulty breathing, inability to speak, blue lips/nails. Do not leave person alone.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "asthma_attack",
                    "subcategory": "respiratory",
                    "response_type": "medical_emergency"
                }
            },
            
            # Allergic Reactions
            {
                "title": "Severe Allergic Reaction (Anaphylaxis)",
                "text": "Anaphylaxis signs: difficulty breathing, swelling of face/throat, hives, nausea, dizziness, rapid pulse. Call 911 immediately. If person has epinephrine auto-injector, help them use it. Keep person calm, lying down with legs elevated. Stay with person until help arrives.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "anaphylaxis",
                    "subcategory": "allergic_reaction",
                    "response_type": "medical_emergency",
                    "time_critical": True
                }
            },
            {
                "title": "Food Allergy Emergency",
                "text": "Food allergy reaction: Stop eating immediately. If mild reaction (hives, itching), take antihistamine if available. If severe reaction (difficulty breathing, swelling), call 911 immediately. Use epinephrine auto-injector if available. Do not wait for symptoms to worsen.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "food_allergy",
                    "subcategory": "allergic_reaction",
                    "response_type": "medical_emergency"
                }
            },
            
            # Poisoning Emergencies
            {
                "title": "Poisoning Emergency Response",
                "text": "Poisoning: Call Poison Control 1-800-222-1222 immediately. Do not induce vomiting unless instructed. Have product container ready. Provide age, weight, substance ingested. If person unconscious, call 911 immediately. Do not give anything by mouth.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "poisoning",
                    "subcategory": "poisoning",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Drug Overdose Emergency",
                "text": "Drug overdose: Call 911 immediately. Check breathing, start CPR if needed. Do not leave person alone. If unconscious, place in recovery position. Do not induce vomiting. Gather information about substances taken. Stay with person until help arrives.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "drug_overdose",
                    "subcategory": "poisoning",
                    "response_type": "medical_emergency"
                }
            },
            
            # Trauma Emergencies
            {
                "title": "Severe Bleeding Control",
                "text": "Severe bleeding: Apply direct pressure with clean cloth/bandage. Elevate injured area if possible. If bleeding continues, apply more pressure. Do not remove original bandage. Call 911 immediately. If object is embedded, do not remove it - apply pressure around it.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "severe_bleeding",
                    "subcategory": "trauma",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Broken Bone Emergency",
                "text": "Broken bone: Do not move person unless in danger. Immobilize injured area with splint if possible. Apply ice to reduce swelling. Do not try to straighten bone. Call 911 for severe breaks, compound fractures, or if person is unconscious.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "medical_emergency",
                    "condition": "broken_bone",
                    "subcategory": "trauma",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Burn Emergency Response",
                "text": "Burn treatment: Cool burn with cool water for 10-15 minutes. Do not use ice. Remove jewelry/constrictive clothing. Cover with clean, dry cloth. Do not apply butter, oil, or ointments. Call 911 for severe burns, burns to face/hands/feet, or electrical/chemical burns.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "medical_emergency",
                    "condition": "burn",
                    "subcategory": "trauma",
                    "response_type": "medical_emergency"
                }
            },
            
            # Environmental Emergencies
            {
                "title": "Heat Stroke Emergency",
                "text": "Heat stroke: High body temperature, confusion, loss of consciousness. Call 911 immediately. Move person to cool area. Remove excess clothing. Cool with water/fans. Do not give fluids if unconscious. This is life-threatening emergency.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "heat_stroke",
                    "subcategory": "environmental",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Hypothermia Emergency",
                "text": "Hypothermia: Shivering, confusion, drowsiness, slow pulse. Call 911 immediately. Move person to warm area. Remove wet clothing. Warm gradually with blankets. Do not use hot water or heating pads. Do not give alcohol or caffeine.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "hypothermia",
                    "subcategory": "environmental",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Frostbite Emergency",
                "text": "Frostbite: Skin appears white, gray, or blistered. Call 911 for severe frostbite. Move to warm area. Remove wet clothing. Warm affected area gradually. Do not rub or use hot water. Do not walk on frostbitten feet if possible.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "medical_emergency",
                    "condition": "frostbite",
                    "subcategory": "environmental",
                    "response_type": "medical_emergency"
                }
            },
            
            # Pediatric Emergencies
            {
                "title": "Child Fever Emergency",
                "text": "High fever in child: Temperature >104°F, lethargy, difficulty breathing, rash, stiff neck. Call 911 immediately. Do not give aspirin to children. Use lukewarm water for cooling. Keep child hydrated. Monitor breathing and consciousness.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "child_fever",
                    "subcategory": "pediatric",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Child Dehydration Emergency",
                "text": "Child dehydration: Dry mouth, no tears, sunken eyes, decreased urination, lethargy. Call 911 if severe. Offer small amounts of fluids frequently. Use oral rehydration solutions. Do not give plain water to infants. Monitor for improvement.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "medical_emergency",
                    "condition": "child_dehydration",
                    "subcategory": "pediatric",
                    "response_type": "medical_emergency"
                }
            },
            
            # Senior Emergencies
            {
                "title": "Senior Fall Emergency",
                "text": "Senior fall: Do not move person unless in danger. Check for injuries, especially head/neck. Call 911 if person cannot get up, has pain, or appears injured. Stay with person until help arrives. Document fall circumstances for medical team.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "medical_emergency",
                    "condition": "senior_fall",
                    "subcategory": "senior",
                    "response_type": "medical_emergency"
                }
            },
            {
                "title": "Senior Confusion Emergency",
                "text": "Sudden confusion in senior: Could indicate stroke, infection, medication reaction, or other serious condition. Call 911 immediately. Do not leave person alone. Note any recent changes in behavior, medications, or health. Stay calm and reassuring.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "medical_emergency",
                    "condition": "senior_confusion",
                    "subcategory": "senior",
                    "response_type": "medical_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(medical_emergencies)
        logger.info(f"Added {len(medical_emergencies)} medical emergency procedures")
    
    def add_natural_disaster_procedures(self):
        """Add comprehensive natural disaster procedures"""
        disaster_procedures = [
            # Tornado Procedures
            {
                "title": "Tornado Warning - Home Safety",
                "text": "Tornado warning at home: Go to basement or lowest floor. Interior room without windows (bathroom, closet, hallway). Cover head and neck. Stay away from windows and doors. Avoid mobile homes - go to nearest sturdy building. Monitor weather radio.",
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
                "title": "Tornado Warning - Vehicle Safety",
                "text": "Tornado warning in vehicle: Do not try to outrun tornado. Park vehicle safely, get out immediately. Find lowest area nearby (ditch, culvert). Lie flat, cover head with hands. Avoid overpasses and bridges. Do not stay in vehicle.",
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
                "title": "Tornado Warning - Mobile Home Safety",
                "text": "Tornado warning in mobile home: Leave immediately. Go to nearest sturdy building or storm shelter. If no building nearby, go to lowest area and lie flat. Mobile homes are unsafe in tornadoes - never stay inside.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "tornado",
                    "location": "mobile_home",
                    "response_type": "weather_emergency"
                }
            },
            
            # Flood Procedures
            {
                "title": "Flood Warning - Evacuation",
                "text": "Flood warning: Move to higher ground immediately. Do not walk or drive through flood waters. Turn around, don't drown. Turn off utilities if safe to do so. Take emergency supplies. Stay informed via weather radio or local news.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "flood",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Flash Flood Emergency",
                "text": "Flash flood: Move to highest ground immediately. Do not wait for official evacuation order. Avoid canyons, washes, and low-lying areas. Do not attempt to cross flooded roads. Stay away from downed power lines.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "flash_flood",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Flood Aftermath Safety",
                "text": "Flood aftermath: Do not return home until officials declare area safe. Watch for structural damage, gas leaks, electrical hazards. Do not drink tap water until declared safe. Document damage for insurance. Be aware of contamination risks.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "flood_aftermath",
                    "response_type": "weather_emergency"
                }
            },
            
            # Winter Storm Procedures
            {
                "title": "Winter Storm Emergency",
                "text": "Winter storm: Stay indoors if possible. If must go out, dress in layers, avoid overexertion. Keep emergency supplies: food, water, blankets, flashlight. Check on elderly neighbors. Keep pets indoors.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "winter_storm",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Ice Storm Safety",
                "text": "Ice storm: Stay off roads if possible. If driving, slow down, increase following distance. Watch for downed power lines. Stay away from trees and power lines. Use generators safely - outdoors only, away from windows.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "ice_storm",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Blizzard Emergency",
                "text": "Blizzard: Stay indoors. If caught outside, find shelter immediately. Cover exposed skin. Stay hydrated. Signal for help if stranded. Do not attempt to walk in blizzard conditions - you can become lost in minutes.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "natural_disaster",
                    "disaster_type": "blizzard",
                    "response_type": "weather_emergency"
                }
            },
            
            # Heat Wave Procedures
            {
                "title": "Heat Wave Emergency",
                "text": "Heat wave: Stay in air conditioning if possible. If no AC, go to cooling center, library, or mall. Drink plenty of water. Avoid outdoor activities during peak heat. Check on elderly neighbors. Never leave children/pets in vehicles.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "heat_wave",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Heat Exhaustion Response",
                "text": "Heat exhaustion: Move to cool area immediately. Drink cool water. Remove excess clothing. Apply cool, wet cloths. If symptoms worsen (confusion, nausea, vomiting), call 911 immediately - could be heat stroke.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "heat_exhaustion",
                    "response_type": "weather_emergency"
                }
            },
            
            # Thunderstorm Procedures
            {
                "title": "Severe Thunderstorm Safety",
                "text": "Severe thunderstorm: Stay indoors, away from windows. Avoid electrical equipment and plumbing. Do not use corded phones. If outside, avoid high ground, water, metal objects. Seek sturdy shelter immediately.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "severe_thunderstorm",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Lightning Safety",
                "text": "Lightning safety: When thunder roars, go indoors. Stay inside for 30 minutes after last thunder. Avoid plumbing, electronics, windows. If outside, avoid tall objects, water, metal. If in open area, crouch low, avoid being highest object.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "natural_disaster",
                    "disaster_type": "lightning",
                    "response_type": "weather_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(disaster_procedures)
        logger.info(f"Added {len(disaster_procedures)} natural disaster procedures")
    
    def add_home_emergency_procedures(self):
        """Add comprehensive home emergency procedures"""
        home_emergencies = [
            # Fire Emergencies
            {
                "title": "House Fire Emergency",
                "text": "House fire: Get everyone out immediately. Call 911 from outside. Do not re-enter burning building. If trapped, close doors, cover vents, signal from window. Stop, drop, and roll if clothing catches fire. Meet at designated meeting place.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "fire",
                    "response_type": "fire_emergency"
                }
            },
            {
                "title": "Kitchen Fire Response",
                "text": "Kitchen fire: Turn off heat source. For grease fires, cover pan with lid or use baking soda - never water. For oven fires, turn off oven, keep door closed. If fire spreads, evacuate immediately and call 911.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "home_emergency",
                    "emergency_type": "kitchen_fire",
                    "response_type": "fire_emergency"
                }
            },
            {
                "title": "Smoke Inhalation Emergency",
                "text": "Smoke inhalation: Get to fresh air immediately. Call 911 if having difficulty breathing. Do not return to smoky area. If person unconscious, check breathing, start CPR if needed. Seek medical attention for any smoke exposure.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "smoke_inhalation",
                    "response_type": "medical_emergency"
                }
            },
            
            # Gas Emergencies
            {
                "title": "Gas Leak Emergency",
                "text": "Gas leak: Evacuate immediately. Do not use phones, lights, or electrical devices. Call 911 from outside. Do not return until cleared by officials. If you smell gas, leave immediately - do not investigate.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "gas_leak",
                    "response_type": "utility_emergency"
                }
            },
            {
                "title": "Carbon Monoxide Emergency",
                "text": "Carbon monoxide: Headache, nausea, dizziness, confusion. Get everyone to fresh air immediately. Call 911. Check CO detector batteries. Do not re-enter until area is cleared by professionals.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "carbon_monoxide",
                    "response_type": "utility_emergency"
                }
            },
            
            # Electrical Emergencies
            {
                "title": "Electrical Fire Emergency",
                "text": "Electrical fire: Turn off power at main breaker if safe. Use Class C fire extinguisher or baking soda - never water. Evacuate immediately if fire spreads. Call 911. Do not touch electrical equipment during fire.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "electrical_fire",
                    "response_type": "fire_emergency"
                }
            },
            {
                "title": "Electrical Shock Emergency",
                "text": "Electrical shock: Do not touch victim until power is off. Turn off power at main breaker. Call 911 immediately. If victim not breathing, start CPR. Check for burns at entry/exit points. Do not move victim unless necessary.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "electrical_shock",
                    "response_type": "medical_emergency"
                }
            },
            
            # Water Emergencies
            {
                "title": "Water Leak Emergency",
                "text": "Major water leak: Turn off main water valve immediately. Turn off electricity if water near electrical outlets. Move valuables to dry area. Call plumber for repairs. Document damage for insurance.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "home_emergency",
                    "emergency_type": "water_leak",
                    "response_type": "utility_emergency"
                }
            },
            {
                "title": "Sewer Backup Emergency",
                "text": "Sewer backup: Do not use plumbing fixtures. Turn off water to prevent further backup. Evacuate if sewage reaches living areas. Call plumber and insurance company. Do not attempt cleanup without protective equipment.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "home_emergency",
                    "emergency_type": "sewer_backup",
                    "response_type": "utility_emergency"
                }
            },
            
            # Security Emergencies
            {
                "title": "Home Invasion Emergency",
                "text": "Home invasion: If intruder is inside, do not confront. Go to safe room if available, lock door, call 911. If intruder demands valuables, comply - property can be replaced. Focus on getting everyone to safety.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "home_emergency",
                    "emergency_type": "home_invasion",
                    "response_type": "security_emergency"
                }
            },
            {
                "title": "Burglary Response",
                "text": "Burglary discovered: Do not enter home - intruder may still be inside. Go to safe location, call 911. Do not touch anything - preserve evidence. Contact insurance company. Document all missing items.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "home_emergency",
                    "emergency_type": "burglary",
                    "response_type": "security_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(home_emergencies)
        logger.info(f"Added {len(home_emergencies)} home emergency procedures")
    
    def add_vehicle_emergency_procedures(self):
        """Add comprehensive vehicle emergency procedures"""
        vehicle_emergencies = [
            # Car Accidents
            {
                "title": "Car Accident Response",
                "text": "Car accident: Check for injuries, call 911 immediately. Move to safe location if possible. Turn on hazard lights. Do not admit fault. Exchange insurance information. Take photos of damage. Get witness contact information.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "vehicle_emergency",
                    "emergency_type": "car_accident",
                    "response_type": "traffic_emergency"
                }
            },
            {
                "title": "Car Accident - Injuries Present",
                "text": "Car accident with injuries: Call 911 immediately. Do not move injured person unless in danger. Turn off vehicle engine. Apply pressure to stop bleeding. Do not remove helmet if motorcyclist. Stay with injured person until help arrives.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "vehicle_emergency",
                    "emergency_type": "car_accident_injuries",
                    "response_type": "medical_emergency"
                }
            },
            
            # Vehicle Breakdowns
            {
                "title": "Vehicle Breakdown - Highway",
                "text": "Vehicle breakdown on highway: Pull to shoulder, turn on hazard lights. Exit vehicle from passenger side. Move away from traffic. Call roadside assistance or 911. Stay visible to other drivers. Do not stand behind vehicle.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "vehicle_emergency",
                    "emergency_type": "breakdown_highway",
                    "response_type": "traffic_emergency"
                }
            },
            {
                "title": "Vehicle Breakdown - Remote Area",
                "text": "Vehicle breakdown in remote area: Stay with vehicle - easier to find than person. Use flares or reflective materials for visibility. Conserve fuel for heat. Stay hydrated. Signal for help with horn or lights. Do not wander from vehicle.",
                "category": "emergency",
                "metadata": {
                    "priority": "high",
                    "source": "vehicle_emergency",
                    "emergency_type": "breakdown_remote",
                    "response_type": "traffic_emergency"
                }
            },
            
            # Vehicle Fires
            {
                "title": "Vehicle Fire Emergency",
                "text": "Vehicle fire: Pull over immediately, turn off engine. Get everyone out of vehicle. Move away from vehicle - do not open hood. Call 911. Do not attempt to extinguish fire unless you have proper extinguisher and training.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "vehicle_emergency",
                    "emergency_type": "vehicle_fire",
                    "response_type": "fire_emergency"
                }
            },
            
            # Weather-Related Vehicle Emergencies
            {
                "title": "Vehicle in Flood Water",
                "text": "Vehicle in flood water: If water is rising, abandon vehicle immediately. Do not drive through flooded roads. If trapped in vehicle, climb to roof if possible. Call 911. Do not attempt to walk through flood water.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "vehicle_emergency",
                    "emergency_type": "flood_water",
                    "response_type": "weather_emergency"
                }
            },
            {
                "title": "Vehicle in Blizzard",
                "text": "Vehicle in blizzard: Pull over to safe location. Turn on hazard lights. Stay in vehicle - do not attempt to walk for help. Run engine for heat, but crack window for ventilation. Move around to stay warm. Signal for help with horn.",
                "category": "emergency",
                "metadata": {
                    "priority": "critical",
                    "source": "vehicle_emergency",
                    "emergency_type": "blizzard",
                    "response_type": "weather_emergency"
                }
            }
        ]
        
        self.knowledge_base.extend(vehicle_emergencies)
        logger.info(f"Added {len(vehicle_emergencies)} vehicle emergency procedures")
    
    def build_comprehensive_emergency_database(self):
        """Build the complete comprehensive emergency database"""
        logger.info("Building comprehensive emergency procedures database...")
        
        # Add emergency procedures in priority order
        self.add_medical_emergencies()
        self.add_natural_disaster_procedures()
        self.add_home_emergency_procedures()
        self.add_vehicle_emergency_procedures()
        
        logger.info(f"Built comprehensive emergency database with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_emergency_database(self, filename: str = None):
        """Save the emergency database to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_emergency_db_{timestamp}.json"
        
        filepath = os.path.join("data", "comprehensive_emergency", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved comprehensive emergency database to {filepath}")
        return filepath
    
    def get_emergency_stats(self):
        """Get statistics by emergency type"""
        emergency_types = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            emergency_type = entry['metadata'].get('source', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            emergency_types[emergency_type] = emergency_types.get(emergency_type, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return emergency_types, subcategories

def main():
    """Main function to build comprehensive emergency database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive emergency procedures database")
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
    
    # Build comprehensive emergency database
    builder = ComprehensiveEmergencyBuilder(location_config)
    emergency_database = builder.build_comprehensive_emergency_database()
    
    # Save to file
    filepath = builder.save_emergency_database(args.output)
    
    # Print statistics
    emergency_types, subcategories = builder.get_emergency_stats()
    
    print(f"\nComprehensive Emergency Database Statistics:")
    print(f"  Total entries: {len(emergency_database)}")
    print(f"  Emergency types:")
    for etype, count in sorted(emergency_types.items()):
        print(f"    - {etype}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    print(f"Location: {location_config['city']}, {location_config['state']}")
    
    # Show sample entries
    print(f"\nSample emergency procedures:")
    for i, entry in enumerate(emergency_database[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Type: {entry['metadata']['source']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
