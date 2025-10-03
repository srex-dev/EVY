#!/usr/bin/env python3
"""
Legal & Regulatory Information System Builder
Creates comprehensive legal and regulatory information database
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalRegulatorySystemBuilder:
    """Builds comprehensive legal and regulatory information system"""
    
    def __init__(self):
        self.knowledge_base = []
        
    def add_emergency_legal_situations(self):
        """Add emergency legal situation information"""
        emergency_legal = [
            # Domestic Violence
            {
                "title": "Domestic Violence Emergency Response",
                "text": "Domestic Violence Emergency: Call 911 immediately if in danger. Kansas Domestic Violence Hotline: 1-888-END-ABUSE (1-888-363-2287). Seek safe shelter, document injuries, preserve evidence. Protection orders available through courts.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "critical",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "domestic_violence",
                    "services": ["emergency_response", "hotline", "protection_orders", "shelter"],
                    "response_type": "emergency_info"
                }
            },
            {
                "title": "Protection Order Process",
                "text": "Protection Orders: Available through Sedgwick County District Court. File at 525 N Main St, Wichita, KS 67203. Emergency protection orders available 24/7. Free legal assistance through Kansas Legal Services. Process typically takes 1-2 hours.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "protection_orders",
                    "services": ["court_filing", "emergency_orders", "legal_assistance"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Child Abuse
            {
                "title": "Child Abuse Reporting",
                "text": "Child Abuse: Call 911 immediately for emergency situations. Kansas Child Abuse Hotline: 1-800-922-5330. Report suspected abuse to law enforcement or Department for Children and Families. Mandatory reporters include teachers, healthcare workers, clergy.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "critical",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "child_abuse",
                    "services": ["emergency_response", "hotline", "reporting", "mandatory_reporters"],
                    "response_type": "emergency_info"
                }
            },
            
            # Elder Abuse
            {
                "title": "Elder Abuse Reporting",
                "text": "Elder Abuse: Call 911 for emergencies. Kansas Adult Protective Services: 1-800-922-5330. Report physical, emotional, financial abuse or neglect of adults 60+. Free investigation and protective services available.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "critical",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "elder_abuse",
                    "services": ["emergency_response", "protective_services", "investigation"],
                    "response_type": "emergency_info"
                }
            },
            
            # Identity Theft
            {
                "title": "Identity Theft Response",
                "text": "Identity Theft: Contact police immediately, file report. Contact credit bureaus to place fraud alerts. Contact banks and credit card companies. File complaint with FTC: identitytheft.gov. Keep detailed records of all communications and actions taken.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "identity_theft",
                    "services": ["police_report", "fraud_alerts", "ftc_complaint", "record_keeping"],
                    "response_type": "emergency_info"
                }
            },
            
            # Arrest Rights
            {
                "title": "Rights During Arrest",
                "text": "Arrest Rights: Right to remain silent, right to attorney, right to make phone call. Do not resist arrest. Ask for attorney immediately. Do not answer questions without attorney present. Request written copy of charges.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "critical",
                    "source": "legal_regulatory",
                    "legal_category": "emergency_legal",
                    "subcategory": "arrest_rights",
                    "services": ["right_to_silence", "right_to_attorney", "phone_call", "written_charges"],
                    "response_type": "emergency_info"
                }
            }
        ]
        
        self.knowledge_base.extend(emergency_legal)
        logger.info(f"Added {len(emergency_legal)} emergency legal situation entries")
    
    def add_civil_rights_and_discrimination(self):
        """Add civil rights and discrimination information"""
        civil_rights = [
            # Discrimination
            {
                "title": "Employment Discrimination",
                "text": "Employment Discrimination: Illegal based on race, color, religion, sex, national origin, age, disability. File complaint with Equal Employment Opportunity Commission (EEOC) within 180 days. Kansas Human Rights Commission: (316) 337-6276.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "civil_rights",
                    "subcategory": "employment_discrimination",
                    "services": ["eeoc_complaint", "kansas_human_rights", "legal_protection"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Housing Discrimination",
                "text": "Housing Discrimination: Illegal based on race, color, religion, sex, national origin, familial status, disability. File complaint with Department of Housing and Urban Development (HUD) within 1 year. Fair Housing Center: (316) 263-3300.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "civil_rights",
                    "subcategory": "housing_discrimination",
                    "services": ["hud_complaint", "fair_housing_center", "legal_protection"],
                    "response_type": "service_info"
                }
            },
            
            # Disability Rights
            {
                "title": "Americans with Disabilities Act (ADA)",
                "text": "ADA Rights: Protection against discrimination in employment, public accommodations, transportation, telecommunications. Reasonable accommodations required. File complaint with Department of Justice or EEOC. Disability Rights Center: (316) 263-5151.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "civil_rights",
                    "subcategory": "disability_rights",
                    "services": ["ada_protection", "reasonable_accommodations", "complaint_filing"],
                    "response_type": "service_info"
                }
            },
            
            # Voting Rights
            {
                "title": "Voting Rights and Registration",
                "text": "Voting Rights: Register to vote at age 18, US citizen, Kansas resident. Register online, by mail, or in person. Photo ID required to vote. Early voting available. Absentee voting for qualifying circumstances. Sedgwick County Election Office: (316) 660-7100.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "civil_rights",
                    "subcategory": "voting_rights",
                    "services": ["voter_registration", "photo_id", "early_voting", "absentee_voting"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(civil_rights)
        logger.info(f"Added {len(civil_rights)} civil rights and discrimination entries")
    
    def add_family_law(self):
        """Add family law information"""
        family_law = [
            # Divorce
            {
                "title": "Divorce Process in Kansas",
                "text": "Divorce in Kansas: File petition in county where you live. Residency requirement: 60 days. Grounds include incompatibility, failure to perform marital duty, abandonment. Mediation available. Child custody, support, property division addressed.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "family_law",
                    "subcategory": "divorce",
                    "services": ["petition_filing", "mediation", "custody", "support", "property_division"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Child Custody and Support",
                "text": "Child Custody: Best interests of child standard. Joint or sole custody, visitation schedules. Child support based on Kansas Child Support Guidelines. Modification possible with changed circumstances. Enforcement through court orders.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "family_law",
                    "subcategory": "child_custody",
                    "services": ["custody_determination", "visitation", "support_calculation", "modification", "enforcement"],
                    "response_type": "service_info"
                }
            },
            
            # Adoption
            {
                "title": "Adoption Process",
                "text": "Adoption in Kansas: Private adoption, agency adoption, stepparent adoption, foster care adoption. Home study required. Consent from biological parents or termination of parental rights. Court approval required. Adoption subsidies available for special needs children.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "family_law",
                    "subcategory": "adoption",
                    "services": ["adoption_types", "home_study", "consent", "court_approval", "subsidies"],
                    "response_type": "service_info"
                }
            },
            
            # Guardianship
            {
                "title": "Guardianship and Conservatorship",
                "text": "Guardianship: Legal authority to make decisions for incapacitated adult or minor child. Conservatorship for financial decisions. Court appointment required. Annual reports required. Limited guardianship available for specific needs.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "family_law",
                    "subcategory": "guardianship",
                    "services": ["court_appointment", "decision_making", "annual_reports", "limited_guardianship"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(family_law)
        logger.info(f"Added {len(family_law)} family law entries")
    
    def add_housing_and_landlord_tenant(self):
        """Add housing and landlord-tenant law information"""
        housing_law = [
            # Landlord-Tenant Rights
            {
                "title": "Landlord-Tenant Rights",
                "text": "Landlord-Tenant Rights: Written lease recommended. Security deposit limited to 1.5 months rent. 30-day notice for month-to-month tenancy. Landlord must maintain habitable premises. Tenant has right to quiet enjoyment. Eviction requires court order.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "housing_law",
                    "subcategory": "landlord_tenant",
                    "services": ["lease_agreements", "security_deposits", "notice_requirements", "habitable_premises", "eviction_process"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Eviction Process",
                "text": "Eviction Process: Landlord must give proper notice (3-day for non-payment, 30-day for other violations). If tenant doesn't leave, landlord files eviction lawsuit. Court hearing required. Sheriff enforces eviction order. Tenant has right to defend.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "housing_law",
                    "subcategory": "eviction",
                    "services": ["proper_notice", "eviction_lawsuit", "court_hearing", "sheriff_enforcement", "tenant_defense"],
                    "response_type": "service_info"
                }
            },
            
            # Housing Assistance
            {
                "title": "Housing Assistance Programs",
                "text": "Housing Assistance: Section 8 vouchers through Wichita Housing Authority, emergency rental assistance, utility assistance, weatherization programs. Income limits apply. Waiting lists for some programs. Contact: (316) 263-3300.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "housing_law",
                    "subcategory": "housing_assistance",
                    "services": ["section_8", "rental_assistance", "utility_assistance", "weatherization"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Foreclosure
            {
                "title": "Foreclosure Prevention",
                "text": "Foreclosure Prevention: Contact lender immediately if behind on payments. Loan modification, forbearance, short sale options available. HUD-approved housing counselors provide free assistance. Foreclosure process takes 4-6 months in Kansas.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "housing_law",
                    "subcategory": "foreclosure",
                    "services": ["lender_contact", "loan_modification", "forbearance", "short_sale", "housing_counselors"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(housing_law)
        logger.info(f"Added {len(housing_law)} housing and landlord-tenant entries")
    
    def add_consumer_protection(self):
        """Add consumer protection information"""
        consumer_protection = [
            # Consumer Rights
            {
                "title": "Consumer Rights and Protection",
                "text": "Consumer Rights: Right to fair and honest business practices, accurate advertising, safe products. Right to cancel certain contracts within 3 days. File complaints with Kansas Attorney General, Better Business Bureau, FTC.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "consumer_protection",
                    "subcategory": "consumer_rights",
                    "services": ["fair_practices", "accurate_advertising", "safe_products", "contract_cancellation", "complaint_filing"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "Debt Collection Rights",
                "text": "Debt Collection Rights: Collectors cannot call before 8AM or after 9PM, use abusive language, threaten arrest, contact you at work if told not to. Right to request debt validation. Can request collector to stop calling.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "consumer_protection",
                    "subcategory": "debt_collection",
                    "services": ["call_restrictions", "validation_rights", "stop_calling", "abuse_protection"],
                    "response_type": "service_info"
                }
            },
            
            # Bankruptcy
            {
                "title": "Bankruptcy Information",
                "text": "Bankruptcy: Chapter 7 (liquidation) and Chapter 13 (repayment plan) available. Credit counseling required before filing. Automatic stay stops collection actions. Some debts not dischargeable (student loans, child support, taxes).",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "consumer_protection",
                    "subcategory": "bankruptcy",
                    "services": ["chapter_7", "chapter_13", "credit_counseling", "automatic_stay", "dischargeable_debts"],
                    "response_type": "service_info"
                }
            },
            
            # Scams and Fraud
            {
                "title": "Common Scams and Fraud Prevention",
                "text": "Scam Prevention: Never give personal information to unsolicited callers. Be wary of too-good-to-be-true offers. Verify businesses before paying. Report scams to Kansas Attorney General, FTC, local police. Freeze credit reports if identity compromised.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "consumer_protection",
                    "subcategory": "scam_prevention",
                    "services": ["information_protection", "offer_verification", "business_verification", "scam_reporting", "credit_freeze"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(consumer_protection)
        logger.info(f"Added {len(consumer_protection)} consumer protection entries")
    
    def add_criminal_law(self):
        """Add criminal law information"""
        criminal_law = [
            # Criminal Process
            {
                "title": "Criminal Process Overview",
                "text": "Criminal Process: Arrest, booking, initial appearance, preliminary hearing, arraignment, trial, sentencing. Right to attorney at all stages. Bail/bond may be set. Plea bargains possible. Appeals available for convictions.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "criminal_law",
                    "subcategory": "criminal_process",
                    "services": ["right_to_attorney", "bail_bond", "plea_bargains", "appeals"],
                    "response_type": "service_info"
                }
            },
            {
                "title": "DUI/DWI Laws",
                "text": "DUI/DWI: Illegal to drive with BAC 0.08% or higher (0.02% for under 21). Penalties include license suspension, fines, jail time, mandatory classes. Ignition interlock may be required. Refusal to test results in license suspension.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "criminal_law",
                    "subcategory": "dui_dwi",
                    "services": ["bac_limits", "penalties", "license_suspension", "ignition_interlock", "test_refusal"],
                    "response_type": "service_info"
                }
            },
            
            # Expungement
            {
                "title": "Record Expungement",
                "text": "Record Expungement: Eligible for certain non-violent offenses after waiting period (3-5 years). Process involves petition to court, background check, hearing. Expunged records removed from public view. Not available for all offenses.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "low",
                    "source": "legal_regulatory",
                    "legal_category": "criminal_law",
                    "subcategory": "expungement",
                    "services": ["eligibility", "waiting_period", "court_petition", "background_check", "hearing"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(criminal_law)
        logger.info(f"Added {len(criminal_law)} criminal law entries")
    
    def add_legal_resources(self):
        """Add legal resources and assistance information"""
        legal_resources = [
            # Legal Aid
            {
                "title": "Kansas Legal Services",
                "text": "Kansas Legal Services: Free legal help for low-income residents. Family law, housing, consumer issues, public benefits, employment. Income limits apply. Contact: (316) 263-8950. Offices in Wichita and surrounding areas.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "high",
                    "source": "legal_regulatory",
                    "legal_category": "legal_resources",
                    "subcategory": "legal_aid",
                    "services": ["free_legal_help", "family_law", "housing", "consumer", "public_benefits"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Wichita Bar Association Lawyer Referral",
                "text": "Lawyer Referral: Wichita Bar Association provides referrals to qualified attorneys. Initial consultation fee may apply. Specialized practice areas available. Contact: (316) 263-2251. Can help find appropriate attorney for your needs.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "legal_resources",
                    "subcategory": "lawyer_referral",
                    "services": ["attorney_referrals", "consultations", "specialized_practice"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            
            # Court Information
            {
                "title": "Sedgwick County Court System",
                "text": "Sedgwick County Courts: District Court at 525 N Main St, Wichita, KS 67203. Civil, criminal, family, probate cases. Court records available online. Self-help center for pro se litigants. Filing fees vary by case type.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "legal_resources",
                    "subcategory": "court_system",
                    "services": ["civil_court", "criminal_court", "family_court", "probate_court", "self_help_center"],
                    "location": "Wichita, KS",
                    "response_type": "service_info"
                }
            },
            {
                "title": "Small Claims Court",
                "text": "Small Claims Court: For disputes under $4,000. Simplified process, no attorneys required. Filing fee around $50. Mediation available. Judgment can be enforced through garnishment, liens, property seizure.",
                "category": "legal_regulatory",
                "metadata": {
                    "priority": "medium",
                    "source": "legal_regulatory",
                    "legal_category": "legal_resources",
                    "subcategory": "small_claims",
                    "services": ["dispute_resolution", "simplified_process", "mediation", "judgment_enforcement"],
                    "response_type": "service_info"
                }
            }
        ]
        
        self.knowledge_base.extend(legal_resources)
        logger.info(f"Added {len(legal_resources)} legal resources entries")
    
    def build_legal_regulatory_system(self):
        """Build the complete legal and regulatory information system"""
        logger.info("Building comprehensive legal and regulatory information system...")
        
        # Add legal information in priority order
        self.add_emergency_legal_situations()
        self.add_civil_rights_and_discrimination()
        self.add_family_law()
        self.add_housing_and_landlord_tenant()
        self.add_consumer_protection()
        self.add_criminal_law()
        self.add_legal_resources()
        
        logger.info(f"Built legal and regulatory system with {len(self.knowledge_base)} entries")
        return self.knowledge_base
    
    def save_legal_regulatory_system(self, filename: str = None):
        """Save the legal and regulatory system to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"legal_regulatory_system_{timestamp}.json"
        
        filepath = os.path.join("data", "legal_regulatory", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        
        logger.info(f"Saved legal and regulatory system to {filepath}")
        return filepath
    
    def get_legal_stats(self):
        """Get statistics by legal category and subcategory"""
        legal_categories = {}
        subcategories = {}
        
        for entry in self.knowledge_base:
            legal_category = entry['metadata'].get('legal_category', 'unknown')
            subcategory = entry['metadata'].get('subcategory', 'general')
            
            legal_categories[legal_category] = legal_categories.get(legal_category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        return legal_categories, subcategories

def main():
    """Main function to build legal and regulatory information system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build comprehensive legal and regulatory information system")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    # Build legal and regulatory system
    builder = LegalRegulatorySystemBuilder()
    legal_system = builder.build_legal_regulatory_system()
    
    # Save to file
    filepath = builder.save_legal_regulatory_system(args.output)
    
    # Print statistics
    legal_categories, subcategories = builder.get_legal_stats()
    
    print(f"\nLegal & Regulatory Information System Statistics:")
    print(f"  Total entries: {len(legal_system)}")
    print(f"  Legal categories:")
    for category, count in sorted(legal_categories.items()):
        print(f"    - {category}: {count} entries")
    
    print(f"  Subcategories:")
    for subcat, count in sorted(subcategories.items()):
        print(f"    - {subcat}: {count} entries")
    
    print(f"\nSaved to: {filepath}")
    
    # Show sample entries
    print(f"\nSample legal and regulatory entries:")
    for i, entry in enumerate(legal_system[:5]):
        print(f"  {i+1}. {entry['title']}")
        print(f"     Category: {entry['category']}")
        print(f"     Legal Category: {entry['metadata']['legal_category']}")
        print(f"     Priority: {entry['metadata']['priority']}")
        print(f"     Text: {entry['text'][:80]}...")
        print()

if __name__ == "__main__":
    main()
