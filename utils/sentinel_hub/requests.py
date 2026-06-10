from typing import Tuple

from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    SHConfig,
)

from utils.sentinel_hub.evalscript import (
    evalscript_ndvi,
    evalscript_true_color,
)


COPERNICUS_DATA_COLLECTION = DataCollection.SENTINEL2_L2A.define_from(
    name="s2l2a",
    service_url="https://sh.dataspace.copernicus.eu",
)


def _create_request(
    *,
    evalscript: str,
    aoi_bbox: BBox,
    aoi_size: Tuple[int, int],
    config: SHConfig,
    date: str,
    mosaicking_order: str = "leastCC",
    output_format: MimeType = MimeType.PNG,
) -> SentinelHubRequest:
    """Build a Sentinel Hub request for a single date."""

    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=COPERNICUS_DATA_COLLECTION,
                time_interval=(date, date),
                other_args={
                    "dataFilter": {
                        "mosaickingOrder": mosaicking_order,
                    }
                },
            )
        ],
        responses=[
            SentinelHubRequest.output_response(
                "default",
                output_format,
            )
        ],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )


def create_ndvi_request(
    aoi_bbox: BBox,
    aoi_size: Tuple[int, int],
    config: SHConfig,
    date: str,
    mosaicking_order: str = "leastCC",
    output_format: MimeType = MimeType.PNG,
) -> SentinelHubRequest:
    """Create an NDVI imagery request."""
    return _create_request(
        evalscript=evalscript_ndvi,
        aoi_bbox=aoi_bbox,
        aoi_size=aoi_size,
        config=config,
        date=date,
        mosaicking_order=mosaicking_order,
        output_format=output_format,
    )


def create_true_color_request(
    aoi_bbox: BBox,
    aoi_size: Tuple[int, int],
    config: SHConfig,
    date: str,
    mosaicking_order: str = "leastCC",
    output_format: MimeType = MimeType.PNG,
) -> SentinelHubRequest:
    """Create a true-color (RGB) imagery request."""
    return _create_request(
        evalscript=evalscript_true_color,
        aoi_bbox=aoi_bbox,
        aoi_size=aoi_size,
        config=config,
        date=date,
        mosaicking_order=mosaicking_order,
        output_format=output_format,
    )