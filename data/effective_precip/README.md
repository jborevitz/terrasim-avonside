# Effective precipitation

**Not covered by the repository's MIT licence** — derived from Bureau of Meteorology
products (BARRA-C2 reanalysis, radar) and SILO.

`avonside_interception_euc_range.csv` — **the current numbers.** Annual canopy interception
over the same 20-year hourly series, at the measured eucalypt storage range 0.33–0.65 mm per
unit canopy area (Bulcock and Jewitt 2012, HESS 16:3717), canopy cover 0.553, with
wet-canopy evaporation computed by Penman at zero surface resistance rather than a multiple
of reference ET. Interception is 43.0–56.0 mm/yr, 8.0–10.4% of gross.

`avonside_effective_precip.csv` — **superseded, kept for the record.** Annual water balance
after canopy interception, 20-year means over 2006–2025, for a forest canopy (3 mm store)
and grass (1 mm store), with the canopy dried between events at 2× reference ET. Gross
rainfall is BARRA-C2 hourly scaled by 0.577 to match SILO's 20-year total. **Its 3 mm forest
store is six times the measured eucalypt value**, so its 272.4 mm/yr interception and 49%
effective rainfall are both wrong; see the main README. Awaiting regeneration, as is
`docs/avonside_effective_rain.png`.

`avonside_storm_runoff_resolution.csv` — the 5 January 2015 storm as measured by radar,
run through the same interception filter and then an infiltration cap, at both 6-minute
and hourly resolution, for three infiltration capacities. Columns are millimetres for that
single storm.

**The canopy store is now measured — but measured elsewhere, on another species.** It is
taken from an *E. grandis* plantation and carried here as a low–high pair rather than a
point value. Across that pair interception moves only 43–56 mm/yr, so the remaining
sensitivity is small; the larger open question is the *missing litter store* (8.5% of gross
in the same study). The main README sets out the two leaf measurements that would replace
the borrowed constant.
