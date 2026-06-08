"""
Test CDSE auth + query real Sentinel-2 scenes over Mopani mine.
Run: python cdse_test.py
"""
import urllib.request
import urllib.parse
import json
import os
from pathlib import Path

# Load .env manually
env_path = Path(__file__).parent / ".env"
env = {}
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

USER = env.get("COPERNICUS_USER", "")
PASS = env.get("COPERNICUS_PASSWORD", "")

print(f"Logging in as: {USER}")

# Step 1: Get token
token_data = urllib.parse.urlencode({
    "grant_type": "password",
    "username": USER,
    "password": PASS,
    "client_id": "cdse-public"
}).encode()

req = urllib.request.Request(
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    data=token_data,
    method="POST"
)
req.add_header("Content-Type", "application/x-www-form-urlencoded")

with urllib.request.urlopen(req, timeout=20) as r:
    token = json.loads(r.read())["access_token"]

print("✓ Authenticated with CDSE\n")

# Step 2: Query Sentinel-2 scenes over Mopani mine
# Mopani: -12.5501 S, 28.2371 E
wkt = "POINT(28.2371 -12.5501)"
odata_filter = (
    "Collection/Name eq 'SENTINEL-2' "
    "and OData.CSC.Intersects(area=geography'SRID=4326;" + wkt + "') "
    "and ContentDate/Start gt 2026-01-01T00:00:00.000Z"
)

params = {
    "$filter": odata_filter,
    "$orderby": "ContentDate/Start desc",
    "$top": "5",
    "$expand": "Attributes"
}

base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
query = base_url + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

req2 = urllib.request.Request(query)
req2.add_header("Authorization", f"Bearer {token}")
req2.add_header("Accept", "application/json")

with urllib.request.urlopen(req2, timeout=20) as r:
    results = json.loads(r.read())

scenes = results.get("value", [])
print(f"Found {len(scenes)} Sentinel-2 scenes over Mopani mine:\n")

for s in scenes:
    name = s.get("Name", "")[:70]
    date = s.get("ContentDate", {}).get("Start", "")[:10]
    size_mb = round(s.get("ContentLength", 0) / 1_000_000, 1)
    sid = s.get("Id", "")

    # Extract cloud cover from attributes
    cloud = "N/A"
    for attr in s.get("Attributes", []):
        if "cloudCover" in attr.get("Name", ""):
            cloud = f"{attr.get('Value', 'N/A')}%"

    print(f"  📡 {date}  |  Cloud: {cloud}  |  {size_mb} MB")
    print(f"     {name}")
    print(f"     ID: {sid}")
    print()

# Save to JSON for demo server to load
output = {
    "mine": "MPNI - Mopani, Mufulira, Zambia",
    "coordinates": {"lat": -12.5501, "lon": 28.2371},
    "source": "ESA Copernicus Data Space Ecosystem",
    "scenes": [
        {
            "id": s.get("Id"),
            "name": s.get("Name"),
            "date": s.get("ContentDate", {}).get("Start", "")[:10],
            "cloud_cover": next(
                (a.get("Value") for a in s.get("Attributes", []) if "cloudCover" in a.get("Name", "")),
                None
            ),
            "size_mb": round(s.get("ContentLength", 0) / 1_000_000, 1),
        }
        for s in scenes
    ]
}

out_path = Path(__file__).parent / "cdse_mopani_scenes.json"
out_path.write_text(json.dumps(output, indent=2))
print(f"✓ Saved to {out_path.name}")
print("\nThese real scene IDs will now show in the demo satellite panel.")
