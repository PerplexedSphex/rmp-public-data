# EPA RMP State Facility Search

This script searches for EPA RMP facilities by state and retrieves comprehensive data for all facilities found.

## Overview

The `epa_state_search.py` script provides a powerful way to search for and retrieve data from the EPA's Risk Management Plan (RMP) Program Delivery System API. It follows a three-level approach:

1. **State Search**: Searches for all facilities in a specified state
2. **EPA Facility ID Processing**: For each unique EPA Facility ID found, retrieves all facility submissions
3. **Facility Data Retrieval**: For each facility submission, retrieves detailed facility information

This hierarchical approach allows for comprehensive data collection and organization.

## Features

- Searches for all facilities in a specified state using the EPA RMP API
- Extracts unique EPA Facility IDs from the search results
- Retrieves all facility submissions for each EPA Facility ID
- Fetches detailed information for each facility submission
- Organizes data in a hierarchical directory structure
- Creates a summary file with key information about all facilities
- Supports command-line arguments to specify different states
- Implements rate limiting to avoid overwhelming the API

## Requirements

- Python 3.x
- Required packages:
  - requests
  - python-dotenv
  - time

## Installation

1. Ensure you have Python 3.x installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python epa_state_search.py
```

This will search for facilities in the default state "GU" (Guam).

### Specifying a State

```bash
python epa_state_search.py [state_code]
```

Replace `[state_code]` with a valid 2-letter US state or territory code (e.g., "CA" for California, "TX" for Texas).

### Output

The script creates a hierarchical directory structure:

```
epa_state_[state_code]/
├── state_search_[state_code].json       # Initial state search results
├── summary_[state_code].json            # Summary of all facilities
└── facility_[epa_facility_id]/          # One directory per EPA Facility ID
    ├── submissions_[epa_facility_id].json  # Submissions for this EPA Facility ID
    ├── facility_[facility_id_1].json       # Detailed data for each facility submission
    ├── facility_[facility_id_2].json
    └── ...
```

## API Endpoints

The script uses three EPA RMP API endpoints:

1. State search endpoint (POST):
   ```
   https://cdxapps.epa.gov/olem-rmp-pds/api/search
   ```

2. Submissions search endpoint (GET):
   ```
   https://cdxapps.epa.gov/olem-rmp-pds/api/search/submissions?id={epa_facility_id}
   ```

3. Facility endpoint (GET):
   ```
   https://cdxapps.epa.gov/olem-rmp-pds/api/facilities/{facility_id}
   ```

## Data Structure

### State Search Results

The state search returns a list of facilities with basic information:
- `facilityId`: The facility's unique identifier
- `epaFacId`: The EPA's facility identifier
- `facName`: The facility name
- `city`: The city where the facility is located
- `state`: The state code
- `county`: The county name
- `facLatDecMs`/`facLongDecMs`: Latitude and longitude coordinates

### Facility Data

The facility endpoint returns detailed information:
- Basic facility details (name, location, contact info)
- Emergency plan information
- Process details
- Chemical inventories

### Summary File

The summary file provides an overview of all facilities found:
- Total number of EPA Facility IDs
- For each EPA Facility ID:
  - Total number of submissions
  - Basic information about each submission

## License

[Add your license information here] 