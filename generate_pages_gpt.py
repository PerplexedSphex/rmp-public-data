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

def print_recursive_links(f, data, printed=None):
    """
    Recursively print any _links entries found in data.
    This function collects all link entries from nested structures.
    """
    if printed is None:
        printed = set()
    if isinstance(data, dict):
        if "_links" in data:
            for key, link_obj in data["_links"].items():
                if isinstance(link_obj, dict):
                    href = link_obj.get("href")
                    if href and href not in printed:
                        f.write(f"- **{key}**: [Link]({href})\n")
                        printed.add(href)
                elif isinstance(link_obj, list):
                    for item in link_obj:
                        href = item.get("href")
                        if href and href not in printed:
                            f.write(f"- **{key}**: [Link]({href})\n")
                            printed.add(href)
        for v in data.values():
            print_recursive_links(f, v, printed)
    elif isinstance(data, list):
        for item in data:
            print_recursive_links(f, item, printed)

def print_additional_fields(f, data, printed_keys, indent=0):
    """Recursively print any keys not already printed."""
    indent_str = "  " * indent
    for key, value in data.items():
        if key in printed_keys:
            continue
        if isinstance(value, dict):
            f.write(f"{indent_str}- **{key}**:\n")
            print_additional_fields(f, value, set(), indent+1)
        else:
            f.write(f"{indent_str}- **{key}**: {value}\n")

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

def generate_state_index_updated(state_code, state_name, facility_summaries):
    """Generate a state index page with a detailed facility table."""
    # Sort by parent company name then city
    sorted_facilities = sorted(facility_summaries, key=lambda x: ((x['parent_co'] or '').lower(), (x['city'] or '').lower()))
    state_dir = f"{OUTPUT_DIR}/states/{state_code}"
    create_directory(state_dir)
    
    with open(f"{state_dir}/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# {state_name} EPA RMP Facilities\n\n")
        f.write(f"[← Back to Main Index](../../index.md)\n\n")
        total_facilities = len(facility_summaries)
        total_submissions = sum(item['submission_count'] for item in facility_summaries)
        f.write("## Summary\n\n")
        f.write(f"- **State**: {state_name}\n")
        f.write(f"- **Total Facilities**: {total_facilities}\n")
        f.write(f"- **Total Submissions**: {total_submissions}\n\n")
        
        f.write("## Facilities\n\n")
        f.write("| Facility Name | Parent Co Name | City | First Submission | Latest Submission | Submission Count |\n")
        f.write("|---------------|----------------|------|------------------|-------------------|------------------|\n")
        
        for facility in sorted_facilities:
            first_date = format_date(facility['first_submission'])
            latest_date = format_date(facility['latest_submission'])
            f.write(f"| [{facility['facility_name']}](facilities/{facility['epa_facility_id']}/index.md) | {facility['parent_co']} | {facility['city']} | {first_date} | {latest_date} | {facility['submission_count']} |\n")
    
    print(f"Generated state index page for {state_name}: {state_dir}/index.md")

