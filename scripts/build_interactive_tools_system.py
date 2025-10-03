#!/usr/bin/env python3
"""
Interactive Tools System Builder
Creates comprehensive interactive tools and assessment systems
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveToolsSystemBuilder:
    """Builds comprehensive interactive tools system"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_emergency_preparedness_tools(self):
        """Add emergency preparedness checklists and tools"""
        emergency_preparedness_tools = [
            # Emergency Preparedness Checklists
            {
                "title": "Emergency Preparedness Checklist",
                "text": "Emergency Preparedness Checklist: 1) Emergency kit with 3-day supply of water (1 gallon per person), non-perishable food, first aid kit, flashlight, batteries, radio. 2) Important documents in waterproof container. 3) Family communication plan with meeting places. 4) Emergency contacts list. 5) Evacuation routes mapped. 6) Practice drills scheduled. Update kit every 6 months.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "critical",
                    "source": "interactive_tools",
                    "tool_category": "emergency_preparedness",
                    "subcategory": "preparedness_checklists",
                    "services": ["emergency_kit", "water_supply", "food_supply", "first_aid", "documents", "communication_plan", "evacuation_routes"],
                    "tool_type": "checklist",
                    "completion_time": "2_hours",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Tornado Preparedness Assessment",
                "text": "Tornado Preparedness Assessment: Rate your preparedness (1-5 scale): 1) Do you have a tornado shelter or safe room? 2) Do you know the difference between watch and warning? 3) Do you have a NOAA weather radio? 4) Do you have emergency supplies for 3 days? 5) Do you have a family communication plan? 6) Do you practice tornado drills? Score 25-30: Excellent, 20-24: Good, 15-19: Needs improvement, Below 15: Critical improvement needed.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "critical",
                    "source": "interactive_tools",
                    "tool_category": "emergency_preparedness",
                    "subcategory": "tornado_preparedness",
                    "services": ["tornado_shelter", "watch_vs_warning", "weather_radio", "emergency_supplies", "communication_plan", "practice_drills"],
                    "tool_type": "assessment",
                    "completion_time": "10_minutes",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Home Fire Safety Assessment",
                "text": "Home Fire Safety Assessment: Check each item (Yes/No): 1) Smoke detectors on every level and in every bedroom? 2) Smoke detectors tested monthly? 3) Fire extinguisher in kitchen? 4) Fire extinguisher near fireplace/furnace? 5) Escape plan with 2 exits from each room? 6) Escape plan practiced with family? 7) Clear pathways to exits? 8) Matches/lighters stored safely? 9) Electrical cords in good condition? 10) Space heaters 3 feet from flammable items? Score: 8-10: Excellent, 6-7: Good, 4-5: Needs improvement, Below 4: Critical improvement needed.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "emergency_preparedness",
                    "subcategory": "fire_safety_assessment",
                    "services": ["smoke_detectors", "fire_extinguishers", "escape_plans", "electrical_safety", "space_heater_safety"],
                    "tool_type": "assessment",
                    "completion_time": "15_minutes",
                    "response_type": "emergency_info"
                }
            },
            
            # Emergency Contact Tools
            {
                "title": "Emergency Contact Information Template",
                "text": "Emergency Contact Template: Create a comprehensive contact list including: 1) Family members (names, phone numbers, addresses). 2) Emergency services (911, police, fire, ambulance). 3) Medical contacts (doctors, pharmacies, insurance). 4) Utility companies (electric, gas, water, internet). 5) Insurance companies (home, auto, health). 6) Work contacts (employer, supervisor). 7) School contacts (children's schools). 8) Neighbors and nearby friends. Keep copies in wallet, car, and emergency kit. Update every 6 months.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "emergency_preparedness",
                    "subcategory": "contact_tools",
                    "services": ["family_contacts", "emergency_services", "medical_contacts", "utility_companies", "insurance_companies", "work_contacts"],
                    "tool_type": "template",
                    "completion_time": "30_minutes",
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Emergency Supply Calculator",
                "text": "Emergency Supply Calculator: Calculate supplies needed based on household size and duration. Water: 1 gallon per person per day (minimum 3 days). Food: Non-perishable items for 3 days minimum. Formula: Adults need 2,000 calories daily, children need 1,500-1,800 calories. Medications: 7-day supply minimum. Pet supplies: Food and water for 3 days per pet. Baby supplies: Formula, diapers, wipes for 3 days. Special needs: Medical equipment, oxygen, mobility aids. Update calculations annually or when household changes.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "emergency_preparedness",
                    "subcategory": "supply_calculator",
                    "services": ["water_calculation", "food_calculation", "medication_supply", "pet_supplies", "baby_supplies", "special_needs"],
                    "tool_type": "calculator",
                    "completion_time": "20_minutes",
                    "response_type": "emergency_info"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_preparedness_tools)
        logger.info(f"Added {len(emergency_preparedness_tools)} emergency preparedness tools entries")
    
    def add_home_safety_assessment_tools(self):
        """Add home safety assessment and improvement tools"""
        home_safety_tools = [
            # Home Safety Assessments
            {
                "title": "Comprehensive Home Safety Assessment",
                "text": "Home Safety Assessment: Evaluate your home safety (Yes/No for each): 1) All stairs have handrails? 2) All walkways are clear of clutter? 3) All rugs are secured with non-slip backing? 4) All electrical outlets have covers? 5) All cords are in good condition? 6) All smoke detectors work? 7) All carbon monoxide detectors work? 8) All windows open and close easily? 9) All doors lock properly? 10) All outdoor lighting works? Score: 9-10: Excellent, 7-8: Good, 5-6: Needs improvement, Below 5: Critical improvement needed.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "home_safety",
                    "subcategory": "comprehensive_assessment",
                    "services": ["stair_safety", "walkway_safety", "rug_safety", "electrical_safety", "detector_safety", "window_door_safety"],
                    "tool_type": "assessment",
                    "completion_time": "20_minutes",
                    "response_type": "safety_info"
                }
            },
            {
                "title": "Senior Home Safety Assessment",
                "text": "Senior Home Safety Assessment: Special considerations for seniors (Yes/No): 1) Grab bars in bathroom? 2) Non-slip mats in shower/tub? 3) Raised toilet seat if needed? 4) Shower chair if needed? 5) Good lighting in all areas? 6) Night lights in hallways? 7) Emergency response system? 8) Medications clearly labeled? 9) Easy-to-reach storage? 10) Clear emergency exits? 11) Sturdy step stools? 12) Cordless phones accessible? Score: 10-12: Excellent, 8-9: Good, 6-7: Needs improvement, Below 6: Critical improvement needed.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "home_safety",
                    "subcategory": "senior_safety",
                    "services": ["bathroom_safety", "lighting_safety", "emergency_systems", "medication_safety", "accessibility", "communication_safety"],
                    "tool_type": "assessment",
                    "completion_time": "25_minutes",
                    "response_type": "safety_info"
                }
            },
            {
                "title": "Child Safety Assessment",
                "text": "Child Safety Assessment: Childproofing checklist (Yes/No): 1) Safety gates on stairs? 2) Cabinet locks on dangerous items? 3) Outlet covers on all outlets? 4) Corner guards on sharp furniture? 5) Window guards on upper floors? 6) Blind cord safety devices? 7) Door knob covers on dangerous rooms? 8) Toilet locks if needed? 9) Appliance locks (stove, dishwasher)? 10) Furniture secured to walls? 11) Poison control number posted? 12) First aid kit accessible? Score: 10-12: Excellent, 8-9: Good, 6-7: Needs improvement, Below 6: Critical improvement needed.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "home_safety",
                    "subcategory": "child_safety",
                    "services": ["stair_safety", "cabinet_safety", "outlet_safety", "furniture_safety", "window_safety", "poison_safety"],
                    "tool_type": "assessment",
                    "completion_time": "30_minutes",
                    "response_type": "safety_info"
                }
            },
            
            # Home Improvement Tools
            {
                "title": "Home Safety Improvement Planner",
                "text": "Home Safety Improvement Planner: Prioritize improvements based on risk level and cost. High Priority (Do First): Smoke/carbon monoxide detectors, handrails on stairs, secure rugs, clear walkways, working locks. Medium Priority (Do Soon): Better lighting, grab bars in bathroom, outlet covers, window guards. Low Priority (Do When Possible): Security system, automatic lighting, smart home devices, aesthetic improvements. Budget: High priority items $100-500, Medium priority $200-800, Low priority $500-2000.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "home_safety",
                    "subcategory": "improvement_planner",
                    "services": ["priority_assessment", "risk_evaluation", "cost_estimation", "improvement_timeline", "budget_planning"],
                    "tool_type": "planner",
                    "completion_time": "45_minutes",
                    "response_type": "safety_info"
                }
            }
        ]
        
        self.knowledge_base.extend(home_safety_tools)
        logger.info(f"Added {len(home_safety_tools)} home safety assessment tools entries")
    
    def add_budget_planning_tools(self):
        """Add budget planning and financial management tools"""
        budget_planning_tools = [
            # Budget Creation Tools
            {
                "title": "Monthly Budget Calculator",
                "text": "Monthly Budget Calculator: Calculate your monthly budget using the 50/30/20 rule. 50% for needs (housing, utilities, food, transportation, minimum debt payments). 30% for wants (entertainment, dining out, hobbies, shopping). 20% for savings and debt repayment. Track all income sources (salary, benefits, side jobs). Track all expenses (fixed and variable). Use budgeting apps or spreadsheets. Review and adjust monthly. Emergency fund goal: 3-6 months of expenses.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "budget_planning",
                    "subcategory": "budget_calculator",
                    "services": ["income_tracking", "expense_tracking", "budget_allocation", "emergency_fund", "debt_repayment", "savings_planning"],
                    "tool_type": "calculator",
                    "completion_time": "60_minutes",
                    "response_type": "financial_info"
                }
            },
            {
                "title": "Emergency Fund Calculator",
                "text": "Emergency Fund Calculator: Calculate your emergency fund needs. Formula: Monthly expenses × 3-6 months. Include: housing, utilities, food, transportation, insurance, minimum debt payments, medical expenses. Start with $1,000 goal, then build to 3 months, then 6 months. High-risk jobs need 6 months, stable jobs need 3 months. Keep in high-yield savings account or money market account. Don't invest emergency fund in stocks or bonds.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "budget_planning",
                    "subcategory": "emergency_fund_calculator",
                    "services": ["expense_calculation", "risk_assessment", "savings_goals", "account_types", "investment_guidance"],
                    "tool_type": "calculator",
                    "completion_time": "30_minutes",
                    "response_type": "financial_info"
                }
            },
            {
                "title": "Debt Payoff Calculator",
                "text": "Debt Payoff Calculator: Calculate debt payoff strategies. List all debts (credit cards, loans, mortgages) with balances, interest rates, and minimum payments. Choose strategy: 1) Debt Snowball (pay minimums, extra to smallest balance). 2) Debt Avalanche (pay minimums, extra to highest interest rate). Calculate payoff time and total interest paid. Consider debt consolidation if rates are high. Track progress monthly. Celebrate milestones to stay motivated.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "budget_planning",
                    "subcategory": "debt_payoff_calculator",
                    "services": ["debt_listing", "strategy_comparison", "payoff_calculation", "consolidation_options", "progress_tracking"],
                    "tool_type": "calculator",
                    "completion_time": "45_minutes",
                    "response_type": "financial_info"
                }
            },
            
            # Expense Tracking Tools
            {
                "title": "Expense Tracking System",
                "text": "Expense Tracking System: Track all expenses for 30 days to understand spending patterns. Categories: Housing (rent, mortgage, utilities), Transportation (gas, insurance, maintenance), Food (groceries, dining out), Healthcare (insurance, medications, copays), Entertainment (movies, hobbies, subscriptions), Personal (clothing, personal care), Savings (emergency fund, retirement). Use apps, spreadsheets, or pen and paper. Review weekly to identify overspending areas.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "budget_planning",
                    "subcategory": "expense_tracking",
                    "services": ["expense_categorization", "spending_analysis", "pattern_identification", "overspending_detection", "budget_adjustment"],
                    "tool_type": "tracking_system",
                    "completion_time": "30_days",
                    "response_type": "financial_info"
                }
            },
            {
                "title": "Bill Payment Organizer",
                "text": "Bill Payment Organizer: Organize all recurring bills and payments. List: Bill name, amount, due date, payment method, account number. Set up automatic payments for fixed bills (rent, utilities, insurance). Set up reminders for variable bills (credit cards, medical bills). Use calendar or app reminders. Consider bill payment services. Keep records of all payments. Review bills for errors or unnecessary charges.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "budget_planning",
                    "subcategory": "bill_organizer",
                    "services": ["bill_listing", "automatic_payments", "payment_reminders", "record_keeping", "bill_review"],
                    "tool_type": "organizer",
                    "completion_time": "60_minutes",
                    "response_type": "financial_info"
                }
            }
        ]
        
        self.knowledge_base.extend(budget_planning_tools)
        logger.info(f"Added {len(budget_planning_tools)} budget planning tools entries")
    
    def add_health_questionnaires(self):
        """Add health questionnaires and assessment tools"""
        health_questionnaires = [
            # Health Risk Assessments
            {
                "title": "Health Risk Assessment Questionnaire",
                "text": "Health Risk Assessment: Answer questions to assess health risks. 1) Do you smoke or use tobacco? 2) Do you drink alcohol? If yes, how many drinks per week? 3) Do you exercise regularly (150 minutes moderate activity weekly)? 4) Do you eat 5+ servings fruits/vegetables daily? 5) Do you get 7-9 hours sleep nightly? 6) Do you manage stress effectively? 7) Do you maintain healthy weight? 8) Do you get regular checkups? 9) Do you take medications as prescribed? 10) Do you have family history of heart disease, diabetes, or cancer? Score and get personalized recommendations.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "health_questionnaires",
                    "subcategory": "health_risk_assessment",
                    "services": ["smoking_assessment", "alcohol_assessment", "exercise_assessment", "nutrition_assessment", "sleep_assessment", "stress_assessment"],
                    "tool_type": "questionnaire",
                    "completion_time": "15_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Mental Health Screening Questionnaire",
                "text": "Mental Health Screening: Answer questions about mental health (Past 2 weeks): 1) Little interest or pleasure in doing things? 2) Feeling down, depressed, or hopeless? 3) Trouble falling or staying asleep, or sleeping too much? 4) Feeling tired or having little energy? 5) Poor appetite or overeating? 6) Feeling bad about yourself or feeling like a failure? 7) Trouble concentrating on things? 8) Moving or speaking slowly, or being fidgety? 9) Thoughts of hurting yourself? Score: 0-4: Minimal depression, 5-9: Mild depression, 10-14: Moderate depression, 15-19: Moderately severe depression, 20-27: Severe depression. Seek professional help if score 10+.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "health_questionnaires",
                    "subcategory": "mental_health_screening",
                    "services": ["depression_screening", "anxiety_assessment", "sleep_assessment", "energy_assessment", "concentration_assessment", "suicide_risk"],
                    "tool_type": "questionnaire",
                    "completion_time": "10_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Senior Health Assessment",
                "text": "Senior Health Assessment: Questions for seniors (Yes/No): 1) Do you have difficulty with daily activities? 2) Do you have memory problems? 3) Do you have vision or hearing problems? 4) Do you have balance or mobility issues? 5) Do you take 5+ medications? 6) Do you have chronic health conditions? 7) Do you have social support? 8) Do you have transportation to medical appointments? 9) Do you have adequate nutrition? 10) Do you have safe housing? 11) Do you have advance directives? 12) Do you have emergency contacts? Score and get recommendations for senior services.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "health_questionnaires",
                    "subcategory": "senior_health_assessment",
                    "services": ["daily_activities", "memory_assessment", "sensory_assessment", "mobility_assessment", "medication_management", "social_support"],
                    "tool_type": "questionnaire",
                    "completion_time": "20_minutes",
                    "response_type": "health_info"
                }
            },
            
            # Medication Management Tools
            {
                "title": "Medication Management Assessment",
                "text": "Medication Management Assessment: Questions about medications (Yes/No): 1) Do you take medications as prescribed? 2) Do you understand what each medication does? 3) Do you know the side effects of your medications? 4) Do you have a medication list with doses and times? 5) Do you use a pill organizer? 6) Do you take medications with or without food as directed? 7) Do you avoid alcohol with medications that interact? 8) Do you store medications properly? 9) Do you dispose of expired medications safely? 10) Do you tell all doctors about all medications? Score and get medication management tips.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "health_questionnaires",
                    "subcategory": "medication_management",
                    "services": ["medication_adherence", "medication_understanding", "side_effects", "medication_list", "pill_organizer", "storage_safety"],
                    "tool_type": "questionnaire",
                    "completion_time": "15_minutes",
                    "response_type": "health_info"
                }
            },
            {
                "title": "Nutrition Assessment Tool",
                "text": "Nutrition Assessment: Questions about eating habits (Yes/No): 1) Do you eat breakfast daily? 2) Do you eat 5+ servings fruits/vegetables daily? 3) Do you limit processed foods? 4) Do you drink 8+ glasses water daily? 5) Do you limit sugary drinks? 6) Do you eat whole grains? 7) Do you limit sodium intake? 8) Do you eat lean proteins? 9) Do you limit saturated fats? 10) Do you take vitamins if recommended? 11) Do you read nutrition labels? 12) Do you cook meals at home? Score and get personalized nutrition recommendations.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "health_questionnaires",
                    "subcategory": "nutrition_assessment",
                    "services": ["meal_patterns", "fruit_vegetable_intake", "processed_foods", "hydration", "sugar_intake", "whole_grains"],
                    "tool_type": "questionnaire",
                    "completion_time": "15_minutes",
                    "response_type": "health_info"
                }
            }
        ]
        
        self.knowledge_base.extend(health_questionnaires)
        logger.info(f"Added {len(health_questionnaires)} health questionnaires entries")
    
    def add_community_resource_finder(self):
        """Add community resource finding and matching tools"""
        community_resource_tools = [
            # Resource Matching Tools
            {
                "title": "Community Resource Matching Tool",
                "text": "Community Resource Matching: Answer questions to find relevant resources. 1) What type of help do you need? (Food, housing, healthcare, employment, education, legal, mental health, transportation). 2) What is your income level? (Below poverty line, low income, moderate income, higher income). 3) Do you have insurance? (Medicaid, Medicare, private insurance, no insurance). 4) Do you have transportation? (Yes, limited, no). 5) What is your preferred language? (English, Spanish, other). 6) Do you need immediate help or ongoing services? Get personalized list of available resources.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "community_resources",
                    "subcategory": "resource_matching",
                    "services": ["help_type_assessment", "income_level_matching", "insurance_matching", "transportation_matching", "language_matching", "urgency_assessment"],
                    "tool_type": "matching_tool",
                    "completion_time": "10_minutes",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Emergency Assistance Eligibility Checker",
                "text": "Emergency Assistance Eligibility: Check eligibility for emergency assistance programs. Questions: 1) What is your household size? 2) What is your monthly income? 3) Do you have any savings? 4) What is your current crisis? (Job loss, medical emergency, natural disaster, domestic violence, eviction, utility shutoff). 5) Do you have children under 18? 6) Are you over 65 or disabled? 7) Do you have a documented emergency? Get list of programs you may qualify for including SNAP, emergency rental assistance, utility assistance, food pantries, and other emergency services.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "high",
                    "source": "interactive_tools",
                    "tool_category": "community_resources",
                    "subcategory": "eligibility_checker",
                    "services": ["household_assessment", "income_verification", "crisis_type_identification", "program_eligibility", "emergency_services"],
                    "tool_type": "eligibility_tool",
                    "completion_time": "15_minutes",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Healthcare Provider Finder",
                "text": "Healthcare Provider Finder: Find healthcare providers based on your needs. Questions: 1) What type of care do you need? (Primary care, specialist, mental health, dental, vision, urgent care). 2) Do you have insurance? (Medicaid, Medicare, private insurance, no insurance). 3) What is your preferred language? (English, Spanish, other). 4) Do you need evening or weekend hours? 5) Do you need transportation assistance? 6) Do you need sliding fee scale? 7) What area of Wichita do you prefer? Get list of providers with contact information, hours, services, and insurance accepted.",
                "category": "interactive_tools",
                "metadata": {
                    "priority": "medium",
                    "source": "interactive_tools",
                    "tool_category": "community_resources",
                    "subcategory": "provider_finder",
                    "services": ["care_type_matching", "insurance_matching", "language_matching", "hours_matching", "location_matching", "fee_structure_matching"],
                    "tool_type": "finder_tool",
                    "completion_time": "10_minutes",
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(community_resource_tools)
        logger.info(f"Added {len(community_resource_tools)} community resource tools entries")
    
    def build_interactive_tools_system(self):
        """Build the complete interactive tools system"""
        logger.info("Building comprehensive interactive tools system...")
        
        # Add interactive tools in priority order
        self.add_emergency_preparedness_tools()
        self.add_home_safety_assessment_tools()
        self.add_budget_planning_tools()
        self.add_health_questionnaires()
        self.add_community_resource_finder()
        
        logger.info(f"Built interactive tools system with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_interactive_tools_system(self, filename: str = None):
        """Save the interactive tools system to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interactive_tools_system_{timestamp}.json"
        
        filepath = os.path.join("data", "interactive_tools", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved interactive tools system to {filepath}")
        return filepath
    
    def get_interactive_tools_stats(self):
        """Get statistics by tool category and subcategory"""
        tool_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            tool_category = entry['metadata'].get('tool_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            tool_categories[tool_category] = tool_categories.get(tool_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return tool_categories, subcategories

def main():
    """Main function to build interactive tools system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive interactive tools system")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build interactive tools system
    builder = InteractiveToolsSystemBuilder()
    interactive_tools_system = builder.build_interactive_tools_system()
    
    # Save to file
    filepath = builder.save_interactive_tools_system(args.output)
    
    # Print statistics
    tool_categories, subcategories = builder.get_interactive_tools_stats()
    
    print(f"\nInteractive Tools System Statistics:")
    print(f"  Total entries: {len(interactive_tools_system)}")
    print(f"  Tool categories:")
    for category, count in sorted(tool_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample interactive tools entries:")
    for i, entry in enumerate(interactive_tools_system[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Tool Category: {entry['metadata']['tool_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
