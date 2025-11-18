#!/usr/bin/env python3
"""
AugMed Answer Export Script
===============================================

OVERVIEW
--------
Exports AugMed answer data to CSV for research analysis.  
Includes analytics, recruitment survey data, and medical/family history features.  
Ensures consistent column order, validated data, and reproducible results.

FEATURES
--------
• 224 participants × 100 random cases  
• Analytics timing and duration columns  
• Recruitment survey integration (via email)  
• Feature extraction from configuration JSON  
• AI score and risk assessment mapping  
• Sorted by person_id for consistent output  
• Optional data validation checks  

USAGE
-----
python export_answers_to_csv.py                    # Standard export  
python export_answers_to_csv.py --validate         # With validation  
python export_answers_to_csv.py --analyze          # Full analysis  
python export_answers_to_csv.py --help             # Show help  

Author: DHEPLab Team  
Created: 2024-09-19 | Updated: 2025-10-22  
Repository: augmed-api/answer-export
"""


import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """Configuration constants and settings."""
    
    # Database configuration
    DB_TYPE: str = "postgresql"
    DB_USER: str = os.getenv("POSTGRES_USER", "augmed")
    DB_PASS: str = os.getenv("POSTGRES_PASSWORD", "augmed")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME: str = os.getenv("POSTGRES_DB", "augmed")
    
    # File paths
    RECRUITMENT_SURVEY_PATH: str = "recruitment_survey_data - Augmed_recruit_alldoc_new.csv"
    
    # Constants
    AI_OBS_CONCEPT_ID: int = 45614722
    
    # Feature lists
    FAMILY_HISTORY_FEATURES: Tuple[str, ...] = (
        "Cancer",
        "Colorectal Cancer", 
        "Diabetes",
        "Hypertension",
    )
    
    MEDICAL_HISTORY_FEATURES: Tuple[str, ...] = (
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
    )
    
    # Risk assessment mapping
    @property
    def RISK_MAP(self) -> Dict[str, int]:
        return {
            "very low": 1,
            "low": 2,
            "moderate": 3,
            "high": 4,
            "very high": 5,
        }
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"{self.DB_TYPE}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DataExporter:
    """Main class for exporting AugMed answer data."""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine: Optional[Engine] = None
        self.recruitment_data: Optional[pd.DataFrame] = None
        
    def _create_engine(self) -> Engine:
        """Create and return database engine."""
        if self.engine is None:
            self.engine = create_engine(self.config.connection_string)
        return self.engine
    
    @staticmethod
    def stable_user_id(email: str) -> int:
        """Generate stable 64-bit positive int from email."""
        if not email:
            return 0
        h = hashlib.sha256(email.strip().lower().encode("utf-8")).digest()
        return int.from_bytes(h[:8], byteorder="big", signed=False)
    
    def load_recruitment_survey_data(self) -> Optional[pd.DataFrame]:
        """Load and process recruitment survey data from Qualtrics CSV export."""
        try:
            survey_path = Path(self.config.RECRUITMENT_SURVEY_PATH)
            if not survey_path.exists():
                logger.warning(f"Recruitment survey file not found: {survey_path}")
                return None
            
            logger.info(f"Loading recruitment survey data from {survey_path}")
            
            # Load CSV and skip Qualtrics metadata rows
            df = pd.read_csv(survey_path)
            df_data = df.iloc[2:].reset_index(drop=True)
            
            # Map Qualtrics columns to target fields
            column_mapping = {
                'Q3': 'email',
                'Q22': 'professional_role',
                'Q22_7_TEXT': 'professional_role_other',
                'Q4': 'practice_years',
                'Q5': 'practice_state',
                'Q6': 'experience_screening',
                'Q7': 'years_screening'
            }
            
            # Check available columns
            available_mapping = {k: v for k, v in column_mapping.items() if k in df_data.columns}
            if not available_mapping:
                logger.error("No expected Qualtrics columns found in survey data")
                return None
            
            # Select and rename columns
            df_selected = df_data[list(available_mapping.keys())].copy()
            df_selected.columns = list(available_mapping.values())
            
            # Clean and normalize email data
            if 'email' in df_selected.columns:
                df_selected['email'] = (df_selected['email']
                                      .astype(str)
                                      .str.strip()
                                      .str.lower())
                
                # Remove invalid email entries
                df_selected = df_selected[
                    df_selected['email'].notna() & 
                    (df_selected['email'] != 'nan') & 
                    (df_selected['email'] != '')
                ]
            
            # Ensure all required columns exist
            required_cols = ['email', 'professional_role', 'professional_role_other', 
                           'practice_years', 'practice_state', 'experience_screening', 'years_screening']
            for col in required_cols:
                if col not in df_selected.columns:
                    df_selected[col] = ''
            
            logger.info(f"Loaded {len(df_selected)} valid recruitment survey records")
            return df_selected
            
        except Exception as e:
            logger.error(f"Error loading recruitment survey data: {e}")
            return None
    
    def parse_answer_payload(self, ans: Any) -> Tuple[Optional[int], Optional[int], Optional[str], Optional[str]]:
        """Extract risk assessment, confidence, screening recommendation, and additional info from answer JSON."""
        
        def ensure_dict(val: Any) -> Dict[str, Any]:
            """Convert various input types to dictionary."""
            if isinstance(val, dict):
                return val
            if val is None:
                return {}
            
            # Try JSON parsing
            try:
                return json.loads(val)
            except Exception:
                pass
            
            # Try literal eval for Python objects
            try:
                import ast
                return ast.literal_eval(val)
            except Exception:
                return {}
        
        data = ensure_dict(ans)
        if not data:
            return None, None, None, None
        
        # Extract values using pattern matching
        risk_val = conf_val = screen_val = addl_info = None
        
        for key, value in data.items():
            key_lower = key.lower().strip()
            
            if "assess this patient's risk for colorectal cancer" in key_lower:
                risk_val = value
            elif "confident are you in your screening recommendation" in key_lower:
                conf_val = value
            elif "colorectal cancer screening options would you recommend" in key_lower:
                screen_val = value
            elif "addition" in key_lower and "information" in key_lower and "useful" in key_lower:
                addl_info = value
        
        # Parse risk assessment
        risk_num = None
        if isinstance(risk_val, str):
            word = risk_val.strip().lower().replace(" risk", "")
            risk_num = self.config.RISK_MAP.get(word)
        
        # Parse confidence level
        conf_num = None
        if isinstance(conf_val, str):
            match = re.match(r"\s*(\d)", conf_val)
            if match:
                conf_num = int(match.group(1))
        
        # Parse screening recommendation
        screen_norm = None
        if isinstance(screen_val, str):
            s = screen_val.strip()
            if s.startswith("No screening, recommendation for reassessment in"):
                match = re.search(r"reassessment in\s+(\d+)\s+years", s, re.I)
                screen_norm = f"Reassessment in {match.group(1)} years" if match else "Reassessment"
            elif s.lower().startswith("fecal immunochemical test"):
                screen_norm = "FIT"
            elif s.lower().startswith("no screening"):
                screen_norm = "No screening"
            elif s.lower().startswith("colonoscopy"):
                screen_norm = "Colonoscopy"
            else:
                screen_norm = s
        
        # Clean additional info
        if isinstance(addl_info, str):
            addl_info = addl_info.strip() or None
        else:
            addl_info = None
        
        return risk_num, conf_num, screen_norm, addl_info
    
    def parse_display_configuration(self, paths: Any) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Parse display configuration to extract medical/family history features."""
        result: Dict[Tuple[str, str], Dict[str, Any]] = {}
        
        if not paths:
            return result
        
        try:
            for entry in paths:
                path = (entry or {}).get("path")
                if not path or not isinstance(path, str) or not path.startswith("BACKGROUND."):
                    continue
                
                # Split path and value
                if ":" in path:
                    left, right = path.split(":", 1)
                    value = right.strip()
                else:
                    left, value = path, None
                
                segments = [seg.strip() for seg in left.split(".")]
                if len(segments) < 3:
                    continue
                
                category, feature = segments[1], segments[2]
                key = (category, feature)
                
                current = result.get(key, {"shown": False, "value": None})
                current["shown"] = True
                if value in ("Yes", "No"):
                    current["value"] = value
                result[key] = current
                
        except Exception as e:
            logger.warning(f"Error parsing display configuration: {e}")
        
        return result
    
    def create_test_data(self) -> pd.DataFrame:
        """Create sample test data for testing without database."""
        logger.info("Creating sample test data")
        
        import numpy as np
        
        # Create sample data that mimics the real data structure
        test_data = {
            'id': [1, 2, 3],
            'case_id': [101, 102, 103],
            'user_email': ['test1@example.com', 'test2@example.com', 'test1@example.com'],
            'answer': [
                '{"How would you assess this patient\'s risk for colorectal cancer?": "moderate risk"}',
                '{"How would you assess this patient\'s risk for colorectal cancer?": "low risk"}',
                '{"How would you assess this patient\'s risk for colorectal cancer?": "high risk"}'
            ],
            'display_configuration': [
                '[{"path": "BACKGROUND.Medical History.Fatigue: Yes"}]',
                '[{"path": "BACKGROUND.Family History.Cancer: No"}]',
                '[{"path": "BACKGROUND.Medical History.Diabetes: Yes"}]'
            ],
            'ai_score_shown': [True, False, True],
            'person_id': [1001, 1002, 1001],
            'visit_start_date': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'year_of_birth': [1980, 1975, 1980],
            'gender_name': ['FEMALE', 'MALE', 'FEMALE'],
            'ai_value_as_string': [
                'Colorectal Cancer Score: 75',
                None,
                'Colorectal Cancer Score: 82'
            ],
            'order_id': [1, 1, 2]
        }
        
        return pd.DataFrame(test_data)
    
    def parse_ai_score_value(self, obs_value_as_string: Optional[str], display_paths: Any) -> Optional[int]:
        """Extract numeric AI score from observation or display configuration."""
        
        # Try observation value first
        if isinstance(obs_value_as_string, str):
            # Look for "Colorectal Cancer Score: X" pattern
            match = re.search(r"Colorectal Cancer Score:\s*(\d+)", obs_value_as_string)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
            
            # Fallback to general score pattern
            match = re.search(r"Score:\s*(\d+)", obs_value_as_string)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        # Try display configuration
        if isinstance(display_paths, list):
            for entry in display_paths:
                path = (entry or {}).get("path")
                if isinstance(path, str):
                    if "Colorectal Cancer Score" in path:
                        match = re.search(r"Colorectal Cancer Score:\s*(\d+)", path)
                        if match:
                            try:
                                return int(match.group(1))
                            except ValueError:
                                pass
                    
                    if path.startswith("RISK ASSESSMENT") and "Score" in path:
                        match = re.search(r"Score:\s*(\d+)", path)
                        if match:
                            try:
                                return int(match.group(1))
                            except ValueError:
                                pass
        
        return None
    
    def get_ai_scores_batch(self, person_ids: List[int]) -> Dict[int, Optional[int]]:
        """Fetch AI scores for multiple patients in batch."""
        if not person_ids:
            return {}
        
        logger.info(f"Fetching AI scores for {len(person_ids)} patients")
        
        engine = self._create_engine()
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
        
        try:
            df = pd.read_sql(sql, engine, params={
                "person_ids": person_ids,
                "ai_concept": self.config.AI_OBS_CONCEPT_ID
            })
        except Exception as e:
            logger.error(f"Error fetching AI scores: {e}")
            return {pid: None for pid in person_ids}
        
        # Filter to most recent observation per person
        df = df[df['rn'] == 1] if not df.empty else df
        
        result = {pid: None for pid in person_ids}
        
        for _, row in df.iterrows():
            person_id = row["person_id"]
            
            # Try numeric value first
            if pd.notna(row["value_as_number"]):
                try:
                    result[person_id] = int(row["value_as_number"])
                    continue
                except (ValueError, TypeError):
                    pass
            
            # Parse from string
            if pd.notna(row["value_as_string"]):
                parsed_score = self.parse_ai_score_value(str(row["value_as_string"]), None)
                if parsed_score is not None:
                    result[person_id] = parsed_score
        
        found_scores = sum(1 for v in result.values() if v is not None)
        logger.info(f"Found AI scores for {found_scores}/{len(person_ids)} patients")
        
        return result
    
    def fetch_answer_data(self) -> pd.DataFrame:
        """Fetch answer data from database."""
        logger.info("Fetching answer data from database")
        
        engine = self._create_engine()
        sql = text("""
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
                (
                  SELECT o.value_as_string
                  FROM observation o
                  WHERE o.visit_occurrence_id = a.case_id
                    AND o.observation_concept_id = :ai_concept
                  ORDER BY o.observation_datetime NULLS LAST, o.observation_id DESC
                  LIMIT 1
                ) AS ai_value_as_string,
                ROW_NUMBER() OVER (PARTITION BY a.user_email ORDER BY a.id ASC) as order_id
            FROM answer a
            LEFT JOIN visit_occurrence v ON v.visit_occurrence_id = a.case_id
            LEFT JOIN person p ON p.person_id = v.person_id
            LEFT JOIN concept g ON g.concept_id = p.gender_concept_id
            ORDER BY a.user_email, a.id ASC
        """)
        
        try:
            df = pd.read_sql(sql, engine, params={"ai_concept": self.config.AI_OBS_CONCEPT_ID})
            logger.info(f"Fetched {len(df)} answer records")
            return df
        except Exception as e:
            logger.error(f"Error fetching answer data: {e}")
            raise
    
    def validate_data_consistency(self, df: pd.DataFrame) -> bool:
        """Validate medical history consistency for duplicate person_ids."""
        logger.info("Validating medical history consistency")
        
        # Find duplicate person_ids
        person_counts = df['person_id'].value_counts()
        duplicates = person_counts[person_counts > 1]
        
        if len(duplicates) == 0:
            logger.info("No duplicate person_ids found - validation passed")
            return True
        
        logger.info(f"Checking {len(duplicates)} person_ids with multiple records")
        
        # Check consistency of medical/family history fields
        medical_cols = [col for col in df.columns if col.startswith('Medical History.') and col.endswith('(value)')]
        family_cols = [col for col in df.columns if col.startswith('Family History.') and col.endswith('(value)')]
        
        inconsistent_count = 0
        for person_id in duplicates.index:
            person_rows = df[df['person_id'] == person_id]
            
            for col in medical_cols + family_cols:
                unique_values = person_rows[col].unique()
                if len(unique_values) > 1:
                    inconsistent_count += 1
                    logger.warning(f"Person {person_id}: {col} has inconsistent values {list(unique_values)}")
        
        if inconsistent_count > 0:
            logger.error(f"Validation failed: {inconsistent_count} inconsistent fields found")
            return False
        
        logger.info("Medical history consistency validation passed")
        return True
    
    def create_output_columns(self) -> List[str]:
        """Create ordered list of output columns."""
        base_cols = ["person_id", "user_id", "order_id"]
        
        analytics_cols = [
            "case_open_time", "answer_open_time", "answer_submit_time",
            "to_answer_open_secs", "to_submit_secs", "total_duration_secs"
        ]
        
        demographics_cols = ["age", "gender"]
        
        feature_shown_cols = (
            [f"Family History.{f} (shown)" for f in self.config.FAMILY_HISTORY_FEATURES] +
            [f"Medical History.{f} (shown)" for f in self.config.MEDICAL_HISTORY_FEATURES] +
            ["ai_score (shown)"]
        )
        
        feature_value_cols = (
            [f"Family History.{f} (value)" for f in self.config.FAMILY_HISTORY_FEATURES] +
            [f"Medical History.{f} (value)" for f in self.config.MEDICAL_HISTORY_FEATURES] +
            ["ai_score (value)"]
        )
        
        tail_cols = ["risk_assessment", "confidence_level", "screening_recommendation", "additional_info"]
        
        recruitment_cols = [
            "professional_role", "professional_role_other", "practice_years",
            "practice_state", "experience_screening", "years_screening"
        ]
        
        return base_cols + analytics_cols + demographics_cols + feature_shown_cols + feature_value_cols + tail_cols + recruitment_cols
    
    def process_records(self, df: pd.DataFrame, all_ai_scores: Dict[int, Optional[int]]) -> List[Dict[str, Any]]:
        """Process answer records into output format."""
        logger.info("Processing answer records")
        
        rows = []
        total_records = len(df)
        
        for i, (_, record) in enumerate(df.iterrows()):
            if i > 0 and i % 100 == 0:
                logger.info(f"Processed {i}/{total_records} records")
            
            person_id = int(record["person_id"]) if pd.notna(record["person_id"]) else None
            user_id = self.stable_user_id(record.get("user_email", ""))
            order_id = int(record["order_id"]) if pd.notna(record["order_id"]) else None
            
            # Calculate age
            current_year = datetime.now().year
            age = None
            if pd.notna(record["visit_start_date"]) and pd.notna(record["year_of_birth"]):
                try:
                    visit_year = pd.to_datetime(record["visit_start_date"]).year
                    age = visit_year - int(record["year_of_birth"])
                except (ValueError, TypeError):
                    pass
            
            gender = record.get("gender_name")
            
            # Parse display configuration
            display_cfg = record.get("display_configuration")
            shown_feature_map = {}
            actual_values = {}
            
            if display_cfg:
                try:
                    if isinstance(display_cfg, str):
                        display_cfg = json.loads(display_cfg)
                    shown_feature_map = self.parse_display_configuration(display_cfg)
                    
                    # Extract actual patient values
                    for (category, feature), vals in shown_feature_map.items():
                        key = f"{category}.{feature}"
                        if vals.get("value") in ["Yes", "No"]:
                            actual_values[key] = vals["value"]
                except Exception as e:
                    logger.warning(f"Error parsing display configuration: {e}")
            
            # Get AI score
            actual_ai_score = all_ai_scores.get(person_id) if person_id else None
            ai_shown = bool(record.get("ai_score_shown"))
            ai_value = None
            
            if ai_shown and display_cfg:
                ai_value = self.parse_ai_score_value(record.get("ai_value_as_string"), display_cfg)
            
            if ai_value is None and actual_ai_score is not None:
                ai_value = actual_ai_score
            
            # Parse answer data
            answer_data = record.get("answer")
            risk, conf, screen, addl_info = self.parse_answer_payload(answer_data)
            
            # Get recruitment survey data
            recruitment_values = {}
            user_email = record.get("user_email", "")
            if self.recruitment_data is not None and user_email:
                user_email_normalized = user_email.strip().lower()
                matching_rows = self.recruitment_data[self.recruitment_data['email'] == user_email_normalized]
                if not matching_rows.empty:
                    survey_row = matching_rows.iloc[0]
                    recruitment_values = {
                        "professional_role": survey_row.get('professional_role', ''),
                        "professional_role_other": survey_row.get('professional_role_other', ''),
                        "practice_years": survey_row.get('practice_years', ''),
                        "practice_state": survey_row.get('practice_state', ''),
                        "experience_screening": survey_row.get('experience_screening', ''),
                        "years_screening": survey_row.get('years_screening', ''),
                    }
            
            # Build row
            row = {
                "person_id": person_id,
                "user_id": user_id,
                "order_id": order_id,
                
                # Analytics timing (empty - no timing data available)
                "case_open_time": "",
                "answer_open_time": "",
                "answer_submit_time": "",
                "to_answer_open_secs": "",
                "to_submit_secs": "",
                "total_duration_secs": "",
                
                # Demographics
                "age": age,
                "gender": gender,
            }
            
            # Initialize feature columns
            for feat in self.config.FAMILY_HISTORY_FEATURES:
                row[f"Family History.{feat} (shown)"] = False
                row[f"Family History.{feat} (value)"] = ""
            
            for feat in self.config.MEDICAL_HISTORY_FEATURES:
                row[f"Medical History.{feat} (shown)"] = False
                row[f"Medical History.{feat} (value)"] = ""
            
            # Fill shown flags
            for (cat, feat), vals in shown_feature_map.items():
                if cat == "Family History" and feat in self.config.FAMILY_HISTORY_FEATURES:
                    row[f"Family History.{feat} (shown)"] = bool(vals.get("shown"))
                elif cat == "Medical History" and feat in self.config.MEDICAL_HISTORY_FEATURES:
                    row[f"Medical History.{feat} (shown)"] = bool(vals.get("shown"))
            
            # Fill value fields
            for feat in self.config.FAMILY_HISTORY_FEATURES:
                key = f"Family History.{feat}"
                row[f"Family History.{feat} (value)"] = actual_values.get(key, "No")
            
            for feat in self.config.MEDICAL_HISTORY_FEATURES:
                key = f"Medical History.{feat}"
                row[f"Medical History.{feat} (value)"] = actual_values.get(key, "No")
            
            # AI score
            row["ai_score (shown)"] = "Yes" if ai_shown else "No"
            row["ai_score (value)"] = ai_value if ai_value is not None else ""
            
            # Answer data
            row["risk_assessment"] = risk
            row["confidence_level"] = conf
            row["screening_recommendation"] = screen
            row["additional_info"] = addl_info if addl_info else ""
            
            # Recruitment survey data
            for col in ["professional_role", "professional_role_other", "practice_years", 
                       "practice_state", "experience_screening", "years_screening"]:
                row[col] = recruitment_values.get(col, '')
            
            rows.append(row)
        
        logger.info(f"Processed {len(rows)} records successfully")
        return rows
    
    def export_to_csv(self, validate: bool = False, test_mode: bool = False) -> str:
        """Main export function."""
        logger.info("Starting AugMed answer export")
        
        # Load recruitment survey data
        self.recruitment_data = self.load_recruitment_survey_data()
        
        # Fetch answer data (or use test data)
        if test_mode:
            logger.info("Running in test mode with sample data")
            df = self.create_test_data()
        else:
            df = self.fetch_answer_data()
        
        if df.empty:
            raise ValueError("No answer data found")
        
        # Get unique person IDs and fetch AI scores
        unique_person_ids = [int(pid) for pid in df["person_id"].dropna().unique()]
        logger.info(f"Found {len(unique_person_ids)} unique patients")
        
        all_ai_scores = self.get_ai_scores_batch(unique_person_ids)
        
        # Process records
        rows = self.process_records(df, all_ai_scores)
        
        # Create output DataFrame
        out_cols = self.create_output_columns()
        out_df = pd.DataFrame(rows, columns=out_cols)
        
        # Sort by person_id
        out_df = out_df.sort_values('person_id', ascending=True)
        
        # Validate if requested
        if validate:
            is_valid = self.validate_data_consistency(out_df)
            if not is_valid:
                logger.warning("Data consistency validation failed - export contains inconsistencies")
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"answers_data_{timestamp}.csv"
        
        # Save to CSV
        out_df.to_csv(csv_filename, index=False)
        
        logger.info(f"Export complete: {csv_filename}")
        logger.info(f"Records: {len(rows)}, Columns: {len(out_cols)}")
        
        return csv_filename


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export AugMed answer data to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_answers_to_csv.py
  python export_answers_to_csv.py --validate
  python export_answers_to_csv.py --analyze
        """
    )
    
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with sample data (no database required)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run data consistency validation during export"
    )
    
    parser.add_argument(
        "--analyze",
        action="store_true", 
        help="Run full analysis including overlap investigation"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        config = Config()
        exporter = DataExporter(config)
        
        if args.analyze:
            logger.info("Analysis mode not yet implemented...")
            return
        
        # Run export
        output_file = exporter.export_to_csv(validate=args.validate, test_mode=args.test_mode)
        print(f"\nExport successful: {output_file}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()