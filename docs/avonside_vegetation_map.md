# Avonside vegetation map — where the trees are

A per-cell tree-versus-grass layer for the TerraSim2 / TOPMODEL runs, so `tree_root_depth`
can differ from the 0.3 m grass root zone. Built 2026-11-16 from the 2018 ELVIS lidar
(Berridale201802-LID2-C3-AHD, four tiles), at **3 m** with a **5 m canopy-height cut**.

![3 m tree mask over the farm]({{artifact:art_fb71556e-2d49-49c2-8137-f96f93fac66a}})

## What was built

| product | grid | file |
|---|---|---|
| 3 m canopy height model + binary tree mask | 545 x 618 cells, 3 m, origin E 653680 / N 5967505, EPSG:28355 | `avonside_chm3m.npz` |
| 10 m fractional tree cover | **164 x 146, 10 m, origin E 653806 / N 5967505** — the TerraSim2 site grid, cell for cell | `avonside_tree_cover_10m.npz`, `avonside_tree_cover_10m.csv` |

`avonside_tree_cover_10m.npz` carries `tree_frac_5m` (the product), `tree_frac_4m`
(sensitivity), `chm_mean`, `n_3m_cells`, `domain`, `part_id`, and the grid origin.
The CSV is one row per 10 m cell keyed `row, col, easting, northing, lon, lat` in the
same style as `farm_grid10m.csv`.

**Alignment note.** The TerraSim2 grid starts at E 653806, which is not a multiple of 10
away from the four-tile grid origin (E 652000) used by `farm_grid10m.csv`, so the two
10 m grids are offset by 6 m and do **not** share row/col indices. The fraction is formed
by assigning each 3 m cell centre to the 10 m cell containing it, giving 6-16
(median 12) three-metre cells per 10 m cell. Aggregating that way reproduces the direct
3 m cover over the domain to 0.0002 (0.5530 against 0.5532).

## Tree area and cover

Tree = a 3 m cell whose canopy height model reaches 5 m or more.

| | area (ha) | tree (ha) | cover | at a 4 m cut (ha) | cover | difference |
|---|---|---|---|---|---|---|
| **Farm, whole title** | 46.81 | **27.22** | **58.2 %** | 28.89 | 61.7 % | +1.67 ha (+6.1 %) |
| Top farm | 11.65 | 3.93 | 33.8 % | 4.05 | 34.8 % | +0.12 ha (+3.0 %) |
| Upper forest | 10.16 | 6.68 | 65.7 % | 7.06 | 69.5 % | +0.39 ha (+5.8 %) |
| Northerly woodland | 11.84 | 7.68 | 64.8 % | 8.11 | 68.5 % | +0.43 ha (+5.6 %) |
| Lower forest flats | 12.66 | 8.82 | 69.6 % | 9.50 | 75.0 % | +0.68 ha (+7.7 %) |
| Model domain (113 ha) | 112.61 | 62.29 | 55.3 % | 65.61 | 58.3 % | +3.32 ha (+5.3 %) |

Top farm is the one mostly-open part at a third treed; the three wooded parts all sit
between 65 and 70 %. Over the 113 ha model domain the mean 10 m tree fraction is 0.553;
only 9.0 % of domain cells are fully treed and 14.3 % fully open, so most cells are
mixed and a fractional layer carries real information that a binary one would discard.

### 5 m versus 4 m

Dropping the cut to 4 m adds **1.67 ha across the farm (27.22 -> 28.89 ha, +3.6
percentage points of cover)** and 3.32 ha across the model domain. The extra ground is
not spread evenly: Top farm gains almost nothing (+0.12 ha) because its open paddock has
little 4-5 m vegetation, while Lower forest flats gains the most (+0.68 ha, +7.7 %
relative), consistent with Justin's field account of shrubs plus taller trees there.
**The 5 m layer is the product.** 5 m was chosen over 4 m to stay consistent with the
field-confirmed crown inventory, in which the low linear objects on the south and west
of the drone footprint have a median top height of 3.9 m and real crowns a median of
8.2 m — a 4 m cut runs through the top of that low-vegetation population.

