from dotenv import load_dotenv
import os
import json

from sentinelhub import (
    SHConfig,
    SentinelHubCatalog,
    DataCollection,
    BBox,
    CRS,
)


def main():

    # Configure Sentinel Hub credentials
    load_dotenv()

    config = SHConfig()
    config.sh_client_id = os.getenv("SH_CLIENT_ID")
    config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

    config.sh_token_url = (
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    )
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"

    # Define Area Of Interest
    aoi_path = "data/example_polygon_2.geojson"
    with open(aoi_path) as f:
        geojson = json.load(f)
    geometry = geojson["geometry"]

    # Convert polygon to bbox (Sentinel Hub Catalog uses bbox)
    coords = geometry["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    bbox_coords = [min(lons), min(lats), max(lons), max(lats)]

    aoi_bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)

    # Search items in Sentinel Hub catalog
    catalog = SentinelHubCatalog(config=config)
    
    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=aoi_bbox,
        time=("2020-01-02"),
        fields={
            "include": ["id", "properties.datetime"],
            "exclude": []
        },
    )

    items = list(search_iterator)

    print(f"Found {len(items)} products")

    if not items:
        return

    # Download images
    for i, item in enumerate(items[:5]):

        if item["id"] not in os.listdir("data/sentinel_images"):
            print(f"Downloading product {i+1}/{len(items)}: {item['id']}")
            
        print(f"Processed {i+1}/{len(items)} items: {item['id']}")


if __name__ == "__main__":
    main()