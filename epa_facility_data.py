#!/usr/bin/env python3
"""
Script to fetch facility data from the EPA RMP API.

This script retrieves information about a specific facility from the EPA's 
Risk Management Plan (RMP) Program Delivery System API.

Usage:
    python epa_facility_data.py [facility_id]
    
    If no facility_id is provided, it defaults to 1000041063.
"""
import json
import sys
import requests
from dotenv import load_dotenv

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
        print(f"Error fetching data: {e}")
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

def main():
    """Main function to fetch and display facility data."""
    # Load environment variables if needed
    load_dotenv()
    
    # Get facility ID from command line arguments or use default
    if len(sys.argv) > 1:
        facility_id = sys.argv[1]
    else:
        facility_id = "1000041063"  # Default facility ID
    
    print(f"Fetching data for facility ID: {facility_id}")
    facility_data = fetch_facility_data(facility_id)
    
    if facility_data:
        # Display facility information
        display_facility_info(facility_data)
        
        # Save the complete data to a file
        save_to_file(facility_data, f"facility_{facility_id}.json")
    else:
        print("Failed to fetch facility data.")

if __name__ == "__main__":
    main() 