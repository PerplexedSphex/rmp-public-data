# EPA RMP Data Validator (Fixed)

This script validates the completeness of EPA Risk Management Plan (RMP) data collection, identifies any missing data, and optionally fetches missing information using a more efficient approach.

## Overview

The `epa_data_validator_fixed.py` script performs a comprehensive check of the collected EPA RMP data to ensure that:

1. All facilities found in existing state search files have corresponding data directories
2. All facilities have submissions files
3. All submissions have corresponding facility JSON files
4. No data is missing or corrupted

If missing data is found, the script can optionally fetch it directly from the EPA RMP API.

## Key Improvements

This fixed validator improves upon the original validator in several ways:

1. **No Redundant API Queries**: Uses existing state search files instead of querying the EPA API again
2. **No Summary File Dependency**: Doesn't rely on summary files for validation (they might not exist yet)
3. **Direct File Checking**: Directly checks for facility directories and submission files
4. **Efficient Summary Generation**: Only generates summary files when needed
5. **Accurate Master Summary**: Creates a master summary based on actual files, not summary files

## Features

- **Comprehensive Validation**: Checks all aspects of the data collection process
- **Missing Data Detection**: Identifies missing EPA facilities and facility submissions
- **Data Recovery**: Can automatically fetch any missing data
- **Detailed Reporting**: Provides a comprehensive validation report
- **Master Summary Generation**: Creates a master summary of all collected data
- **State-Specific Validation**: Can validate a single state or all states

## Requirements

- Python 3.x
- Required packages:
  - requests
  - argparse
  - json
  - os
  - time
  - threading (standard library)
  - datetime (standard library)

## Installation

1. Ensure you have Python 3.x installed
2. Install the required packages:
   ```bash
   pip install requests
   ```

## Usage

### Basic Validation

To validate all collected data without fetching missing data:

```bash
python epa_data_validator_fixed.py
```

This will check all states and territories and generate a validation report.

### Fetching Missing Data

To validate all data and fetch any missing information:

```bash
python epa_data_validator_fixed.py --fetch-missing
```

This will check all states and territories, fetch any missing data, and generate summary files as needed.

### Validating a Specific State

To validate data for a specific state:

```bash
python epa_data_validator_fixed.py --state CA
```

This will check only the data for California.

To validate and fetch missing data for a specific state:

```bash
python epa_data_validator_fixed.py --state CA --fetch-missing
```

## Validation Process

The script performs the following validation steps for each state:

1. **Directory Check**: Verifies that the state directory exists
2. **Search File Check**: Confirms that the state search file exists and is valid
3. **Facility Directory Check**: Verifies that each EPA facility has a corresponding directory
4. **Submissions File Check**: Confirms that each EPA facility has a valid submissions file
5. **Facility File Check**: Ensures that each facility submission has a corresponding facility file

## Validation Report

After validation, the script generates a detailed report that includes:

- Total number of states validated
- Number of states with missing EPA facilities
- Number of states with missing submissions
- Details of any missing data

## Data Recovery

When run with the `--fetch-missing` flag, the script will:

1. Create missing facility directories
2. Fetch missing EPA facility submissions
3. Fetch missing facility data
4. Generate summary files for states that don't have them

## Master Summary

If requested (after fetching missing data), the script will create a master summary file (`master_summary.json`) that includes:

- Total number of states processed
- Total number of EPA facilities
- Total number of facility submissions
- Per-state statistics, sorted by number of facilities
- Timestamp of when the summary was generated

## Error Handling

The script includes robust error handling to deal with:

- Missing files and directories
- Invalid JSON data
- API request failures
- Network issues

All errors are logged to the console for review.

## Performance Considerations

- The script uses thread-local sessions for efficient API requests
- Rate limiting is implemented to avoid overwhelming the EPA API
- Only fetches data that is actually missing
- Doesn't regenerate summary files unnecessarily

## License

[Add your license information here] 