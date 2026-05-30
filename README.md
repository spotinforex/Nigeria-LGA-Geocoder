# Nigeria LGA Geocoder

A Python script that reads addresses from an Excel file, geocodes each one using the Google Geocoding API, and matches the resulting coordinates against a Nigeria LGA boundary dataset. The matched LGA is written back to the same row as the address in the output file.

---

## How It Works

1. Reads an `.xlsx` file containing addresses
2. Skips any rows where the address cell is empty or blank
3. Calls the Google Geocoding API to get latitude and longitude for each address
4. Loads a Nigeria LGA boundary shapefile or GeoJSON with GeoPandas
5. Performs a spatial point-in-polygon check to find the matching LGA
6. Saves the result to a new `.xlsx` file with `latitude`, `longitude`, and `lga` columns appended — aligned to the same row as each address

---

## Requirements

- Python 3.10+
- A [Google Geocoding API key](https://developers.google.com/maps/documentation/geocoding/get-api-key)
- A Nigeria LGA boundary file (GeoJSON or shapefile) — a reliable free source is [OCHA HDX Nigeria Admin2](https://data.humdata.org/dataset/cod-ab-nga)

---

## Installation

```bash
# Clone the repo
git clone https://github.com/your-username/nigeria-lga-geocoder.git
cd nigeria-lga-geocoder

# Create and activate a virtual environment
uv venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
uv pip install -r requirements.txt
```

---

## Configuration

Store your API key in a `.env` file at the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> The script also accepts the key directly via `--api-key` if you prefer not to use a `.env` file.

---

## Usage

```bash
python geocode_lga.py \
  --input addresses.xlsx \
  --address-col "Address" \
  --lga-shapefile geodata/nigeria_lgas.geojson \
  --lga-name-col "lga_name" \
  --output output_with_lga.xlsx \
  --api-key YOUR_GOOGLE_API_KEY
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--input` | ✅ | — | Input Excel file (`.xlsx`) |
| `--address-col` | ❌ | `address` | Column name containing addresses |
| `--lga-shapefile` | ✅ | — | Path to Nigeria LGA GeoJSON or shapefile |
| `--lga-name-col` | ❌ | `lga_name` | Column in shapefile holding LGA names |
| `--output` | ❌ | `output_with_lga.xlsx` | Output file path |
| `--api-key` | ✅ | — | Google Geocoding API key |
| `--delay` | ❌ | `0.1` | Seconds to wait between API calls |

> **Tip:** Run `python -c "import geopandas as gpd; print(gpd.read_file('your_file.geojson').columns.tolist())"` to find the correct value for `--lga-name-col`.

---

## Output

The script appends three columns to your original data and saves to a new file:

| Column | Description |
|---|---|
| `latitude` | Geocoded latitude |
| `longitude` | Geocoded longitude |
| `lga` | Matched Nigeria LGA name |

Empty rows produce `None` in all three columns. The LGA always lands on the same row as its address.

---

## Project Structure

```
nigeria-lga-geocoder/
├── geocode_lga.py       # Main script
├── requirements.txt     # Python dependencies
├── .env                 # API key (not committed)
├── .gitignore
└── README.md
```

---

## Dependencies

```
pandas
geopandas
shapely
openpyxl
requests
```

Install individually with:

```bash
uv add pandas geopandas shapely openpyxl requests
```

---

## Notes

- Increase `--delay` (e.g. `--delay 0.5`) if you are on a free-tier Google API key to avoid hitting QPS limits
- The boundary file is reprojected to WGS84 (EPSG:4326) automatically if needed
- Addresses that fail geocoding will have `None` for all three appended columns
