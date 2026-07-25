#!/usr/bin/env python3
"""Validate that the canonical event ledger is internally consistent.

Checks that data/events/events.csv and data/events/events.json describe exactly
the same set of events with the same key fields, that the CSV is well-formed, and
that no un-verified forward-regression candidate has leaked into the ledger (those
belong in data/events/PROVENANCE_BACKLOG.md). Exits non-zero on any mismatch so it
can gate a release.

Usage:  python scripts/validate_ledger.py
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "events" / "events.csv"
JSON = ROOT / "data" / "events" / "events.json"

# Fields that must agree between the CSV row and the JSON object for each event.
KEY_FIELDS = [
    "fault_type",
    "event_kind",
    "pair_orientation",
    "evaluation_cohort",
    "baseline_sha",
    "candidate_sha",
    "change_metadata_sha",
    "reproducibility_status",
]

EXPECTED_N = 14  # 5 historical + 9 mutation; see EVENTS_AUDIT.md


def main() -> int:
    errors = []

    # --- CSV: well-formed, fixed field count ---
    with open(CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    ncol = len(header)
    csv_records = []
    with open(CSV, newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.reader(fh)):
            if i == 0 or not r:
                continue
            if len(r) != ncol:
                errors.append(f"CSV row {i} has {len(r)} fields, expected {ncol}")
            csv_records.append(dict(zip(header, r)))
    csv_by_id = {r["event_id"]: r for r in csv_records}

    # --- JSON ---
    data = json.loads(JSON.read_text(encoding="utf-8"))
    json_events = data.get("events", [])
    json_by_id = {e["event_id"]: e for e in json_events}

    # --- counts ---
    if data.get("n_events") != len(json_events):
        errors.append(f"JSON n_events={data.get('n_events')} but {len(json_events)} event objects")
    if len(csv_records) != EXPECTED_N:
        errors.append(f"CSV has {len(csv_records)} events, expected {EXPECTED_N}")
    if len(json_events) != EXPECTED_N:
        errors.append(f"JSON has {len(json_events)} events, expected {EXPECTED_N}")

    # --- same event_id set ---
    csv_ids, json_ids = set(csv_by_id), set(json_by_id)
    if csv_ids != json_ids:
        errors.append(f"CSV-only ids: {sorted(csv_ids - json_ids)}")
        errors.append(f"JSON-only ids: {sorted(json_ids - csv_ids)}")

    # --- no un-verified forward candidate leaked in ---
    for eid in csv_ids | json_ids:
        if eid.startswith("fwd-"):
            errors.append(f"forward candidate '{eid}' is in the ledger; it belongs in PROVENANCE_BACKLOG.md")

    # --- key fields agree ---
    for eid in sorted(csv_ids & json_ids):
        c, j = csv_by_id[eid], json_by_id[eid]
        for f in KEY_FIELDS:
            if c.get(f, "") != (j.get(f, "") or ""):
                errors.append(f"{eid}: field '{f}' CSV={c.get(f)!r} != JSON={j.get(f)!r}")

    if errors:
        print("LEDGER INVALID:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"Ledger OK: {len(csv_records)} events, CSV == JSON on {len(KEY_FIELDS)} key fields, no forward leakage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
