"""
Zone-to-zone travel time pipeline for Austria (ÖBB network).

This script is the Austrian equivalent of the German zone_od_traveltimes.py
pipeline.  It uses the same RAPTOR-based routing engine but is configured for:

  - Austrian GTFS data (ÖBB)
  - Statistik Austria Bezirke as the zone system

Usage (from the repository root)::

    python -m src.analysis.zone_od_traveltimes_austria

Prerequisites
-------------
1. Place an ÖBB GTFS feed directory at the path configured in ``GTFS_PATH``.
   Official ÖBB GTFS data is available from:
   https://www.data.gv.at/katalog/en/dataset/zugverbindungen-fahrplandaten-oebb

2. Place an Austrian Bezirke boundary file in
   ``data/shapefiles_austria/austria_bezirke.gpkg`` (or adjust ``SHAPES_PATH``
   and ``AT_VG_LAYER`` / column names in ``app/config.py``).
   See ``data/shapefiles_austria/README.md`` for download instructions.

3. Run this script for one service day.  Repeat for each day type
   (weekday, saturday, sunday) and each hour of day you want to visualize
   by adjusting ``SERVICE_DATE`` and ``DEP_HOUR``.

Output
------
Arrow files written to ``data/od_austria/<PERIOD>/day_type=<TYPE>/hour=<HH>.arrow``
in the same layout expected by the FastAPI backend.
"""

from datetime import date
from pathlib import Path

from src.analysis.zone_od_traveltimes import compute_zone_od_one_time
from app.config import (
    AT_OD_DIR,
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

# Service date to analyse (use a representative weekday / Saturday / Sunday)
SERVICE_DATE = date(2026, 2, 24)   # Tuesday – representative weekday

# Day-type label used in the output folder hierarchy
DAY_TYPE = "weekday"               # "weekday" | "saturday" | "sunday"

# Calendar week identifier used as the period folder name (e.g. "2026W09")
PERIOD = f"{SERVICE_DATE.isocalendar().year}W{SERVICE_DATE.isocalendar().week:02d}"

# Hours of day to compute (0–23); extend as needed
HOURS = list(range(0, 24))

# Maximum number of transfers allowed by the RAPTOR router
MAX_TRANSFERS = 5

# Write an additional CSV next to each Arrow file for quick inspection
WRITE_CSV_DEBUG = False

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    if not GTFS_PATH.exists():
        raise FileNotFoundError(
            f"GTFS directory not found: {GTFS_PATH}\n"
            "Please download ÖBB GTFS data and place it at the configured path.\n"
            "See the module docstring for download instructions."
        )

    if not AT_SHAPES_DIR.exists() or not any(AT_SHAPES_DIR.iterdir()):
        raise FileNotFoundError(
            f"Austrian boundary data not found in: {AT_SHAPES_DIR}\n"
            "Please download the Statistik Austria Bezirke boundary file.\n"
            f"See {AT_SHAPES_DIR / 'README.md'} for instructions."
        )

    print(f"[oebb pipeline] Period: {PERIOD}, day type: {DAY_TYPE}")
    print(f"[oebb pipeline] Service date: {SERVICE_DATE}")
    print(f"[oebb pipeline] Hours: {HOURS[0]}–{HOURS[-1]}")

    for hour in HOURS:
        dep_time = f"{hour:02d}:00:00"
        out_file = (
            AT_OD_DIR
            / PERIOD
            / f"day_type={DAY_TYPE}"
            / f"hour={hour:02d}.arrow"
        )

        if out_file.exists():
            print(f"[oebb pipeline] Hour {hour:02d}: already exists, skipping.")
            continue

        print(f"[oebb pipeline] Hour {hour:02d}: computing …")
        compute_zone_od_one_time(
            gtfs_path=GTFS_PATH,
            shapes_path=AT_SHAPES_DIR,
            vg_layer=AT_VG_LAYER,
            zone_id_col=AT_ZONE_ID_COL,
            zone_name_col=AT_ZONE_NAME_COL,
            on=SERVICE_DATE,
            dep_time=dep_time,
            out_file=out_file,
            max_transfers=MAX_TRANSFERS,
            write_csv_debug=WRITE_CSV_DEBUG,
        )
        print(f"[oebb pipeline] Hour {hour:02d}: done → {out_file}")

    print("[oebb pipeline] All hours complete.")


if __name__ == "__main__":
    main()
