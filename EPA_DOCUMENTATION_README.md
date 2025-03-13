# EPA RMP Documentation Generator

This script generates a well-structured documentation site from EPA Risk Management Plan (RMP) data that has been collected using the EPA data collection scripts. It creates a hierarchical set of markdown files that can be easily browsed or converted to HTML.

## Overview

The `generate_documentation.py` script processes the JSON data files in the `epa_all_states` directory and creates a structured documentation site in the `pages` directory. The documentation includes:

- A main index page with links to all states and territories
- State index pages with links to all facilities in that state
- Facility index pages with links to all submissions for that facility
- Detailed submission pages with information about each submission

The script operates entirely on local files and does not make any network requests.

## Features

- **Hierarchical Structure**: Creates a well-organized directory structure that mirrors the JSON data
- **Navigation Links**: Includes navigation links between pages for easy browsing
- **Formatted Data**: Presents the data in a clean, readable format with tables and lists
- **Sortable Lists**: Sorts states alphabetically and submissions by date for easy reference
- **Detailed Information**: Includes detailed information about facilities and submissions when available
- **Map Links**: Includes Google Maps links for facilities with coordinate data

## Requirements

- Python 3.6 or higher
- JSON data collected using the EPA RMP data collection scripts

## Usage

1. Ensure you have collected EPA RMP data using the data collection scripts, which should be stored in the `epa_all_states` directory.

2. Run the documentation generator script:

```bash
python generate_documentation.py
```

3. The script will create a `pages` directory with the following structure:

```
pages/
├── index.md                  # Main index with links to all states
├── states/
│   ├── AL/                   # Alabama directory
│   │   ├── index.md          # Alabama index with links to all facilities
│   │   └── facilities/
│   │       ├── 100000123456/ # Facility directory
│   │       │   ├── index.md  # Facility index with links to all submissions
│   │       │   └── submissions/
│   │       │       └── 12345.md # Detailed submission page
│   │       └── ...
│   ├── AK/                   # Alaska directory
│   │   └── ...
│   └── ...
```

4. You can browse the documentation by opening the `pages/index.md` file in a markdown viewer or converting it to HTML.

## Customization

You can customize the script by modifying the following variables at the top of the file:

- `INPUT_DIR`: The directory containing the EPA RMP data (default: `epa_all_states`)
- `OUTPUT_DIR`: The directory where the documentation will be generated (default: `pages`)

## Converting to HTML

If you want to convert the markdown files to HTML for web viewing, you can use a tool like [Pandoc](https://pandoc.org/) or a static site generator like [MkDocs](https://www.mkdocs.org/).

### Example using Pandoc:

```bash
pandoc -s pages/index.md -o pages/index.html
```

### Example using MkDocs:

1. Install MkDocs:

```bash
pip install mkdocs
```

2. Create an MkDocs configuration file (`mkdocs.yml`):

```yaml
site_name: EPA RMP Documentation
docs_dir: pages
```

3. Build the site:

```bash
mkdocs build
```

This will create a `site` directory with HTML files that you can serve using any web server.

## License

This script is provided under the same license as the EPA RMP data collection scripts. 