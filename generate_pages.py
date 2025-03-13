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

FIELD_LABELS = {
    "facilityId": "Plan Sequence Number",
    "epaFacId": "EPA Facility Identifier",
    "facNm": "Facility Name",
    "parntCo1Nm": "Parent Company #1 Name",
    "facDunsNu": "Facility DUNS",
    "sbmsnTypeCd": "Submission Type",
    "facStreet1Tx": "Street 1",
    "facStreet2Tx": "Street 2",
    "facCityNm": "City",
    "facStateCd": "State",
    "countyNm": "County",
    "facZipCd": "ZIP",
    "facZip4Cd": "ZIP4",
    "receiptDa": "Receipt Date",
    "facLatDecMs": "Latitude (decimal)",
    "facLongDecMs": "Longitude (decimal)",
    "lepcNm": "LEPC",
    "oshaPsmCd": "OSHA PSM",
    "epcra302Cd": "EPCRA 302",
    "caaTitleVCd": "CAA Title V",
    "deregisteredDate": "Deregistered Date",
    "emergencyPlan.communityPlanCd": "Community Plan",
    "emergencyPlan.facilityPlanCd": "Facility Plan",
    "emergencyPlan.responseActionsCd": "Response Actions",
    "emergencyPlan.publicProceduresCd": "Public Information",
    "emergencyPlan.healthcareCd": "Healthcare",
    "emergencyPlan.agencyNm": "Agency Name",
    "emergencyPlan.agencyPhoneNm": "Agency Phone Number",
    "processes.programLevelCd": "Program Level",
    "processes.processNaics.naicsCd": "NAICS Code",
    "processes.processNaics.description": "NAICS Description",
    "processes.processChemicals.chemicalNm": "Chemical Name",
    "processes.processChemicals.casNu": "CAS Number",
    "processes.processChemicals.flamToxCd": "Flammable/Toxic",
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

def format_value(value):
    """Convert value to string, handling None and boolean-like codes."""
    if isinstance(value, list) and not value:
        return "None"
    if value is None:
        return "No records found"
    if value in ("Y", "N"):
        return "Yes" if value == "Y" else "No"
    return str(value)

def flatten_json(data, parent_key="", sep="."):
    """Flatten nested JSON, preserving links and handling arrays."""
    items = []
    links = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if key == "_links" and isinstance(value, dict):
            for link_name, link_data in value.items():
                links[new_key] = f"[{link_name}]({link_data.get('href', '')})"
        elif isinstance(value, dict):
            sub_items, sub_links = flatten_json(value, new_key, sep)
            items.extend(sub_items.items())
            links.update(sub_links)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    sub_items, sub_links = flatten_json(item, f"{new_key}[{i}]", sep)
                    items.extend(sub_items.items())
                    links.update(sub_links)
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, value))
    return dict(items), links

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
        
        sorted_states = sorted(master_summary['states'], key=lambda x: x['state_name'])
        for state in sorted_states:
            state_code = state['state_code']
            state_name = state['state_name']
            facilities = state['epa_facilities']
            submissions = state['facility_submissions']
            f.write(f"| [{state_name}](states/{state_code}/index.md) | {facilities:,} | {submissions:,} |\n")
    
    print(f"Generated main index page: {OUTPUT_DIR}/index.md")

def generate_state_index(state_code):
    """Generate an index page for a state with detailed facility table sorted by parent company and city."""
    state_summary_path = f"{INPUT_DIR}/epa_state_{state_code}/summary_{state_code}.json"
    state_summary = load_json_file(state_summary_path)
    if not state_summary:
        print(f"Error: State summary file not found for {state_code}.")
        return

    state_name = state_summary['state_name']
    total_facilities = state_summary['total_epa_facilities']
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
        f.write("| Facility Name | City | Parent Company | First Submission | Latest Submission | Submission Count |\n")
        f.write("|--------------|------|----------------|------------------|-------------------|------------------|\n")
        
        facilities_with_data = []
        for facility in state_summary.get('epa_facilities', []):
            epa_facility_id = facility.get('epa_facility_id', '')
            submissions = sorted([s for s in facility.get('submissions', []) if isinstance(s, dict)], 
                               key=lambda x: x.get('receiptDa', ''))
            submission_count = len(submissions)
            
            if submissions:
                first_submission = format_date(submissions[0].get('receiptDa', ''))
                latest_submission_id = submissions[-1].get('facilityId', '')
                latest_submission_file = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{latest_submission_id}.json"
                latest_data = load_json_file(latest_submission_file) or {}
                
                facility_name = latest_data.get('facNm', 'Unknown')
                city = latest_data.get('facCityNm', 'Unknown')
                parent_company = latest_data.get('parntCo1Nm', 'Unknown')
                latest_submission = format_date(submissions[-1].get('receiptDa', ''))
            else:
                facility_name = "Unknown"
                city = "Unknown"
                parent_company = "Unknown"
                first_submission = "N/A"
                latest_submission = "N/A"
            
            facilities_with_data.append({
                'name': facility_name,
                'city': city,
                'parent': parent_company,
                'first': first_submission,
                'latest': latest_submission,
                'count': submission_count,
                'id': epa_facility_id
            })
        
        sorted_facilities = sorted(facilities_with_data, 
                                 key=lambda x: (x['parent'].lower(), x['city'].lower()))
        
        for facility in sorted_facilities:
            f.write(f"| [{facility['name']}](facilities/{facility['id']}/index.md) | {facility['city']} | {facility['parent']} | {facility['first']} | {facility['latest']} | {facility['count']} |\n")
    
    print(f"Generated state index page for {state_name}: {state_dir}/index.md")

