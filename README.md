# Real Estate Site Selection Tool

A web application for visualizing census data on interactive maps to inform real estate site selection decisions.

## Features

- Interactive map visualization (Google Maps)
- Census data layers:
  - Average Household Income (AHHI)
  - Median Age
  - Population
- Data granularity: Zip code level
- PostgreSQL database for efficient data storage
- Export functionality to Google Sheets
- Easy data modification and appending

## Tech Stack

- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Frontend**: HTML, JavaScript, Google Maps API
- **Data Source**: US Census Bureau API

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Google Maps API Key
- US Census Bureau API Key (optional, but recommended)

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database:
```bash
createdb real_estate_census
```

3. Configure environment variables (see `.env.example`)

4. Initialize database:
```bash
python scripts/init_db.py
```

5. Fetch census data:
```bash
python scripts/fetch_census_data.py
```

6. Run the application:
```bash
python app.py
```

## Project Structure

```
├── app.py                 # Flask application entry point
├── backend/
│   ├── models.py          # Database models
│   ├── census_api.py      # Census Bureau API client
│   ├── database.py        # Database connection and setup
│   └── routes.py          # API routes
├── frontend/
│   ├── index.html         # Main map interface
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Styling
│   │   └── js/
│   │       └── map.js     # Map and layer logic
├── scripts/
│   ├── init_db.py         # Database initialization
│   └── fetch_census_data.py # Census data fetcher
├── config/
│   └── config.py          # Configuration settings
└── requirements.txt       # Python dependencies
```

## Usage

1. Access the application at `http://localhost:5000`
2. Select data layers from the control panel
3. View census data by zip code on the map
4. Export data to Google Sheets using the export button

## API Endpoints

- `GET /api/census-data` - Get census data (with optional filters)
- `GET /api/census-data/zip/<zip_code>` - Get data for specific zip code
- `POST /api/census-data` - Add/update census data
- `GET /api/export/sheets` - Export data to Google Sheets

