"""
AugMed Answer Export Script - Enhanced Format
=============================================

STUDY DESIGN & CASE ASSIGNMENT STRATEGY:
-----------------------------------------
• 224 recruited participants (healthcare professionals)
• Each participant assigned 100 random cases from 20,020 synthetic patients
• Random assignment with overlap allowed (same case can be assigned to multiple participants)
• Total theoretical assignments: 22,400 (224 × 100)
• Actual responses: ~1,516 (6.8% completion rate as of current export)

CASE OVERLAP DESIGN:
-------------------
• Multiple participants can review the same case (inter-rater reliability)
• Cases are drawn randomly from full synthetic patient pool (person_id 1-20,020)
• Not all synthetic patients become assigned cases (gaps in person_id sequence)
• Current data shows person_id starts at 84 (first randomly assigned case)

DATA STRUCTURE:
--------------
• 1,516 total responses from ~29 active participants
• 1,481 unique cases completed (some cases answered by multiple participants)
• person_id range: 84 to 20,000 (gaps are unassigned patients, not missing data)
• Recruitment survey integration: 220 records with 89.7% linkage success rate

EXPORT FEATURES:
---------------
• Column ordering optimized for analysis workflow
• Analytics timing columns from dedicated analytics table (not answer JSON)
• Recruitment survey data integration via email matching
• Feature extraction from display_configuration JSON for "(shown)" flags
• Patient values (Family/Medical History) from observation table, not display_configuration
• AI score mapping and risk assessment parsing from observation table
• Person_id ascending sort for consistent output
• Empty strings for missing data (not default "No" assumptions)

USAGE:
------
python script/answer_export/export_answers_to_csv_new_format.py          # Run export
python script/answer_export/export_answers_to_csv_new_format.py --test   # Test columns
python script/answer_export/export_answers_to_csv_new_format.py --investigate  # Case assignment analysis
python script/answer_export/export_answers_to_csv_new_format.py --overlap      # Overlap analysis
python script/answer_export/export_answers_to_csv_new_format.py --analyze      # Full analysis

OUTPUT COLUMNS (67 total):
--------------------------
1. person_id, user_id, order_id                          # Base identifiers
2. case_open_time → total_duration_secs                  # Analytics timing (6 cols)
3. age, gender                                           # Demographics
4. Family History.* (shown) [4 cols]                    # Family history flags
5. Medical History.* (shown) [18 cols]                  # Medical history flags  
6. ai_score (shown)                                     # AI score display flag
7. Family History.* (value) [4 cols]                   # Family history values
8. Medical History.* (value) [18 cols]                 # Medical history values
9. ai_score (value)                                     # AI score value
10. risk_assessment, confidence_level, screening_recommendation, additional_info  # Answer data
11. professional_role → years_screening                 # Recruitment survey (6 cols)

Created: 2024-09-19 | Last Updated: 2025-01-23
Contact: DHEPLab Team | Repository: augmed-api/answer-export
Fixes: Analytics table integration, observation table patient values, empty string defaults
"""

import json
import os
import re
import hashlib
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, text


# --- DB config from env (same defaults as existing exporter) ---
DB_TYPE = "postgresql"
DB_USER = os.getenv("POSTGRES_USER", "augmed")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "augmed")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "augmed")

CONN_STR = f"{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Recruitment survey data path
RECRUITMENT_SURVEY_PATH = "recruitment_survey_data - Augmed_recruit_alldoc_new.csv"


# --- Constants & mappings ---

# IMPORTANT: convert.py renumbers person_ids with START_PERSON_ID=21
# This creates a +20 offset between source data.csv and OMOP database
# We subtract this offset when exporting to match source data.csv person_ids
PERSON_ID_OFFSET = 20

FAMILY_HISTORY_FEATURES = [
    "Cancer",
    "Colorectal Cancer", 
    "Diabetes",
    "Hypertension",
]

MEDICAL_HISTORY_FEATURES = [
    "Abdominal Pain/Distension",
    "Anxiety and/or Depression",
    "Asthma",
    "Blood Stained Stool",
    "Chronic Diarrhea",
    "Constipation",
    "Diabetes",
    "Fatigue",
    "Headache",
    "Hyperlipidemia",
    "Hypertension",
    "Hypothyroidism",
    "Irritable Bowel Syndrome",
    "Migraines",
    "Osteoarthritis",
    "Rectal Bleeding",
    "Shortness of Breath",
    "Tenderness Abdomen",
]

AI_OBS_CONCEPT_ID = 45614722  # CRC risk assessments concept id

RISK_MAP = {
    "very low": 1,
    "low": 2,
    "moderate": 3,
    "high": 4,
    "very high": 5,
}


def stable_user_id(email: str) -> int:
    """Derive a stable 64-bit positive int from the email (lowercased)."""
    if not email:
        return 0
    h = hashlib.sha256(email.strip().lower().encode("utf-8")).digest()
    # Use first 8 bytes -> int, make positive
    return int.from_bytes(h[:8], byteorder="big", signed=False)


