import argparse
import time
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime


def geocode_address(address: str, api_key: str) -> tuple[float | None, float | None]:
    """Call Google Geocoding API and return (lat, lng) or (None, None) on failure."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        print(f"  [WARN] Geocoding failed for '{address}': {data['status']}")
    except Exception as e:
        print(f"  [ERROR] Request error for '{address}': {e}")
    return None, None


def match_lga(lat: float, lng: float, lga_gdf: gpd.GeoDataFrame, lga_col: str) -> str | None:
    """Return LGA name for a coordinate pair using spatial join."""
    point = Point(lng, lat)  # Shapely: (x=lng, y=lat)
    matches = lga_gdf[lga_gdf.geometry.contains(point)]
    if not matches.empty:
        return matches.iloc[0][lga_col]
    return None


def main():
    parser = argparse.ArgumentParser(description="Geocode addresses and assign Nigeria LGAs.")
    parser.add_argument("--input", required=True, help="Input Excel file (.xlsx)")
    parser.add_argument("--address-col", default="address", help="Column name containing addresses")
    parser.add_argument("--lga-shapefile", required=True, help="Path to Nigeria LGA shapefile or GeoJSON")
    parser.add_argument("--lga-name-col", default="adm2_name", help="Column in shapefile with LGA names")
    parser.add_argument("--output", default="output_with_lga.xlsx", help="Output Excel file path")
    parser.add_argument("--api-key", required=True, help="Google Geocoding API key")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds to wait between API calls")
    args = parser.parse_args()

    # --- Load inputs ---
    print(f"Loading addresses from: {args.input}")
    df = pd.read_excel(args.input)

    if args.address_col not in df.columns:
        raise ValueError(f"Column '{args.address_col}' not found. Available: {list(df.columns)}")

    print(f"Loading LGA boundaries from: {args.lga_shapefile}")
    lga_gdf = gpd.read_file(args.lga_shapefile)
    lga_gdf = lga_gdf.to_crs(epsg=4326)  # Ensure WGS84

    if args.lga_name_col not in lga_gdf.columns:
        print(f"[WARN] '{args.lga_name_col}' not found in shapefile. Columns: {list(lga_gdf.columns)}")
        print("       Update --lga-name-col to the correct column name.")

    # --- Geocode & match ---
    lats, lngs, lgas = [], [], []

    for i, row in df.iterrows():
        raw = row[args.address_col]

        # Skip empty / NaN / whitespace-only cells
        if pd.isna(raw) or str(raw).strip() == "":
            lats.append(None)
            lngs.append(None)
            lgas.append(None)
            print(f"[{i+1}/{len(df)}] (empty — skipped)")
            continue

        address = str(raw).strip()
        print(f"[{i+1}/{len(df)}] {address}")

        lat, lng = geocode_address(address, args.api_key)
        lats.append(lat)
        lngs.append(lng)

        if lat is not None and lng is not None:
            lga = match_lga(lat, lng, lga_gdf, args.lga_name_col)
            lgas.append(lga)
            print(f"        → ({lat:.5f}, {lng:.5f})  LGA: {lga or 'No match'}")
        else:
            lgas.append(None)

        time.sleep(args.delay)

    # --- Append columns & save ---
    df["latitude"] = lats
    df["longitude"] = lngs
    df["lga"] = lgas

    file_name = f"{args.output}{datetime.now()}"
    df.to_excel(file_name, index=False)
    total = len(df)
    matched = df["lga"].notna().sum()
    print(f"\nDone. {matched}/{total} rows matched to an LGA.")
    print(f"Saved to: {file_name}")


if __name__ == "__main__":
    main()