## Checks

**Crown inventory.** The merged drone inventory (`avonside_crowns_merged.csv`) holds
**17 trees totalling 542 m2** and **16 low objects totalling 134 m2** — note 17, not the
18 quoted in the brief; the handoff and the table agree on 17. Sampling the 2018 3 m CHM
at each object:

| search radius about the 2026 centroid | trees found (of 17) | low objects called tree (of 16) |
|---|---|---|
| crown radius only (strict overlap) | 11 | **2** |
| crown radius + 1.5 m | 15 | 5 |
| crown radius + 3 m | 17 | 5 |

At strict overlap the 5 m cut excludes 14 of the 16 low objects, which is the behaviour
the inventory requires. The two that are not excluded are **N3** (2018 CHM 6.07 m at
strict overlap, 17.88 m within 3 m) and **N15** (11.42 m strict, 12.45 m within 3 m) —
both stood as canopy well above 5 m in 2018 and measure 3.5 and 4.1 m on the 2026 drone.
That is a fallen or died-back stem, not a threshold failure, and it is the same signature
Justin describes. `avonside_crown_check_2018chm.csv` carries `chm2018_max_pad0`,
`chm2018_max_pad1p5` and `chm2018_max_pad3` with the matching `tree5_*` flags, so each
row of the table above can be read off its own column.

**This check crosses two epochs and two sensors** — 2018 lidar at 0.69 first returns/m2
against the 2026 photogrammetric drone — so it cannot be read as a straight accuracy
test. The 3 m-radius row is included because canopy-to-canopy registration between the
two epochs gave an offset of about dx -3 m, dy -2 m, one full cell at this resolution;
at that tolerance every one of the 17 validated trees is inside the mask.

**Mask coherence.** The 5 m mask over the mapped window is 994 connected components, of
which the largest is 122.9 ha of continuous forest. Only 242 cells (0.1 % of tree cells)
are isolated singletons, so no de-speckling filter was applied.

## How the CHM was built

Rebuilt at 3 m directly from the point cloud — **not** resampled from the 1.5 m drone
CHM, which exists only over the 4.8 ha drone footprint and is a different sensor and
epoch. Steps:

1. All four ELVIS tiles read, classes 7 (noise) and 12 (overlap) dropped, leaving
   2.64 M returns over the mapped window at 0.69 first returns/m2.
2. Height above ground taken as the return elevation minus the existing filled 3 m
   ELVIS DEM (`avonside_catchments.npz['dem_filled']`), **bilinearly interpolated** at
   each return's position rather than read from the containing cell — on 25-degree
   ground a 3 m cell falls 1.4 m, so nearest-cell subtraction would carry that as error.
3. Canopy height per 3 m cell = the maximum height of vegetation returns (classes 3, 4,
   5) in that cell. Buildings (class 6) and water (9) are excluded from the canopy.
   Cells holding returns but no vegetation return are set to 0 m; the 244 cells with no
   returns at all are nearest-neighbour filled.
4. Tree mask = canopy height >= 5 m.

Because it is a cell maximum, this is a **cell-occupancy cover, not a crown-projection
cover** — a 9 m2 cell counts as treed if any part of it is under a crown. Cover above
1.5 m by this definition is 71.7 % of the title against a first-return crown-projection
figure of 55.7 % known for this farm, and the gap is that definitional difference. For
the model this is the right convention: the question is whether a cell has tree roots
in it, not what share of its area is leaf.

## Caveats

- The lidar is **2018**. The crown work showed a median crown-top fall of 3.3 m between
  2018 and 2026 across 16 trees, so some cells mapped as tree here may now be below 5 m,
  and the map will over-state the tall stratum by an unknown amount.
- The mask says tall woody vegetation, not species or condition. Dense shrubland that
  has reached 5 m reads as tree.
- No height-cut choice separates the dieback classes. If the model needs an intact-tall
  versus died-back distinction, that is the four-state stand-form rule, not this layer.
- Nothing here has been validated against a field tree census outside the 4.8 ha drone
  footprint.