def load_recruitment_survey_data() -> Optional[pd.DataFrame]:
    """
    Load recruitment survey data from Qualtrics CSV export.
    Returns DataFrame with columns: professional_role, professional_role_other, 
    practice_years, practice_state, experience_screening, years_screening.
    Returns None if file not found or has issues.
    """
    try:
        if not os.path.exists(RECRUITMENT_SURVEY_PATH):
            print(f"Warning: Recruitment survey file not found at {RECRUITMENT_SURVEY_PATH}")
            return None
        
        # Load CSV - Qualtrics exports have metadata rows at the top
        df = pd.read_csv(RECRUITMENT_SURVEY_PATH)
        
        # Skip the first 2 rows (question text and import metadata) and get actual data
        df_data = df.iloc[2:].reset_index(drop=True)
        
        # Map Qualtrics columns to our target fields
        column_mapping = {
            'Q3': 'email',                          # Email
            'Q22': 'professional_role',             # Current professional role
            'Q22_7_TEXT': 'professional_role_other', # Other role specification
            'Q4': 'practice_years',                 # Years practicing medicine
            'Q5': 'practice_state',                 # State of practice
            'Q6': 'experience_screening',           # Experience with CRC screening
            'Q7': 'years_screening'                 # Years in CRC screening setting
        }
        
        # Check if required columns exist
        missing_cols = [col for col in column_mapping.keys() if col not in df_data.columns]
        if missing_cols:
            print(f"Warning: Missing columns in survey data: {missing_cols}")
        
        # Select available columns and rename
        available_mapping = {k: v for k, v in column_mapping.items() if k in df_data.columns}
        
        if not available_mapping:
            print("Error: No expected Qualtrics columns found in survey data")
            return None
            
        df_selected = df_data[list(available_mapping.keys())].copy()
        df_selected.columns = list(available_mapping.values())
        
        # Clean and normalize data
        if 'email' in df_selected.columns:
            # Normalize email for matching
            df_selected['email'] = df_selected['email'].astype(str).str.strip().str.lower()
            # Remove rows with empty emails
            df_selected = df_selected[df_selected['email'].notna() & (df_selected['email'] != 'nan') & (df_selected['email'] != '')]
        
        # Fill missing columns with empty strings if not present
        required_cols = ['email', 'professional_role', 'professional_role_other', 'practice_years', 'practice_state', 'experience_screening', 'years_screening']
        for col in required_cols:
            if col not in df_selected.columns:
                df_selected[col] = ''
        
        print(f"Loaded recruitment survey data: {len(df_selected)} records with valid emails")
        return df_selected
            
    except Exception as e:
        print(f"Error loading recruitment survey data: {e}")
        return None


def parse_answer_payload(ans: Any) -> Tuple[Optional[int], Optional[int], Optional[str], Optional[str]]:
    """
    Extract (risk_assessment, confidence_level, screening_recommendation, additional_info)
    from answer JSON. Handles both dict and string payloads.
    """
    def ensure_dict(val: Any) -> Dict[str, Any]:
        if isinstance(val, dict):
            return val
        if val is None:
            return {}
        # Try JSON first
        try:
            import json
            return json.loads(val)
        except Exception:
            # Try Python literal (single quotes)
            try:
                import ast
                return ast.literal_eval(val)
            except Exception:
                return {}

    data = ensure_dict(ans)
    
    if not data:
        return None, None, None, None

    # Find the actual keys by looking for patterns (case-insensitive, flexible matching)
    risk_val = None
    conf_val = None
    screen_val = None
    addl_info = None
    
    for key, value in data.items():
        key_lower = key.lower().strip()
        
        # Risk assessment question
        if "assess this patient's risk for colorectal cancer" in key_lower:
            risk_val = value
        
        # Confidence question  
        elif "confident are you in your screening recommendation" in key_lower:
            conf_val = value
            
        # Screening recommendation question
        elif "colorectal cancer screening options would you recommend" in key_lower:
            screen_val = value
            
        # Additional information question - matches "In addition to the presented information, what other information would have been useful..."
        elif "addition" in key_lower and "information" in key_lower and "useful" in key_lower:
            addl_info = value

    # Parse risk_assessment (map phrase -> int)
    risk_num: Optional[int] = None
    if isinstance(risk_val, str):
        word = risk_val.strip().lower().replace(" risk", "")
        risk_num = RISK_MAP.get(word)

    # Parse confidence_level (string starts with digit)
    conf_num: Optional[int] = None
    if isinstance(conf_val, str):
        m = re.match(r"\s*(\d)", conf_val)
        if m:
            conf_num = int(m.group(1))

    # Parse screening recommendation normalization
    screen_norm: Optional[str] = None
    if isinstance(screen_val, str):
        s = screen_val.strip()
        if s.startswith("No screening, recommendation for reassessment in"):
            # Normalize to "Reassessment in N years"
            m = re.search(r"reassessment in\s+(\d+)\s+years", s, re.I)
            if m:
                screen_norm = f"Reassessment in {m.group(1)} years"
            else:
                screen_norm = "Reassessment"
        elif s.lower().startswith("fecal immunochemical test"):
            screen_norm = "FIT"
        elif s.lower().startswith("no screening"):
            screen_norm = "No screening"
        elif s.lower().startswith("colonoscopy"):
            screen_norm = "Colonoscopy"
        else:
            screen_norm = s

    # Clean additional info - preserve actual responses, only filter out truly empty ones
    if isinstance(addl_info, str):
        addl_info = addl_info.strip()
        # Only convert to None if completely empty
        if addl_info == '':
            addl_info = None
        # Keep "Na", "N/A", "None" as actual responses since they represent clinician input
    else:
        addl_info = None

    return risk_num, conf_num, screen_norm, addl_info


