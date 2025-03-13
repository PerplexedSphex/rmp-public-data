#!/usr/bin/env python3

"""
EPA RMP Data Validator

This script validates the completeness of EPA RMP data collection by:
1. Checking all state directories and summary files
2. Verifying that all facilities found in state searches have corresponding data
3. Ensuring all submissions for each facility have been collected
4. Generating a report of any missing data
5. Optionally fetching missing data

Usage:
    python epa_data_validator.py [--fetch-missing] [--state STATE_CODE]
    
    Optional:
    --fetch-missing: Attempt to fetch any missing data
    --state STATE_CODE: Validate only a specific state
"""

import os
import json
import argparse
import requests
import time
import concurrent.futures
import threading
from datetime import datetime

# Thread-local storage for session objects
thread_local = threading.local()

# Get thread-local session
def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

# List of all US states and territories
ALL_STATES = [
    "AL", "AK", "AS", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "GU", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", 
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "MP", "OH", 
    "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "VI", 
    "WA", "WV", "WI", "WY"
]

# Map of state codes to names for better reporting
STATE_NAMES = {
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

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def search_facilities_by_state(state_code):
    """
    Search for facilities in a specific state.
    
    Args:
        state_code (str): The 2-letter state code to search for
        
    Returns:
        list: A list of facility data dictionaries
        list: A list of unique EPA Facility IDs
    """
    url = "https://cdxapps.epa.gov/olem-rmp-pds/api/search"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    # Payload with state parameter
    payload = {
        "epaFacilityID": "",
        "epaFacilityName": "",
        "nameExactMatchString": "contains",
        "parentExactMatchString": "contains",
        "parentCompanyName": "",
        "facilityDUNS": "",
        "address": "",
        "city": "",
        "addressExactMatchString": "contains",
        "state": state_code,
        "county": "",
        "zipcode": "",
        "chemicals": [],
        "chemicalType": "",
        "programLevel": "",
        "naicsCodes": [],
        "excludeChemicals": False,
        "excludeNaics": False,
        "excludeDereg": "false"
    }
    
    try:
        print(f"Searching for facilities in {STATE_NAMES.get(state_code, state_code)} ({state_code})")
        session = get_session()
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        # Check if we have embedded data
        if "_embedded" in data and len(data["_embedded"]) > 0:
            facilities = data["_embedded"]
            # Extract unique EPA Facility IDs
            epa_facility_ids = list(set(facility["epaFacId"] for facility in facilities))
            print(f"Found {len(facilities)} facilities with {len(epa_facility_ids)} unique EPA Facility IDs in {state_code}")
            return facilities, epa_facility_ids
        else:
            print(f"No facilities found in {state_code}")
            return [], []
            
    except requests.exceptions.RequestException as e:
        print(f"Error searching for facilities in {state_code}: {e}")
        return [], []

def fetch_facility_ids(epa_facility_id):
    """
    Fetch all facility IDs associated with an EPA facility ID.
    
    Args:
        epa_facility_id (str): The EPA facility ID to search for
        
    Returns:
        list: A list of facility submissions
        list: A list of facility IDs
    """
    url = f"https://cdxapps.epa.gov/olem-rmp-pds/api/search/submissions?id={epa_facility_id}"
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        print(f"  Searching for submissions with EPA Facility ID: {epa_facility_id}")
        session = get_session()
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        # Check if we have embedded data
        if "_embedded" in data and len(data["_embedded"]) > 0:
            # Extract facility IDs
            facility_ids = [facility["facilityId"] for facility in data["_embedded"]]
            print(f"    Found {len(facility_ids)} facility submissions")
            return data["_embedded"], facility_ids
        else:
            print(f"    No submissions found for EPA Facility ID: {epa_facility_id}")
            return [], []
            
    except requests.exceptions.RequestException as e:
        print(f"    Error fetching facility IDs: {e}")
        return [], []

def fetch_facility_data(facility_id):
    """
    Fetch data for a specific facility from the EPA RMP API.
    
    Args:
        facility_id (str): The ID of the facility to fetch data for
        
    Returns:
        dict: The facility data as a JSON object
    """
    url = f"https://cdxapps.epa.gov/olem-rmp-pds/api/facilities/{facility_id}"
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        session = get_session()
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"      Error fetching data for facility {facility_id}: {e}")
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
    print(f"      Data saved to {filename}")

