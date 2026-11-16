# BARRA-C2 hourly precipitation at Avonside

**This directory is not covered by the repository's MIT licence.**

## What is here

`barra_avonside_20y_hourly_pr.npz` — hourly precipitation, 2006-01-01 00:30 to
2025-12-31 23:30 UTC-referenced BARRA time, 175,320 hours.

| key | shape | meaning |
|---|---|---|
| `pr` | (175320, 5, 5) float32 | precipitation in **mm/h** |
| `time` | (175320,) int64 | seconds since the Unix epoch |
| `lat` | (5,) float64 | −36.53 to −36.37 |
| `lon` | (5,) float64 | 148.66 to 148.82 |

Index `[:, 2, 2]` is the cell serving the farm, centred −36.45, 148.74, about 1.7 km from
the farm centroid — as close as the 4.4 km AUST-04 grid gets.

The published variable is `pr` in kg m⁻² s⁻¹; it has been **multiplied by 3600** to give
mm/h. No other transformation has been applied: this is the reanalysis as published, and
in particular **no bias correction has been applied**, though one is needed — see the
repository README.

## Source and licence

Bureau of Meteorology Atmospheric high-resolution Regional Reanalysis for Australia,
Version 2 (BARRA2), BARRA-C2 convective-scale product at 4.4 km, obtained from the
National Computational Infrastructure collection `ob53` over OPeNDAP.

The netCDF files carry `license: https://doi.org/10.25914/1x6g-2v48`, and NCI's collection
page for that DOI states the licence as **Creative Commons Attribution 4.0 International**
(https://creativecommons.org/licenses/by/4.0/). Attribution to the Bureau of Meteorology
is required when this data is used or shared.

> Note for anyone reusing this: there is a documented inconsistency in the wild between
> the CC BY 4.0 statement on the NCI and AWS catalogue entries and an "Express Licence
> Agreement" string reported in some BARRA2 netCDF global attributes. The files actually
> used here carry the DOI pointer quoted above, not that string. If you intend to
> redistribute BARRA2 data yourself, confirm the current terms with the Bureau.

## Citation

Bureau of Meteorology (2023+). *BARRA2: Bureau of Meteorology Atmospheric
high-resolution Regional Reanalysis for Australia — Version 2.* NCI Australia.
https://doi.org/10.25914/1x6g-2v48

The production of BARRA2 was supported with funding from the Australian Climate Service.

## Fitness for use

BARRA-C2 is a 4.4 km reanalysis. It cannot resolve a convective core, and at this site it
overstates the annual total by 73% against SILO point data. It is used here for the
*shape* of sub-daily rainfall, not its magnitude.
