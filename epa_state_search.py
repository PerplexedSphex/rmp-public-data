#!/usr/bin/env python3
"""
Script to fetch EPA RMP facility data by state.

This script searches for facilities in a specific state using the EPA's
Risk Management Plan (RMP) Program Delivery System API, then retrieves
detailed information for each facility.

Usage:
    python epa_state_search.py [state_code]
    
    If no state_code is provided, it defaults to "GU" (Guam).
    State code should be a valid 2-letter US state or territory code.
"""
import json
import sys
import os
import requests
import time
from dotenv import load_dotenv

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
        print(f"Searching for facilities in state: {state_code}")
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
            print(f"No facilities found in state: {state_code}")
            return [], []
            
    except requests.exceptions.RequestException as e:
        print(f"Error searching for facilities: {e}")
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

def display_facility_info(facility_data, detailed=False):
    """
    Display key information about the facility.
    
    Args:
        facility_data (dict): The facility data
        detailed (bool): Whether to display detailed information
    """
    if not detailed:
        # Display basic information
        print(f"      Facility: {facility_data.get('facNm', 'N/A')}")
        print(f"      Location: {facility_data.get('facCityNm', 'N/A')}, {facility_data.get('facStateCd', 'N/A')}")
        return
    
    # Display detailed information
    print("\n      Facility Information:")
    print(f"      Facility ID: {facility_data.get('facilityId', 'N/A')}")
    print(f"      EPA Facility ID: {facility_data.get('epaFacId', 'N/A')}")
    print(f"      Name: {facility_data.get('facNm', 'N/A')}")
    print(f"      Parent Company: {facility_data.get('parntCo1Nm', 'N/A')}")
    print(f"      Address: {facility_data.get('facStreet1Tx', 'N/A')}")
    if facility_data.get('facStreet2Tx'):
        print(f"               {facility_data.get('facStreet2Tx')}")
    print(f"      City: {facility_data.get('facCityNm', 'N/A')}")
    print(f"      State: {facility_data.get('facStateCd', 'N/A')}")
    print(f"      County: {facility_data.get('countyNm', 'N/A')}")
    print(f"      ZIP: {facility_data.get('facZipCd', 'N/A')}")
    print(f"      Coordinates: {facility_data.get('facLatDecMs', 'N/A')}, {facility_data.get('facLongDecMs', 'N/A')}")
    print(f"      Receipt Date: {facility_data.get('receiptDa', 'N/A')}")
    
    # Display emergency plan information if available
    emergency_plan = facility_data.get('emergencyPlan', {})
    if emergency_plan:
        print("\n      Emergency Plan:")
        print(f"      Community Plan: {'Yes' if emergency_plan.get('communityPlanCd') == 'Y' else 'No'}")
        print(f"      Facility Plan: {'Yes' if emergency_plan.get('facilityPlanCd') == 'Y' else 'No'}")
        print(f"      Agency: {emergency_plan.get('agencyNm', 'N/A')}")
        print(f"      Agency Phone: {emergency_plan.get('agencyPhoneNm', 'N/A')}")
    
    # Display process information if available
    processes = facility_data.get('processes', [])
    if processes:
        print("\n      Processes:")
        for i, process in enumerate(processes, 1):
            print(f"\n      Process {i}:")
            print(f"      Program Level: {process.get('programLevelCd', 'N/A')}")
            
            # Display NAICS codes
            naics_codes = process.get('processNaics', [])
            if naics_codes:
                print("      NAICS Codes:")
                for naics in naics_codes:
                    print(f"        - {naics.get('naicsCd', 'N/A')}: {naics.get('description', 'N/A')}")
            
            # Display chemicals
            chemicals = process.get('processChemicals', [])
            if chemicals:
                print("      Chemicals:")
                for chem in chemicals:
                    print(f"        - {chem.get('chemicalNm', 'N/A')} (CAS: {chem.get('casNu', 'N/A')})")
                    print(f"          Type: {'Toxic' if chem.get('flamToxCd') == 'T' else 'Flammable' if chem.get('flamToxCd') == 'F' else 'Unknown'}")

def create_output_directory(state_code):
    """
    Create a directory to store output files.
    
    Args:
        state_code (str): The state code
        
    Returns:
        str: The path to the output directory
    """
    output_dir = f"epa_state_{state_code}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def main():
    """Main function to fetch and display facility data by state."""
    # Load environment variables if needed
    load_dotenv()
    
    # Get state code from command line arguments or use default
    if len(sys.argv) > 1:
        state_code = sys.argv[1].upper()
    else:
        state_code = "GU"  # Default state code (Guam)
    
    # Create output directory
    output_dir = create_output_directory(state_code)
    
    # First, search for facilities in the specified state
    facilities, epa_facility_ids = search_facilities_by_state(state_code)
    
    if not epa_facility_ids:
        print("No EPA Facility IDs found. Exiting.")
        return
    
    # Save the state search results
    state_search_file = os.path.join(output_dir, f"state_search_{state_code}.json")
    save_to_file({"_embedded": facilities}, state_search_file)
    
    # Create a summary file to track all facilities
    summary_data = {
        "state": state_code,
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
                display_facility_info(facility_data)
                
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
    
    print(f"\nAll data has been saved to the '{output_dir}' directory")
    print(f"Summary information is available in '{summary_file}'")

if __name__ == "__main__":
    main() 