def validate_state(state_code, fetch_missing=False):
    """
    Validate the data for a specific state.
    
    Args:
        state_code (str): The state code to validate
        fetch_missing (bool): Whether to fetch missing data
        
    Returns:
        dict: Validation results
    """
    print(f"\n=== Validating {STATE_NAMES.get(state_code, state_code)} ({state_code}) ===")
    
    base_dir = "epa_all_states"
    state_dir = os.path.join(base_dir, f"epa_state_{state_code}")
    
    # Check if state directory exists
    if not os.path.exists(state_dir):
        print(f"State directory not found: {state_dir}")
        if fetch_missing:
            print(f"Creating directory and fetching data for {state_code}")
            os.makedirs(state_dir, exist_ok=True)
        else:
            return {
                "state": state_code,
                "exists": False,
                "missing_epa_facilities": [],
                "missing_submissions": []
            }
    
    # Check for state search file
    state_search_file = os.path.join(state_dir, f"state_search_{state_code}.json")
    if not os.path.exists(state_search_file):
        print(f"State search file not found: {state_search_file}")
        if fetch_missing:
            print(f"Fetching state search data for {state_code}")
            facilities, epa_facility_ids = search_facilities_by_state(state_code)
            if facilities:
                save_to_file({"_embedded": facilities}, state_search_file)
        else:
            return {
                "state": state_code,
                "exists": True,
                "search_file_exists": False,
                "missing_epa_facilities": [],
                "missing_submissions": []
            }
    
    # Load state search data
    state_search_data = load_json_file(state_search_file)
    if not state_search_data or "_embedded" not in state_search_data:
        print(f"Invalid state search data in {state_search_file}")
        return {
            "state": state_code,
            "exists": True,
            "search_file_exists": True,
            "search_file_valid": False,
            "missing_epa_facilities": [],
            "missing_submissions": []
        }
    
    # Extract EPA facility IDs from search data
    facilities = state_search_data["_embedded"]
    epa_facility_ids = list(set(facility["epaFacId"] for facility in facilities))
    
    # Check for summary file
    summary_file = os.path.join(state_dir, f"summary_{state_code}.json")
    if not os.path.exists(summary_file):
        print(f"Summary file not found: {summary_file}")
        if fetch_missing:
            print(f"Will create summary file after validation")
        else:
            return {
                "state": state_code,
                "exists": True,
                "search_file_exists": True,
                "search_file_valid": True,
                "summary_file_exists": False,
                "epa_facilities_found": len(epa_facility_ids),
                "missing_epa_facilities": epa_facility_ids,
                "missing_submissions": []
            }
    
    # Load summary data
    summary_data = load_json_file(summary_file)
    if not summary_data or "epa_facilities" not in summary_data:
        print(f"Invalid summary data in {summary_file}")
        return {
            "state": state_code,
            "exists": True,
            "search_file_exists": True,
            "search_file_valid": True,
            "summary_file_exists": True,
            "summary_file_valid": False,
            "epa_facilities_found": len(epa_facility_ids),
            "missing_epa_facilities": epa_facility_ids,
            "missing_submissions": []
        }
    
    # Extract EPA facility IDs from summary data
    summary_epa_facility_ids = [facility["epa_facility_id"] for facility in summary_data["epa_facilities"]]
    
    # Find missing EPA facility IDs
    missing_epa_facility_ids = [id for id in epa_facility_ids if id not in summary_epa_facility_ids]
    
    # Check for missing submissions
    missing_submissions = []
    
    for epa_facility_id in summary_epa_facility_ids:
        # Check for facility directory
        facility_dir = os.path.join(state_dir, f"facility_{epa_facility_id}")
        if not os.path.exists(facility_dir):
            print(f"Facility directory not found: {facility_dir}")
            missing_submissions.append({
                "epa_facility_id": epa_facility_id,
                "directory_exists": False,
                "missing_facility_ids": []
            })
            continue
        
        # Check for submissions file
        submissions_file = os.path.join(facility_dir, f"submissions_{epa_facility_id}.json")
        if not os.path.exists(submissions_file):
            print(f"Submissions file not found: {submissions_file}")
            missing_submissions.append({
                "epa_facility_id": epa_facility_id,
                "directory_exists": True,
                "submissions_file_exists": False,
                "missing_facility_ids": []
            })
            continue
        
        # Load submissions data
        submissions_data = load_json_file(submissions_file)
        if not submissions_data or "_embedded" not in submissions_data:
            print(f"Invalid submissions data in {submissions_file}")
            missing_submissions.append({
                "epa_facility_id": epa_facility_id,
                "directory_exists": True,
                "submissions_file_exists": True,
                "submissions_file_valid": False,
                "missing_facility_ids": []
            })
            continue
        
        # Extract facility IDs from submissions data
        facility_ids = [submission["facilityId"] for submission in submissions_data["_embedded"]]
        
        # Find facility summary in summary data
        facility_summary = next((f for f in summary_data["epa_facilities"] if f["epa_facility_id"] == epa_facility_id), None)
        if not facility_summary:
            print(f"Facility summary not found for EPA Facility ID: {epa_facility_id}")
            continue
        
        # Extract facility IDs from facility summary
        summary_facility_ids = [submission["facility_id"] for submission in facility_summary["submissions"]]
        
        # Find missing facility IDs
        missing_facility_ids = []
        for facility_id in facility_ids:
            facility_file = os.path.join(facility_dir, f"facility_{facility_id}.json")
            if not os.path.exists(facility_file):
                print(f"Facility file not found: {facility_file}")
                missing_facility_ids.append(facility_id)
        
        if missing_facility_ids:
            missing_submissions.append({
                "epa_facility_id": epa_facility_id,
                "directory_exists": True,
                "submissions_file_exists": True,
                "submissions_file_valid": True,
                "missing_facility_ids": missing_facility_ids
            })
    
    # Fetch missing data if requested
    if fetch_missing and (missing_epa_facility_ids or missing_submissions):
        print(f"Fetching missing data for {state_code}")
        
        # Fetch missing EPA facilities
        for epa_facility_id in missing_epa_facility_ids:
            print(f"Fetching data for EPA Facility ID: {epa_facility_id}")
            facility_dir = os.path.join(state_dir, f"facility_{epa_facility_id}")
            os.makedirs(facility_dir, exist_ok=True)
            
            # Fetch submissions
            submissions, facility_ids = fetch_facility_ids(epa_facility_id)
            if submissions:
                submissions_file = os.path.join(facility_dir, f"submissions_{epa_facility_id}.json")
                save_to_file({"_embedded": submissions}, submissions_file)
                
                # Fetch facility data
                for facility_id in facility_ids:
                    print(f"  Fetching data for Facility ID: {facility_id}")
                    facility_data = fetch_facility_data(facility_id)
                    if facility_data:
                        facility_file = os.path.join(facility_dir, f"facility_{facility_id}.json")
                        save_to_file(facility_data, facility_file)
                    time.sleep(0.2)  # Small delay to avoid overwhelming the API
            
            time.sleep(0.5)  # Small delay to avoid overwhelming the API
        
        # Fetch missing submissions
        for missing in missing_submissions:
            epa_facility_id = missing["epa_facility_id"]
            
            # Create facility directory if it doesn't exist
            facility_dir = os.path.join(state_dir, f"facility_{epa_facility_id}")
            os.makedirs(facility_dir, exist_ok=True)
            
            # Fetch submissions if needed
            if not missing.get("submissions_file_exists", True) or not missing.get("submissions_file_valid", True):
                print(f"Fetching submissions for EPA Facility ID: {epa_facility_id}")
                submissions, facility_ids = fetch_facility_ids(epa_facility_id)
                if submissions:
                    submissions_file = os.path.join(facility_dir, f"submissions_{epa_facility_id}.json")
                    save_to_file({"_embedded": submissions}, submissions_file)
            
            # Fetch missing facility data
            for facility_id in missing.get("missing_facility_ids", []):
                print(f"  Fetching data for Facility ID: {facility_id}")
                facility_data = fetch_facility_data(facility_id)
                if facility_data:
                    facility_file = os.path.join(facility_dir, f"facility_{facility_id}.json")
                    save_to_file(facility_data, facility_file)
                time.sleep(0.2)  # Small delay to avoid overwhelming the API
            
            time.sleep(0.5)  # Small delay to avoid overwhelming the API
        
        # Regenerate summary file
        print(f"Regenerating summary file for {state_code}")
        regenerate_summary(state_code)
    
    return {
        "state": state_code,
        "exists": True,
        "search_file_exists": True,
        "search_file_valid": True,
        "summary_file_exists": True,
        "summary_file_valid": True,
        "epa_facilities_found": len(epa_facility_ids),
        "epa_facilities_processed": len(summary_epa_facility_ids),
        "missing_epa_facilities": missing_epa_facility_ids,
        "missing_submissions": missing_submissions
    }

