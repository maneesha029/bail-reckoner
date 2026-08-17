#!/usr/bin/env python3
"""
Generate realistic synthetic bail cases for testing purposes.

IMPORTANT: RTI REQUESTS REJECTED
Both NCRB (central) and state prison department RTI requests were rejected.
Data is not available through RTI channels due to privacy concerns.

Therefore, we are proceeding with SYNTHETIC DATA GENERATION ONLY.

All records in synthetic_cases.json are clearly labeled:
    "_data_label": "SYNTHETIC — not real prisoner data"

Synthetic data is grounded in publicly available NCRB Prison Statistics reports
and provides realistic distributions for testing all bail monitoring logic.

For production deployment, institutions must establish a formal data-sharing
agreement (not through RTI).

---

This script creates ~100 synthetic undertrial prisoner cases modeled on
real NCRB (National Crime Records Bureau) distributions. All records are
clearly labeled as SYNTHETIC for clarity.

Time Complexity: O(n) where n is number of cases
Space Complexity: O(n) for storing all cases in memory
(acceptable for ~100 records, ~2MB JSON output)
"""

import json
import random
from datetime import datetime, timedelta
import uuid
import os

# Offense categories matching shared_schemas
OFFENSE_CATEGORIES = [
    "cyber_crimes",
    "crimes_against_sc_st",
    "crimes_against_women",
    "crimes_against_children",
    "offences_against_state",
    "economic_offences",
    "crimes_against_foreigners",
    "general"
]

# Indian states for realistic distribution (weighted by prison population)
STATES_WEIGHTED = {
    "Karnataka": 0.12,
    "Maharashtra": 0.14,
    "Tamil Nadu": 0.10,
    "Uttar Pradesh": 0.11,
    "Delhi": 0.08,
    "West Bengal": 0.09,
    "Telangana": 0.07,
    "Punjab": 0.06,
    "Gujarat": 0.06,
    "Madhya Pradesh": 0.05,
    "Rajasthan": 0.05,
    "Bihar": 0.04,
    "Haryana": 0.03,
}

