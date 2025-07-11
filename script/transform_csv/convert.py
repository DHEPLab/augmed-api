#!/usr/bin/env python3
"""
convert.py
══════════

Reads a raw CSV called **data.csv** (columns listed at the very end of this
file) and APPENDS four OMOP-style CSVs in the *current* directory:

┌───────────────────────┬────────────────────────────────────────────────────┐
│ File                  │ ID policy (IGNORES any existing rows)             │
├───────────────────────┼────────────────────────────────────────────────────┤
│ person.csv            │ person_id           starts at **21**              │
│ measurement.csv       │ measurement_id      starts at **21**              │
│ observation.csv       │ observation_id      starts at **541**             │
│ visit_occurrence.csv  │ visit_occurrence_id starts at **21**              │
└───────────────────────┴────────────────────────────────────────────────────┘

*Every new row* is numbered purely by its offset from those bases; existing
CSV contents are **never scanned** for “next” IDs – they’re simply appended.

──────────────────────────────────────────────────────────────────────────────
Quick-start
───────────
1. (Optional but recommended) create a venv:

       python3 -m venv .venv
       source .venv/bin/activate        # Windows: .venv\Scripts\activate

2. Install pandas:

       pip install pandas

3. Place `data.csv` alongside this script and run:

       python3 convert.py

All four CSVs will appear / grow in the working directory.

──────────────────────────────────────────────────────────────────────────────
Expected columns in **data.csv**

person_id,AGE,GENDER,MH_IBS,MH_AST,MH_ANX_DEP,FH_DIAB,FH_CANCER,FH_HYPERT,
FH_CRC,BMI,MH_MIG,MH_OA,MH_HYPO,APD,CONST,CD,RB,MH_HYPERT,MH_HYPERL,MH_DIAB,
TA,BSS,HA,FAT,SOB,CRC_RISK (LOW),CRC_RISK (MEDIUM),CRC_RISK (HIGH),CRC_SCORE,
CRC_RISK (ADJUSTED)

(Anything beyond those is ignored.)
──────────────────────────────────────────────────────────────────────────────
"""

import os
import pandas as pd
from datetime import date

# ── static config ───────────────────────────────────────────────────────────
INPUT_FILE        = "data.csv"
MEASUREMENT_DATE  = date(2024, 12, 6).isoformat()   # 2024-12-06
OBSERVATION_DATE  = MEASUREMENT_DATE                # use same ISO date

START_PERSON_ID   = 21
START_MEAS_ID     = 21
START_OBS_ID      = 541
START_VISIT_ID    = 21

# visit_concept_id pattern for first 12 rows (cycles thereafter)
VISIT_CONCEPT_SEQ = [
    9202, 9201, 9201, 9202, 9203, 9201,
    9202, 9203, 9202, 9201, 9202, 9202,
]
# simplistic mapping → visit_type_concept_id
VISIT_TYPE_MAP = {9201: 44818519, 9202: 44818518, 9203: 44818520}

BMI_VALUE      = {"UNDERWEIGHT": 18, "NORMAL": 22, "OVERWEIGHT": 27, "OBESE": 30}
GENDER_CONCEPT = {"MALE": 8507, "FEMALE": 8532}

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== AugMed CSV converter ===")
print(f"Reading {INPUT_FILE} …")

df    = pd.read_csv(INPUT_FILE, dtype=str)
count = len(df)
print(f"  rows read: {count}\n")

# ═════════════════════════════════ person.csv ═══════════════════════════════
print("▶ person.csv")
persons = []
for idx, row in enumerate(df.itertuples(index=False)):
    pid   = START_PERSON_ID + idx
    lo,hi = map(int, row.AGE.split("-"))
    persons.append(
        dict(
            person_id                  = pid,
            gender_concept_id          = GENDER_CONCEPT.get(row.GENDER.upper(), 0),
            year_of_birth              = date.today().year - (lo + hi)//2,
            month_of_birth             = "",
            day_of_birth               = "",
            birth_datetime             = "",
            race_concept_id            = 0,
            ethnicity_concept_id       = 0,
            location_id                = "",
            provider_id                = "",
            care_site_id               = "",
            person_source_value        = "",
            gender_source_value        = "",
            gender_source_concept_id   = "",
            race_source_value          = "",
            race_source_concept_id     = "",
            ethnicity_source_value     = "",
            ethnicity_source_concept_id= "",
        )
    )
    print(f"  • person_id={pid}")