def parse_display_configuration(paths: Any) -> Dict[Tuple[str, str], Dict[str, Optional[str]]]:
    """
    Build a map {(category, feature) -> {"shown": bool, "value": str|None}} from display_configuration.
    Expected path examples:
      "BACKGROUND.Family History.Cancer: Yes"
      "BACKGROUND.Medical History.Constipation: No"
    """
    result: Dict[Tuple[str, str], Dict[str, Optional[str]]] = {}
    if not paths:
        return result
    try:
        # paths is typically a list of {path: str, style: {...}}
        for entry in paths:
            path = (entry or {}).get("path")
            if not path or not isinstance(path, str):
                continue
            # Only BACKGROUND.Family History.* or BACKGROUND.Medical History.*
            if not path.startswith("BACKGROUND."):
                continue
            # Split leaf value (": Yes"/": No")
            if ":" in path:
                left, right = path.split(":", 1)
                value = right.strip()
            else:
                left, value = path, None

            segments = [seg.strip() for seg in left.split(".")]
            if len(segments) < 3:
                continue
            # segments[1] is category (e.g., "Family History" or "Medical History")
            category = segments[1]
            feature = segments[2]
            key = (category, feature)

            cur = result.get(key, {"shown": False, "value": None})
            cur["shown"] = True
            if value in ("Yes", "No"):
                cur["value"] = value
            result[key] = cur
    except Exception:
        # be resilient to unexpected shapes
        return result
    return result


def parse_ai_score_value(obs_value_as_string: Optional[str], display_paths: Any) -> Optional[int]:
    """Extract a numeric AI score if present."""
    
    # 1) Try observation value, expecting "Colorectal Cancer Score: 7"
    if isinstance(obs_value_as_string, str):
        # Look for specific Colorectal Cancer Score pattern first
        m = re.search(r"Colorectal Cancer Score:\s*(\d+)", obs_value_as_string)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
        
        # Fallback to general score pattern
        m = re.search(r"Score:\s*(\d+)", obs_value_as_string)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass

    # 2) Try display_configuration entries e.g. "RISK ASSESSMENT.Colorectal Cancer Score: 8"
    if isinstance(display_paths, list):
        for entry in display_paths:
            path = (entry or {}).get("path")
            if isinstance(path, str):
                if "Colorectal Cancer Score" in path:
                    m = re.search(r"Colorectal Cancer Score:\s*(\d+)", path)
                    if m:
                        try:
                            return int(m.group(1))
                        except Exception:
                            pass
                
                # Also check for general RISK ASSESSMENT patterns
                if path.startswith("RISK ASSESSMENT") and "Score" in path:
                    m = re.search(r"Score:\s*(\d+)", path)
                    if m:
                        try:
                            return int(m.group(1))
                        except Exception:
                            pass
    return None


def get_all_patient_values(person_ids: List[int], engine) -> Dict[int, Dict[str, str]]:
    """
    Fetch actual patient values (Family History and Medical History) from observation table.
    Returns a dict mapping person_id -> {"Family History.Cancer": "Yes", ...}
    """
    if not person_ids:
        return {}
    
    print(f"Fetching patient values for {len(person_ids)} unique patients...")
    
    # Family History observations (concept_id = 4167217)
    sql_family = text("""
        SELECT 
            v.person_id,
            o.value_as_string
        FROM observation o
        JOIN visit_occurrence v ON v.visit_occurrence_id = o.visit_occurrence_id
        WHERE v.person_id = ANY(:person_ids)
        AND o.observation_concept_id = 4167217
        AND o.value_as_string IS NOT NULL
    """)
    
    # Medical History observations (concept_id = 1008364)
    sql_medical = text("""
        SELECT 
            v.person_id,
            o.value_as_string
        FROM observation o
        JOIN visit_occurrence v ON v.visit_occurrence_id = o.visit_occurrence_id
        WHERE v.person_id = ANY(:person_ids)
        AND o.observation_concept_id = 1008364
        AND o.value_as_string IS NOT NULL
    """)
    
    # Fetch both datasets
    df_family = pd.read_sql(sql_family, engine, params={"person_ids": person_ids})
    df_medical = pd.read_sql(sql_medical, engine, params={"person_ids": person_ids})
    
    # Initialize result dict
    result = {pid: {} for pid in person_ids}
    
    # Parse Family History values (format: "Cancer: Yes", "Diabetes: No")
    for _, row in df_family.iterrows():
        person_id = row["person_id"]
        value_str = row["value_as_string"]
        if ":" in value_str:
            feature, value = value_str.split(":", 1)
            feature = feature.strip()
            value = value.strip().capitalize()  # "Yes" or "No"
            if feature in ["Cancer", "Colorectal Cancer", "Diabetes", "Hypertension"]:
                result[person_id][f"Family History.{feature}"] = value
    
    # Parse Medical History values (format: "Asthma: Yes", "Diabetes: No")
    for _, row in df_medical.iterrows():
        person_id = row["person_id"]
        value_str = row["value_as_string"]
        if ":" in value_str:
            feature, value = value_str.split(":", 1)
            feature = feature.strip()
            value = value.strip().capitalize()  # "Yes" or "No"
            # Check if this feature is in our medical history list
            if feature in MEDICAL_HISTORY_FEATURES:
                result[person_id][f"Medical History.{feature}"] = value
    
    # Debug output
    patients_with_data = sum(1 for v in result.values() if len(v) > 0)
    print(f"Patient values found for {patients_with_data}/{len(person_ids)} patients.")
    
    return result


