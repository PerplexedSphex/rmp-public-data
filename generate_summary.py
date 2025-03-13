#!/usr/bin/env python3

"""
Generate Summary File

This script generates a summary file for a specific state based on the collected data.

Usage:
    python generate_summary.py STATE_CODE
"""

import os
import json
import sys

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_to_file(data, filename):
    """
    Save the data to a JSON file.
    
    Args:
        data (dict): The data to save
        filename (str): The name of the file to save to
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def generate_summary(state_code):
    """
    Generate a summary file for a state based on the collected data.
    
    Args:
        state_code (str): The state code to generate the summary for
    """
    base_dir = "epa_all_states"
    state_dir = os.path.join(base_dir, f"epa_state_{state_code}")
    
    # Check if state directory exists
    if not os.path.exists(state_dir):
        print(f"State directory not found: {state_dir}")
        return
    
    # Check for state search file
    state_search_file = os.path.join(state_dir, f"state_search_{state_code}.json")
    if not os.path.exists(state_search_file):
        print(f"State search file not found: {state_search_file}")
        return
    
    # Load state search data
    state_search_data = load_json_file(state_search_file)
    if not state_search_data or "_embedded" not in state_search_data:
        print(f"Invalid state search data in {state_search_file}")
        return
    
    # Extract EPA facility IDs from search data
    facilities = state_search_data["_embedded"]
    epa_facility_ids = list(set(facility["epaFacId"] for facility in facilities))
    
    # Create summary data
    summary_data = {
        "state": state_code,
        "state_name": get_state_name(state_code),
        "total_epa_facilities": len(epa_facility_ids),
        "epa_facilities": []
    }
    
    # Process each EPA facility
    for epa_facility_id in epa_facility_ids:
        facility_dir = os.path.join(state_dir, f"facility_{epa_facility_id}")
        if not os.path.exists(facility_dir):
            print(f"Facility directory not found: {facility_dir}")
            continue
        
        # Check for submissions file
        submissions_file = os.path.join(facility_dir, f"submissions_{epa_facility_id}.json")
        if not os.path.exists(submissions_file):
            print(f"Submissions file not found: {submissions_file}")
            continue
        
        # Load submissions data
        submissions_data = load_json_file(submissions_file)
        if not submissions_data or "_embedded" not in submissions_data:
            print(f"Invalid submissions data in {submissions_file}")
            continue
        
        # Extract facility IDs from submissions data
        submissions = submissions_data["_embedded"]
        facility_ids = [submission["facilityId"] for submission in submissions]
        
        # Create facility summary
        facility_summary = {
            "epa_facility_id": epa_facility_id,
            "total_submissions": len(facility_ids),
            "submissions": []
        }
        
        # Process each facility submission
        for facility_id in facility_ids:
            facility_file = os.path.join(facility_dir, f"facility_{facility_id}.json")
            if not os.path.exists(facility_file):
                print(f"Facility file not found: {facility_file}")
                continue
            
            # Load facility data
            facility_data = load_json_file(facility_file)
            if not facility_data:
                print(f"Invalid facility data in {facility_file}")
                continue
            
            # Add submission summary
            facility_summary["submissions"].append({
                "facility_id": facility_id,
                "facility_name": facility_data.get("facNm", "N/A"),
                "city": facility_data.get("facCityNm", "N/A"),
                "state": facility_data.get("facStateCd", "N/A"),
                "receipt_date": facility_data.get("receiptDa", "N/A")
            })
        
        # Add facility summary to overall summary
        summary_data["epa_facilities"].append(facility_summary)
    
    # Save the summary data
    summary_file = os.path.join(state_dir, f"summary_{state_code}.json")
    save_to_file(summary_data, summary_file)
    
    print(f"Summary file generated: {summary_file}")

def get_state_name(state_code):
    """Get the full name of a state from its code."""
    state_names = {
        "AL": "Alabama", "AK": "Alaska", "AS": "American Samoa", "AZ": "Arizona", 
        "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", 
        "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", 
        "GU": "Guam", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", 
        "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", 
        "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", 
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", 
        "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", 
        "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", 
        "MP": "Northern Mariana Islands", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", 
        "PA": "Pennsylvania", "PR": "Puerto Rico", "RI": "Rhode Island", 
        "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", 
        "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "VI": "Virgin Islands", 
        "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    return state_names.get(state_code, state_code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_summary.py STATE_CODE")
        sys.exit(1)
    
    state_code = sys.argv[1].upper()
    generate_summary(state_code) 