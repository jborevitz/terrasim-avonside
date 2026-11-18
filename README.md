# terrasim-avonside

Two spatial models of soil water on one farm, run on the same prepared site, and the
figures that explain why they disagree.

The farm is **845 Avonside**, in the Snowy Mountains of New South Wales (−36.4355,
148.7257, 861 m). The modelled domain is 113 ha, **164 × 146 cells of 10 m**, driven by
**7,305 days** of SILO point weather (2006–2025).

This repository is a library plus its worked example. The library is a TOPMODEL step that
conforms to [TerraSim2](https://github.com/thestochasticman/TerraSim2)'s `StepFunction`
protocol and is not specific to this farm. The example is Avonside.

## Provenance — please read before reusing the model code

`src/terrasim_avonside/step_topmodel.py` is an **independent reimplementation** of the
TOPMODEL formulation, written to the `StepFunction` signature so it can be compared
against Yasar Arfat's subsurface bucket step on identical inputs. **No source code was
copied from any of his repositories.** At the time of writing,
`thestochasticman/DownscalingMoistureModel` carries no licence file and is therefore
all-rights-reserved; being on the same team is not a licence, because a downstream reader
has no way to know an internal arrangement exists. The comparison in this repository is
made from his method as presented, run through TerraSim2's own public API.

## How the two models differ

![Process diagram: Yasar's subsurface step against our TOPMODEL](docs/avonside_two_model_process.png)

Both carry the same 0.3 m root-zone bucket on the same hillslope. The difference is
underneath it.

**Yasar's subsurface step** has a root-zone store and a free store above field capacity.
Water leaves downward as `leak`, a fixed share of conductivity, and sideways as `drainage`
to the downslope neighbour, where it arrives as `inflow`. There is no catchment store, so
there is no water table, no baseflow, and nothing for a tree root to reach. A cell
saturates only when its own store fills.

**Our TOPMODEL** keeps that bucket but puts a catchment store beneath it, carried as the
mean saturation deficit `S̄`. The local deficit `S_i = S̄ + m(λ̄ − λ_i)` sets the water
table depth; cells with `S_i ≤ 0` are saturated and shed rain as saturation excess;
percolation recharges the store; baseflow `Q₀·exp(−S̄/m)` drains it; and trees draw from
it when the table is within about a metre.

Bulk density is the single measured property that sets both how much the soil holds and
how fast it conducts, and it is the same input to both models. Across the four parts of
the farm it runs from 1.31 g/cm³ in the upper forest to 1.43 in the northerly woodland —
a difference of +0.115 g/cm³ (Welch p < 0.001) that carries porosity 0.504 against 0.461
and Ksat 60.6 against 40.6 mm/h.

### The result

![The two models on the same farm](docs/avonside_two_models.png)

The two models **agree closely on evaporation and disagree completely on runoff**, because
only the TOPMODEL lets ground saturate from below.

| mm/yr over the 113 ha | Yasar, lateral ×1 | Yasar, lateral ×30 | our TOPMODEL |
|---|---|---|---|
| evaporation | 455.4 | 457.3 | 421.8 |
| below the root zone | 82.3 | 66.6 | 91.2 (percolation) |
| moved downslope | 2.4 | 138.0 | — |
| runoff | 0.0 | 0.0 | **24.8** |
| baseflow | — | — | 66.9 |
| tree uptake | — | — | 21.1 |

On the evaporation line alone the models are 7.4% apart. They close to **2.7%** once the
TOPMODEL's 21.1 mm/yr of tree uptake is counted as evaporative loss, which it is — that
water is transpired. Quote whichever you mean, but say which. Disposal totals come to
537.7 mm/yr (Yasar ×1) and 534.6 (TOPMODEL) against 536.9 mm/yr of rain.

## Hourly rainfall

![Hourly rainfall intensity, BARRA-C2 2006-2025](docs/avonside_hourly_rain.png)

`data/barra/` holds 20 years of hourly precipitation from BARRA-C2 at the 4.4 km cell
serving the farm, pulled from NCI over OPeNDAP by `scripts/pull_barra_hourly.py`.
Precipitation is published only at 1-hourly; the 20-minute product carries wind variables,
not rain.

![SILO against BARRA-C2, day by day and year by year](docs/avonside_silo_vs_barra_daily.png)

**Aligning the two is worth more than it looks.** SILO's day is the 24 hours ending at
9am, so the matching BARRA window starts at 23:00 UTC (09:00 AEST) and carries a two-day
label shift. Get that right and daily correlation is **r = 0.73**; align naively to UTC
midnight and it collapses to **r = 0.22**. The wet bias is also not a constant factor —
the annual ratio runs from 1.14 to 2.29 across the twenty years, so the ×0.577 correction
is an average, not a per-year fix. The 7,870 mm of 20-year excess partitions exactly as:
**+6,099 mm (78%)** extra rain on the 1,253 days both call wet, **+2,485 mm (32%)** on the
680 days SILO calls dry but BARRA rains, **+113 mm (1%)** on days both call dry, and
**−828 mm (−11%)** handed back on the 265 days SILO calls wet but BARRA does not. BARRA
has 1,933 wet days against SILO's 1,518 — the familiar reanalysis drizzle problem.

Two further things the record settles:

- **BARRA-C2 is 73% wetter than SILO here** — 930.5 mm/yr against 536.9 at the farm point.
  Every calendar month is biased the same way and monthly r = 0.86, so the timing is
  usable and the magnitude is not. The correction factor to SILO's total is ×0.577.
  Do not substitute BARRA for SILO without applying it.
- **Rainfall intensity barely reaches the infiltration capacity of a wettable soil.**
  8.7% of hours are wet at all, the median wet hour is 0.52 mm/h, and 98% of all rain
  falls at under 10 mm/h. Exactly two hours in twenty years reach the 47 mm/h Ksat, and
  after the SILO bias correction none do.

  **That conclusion is conditional, and the condition is not measured.** Ksat here is
  computed from texture and bulk density, so it is the conductivity of a *wettable* soil.
  Eucalypt litter is a well-known cause of soil water repellency, which can cut effective
  infiltration by an order of magnitude irrespective of pore space. At an effective
  10 mm/h the record already holds 134 hours over 20 years; at 5 mm/h, 616. So
  infiltration-excess runoff cannot be ruled out under the forest and woodland litter,
  particularly after a dry spell, and the question is a field measurement — water-drop
  penetration time or a mini-disk infiltrometer under litter against adjacent grass —
  not something a reanalysis can settle.

## Which rainfall do you believe?

![Three measurement footprints over the four-tile LiDAR block](docs/avonside_rain_pixels.png)

The farm is smaller than two of the three instruments that measure its rainfall, and it
sits on the seam of both coarse grids.

SILO's Data Drill grid is 0.05°, with cell edges here at lon 148.725/148.775 and lat
−36.475/−36.425 (measured by scanning the API, not read from documentation). The farm
centroid lies about **60 m inside the western edge** of its cell, so the property
straddles two: 44.5% of the title and **72.4% of the model domain fall in the cell to the
west**, which the 20-year forcing never used. BARRA-C2's 0.04° cell edge at lon 148.720
splits the farm too, leaving 26% of the domain outside the pixel we sampled.

| | mm/yr |
|---|---|
| SILO east cell — used for the 20-year forcing | 536.9 |
| SILO west cell | 607.7 |
| BARRA-C2 cell, as published | 930.5 |

**But do not correct the forcing on that basis.** BoM's own gridded analysis, AGCD, sits
on the *same* 0.05° grid and was pulled from NCI for 2006–2019. The two products agree on
daily rainfall almost perfectly (r = 0.976) and on a broad west-wet gradient across the
window — and they disagree completely about where it steepens. Along latitude −36.45,
AGCD declines smoothly from west to east (573, 545, 539, 528, 521 mm/yr) while SILO is
**non-monotonic**, stepping *up* to 581 at the farm's western cell against 570 in the cell
further west, then dropping 60 mm in one cell.

Weighting by where the model domain actually lies therefore gives **+8.4% under SILO but
only +0.8% under AGCD**. A gradient that one interpolation places exactly on the property
boundary and the other does not place at all is an artefact of interpolation, not a
measurement. Treat the farm's rainfall as **540–565 mm/yr with the upper end unsupported**,
and do not silently adopt the SILO west cell as a correction.

**Gauges, and which ones are real.** Of the stations within 60 km, several nearby records
are entirely interpolated: Oak Vale (7.7 km) and Jindabyne (10.7 km) are **0% observed**
over 2006–2025 — the stations are closed and SILO is infilling them. Six stations are
genuinely observing, and they are almost all to the east:

| station | km | elevation | observed | mm/yr |
|---|---|---|---|---|
| Berridale (Bolton St) | 11.8 E | 895 m | 94.9% | 553.9 |
| Dalgety (Hamilton St) | 12.7 E | 775 m | 97.5% | 534.8 |
| **Jindabyne (Glochinbah)** | **13.4 W** | **990 m** | **96.6%** | **654.8** |
| Dalgety (Severn Park) | 19.0 E | 895 m | 93.3% | 531.8 |
| Cooma Airport AWS | 27.2 E | 930 m | 99.0% | 558.6 |
| Cooma (Myalla) | 34.5 E | 1042 m | 94.5% | 608.7 |

The single operating western gauge is **18% wetter than the nearest eastern one**, which
supports a west-wet gradient at the 25 km scale — though Glochinbah is also 95 m higher,
so elevation and longitude cannot be separated with one western gauge. Across these
six, rainfall rises about 40 mm/yr per 100 m of elevation, though with n = 6 and elevation
confounded with longitude the fit is weak (r² = 0.58, p = 0.08) and should not be leaned
on hard.

**And the farm is higher than SILO thinks it is.** SILO reports 861 m for its cell. The
four farm parts average 1175 m (Top farm), 1055 m (Upper forest), 995 m (Northerly
woodland) and 951 m (Lower forest flats) — 224 m of internal relief, all of it above the
cell elevation. Taken with the gradient above that implies a real within-farm rainfall
range, and that every part of the farm is wetter than the forcing says.

## Summer and winter rain are different processes

![Seasonal rainfall intensity](docs/avonside_seasonal_intensity.png)

Splitting the hourly record by season separates the two rainfall regimes cleanly:

- On wet days, the wettest hour carries a median **39% of summer daily rain against 32%
  in winter** (Mann-Whitney p ≈ 1e-12, n = 526/483 wet days).
- **19.1% of summer rain falls at more than 10 mm/h, against 0.6% of winter rain** — a
  32-fold difference.
- The wettest winter hour in twenty years is **11.0 mm/h**; the wettest summer hour is
  **51.8 mm/h**.

So whatever runoff intensity can generate at this site, it is a **summer process
exclusively**. That matters for the water-repellency question above, because summer is
also when the soil is driest and eucalypt-litter repellency is strongest — the two
mechanisms peak together rather than cancelling.

## Design rainfall: the frequency reference

![BoM design rainfall against the soil's infiltration capacity](docs/avonside_design_rainfall.png)

**What IFD is.** Intensity–Frequency–Duration is the Bureau's 2016 design rainfall product.
It is not a time series and cannot tell you what fell on any given day. It answers a
different question: *for a storm of duration D, how deep does the rain get before it
becomes a 1-in-N-year event?* It is derived by fitting frequency distributions to the
Bureau's ground gauge archive — thousands of stations, many with records far longer than
twenty years — and interpolating the fitted parameters onto a grid.

**Why it beats everything else here for intensity questions.** SILO and AGCD are daily, so
they cannot see a burst at all. BARRA is hourly and, as the table below shows, 1.5× too
extreme. The radar measures the right timescale but needs a Z–R assumption and sits
2 km above the ground. IFD is built from the one instrument that actually catches short
bursts at ground level — the tipping bucket — and pools far more station-years than any
single record near Avonside. It is also on a **~0.0125° grid, about 1.4 km, four times
finer than SILO or AGCD**, fine enough that the farm's four parts fall in **three
different IFD cells**.

**Where to get it.** `bom.gov.au/water/designRainfalls/revised-ifd/` — enter the
coordinate in decimal degrees with a negative latitude, tick the sub-daily durations so
the table starts at 1 minute, choose depths, and download the CSV. The site refuses
non-browser clients, so this is a manual step. `data/ifd_depths_Top_farm_all_design.csv`
is the Top farm pull (requested −36.43347, 148.71793; nearest grid cell 36.4375 S,
148.7125 E).

**What it says about this farm.** The soil's wettable Ksat is 47 mm/h. Expressed as a
depth, that line crosses the design curves between 10 minutes and an hour:

| burst duration | depth to reach 47 mm/h | times per year |
|---|---|---|
| 5 min | 3.9 mm | **1.44** |
| 10 min | 7.8 mm | **0.75** |
| 15 min | 11.8 mm | 0.41 |
| 20 min | 15.7 mm | 0.24 |
| 30 min | 23.5 mm | 0.10 |
| 60 min | 47.0 mm | 0.01 — once a century |

So short bursts beat the soil's infiltration capacity **roughly once a year**, and the
"two hours in twenty years" figure derived from hourly data was an artefact of hourly
averaging — it is the 60-minute row of this table and nothing more. A 10 mm fall in
10 minutes, which Justin reports seeing run off, is a **1-in-2.8-year event** here.

IFD also condemns BARRA's extremes. BARRA's six biggest hours in twenty years map to
recurrence intervals of 1 in 177, 110, 60, 18, 11 and 8 years. A twenty-year record should
top out near the 1-in-20-year value of 34.0 mm; BARRA's largest hour is 51.8 mm, **1.5×
too large**, with its top four hours all above what the record should contain. Size storms
from IFD, not from BARRA.

## Radar: a rain gauge in the sky

![One storm, three instruments](docs/avonside_storm_20150105.png)

BoM's radar volumes are on NCI under project `rq0`, indexed by radar id. Captains Flat is
radar 40, **111.4 km** from the farm, archived **2002–2026 at a volume every 6 minutes**
with 14 tilts. These are ODIM HDF5 files holding reflectivity as numbers — not the binned
colour images on the Bureau's website.

**It is literally a gauge in the sky, and that is the catch.** The dish is 1,382.7 m above
sea level and the beam is 1.9° wide (confirmed from the files' own `/how/beamwH`), so at
this range it is 3.7 km deep: the lowest scan samples roughly **60 m to 3,770 m above the
farm**, centred **1,915 m** up. Note that figure is above Top farm's own 1,175 m, not above
SILO's 861 m grid elevation, which sits below the entire property. It measures
hydrometeors *aloft*. What it sees may evaporate before landing, or grow by collision
below the beam. Shallow winter rain is under-seen; deep summer convection is seen well —
which is convenient, because convection is the part that matters for runoff.

**This is not the same thing as IFD and the two are not alternatives.** The radar is a
measurement of individual events at 6-minute resolution with no frequency information;
IFD is a frequency distribution at ground level with no events in it. Radar tells you what
a storm did; IFD tells you how often a storm like that is permitted to happen. Used
together, the radar supplies event structure and IFD calibrates whether that structure is
typical or freakish.

The worked example above is 5 January 2015, the day BARRA claims a 1-in-177-year hour.
The radar finds the day's rain arriving in a **single 45-minute cell** — echo in 32 of 240
scans, peaking at 60.5 dBZ, which is hail. Three instruments, three answers for the same
day: **SILO 21 mm, radar 51 mm, BARRA 95 mm**. BARRA gets the peak hour about right
(51.8 mm against the radar's 46.5 mm) and then adds ~44 mm of rain after the cell has
gone — its drizzle bias visible inside one event.

`data/radar/` holds the extracted 6-minute series for that storm and a 20-year
warm-season storm-day index (3,555 days ranked by daily 40 dBZ echo area, built from the
archive's own metadata) so that volumes can be pulled for chosen storms rather than
wholesale — one day is 354 MB.

**The radar has now been calibrated against gauges, and it reads low.** Extracting the
pixel over six genuinely-observing stations for 54 archive days gives 126 radar–gauge
station-days. Radar depth must be **multiplied by 1.91** to match the gauges (95% CI 1.51
to 2.55, bootstrapped over the 26 days, which are the real unit of replication since up to
six stations share a day). The factor is flat in event size — ×1.96 for events under 20 mm,
×1.91 for events over — so it is not an artefact of how small events are weighted.

Two honest limits on that number. First, **the scatter is the real constraint**: after
applying the factor, a single station-day still carries a weighted absolute error of 47%.
Second, **we could not explain the deficit**. Beam height looked like the culprit across
stations, but with day-clustered errors and squared error in millimetres — so that large
events drive the fit — the coefficient is +0.05 per km (p = 0.84) and adding it does not
improve RMSE at all. Storm concentration fails the same way. The calibration days were also
chosen as the wettest of each season, which biases any size-dependent term; days drawn
across the whole rainfall distribution would give those terms a fair test.

**Gauge interpolation beats calibrated radar for daily depth, and it is not close.**
Leaving each of the six stations out in turn and interpolating it from the other five
(9–23 km away) gives RMSE 9.7 mm against the calibrated radar's 26.0 mm on exactly the same
station-days, with r = 0.90 against 0.58. Use radar for **event structure and timing**,
which gauges cannot supply at all, and gauges for depth.

Remaining caveats on every radar number here: generic Marshall–Palmer Z = 200·R^1.6, a
53 dBZ hail cap that is a convention not a measurement, no attenuation or beam-blockage
correction, and a sample volume wider than the farm. Note also that forcing Marshall–Palmer
to close the gauge gap would need a coefficient of 71 against a standard range of 200–500,
so the deficit is not plausibly a Z–R problem.

### Use the module, not the recipe

The hand recipe above is correct only for pre-upgrade volumes, and the archive is not
uniform. `src/terrasim_avonside/rainfall.py` handles the variation, and
`scripts/pull_rain.py` drives it.

Two traps it exists to avoid:

1. **The ODIM layout changed at the dual-polarisation upgrade.** Before it, Captains Flat
   volumes held 14 tilts with `dataset1` the lowest at 0.5° and 500 m gates. From 2021
   there are 13 tilts in *descending* order, so the 0.5° tilt is `dataset13`, gates are
   250 m, cadence is 5 minutes, and clutter-filtered `DBZH_CLEAN` appears. **A reader
   hard-coded to `dataset1` silently returns nothing for recent years** — that is exactly
   what cost 8 days of the calibration pull above. The module finds the sweep by elevation
   angle and reads gate spacing from the file.
2. **Scan cadence varies across the archive** (5, 6 and 10 minutes). Accumulating with a
   fixed 6-minute step understates a 10-minute day by 40%. The module uses each day's own
   median step.

It always pulls **both SILO and radar** for the same coordinates, because the two fail in
different ways and the choice belongs to whoever is using them. Radar is sampled with a
**±1 ray halo** and the per-ray envelope is carried into the output: at 110 km one ray is
about 1.9 km, so on a convective day that envelope is the real spatial uncertainty. On
5 January 2015 the farm total is 50.6 mm with an envelope of 29.8 to 59.8 mm.

Geometry is computed once and every scan sampled in one vectorised gather, so a whole
property costs little more than a single point — built for the 10,000 ha case where
within-farm variation is real:

```bash
# one point, one storm day
python scripts/pull_rain.py --lat -36.43347 --lon 148.71793 --days 20150105 --out topfarm

# a property on a 250 m grid, across the upgrade boundary
python scripts/pull_rain.py --bbox -36.45 148.70 -36.42 148.74 --grid 250 \
    --days 20150105 20211125 --out farmgrid
```

`tests/test_rainfall.py` pins the behaviour, including that the lowest tilt on a 2021
volume is *not* `dataset1`. The volume-reading tests skip unless `TERRASIM_ODIM_PRE` and
`TERRASIM_ODIM_POST` point at directories of real `.h5` files.

## The lesson, after five rainfall products

> Summer rainfall is hardest to observe, hardest to record where and when, and hardest of
> all to predict. In summer you get what you get, and catching a thunderstorm is worth
> being ready for. Our tools will help us predict how to be ready, and by how much it will
> help.

Every instrument on this page agrees, and they fail in different ways, which is why the
agreement is worth something:

| | summer | winter |
|---|---|---|
| radar against gauges (r, daily depth) | 0.26 | 0.91 |
| gauge network, leave-one-out (r) | 0.71 | 0.90 |
| gauge network, leave-one-out (weighted error) | 50.7% | 37.5% |
| rain falling above 10 mm/h | 19.1% | 0.6% |

Winter rain is widespread and slow, so a gauge 15 km away is a good witness and the radar
tracks it well. Summer rain arrives in cells smaller than a radar pixel and smaller than
the gap between gauges, so **neither instrument can tell you how much fell on this farm**.
The pixel test makes the point sharply: shifting the sampled radar pixel by two rays moves
the 5 January 2015 farm total between 20.1 and 52.2 mm, because the cell's edge sits inside
the property.

That is not a failure to be fixed with a better product. It is a property of the rain, and
it has a management consequence: the summer storm is the event that most affects this
place and is least predictable, so the useful question is not *will it rain* but *is the
farm ready when it does* — contours cut, cover maintained, soil able to take water quickly.

**Where the missing information eventually turns up.** What no rain gauge recorded, the
vegetation did. Sentinel-2 NDVI in the weeks after a storm carries the residual — the
response is proportional to cumulative photosynthesis, so the plants integrate the rainfall
the instruments missed. Coupling that to
[DAESIM](https://github.com/NortonAlex/DAESIM), the Dynamic Agro-Ecosystem Simulator, is
how this becomes a prediction of readiness rather than a post-hoc rainfall estimate.

## Speculative: do the trees seed their own rain?

*This section is speculation, flagged as such, and nothing in this repository depends on
it. It is recorded because it is a decade-scale research question this farm is unusually
well placed to ask.*

Eucalypts are strong emitters of biogenic volatile organic compounds — isoprene and
monoterpenes. CSIRO describes eucalypts as among the highest emitters of the BVOCs
responsible for the Blue Mountains' blue haze. Those compounds oxidise in the atmosphere
into secondary organic aerosol, and SOA of this kind is reported to supply up to half of
all cloud condensation nuclei globally. Isoprene-derived SOA is a competent nucleus: its
hygroscopicity parameter is around 0.12, similar to the ~0.1 of monoterpene SOA. There is
even a pathway running through clouds themselves — cloud processing of isoprene oxidation
products is estimated to produce roughly 6.9 Tg of SOA per year, about 20% of the biogenic
burden and the main source in the mid-troposphere.

The speculative chain is therefore: forest cover → BVOC emission → secondary organic
aerosol → cloud condensation nuclei → cloud microphysics, and possibly rainfall. If it
operates at landscape scale, a revegetated catchment is not only consuming water but
partly seeding its own supply.

Two honest cautions. First, do not assume a large effect: CSIRO's own field campaign found
modelled isoprene emissions overestimated by a factor of six, and suggested eucalypts emit
less than previously thought because the high rates in models came from young trees under
seven years old. Second, that caveat is itself the interesting part here, because it makes
emission an **age and structure** property — and this farm carries a measured
age-and-structure gradient from intact tall forest to resprouting dieback. Which species
and which stand ages emit most is not settled by a literature search and remains open.

Sources to start from:
- CSIRO, *Beating the eucalypt blues* — https://www.csiro.au/en/news/all/articles/2016/april/beating-eucalypt-blues-new-ways-model-air-quality
- Lamkaddam et al., *Large contribution to secondary organic aerosol from isoprene cloud chemistry*, Science Advances — https://www.science.org/doi/10.1126/sciadv.abe2952
- Engelhart et al. (2011), *Cloud condensation nuclei activity of isoprene secondary organic aerosol*, JGR Atmospheres — https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JD014706

## Effective precipitation: what actually gets into the soil

![Effective precipitation at Avonside](docs/avonside_effective_rain.png)

**This section has a direct consequence for the model.** Both step functions in this
repository — Yasar's subsurface bucket and our TOPMODEL — receive `rain` and put it
straight into the root-zone store, with no canopy ahead of it. That is an error of about
10% of gross rainfall under forest here, and the error is not in the rainfall product.

It is also a cautionary tale about assumed parameters: an earlier version of this section
put the figure at 50%, and the whole difference came from one number nobody had measured.

### Rather less of the rain is intercepted than we first thought

Putting a canopy-interception filter over the 20-year hourly series (bias-corrected to
SILO's total, 536.9 mm/yr gross), with the canopy store held per unit *canopy* area and
the loss to the ground scaled by canopy cover 0.553.

**The canopy store is carried as a range, not a single number.** We use the measured
eucalypt low and high, **0.33–0.65 mm per unit canopy area**:

| canopy store | intercepted | into the soil | effective |
|---|---|---|---|
| forest, 0.33 mm (low) | 43.0 mm/yr | **494 mm/yr** | **92%** |
| forest, 0.47 mm (mid) | 49.3 mm/yr | 488 mm/yr | 91% |
| forest, 0.65 mm (high) | 56.0 mm/yr | **481 mm/yr** | **90%** |
| grass | 56.1 mm/yr | 481 mm/yr | 90% |

The whole measured range moves effective rainfall by 13 mm/yr — 2% of gross — so the
choice within it is no longer load-bearing. `data/effective_precip/avonside_interception_euc_range.csv`.

**An earlier version of this section said 272 mm/yr and 49% effective. That was wrong,
and the error was a single assumed parameter.** It used a 3 mm canopy store. Measured
values for eucalypts are far smaller: Bulcock and Jewitt (2012,
[HESS 16:3717](https://doi.org/10.5194/hess-16-3717-2012)) measured a canopy storage
capacity of **0.33–0.65 mm, mean 0.47 mm at LAI 2.7**, for an *Eucalyptus grandis*
plantation — the lowest of the three species they measured despite the highest LAI, which
is the pendulous waxy-leaf effect. The mean is **0.174 mm per unit LAI**, about six times
smaller than the value assumed here; but see the note below on why we no longer scale the
store by LAI.

The shape of the rainfall still matters — **73% of gross rain arrives in hours of under
3 mm**, and the mean wet hour is 0.81 mm — but with a realistic store the canopy no longer
absorbs whole events.

**Interception here is 8.0–10.4% of gross rain** across the measured store range (14.5–18.9%
if the canopy were closed rather than 55% cover), against 14.9% measured for a closed eucalypt
plantation and a global median of 21.8% across 2,430 observations. Running our model with
that plantation's own parameters under Avonside rainfall gives 16.6% against their measured
14.9% — the right magnitude, and higher as it should be, since our smaller events favour
interception.

**LAI is not the sensitive parameter; the store was.** Across the whole plausible LAI range
— including a seasonal cycle thinning from 2.0 in winter to 1.0 in summer — interception
moves only between 42 and 63 mm/yr. Once the store is a few tenths of a millimetre,
interception is governed by *how many times the canopy gets wet*, not by how much it holds.

Canopy cover from the 2018 LiDAR, by part: Top farm 0.50 (canopy 9.3 m), Upper forest 0.66
(10.9 m), Northerly woodland 0.65 (7.4 m), Lower forest flats 0.58 (6.0 m). **The woodland
is not more open than the forest — it is shorter.** Modelled interception spans only
8.4–11.8% across the four parts, so differentiating them is not yet justified.

### The canopy store is borrowed, and it is measurable in an afternoon

**What we use, and why.** 0.33–0.65 mm per unit canopy area, from a *Eucalyptus grandis*
plantation in KwaZulu-Natal (Bulcock and Jewitt 2012,
[HESS 16:3717](https://doi.org/10.5194/hess-16-3717-2012)) — a different species, a
different climate and a closed plantation canopy, transferred to an open *E. viminalis* /
*E. pauciflora* woodland. It is the best measured eucalypt anchor we have and it is
explicitly a placeholder for a leaf-type value of our own.

**Three things are known to be uncertain about it.**

1. **The store depends on rainfall intensity, not just on the canopy.** Bulcock and Jewitt
   fit storage as a power law in intensity with an exponent near −0.3: low-intensity drops
   have little kinetic energy and settle, large drops dislodge water. Their storage changes
   little above 1–2 mm/h for *E. grandis*. **73% of our rain falls in hours under 3 mm**, so
   Avonside sits in the regime where storage is at the *high* end of its range — the 0.65 mm
   case is likely the better central estimate for us, not the 0.47 mm mean.
2. **Leaf width is probably the wrong axis to split species on.** The parameter that
   governs shedding is the **drop retention angle** — water runs off once leaf inclination
   exceeds it — and it does not track the static contact angle (Lenz, Bauer and Ruxton 2021,
   *J. Exp. Bot.*, [10.1093/jxb/erab479](https://doi.org/10.1093/jxb/erab479)). Narrow
   elongated leaves and drip tips shed *more* readily. Eucalypt leaves hang pendulously,
   which explains the low plantation storage better than leaf area or width does. Prediction
   worth testing: ribbon gum (~1 cm leaf) and snow gum (~3 cm) differ threefold in width but
   both hang, so they should store *similarly*, and a width-based split would be wasted work.
3. **The measurement method itself moves the number.** Spraying and submergence give
   systematically different maximum storage, hydrophobic leaves hold more water, and
   trichomes and serrated margins raise spray-based capacity (Cao, Li, Seibert and
   Gerlein-Safdi 2026, *Ecohydrology*,
   [10.1002/eco.70162](https://doi.org/10.1002/eco.70162)). Note the unresolved tension with
   the point above: that synthesis finds serrated margins *raise* holding capacity while the
   retention-angle review finds elongation and drip tips *lower* it.

**A student project that would settle it, with a balance and a protractor.** Two
measurements, both on fresh ribbon gum and snow gum material:

- **Maximum storage per unit leaf area.** Weigh leaf samples dry, wet them, re-weigh, divide
  by one-sided leaf area (scan or grid-count). Do it **both ways — spray to runoff and full
  submergence** — and report both numbers, because they disagree and the disagreement is the
  honest error bar. Repeat on branch sections if time allows: twigs and bark hold water too,
  and the canopy store is not only leaves.
- **Drop retention angle.** Put a wetted leaf on a tilting stage, raise it until the drop
  runs, record the angle. Compare that angle against the leaves' *natural* inclination in the
  canopy — if inclination routinely exceeds retention angle, the canopy sheds and the store
  is small regardless of leaf area.

Either number replaces a borrowed constant with a measured one. The second is the one the
literature says actually governs the physics, and nobody appears to have measured it for
these two species.

Still missing: a **litter** store. The same study measured litter interception separately at
8.5% of gross — roughly 46 mm/yr here — and neither step function has such a layer. The one
field measurement that would settle this is throughfall gauges under canopy against one in
the open.

### Interception and infiltration excess act on different events

They are easy to conflate and they are not the same mechanism.

- **Interception governs the annual balance**, because it works on the many small events.
- **Infiltration excess governs the big events**, and is invisible at hourly resolution.

On the radar-measured storm of 5 January 2015 (50.9 mm at the farm), interception took
only **3.3 mm** — the canopy fills in the first minutes and is irrelevant thereafter.
Runoff, by soil state and by the resolution you look at it with:

| infiltration capacity | runoff seen hourly | runoff seen at 6 min |
|---|---|---|
| 47 mm/h (wettable) | **0.0 mm** | **9.5 mm** |
| 10 mm/h (repellent) | 27.3 mm | 35.4 mm |
| 5 mm/h (strongly repellent) | 37.1 mm | 40.8 mm |

Hourly averaging halves the peak rate — 75 mm/h becomes 37 mm/h — and on a wettable soil
it removes the infiltration-excess runoff **entirely**. A model driven by hourly rain
cannot produce this runoff no matter how its soil physics is written.

### What this implies for the step functions

1. **Add a canopy store ahead of the root-zone store**, with its own capacity and a
   wet-canopy evaporation term, and size the capacity from the measured eucalypt range
   (**0.33–0.65 mm per unit canopy area**, run low and high) rather than a round number or
   an LAI multiplier — storage here is governed by intensity and leaf posture, not by leaf
   area, and across the plausible LAI range it barely moves. Neither step currently has one.
   Without it the model is given about 10% more water than the forest floor receives, and
   with a carelessly chosen capacity it can be wrong by a factor of four in either
   direction.
2. **Drive storm experiments at sub-hourly resolution.** Hourly forcing structurally
   cannot generate infiltration-excess runoff here. The radar archive supplies 6-minute
   real storms (see the radar section); design storms can be built from the IFD depths.
3. **Make infiltration capacity a state, not a constant**, if the repellency question
   turns out to matter — it is a function of how dry the litter has been, which is
   exactly what a soil-water model already tracks.

### Why this matters for management, and for contours

Intensity-driven runoff here is summer-only: 19.1% of summer rain falls above 10 mm/h
against 0.6% of winter rain. The Northerly woodland carries the sandiest topsoil on the
property (78.8% sand) on roughly 30% grade over thin cover, and the densest (bulk density
1.43, Ksat 40.6 mm/h). A summer thunderstorm on dry, water-repellent litter over that
ground sheds water and moves litter with it.

A contour cut intended to intercept that water is therefore **sized by the runoff depth of
a single event, not by an annual average**. The earlier figure in this project of
1,140–3,733 m³/yr was an annual-average calculation and is the wrong basis for a
summer-storm intervention.

`data/effective_precip/` holds the annual balance and the storm resolution comparison.

## Vegetation

![Tree mask at 3 m, canopy >= 5 m](docs/avonside_tree_mask_3m.png)

`data/vegetation/` carries fractional tree cover on the model grid, so `tree_root_depth`
can separate grass from trees. Trees cover **58.2% of the 46.8 ha title** and 55.3% of the
113 ha model domain at a 5 m canopy cut — Top farm 33.8%, Upper forest 65.7%, Northerly
woodland 64.8%, Lower forest flats 69.6%. Dropping the cut to 4 m adds 1.67 ha farm-wide.

The 5 m cut is the one validated against the field-checked crown inventory, and it
behaves: of 17 inventory trees and 16 low linear objects known not to be trees, a 3 m
search radius finds all 17 trees and still admits only 5 of the low objects — and two of
those stood above 5 m in the 2018 lidar and are low now, which is a fallen or died-back
stem rather than a threshold failure. See `data/vegetation/README.md` for the caveats
that govern these numbers, especially that the lidar is 2018 and crowns have fallen a
median 3.3 m since.

## What is not here

**Nothing in this repository is calibrated.** There is no streamflow gauge at Avonside, so
no local observation exists to calibrate against. `m`, `T₀` and specific yield are
plausible values, not fitted ones, and every flux above should be read as a comparison
between model structures rather than a prediction of the farm's water balance.

Two further caveats worth carrying:

- The split between evaporation and percolation is partly a labelling choice set by where
  the bottom of the root zone is drawn. Water called percolation at 0.3 m has only been
  handed to the material below 0.3 m, where tree roots may still reach it.
- The subsoil basin figure of 269 mm quoted elsewhere in this project is an **upper
  bound**: SLGA maps no specific yield for saprolite.

## Layout

```
src/terrasim_avonside/step_topmodel.py   the TOPMODEL StepFunction, with inline tests
scripts/pull_barra_hourly.py             the BARRA-C2 hourly pull
scripts/pull_rain.py                     SILO + radar for any farm, both sources
src/terrasim_avonside/rainfall.py        ODIM radar and SILO extraction
tests/                                   unit tests
data/barra/                              20 years of hourly rain (CC BY — see its README)
docs/                                    figures
```

## Licence

Code in `src/` and `scripts/` is MIT (see `LICENSE`).

**`data/` is not covered by the MIT licence.** It holds Bureau of Meteorology BARRA-C2
reanalysis output, released under CC BY 4.0, with its attribution and citation
requirements set out in `data/barra/README.md`.