def regenerate_summary(state_code):
    """
    Regenerate the summary file for a state based on the collected data.
    
    Args:
        state_code (str): The state code to regenerate the summary for
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
        "state_name": STATE_NAMES.get(state_code, state_code),
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
    
    print(f"Summary file regenerated: {summary_file}")

def create_master_summary(base_dir="epa_all_states"):
    """
    Create a master summary file with information from all states.
    
    Args:
        base_dir (str): The base directory containing all state data
    """
    master_summary = {
        "total_states": 0,
        "total_epa_facilities": 0,
        "total_facility_submissions": 0,
        "states": []
    }
    
    # Find all summary files
    for state_code in ALL_STATES:
        summary_file = os.path.join(base_dir, f"epa_state_{state_code}", f"summary_{state_code}.json")
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r') as f:
                    state_summary = json.load(f)
                
                # Extract key information
                state_info = {
                    "state_code": state_code,
                    "state_name": STATE_NAMES.get(state_code, state_code),
                    "epa_facilities": state_summary.get("total_epa_facilities", 0),
                    "facility_submissions": 0
                }
                
                # Count total submissions
                for facility in state_summary.get("epa_facilities", []):
                    state_info["facility_submissions"] += facility.get("total_submissions", 0)
                
                # Update master counts
                master_summary["total_states"] += 1
                master_summary["total_epa_facilities"] += state_info["epa_facilities"]
                master_summary["total_facility_submissions"] += state_info["facility_submissions"]
                
                # Add state info to master summary
                master_summary["states"].append(state_info)
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error processing summary file for {state_code}: {e}")
    
    # Sort states by number of facilities
    master_summary["states"].sort(key=lambda x: x["epa_facilities"], reverse=True)
    
    # Add timestamp
    master_summary["generated_at"] = datetime.now().isoformat()
    
    # Save master summary
    master_file = os.path.join(base_dir, "master_summary.json")
    with open(master_file, 'w') as f:
        json.dump(master_summary, f, indent=2)
    
    print(f"\nMaster summary created: {master_file}")
    print(f"Total states processed: {master_summary['total_states']}")
    print(f"Total EPA facilities: {master_summary['total_epa_facilities']}")
    print(f"Total facility submissions: {master_summary['total_facility_submissions']}")

def main():
    """Main function to validate EPA RMP data collection."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Validate EPA RMP data collection.')
    parser.add_argument('--fetch-missing', action='store_true', help='Fetch missing data')
    parser.add_argument('--state', type=str, help='Validate only a specific state')
    args = parser.parse_args()
    
    # Determine which states to validate
    states_to_validate = [args.state.upper()] if args.state else ALL_STATES
    
    # Validate each state
    validation_results = []
    for state_code in states_to_validate:
        if state_code not in ALL_STATES:
            print(f"Invalid state code: {state_code}")
            continue
        
        result = validate_state(state_code, args.fetch_missing)
        validation_results.append(result)
    
    # Generate validation report
    print("\n=== Validation Report ===")
    
    # Count states with issues
    states_with_missing_epa_facilities = [r for r in validation_results if r.get("missing_epa_facilities")]
    states_with_missing_submissions = [r for r in validation_results if r.get("missing_submissions")]
    
    print(f"Total states validated: {len(validation_results)}")
    print(f"States with missing EPA facilities: {len(states_with_missing_epa_facilities)}")
    print(f"States with missing submissions: {len(states_with_missing_submissions)}")
    
    # Print details of states with issues
    if states_with_missing_epa_facilities:
        print("\nStates with missing EPA facilities:")
        for result in states_with_missing_epa_facilities:
            state_code = result["state"]
            missing_count = len(result["missing_epa_facilities"])
            print(f"  {STATE_NAMES.get(state_code, state_code)} ({state_code}): {missing_count} missing EPA facilities")
    
    if states_with_missing_submissions:
        print("\nStates with missing submissions:")
        for result in states_with_missing_submissions:
            state_code = result["state"]
            missing_count = sum(len(s.get("missing_facility_ids", [])) for s in result["missing_submissions"])
            print(f"  {STATE_NAMES.get(state_code, state_code)} ({state_code}): {missing_count} missing facility submissions")
    
    # Create master summary if all states are validated and no issues found
    if len(states_to_validate) == len(ALL_STATES) and not states_with_missing_epa_facilities and not states_with_missing_submissions:
        print("\nAll data is complete. Creating master summary...")
        create_master_summary()
    elif args.fetch_missing:
        print("\nMissing data has been fetched. Creating master summary...")
        create_master_summary()

if __name__ == "__main__":
    main() 