def get_all_ai_scores(person_ids: List[int], engine) -> Dict[int, Optional[int]]:
    """
    Fetch actual AI scores for all patients in batch for efficiency.
    Returns a dict mapping person_id -> ai_score (int or None)
    """
    if not person_ids:
        return {}
    
    print(f"Fetching AI scores for {len(person_ids)} unique patients...")
    
    sql = text("""
        SELECT 
            v.person_id,
            o.value_as_string, 
            o.value_as_number,
            ROW_NUMBER() OVER (PARTITION BY v.person_id ORDER BY o.observation_datetime DESC NULLS LAST) as rn
        FROM observation o
        JOIN visit_occurrence v ON v.visit_occurrence_id = o.visit_occurrence_id
        WHERE v.person_id = ANY(:person_ids)
        AND o.observation_concept_id = :ai_concept
        AND o.value_as_string ILIKE '%Colorectal Cancer Score:%'
    """)
    
    df = pd.read_sql(sql, engine, params={
        "person_ids": person_ids,
        "ai_concept": AI_OBS_CONCEPT_ID
    })
    
    # Filter to most recent observation per person
    df = df[df['rn'] == 1] if not df.empty else df
    
    result = {pid: None for pid in person_ids}
    
    for _, row in df.iterrows():
        person_id = row["person_id"]
        
        # Try numeric first
        if pd.notna(row["value_as_number"]):
            try:
                result[person_id] = int(row["value_as_number"])
                continue
            except:
                pass
        
        # Extract from string - specifically look for "Colorectal Cancer Score: X"
        if pd.notna(row["value_as_string"]):
            value_str = str(row["value_as_string"])
            # Look for the pattern "Colorectal Cancer Score: X"
            m = re.search(r"Colorectal Cancer Score:\s*(\d+)", value_str)
            if m:
                try:
                    result[person_id] = int(m.group(1))
                    continue
                except:
                    pass
            
            # Fallback to more general score pattern
            m = re.search(r"Score:\s*(\d+)", value_str)
            if m:
                try:
                    result[person_id] = int(m.group(1))
                except:
                    pass
    
    # Debug: Show some results
    found_scores = sum(1 for v in result.values() if v is not None)
    print(f"AI scores found for {found_scores}/{len(person_ids)} patients.")
    
    # Show a few examples for debugging
    examples = [(pid, score) for pid, score in result.items() if score is not None][:5]
    if examples:
        print("Example AI scores found:")
        for pid, score in examples:
            print(f"  Person {pid}: Score {score}")
    
    return result


