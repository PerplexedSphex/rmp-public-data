#!/usr/bin/env python3
"""
Script to fetch EPA RMP facility data for all US states and territories.

This script loops through all US states and territories, searching for facilities
in each one using the EPA's Risk Management Plan (RMP) Program Delivery System API,
then retrieves detailed information for each facility.

Usage:
    python epa_all_states.py [--start STATE_CODE]
    
    Optional:
    --start STATE_CODE: Start processing from a specific state code
                       (useful for resuming an interrupted run)
"""
import json
import sys
import os
import requests
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

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
        response = requests.post(url, headers=headers, json=payload)
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
        response = requests.get(url, headers=headers)
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
        response = requests.get(url, headers=headers)
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
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"      Data saved to {filename}")

def create_output_directory(state_code):
    """
    Create a directory to store output files.
    
    Args:
        state_code (str): The state code
        
    Returns:
        str: The path to the output directory
    """
    base_dir = "epa_all_states"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    output_dir = os.path.join(base_dir, f"epa_state_{state_code}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

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

def process_state(state_code):
    """
    Process a single state to fetch and save all facility data.
    
    Args:
        state_code (str): The state code to process
        
    Returns:
        dict: Summary data for the state
    """
    # Create output directory
    output_dir = create_output_directory(state_code)
    
    # First, search for facilities in the specified state
    facilities, epa_facility_ids = search_facilities_by_state(state_code)
    
    if not epa_facility_ids:
        print(f"No EPA Facility IDs found for {state_code}. Skipping.")
        # Create an empty summary
        summary_data = {
            "state": state_code,
            "state_name": STATE_NAMES.get(state_code, state_code),
            "total_epa_facilities": 0,
            "epa_facilities": []
        }
        # Save the empty summary
        summary_file = os.path.join(output_dir, f"summary_{state_code}.json")
        save_to_file(summary_data, summary_file)
        return summary_data
    
    # Save the state search results
    state_search_file = os.path.join(output_dir, f"state_search_{state_code}.json")
    save_to_file({"_embedded": facilities}, state_search_file)
    
    # Create a summary file to track all facilities
    summary_data = {
        "state": state_code,
        "state_name": STATE_NAMES.get(state_code, state_code),
        "total_epa_facilities": len(epa_facility_ids),
        "epa_facilities": []
    }
    
    # Process each EPA Facility ID
    for i, epa_facility_id in enumerate(epa_facility_ids, 1):
        print(f"\n[{i}/{len(epa_facility_ids)}] Processing EPA Facility ID: {epa_facility_id}")
        
        # Create a directory for this EPA Facility ID
        facility_dir = os.path.join(output_dir, f"facility_{epa_facility_id}")
        if not os.path.exists(facility_dir):
            os.makedirs(facility_dir)
        
        # Fetch all facility submissions for this EPA Facility ID
        submissions, facility_ids = fetch_facility_ids(epa_facility_id)
        
        if not facility_ids:
            print(f"  No facility submissions found for EPA Facility ID: {epa_facility_id}")
            # Add empty facility to summary
            facility_summary = {
                "epa_facility_id": epa_facility_id,
                "total_submissions": 0,
                "submissions": []
            }
            summary_data["epa_facilities"].append(facility_summary)
            continue
        
        # Save the submissions search results
        submissions_file = os.path.join(facility_dir, f"submissions_{epa_facility_id}.json")
        save_to_file({"_embedded": submissions}, submissions_file)
        
        # Add to summary data
        facility_summary = {
            "epa_facility_id": epa_facility_id,
            "total_submissions": len(facility_ids),
            "submissions": []
        }
        
        # Process each facility submission
        for j, facility_id in enumerate(facility_ids, 1):
            print(f"    [{j}/{len(facility_ids)}] Fetching data for facility ID: {facility_id}")
            facility_data = fetch_facility_data(facility_id)
            
            if facility_data:
                # Display basic facility information
                print(f"      Facility: {facility_data.get('facNm', 'N/A')}")
                print(f"      Location: {facility_data.get('facCityNm', 'N/A')}, {facility_data.get('facStateCd', 'N/A')}")
                
                # Save the complete data to a file
                output_file = os.path.join(facility_dir, f"facility_{facility_id}.json")
                save_to_file(facility_data, output_file)
                
                # Add to facility summary
                facility_summary["submissions"].append({
                    "facility_id": facility_id,
                    "facility_name": facility_data.get("facNm", "N/A"),
                    "city": facility_data.get("facCityNm", "N/A"),
                    "state": facility_data.get("facStateCd", "N/A"),
                    "receipt_date": facility_data.get("receiptDa", "N/A")
                })
            else:
                print(f"      Failed to fetch data for facility ID: {facility_id}")
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        # Add facility summary to overall summary
        summary_data["epa_facilities"].append(facility_summary)
    
    # Save the summary data
    summary_file = os.path.join(output_dir, f"summary_{state_code}.json")
    save_to_file(summary_data, summary_file)
    
    print(f"\nAll data for {state_code} has been saved to the '{output_dir}' directory")
    print(f"Summary information is available in '{summary_file}'")
    
    return summary_data

def main():
    """Main function to fetch and display facility data for all states."""
    # Load environment variables if needed
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch EPA RMP facility data for all US states and territories.')
    parser.add_argument('--start', type=str, help='Start processing from a specific state code')
    args = parser.parse_args()
    
    # Determine which states to process
    states_to_process = ALL_STATES
    if args.start and args.start.upper() in ALL_STATES:
        start_index = ALL_STATES.index(args.start.upper())
        states_to_process = ALL_STATES[start_index:]
        print(f"Starting from {args.start.upper()} ({len(states_to_process)} states remaining)")
    
    # Create base directory
    base_dir = "epa_all_states"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Process each state
    start_time = datetime.now()
    print(f"Starting data collection at {start_time.isoformat()}")
    print(f"Processing {len(states_to_process)} states/territories")
    
    for i, state_code in enumerate(states_to_process, 1):
        state_start_time = datetime.now()
        print(f"\n[{i}/{len(states_to_process)}] Processing {STATE_NAMES.get(state_code, state_code)} ({state_code})")
        
        try:
            process_state(state_code)
        except Exception as e:
            print(f"Error processing state {state_code}: {e}")
        
        state_end_time = datetime.now()
        state_duration = state_end_time - state_start_time
        print(f"Completed {state_code} in {state_duration}")
        
        # Add a delay between states to avoid overwhelming the API
        if i < len(states_to_process):
            print(f"Waiting 5 seconds before processing next state...")
            time.sleep(5)
    
    # Create master summary
    create_master_summary(base_dir)
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nData collection completed at {end_time.isoformat()}")
    print(f"Total duration: {duration}")

if __name__ == "__main__":
    main() 