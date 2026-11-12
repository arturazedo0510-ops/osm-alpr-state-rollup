#!/usr/bin/env python3
"""
Fetch OpenStreetMap ALPR surveillance tags and roll them up by US state.

Why by state: OSM place names (addr:city, addr:state) are inconsistent and often
missing, so grouping by a free-text field silently loses records. Administrative
boundaries do not have that problem, so the query asks Overpass for each state's
admin_level=4 area and counts whatever ALPR devices fall inside it.

Tagging convention used by OSM contributors:
    man_made=surveillance
    surveillance:type=ALPR

Usage:
    python fetch_by_state.py                      # all 51 jurisdictions
    python fetch_by_state.py --states US-CA US-TX
    python fetch_by_state.py --raw                # also dump raw elements

Output:
    data/alpr_by_state.csv      one row per state
    data/raw/<code>.json        raw Overpass payload (only with --raw)

Data (c) OpenStreetMap contributors, ODbL 1.0 - https://osm.org/copyright
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

QUERY = """
[out:json][timeout:{timeout}];
area["ISO3166-2"="{code}"][admin_level=4]->.a;
(
  node["man_made"="surveillance"]["surveillance:type"="ALPR"](area.a);
  way["man_made"="surveillance"]["surveillance:type"="ALPR"](area.a);
);
out center tags;
""".strip()

# US states + DC, ISO 3166-2 codes as used on OSM administrative boundaries.
STATES = {
    "US-AL": "Alabama", "US-AK": "Alaska", "US-AZ": "Arizona", "US-AR": "Arkansas",
    "US-CA": "California", "US-CO": "Colorado", "US-CT": "Connecticut", "US-DE": "Delaware",
    "US-DC": "District of Columbia", "US-FL": "Florida", "US-GA": "Georgia", "US-HI": "Hawaii",
    "US-ID": "Idaho", "US-IL": "Illinois", "US-IN": "Indiana", "US-IA": "Iowa",
    "US-KS": "Kansas", "US-KY": "Kentucky", "US-LA": "Louisiana", "US-ME": "Maine",
    "US-MD": "Maryland", "US-MA": "Massachusetts", "US-MI": "Michigan", "US-MN": "Minnesota",
    "US-MS": "Mississippi", "US-MO": "Missouri", "US-MT": "Montana", "US-NE": "Nebraska",
    "US-NV": "Nevada", "US-NH": "New Hampshire", "US-NJ": "New Jersey", "US-NM": "New Mexico",
    "US-NY": "New York", "US-NC": "North Carolina", "US-ND": "North Dakota", "US-OH": "Ohio",
    "US-OK": "Oklahoma", "US-OR": "Oregon", "US-PA": "Pennsylvania", "US-RI": "Rhode Island",
    "US-SC": "South Carolina", "US-SD": "South Dakota", "US-TN": "Tennessee", "US-TX": "Texas",
    "US-UT": "Utah", "US-VT": "Vermont", "US-VA": "Virginia", "US-WA": "Washington",
    "US-WV": "West Virginia", "US-WI": "Wisconsin", "US-WY": "Wyoming",
}

FIELDS = ["iso", "state", "nodes", "ways", "total", "error"]


def fetch_state(session: requests.Session, code: str, timeout: int, retries: int = 2) -> list:
    payload = {"data": QUERY.format(code=code, timeout=timeout)}
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = session.post(OVERPASS_URL, data=payload, timeout=timeout + 60)
            if r.status_code in (429, 504):
                raise RuntimeError(f"overpass busy ({r.status_code})")
            r.raise_for_status()
            return r.json().get("elements", [])
        except Exception as exc:  # noqa: BLE001 - retried below
            last = exc
            if attempt < retries:
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{code}: {last}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Roll up OSM ALPR tags by US state.")
    ap.add_argument("--states", nargs="*", help="ISO 3166-2 codes; defaults to all")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--timeout", type=int, default=180, help="per-query Overpass timeout")
    ap.add_argument("--sleep", type=float, default=2.0, help="pause between queries, be polite")
    ap.add_argument("--raw", action="store_true", help="also write raw elements per state")
    args = ap.parse_args()

    codes = args.states or list(STATES)
    unknown = [c for c in codes if c not in STATES]
    if unknown:
        sys.exit(f"unknown state code(s): {', '.join(unknown)}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.raw:
        (out / "raw").mkdir(exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "osm-alpr-state-rollup/1.0 (ODbL state rollup)"

    rows = []
    for i, code in enumerate(codes, 1):
        name = STATES[code]
        try:
            els = fetch_state(session, code, args.timeout)
        except RuntimeError as exc:
            print(f"[{i}/{len(codes)}] {code} FAILED {exc}", file=sys.stderr)
            rows.append({"iso": code, "state": name, "nodes": "", "ways": "",
                         "total": "", "error": str(exc)})
            continue

        nodes = sum(1 for e in els if e.get("type") == "node")
        ways = sum(1 for e in els if e.get("type") == "way")
        rows.append({"iso": code, "state": name, "nodes": nodes, "ways": ways,
                     "total": nodes + ways, "error": ""})
        print(f"[{i}/{len(codes)}] {code} nodes={nodes} ways={ways} total={nodes + ways}", flush=True)

        if args.raw:
            (out / "raw" / f"{code}.json").write_text(
                json.dumps(els, ensure_ascii=False), encoding="utf-8"
            )

        time.sleep(args.sleep)

    csv_path = out / "alpr_by_state.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r["iso"]))

    ok = sum(1 for r in rows if not r["error"])
    seen = sum(r["total"] for r in rows if isinstance(r["total"], int))
    print(f"\nwrote {csv_path}")
    print(f"{ok}/{len(rows)} states queried ok; {seen} tagged records seen in this run")
    print("Reminder: this is volunteered data, not a device inventory.")


if __name__ == "__main__":
    main()
