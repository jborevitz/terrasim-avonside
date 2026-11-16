"""A TOPMODEL step in TerraSim2's StepFunction form, with a tree water-table term.

Conforms structurally to ``terrasim2.k.step_function.StepFunction`` but, unlike
the protocol's pure steps, carries the catchment-mean saturation deficit between
days as internal state -- TOPMODEL has no per-cell representation of it.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from dataclasses import dataclass
from enum import IntEnum
import numpy as np


class TopmodelFlux(IntEnum):
    INFILTRATION = 0
    RUNOFF = 1          # saturation excess
    EVAPORATION = 2     # from the root-zone store
    PERCOLATION = 3     # root zone -> saturated store
    BASEFLOW = 4        # saturated store -> stream
    UPTAKE = 5          # saturated store -> trees, when the table is in reach


@dataclass(frozen=True)
class TopmodelParams:
    m: float = 0.02                 # recession parameter, m
    t0: float = 1.3                 # transmissivity at saturation, m2/day
    specific_yield: float = 0.05    # of the saprolite
    stress_exponent: float = 1.0
    tree_fraction: float = 0.0      # share of each cell that is tree
    tree_reach: float = 1.0         # m below surface a tree root can draw from
    initial_deficit: float = 0.067  # m of water


class StepTopmodel:
    """Callable with the StepFunction signature; holds S-bar between days."""

    def __init__(self, params: TopmodelParams):
        self.p = params
        self.s_bar = float(params.initial_deficit)
        self._lam = None
        self.history = []

    def _lambda(self, d):
        if self._lam is None:
            a = (np.asarray(d.upslope_cells, dtype=float) + 1.0) * d.grid.cell_size
            tanb = np.maximum(np.asarray(d.slope, dtype=float), 1e-4)
            self._lam = np.log(a / tanb)
            self._lam_bar = float(self._lam.mean())
        return self._lam, self._lam_bar

    def __call__(self, moisture, soil_hydraulics, rain, pet, terrain_derivatives, params):
        p = self.p
        lam, lam_bar = self._lambda(terrain_derivatives)
        cap = np.asarray(soil_hydraulics.capacity, dtype=float)
        s = np.asarray(moisture, dtype=float).copy()
        fl = np.zeros((len(TopmodelFlux), *s.shape))

        # local deficit and where the ground is saturated
        s_local = self.s_bar + p.m * (lam_bar - lam)
        saturated = s_local <= 0.0

        # rain: saturated cells shed it, the rest take it in
        runoff = np.where(saturated, rain, 0.0)   # saturation excess, the only runoff
        infil = rain - runoff
        s = s + infil
        fl[TopmodelFlux.INFILTRATION] = infil
        fl[TopmodelFlux.RUNOFF] = runoff

        # what the root zone cannot hold percolates to the saturated store
        perc = np.maximum(s - cap, 0.0)
        s = s - perc
        fl[TopmodelFlux.PERCOLATION] = perc

        # evaporation from the root-zone store
        full = np.clip(np.divide(s, np.maximum(cap, 1e-9)), 0.0, 1.0)
        ev = np.minimum(pet * full ** p.stress_exponent, s)
        s = s - ev
        fl[TopmodelFlux.EVAPORATION] = ev

        # trees draw on the saturated zone when the water table is within reach
        uptake = np.zeros_like(s)
        if p.tree_fraction > 0:
            z_wt = np.maximum(s_local, 0.0) / p.specific_yield          # m below surface
            reach = np.clip(1.0 - z_wt / p.tree_reach, 0.0, 1.0)
            unmet = np.maximum(pet - ev, 0.0)
            uptake = p.tree_fraction * unmet * reach
        fl[TopmodelFlux.UPTAKE] = uptake

        # the catchment store: recharge in, baseflow and uptake out
        q0 = p.t0 * np.exp(-lam_bar)                                     # m/day
        qb = q0 * np.exp(-self.s_bar / p.m)                              # m/day
        recharge_m = float(perc.mean()) / 1000.0
        uptake_m = float(uptake.mean()) / 1000.0
        self.s_bar = max(self.s_bar + qb + uptake_m - recharge_m, 0.0)
        fl[TopmodelFlux.BASEFLOW] = qb * 1000.0
        self.history.append((self.s_bar, float(saturated.mean())))
        return s, fl


def t():
    """Mass balance closes on the root-zone store, and a wetter catchment saturates more."""
    from terrasim2.k.terrain_grid import TerrainGrid
    from terrasim2.k.terrain_derivatives import TerrainDerivatives
    from terrasim2.k.soil_hydraulics import SoilHydraulics
    rng = np.random.default_rng(0)
    elev = np.cumsum(rng.random((12, 12)), axis=0) * 3.0
    d = TerrainDerivatives(TerrainGrid(elev, 10.0))
    h = SoilHydraulics(np.full((12, 12), 50.0))
    step = StepTopmodel(TopmodelParams())
    s = np.full((12, 12), 25.0)
    for _ in range(40):
        before = s.copy()
        s, fl = step(s, h, np.full((12, 12), 8.0), np.full((12, 12), 3.0), d, None)
        bal = (before + fl[TopmodelFlux.INFILTRATION] - fl[TopmodelFlux.PERCOLATION]
               - fl[TopmodelFlux.EVAPORATION]) - s
        assert np.abs(bal).max() < 1e-9, np.abs(bal).max()
    wet = StepTopmodel(TopmodelParams(initial_deficit=0.0))
    dry = StepTopmodel(TopmodelParams(initial_deficit=0.5))
    for st in (wet, dry):
        st(np.full((12, 12), 25.0), h, np.full((12, 12), 8.0), np.full((12, 12), 3.0), d, None)
    assert wet.history[0][1] >= dry.history[0][1]
    assert fl.shape == (6, 12, 12)


if __name__ == "__main__":
    t()
    print("step_topmodel tests PASS")
