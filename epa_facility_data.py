#!/usr/bin/env python3
"""
Script to fetch facility data from the EPA RMP API.

This script retrieves information about facilities from the EPA's 
Risk Management Plan (RMP) Program Delivery System API.

Usage:
    python epa_facility_data.py [epa_facility_id]
    
    If no epa_facility_id is provided, it defaults to 100000001892.
"""
import json
import sys
import os
import requests
from dotenv import load_dotenv

def fetch_facility_ids(epa_facility_id):
    """
    Fetch all facility IDs associated with an EPA facility ID.
    
    Args:
        epa_facility_id (str): The EPA facility ID to search for
        
    Returns:
        list: A list of facility IDs
    """
    url = f"https://cdxapps.epa.gov/olem-rmp-pds/api/search/submissions?id={epa_facility_id}"
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        print(f"Searching for facilities with EPA Facility ID: {epa_facility_id}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        # Check if we have embedded data
        if "_embedded" in data and len(data["_embedded"]) > 0:
            # Extract facility IDs
            facility_ids = [facility["facilityId"] for facility in data["_embedded"]]
            print(f"Found {len(facility_ids)} facility submissions")
            return data["_embedded"], facility_ids
        else:
            print("No facilities found with the given EPA Facility ID")
            return [], []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching facility IDs: {e}")
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
        print(f"Error fetching data for facility {facility_id}: {e}")
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
    print(f"Data saved to {filename}")

def display_facility_info(facility_data):
    """
    Display key information about the facility.
    
    Args:
        facility_data (dict): The facility data
    """
    print("\nFacility Information:")
    print(f"Facility ID: {facility_data.get('facilityId', 'N/A')}")
    print(f"EPA Facility ID: {facility_data.get('epaFacId', 'N/A')}")
    print(f"Name: {facility_data.get('facNm', 'N/A')}")
    print(f"Parent Company: {facility_data.get('parntCo1Nm', 'N/A')}")
    print(f"Address: {facility_data.get('facStreet1Tx', 'N/A')}")
    if facility_data.get('facStreet2Tx'):
        print(f"         {facility_data.get('facStreet2Tx')}")
    print(f"City: {facility_data.get('facCityNm', 'N/A')}")
    print(f"State: {facility_data.get('facStateCd', 'N/A')}")
    print(f"County: {facility_data.get('countyNm', 'N/A')}")
    print(f"ZIP: {facility_data.get('facZipCd', 'N/A')}")
    print(f"Coordinates: {facility_data.get('facLatDecMs', 'N/A')}, {facility_data.get('facLongDecMs', 'N/A')}")
    print(f"Receipt Date: {facility_data.get('receiptDa', 'N/A')}")
    
    # Display emergency plan information if available
    emergency_plan = facility_data.get('emergencyPlan', {})
    if emergency_plan:
        print("\nEmergency Plan:")
        print(f"Community Plan: {'Yes' if emergency_plan.get('communityPlanCd') == 'Y' else 'No'}")
        print(f"Facility Plan: {'Yes' if emergency_plan.get('facilityPlanCd') == 'Y' else 'No'}")
        print(f"Agency: {emergency_plan.get('agencyNm', 'N/A')}")
        print(f"Agency Phone: {emergency_plan.get('agencyPhoneNm', 'N/A')}")
    
    # Display process information if available
    processes = facility_data.get('processes', [])
    if processes:
        print("\nProcesses:")
        for i, process in enumerate(processes, 1):
            print(f"\nProcess {i}:")
            print(f"Program Level: {process.get('programLevelCd', 'N/A')}")
            
            # Display NAICS codes
            naics_codes = process.get('processNaics', [])
            if naics_codes:
                print("NAICS Codes:")
                for naics in naics_codes:
                    print(f"  - {naics.get('naicsCd', 'N/A')}: {naics.get('description', 'N/A')}")
            
            # Display chemicals
            chemicals = process.get('processChemicals', [])
            if chemicals:
                print("Chemicals:")
                for chem in chemicals:
                    print(f"  - {chem.get('chemicalNm', 'N/A')} (CAS: {chem.get('casNu', 'N/A')})")
                    print(f"    Type: {'Toxic' if chem.get('flamToxCd') == 'T' else 'Flammable' if chem.get('flamToxCd') == 'F' else 'Unknown'}")

def create_output_directory(epa_facility_id):
    """
    Create a directory to store output files.
    
    Args:
        epa_facility_id (str): The EPA facility ID
        
    Returns:
        str: The path to the output directory
    """
    output_dir = f"epa_facility_{epa_facility_id}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def main():
    """Main function to fetch and display facility data."""
    # Load environment variables if needed
    load_dotenv()
    
    # Get EPA facility ID from command line arguments or use default
    if len(sys.argv) > 1:
        epa_facility_id = sys.argv[1]
    else:
        epa_facility_id = "100000001892"  # Default EPA facility ID
    
    # Create output directory
    output_dir = create_output_directory(epa_facility_id)
    
    # First, fetch all facility IDs associated with the EPA facility ID
    submissions, facility_ids = fetch_facility_ids(epa_facility_id)
    
    if not facility_ids:
        print("No facilities found. Exiting.")
        return
    
    # Save the search results
    search_results_file = os.path.join(output_dir, f"search_results_{epa_facility_id}.json")
    save_to_file({"_embedded": submissions}, search_results_file)
    
    # Process each facility ID
    for i, facility_id in enumerate(facility_ids, 1):
        print(f"\n[{i}/{len(facility_ids)}] Fetching data for facility ID: {facility_id}")
        facility_data = fetch_facility_data(facility_id)
        
        if facility_data:
            # Display facility information
            display_facility_info(facility_data)
            
            # Save the complete data to a file
            output_file = os.path.join(output_dir, f"facility_{facility_id}.json")
            save_to_file(facility_data, output_file)
        else:
            print(f"Failed to fetch data for facility ID: {facility_id}")
    
    print(f"\nAll data has been saved to the '{output_dir}' directory")

if __name__ == "__main__":
    main() 