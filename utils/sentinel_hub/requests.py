from typing import Tuple
from pathlib import Path
from typing import Callable

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

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

MAX_SATELLITE_REQUEST_DIMENSION = 2500


def validate_request_size(aoi_size: tuple[int, int]) -> None:
    """Raise if the request size exceeds Sentinel Hub process limits."""

    width, height = aoi_size
    if width > MAX_SATELLITE_REQUEST_DIMENSION or height > MAX_SATELLITE_REQUEST_DIMENSION:
        raise ValueError(
            f"Requested image size {width}x{height} exceeds Sentinel Hub process limit "
            f"of {MAX_SATELLITE_REQUEST_DIMENSION}x{MAX_SATELLITE_REQUEST_DIMENSION}. "
            "Reduce resolution or request a smaller AOI."
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
    output_format: MimeType = MimeType.TIFF,
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
    output_format: MimeType = MimeType.TIFF,
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
    output_format: MimeType = MimeType.TIFF,
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


def _write_geotiff(
    array: np.ndarray,
    path: Path,
    bbox: BBox,
    crs: str = "EPSG:4326",
) -> None:
    """
    Save Sentinel Hub array as proper GeoTIFF.
    Supports:
    - NDVI (H, W)
    - RGB/RGBA (H, W, C)
    """

    arr = array

    # NDVI case: (H, W) → (1, H, W)
    if arr.ndim == 2:
        arr = arr[np.newaxis, :, :]

    # RGB case: (H, W, C) → (C, H, W)
    elif arr.ndim == 3:
        arr = np.transpose(arr, (2, 0, 1))

    bands, height, width = arr.shape

    minx, miny, maxx, maxy = bbox

    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype=arr.dtype,
        crs=CRS.from_string(crs),
        transform=transform,
    ) as dst:
        dst.write(arr)


def download_sentinel_data(
    item_id: str,
    date: str,
    images_dir: Path,
    request_builders: dict[str, Callable[..., SentinelHubRequest]],
    aoi_bbox: BBox,
    aoi_size: tuple[int, int],
    config: SHConfig,
) -> None:
    """
    Download all configured Sentinel image data for a given acquisition.
    """

    for image_type, request_builder in request_builders.items():

        output_path = images_dir / f"{image_type}_{item_id}.tif"

        if output_path.exists():
            continue

        validate_request_size(aoi_size)

        request = request_builder(
            aoi_bbox=aoi_bbox,
            aoi_size=aoi_size,
            config=config,
            date=date,
        )
        image_data = request.get_data()[0]

        _write_geotiff(image_data, output_path, aoi_bbox)
        print(f"Downloaded: {output_path}")
