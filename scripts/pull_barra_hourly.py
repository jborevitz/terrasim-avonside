"""Pull BARRA-C2 hourly precipitation for a point, from NCI over OPeNDAP.

BARRA-C2 publishes precipitation at 1-hourly only; the 20-minute product carries
wind variables, not rain. Units are kg m-2 s-1 and are converted to mm/h here.

The whole 2006-2025 pull is 240 monthly requests and takes about 13 minutes with
six threads. Each month is cached to its own .npz so an interrupted run resumes.

Requires xarray and netcdf4.
"""
import argparse, concurrent.futures as cf, os, time
import numpy as np
import xarray as xr

BASE = "https://thredds.nci.org.au/thredds"
DIR = ("ob53/output/reanalysis/AUST-04/BOM/ERA5/historical/hres/BARRA-C2/v1"
       "/{temporal}/{var}/latest")
FILE = "{var}_AUST-04_ERA5_historical_hres_BOM_BARRA-C2_v1_{temporal}_{ym}-{ym}.nc"


def month_url(ym, var="pr", temporal="1hr"):
    d = DIR.format(temporal=temporal, var=var)
    return f"{BASE}/dodsC/{d}/" + FILE.format(var=var, temporal=temporal, ym=ym)


def grab(ym, lat, lon, outdir, halo=2, var="pr", retries=4):
    """Fetch one month as a (time, 2*halo+1, 2*halo+1) window in mm/h."""
    path = os.path.join(outdir, f"{ym}.npz")
    if os.path.exists(path):
        return ym, "cached"
    for attempt in range(retries):
        try:
            with xr.open_dataset(month_url(ym, var)) as d:
                la, lo = d.lat.values, d.lon.values
                i = int(np.abs(la - lat).argmin())
                j = int(np.abs(lo - lon).argmin())
                s = d[var].isel(lat=slice(i - halo, i + halo + 1),
                                lon=slice(j - halo, j + halo + 1)).load()
                np.savez_compressed(
                    path,
                    pr=np.float32(s.values) * 3600.0,          # kg m-2 s-1 -> mm/h
                    time=s.time.values.astype("datetime64[s]").astype("int64"),
                    lat=np.float64(la[i - halo:i + halo + 1]),
                    lon=np.float64(lo[j - halo:j + halo + 1]))
            return ym, "ok"
        except Exception as e:                                  # noqa: BLE001
            if attempt == retries - 1:
                return ym, f"FAIL {type(e).__name__}: {e}"
            time.sleep(5 * (attempt + 1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lat", type=float, default=-36.435477, help="target latitude")
    p.add_argument("--lon", type=float, default=148.725680, help="target longitude")
    p.add_argument("--start-year", type=int, default=2006)
    p.add_argument("--end-year", type=int, default=2025)
    p.add_argument("--cache", default="barra_months")
    p.add_argument("--out", default="barra_hourly_pr.npz")
    p.add_argument("--workers", type=int, default=6)
    a = p.parse_args()

    os.makedirs(a.cache, exist_ok=True)
    months = [f"{y}{m:02d}" for y in range(a.start_year, a.end_year + 1)
              for m in range(1, 13)]
    t0 = time.time()
    with cf.ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda ym: grab(ym, a.lat, a.lon, a.cache), months))
    bad = [r for r in res if r[1].startswith("FAIL")]
    print(f"{len(res)} months, {len(bad)} failed, {time.time() - t0:.0f} s")
    for b in bad:
        print(" ", b)
    if bad:
        raise SystemExit("incomplete pull; rerun to retry the failed months")

    t, pr = [], []
    for ym in months:
        z = np.load(os.path.join(a.cache, f"{ym}.npz"))
        t.append(z["time"])
        pr.append(z["pr"])
        lat, lon = z["lat"], z["lon"]
    t = np.concatenate(t)
    pr = np.concatenate(pr)
    order = np.argsort(t)
    t, pr = t[order], pr[order]
    assert np.all(np.diff(t) == 3600), "gaps or duplicates in the hourly series"
    np.savez_compressed(a.out, pr=pr, time=t, lat=lat, lon=lon, units="mm/h",
                        source="BARRA-C2 1hr pr, NCI THREDDS ob53")
    print(f"{a.out}: {pr.shape[0]} hours, centre cell {lat[len(lat)//2]:.2f} "
          f"{lon[len(lon)//2]:.2f}, {pr[:, 2, 2].sum() / (a.end_year - a.start_year + 1):.1f} mm/yr")


if __name__ == "__main__":
    main()
