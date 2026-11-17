# Effective precipitation

**Not covered by the repository's MIT licence** — derived from Bureau of Meteorology
products (BARRA-C2 reanalysis, radar) and SILO.

`avonside_effective_precip.csv` — annual water balance after canopy interception, 20-year
means over 2006–2025, for a forest canopy (3 mm store) and grass (1 mm store), with the
canopy dried between events at 2× reference ET. Gross rainfall is BARRA-C2 hourly scaled
by 0.577 to match SILO's 20-year total.

`avonside_storm_runoff_resolution.csv` — the 5 January 2015 storm as measured by radar,
run through the same interception filter and then an infiltration cap, at both 6-minute
and hourly resolution, for three infiltration capacities. Columns are millimetres for that
single storm.

**The parameters are assumptions, not measurements.** Canopy storage capacity and
wet-canopy evaporation rate between them swing interception from 28% to 61% of gross
rainfall. Any conclusion drawn from these files should carry that range.
