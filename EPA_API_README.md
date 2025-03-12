# EPA RMP Facility Data Retrieval

This script fetches facility data from the EPA's Risk Management Plan (RMP) Program Delivery System API.

## Overview

The `epa_facility_data.py` script retrieves detailed information about facilities registered in the EPA's Risk Management Plan (RMP) database. It first searches for all facility submissions associated with a specific EPA Facility ID, then retrieves detailed information for each facility. This provides a comprehensive way to access facility information, emergency plans, processes, and chemicals stored at these facilities.

## Features

- Searches for all facility submissions associated with an EPA Facility ID
- Retrieves comprehensive facility data for each submission from the EPA RMP API
- Displays formatted information about each facility, including:
  - Basic facility details (name, location, contact info)
  - Emergency plan information
  - Process details
  - Chemical inventories
- Saves all data to JSON files in an organized directory structure
- Supports command-line arguments to specify different EPA Facility IDs

## Requirements

- Python 3.x
- Required packages:
  - requests
  - python-dotenv

## Installation

1. Ensure you have Python 3.x installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python epa_facility_data.py
```

This will fetch data for the default EPA Facility ID (100000001892).

### Specifying an EPA Facility ID

```bash
python epa_facility_data.py [epa_facility_id]
```

Replace `[epa_facility_id]` with the EPA Facility ID you want to retrieve data for.

### Output

The script creates a directory named `epa_facility_[epa_facility_id]` and saves the following files:

1. `search_results_[epa_facility_id].json` - Contains the initial search results
2. `facility_[facility_id].json` - One file for each facility submission, containing detailed information

## API Endpoints

The script uses two EPA RMP API endpoints:

1. Search endpoint to find all facility submissions:
   ```
   https://cdxapps.epa.gov/olem-rmp-pds/api/search/submissions?id={epa_facility_id}
   ```

2. Facility endpoint to get detailed information for each facility:
   ```
   https://cdxapps.epa.gov/olem-rmp-pds/api/facilities/{facility_id}
   ```

## Data Fields

The API returns various data fields, including:

- `facilityId`: The facility's unique identifier
- `epaFacId`: The EPA's facility identifier
- `facNm`: The facility name
- `parntCo1Nm`: The parent company name
- `facStreet1Tx`: The facility's street address
- `facCityNm`: The city where the facility is located
- `facStateCd`: The state code
- `countyNm`: The county name
- `facZipCd`: The ZIP code
- `facLatDecMs`/`facLongDecMs`: Latitude and longitude coordinates
- `emergencyPlan`: Emergency planning information
- `processes`: Information about processes at the facility
  - `programLevelCd`: The program level code
  - `processNaics`: NAICS codes for the process
  - `processChemicals`: Chemicals used in the process

## License

[Add your license information here] 