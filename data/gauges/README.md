# Gauge context for Avonside

**Not covered by the repository's MIT licence.** Derived from SILO (Queensland Government,
CC BY 4.0) which patches Bureau of Meteorology station records.

`avonside_nearby_stations.csv` — the 18 nearest SILO stations within ~60 km, with distance
from the farm centroid, elevation, the **percentage of 2006–2025 daily rainfall that is a
real observation** (SILO source code 0) rather than interpolated, and the mean annual
total. Read `pct_observed` before using any of these as an independent check: Oak Vale and
Jindabyne are 0% observed — closed stations whose SILO series is entirely infilled.

`avonside_part_elevations.csv` — mean, minimum and maximum elevation of the four farm
parts from the 3 m LiDAR DEM, with their centroids in latitude/longitude. Note these run
888–1197 m while SILO assigns 861 m to the grid cell.

Source: SILO, https://www.longpaddock.qld.gov.au/silo/ — Queensland Department of
Environment, Science and Innovation, licensed CC BY 4.0. Underlying observations are
Bureau of Meteorology station data.
