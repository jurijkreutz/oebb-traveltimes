"""
Zone data access helpers.

Provides cached loading and serialization of zone polygons for fast
client delivery (GeoJSON) and lightweight dropdown population.

Supports both Germany (country="de") using VG1000 and Austria (country="at")
using the Statistik Austria Bezirke boundary dataset.
"""

# Standard library
from functools import lru_cache
from typing import Any

# Local
from src.gtfs_toolbox.geo_utilities import load_zones
from app.config import (
    SIMPLIFY,
    SIMPLIFY_TOLERANCE,
    VG1000_DIR,
    VG_LAYER,
    ZONE_ID_COL,
    ZONE_NAME_COL,
    AT_SHAPES_DIR,
    AT_VG_LAYER,
    AT_ZONE_ID_COL,
    AT_ZONE_NAME_COL,
)


def _country_config(country: str) -> tuple:
    """Return (shapes_dir, vg_layer, zone_id_col, zone_name_col) for *country*."""
    if country == "at":
        return AT_SHAPES_DIR, AT_VG_LAYER, AT_ZONE_ID_COL, AT_ZONE_NAME_COL
    # Default: Germany
    return VG1000_DIR, VG_LAYER, ZONE_ID_COL, ZONE_NAME_COL


@lru_cache(maxsize=2)
def zones_gdf(country: str = "de"):
    """
    Load zone boundaries once and normalize them for web mapping.

    Args:
        country: "de" for Germany (VG1000) or "at" for Austria (Bezirke).

    Returns:
        GeoDataFrame with columns: zone_id, zone_name, geometry
    """
    shapes_dir, vg_layer, zone_id_col, zone_name_col = _country_config(country)

    layers = load_zones(shapes_dir, merge=False)
    if vg_layer not in layers:
        available = ", ".join(sorted(layers.keys()))
        raise KeyError(f"Layer '{vg_layer}' not found. Available: {available}")

    gdf = layers[vg_layer].copy()

    # Keep a minimal schema for the UI
    gdf = gdf[[zone_id_col, zone_name_col, "geometry"]].rename(
        columns={zone_id_col: "zone_id", zone_name_col: "zone_name"}
    )
    gdf["zone_id"] = gdf["zone_id"].astype(str)
    gdf["zone_name"] = gdf["zone_name"].astype(str)

    # Normalize CRS for Leaflet (lat/lon)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    # Simplification reduces payload + rendering cost in the browser
    if SIMPLIFY:
        gdf["geometry"] = gdf["geometry"].simplify(
            SIMPLIFY_TOLERANCE, preserve_topology=True
        )

    return gdf


@lru_cache(maxsize=2)
def zones_geojson(country: str = "de") -> dict[str, Any]:
    """
    Return the full zone layer as GeoJSON.

    Args:
        country: "de" for Germany or "at" for Austria.
    """
    return zones_gdf(country).__geo_interface__


@lru_cache(maxsize=2)
def zones_index(country: str = "de") -> list[dict[str, str]]:
    """
    Return a lightweight zone list for the dropdown.

    Args:
        country: "de" for Germany or "at" for Austria.
    """
    gdf = zones_gdf(country)
    return (
        gdf[["zone_id", "zone_name"]]
        .sort_values(["zone_name", "zone_id"])
        .to_dict(orient="records")
    )