def generate_facility_index(state_code, epa_facility_id, facility_name, city, submissions_list):
    """Generate an index page for a facility with data from the most recent submission."""
    facility_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}"
    create_directory(facility_dir)
    create_directory(f"{facility_dir}/submissions")
    
    valid_submissions = [s for s in submissions_list if isinstance(s, dict)]
    sorted_submissions = sorted(valid_submissions, 
                              key=lambda x: x.get('receiptDa', ''), 
                              reverse=True)
    
    latest_submission = sorted_submissions[0] if sorted_submissions else {}
    latest_submission_id = latest_submission.get('facilityId', '')
    latest_submission_file = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{latest_submission_id}.json"
    latest_data = load_json_file(latest_submission_file) or {}
    
    facility_name = latest_data.get('facNm', facility_name)
    parent_company = latest_data.get('parntCo1Nm', 'Unknown')
    address_parts = [
        latest_data.get('facStreet1Tx', ''),
        latest_data.get('facStreet2Tx', ''),
        latest_data.get('facCityNm', city),
        latest_data.get('facStateCd', state_code),
        f"{latest_data.get('facZipCd', '')}-{latest_data.get('facZip4Cd', '')}" if latest_data.get('facZip4Cd') else latest_data.get('facZipCd', '')
    ]
    address = ", ".join(part for part in address_parts if part)
    
    with open(f"{facility_dir}/index.md", 'w', encoding='utf-8') as f:
        f.write(f"# {facility_name}\n\n")
        f.write(f"**Location:** {address}\n\n")
        f.write(f"**EPA Facility ID:** {epa_facility_id}\n\n")
        f.write(f"**Parent Company:** {parent_company}\n\n")
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

