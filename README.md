# Aggregating OpenStreetMap ALPR surveillance tags by state

Notes and small scripts behind the community map at **https://flock-camera.com/map/**.

## What this is

[OpenStreetMap](https://www.openstreetmap.org/) contributors tag roadside ALPR
(automatic license plate reader) devices with `man_made=surveillance` and
`surveillance:type=ALPR`. Those tags are volunteered data: they are added by
people who noticed a device, they are not an official inventory, and coverage
varies a lot from one place to another.

This repository documents a simple, reproducible way to turn those tags into a
state-level rollup that a normal reader can browse:

1. Read the relevant OSM tags from a planet extract or an Overpass query.
2. Keep only records with a usable geometry.
3. Group by state boundary, not by city name (place names are inconsistent).
4. Publish the grouping as a browsable table, with the raw tags available for
   anyone to check or correct.

## Files

| File | What it does |
|---|---|
| `overpass_alpr.overql` | The canonical Overpass query, readable on its own |
| `fetch_by_state.py` | Runs that query for every state, writes the CSV |
| `requirements.txt` | Single dependency: `requests` |

## Usage

```bash
pip install -r requirements.txt

python fetch_by_state.py                       # all 51 jurisdictions
python fetch_by_state.py --states US-CA US-TX  # just a couple
python fetch_by_state.py --raw                 # keep raw elements per state
```

Output goes to `data/alpr_by_state.csv`, one row per state:

| Column | Meaning |
|---|---|
| `iso` | ISO 3166-2 code used in the query, e.g. `US-CA` |
| `state` | Human-readable name |
| `nodes` | ALPR devices tagged as standalone nodes |
| `ways` | ALPR devices tagged on the way itself (e.g. a gantry) |
| `total` | `nodes + ways` |
| `error` | Populated only if that state's query failed |

## Why an area filter and not `addr:state`

The obvious approach is to read `addr:state` off each record and group on that.
It does not work: contributed records routinely omit address tags, and where they
exist the free text varies (`CA`, `Calif.`, `California`). Asking Overpass for
`area["ISO3166-2"="US-CA"][admin_level=4]` puts the boundary in charge instead,
so a device is counted where it physically is.

## Where to look

- **Map:** https://flock-camera.com/map/
- **State-by-state table:** https://flock-camera.com/cameras/
- **Method and data caveats:** https://flock-camera.com/methodology/
- **How to recognise an ALPR device:** https://flock-camera.com/learn/identify/

## Data licence and attribution

Map data © OpenStreetMap contributors, available under the
[Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
If you reuse the derived tables, keep the attribution and share alike.

## Important caveats

- This is **community-reported** data, not a government registry and not a
  complete count of deployed devices.
- A tag can be outdated, duplicated, or describe a device that has since been
  removed. Absence of a tag does not mean absence of a camera.
- We deliberately publish no totals or coverage percentages here, because the
  underlying tag coverage is uneven and any single number would be misleading.
  The script prints counts for the operator to sanity-check a run; they are not
  presented as a national figure.
- If you find an error, the fix belongs in OpenStreetMap itself, so every
  downstream consumer benefits.

## Scope

This repository is documentation and tooling, not an official OpenStreetMap
project and not affiliated with any camera vendor, law-enforcement agency, or
advocacy group.
# Aggregating OpenStreetMap ALPR surveillance tags by state

Notes and small scripts behind the community map at **https://flock-camera.com/map/**.

## What this is

[OpenStreetMap](https://www.openstreetmap.org/) contributors tag roadside ALPR
(automatic license plate reader) devices with `man_made=surveillance` and
`surveillance:type=ALPR`. Those tags are volunteered data: they are added by
people who noticed a device, they are not an official inventory, and coverage
varies a lot from one place to another.

This repository documents a simple, reproducible way to turn those tags into a
state-level rollup that a normal reader can browse:

1. Read the relevant OSM tags from a planet extract or an Overpass query.
2. Keep only records with a usable geometry.
3. Group by state boundary, not by city name (place names are inconsistent).
4. Publish the grouping as a browsable table, with the raw tags available for
   anyone to check or correct.

## Where to look

- **Map:** https://flock-camera.com/map/
- **State-by-state table:** https://flock-camera.com/cameras/
- **Method and data caveats:** https://flock-camera.com/methodology/
- **How to recognise an ALPR device:** https://flock-camera.com/learn/identify/

## Data licence and attribution

Map data © OpenStreetMap contributors, available under the
[Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
If you reuse the derived tables, keep the attribution and share alike.

## Important caveats

- This is **community-reported** data, not a government registry and not a
  complete count of deployed devices.
- A tag can be outdated, duplicated, or describe a device that has since been
  removed. Absence of a tag does not mean absence of a camera.
- We deliberately publish no totals or coverage percentages here, because the
  underlying tag coverage is uneven and any single number would be misleading.
- If you find an error, the fix belongs in OpenStreetMap itself, so every
  downstream consumer benefits.

## Scope

This repository is documentation, not an official OpenStreetMap project and not
affiliated with any camera vendor, law-enforcement agency, or advocacy group.