def main():
    engine = create_engine(CONN_STR)
    
    print("Starting export process...")
    
    # Load recruitment survey data
    print("Step 0: Loading recruitment survey data...")
    recruitment_data = load_recruitment_survey_data()
    if recruitment_data is not None:
        print(f"Loaded {len(recruitment_data)} recruitment survey records")
    else:
        print("No recruitment survey data available - survey columns will be empty")
    
    print("Step 1: Fetching answer data...")

    # Pull all needed base fields with one query, including analytics timing data
    sql = text(f"""
        SELECT
            a.id,
            a.case_id,
            a.user_email,
            a.answer,
            a.display_configuration,
            a.ai_score_shown,
            v.person_id,
            v.visit_start_date,
            p.year_of_birth,
            g.concept_name AS gender_name,
            -- Try to grab one observation row for CRC risk concept id
            (
              SELECT o.value_as_string
              FROM observation o
              WHERE o.visit_occurrence_id = a.case_id
                AND o.observation_concept_id = :ai_concept
              ORDER BY o.observation_datetime NULLS LAST, o.observation_id DESC
              LIMIT 1
            ) AS ai_value_as_string,
            -- Add row number for order_id per user
            ROW_NUMBER() OVER (PARTITION BY a.user_email ORDER BY a.id ASC) as order_id,
            -- Analytics timing data from analytics table
            an.case_open_time,
            an.answer_open_time,
            an.answer_submit_time,
            an.to_answer_open_secs,
            an.to_submit_secs,
            an.total_duration_secs
        FROM answer a
        LEFT JOIN visit_occurrence v ON v.visit_occurrence_id = a.case_id
        LEFT JOIN person p ON p.person_id = v.person_id
        LEFT JOIN concept g ON g.concept_id = p.gender_concept_id
        LEFT JOIN analytics an ON an.user_email = a.user_email AND an.case_id = a.case_id
        ORDER BY a.user_email, a.id ASC
    """)

    df = pd.read_sql(sql, engine, params={"ai_concept": AI_OBS_CONCEPT_ID})
    print(f"Fetched {len(df)} answer records.")
    
    # Get unique person IDs for batch processing
    unique_person_ids = [int(pid) for pid in df["person_id"].dropna().unique()]
    print(f"Found {len(unique_person_ids)} unique patients.")
    
    # Batch fetch all patient values and AI scores
    print("Step 2: Fetching patient values from observation table...")
    all_patient_values = get_all_patient_values(unique_person_ids, engine)
    
    print("Step 3: Fetching AI scores...")
    all_ai_scores = get_all_ai_scores(unique_person_ids, engine)

    # Prepare output schema - all column names exactly as specified
    base_cols = [
        "person_id",
        "user_id", 
        "order_id",
    ]
    
    # Analytics timing columns (moved to early position)
    analytics_cols = [
        "case_open_time",
        "answer_open_time",
        "answer_submit_time",
        "to_answer_open_secs",
        "to_submit_secs",
        "total_duration_secs",
    ]
    
    # Demographics after timing
    demographics_cols = [
        "age",
        "gender",
    ]

    feature_shown_cols: List[str] = (
        [f"Family History.{f} (shown)" for f in FAMILY_HISTORY_FEATURES]
        + [f"Medical History.{f} (shown)" for f in MEDICAL_HISTORY_FEATURES]
        + ["ai_score (shown)"]
    )
    
    feature_value_cols: List[str] = (
        [f"Family History.{f} (value)" for f in FAMILY_HISTORY_FEATURES]
        + [f"Medical History.{f} (value)" for f in MEDICAL_HISTORY_FEATURES]
        + ["ai_score (value)"]
    )

    tail_cols = [
        "risk_assessment",
        "confidence_level",
        "screening_recommendation",
        "additional_info",
    ]
    
    # Recruitment survey columns (moved to end)
    recruitment_cols = [
        "professional_role",
        "professional_role_other", 
        "practice_years",
        "practice_state",
        "experience_screening",
        "years_screening",
    ]

    out_cols = base_cols + analytics_cols + demographics_cols + feature_shown_cols + feature_value_cols + tail_cols + recruitment_cols

    print("Step 4: Processing answer records...")
    rows: List[Dict[str, Any]] = []

    for i, (_, r) in enumerate(df.iterrows()):
        if i > 0 and i % 100 == 0:
            print(f"Processed {i}/{len(df)} records...")
            
        # Get OMOP person_id from database
        omop_person_id = int(r["person_id"]) if pd.notna(r["person_id"]) else None
        
        # Convert OMOP person_id back to source data.csv person_id
        # Formula: source_person_id = omop_person_id - PERSON_ID_OFFSET
        person_id = omop_person_id - PERSON_ID_OFFSET if omop_person_id else None
        
        case_id = int(r["case_id"]) if pd.notna(r["case_id"]) else None
        user_email = r.get("user_email") or ""
        user_id = stable_user_id(str(user_email))
        order_id = int(r["order_id"]) if pd.notna(r["order_id"]) else None

        # age
        age = None
        try:
            if pd.notna(r["visit_start_date"]) and pd.notna(r["year_of_birth"]):
                visit_year = pd.to_datetime(r["visit_start_date"]).year
                age = int(visit_year) - int(r["year_of_birth"])
        except Exception:
            age = None

        gender = r.get("gender_name")

        # parse display configuration for "(shown)" flags
        display_cfg = r.get("display_configuration")
        # The DB driver should return JSON -> dict/list; if it's a string, try to parse
        if isinstance(display_cfg, str):
            try:
                import json
                display_cfg = json.loads(display_cfg)
            except Exception:
                try:
                    import ast
                    display_cfg = ast.literal_eval(display_cfg)
                except Exception:
                    display_cfg = []

        shown_feature_map = parse_display_configuration(display_cfg)
        
        # Get actual patient values from observation table (fetched in batch earlier)
        # Note: Use omop_person_id to lookup in database, but export source person_id
        actual_values = all_patient_values.get(omop_person_id, {}) if omop_person_id else {}
        actual_ai_score = all_ai_scores.get(omop_person_id) if omop_person_id else None

        # Answer payload parsing
        answer_data = r.get("answer")
        risk_num, conf_num, screen_norm, addl_info = parse_answer_payload(answer_data)

        # AI score flags & value
        ai_shown = bool(r.get("ai_score_shown"))
        
        # For ai_score (value), prefer actual patient value, then try parsing from display
        ai_value = actual_ai_score
        if ai_value is None:
            ai_value = parse_ai_score_value(r.get("ai_value_as_string"), display_cfg)

        # Lookup recruitment survey data for this user
        recruitment_values = {}
        if recruitment_data is not None and user_email:
            user_email_normalized = user_email.strip().lower()
            matching_rows = recruitment_data[recruitment_data['email'] == user_email_normalized]
            if not matching_rows.empty:
                survey_row = matching_rows.iloc[0]  # Take first match
                recruitment_values = {
                    "professional_role": survey_row.get('professional_role', ''),
                    "professional_role_other": survey_row.get('professional_role_other', ''),
                    "practice_years": survey_row.get('practice_years', ''),
                    "practice_state": survey_row.get('practice_state', ''),
                    "experience_screening": survey_row.get('experience_screening', ''),
                    "years_screening": survey_row.get('years_screening', ''),
                }

        row: Dict[str, Any] = {
            "person_id": person_id,
            "user_id": user_id,
            "order_id": order_id,
        }
        
        # Extract timing data from analytics table (joined in main query)
        # Analytics data comes from the separate analytics table, not from answer JSON
        row["case_open_time"] = r.get("case_open_time") if pd.notna(r.get("case_open_time")) else ""
        row["answer_open_time"] = r.get("answer_open_time") if pd.notna(r.get("answer_open_time")) else ""
        row["answer_submit_time"] = r.get("answer_submit_time") if pd.notna(r.get("answer_submit_time")) else ""
        
        # Duration fields are pre-calculated in analytics table
        row["to_answer_open_secs"] = r.get("to_answer_open_secs") if pd.notna(r.get("to_answer_open_secs")) else ""
        row["to_submit_secs"] = r.get("to_submit_secs") if pd.notna(r.get("to_submit_secs")) else ""
        row["total_duration_secs"] = r.get("total_duration_secs") if pd.notna(r.get("total_duration_secs")) else ""
            
        # Add demographics
        row["age"] = age
        row["gender"] = gender
        
        # Add recruitment survey data
        for col in recruitment_cols:
            row[col] = recruitment_values.get(col, '')

        # Initialize all feature columns
        for feat in FAMILY_HISTORY_FEATURES:
            row[f"Family History.{feat} (shown)"] = False
            row[f"Family History.{feat} (value)"] = ""
        for feat in MEDICAL_HISTORY_FEATURES:
            row[f"Medical History.{feat} (shown)"] = False
            row[f"Medical History.{feat} (value)"] = ""

        # Fill "(shown)" flags from display configuration  
        for (cat, feat), vals in shown_feature_map.items():
            if cat == "Family History" and feat in FAMILY_HISTORY_FEATURES:
                row[f"Family History.{feat} (shown)"] = bool(vals.get("shown"))
            elif cat == "Medical History" and feat in MEDICAL_HISTORY_FEATURES:
                row[f"Medical History.{feat} (shown)"] = bool(vals.get("shown"))

        # Fill "(value)" fields with actual patient values from observation table
        # Note: We use empty string for missing data rather than assuming "No"
        # because absence of data doesn't necessarily mean the answer is "No"
        for feat in FAMILY_HISTORY_FEATURES:
            key = f"Family History.{feat}"
            if key in actual_values:
                row[f"Family History.{feat} (value)"] = actual_values[key]
            else:
                row[f"Family History.{feat} (value)"] = ""  # Empty if no data available
                
        for feat in MEDICAL_HISTORY_FEATURES:
            key = f"Medical History.{feat}"
            if key in actual_values:
                row[f"Medical History.{feat} (value)"] = actual_values[key]
            else:
                row[f"Medical History.{feat} (value)"] = ""  # Empty if no data available

        # AI score flags/value - note: using Yes/No for ai_score (shown) per requirements
        row["ai_score (shown)"] = "Yes" if ai_shown else "No"
        row["ai_score (value)"] = ai_value if ai_value is not None else ""

        # Tail fields
        row["risk_assessment"] = risk_num
        row["confidence_level"] = conf_num
        row["screening_recommendation"] = screen_norm
        row["additional_info"] = addl_info

        rows.append(row)

    print(f"Step 5: Creating CSV output...")
    out_df = pd.DataFrame(rows, columns=out_cols)
    
    # Order by person_id ascending
    out_df = out_df.sort_values('person_id', ascending=True)

    # Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"answers_data_{timestamp}.csv"

    out_df.to_csv(csv_filename, index=False)
    print(f"\n=== Export Complete ===")
    print(f"File: {csv_filename}")
    print(f"Records: {len(rows)} rows")
    print(f"Columns: {len(out_cols)}")
    print(f"Unique patients: {len(unique_person_ids)}")
    print(f"Unique users: {df['user_email'].nunique()}")