def generate_submission_page(state_code, epa_facility_id, facility_name, submission):
    """Generate a detailed page for a facility submission, capturing all fields."""
    if isinstance(submission, str):
        try:
            submission = json.loads(submission)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse submission data: {submission[:100]}...")
            return
    
    submission_id = submission.get('facilityId', '')
    if not submission_id:
        print(f"Warning: No facility ID found in submission data.")
        return
        
    submission_dir = f"{OUTPUT_DIR}/states/{state_code}/facilities/{epa_facility_id}/submissions"
    create_directory(submission_dir)
    
    facility_file_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/facility_{submission_id}.json"
    if not os.path.exists(facility_file_path):
        print(f"Warning: Facility file missing, skipping submission: {facility_file_path}")
        return
    
    facility_data = load_json_file(facility_file_path)
    if not facility_data:
        print(f"Warning: Failed to load facility data, skipping submission: {facility_file_path}")
        return
    
    flattened, links = flatten_json(facility_data)
    facility_name_from_data = facility_data.get('facNm', facility_name)
    
    with open(f"{submission_dir}/{submission_id}.md", 'w', encoding='utf-8') as f:
        f.write(f"# {facility_name_from_data} - Submission {submission_id}\n\n")
        f.write(f"[← Back to Facility Index](../index.md)\n\n")
        
        if "" in links:
            f.write("## Links\n")
            f.write(f"- {links['']}\n\n")
        
        f.write("## Facility Details\n")
        mapped_keys = set()
        for key in ["facNm", "parntCo1Nm", "sbmsnTypeCd", "receiptDa", "epaFacId", "facDunsNu", 
                    "facStreet1Tx", "facStreet2Tx", "facCityNm", "facStateCd", "facZipCd", 
                    "facZip4Cd", "countyNm", "facLatDecMs", "facLongDecMs", "lepcNm", 
                    "oshaPsmCd", "epcra302Cd", "caaTitleVCd", "facilityId", "deregisteredDate"]:
            if key in flattened:
                label = FIELD_LABELS.get(key, key)
                value = format_value(flattened[key])
                f.write(f"- **{label}:** {value}\n")
                mapped_keys.add(key)
        
        if "processes" in facility_data:
            f.write("\n## Process Information\n")
            for i, process in enumerate(facility_data.get("processes", [])):
                f.write(f"### Process {i + 1}\n")
                process_flattened, process_links = flatten_json(process)
                for key, value in process_flattened.items():
                    if key.startswith(f"processes[{i}]"):
                        subkey = key[len(f"processes[{i}]."):]
                        label = FIELD_LABELS.get(f"processes.{subkey}", subkey)
                        f.write(f"- **{label}:** {format_value(value)}\n")
                if f"processes[{i}]" in links:
                    f.write(f"- **Links:** {links[f'processes[{i}]']}\n")
        
        if "emergencyPlan" in facility_data:
            f.write("\n## Emergency Response\n")
            emergency_keys = ["communityPlanCd", "facilityPlanCd", "responseActionsCd", 
                            "publicProceduresCd", "healthcareCd", "agencyNm", "agencyPhoneNm"]
            mapped_emergency = set()
            for key in emergency_keys:
                full_key = f"emergencyPlan.{key}"
                if full_key in flattened:
                    label = FIELD_LABELS.get(full_key, key)
                    value = format_value(flattened[full_key])
                    f.write(f"- **{label}:** {value}\n")
                    mapped_emergency.add(full_key)
            
            for key, value in flattened.items():
                if (key.startswith("emergencyPlan") and key not in mapped_emergency and 
                    not key.startswith("emergencyPlan._links")):
                    label = FIELD_LABELS.get(key, key.split(".", 1)[1])
                    f.write(f"- **{label}:** {format_value(value)}\n")
            if "emergencyPlan" in links:
                f.write(f"- **Links:** {links['emergencyPlan']}\n")
        
        # Capture all unmapped fields under Other
        unmapped_fields = [(k, v) for k, v in flattened.items() if (k not in mapped_keys and 
                                                                  not k.startswith("processes") and 
                                                                  not k.startswith("emergencyPlan") and 
                                                                  not k.startswith("_links"))]
        if unmapped_fields:
            f.write("\n## Other\n")
            for key, value in unmapped_fields:
                label = FIELD_LABELS.get(key, key)
                f.write(f"- **{label}:** {format_value(value)}\n")
        
        f.write(f"\n*Data displayed is accurate as of 12:00 AM (EST) {datetime.now().strftime('%b %d, %Y')}*")
    
    print(f"Generated submission page: {submission_dir}/{submission_id}.md")

def process_state(state_code):
    """Process all facilities and submissions for a state."""
    print(f"Processing state: {state_code}")
    generate_state_index(state_code)
    
    state_summary_path = f"{INPUT_DIR}/epa_state_{state_code}/summary_{state_code}.json"
    state_summary = load_json_file(state_summary_path)
    if not state_summary:
        return
    
    for facility in state_summary.get('epa_facilities', []):
        epa_facility_id = facility.get('epa_facility_id', '')
        facility_name = facility.get('facility_name', 'Unknown')
        city = facility.get('city', 'Unknown')
        
        submissions_path = f"{INPUT_DIR}/epa_state_{state_code}/facility_{epa_facility_id}/submissions_{epa_facility_id}.json"
        submissions_data = load_json_file(submissions_path)
        if not submissions_data:
            print(f"Warning: Submissions file not found for {facility_name} ({epa_facility_id}).")
            continue
        
        if isinstance(submissions_data, str):
            try:
                submissions_data = json.loads(submissions_data)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse submissions data for {facility_name} ({epa_facility_id}).")
                continue
        
        submissions_list = submissions_data["_embedded"] if "_embedded" in submissions_data else submissions_data
        generate_facility_index(state_code, epa_facility_id, facility_name, city, submissions_list)
        
        for submission in submissions_list:
            if isinstance(submission, dict):
                generate_submission_page(state_code, epa_facility_id, facility_name, submission)

def main():
    """Main function to generate the documentation."""
    create_directory(OUTPUT_DIR)
    generate_main_index()
    
    master_summary = load_json_file(f"{INPUT_DIR}/master_summary.json")
    if not master_summary:
        return
    
    for state in master_summary['states']:
        process_state(state['state_code'])
    
    print("Documentation generation complete!")

if __name__ == "__main__":
    main()