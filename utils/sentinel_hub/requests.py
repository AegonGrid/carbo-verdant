from typing import Tuple
from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    SHConfig,
)
from utils.sentinel_hub.evalscript import evalscript_ndvi, evalscript_true_color

def create_ndvi_request(
    aoi_bbox: BBox,
    aoi_size: Tuple[int, int],
    config: SHConfig,
    date: str,  # Single date in YYYY-MM-DD format
    mosaicking_order: str = "leastCC",
    output_format: MimeType = MimeType.PNG,
) -> SentinelHubRequest:
    """
    Creates a SentinelHubRequest for NDVI imagery for a single date.

    Args:
        aoi_bbox: Bounding box defining the area of interest.
        aoi_size: Output image dimensions as (width, height) in pixels.
        config: SentinelHub configuration with credentials.
        date: Date in YYYY-MM-DD format (e.g., "2022-05-01").
        mosaicking_order: Mosaicking order strategy (default: "leastCC"). leastCC which will return pixels from the least cloudy acquisition in the specified time period.
        output_format: Output image format (default: MimeType.PNG).

    Returns:
        Configured SentinelHubRequest for the specified date.
    """
    data_collection = DataCollection.SENTINEL2_L2A.define_from(
        name="s2l2a",
        service_url="https://sh.dataspace.copernicus.eu",
    )

    return SentinelHubRequest(
        evalscript=evalscript_ndvi,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=data_collection,
                time_interval=(date, date),  # Single day
                other_args={
                    "dataFilter": {
                        "mosaickingOrder": mosaicking_order,
                    }
                },
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", output_format)
        ],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )

def create_true_color_request(
    aoi_bbox: BBox,
    aoi_size: Tuple[int, int],
    config: SHConfig,
    date: str,  # Single date in YYYY-MM-DD format
    mosaicking_order: str = "leastCC",
    output_format: MimeType = MimeType.PNG,
) -> SentinelHubRequest:
    """
    Creates a SentinelHubRequest for true color imagery (RGB) for a single date.

    Args:
        aoi_bbox: Bounding box defining the area of interest.
        aoi_size: Output image dimensions as (width, height) in pixels.
        config: SentinelHub configuration with credentials.
        date: Date in YYYY-MM-DD format (e.g., "2022-05-01").
        mosaicking_order: Mosaicking order strategy (default: "leastCC"). leastCC which will return pixels from the least cloudy acquisition in the specified time period.
        output_format: Output image format (default: MimeType.PNG).

    Returns:
        Configured SentinelHubRequest for the specified date.
    """
    data_collection = DataCollection.SENTINEL2_L2A.define_from(
        name="s2l2a",
        service_url="https://sh.dataspace.copernicus.eu",
    )

    return SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=data_collection,
                time_interval=(date, date),  # Single day
                other_args={
                    "dataFilter": {
                        "mosaickingOrder": mosaicking_order,
                    }
                },
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", output_format)
        ],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )
