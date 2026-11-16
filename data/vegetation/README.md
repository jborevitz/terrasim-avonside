# Tree cover at Avonside

**This directory is not covered by the repository's MIT licence.** These are derived
products; the elevation data they come from carries its own terms.

## What is here

`avonside_tree_cover_10m.npz` / `.csv` — fractional tree cover on the **164 × 146
TerraSim2 model grid at 10 m**, origin E 653806 / N 5967505, EPSG:28355 (MGA zone 55).

| key | meaning |
|---|---|
| `tree_frac_5m` | fraction of the 3 m cells in each 10 m cell with canopy ≥ 5 m |
| `tree_frac_4m` | the same at a 4 m cut, carried as a sensitivity |
| `chm_mean` | mean 3 m canopy height in the cell |
| `n_3m_cells` | 3 m cells contributing (6–16, median 12) |
| `part_id`, `domain` | farm part and model-domain membership |

`tree_frac_5m` is the layer intended for `tree_root_depth`.

## How it was made

A 3 m canopy height model was built directly from the **2018 ELVIS lidar**
(Berridale201802-LID2-C3-AHD, four tiles), not resampled from the 1.5 m drone CHM, which
covers only the 4.8 ha drone footprint and is a different sensor and epoch. Classes 7
(noise) and 12 (flight-line overlap) were dropped, leaving 2.64 M returns at 0.69 first
returns/m² — about six pulses per 3 m cell. Height above ground is the return elevation
minus the filled 3 m ELVIS DEM, **bilinearly interpolated at each return's position**
rather than read from the containing cell, because on 25° ground a 3 m cell falls 1.4 m.
Canopy height per cell is the maximum height of vegetation returns (classes 3, 4, 5);
buildings and water are excluded.

## Read these before using the numbers

- **The lidar is 2018.** The crown work measured a median crown-top fall of 3.3 m between
  2018 and 2026 over 16 trees, so some cells mapped as tree may now be below 5 m. The
  tall stratum is over-stated by an unknown amount.
- **This is cell occupancy, not crown projection.** A 9 m² cell counts as treed if any
  part of it sits under a crown. That is the right convention for a root-depth layer and
  the wrong one for comparison with crown-projection cover — at a 1.5 m cut the two
  conventions give 71.7% against 55.7% for the same farm.
- **The 10 m grid here is not the four-tile 10 m grid.** The TerraSim2 origin E 653806 is
  not a multiple of 10 from the four-tile origin E 652000, so these row/col indices do
  **not** join to `farm_grid10m.csv` — the two grids are offset by 6 m. Join on easting
  and northing, not on indices.
- **The mask means tall woody vegetation, not species or condition.** Shrubland that has
  reached 5 m reads as tree. Separating dieback classes is the four-state stand-form rule,
  not a height cut.
- Nothing is validated against a field tree census outside the 4.8 ha drone footprint.

## Source and licence

Derived from LiDAR distributed through **ELVIS** (Elevation and Depth — Foundation
Spatial Data, https://elevation.fsdf.org.au/), capture `Berridale201802-LID2-C3-AHD`.

Geoscience Australia states that most data in ELVIS is licensed under Creative Commons
Attribution. The custodian for New South Wales elevation data is Spatial Services, with
the attribution **© State of New South Wales (Spatial Services, a business unit of the
Department of Customer Service NSW)**. Confirm the terms attaching to this particular
capture before redistributing it or anything derived from it.
