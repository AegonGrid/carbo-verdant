from dotenv import load_dotenv
import os

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

def main():

    load_dotenv()
    COPERNICUS_USERNAME = os.getenv('COPERNICUS_USERNAME')
    COPERNICUS_PASSWORD = os.getenv('COPERNICUS_PASSWORD')

    aoi_path = "data/example_polygon_2.geojson"
    
    api = SentinelAPI(COPERNICUS_USERNAME, COPERNICUS_PASSWORD, 'https://apihub.copernicus.eu/apihub')
    footprint = geojson_to_wkt(read_geojson(aoi_path))
    products = api.query(
        area=footprint,
        date=("20200101", "20201202"),  # YYYYMMDD format
        platformname="Sentinel-2",
        producttype="S2MSI2A",  # Level-2A (surface reflectance)
        cloudcoverpercentage=(0, 10)  # 0-10% cloud cover
    )
    api.download_all(products[:1], directory="data/sentinel2")
    
if __name__ == "__main__":
    main()