def generate_facility_index(state_code, epa_facility_id, default_facility_name, default_city, submissions_list):
    """
    Generate an index page for a facility with links to all submissions.
    This version uses the detailed facility file (from the latest submission) to set facility-level data.
    """
    facility_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}"
    create_directory(facility_dir)
    create_directory(f"{facility_dir}/submissions")
    
    # Filter and sort valid submissions
    valid_submissions = [item for item in submissions_list if isinstance(item, dict)]
    sorted_submissions = sorted(valid_submissions, key=lambda x: x.get('receiptDa', ''), reverse=True)
    
    # Use detailed facility data from the latest submission file
    facility_name = default_facility_name
    city = default_city
    if sorted_submissions:
        latest_submission_id = sorted_submissions[0].get('facilityId', '')
        detailed_file_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{latest_submission_id}.json"
        detailed_data = load_json_file(detailed_file_path)
        if detailed_data:
            facility_name = detailed_data.get('facNm') or facility_name
            city = detailed_data.get('facCityNm') or city
    
    with open(f"{facility_dir}/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# {facility_name}\n\n")
        f.write(f"**Location:** {city}, {state_code}\n\n")
        f.write(f"**EPA Facility ID:** {epa_facility_id}\n\n")
        f.write(f"[Back to {state_code} Index](../../index.md)\n\n")
        
        f.write("## Submissions\n\n")
        f.write("| Date | Submission ID | Document Control Number |\n")
        f.write("|------|--------------|-------------------------|\n")
        
        for submission in sorted_submissions:
            submission_id = submission.get('facilityId', '')
            receipt_date = format_date(submission.get('receiptDa', ''))
            doc_control_num = submission.get('documentControlNumber', '')
            f.write(f"| [{receipt_date}](submissions/{submission_id}.md) | {submission_id} | {doc_control_num} |\n")
    
    print(f"Generated facility index page for {facility_name}: {facility_dir}/index.md")