def debug_ai_scores():
    """
    Debug function to understand how AI scores are stored in the database.
    """
    engine = create_engine(CONN_STR)
    
    print("=== DEBUGGING AI SCORES ===")
    
    # 1. Check what AI-related concepts exist
    print("\n1. Checking AI-related concepts...")
    
    sql = text("""
        SELECT DISTINCT c.concept_id, c.concept_name, COUNT(*) as obs_count
        FROM concept c
        JOIN observation o ON o.observation_concept_id = c.concept_id
        WHERE LOWER(c.concept_name) LIKE '%ai%' 
           OR LOWER(c.concept_name) LIKE '%score%'
           OR LOWER(c.concept_name) LIKE '%risk%'
           OR LOWER(c.concept_name) LIKE '%assessment%'
        GROUP BY c.concept_id, c.concept_name
        ORDER BY obs_count DESC
        LIMIT 20
    """)
    
    try:
        df = pd.read_sql(sql, engine)
        print("AI/Score/Risk related concepts:")
        for _, row in df.iterrows():
            print(f"  ID {row['concept_id']}: {row['concept_name']} (Count: {row['obs_count']})")
    except Exception as e:
        print(f"Error fetching AI concepts: {e}")
    
    # 2. Check sample AI score observations
    print(f"\n2. Checking observations for concept ID {AI_OBS_CONCEPT_ID}...")
    
    sql = text("""
        SELECT 
            o.person_id,
            o.value_as_string,
            o.value_as_number,
            o.value_as_concept_id,
            vc.concept_name as value_concept_name
        FROM observation o
        LEFT JOIN concept vc ON vc.concept_id = o.value_as_concept_id
        WHERE o.observation_concept_id = :ai_concept
        LIMIT 10
    """)
    
    try:
        df = pd.read_sql(sql, engine, params={"ai_concept": AI_OBS_CONCEPT_ID})
        print(f"Sample observations for concept {AI_OBS_CONCEPT_ID}:")
        for _, row in df.iterrows():
            print(f"  Person {row['person_id']}: string='{row['value_as_string']}', number={row['value_as_number']}, concept='{row['value_concept_name']}'")
    except Exception as e:
        print(f"Error fetching AI observations: {e}")
    
    # 3. Check display_configuration for AI scores
    print("\n3. Checking display_configuration for AI score patterns...")
    
    sql = text("""
        SELECT display_configuration
        FROM answer 
        WHERE display_configuration IS NOT NULL
          AND CAST(display_configuration AS TEXT) ILIKE '%score%'
        LIMIT 5
    """)
    
    try:
        df = pd.read_sql(sql, engine)
        print("Sample display configurations with 'score':")
        for i, row in df.iterrows():
            config = row['display_configuration']
            if isinstance(config, str):
                try:
                    import json
                    config = json.loads(config)
                except:
                    try:
                        import ast
                        config = ast.literal_eval(config)
                    except:
                        pass
            
            if isinstance(config, list):
                print(f"\nConfig {i+1}:")
                for entry in config:
                    path = entry.get('path', 'No path')
                    if 'score' in path.lower() or 'risk' in path.lower():
                        print(f"  - {path}")
    except Exception as e:
        print(f"Error checking display configurations for scores: {e}")
    
    # 4. Check if AI scores might be stored differently
    print("\n4. Checking other tables for AI scores...")
    
    # Check if there's a separate AI score field in answer table
    sql = text("""
        SELECT 
            ai_score_shown,
            answer,
            display_configuration
        FROM answer 
        WHERE ai_score_shown = true
        LIMIT 3
    """)
    
    try:
        df = pd.read_sql(sql, engine)
        print("Sample answers where AI score was shown:")
        for i, row in df.iterrows():
            print(f"\nAnswer {i+1}:")
            print(f"  AI Score Shown: {row['ai_score_shown']}")
            
            # Check if there's a score in the answer JSON
            answer = row['answer']
            if isinstance(answer, str):
                try:
                    import json
                    answer = json.loads(answer)
                except:
                    try:
                        import ast
                        answer = ast.literal_eval(answer)
                    except:
                        pass
            
            if isinstance(answer, dict):
                for key, value in answer.items():
                    if 'score' in key.lower() or 'risk' in key.lower():
                        print(f"  Answer contains: {key} = {value}")
            
            # Check display_configuration for scores
            config = row['display_configuration']
            if isinstance(config, str):
                try:
                    import json
                    config = json.loads(config)
                except:
                    try:
                        import ast
                        config = ast.literal_eval(config)
                    except:
                        pass
            
            if isinstance(config, list):
                for entry in config:
                    path = entry.get('path', '')
                    if 'score' in path.lower() and 'RISK' in path:
                        print(f"  Display config: {path}")
    except Exception as e:
        print(f"Error checking answer table for AI scores: {e}")


