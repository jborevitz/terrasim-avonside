"""Tests for terrasim_avonside.rainfall.

The two that matter are the layout tests: they pin the behaviour that a reader
hard-coded to ``dataset1`` gets wrong on post-2021 volumes, and the floor-not-
round indexing that puts a site in the correct ray at 110 km.

The volume-reading tests need real ODIM files and are skipped when absent; set
TERRASIM_ODIM_PRE / TERRASIM_ODIM_POST to directories of .h5 volumes to run
them.  Everything else runs offline.
"""
import glob
import math
import os

import numpy as np
import pytest

from terrasim_avonside import rainfall as rf

RADAR_LAT, RADAR_LON, RADAR_H = -35.6614, 149.5122, 1382.7
TOP_FARM = (-36.43347, 148.71793)


def test_vincenty_matches_known_baseline():
    km, az = rf.vincenty(RADAR_LAT, RADAR_LON, *TOP_FARM)
    assert km == pytest.approx(111.63, abs=0.05)
    assert az == pytest.approx(219.64, abs=0.05)


def test_vincenty_agrees_with_spherical_to_within_a_fraction_of_a_gate():
    """Documents the size of the ellipsoidal correction: ~70 m at 110 km."""
    km, _ = rf.vincenty(RADAR_LAT, RADAR_LON, *TOP_FARM)
    p1, p2 = math.radians(RADAR_LAT), math.radians(TOP_FARM[0])
    dl = math.radians(TOP_FARM[1] - RADAR_LON)
    sph = 6371.0 * math.acos(math.sin(p1) * math.sin(p2)
                             + math.cos(p1) * math.cos(p2) * math.cos(dl))
    assert 20.0 < abs(sph - km) * 1000 < 150.0


def _tilt(nrays=360, nbins=598, rscale=500.0, rstart=1.0):
    return rf.TiltSpec("dataset1", "data1", 0.5, nrays, nbins, rscale, rstart,
                       0.5, -32.0, 0.0, 0.0)


def test_indices_floor_not_round():
    """Azimuth 219.64 belongs to ray 219; rounding gives 220, ~1.9 km away."""
    ray, bin_, km, az = rf.site_indices([TOP_FARM[0]], [TOP_FARM[1]],
                                        RADAR_LAT, RADAR_LON, _tilt())
    assert ray[0] == 219
    assert bin_[0] == 221


def test_indices_follow_gate_spacing():
    """The post-upgrade 250 m gate doubles the bin index for the same range."""
    _, b500, _, _ = rf.site_indices([TOP_FARM[0]], [TOP_FARM[1]],
                                    RADAR_LAT, RADAR_LON, _tilt(rscale=500.0))
    _, b250, _, _ = rf.site_indices([TOP_FARM[0]], [TOP_FARM[1]], RADAR_LAT,
                                    RADAR_LON, _tilt(rscale=250.0, nbins=1496))
    assert b250[0] == pytest.approx(2 * b500[0], abs=2)


def test_beam_height_above_the_farm():
    km, _ = rf.vincenty(RADAR_LAT, RADAR_LON, *TOP_FARM)
    centre = rf.beam_height_m(km, 0.5, RADAR_H)
    assert centre - 1175.0 == pytest.approx(1915, abs=10)


def test_zr_inverts_marshall_palmer():
    rate = 12.5
    z = rf.ZR_A * rate ** rf.ZR_B
    assert rf.zr_depth([z], 1.0)[0] == pytest.approx(rate, rel=1e-6)


def test_zr_hail_cap_binds():
    z_huge = 10 ** (65.0 / 10)
    capped = 10 ** (rf.HAIL_CAP_DBZ / 10)
    assert rf.zr_depth([z_huge], 1.0)[0] == pytest.approx(
        rf.zr_depth([capped], 1.0)[0])


def test_median_step_handles_each_cadence():
    for minutes in (5, 6, 10):
        t = np.arange("2015-01-05T00:00", "2015-01-06T00:00",
                      np.timedelta64(minutes, "m"), dtype="datetime64[s]")
        assert rf.median_step_hours(t) == pytest.approx(minutes / 60.0)


def test_median_step_survives_a_gap():
    t = np.concatenate([
        np.arange("2015-01-05T00:00", "2015-01-05T06:00",
                  np.timedelta64(6, "m"), dtype="datetime64[s]"),
        np.arange("2015-01-05T09:00", "2015-01-06T00:00",
                  np.timedelta64(6, "m"), dtype="datetime64[s]")])
    assert rf.median_step_hours(t) == pytest.approx(0.1)


def test_silo_day_label_is_the_9am_window():
    import pandas as pd
    before = rf.silo_day_of(pd.DatetimeIndex(["2015-01-04T22:30"]))[0]
    after = rf.silo_day_of(pd.DatetimeIndex(["2015-01-04T23:30"]))[0]
    assert (after - before).days == 1


def test_radar_day_url():
    assert rf.radar_day_url(40, "20150105").endswith(
        "rq0/40/2015/vol/40_20150105.pvol.zip")


def _volumes(env):
    d = os.environ.get(env)
    return sorted(glob.glob(os.path.join(d, "**", "*.h5"), recursive=True)) if d else []


@pytest.mark.parametrize("env,expect_rscale", [("TERRASIM_ODIM_PRE", 500.0),
                                               ("TERRASIM_ODIM_POST", 250.0)])
def test_lowest_tilt_found_in_both_layouts(env, expect_rscale):
    files = _volumes(env)
    if not files:
        pytest.skip(f"set {env} to a directory of ODIM volumes")
    import h5py
    with h5py.File(files[0], "r") as h:
        tilt = rf.lowest_tilt(h)
    assert tilt.elangle == pytest.approx(0.5, abs=0.01)
    assert tilt.rscale_m == pytest.approx(expect_rscale)


def test_post_upgrade_lowest_tilt_is_not_dataset1():
    """The regression this module exists for."""
    files = _volumes("TERRASIM_ODIM_POST")
    if not files:
        pytest.skip("set TERRASIM_ODIM_POST to a directory of ODIM volumes")
    import h5py
    with h5py.File(files[0], "r") as h:
        tilt = rf.lowest_tilt(h)
        assert tilt.group != "dataset1"
        assert float(dict(h["/dataset1/where"].attrs)["elangle"]) > 10.0


def test_sample_volume_shapes_and_spread():
    files = _volumes("TERRASIM_ODIM_PRE") or _volumes("TERRASIM_ODIM_POST")
    if not files:
        pytest.skip("set TERRASIM_ODIM_PRE or _POST to ODIM volumes")
    import h5py
    lats = [TOP_FARM[0], TOP_FARM[0] + 0.01, TOP_FARM[0] - 0.01]
    lons = [TOP_FARM[1], TOP_FARM[1] + 0.01, TOP_FARM[1] - 0.01]
    with h5py.File(files[0], "r") as h:
        tilt = rf.lowest_tilt(h)
        ray, bin_, _, _ = rf.site_indices(lats, lons, RADAR_LAT, RADAR_LON, tilt)
        zm, zlo, zhi, n = rf.sample_volume(h, ray, bin_, tilt, halo=1)
    assert zm.shape == zlo.shape == zhi.shape == (3,)
    ok = ~np.isnan(zm)
    assert np.all(zlo[ok] <= zm[ok] + 1e-6) and np.all(zm[ok] <= zhi[ok] + 1e-6)