def generate_submission_page(state_code, epa_facility_id, default_facility_name, submission):
    """
    Generate a detailed page for a facility submission.
    This page loads the detailed facility file and prints nested links in relevant sections.
    """
    if isinstance(submission, str):
        try:
            submission = json.loads(submission)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse submission data: {submission[:100]}...")
            return
    
    submission_id = submission.get('facilityId', '')
    if not submission_id:
        print("Warning: No facility ID found in submission data.")
        return
        
    submission_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}/submissions"
    create_directory(submission_dir)
    
    # Load the detailed facility data (authoritative source)
    facility_file_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{submission_id}.json"
    detailed_data = load_json_file(facility_file_path)
    if not detailed_data:
        print(f"Warning: Facility data file not found: {facility_file_path}")
        return
    
    with open(f"{submission_dir}/{submission_id}.md", 'w', encoding='utf-8') as f:
        facility_name = detailed_data.get('facNm') or default_facility_name
        f.write(f"# {facility_name} - Submission {submission_id}\n\n")
        f.write(f"[← Back to Facility Index](../index.md)\n\n")
        
        # Registration Information
        f.write("## Registration Information\n\n")
        f.write(f"- **EPA Facility ID**: {detailed_data.get('epaFacId', '')}\n")
        f.write(f"- **Facility ID**: {submission_id}\n")
        f.write(f"- **Submission Type**: {get_submission_type(detailed_data.get('sbmsnTypeCd', ''))}\n")
        f.write(f"- **Receipt Date**: {format_date(detailed_data.get('receiptDa', ''))}\n")
        f.write(f"- **Parent Company**: {detailed_data.get('parntCo1Nm', 'Not specified')}\n")
        
        # Facility Identification
        f.write("\n## Facility Identification\n\n")
        f.write(f"- **Facility Name**: {facility_name}\n")
        f.write(f"- **DUNS Number**: {detailed_data.get('facDunsNu', 'Not specified')}\n")
        
        # Location
        f.write("\n## Location\n\n")
        street = detailed_data.get('facStreet1Tx', '')
        if detailed_data.get('facStreet2Tx'):
            street += ", " + detailed_data.get('facStreet2Tx')
        f.write(f"- **Street Address**: {street}\n")
        f.write(f"- **City**: {detailed_data.get('facCityNm', '')}\n")
        f.write(f"- **State**: {detailed_data.get('facStateCd', '')}\n")
        f.write(f"- **County**: {detailed_data.get('countyNm', '')}\n")
        zip_str = detailed_data.get('facZipCd', '')
        if detailed_data.get('facZip4Cd'):
            zip_str += "-" + detailed_data.get('facZip4Cd')
        f.write(f"- **ZIP Code**: {zip_str}\n")
        
        # Geographic Coordinates
        f.write("\n## Geographic Coordinates\n\n")
        f.write(f"- **Latitude**: {detailed_data.get('facLatDecMs', 'Not specified')}\n")
        f.write(f"- **Longitude**: {detailed_data.get('facLongDecMs', 'Not specified')}\n")
        
        # LEPC Information
        f.write("\n## Local Emergency Planning Committee\n\n")
        f.write(f"- **LEPC Name**: {detailed_data.get('lepcNm', 'Not specified')}\n")
        
        # Regulatory Information
        f.write("\n## Regulatory Information\n\n")
        f.write(f"- **OSHA PSM**: {yes_no(detailed_data.get('oshaPsmCd', ''))}\n")
        f.write(f"- **EPCRA 302**: {yes_no(detailed_data.get('epcra302Cd', ''))}\n")
        f.write(f"- **CAA Title V**: {yes_no(detailed_data.get('caaTitleVCd', ''))}\n")
        
        # Emergency Response Plan
        if detailed_data.get('emergencyPlan'):
            f.write("\n## Emergency Response Plan\n\n")
            ep = detailed_data.get('emergencyPlan', {})
            f.write(f"- **Community Plan**: {yes_no(ep.get('communityPlanCd', ''))}\n")
            f.write(f"- **Facility Plan**: {yes_no(ep.get('facilityPlanCd', ''))}\n")
            f.write(f"- **Response Actions**: {yes_no(ep.get('responseActionsCd', ''))}\n")
            f.write(f"- **Public Procedures**: {yes_no(ep.get('publicProceduresCd', ''))}\n")
            f.write(f"- **Healthcare**: {yes_no(ep.get('healthcareCd', ''))}\n")
            f.write(f"- **Agency Name**: {ep.get('agencyNm', 'Not specified')}\n")
            f.write(f"- **Agency Phone**: {ep.get('agencyPhoneNm', 'Not specified')}\n")
        
        # Process Information (including NAICS and Chemicals with links)
        if detailed_data.get('processes'):
            f.write("\n## Process Information\n\n")
            for i, process in enumerate(detailed_data.get('processes', []), 1):
                f.write(f"### Process {i}\n\n")
                f.write(f"- **Program Level**: {process.get('programLevelCd', 'Not specified')}\n")
                
                # NAICS Codes
                if process.get('processNaics'):
                    f.write("\n#### NAICS Codes\n\n")
                    for naics in process.get('processNaics', []):
                        code = naics.get('naicsCd', '')
                        desc = naics.get('description', 'Not specified')
                        naics_line = f"- **{code}**: {desc}"
                        # Add link if available
                        naics_link = naics.get('_links', {}).get('naics', {}).get('href', '')
                        if naics_link:
                            naics_line += f" ([Link]({naics_link}))"
                        f.write(naics_line + "\n")
                
                # Process Chemicals
                if process.get('processChemicals'):
                    f.write("\n#### Chemicals\n\n")
                    for chemical in process.get('processChemicals', []):
                        chem_name = chemical.get('chemicalNm', 'Unknown Chemical')
                        cas = chemical.get('casNu', 'Not specified')
                        chem_line = f"- **{chem_name}** (CAS: {cas})"
                        chem_link = chemical.get('_links', {}).get('chemical', {}).get('href', '')
                        if chem_link:
                            chem_line += f" ([Link]({chem_link}))"
                        f.write(chem_line + "\n")
                        f.write(f"  - **Type**: {get_flam_tox(chemical.get('flamToxCd', ''))}\n")
        
        # Deregistration
        if detailed_data.get('deregisteredDate'):
            f.write("\n## Deregistration\n\n")
            f.write(f"- **Deregistered Date**: {format_date(detailed_data.get('deregisteredDate', ''))}\n")
        
        # Additional Links: Recursively print any remaining _links not already included
        f.write("\n## Additional Links\n\n")
        print_recursive_links(f, detailed_data)
        
        # Additional Data: print any keys not explicitly handled
        printed_keys = {
            'epaFacId', 'facilityId', 'sbmsnTypeCd', 'receiptDa', 'parntCo1Nm', 
            'facNm', 'facDunsNu', 'facStreet1Tx', 'facStreet2Tx', 'facCityNm', 
            'facStateCd', 'countyNm', 'facZipCd', 'facZip4Cd', 'facLatDecMs', 
            'facLongDecMs', 'lepcNm', 'oshaPsmCd', 'epcra302Cd', 'caaTitleVCd', 
            'deregisteredDate', 'emergencyPlan', 'processes', '_links'
        }
        f.write("\n## Additional Data\n\n")
        print_additional_fields(f, detailed_data, printed_keys)
    
    print(f"Generated submission page: {submission_dir}/{submission_id}.md")

