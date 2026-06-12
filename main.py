from dotenv import load_dotenv
import os
import json
from pathlib import Path

from sentinelhub import (
    SHConfig,
    SentinelHubCatalog,
    BBox,
    CRS,
    bbox_to_dimensions,
)

from utils.sentinel_hub.requests import (
    create_ndvi_request,
    create_true_color_request,
    download_sentinel_data,
)
from utils.sentinel_hub.search import search_sentinel2_products
from config.inputs import (
    TIMESERIES_START,
    TIMESERIES_END,
    RESOLUTION,
    MAX_CLOUD_COVER_PCT,
)


def main():

    # Configure Sentinel Hub credentials
    load_dotenv()

    config = SHConfig()
    config.sh_client_id = os.getenv("SH_CLIENT_ID")
    config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"

    # Define Area Of Interest
    aoi_path = "data/example_polygon_1.geojson"
    with open(aoi_path) as f:
        geojson = json.load(f)
    geometry = geojson["geometry"]

    # Convert polygon to bbox (Sentinel Hub Catalog uses bbox)
    coords = geometry["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    aoi_bbox_coords = [min(lons), min(lats), max(lons), max(lats)]

    aoi_bbox = BBox(bbox=aoi_bbox_coords, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=RESOLUTION)

    # Find candidate Sentinel-2 products before downloading
    catalog = SentinelHubCatalog(config=config)
    items = search_sentinel2_products(
        catalog=catalog,
        aoi_bbox=aoi_bbox,
        time_interval=(TIMESERIES_START, TIMESERIES_END),
        max_cloud_cover_pct=MAX_CLOUD_COVER_PCT,
    )
    print(f"Using cloud cover threshold: {MAX_CLOUD_COVER_PCT}%")
    print(f"Found {len(items)} products")

    if not items:
        return

    # Download images

    images_dir = Path("data/sentinel_images")
    images_dir.mkdir(parents=True, exist_ok=True)

    SATELLITE_REQUESTS = {
        "ndvi": create_ndvi_request,
        "rgb": create_true_color_request,
    }

    for i, item in enumerate(items):

        date = item["properties"]["datetime"].split("T")[0]

        download_sentinel_data(
            item_id=item["id"],
            date=date,
            images_dir=images_dir,
            request_builders=SATELLITE_REQUESTS,
            aoi_bbox=aoi_bbox,
            aoi_size=aoi_size,
            config=config,
        )

    print(f"Processed {i+1}/{len(items)} items: {item['id']}")


if __name__ == "__main__":
    main()
