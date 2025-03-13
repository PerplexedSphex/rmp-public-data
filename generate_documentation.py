#!/usr/bin/env python3
"""
EPA RMP Documentation Generator

This script generates a structured documentation site from EPA Risk Management Plan (RMP) data.
It creates markdown files in a 'pages' directory that mirrors the structure of the JSON data directories.
The script processes master summaries, state summaries, facility data, and submission data.

No network requests are made - all data is read from existing JSON files.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import re

# Configuration
INPUT_DIR = "epa_all_states"
OUTPUT_DIR = "pages"
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AS": "American Samoa", "AZ": "Arizona", 
    "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", 
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", 
    "GU": "Guam", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", 
    "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", 
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", 
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", 
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", 
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "MP": "Northern Mariana Islands", 
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", 
    "PR": "Puerto Rico", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", 
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", 
    "VI": "Virgin Islands", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

def sanitize_filename(name):
    """Convert a string to a valid filename."""
    if not name:
        return "unknown"
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def format_date(date_str):
    """Format a date string for display."""
    if not date_str:
        return "Unknown Date"
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return date_str

def generate_main_index():
    """Generate the main index page with links to all states."""
    master_summary = load_json_file(f"{INPUT_DIR}/master_summary.json")
    if not master_summary:
        print("Error: Master summary file not found.")
        return

    create_directory(OUTPUT_DIR)
    
    with open(f"{OUTPUT_DIR}/index.md", 'w', encoding='utf-8') as f:
        f.write("# EPA Risk Management Plan (RMP) Facility Database\n\n")
        f.write("This documentation provides access to EPA RMP facility data across the United States and its territories.\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total States/Territories**: {len(master_summary['states'])}\n")
        f.write(f"- **Total EPA Facilities**: {master_summary['total_epa_facilities']}\n")
        f.write(f"- **Total Facility Submissions**: {master_summary['total_facility_submissions']}\n\n")
        
        f.write("## States and Territories\n\n")
        f.write("| State/Territory | Facilities | Submissions |\n")
        f.write("|----------------|------------|-------------|\n")
        
        # Sort states alphabetically by state name
        sorted_states = sorted(master_summary['states'], key=lambda x: x['state_name'])
        
        for state in sorted_states:
            state_code = state['state_code']
            state_name = state['state_name']
            facilities = state['epa_facilities']
            submissions = state['facility_submissions']
            
            f.write(f"| [{state_name}](states/{state_code}/index.md) | {facilities:,} | {submissions:,} |\n")
    
    print(f"Generated main index page: {OUTPUT_DIR}/index.md")

def generate_state_index(state_code):
    """Generate an index page for a state with links to all facilities."""
    state_summary_path = f"{INPUT_DIR}/epa_state_{state_code}/summary_{state_code}.json"
    state_summary = load_json_file(state_summary_path)
    if not state_summary:
        print(f"Error: State summary file not found for {state_code}.")
        return

    state_name = state_summary['state_name']
    total_facilities = state_summary['total_epa_facilities']
    
    # Calculate total submissions by summing from each facility
    total_submissions = sum(len(facility.get('submissions', [])) for facility in state_summary.get('epa_facilities', []))
    
    state_dir = f"{OUTPUT_DIR}/states/{state_code}"
    create_directory(state_dir)
    
    with open(f"{state_dir}/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# {state_name} EPA RMP Facilities\n\n")
        f.write(f"[← Back to Main Index](../../index.md)\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **State**: {state_name}\n")
        f.write(f"- **Total Facilities**: {total_facilities}\n")
        f.write(f"- **Total Submissions**: {total_submissions}\n\n")
        
        f.write("## Facilities\n\n")
        f.write("| Facility Name | City | Submissions |\n")
        f.write("|--------------|------|-------------|\n")
        
        # Sort facilities alphabetically by name
        sorted_facilities = sorted(state_summary.get('epa_facilities', []), 
                                  key=lambda x: x.get('facility_name', '').lower())
        
        for facility in sorted_facilities:
            facility_id = facility.get('epa_facility_id', '')
            facility_name = facility.get('facility_name', 'Unknown')
            city = facility.get('city', 'Unknown')
            submissions_count = len(facility.get('submissions', []))
            
            f.write(f"| [{facility_name}](facilities/{facility_id}/index.md) | {city} | {submissions_count} |\n")
    
    print(f"Generated state index page for {state_name}: {state_dir}/index.md")

def generate_facility_index(state_code, epa_facility_id, facility_name, city, facility_data):
    """Generate an index page for a facility with links to all submissions."""
    facility_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}"
    create_directory(facility_dir)
    create_directory(f"{facility_dir}/submissions")
    
    with open(f"{facility_dir}/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# {facility_name}\n\n")
        f.write(f"**Location:** {city}, {state_code}\n\n")
        f.write(f"**EPA Facility ID:** {epa_facility_id}\n\n")
        f.write(f"[Back to {state_code} Index](../../index.md)\n\n")
        
        f.write("## Submissions\n\n")
        f.write("| Date | Submission ID | Document Control Number |\n")
        f.write("|------|--------------|-------------------------|\n")
        
        # Filter out non-dictionary items and sort submissions by date (newest first)
        valid_submissions = []
        for item in facility_data:
            if isinstance(item, dict):
                valid_submissions.append(item)
            else:
                print(f"Warning: Skipping invalid submission data: {item}")
        
        # Sort submissions by date
        sorted_submissions = sorted(valid_submissions, 
                                   key=lambda x: x.get('receiptDa', ''), 
                                   reverse=True)
        
        for submission in sorted_submissions:
            submission_id = submission.get('facilityId', '')
            receipt_date = format_date(submission.get('receiptDa', ''))
            doc_control_num = submission.get('documentControlNumber', '')
            
            f.write(f"| [{receipt_date}](submissions/{submission_id}.md) | {submission_id} | {doc_control_num} |\n")
    
    print(f"Generated facility index page for {facility_name}: {facility_dir}/index.md")

def generate_submission_page(state_code, epa_facility_id, facility_name, submission):
    """Generate a detailed page for a facility submission."""
    # Handle case where submission is a string (JSON)
    if isinstance(submission, str):
        try:
            submission = json.loads(submission)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse submission data: {submission[:100]}...")
            return
    
    # Get submission ID (facilityId in the JSON)
    submission_id = submission.get('facilityId', '')
    if not submission_id:
        print(f"Warning: No facility ID found in submission data.")
        return
        
    submission_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}/submissions"
    create_directory(submission_dir)
    
    # Load the detailed facility data
    facility_file_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{submission_id}.json"
    facility_data = load_json_file(facility_file_path)
    if not facility_data:
        print(f"Warning: Facility data file not found: {facility_file_path}")
        return
    
    # Create the submission page
    with open(f"{submission_dir}/{submission_id}.md", 'w', encoding='utf-8') as f:
        # Use facNm from facility_data if available, otherwise use the facility_name passed in
        facility_name_from_data = facility_data.get('facNm', facility_name)
        if facility_name_from_data == "Unknown" or facility_name_from_data is None:
            facility_name_from_data = facility_name
            
        f.write(f"# {facility_name_from_data} - Submission {submission_id}\n\n")
        f.write(f"[← Back to Facility Index](../index.md)\n\n")
        
        # Registration Information
        f.write("## Registration Information\n\n")
        f.write(f"- **EPA Facility ID**: {facility_data.get('epaFacId', '')}\n")
        f.write(f"- **Facility ID**: {submission_id}\n")
        f.write(f"- **Submission Type**: {get_submission_type(facility_data.get('sbmsnTypeCd', ''))}\n")
        f.write(f"- **Receipt Date**: {format_date(facility_data.get('receiptDa', ''))}\n")
        f.write(f"- **Parent Company**: {facility_data.get('parntCo1Nm', 'Not specified')}\n")
        
        # Facility Identification
        f.write("\n## Facility Identification\n\n")
        f.write(f"- **Facility Name**: {facility_name_from_data}\n")
        f.write(f"- **DUNS Number**: {facility_data.get('facDunsNu', 'Not specified')}\n")
        
        # Location
        f.write("\n## Location\n\n")
        f.write(f"- **Street Address**: {facility_data.get('facStreet1Tx', '')}")
        if facility_data.get('facStreet2Tx'):
            f.write(f", {facility_data.get('facStreet2Tx')}")
        f.write("\n")
        f.write(f"- **City**: {facility_data.get('facCityNm', '')}\n")
        f.write(f"- **State**: {facility_data.get('facStateCd', '')}\n")
        f.write(f"- **County**: {facility_data.get('countyNm', '')}\n")
        f.write(f"- **ZIP Code**: {facility_data.get('facZipCd', '')}")
        if facility_data.get('facZip4Cd'):
            f.write(f"-{facility_data.get('facZip4Cd')}")
        f.write("\n")
        
        # Latitude and Longitude
        f.write("\n## Geographic Coordinates\n\n")
        f.write(f"- **Latitude**: {facility_data.get('facLatDecMs', 'Not specified')}\n")
        f.write(f"- **Longitude**: {facility_data.get('facLongDecMs', 'Not specified')}\n")
        
        # LEPC Information
        f.write("\n## Local Emergency Planning Committee\n\n")
        f.write(f"- **LEPC Name**: {facility_data.get('lepcNm', 'Not specified')}\n")
        
        # Regulations
        f.write("\n## Regulatory Information\n\n")
        f.write(f"- **OSHA PSM**: {yes_no(facility_data.get('oshaPsmCd', ''))}\n")
        f.write(f"- **EPCRA 302**: {yes_no(facility_data.get('epcra302Cd', ''))}\n")
        f.write(f"- **CAA Title V**: {yes_no(facility_data.get('caaTitleVCd', ''))}\n")
        
        # Emergency Response Plan
        if facility_data.get('emergencyPlan'):
            f.write("\n## Emergency Response Plan\n\n")
            emergency_plan = facility_data.get('emergencyPlan', {})
            f.write(f"- **Community Plan**: {yes_no(emergency_plan.get('communityPlanCd', ''))}\n")
            f.write(f"- **Facility Plan**: {yes_no(emergency_plan.get('facilityPlanCd', ''))}\n")
            f.write(f"- **Response Actions**: {yes_no(emergency_plan.get('responseActionsCd', ''))}\n")
            f.write(f"- **Public Procedures**: {yes_no(emergency_plan.get('publicProceduresCd', ''))}\n")
            f.write(f"- **Healthcare**: {yes_no(emergency_plan.get('healthcareCd', ''))}\n")
            f.write(f"- **Agency Name**: {emergency_plan.get('agencyNm', 'Not specified')}\n")
            f.write(f"- **Agency Phone**: {emergency_plan.get('agencyPhoneNm', 'Not specified')}\n")
        
        # Process Chemicals
        if facility_data.get('processes'):
            f.write("\n## Process Information\n\n")
            for i, process in enumerate(facility_data.get('processes', []), 1):
                f.write(f"### Process {i}\n\n")
                f.write(f"- **Program Level**: {process.get('programLevelCd', 'Not specified')}\n")
                
                # NAICS Codes
                if process.get('processNaics'):
                    f.write("\n#### NAICS Codes\n\n")
                    for naics in process.get('processNaics', []):
                        f.write(f"- **{naics.get('naicsCd', '')}**: {naics.get('description', 'Not specified')}\n")
                
                # Chemicals
                if process.get('processChemicals'):
                    f.write("\n#### Chemicals\n\n")
                    for chemical in process.get('processChemicals', []):
                        f.write(f"- **{chemical.get('chemicalNm', 'Unknown Chemical')}** (CAS: {chemical.get('casNu', 'Not specified')})\n")
                        f.write(f"  - **Type**: {get_flam_tox(chemical.get('flamToxCd', ''))}\n")
        
        # Deregistration
        if facility_data.get('deregisteredDate'):
            f.write("\n## Deregistration\n\n")
            f.write(f"- **Deregistered Date**: {format_date(facility_data.get('deregisteredDate', ''))}\n")
    
    print(f"Generated submission page: {submission_dir}/{submission_id}.md")

def get_submission_type(code):
    """Convert submission type code to readable text."""
    types = {
        'R': 'Resubmission',
        'F': 'First Submission',
        'C': 'Correction',
    }
    return types.get(code, code)

def get_flam_tox(code):
    """Convert flammable/toxic code to readable text."""
    types = {
        'F': 'Flammable',
        'T': 'Toxic',
    }
    return types.get(code, code)

def yes_no(code):
    """Convert Y/N code to Yes/No."""
    if code == 'Y':
        return 'Yes'
    elif code == 'N':
        return 'No'
    else:
        return code

def process_state(state_code):
    """Process all facilities and submissions for a state."""
    print(f"Processing state: {state_code}")
    
    # Generate state index page
    generate_state_index(state_code)
    
    # Load state summary
    state_summary_path = f"{INPUT_DIR}/epa_state_{state_code}/summary_{state_code}.json"
    state_summary = load_json_file(state_summary_path)
    if not state_summary:
        print(f"Error: State summary file not found for {state_code}.")
        return
    
    # Process each facility
    for facility in state_summary.get('epa_facilities', []):
        epa_facility_id = facility.get('epa_facility_id', '')
        facility_name = facility.get('facility_name', 'Unknown')
        city = facility.get('city', 'Unknown')
        
        # Load submissions for this facility
        submissions_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/submissions_{epa_facility_id}.json"
        submissions_data = load_json_file(submissions_path)
        if not submissions_data:
            print(f"Warning: Submissions file not found for {facility_name} ({epa_facility_id}).")
            continue
        
        # Handle case where submissions_data might be a string
        if isinstance(submissions_data, str):
            try:
                submissions_data = json.loads(submissions_data)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse submissions data for {facility_name} ({epa_facility_id}).")
                continue
        
        # Extract submissions from _embedded key if it exists
        if "_embedded" in submissions_data:
            submissions_list = submissions_data["_embedded"]
        else:
            submissions_list = submissions_data
            
        # Generate facility index page
        generate_facility_index(state_code, epa_facility_id, facility_name, city, submissions_list)
        
        # Generate a page for each submission
        for submission in submissions_list:
            if isinstance(submission, dict):
                generate_submission_page(state_code, epa_facility_id, facility_name, submission)
            else:
                print(f"Warning: Skipping invalid submission: {submission}")

def main():
    """Main function to generate the documentation."""
    # Create output directory
    create_directory(OUTPUT_DIR)
    
    # Generate main index page
    generate_main_index()
    
    # Process each state
    master_summary = load_json_file(f"{INPUT_DIR}/master_summary.json")
    if not master_summary:
        print("Error: Master summary file not found.")
        return
    
    for state in master_summary['states']:
        state_code = state['state_code']
        process_state(state_code)
    
    print("Documentation generation complete!")

if __name__ == "__main__":
    main() 