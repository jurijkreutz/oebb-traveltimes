"""
Zone-to-zone car travel time pipeline for Austria (ÖBB network).

This script is the Austrian equivalent of the German zone_od_car_traveltimes.py
pipeline.  It selects the same representative stops that are used by the
RAPTOR-based PT pipeline and requests car travel times from the
openrouteservice matrix API.

Usage (from the repository root)::

    ORS_API_KEY=<your-key> python -m src.analysis.zone_od_car_traveltimes_austria

Prerequisites
-------------
1. An ÖBB GTFS feed directory at the path configured in ``GTFS_PATH``.
2. Austrian Bezirke boundary file in ``data/shapefiles_austria/``.
   See ``data/shapefiles_austria/README.md`` for download instructions.
3. A valid openrouteservice API key (https://openrouteservice.org/).

Output
------
A single Arrow file written to ``data/car_od_austria/car_od.arrow`` with
columns ``origin_zone_id``, ``dest_zone_id``, ``car_travel_time_sec``, etc.
"""

from datetime import date
from pathlib import Path

from src.analysis.zone_od_car_traveltimes import compute_zone_car_od_one_time
from app.config import (
    AT_CAR_OD_DIR,
    AT_VG_LAYER,
    AT_ZONE_ID_COL,
    AT_ZONE_NAME_COL,
    AT_SHAPES_DIR,
)

# ---------------------------------------------------------------------------
# Configuration – adjust these values before running
# ---------------------------------------------------------------------------

# Path to the ÖBB GTFS directory (unzipped)
GTFS_PATH = Path("data/GTFS_oebb")

# Service date – should match the date used for the PT OD pipeline
SERVICE_DATE = date(2026, 2, 24)

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    if not GTFS_PATH.exists():
        raise FileNotFoundError(
            f"GTFS directory not found: {GTFS_PATH}\n"
            "Please download ÖBB GTFS data and place it at the configured path."
        )

    out_file = AT_CAR_OD_DIR / "car_od.arrow"
    if out_file.exists():
        print(f"[oebb car pipeline] Output already exists: {out_file}")
        return

    print(f"[oebb car pipeline] Service date: {SERVICE_DATE}")
    print("[oebb car pipeline] Computing car OD matrix …")

    compute_zone_car_od_one_time(
        gtfs_path=GTFS_PATH,
        shapes_path=AT_SHAPES_DIR,
        vg_layer=AT_VG_LAYER,
        zone_id_col=AT_ZONE_ID_COL,
        zone_name_col=AT_ZONE_NAME_COL,
        on=SERVICE_DATE,
        out_file=out_file,
    )

    print(f"[oebb car pipeline] Done → {out_file}")


if __name__ == "__main__":
    main()
