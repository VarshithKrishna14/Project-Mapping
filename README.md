# MSA Physician Group Mapping

This application maps Physician Groups (PGs) within Metropolitan Statistical Areas (MSAs) using data from the NPI registry and AI-powered group identification.

## Features

- Search for MSAs and view physician groups on an interactive map
- Automatic identification of physician groups using Gemini AI
- Detailed information about physicians and their affiliated groups
- Interactive map visualization with Folium

## Prerequisites

- Python 3.8 or higher
- Gemini API key
- Excel file with MSA to ZIP code mappings

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd msa-physician-mapping
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key to the `.env` file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter an MSA name in the search box and click "Search"
