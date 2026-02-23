import json
import requests
from pathlib import Path

DATASET_ID = "4pq5-n9py"
BASE = "https://data.cms.gov"

# Metastore endpoint (full URL)
METASTORE_URL = f"{BASE}/provider-data/api/1/metastore/schemas/dataset/items/{DATASET_ID}"

# Make sure outputs folder exists
Path("outputs").mkdir(exist_ok=True)

resp = requests.get(METASTORE_URL, timeout=30)
resp.raise_for_status()
meta = resp.json()

print("Top-level keys:", list(meta.keys()))

# Print distributions (these tell us how to query/download)
distributions = meta.get("distribution", [])
print("\nNumber of distributions:", len(distributions))

for i, d in enumerate(distributions[:10]):  # show first 10
    print(f"\n--- Distribution index {i} ---")
    print("identifier:", d.get("identifier"))
    print("title:", d.get("title"))
    print("format:", d.get("format"))
    print("mediaType:", d.get("mediaType"))
    print("accessURL:", d.get("accessURL"))
    print("downloadURL:", d.get("downloadURL"))

# Some datasets include field names in resource metadata
resource = meta.get("resource", {})
field_names = resource.get("columns_field_name") or resource.get("fields") or []
if field_names:
    print("\nSample field names:")
    if isinstance(field_names, list):
        for f in field_names[:50]:
            print("-", f)
    else:
        print(field_names)

# Save metastore output to inspect later
out_path = Path("outputs") / f"metastore_{DATASET_ID}.json"
out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"\nSaved {out_path}")