def test_column_structure():
    """
    Test function to validate the expected column structure.
    """
    base_cols = [
        "person_id",
        "user_id", 
        "order_id",
        "age",
        "gender",
    ]

    feature_shown_cols = (
        [f"Family History.{f} (shown)" for f in FAMILY_HISTORY_FEATURES]
        + [f"Medical History.{f} (shown)" for f in MEDICAL_HISTORY_FEATURES]
        + ["ai_score (shown)"]
    )
    
    feature_value_cols = (
        [f"Family History.{f} (value)" for f in FAMILY_HISTORY_FEATURES]
        + [f"Medical History.{f} (value)" for f in MEDICAL_HISTORY_FEATURES]
        + ["ai_score (value)"]
    )

    tail_cols = [
        "risk_assessment",
        "confidence_level",
        "screening_recommendation",
        "additional_info",
    ]

    all_cols = base_cols + feature_shown_cols + feature_value_cols + tail_cols
    
    print(f"Total columns: {len(all_cols)}")
    print("\nExpected column structure:")
    for i, col in enumerate(all_cols, 1):
        print(f"{i:2d}. {col}")
    
    # Test parsing functions
    sample_display_config = [
        {"path": "BACKGROUND.Family History.Cancer: Yes", "style": {"highlight": True}},
        {"path": "BACKGROUND.Medical History.Diabetes: No", "style": {"highlight": True}},
    ]
    
    parsed = parse_display_configuration(sample_display_config)
    print(f"\nTest display configuration parsing: {parsed}")
    
    sample_answer = {
        "How would you assess this patient's risk for colorectal cancer?\u2009": "Moderate risk",
        "On a scale from 1 to 5, how confident are you in your screening recommendation for this patient?\u2009": "3 - Fairly confident",
    }
    
    risk, conf, screen, info = parse_answer_payload(sample_answer)
    print(f"Test answer parsing: risk={risk}, confidence={conf}, screening={screen}")
    
    return True


