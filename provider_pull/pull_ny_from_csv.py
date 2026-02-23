import requests
from pathlib import Path
import pandas as pd

DATASET_ID = "4pq5-n9py"
BASE = "https://data.cms.gov"
METASTORE_URL = f"{BASE}/provider-data/api/1/metastore/schemas/dataset/items/{DATASET_ID}"

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

def get_download_url() -> str:
    resp = requests.get(METASTORE_URL, timeout=30)
    resp.raise_for_status()
    meta = resp.json()
    distributions = meta.get("distribution", [])
    if not distributions:
        raise RuntimeError("No distributions found in metastore response.")
    download_url = distributions[0].get("downloadURL")
    if not download_url:
        raise RuntimeError("No downloadURL found (dataset may not be downloadable).")
    return download_url

def download_file(url: str, dest: Path) -> None:
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

def main():
    download_url = get_download_url()
    print("Latest CSV downloadURL:", download_url)

    raw_csv_path = OUT_DIR / "provider_raw_latest.csv"
    print(f"Downloading to {raw_csv_path} ...")
    download_file(download_url, raw_csv_path)
    print("Download complete.")

    # Peek headers so we know the state column name
    preview = pd.read_csv(raw_csv_path, nrows=5)
    print("\nColumns found:")
    for c in preview.columns:
        print("-", c)

    # TODO: Set this once you see the correct column name.
    # Common ones for nursing home provider info: "Provider State" or "PROVIDER_STATE" etc.
    STATE_COL = "State"  # <-- CHANGE THIS to match your printed column list
    # Additional option to filter for counties
    COUNTY_COL = "County/Parish"

    NY_TARGET_COUNTIES = {"BRONX", "KINGS", "NEW YORK", "QUEENS", "RICHMOND", "WESTCHESTER"}
    # Read in chunks so we don't load everything into memory
    out_ny_path = OUT_DIR / "NYC_Westchester_providers.csv"
    first_write = True

    for chunk in pd.read_csv(raw_csv_path, chunksize=50_000):
        ny = chunk[chunk[STATE_COL].astype(str).str.upper() == "NY"]
        if ny.empty:
            continue

         # County filter next (NYC borough-counties + Westchester)
        ny_target = ny[ny[COUNTY_COL].astype(str).str.upper().isin(NY_TARGET_COUNTIES)]
        if ny_target.empty:
            continue

        ny_target.to_csv(out_ny_path, index=False, mode="w" if first_write else "a", header=first_write)
        first_write = False

    print(f"\nSaved filtered NY file to: {out_ny_path}")

if __name__ == "__main__":
    main()