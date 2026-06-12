from typing import Optional

from sentinelhub import SentinelHubCatalog, DataCollection, BBox


def search_sentinel2_products(
    catalog: SentinelHubCatalog,
    aoi_bbox: BBox,
    time_interval: tuple[str, str],
    max_cloud_cover_pct: Optional[float] = None,
    limit: int = 100,
) -> list[dict]:
    """Search Sentinel-2 L2A products and apply an optional cloud cover filter."""

    if max_cloud_cover_pct is not None:
        if not 0 <= max_cloud_cover_pct <= 100:
            raise ValueError("max_cloud_cover_pct must be between 0 and 100")
        search_filter = f"eo:cloud_cover < {int(max_cloud_cover_pct)}"
    else:
        search_filter = None

    fields = {
        "include": [
            "id",
            "properties.datetime",
            "properties.eo:cloud_cover",
        ],
        "exclude": [],
    }

    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=aoi_bbox,
        time=time_interval,
        filter=search_filter,
        fields=fields,
        limit=limit,
    )

    return list(search_iterator)