def investigate_case_assignment():
    """Investigate why person_id starts at 84 instead of 1."""
    engine = create_engine(CONN_STR)
    
    print("🔍 CASE ASSIGNMENT INVESTIGATION")
    print("=" * 50)
    
    # Check total persons vs assigned cases
    sql = text("""
        SELECT 
            'Total Persons' as category,
            MIN(person_id) as min_id,
            MAX(person_id) as max_id,
            COUNT(*) as count
        FROM person
        
        UNION ALL
        
        SELECT 
            'Assigned Cases' as category,
            MIN(v.person_id) as min_id,
            MAX(v.person_id) as max_id,
            COUNT(*) as count
        FROM visit_occurrence v
        JOIN answer a ON a.case_id = v.visit_occurrence_id
        
        UNION ALL
        
        SELECT 
            'All Visit Occurrences' as category,
            MIN(person_id) as min_id,
            MAX(person_id) as max_id,
            COUNT(*) as count
        FROM visit_occurrence
    """)
    
    df = pd.read_sql(sql, engine)
    for _, row in df.iterrows():
        print(f"{row['category']}: {row['min_id']} to {row['max_id']} ({row['count']} records)")
    
    # Check if persons 1-83 have visit_occurrences but no answers
    sql = text("""
        SELECT 
            CASE 
                WHEN v.person_id IS NULL THEN 'No visit_occurrence'
                WHEN a.case_id IS NULL THEN 'Has visit but no answers'
                ELSE 'Has answers'
            END as status,
            COUNT(*) as count
        FROM person p
        LEFT JOIN visit_occurrence v ON v.person_id = p.person_id
        LEFT JOIN answer a ON a.case_id = v.visit_occurrence_id
        WHERE p.person_id BETWEEN 1 AND 100
        GROUP BY 1
        ORDER BY 1
    """)
    
    df = pd.read_sql(sql, engine)
    print("\nStatus of persons 1-100:")
    for _, row in df.iterrows():
        print(f"  {row['status']}: {row['count']} persons")


def analyze_case_overlap():
    """Analyze how cases overlap between participants and participant completion rates."""
    engine = create_engine(CONN_STR)
    
    print("\n" + "=" * 60)
    print("📊 CASE OVERLAP & PARTICIPANT ANALYSIS")
    print("=" * 60)
    
    # Check how many participants answered each case
    sql = text("""
        SELECT 
            a.case_id,
            v.person_id,
            COUNT(DISTINCT a.user_email) as participant_count,
            COUNT(*) as total_answers,
            STRING_AGG(DISTINCT SUBSTRING(a.user_email, 1, 15), ', ') as sample_users
        FROM answer a
        JOIN visit_occurrence v ON v.visit_occurrence_id = a.case_id
        GROUP BY a.case_id, v.person_id
        ORDER BY participant_count DESC, a.case_id
        LIMIT 15
    """)
    
    df = pd.read_sql(sql, engine)
    print("🔄 Cases with Multiple Participants (Top 15):")
    print("-" * 50)
    for _, row in df.iterrows():
        print(f"  Case {row['case_id']} (Person {row['person_id']}): {row['participant_count']} participants")
        print(f"    └─ Total answers: {row['total_answers']}, Sample users: {row['sample_users']}")
    
    # Overall overlap statistics
    sql = text("""
        SELECT 
            COUNT(DISTINCT a.case_id) as unique_cases,
            COUNT(DISTINCT a.user_email) as active_participants,
            COUNT(*) as total_responses,
            ROUND(AVG(participant_counts.participants_per_case), 2) as avg_participants_per_case,
            MAX(participant_counts.participants_per_case) as max_participants_per_case
        FROM answer a
        JOIN (
            SELECT case_id, COUNT(DISTINCT user_email) as participants_per_case
            FROM answer 
            GROUP BY case_id
        ) participant_counts ON participant_counts.case_id = a.case_id
    """)
    
    df = pd.read_sql(sql, engine)
    stats = df.iloc[0]
    print(f"\n📈 OVERLAP STATISTICS:")
    print("-" * 30)
    print(f"  Unique cases answered: {stats['unique_cases']}")
    print(f"  Active participants: {stats['active_participants']}")
    print(f"  Total responses: {stats['total_responses']}")
    print(f"  Avg participants per case: {stats['avg_participants_per_case']}")
    print(f"  Max participants per case: {stats['max_participants_per_case']}")
    
    # Check participant completion status
    sql = text("""
        SELECT 
            user_email,
            COUNT(*) as cases_completed,
            MIN(case_id) as first_case,
            MAX(case_id) as last_case
        FROM answer
        GROUP BY user_email
        ORDER BY cases_completed DESC
    """)
    
    df = pd.read_sql(sql, engine)
    print(f"\n👥 PARTICIPANT COMPLETION STATUS:")
    print("-" * 40)
    print(f"  Active participants: {len(df)}")
    print(f"  Average cases completed: {df['cases_completed'].mean():.1f}")
    print(f"  Median cases completed: {df['cases_completed'].median():.1f}")
    print(f"  Max cases completed: {df['cases_completed'].max()}")
    print(f"  Min cases completed: {df['cases_completed'].min()}")
    
    # Expected vs actual progress
    expected_total = 224 * 100  # 224 participants × 100 cases each
    actual_total = stats['total_responses']
    completion_rate = (actual_total / expected_total) * 100
    
    print(f"\n🎯 STUDY PROGRESS:")
    print("-" * 20)
    print(f"  Expected total responses: {expected_total:,}")
    print(f"  Actual responses: {actual_total:,}")
    print(f"  Overall completion rate: {completion_rate:.1f}%")
    
    # Show top participants
    print(f"\n🏆 Top 10 Most Active Participants:")
    print("-" * 40)
    for i, row in enumerate(df.head(10).iterrows(), 1):
        _, data = row
        email_preview = data['user_email'][:20] + "..."
        print(f"  {i:2d}. {email_preview}: {data['cases_completed']} cases")
    
    return df


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_column_structure()
    elif len(sys.argv) > 1 and sys.argv[1] == "--investigate":
        investigate_case_assignment()
    elif len(sys.argv) > 1 and sys.argv[1] == "--overlap":
        analyze_case_overlap()
    elif len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        investigate_case_assignment()
        analyze_case_overlap()
    else:
        main()