def process_state(state_code):
    """Process all facilities and submissions for a state."""
    print(f"Processing state: {state_code}")
    
    state_summary_path = f"{INPUT_DIR}/epa_state_{state_code}/summary_{state_code}.json"
    state_summary = load_json_file(state_summary_path)
    if not state_summary:
        print(f"Error: State summary file not found for {state_code}.")
        return
    
    state_name = state_summary.get('state_name', STATE_NAMES.get(state_code, state_code))
    facility_summary_list = []
    
    # Process each facility in the state summary
    for facility in state_summary.get('epa_facilities', []):
        epa_facility_id = facility.get('epa_facility_id', '')
        submissions_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/submissions_{epa_facility_id}.json"
        submissions_data = load_json_file(submissions_path)
        if not submissions_data:
            print(f"Warning: Submissions file not found for facility {epa_facility_id}.")
            continue
        
        if isinstance(submissions_data, str):
            try:
                submissions_data = json.loads(submissions_data)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse submissions data for facility {epa_facility_id}.")
                continue
        
        submissions_list = submissions_data.get("_embedded", submissions_data)
        valid_submissions = [item for item in submissions_list if isinstance(item, dict)]
        if not valid_submissions:
            continue
        
        sorted_submissions = sorted(valid_submissions, key=lambda x: x.get('receiptDa',''), reverse=True)
        latest_submission = sorted_submissions[0]
        latest_submission_id = latest_submission.get('facilityId', '')
        # Load detailed facility file to get authoritative values
        detailed_file_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{latest_submission_id}.json"
        detailed_data = load_json_file(detailed_file_path)
        if detailed_data:
            updated_facility_name = detailed_data.get('facNm') or facility.get('facility_name', 'Unknown')
            updated_city = detailed_data.get('facCityNm') or facility.get('city', 'Unknown')
            parent_co = detailed_data.get('parntCo1Nm') or ''
        else:
            updated_facility_name = facility.get('facility_name', 'Unknown')
            updated_city = facility.get('city', 'Unknown')
            parent_co = ""
        
        first_submission_date = min(valid_submissions, key=lambda x: x.get('receiptDa','')).get('receiptDa','')
        latest_submission_date = latest_submission.get('receiptDa','')
        submission_count = len(valid_submissions)
        
        facility_summary = {
            "epa_facility_id": epa_facility_id,
            "facility_name": updated_facility_name,
            "parent_co": parent_co,
            "city": updated_city,
            "first_submission": first_submission_date,
            "latest_submission": latest_submission_date,
            "submission_count": submission_count,
            "submissions_list": valid_submissions
        }
        facility_summary_list.append(facility_summary)
        
        # Generate facility index page using detailed data
        generate_facility_index(state_code, epa_facility_id, updated_facility_name, updated_city, valid_submissions)
        
        # Generate a page for each submission
        for submission in valid_submissions:
            generate_submission_page(state_code, epa_facility_id, updated_facility_name, submission)
    
    # Generate updated state index with detailed facility table
    generate_state_index_updated(state_code, state_name, facility_summary_list)

def main():
    """Main function to generate the documentation."""
    create_directory(OUTPUT_DIR)
    generate_main_index()
    
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
