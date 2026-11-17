# Radar and design rainfall for Avonside

**Not covered by the repository's MIT licence.** Derived from Bureau of Meteorology
products; see Source below.

## Files

`radar40_stormday_index.csv` — 3,555 October–March days, 2006–2025, with the daily 40 dBZ
reflectivity area (km2, a convective-intensity index taken from the archive's own tarlist
headers) and the scan count for Captains Flat radar 40. `-999` means not computed; 3,118
days are usable. Use it to choose which days are worth pulling volumes for, since each day
is 354 MB. Scan counts of 288 / 240 / 144 correspond to 5 / 6 / 10-minute cadence
depending on era. The largest warm-season days are 2022-01-07 (307,007 km2),
2021-12-18 (299,250), 2023-12-25 (297,998), 2020-02-18 (259,938) and 2020-01-20 (258,512).

`radar_farm_20150105_6min.csv` — the extracted 6-minute series over the farm for the
5 January 2015 storm: raw dBZ, dBZ after the 53 dBZ hail cap, rain rate (mm/h) and depth
(mm) per scan.

## How to extract a farm time series from a volume

Volumes live at `rq0/{radar}/{YYYY}/vol/{radar}_{YYYYMMDD}.pvol.zip` on NCI THREDDS.
In the ODIM HDF5 file, `/dataset1` is the 0.5 deg tilt with `nrays` 360, `nbins` 598,
`rscale` 500 m and **`rstart` 1.0 km** — so the bin index is `(range_m - 1000) / 500`.
For Avonside at 111.4 km and azimuth 219.3 deg that is bin 220, ray 219. `/dataset1/data1`
holds `DBZH` as uint8 with `gain` 0.5 and `offset` -32.0; `nodata` and `undetect` are both
0, meaning no echo. Average a 3x3 ray/bin patch in **linear Z**, not in dBZ, cap at
53 dBZ for hail, then apply Marshall-Palmer `Z = 200*R^1.6`.

## Source

Bureau of Meteorology operational radar archive, hosted by the National Computational
Infrastructure as project `rq0`. Design rainfall (`../ifd_depths_Top_farm_all_design.csv`)
is Copyright Commonwealth of Australia 2016, Bureau of Meteorology, from the revised IFD
system at bom.gov.au/water/designRainfalls/revised-ifd/.
