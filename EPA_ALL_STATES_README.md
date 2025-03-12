# EPA RMP All States Data Collection

This script collects comprehensive EPA Risk Management Plan (RMP) facility data for all US states and territories.

## Overview

The `epa_all_states.py` script automates the process of collecting EPA RMP facility data across all 50 US states, the District of Columbia, and US territories. It builds on the state-specific search functionality and creates a comprehensive dataset organized by state and facility.

## Features

- **Complete Coverage**: Processes all 56 US states and territories
- **Hierarchical Data Collection**: Uses the three-level approach (state search → EPA Facility ID → facility submissions)
- **Parallel Processing**: Utilizes multi-threading to process multiple facilities and submissions simultaneously
- **Robust Error Handling**: Continues processing even if individual states or facilities encounter errors
- **Progress Tracking**: Displays detailed progress information and timing statistics
- **Resumable Processing**: Can resume from any state if the process is interrupted
- **Master Summary**: Creates a comprehensive summary of all collected data
- **Rate Limiting**: Implements delays between requests to avoid overwhelming the API

## Requirements

- Python 3.x
- Required packages:
  - requests
  - python-dotenv
  - argparse
  - time
  - datetime
  - concurrent.futures (standard library)
  - threading (standard library)

## Installation

1. Ensure you have Python 3.x installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python epa_all_states.py
```

This will process all states and territories in alphabetical order with default parallelism (5 workers).

### Resuming from a Specific State

If the process is interrupted, you can resume from a specific state:

```bash
python epa_all_states.py --start CA
```

This will start processing from California and continue through the remaining states.

### Controlling Parallelism

You can specify the number of parallel workers to use:

```bash
python epa_all_states.py --parallel 10
```

This will use up to 10 parallel workers for processing facility submissions, and up to 3 workers for processing EPA facilities (to avoid overwhelming the API).

## Output Structure

The script creates a hierarchical directory structure:

```
epa_all_states/
├── master_summary.json                # Summary of all states
├── epa_state_AL/                      # One directory per state
│   ├── state_search_AL.json           # State search results
│   ├── summary_AL.json                # State summary
│   └── facility_[epa_facility_id]/    # One directory per EPA Facility ID
│       ├── submissions_[id].json      # Submissions for this EPA Facility ID
│       ├── facility_[id_1].json       # Detailed data for each facility submission
│       └── ...
├── epa_state_AK/
│   └── ...
└── ...
```

## Master Summary

The master summary file (`master_summary.json`) provides an overview of all collected data:

- Total number of states processed
- Total number of EPA facilities found
- Total number of facility submissions
- Per-state statistics, sorted by number of facilities
- Timestamp of when the summary was generated

## Performance Considerations

- **Parallelism**: The script uses multi-threading to significantly improve performance:
  - Multiple facility submissions are processed in parallel
  - Multiple EPA facilities can be processed in parallel (limited to 3 by default)
  - The `--parallel` parameter controls the maximum number of concurrent workers
- **Runtime**: With parallelism, the full data collection process is much faster than sequential processing, but may still take 1-2 hours depending on the number of facilities and your internet connection.
- **Disk Space**: The complete dataset may require several gigabytes of disk space.
- **API Rate Limiting**: The script includes minimal delays between requests to avoid overwhelming the EPA API while maintaining good performance.
- **Resource Usage**: Higher parallelism settings will increase CPU and network usage but can significantly reduce total runtime.

## Error Handling

The script is designed to be robust against various types of errors:

- If a state search fails, it will create an empty summary and continue to the next state.
- If a facility submission search fails, it will add an empty entry to the summary and continue.
- If a facility data retrieval fails, it will log the error and continue.
- Parallel processing includes error handling to ensure that failures in one thread don't affect others.

All errors are logged to the console for later review.

## State and Territory Codes

The script processes the following state and territory codes:

| Code | State/Territory |
|------|----------------|
| AL | Alabama |
| AK | Alaska |
| AS | American Samoa |
| AZ | Arizona |
| AR | Arkansas |
| CA | California |
| CO | Colorado |
| CT | Connecticut |
| DE | Delaware |
| DC | District of Columbia |
| FL | Florida |
| GA | Georgia |
| GU | Guam |
| HI | Hawaii |
| ID | Idaho |
| IL | Illinois |
| IN | Indiana |
| IA | Iowa |
| KS | Kansas |
| KY | Kentucky |
| LA | Louisiana |
| ME | Maine |
| MD | Maryland |
| MA | Massachusetts |
| MI | Michigan |
| MN | Minnesota |
| MS | Mississippi |
| MO | Missouri |
| MT | Montana |
| NE | Nebraska |
| NV | Nevada |
| NH | New Hampshire |
| NJ | New Jersey |
| NM | New Mexico |
| NY | New York |
| NC | North Carolina |
| ND | North Dakota |
| MP | Northern Mariana Islands |
| OH | Ohio |
| OK | Oklahoma |
| OR | Oregon |
| PA | Pennsylvania |
| PR | Puerto Rico |
| RI | Rhode Island |
| SC | South Carolina |
| SD | South Dakota |
| TN | Tennessee |
| TX | Texas |
| UT | Utah |
| VT | Vermont |
| VA | Virginia |
| VI | Virgin Islands |
| WA | Washington |
| WV | West Virginia |
| WI | Wisconsin |
| WY | Wyoming |

## License

[Add your license information here] 