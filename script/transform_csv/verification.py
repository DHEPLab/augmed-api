#!/usr/bin/env python3
"""
verification.py

Quick sanity-checks for the four OMOP CSVs produced by convert.py.

• Ensures every person_id referenced in measurement.csv, observation.csv,
  and visit_occurrence.csv exists in person.csv
• Verifies that the primary-key columns (person_id, measurement_id,
  observation_id, visit_occurrence_id) are unique
• Prints a concise PASS / FAIL summary

Run *after* you have executed convert.py:

    python3 verification.py
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------

def load_csv(path: str, required: bool = True) -> pd.DataFrame | None:
    if not Path(path).exists():
        if required:
            raise FileNotFoundError(f"{path} not found")
        return None
    return pd.read_csv(path)

# load files
person_df        = load_csv("person.csv")
measurement_df   = load_csv("measurement.csv")
observation_df   = load_csv("observation.csv")
visit_df         = load_csv("visit_occurrence.csv", required=False)  # may be absent

# ---------------------------------------------------------------------------
# Helper for subset checks

def subset_ok(child_series: pd.Series, parent_set: set[int]) -> bool:
    """Return True if *all* IDs in child_series are contained in parent_set."""
    return set(child_series.unique()).issubset(parent_set)

# Primary-key uniqueness checks
checks = []

def unique_ok(df: pd.DataFrame, col: str) -> bool:
    """Verify the column has unique non-null values."""
    return df[col].is_unique and df[col].notna().all()

checks.append(("person_id uniqueness", unique_ok(person_df, "person_id")))
checks.append((
    "measurement_id uniqueness",
    unique_ok(measurement_df, "measurement_id"),
))
checks.append((
    "observation_id uniqueness",
    unique_ok(observation_df, "observation_id"),
))
if visit_df is not None:
    checks.append((
        "visit_occurrence_id uniqueness",
        unique_ok(visit_df, "visit_occurrence_id"),
    ))

# FK-style subset checks
person_ids = set(person_df["person_id"].unique())

checks.append((
    "measurement.person_id ⊆ person.person_id",
    subset_ok(measurement_df["person_id"], person_ids),
))
checks.append((
    "observation.person_id ⊆ person.person_id",
    subset_ok(observation_df["person_id"], person_ids),
))
if visit_df is not None:
    checks.append((
        "visit_occurrence.person_id ⊆ person.person_id",
        subset_ok(visit_df["person_id"], person_ids),
    ))

# ---------------------------------------------------------------------------
# Print summary

all_ok = True
print("\nValidation results:")
for name, result in checks:
    status = "PASS" if result else "FAIL"
    print(f"  {status:<4} – {name}")
    all_ok &= result

print("\nOverall:", "✔︎ ALL CHECKS PASSED" if all_ok else "✘ SOME CHECKS FAILED")
