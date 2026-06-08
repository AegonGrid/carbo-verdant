import geopandas as gpd

def main():

    aoi = gpd.read_file("data/example_polygon_2.geojson")  
    print(aoi.name)

if __name__ == "__main__":
    main()
