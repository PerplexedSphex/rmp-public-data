# EPA RMP Facility Data Retrieval

This script fetches facility data from the EPA's Risk Management Plan (RMP) Program Delivery System API.

## Overview

The `epa_facility_data.py` script retrieves detailed information about facilities registered in the EPA's Risk Management Plan (RMP) database. It provides a convenient way to access facility information, emergency plans, processes, and chemicals stored at these facilities.

## Features

- Retrieves comprehensive facility data from the EPA RMP API
- Displays formatted information about the facility, including:
  - Basic facility details (name, location, contact info)
  - Emergency plan information
  - Process details
  - Chemical inventories
- Saves the complete data to a JSON file for further analysis
- Supports command-line arguments to specify different facility IDs

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

This will fetch data for the default facility ID (1000041063).

### Specifying a Facility ID

```bash
python epa_facility_data.py [facility_id]
```

Replace `[facility_id]` with the ID of the facility you want to retrieve.

### Example Output

The script will display formatted information about the facility and save the complete data to a JSON file named `facility_[facility_id].json`.

## API Information

The script uses the EPA's RMP API endpoint:
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