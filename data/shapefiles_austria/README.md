# Austrian District Boundaries (Bezirke)

Place your Austrian boundary file in this directory so the application can
render zones for the ÖBB network.

## Expected file

| Property | Value |
|---|---|
| Filename | `austria_bezirke.gpkg` **or** `austria_bezirke.geojson` |
| Layer / file stem | `austria_bezirke` |
| Zone-ID column | `id` |
| Zone-name column | `name` |
| CRS | any (will be reprojected to EPSG:4326 automatically) |

> The filename stem (`austria_bezirke`) must match `AT_VG_LAYER` in
> `app/config.py`.  Column names must match `AT_ZONE_ID_COL` and
> `AT_ZONE_NAME_COL`.  All three values can be changed in `app/config.py` if
> your dataset uses different names.

## Where to get the data

### Option A – Statistik Austria (official, free)

1. Go to <https://data.statistik.gv.at/web/catalog.jsp>
2. Search for **"Politische Bezirke"** or **"NUTS"**.
3. Download the GeoPackage / Shapefile for *Bezirksgrenzen* (district
   boundaries).
4. Rename or convert the file so it matches the expected filename and column
   names above, then place it here.

The standard Statistik Austria download contains two relevant columns:

| Original column | Maps to |
|---|---|
| `id` or `iso` | `id` (zone ID / BKZ) |
| `name` | `name` (district name) |

### Option B – GADM (alternative, free)

1. Go to <https://gadm.org/download_country.html>.
2. Download **Austria** at administrative level **2** (Bezirke).
3. Rename the file to `austria_bezirke.gpkg` and place it here.
4. Update `AT_ZONE_ID_COL = "GID_2"` and `AT_ZONE_NAME_COL = "NAME_2"` in
   `app/config.py`.

### Option C – Natural Earth / OpenStreetMap extracts

Any GeoPackage or GeoJSON file with one polygon per Austrian Bezirk and at
least an ID column and a name column will work.  Adjust the column names in
`app/config.py` accordingly.

## Running the analysis pipeline for Austria

Once you have the boundary file in place, you also need to generate the
OD (origin–destination) travel-time tables.  Use the analysis script:

```bash
python -m src.analysis.zone_od_traveltimes_austria
```

See `src/analysis/zone_od_traveltimes_austria.py` for configuration details
(GTFS path, service date, output directories).

GTFS data for ÖBB (Austrian Federal Railways) is available from
<https://www.data.gv.at/katalog/en/dataset/zugverbindungen-fahrplandaten-oebb>
or via <https://mobilitydb.eu/> and similar open-data portals.