# Major districts (simplified for realism)
DISTRICTS = {
    "Karnataka": ["Bengaluru", "Mysuru", "Tumkur", "Kolar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Aurangabad"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi"],
    "West Bengal": ["Kolkata", "Howrah", "Jalpaiguri"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Punjab": ["Amritsar", "Ludhiana", "Jalandhar"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota"],
    "Bihar": ["Patna", "Gaya", "Madhubani"],
    "Haryana": ["Faridabad", "Gurgaon", "Hisar"],
}

# IPC/BNS offense data (state → section → max_sentence_months, is_compoundable)
# Simplified examples; in production, source from India Code (indiacode.nic.in)
OFFENSE_DATA = {
    "cyber_crimes": [
        {"section": "66C", "max_months": 24, "compoundable": False, "act": "IT_Act"},
        {"section": "66D", "max_months": 36, "compoundable": False, "act": "IT_Act"},
        {"section": "66E", "max_months": 24, "compoundable": False, "act": "IT_Act"},
    ],
    "crimes_against_sc_st": [
        {"section": "3", "max_months": 60, "compoundable": False, "act": "SC_ST_Act"},
        {"section": "4", "max_months": 72, "compoundable": False, "act": "SC_ST_Act"},
    ],
    "crimes_against_women": [
        {"section": "498A", "max_months": 36, "compoundable": True, "act": "IPC"},
        {"section": "376", "max_months": 120, "compoundable": False, "act": "IPC"},
    ],
    "crimes_against_children": [
        {"section": "3", "max_months": 120, "compoundable": False, "act": "POCSO"},
        {"section": "4", "max_months": 120, "compoundable": False, "act": "POCSO"},
    ],
    "offences_against_state": [
        {"section": "121", "max_months": 120, "compoundable": False, "act": "IPC"},
        {"section": "153A", "max_months": 60, "compoundable": False, "act": "IPC"},
    ],
    "economic_offences": [
        {"section": "420", "max_months": 84, "compoundable": False, "act": "IPC"},
        {"section": "406", "max_months": 60, "compoundable": False, "act": "IPC"},
        {"section": "4", "max_months": 120, "compoundable": False, "act": "PMLA"},
    ],
    "crimes_against_foreigners": [
        {"section": "154", "max_months": 60, "compoundable": False, "act": "IPC"},
    ],
    "general": [
        {"section": "307", "max_months": 120, "compoundable": False, "act": "IPC"},
        {"section": "336", "max_months": 12, "compoundable": True, "act": "IPC"},
    ],
}


def generate_custody_start_date():
    """
    Generate a realistic custody start date.
    
    Most undertrial prisoners have been in custody 6-24 months.
    Some are recent (within 3 months), some are older (3+ years).
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    today = datetime.now()
    
    # Weighted distribution
    rand = random.random()
    if rand < 0.15:  # 15% recent (0-3 months)
        days_ago = random.randint(1, 90)
    elif rand < 0.50:  # 50% medium (3-12 months)
        days_ago = random.randint(91, 365)
    elif rand < 0.80:  # 30% long-term (1-2 years)
        days_ago = random.randint(366, 730)
    else:  # 5% very long-term (2-4 years)
        days_ago = random.randint(731, 1460)
    
    return (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_charge():
    """
    Generate a single charge for a case.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    category = random.choice(OFFENSE_CATEGORIES)
    offense = random.choice(OFFENSE_DATA[category])
    
    return {
        "act": offense["act"],
        "section": offense["section"],
        "offense_category": category,
        "is_compoundable": offense["compoundable"],
        "max_sentence_months": offense["max_months"],
    }


def generate_case(case_number):
    """
    Generate a single synthetic case.
    
    Time Complexity: O(1) (constant number of charges per case)
    Space Complexity: O(1) (fixed-size output)
    """
    # Select state weighted by prison population
    state = random.choices(
        list(STATES_WEIGHTED.keys()),
        weights=list(STATES_WEIGHTED.values()),
        k=1
    )[0]
    
    district = random.choice(DISTRICTS.get(state, [state]))
    
    # Generate 1-2 charges per case (realistic)
    num_charges = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
    charges = [generate_charge() for _ in range(num_charges)]
    
    # Custody dates
    custody_start = generate_custody_start_date()
    
    # First-time offender: ~60% of undertrials
    is_first_time = random.choices([True, False], weights=[0.6, 0.4], k=1)[0]
    
    # Legal aid: ~65% of undertrials have legal aid
    has_legal_aid = random.choices([True, False], weights=[0.65, 0.35], k=1)[0]
    
    # Case stage: most are under_trial, some have bail_applied or bail_granted
    case_stage_rand = random.random()
    if case_stage_rand < 0.70:
        case_stage = "under_trial"
    elif case_stage_rand < 0.85:
        case_stage = "bail_applied"
    else:
        case_stage = "bail_granted"
    
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return {
        "_data_label": "SYNTHETIC — not real prisoner data",
        "case_id": str(uuid.uuid4()),
        "prisoner_id": f"PRIS-{datetime.now().year}-{case_number:05d}",
        "charges": charges,
        "custody_start_date": custody_start,
        "is_first_time_offender": is_first_time,
        "state": state,
        "district": district,
        "case_stage": case_stage,
        "has_legal_aid": has_legal_aid,
        "created_at": now_iso,
        "updated_at": now_iso,
    }


def generate_synthetic_cases(num_cases=100):
    """
    Generate a batch of synthetic cases.
    
    Time Complexity: O(n) where n = num_cases
    Space Complexity: O(n) for storing all cases
    
    Args:
        num_cases: Number of synthetic cases to generate (default 100)
    
    Returns:
        List of case dictionaries
    """
    print(f"Generating {num_cases} synthetic bail cases for testing...")
    
    cases = [generate_case(i + 1) for i in range(num_cases)]
    
    return cases


def calculate_statistics(cases):
    """
    Calculate statistics about generated cases for verification.
    
    Time Complexity: O(n)
    Space Complexity: O(1) — only storing aggregate counts
    
    Args:
        cases: List of case dictionaries
    
    Returns:
        Dict of statistics
    """
    stats = {
        "total_cases": len(cases),
        "offense_categories": {},
        "case_stages": {},
        "states": {},
        "first_time_offenders": 0,
        "with_legal_aid": 0,
    }
    
    for case in cases:
        # Count by offense category
        for charge in case["charges"]:
            category = charge["offense_category"]
            stats["offense_categories"][category] = stats["offense_categories"].get(category, 0) + 1
        
        # Count by case stage
        stage = case["case_stage"]
        stats["case_stages"][stage] = stats["case_stages"].get(stage, 0) + 1
        
        # Count by state
        state = case["state"]
        stats["states"][state] = stats["states"].get(state, 0) + 1
        
        # Count demographics
        if case["is_first_time_offender"]:
            stats["first_time_offenders"] += 1
        if case["has_legal_aid"]:
            stats["with_legal_aid"] += 1
    
    return stats


def save_synthetic_cases(cases, output_path):
    """
    Save synthetic cases to JSON file.
    
    Time Complexity: O(n) — proportional to JSON serialization
    Space Complexity: O(1) — streaming write (not holding entire file in memory)
    
    Args:
        cases: List of case dictionaries
        output_path: Path to save JSON file
    """
    # Get absolute path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, output_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Write to file
    with open(full_path, "w") as f:
        json.dump(cases, f, indent=2)
    
    return full_path


def main():
    """
    Main function: Generate, calculate stats, and save synthetic dataset.
    
    NOTE: RTI requests were rejected. This synthetic dataset is used for
    testing and development only. All records are clearly labeled as SYNTHETIC.
    """
    # Print RTI rejection notice
    print("=" * 80)
    print("⚠️  RTI REJECTION NOTICE")
    print("=" * 80)
    print("\nBoth NCRB and state prison department RTI requests have been REJECTED.")
    print("Data not available through RTI channels. Proceeding with synthetic data only.\n")
    print("Full details: docs/RTI_TRACKING.md\n")
    print("=" * 80)
    print()
    
    # Generate cases
    cases = generate_synthetic_cases(num_cases=100)
    
    # Calculate statistics
    stats = calculate_statistics(cases)
    
    # Save to file
    output_file = "synthetic_cases.json"
    saved_path = save_synthetic_cases(cases, output_file)
    
    # Print summary
    print(f"\n✓ Generated {stats['total_cases']} synthetic cases.")
    print(f"✓ Saved to: {saved_path}")
    print(f"\nMetadata:")
    print(f"  - Total cases: {stats['total_cases']}")
    print(f"  - Date generated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"  - ⚠️  All records labeled as SYNTHETIC for clarity")
    print(f"  - ⚠️  Grounded in public NCRB statistics only")
    print(f"  - ⚠️  Not real prisoner data")
    print(f"\nOffense category distribution:")
    for category, count in sorted(stats["offense_categories"].items()):
        print(f"  - {category}: {count}")
    print(f"\nCase stage distribution:")
    for stage, count in sorted(stats["case_stages"].items()):
        print(f"  - {stage}: {count}")
    print(f"\nDemographics:")
    print(f"  - First-time offenders: {stats['first_time_offenders']}/{stats['total_cases']} ({100*stats['first_time_offenders']/stats['total_cases']:.1f}%)")
    print(f"  - With legal aid: {stats['with_legal_aid']}/{stats['total_cases']} ({100*stats['with_legal_aid']/stats['total_cases']:.1f}%)")
    print(f"\n✓ Synthetic dataset ready: {saved_path}")
    print(f"✓ See docs/RTI_TRACKING.md for full details on RTI rejection")


if __name__ == "__main__":
    main()