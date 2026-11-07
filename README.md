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