person_cols = [
    "person_id","gender_concept_id","year_of_birth","month_of_birth","day_of_birth",
    "birth_datetime","race_concept_id","ethnicity_concept_id","location_id",
    "provider_id","care_site_id","person_source_value","gender_source_value",
    "gender_source_concept_id","race_source_value","race_source_concept_id",
    "ethnicity_source_value","ethnicity_source_concept_id"
]
pd.DataFrame(persons, columns=person_cols).to_csv(
    "person.csv", mode="a", header=not os.path.exists("person.csv"), index=False
)
print("  → person.csv updated\n")

# ═════════════════════════════ measurement.csv ══════════════════════════════
print("▶ measurement.csv")
meas_rows = []
for idx, row in enumerate(df.itertuples(index=False)):
    mid = START_MEAS_ID  + idx
    pid = START_PERSON_ID + idx
    vid = START_VISIT_ID  + idx           # tie to visit

    meas_rows.append(
        dict(
            measurement_id               = mid,
            person_id                    = pid,
            measurement_concept_id       = 40490382,   # BMI
            measurement_date             = MEASUREMENT_DATE,
            measurement_datetime         = "",
            measurement_time             = "",
            measurement_type_concept_id  = 0,
            operator_concept_id          = "",
            value_as_number              = BMI_VALUE.get(row.BMI.upper(), ""),
            value_as_concept_id          = "",
            unit_concept_id              = "",
            range_low                    = "",
            range_high                   = "",
            provider_id                  = "",
            visit_occurrence_id          = vid,        # **non-null**
            visit_detail_id              = "",
            measurement_source_value     = "",
            measurement_source_concept_id= "",
            unit_source_value            = "",
            unit_source_concept_id       = "",
            value_source_value           = "",
            measurement_event_id         = "",
            meas_event_field_concept_id  = "",
        )
    )
    print(f"  • measurement_id={mid} (visit_occurrence_id={vid})")

meas_cols = [
    "measurement_id","person_id","measurement_concept_id","measurement_date",
    "measurement_datetime","measurement_time","measurement_type_concept_id",
    "operator_concept_id","value_as_number","value_as_concept_id","unit_concept_id",
    "range_low","range_high","provider_id","visit_occurrence_id","visit_detail_id",
    "measurement_source_value","measurement_source_concept_id","unit_source_value",
    "unit_source_concept_id","value_source_value","measurement_event_id",
    "meas_event_field_concept_id"
]
pd.DataFrame(meas_rows, columns=meas_cols).to_csv(
    "measurement.csv", mode="a", header=not os.path.exists("measurement.csv"), index=False
)
print("  → measurement.csv updated\n")

# ═════════════════════════════ observation.csv ══════════════════════════════
print("▶ observation.csv")
family_map = [("FH_DIAB","Diabetes"),("FH_CANCER","Cancer"),
              ("FH_HYPERT","Hypertension"),("FH_CRC","Colorectal Cancer")]
crc_map    = [("CRC_RISK (LOW)","Colorectal Cancer Risk, low"),
              ("CRC_RISK (MEDIUM)","Colorectal Cancer Risk, medium"),
              ("CRC_RISK (HIGH)","Colorectal Cancer Risk, high"),
              ("CRC_SCORE","Colorectal Cancer Score"),
              ("CRC_RISK (ADJUSTED)","Adjusted CRC Risk")]
self_map   = [
    ("TA","Tenderness Abdomen"),("MH_IBS","Irritable Bowel Syndrome"),
    ("MH_AST","Asthma"),("MH_ANX_DEP","Anxiety and/or Depression"),
    ("MH_MIG","Migraines"),("MH_OA","Osteoarthritis"),
    ("MH_HYPO","Hypothyroidism"),("APD","Abdominal Pain/Distension"),
    ("CONST","Constipation"),("CD","Chronic Diarrhea"),
    ("RB","Rectal Bleeding"),("MH_HYPERT","Hypertension"),
    ("MH_HYPERL","Hyperlipidemia"),("MH_DIAB","Diabetes"),
    ("FAT","Fatigue"),("SOB","Shortness of Breath"),
    ("BSS","Blood Stained Stool"),("HA","Headache")
]

