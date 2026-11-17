#!/usr/bin/env python
"""Pull SILO and radar rainfall for a farm, for the same coordinates.

Users should be able to choose between the two, or compare them, so this always
pulls both.  Radar is sampled with a +-1 ray halo, and the per-ray envelope is
carried through to the output: at 110 km one ray is ~1.9 km, so on a convective
day the envelope is the honest spatial uncertainty, not a rounding detail.

    # a single point, one storm day
    python scripts/pull_rain.py --lat -36.43347 --lon 148.71793 \
        --days 20150105 --out rain_topfarm

    # a whole property on a 250 m grid, several days
    python scripts/pull_rain.py --bbox -36.45 148.70 -36.42 148.74 --grid 250 \
        --days 20150105 20211125 --out rain_farmgrid

Geometry is computed once and every scan is sampled with one vectorised gather,
so a 10,000 ha property costs little more than a single point.
"""
import argparse
import glob
import os
import shutil

import h5py
import numpy as np
import pandas as pd

from terrasim_avonside import rainfall as rf

# Captains Flat (radar 40).  Site coordinates come from each volume's /where.
DEFAULT_RADAR = 40


def grid_points(bbox, spacing_m):
    lat0, lon0, lat1, lon1 = bbox
    lat0, lat1 = sorted((lat0, lat1)); lon0, lon1 = sorted((lon0, lon1))
    dlat = spacing_m / 110_574.0
    dlon = spacing_m / (111_320.0 * np.cos(np.radians((lat0 + lat1) / 2)))
    las = np.arange(lat0, lat1 + 1e-12, dlat)
    los = np.arange(lon0, lon1 + 1e-12, dlon)
    LA, LO = np.meshgrid(las, los, indexing="ij")
    return LA.ravel(), LO.ravel()


def pull_radar_day(radar_id, day, lats, lons, workdir, halo=1, keep=False):
    d = rf.fetch_radar_day(radar_id, day, workdir)
    files = sorted(glob.glob(os.path.join(d, "**", "*.h5"), recursive=True))
    if not files:
        raise RuntimeError(f"{day}: no volumes in archive")
    rows, times, idx = [], [], None
    with h5py.File(files[0], "r") as h:
        radar_lat = float(dict(h["/where"].attrs)["lat"])
        radar_lon = float(dict(h["/where"].attrs)["lon"])
    for f in files:
        with h5py.File(f, "r") as h:
            tilt = rf.lowest_tilt(h)
            if idx is None:
                ray, bn, km, az = rf.site_indices(lats, lons, radar_lat, radar_lon, tilt)
                idx = (ray, bn, km, az, tilt)
            zm, zlo, zhi, n = rf.sample_volume(h, idx[0], idx[1], tilt, halo=halo)
            w = dict(h[f"/{tilt.group}/what"].attrs)
            times.append(pd.to_datetime(w["startdate"].decode() + w["starttime"].decode(),
                                        format="%Y%m%d%H%M%S"))
            rows.append(np.stack([zm, zlo, zhi]))
    if not keep:
        shutil.rmtree(d, ignore_errors=True)
    Z = np.stack(rows)                              # (nscan, 3, nsite)
    dt = rf.median_step_hours(np.array(times, dtype="datetime64[s]"))
    return times, Z, dt, idx


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lat", type=float)
    g.add_argument("--bbox", nargs=4, type=float,
                   metavar=("LAT0", "LON0", "LAT1", "LON1"))
    p.add_argument("--lon", type=float)
    p.add_argument("--grid", type=float, default=500.0,
                   help="grid spacing in metres when --bbox is used")
    p.add_argument("--days", nargs="+", required=True, help="UTC days, YYYYMMDD")
    p.add_argument("--radar", type=int, default=DEFAULT_RADAR)
    p.add_argument("--halo", type=int, default=1, help="ray/bin halo, 1 = +-1 ray")
    p.add_argument("--silo-start", default=None, help="YYYYMMDD; default first day - 7")
    p.add_argument("--silo-finish", default=None)
    p.add_argument("--email", default=None, help="contact address for SILO, optional")
    p.add_argument("--workdir", default="radar_work")
    p.add_argument("--keep-volumes", action="store_true")
    p.add_argument("--out", required=True, help="output prefix")
    a = p.parse_args()

    if a.bbox:
        lats, lons = grid_points(a.bbox, a.grid)
    else:
        if a.lon is None:
            p.error("--lat requires --lon")
        lats, lons = np.array([a.lat]), np.array([a.lon])
    print(f"{len(lats)} sample point(s)")

    frames = []
    for day in a.days:
        times, Z, dt, idx = pull_radar_day(a.radar, day, lats, lons, a.workdir,
                                           halo=a.halo, keep=a.keep_volumes)
        ray, bn, km, az, tilt = idx
        print(f"  {day}: tilt {tilt.group} ({tilt.elangle} deg), gate {tilt.rscale_m:.0f} m, "
              f"{len(times)} scans at {dt*60:.0f} min")
        for j in range(len(lats)):
            frames.append(pd.DataFrame({
                "time": times,
                "lat": lats[j], "lon": lons[j],
                "range_km": km[j], "azimuth_deg": az[j], "ray": ray[j], "bin": bn[j],
                "mm": rf.zr_depth(Z[:, 0, j], dt),
                "mm_ray_low": rf.zr_depth(Z[:, 1, j], dt),
                "mm_ray_high": rf.zr_depth(Z[:, 2, j], dt)}))
    radar = pd.concat(frames, ignore_index=True)
    radar["silo_day"] = rf.silo_day_of(radar["time"])
    radar.to_csv(f"{a.out}_radar_scans.csv", index=False)

    daily = (radar.groupby(["silo_day", "lat", "lon"])[["mm", "mm_ray_low", "mm_ray_high"]]
             .sum().reset_index())
    daily.to_csv(f"{a.out}_radar_daily.csv", index=False)

    start = a.silo_start or (pd.to_datetime(min(a.days)) - pd.Timedelta(days=7)).strftime("%Y%m%d")
    finish = a.silo_finish or (pd.to_datetime(max(a.days)) + pd.Timedelta(days=2)).strftime("%Y%m%d")
    silo = rf.silo_daily(float(np.mean(lats)), float(np.mean(lons)), start, finish,
                         username=a.email)
    silo.to_csv(f"{a.out}_silo_daily.csv")

    print(f"\nwrote {a.out}_radar_scans.csv, {a.out}_radar_daily.csv, {a.out}_silo_daily.csv")
    print("\nREMEMBER: radar depth at Avonside reads about half the gauge value "
          "(x1.91, 95% CI 1.51-2.55) and is NOT applied here.\n"
          "SILO is the better estimate of depth; radar is the only source of structure.")


if __name__ == "__main__":
    main()
