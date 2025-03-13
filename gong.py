import requests
import json
import base64
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

def load_credentials() -> dict:
    """
    Load Gong API credentials from environment variables.
    
    Expected environment variables:
    - GONG_BASE_URL: Base URL for Gong API
    - GONG_ACCESS_KEY: Access key for authentication
    - GONG_ACCESS_KEY_SECRET: Access key secret for authentication
    
    Returns:
        dict: Dictionary containing credentials
    """
    creds = {
        'base_url': os.getenv('GONG_BASE_URL'),
        'access_key': os.getenv('GONG_ACCESS_KEY'),
        'access_key_secret': os.getenv('GONG_ACCESS_KEY_SECRET')
    }
    
    # Validate that all required credentials are provided
    if not all(creds.values()):
        missing = [k for k, v in creds.items() if not v]
        raise Exception(f"Missing environment variables: {', '.join(missing)}")
    
    return creds

def get_auth_headers() -> dict:
    """
    Create authorization headers for Gong API requests.
    
    Returns:
        dict: Headers including authorization
    """
    creds = load_credentials()
    token = base64.b64encode(f"{creds['access_key']}:{creds['access_key_secret']}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    return headers, creds['base_url']

def find_call_ids_from_csv(filters: dict) -> List[str]:
    """
    Read CSV file and filter calls based on criteria.
    
    Args:
        filters (dict): Filter criteria which may include:
            - account_name: Filter by account name
            - min_duration_minutes: Filter by minimum duration in minutes
            - title: Filter by call title
            - host: Filter by call host
            - last_days: Filter calls from last X days
            - call_ids: Directly provide call IDs to use
            
    Returns:
        List[str]: List of call IDs that match the criteria
    """
    try:
        # If call_ids are directly provided, use them
        if 'call_ids' in filters:
            return filters['call_ids']

        csv_files = [f for f in os.listdir('.') if f.startswith('Extensive_Call_Data_') and f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No Extensive Call Data CSV files found")
        
        latest_csv = max(csv_files)
        print(f"Reading file: {latest_csv}")
        
        # Add low_memory=False to handle mixed data types
        df = pd.read_csv(latest_csv, low_memory=False)
        
        # Convert 'Recorded Date' to datetime right away
        df['Recorded Date'] = pd.to_datetime(df['Recorded Date'], format='%m-%d-%Y %H:%M:%S')
        
        # Start with all rows
        mask = pd.Series(True, index=df.index)
        
        # Apply account filter if provided
        if filters.get('account_name'):
            account_mask = (
                df['CRM - Account 1 Name'].str.contains(filters['account_name'], case=False, na=False) |
                df['CRM - Account 2 Name'].str.contains(filters['account_name'], case=False, na=False) |
                df['CRM - Account 3 Name'].str.contains(filters['account_name'], case=False, na=False)
            )
            mask &= account_mask
        
        # Apply duration filter if provided
        if filters.get('min_duration_minutes'):
            duration_mask = df['Duration (Sec.)'] >= filters['min_duration_minutes'] * 60
            mask &= duration_mask
        
        # Apply title filter if provided
        if filters.get('title'):
            title_mask = df['Call Title'].str.contains(filters['title'], case=False, na=False)
            mask &= title_mask
        
        # Apply host filter if provided
        if filters.get('host'):
            host_mask = df['Host'].str.contains(filters['host'], case=False, na=False)
            mask &= host_mask
        
        # Apply days filter if provided
        if filters.get('last_days'):
            cutoff_date = datetime.now() - timedelta(days=filters['last_days'])
            days_mask = df['Recorded Date'] >= cutoff_date
            mask &= days_mask
        
        filtered_df = df[mask].sort_values('Recorded Date', ascending=False)
        call_ids = filtered_df['Gong Internal Call ID'].str.replace('_', '').tolist()
        
        print(f"\nFound {len(call_ids)} calls matching the filter criteria")
        if len(call_ids) > 0:
            print(f"Date range: {filtered_df['Recorded Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Recorded Date'].max().strftime('%Y-%m-%d')}")
            print("\nMatched calls:")
            for _, row in filtered_df.iterrows():
                print(f"{row['Recorded Date']} - {row['Call Title']}")
        
        return call_ids
        
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return []

def get_call_data(call_ids: List[str]) -> Optional[dict]:
    """
    Retrieves extensive metadata for specified calls.
    
    Args:
        call_ids (List[str]): List of call IDs to retrieve data for
        
    Returns:
        Optional[dict]: Call data or None if error
    """
    if not call_ids:
        return None
        
    headers, base_url = get_auth_headers()
    url = f"{base_url}/v2/calls/extensive"
    
    data = {
        "filter": {
            "fromDateTime": "2022-01-01T00:00:00Z",
            "toDateTime": "2024-12-31T23:59:59Z",
            "callIds": call_ids 
        },
        "contentSelector": {
            "context": "Extended",
            "exposedFields": {
                "parties": True,
                "content": {
                    "structure": True,
                    "topics": True,
                    "trackers": True,
                    "trackerOccurrences": True,
                    "pointsOfInterest": True,
                    "brief": True,
                    "outline": True,
                    "highlights": True,
                    "callOutcome": True,
                    "keyPoints": True
                },
                "interaction": {
                    "speakers": True,
                    "video": True,
                    "personInteractionStats": True,
                    "questions": True
                },
                "collaboration": {"publicComments": True},
                "media": True  
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error retrieving call data: {response.status_code} - {response.text}")
        return None

def get_call_transcripts(call_ids: List[str]) -> Optional[Dict[str, dict]]:
    """
    Retrieves transcripts for multiple call IDs.
    
    Args:
        call_ids (List[str]): List of call IDs to retrieve transcripts for
        
    Returns:
        Optional[Dict[str, dict]]: Transcript data mapped by call ID or None if error
    """
    if not call_ids:
        return None
        
    headers, base_url = get_auth_headers()
    url = f"{base_url}/v2/calls/transcript"
    
    data = {
        "filter": {
            "fromDateTime": "2022-01-01T00:00:00Z",
            "toDateTime": "2024-12-31T23:59:59Z",
            "callIds": call_ids
        }
    }
    
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return {
            transcript["callId"]: transcript
            for transcript in response.json().get("callTranscripts", [])
        }
    else:
        print(f"Error retrieving transcripts: {response.status_code} - {response.text}")
        return None

def milliseconds_to_minutes_seconds(ms: int) -> str:
    """
    Convert milliseconds to MM:SS format.
    
    Args:
        ms (int): Time in milliseconds
        
    Returns:
        str: Formatted time string
    """
    total_seconds = ms / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_call_data(data: dict) -> str:
    """
    Format call data into a markdown document.
    
    Args:
        data (dict): Dictionary containing call metadata and transcript
        
    Returns:
        str: Formatted call data as markdown text
    """
    output = []
    
    try:
        call_meta = data['metadata']['metaData']
        call_id = call_meta.get('id', 'unknown_id')
        call_title = call_meta.get('title', 'Unknown Title')
        print(f"\nProcessing call: {call_title} (ID: {call_id})")
        
        # Create speaker ID to name mapping
        print("Processing parties data...")
        speaker_map = {}
        for party in data['metadata']['parties']:
            if 'speakerId' in party:
                # Try to get name from different possible fields
                name = party.get('name') or party.get('displayName') or party.get('email', 'Unknown Speaker')
                speaker_map[party['speakerId']] = name
        
        # Format basic call info
        output.extend([
            "<call>",
            "",  # Add newline
            "# Call Details\n",
            f"- **Title**: {call_meta.get('title', 'Unknown Title')}",
            f"- **Date**: {call_meta.get('scheduled', 'Unknown')}",
            f"- **Duration**: {call_meta.get('duration', 'Unknown')} seconds",
            f"- **System**: {call_meta.get('system', 'Unknown')}",
            f"- **Scope**: {call_meta.get('scope', 'Unknown')}",
            "\n</call>",
            ""  # Add newline
        ])

        # Format participants
        output.extend([
            "<participants>",
            "",  # Add newline
            "# Participants\n"
        ])
        for party in data['metadata']['parties']:
            output.extend([
                f"## {party.get('name', 'Unknown Name')}",
                f"- **Role**: {party.get('title', 'Unknown')}",
                f"- **Email**: {party.get('emailAddress', 'Unknown')}",
                f"- **Affiliation**: {party.get('affiliation', 'Unknown')}"
            ])
            if party.get('phoneNumber'):
                output.append(f"- **Phone**: {party['phoneNumber']}")
            if party.get('speakerId'):
                output.append(f"- **Speaker ID**: {party['speakerId']}")
            output.append("")
        output.extend([
            "</participants>",
            ""  # Add newline
        ])

        # Format Salesforce data if available
        if 'context' in data['metadata']:
            for context in data['metadata']['context']:
                if context['system'] == 'Salesforce':
                    for obj in context['objects']:
                        output.extend([
                            f"<{obj['objectType'].lower()}>",
                            "",  # Add newline
                            f"# {obj['objectType']} Details\n"
                        ])
                        output.extend([
                            f"- **{field['name']}**: {field['value']}"
                            for field in obj['fields']
                            if field['value'] is not None
                        ])
                        output.extend([
                            "",
                            f"</{obj['objectType'].lower()}>",
                            ""  # Add newline
                        ])

        # Format transcript
        output.extend([
            "<transcript>",
            "",  # Add newline
            "# Conversation Transcript\n"
        ])
        
        for segment in data['transcript']['transcript']:
            speaker_name = speaker_map.get(segment['speakerId'], f"Unknown Speaker ({segment['speakerId']})")
            
            for sentence in segment['sentences']:
                start_time = milliseconds_to_minutes_seconds(sentence['start'])
                output.append(f"[{start_time}] **{speaker_name}**: {sentence['text']}")
            output.append("")
        
        output.extend([
            "</transcript>",
            ""  # Add newline
        ])
        
        return "\n".join(output)
        
    except Exception as e:
        error_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = f"error_log_{error_time}_{call_id}.json"
        
        print(f"\nError in format_call_data for call: {call_title} (ID: {call_id})")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Writing error details to: {error_file}")
        
        error_data = {
            "error_type": str(type(e).__name__),
            "error_message": str(e),
            "call_data": data
        }
        
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)
        
        raise

def process_calls(filters: dict) -> Tuple[str, int]:
    """
    Process all calls matching the filters and generate formatted output.
    
    Args:
        filters (dict): Dictionary of filters to select calls
        
    Returns:
        Tuple[str, int]: Formatted output and count of processed calls
    """
    # Get call IDs from CSV
    call_ids = find_call_ids_from_csv(filters)
    if not call_ids:
        return "", 0

    # Get call data and transcripts
    extensive_metadata = get_call_data(call_ids)
    transcripts = get_call_transcripts(call_ids)

    if not extensive_metadata or not transcripts:
        print("Failed to retrieve metadata or transcripts.")
        return "", 0

    # Process each call
    all_outputs = []
    processed_count = 0
    
    for call in extensive_metadata.get("calls", []):
        try:
            call_id = call["metaData"]["id"]
            call_title = call["metaData"].get("title", "Unknown Title")
            print(f"\nProcessing call ID: {call_id}")
            print(f"Title: {call_title}")
            
            transcript = transcripts.get(call_id)
            if transcript:
                formatted_output = format_call_data({
                    "metadata": call,
                    "transcript": transcript
                })
                all_outputs.append(formatted_output)
                processed_count += 1
                print(f"Successfully processed call: {call_title}")
            else:
                print(f"No transcript found for call: {call_title} (ID: {call_id})")
                
        except Exception as e:
            print(f"\nError processing call: {call_title} (ID: {call_id})")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            continue

    # Create output directory if it doesn't exist
    os.makedirs('cleaned-transcripts', exist_ok=True)
    
    # Write combined output
    output_filename = "filtered_calls.md"
    if 'call_ids' in filters:
        output_filename = f"selected_calls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    else:
        filter_parts = []
        if filters.get('account_name'): filter_parts.append(filters['account_name'])
        if filters.get('title'): filter_parts.append(filters['title'])
        if filters.get('host'): filter_parts.append(filters['host'])
        if filters.get('last_days'): filter_parts.append(f"last{filters['last_days']}days")
        
        if filter_parts:
            output_filename = f"{'_'.join(filter_parts).replace(' ', '_').lower()}_calls.md"
    
    # Prepend the cleaned-transcripts directory to the output path
    output_path = os.path.join('cleaned-transcripts', output_filename)
    
    combined_output = "\n\n---\n\n".join(all_outputs)
    with open(output_path, 'w') as f:
        f.write(combined_output)
    
    print(f"\nOutput written to {os.path.abspath(output_path)}")
    return combined_output, processed_count

def process_single_call(call_id: str) -> str:
    """
    Process a single call and return the formatted output.
    
    Args:
        call_id (str): Call ID to process
        
    Returns:
        str: Formatted call data as markdown text
    """
    # Get call data and transcript
    extensive_metadata = get_call_data([call_id])
    transcripts = get_call_transcripts([call_id])

    if not extensive_metadata or not transcripts or call_id not in transcripts:
        print("Failed to retrieve metadata or transcript.")
        return ""

    call = extensive_metadata.get("calls", [])[0] if extensive_metadata.get("calls") else None
    
    if not call:
        print(f"No call data found for call ID: {call_id}")
        return ""
    
    transcript = transcripts.get(call_id)
    if not transcript:
        print(f"No transcript found for call ID: {call_id}")
        return ""
    
    try:
        formatted_output = format_call_data({
            "metadata": call,
            "transcript": transcript
        })
        return formatted_output
    except Exception as e:
        print(f"Error processing call: {str(e)}")
        return ""

# Example usage:
# 1. Set up .env file with:
# GONG_BASE_URL=https://your-company.gong.io/v2
# GONG_ACCESS_KEY=your_access_key
# GONG_ACCESS_KEY_SECRET=your_access_key_secret
#
# 2. Find call IDs from CSV:
# call_ids = find_call_ids_from_csv({'account_name': 'Acme Corp', 'last_days': 30})
#
# 3. Process a single call:
# call_markdown = process_single_call('1234567890')
#
# 4. Process multiple calls with filters:
# output, count = process_calls({'account_name': 'Acme Corp', 'last_days': 30})