obs_rows, obs_id = [], START_OBS_ID
for idx, (_, rec) in enumerate(df.iterrows()):
    pid = START_PERSON_ID + idx
    vid = START_VISIT_ID  + idx           # tie to visit

    # 1) family history
    for col, lbl in family_map:
        obs_rows.append(
            dict(
                observation_id              = obs_id,
                person_id                   = pid,
                observation_concept_id      = 4167217,
                observation_date            = OBSERVATION_DATE,
                observation_datetime        = "",
                observation_type_concept_id = 0,
                value_as_number             = "",
                value_as_string             = f"{lbl}: {rec[col].strip().capitalize()}",
                value_as_concept_id         = "",
                qualifier_concept_id        = "",
                unit_concept_id             = "",
                provider_id                 = "",
                visit_occurrence_id         = vid,   # **non-null**
                visit_detail_id             = "",
                observation_source_value    = "",
                observation_source_concept_id = "",
                unit_source_value           = "",
                qualifier_source_value      = "",
                value_source_value          = "",
                observation_event_id        = "",
                obs_event_field_concept_id  = "",
            )
        )
        obs_id += 1

    # 2) CRC scores / risk
    for col, lbl in crc_map:
        obs_rows.append(
            dict(
                observation_id              = obs_id,
                person_id                   = pid,
                observation_concept_id      = 45614722,
                observation_date            = OBSERVATION_DATE,
                observation_datetime        = "",
                observation_type_concept_id = 0,
                value_as_number             = "",
                value_as_string             = f"{lbl}: {rec[col]}",
                value_as_concept_id         = "",
                qualifier_concept_id        = "",
                unit_concept_id             = "",
                provider_id                 = "",
                visit_occurrence_id         = vid,
                visit_detail_id             = "",
                observation_source_value    = "",
                observation_source_concept_id = "",
                unit_source_value           = "",
                qualifier_source_value      = "",
                value_source_value          = "",
                observation_event_id        = "",
                obs_event_field_concept_id  = "",
            )
        )
        obs_id += 1

    # 3) self-reported conditions
    for col, lbl in self_map:
        obs_rows.append(
            dict(
                observation_id              = obs_id,
                person_id                   = pid,
                observation_concept_id      = 1008364,
                observation_date            = OBSERVATION_DATE,
                observation_datetime        = "",
                observation_type_concept_id = 0,
                value_as_number             = "",
                value_as_string             = f"{lbl}: {rec[col].strip().capitalize()}",
                value_as_concept_id         = "",
                qualifier_concept_id        = "",
                unit_concept_id             = "",
                provider_id                 = "",
                visit_occurrence_id         = vid,
                visit_detail_id             = "",
                observation_source_value    = "",
                observation_source_concept_id = "",
                unit_source_value           = "",
                qualifier_source_value      = "",
                value_source_value          = "",
                observation_event_id        = "",
                obs_event_field_concept_id  = "",
            )
        )
        obs_id += 1

obs_cols = [
    "observation_id","person_id","observation_concept_id","observation_date",
    "observation_datetime","observation_type_concept_id","value_as_number",
    "value_as_string","value_as_concept_id","qualifier_concept_id","unit_concept_id",
    "provider_id","visit_occurrence_id","visit_detail_id","observation_source_value",
    "observation_source_concept_id","unit_source_value","qualifier_source_value",
    "value_source_value","observation_event_id","obs_event_field_concept_id"
]
pd.DataFrame(obs_rows, columns=obs_cols).to_csv(
    "observation.csv", mode="a", header=not os.path.exists("observation.csv"), index=False
)
print("  → observation.csv updated\n")

# ═══════════════════════════ visit_occurrence.csv ═══════════════════════════
print("▶ visit_occurrence.csv")
visit_rows = []
for idx in range(count):
    vid     = START_VISIT_ID + idx
    pid     = START_PERSON_ID + idx
    concept = VISIT_CONCEPT_SEQ[idx % len(VISIT_CONCEPT_SEQ)]
    vtype   = VISIT_TYPE_MAP.get(concept, 0)

    visit_rows.append(
        dict(
            visit_occurrence_id          = vid,
            person_id                    = pid,
            visit_concept_id             = concept,
            visit_start_date             = "2024-01-01",   # placeholder
            visit_start_time             = "",
            visit_end_date               = "2024-01-02",
            visit_end_time               = "",
            visit_type_concept_id        = vtype,
            provider_id                  = "",
            care_site_id                 = "",
            visit_source_value           = "",
            visit_source_concept_id      = "",
            admitted_from_concept_id     = "",
            admitted_from_source_value   = "",
            discharged_to_concept_id     = "",
            discharged_to_source_value   = "",
            preceding_visit_occurrence_id= "",
        )
    )
    print(f"  • visit_occurrence_id={vid} (person_id={pid})")

visit_cols = [
    "visit_occurrence_id","person_id","visit_concept_id","visit_start_date",
    "visit_start_time","visit_end_date","visit_end_time","visit_type_concept_id",
    "provider_id","care_site_id","visit_source_value","visit_source_concept_id",
    "admitted_from_concept_id","admitted_from_source_value","discharged_to_concept_id",
    "discharged_to_source_value","preceding_visit_occurrence_id"
]
pd.DataFrame(visit_rows, columns=visit_cols).to_csv(
    "visit_occurrence.csv", mode="a", header=not os.path.exists("visit_occurrence.csv"), index=False
)
print("  → visit_occurrence.csv updated\n")

print("=== DONE ===\n")
