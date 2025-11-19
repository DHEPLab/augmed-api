#!/usr/bin/env bash

# ---------------------------------------------------------------------------------------------------------------
# generate_round3_test_config.sh
#
# Generate Round 3 TEST configuration for 4 test users with the following specs:
# - 10 cases per user randomly selected from valid person_ids
# - Always shown: Age, Gender
# - Random 50%: All Medical History, Family History fields, BMI, CRC_SCORE
# - Never shown (0%): CRC_RISK (low/med/high/adjusted)
#
# Test users:
#   - lirjiao@unc.edu
#   - test@unc.edu
#   - sean.sylvia@unc.edu
#   - srfort@live.unc.edu
#
# Usage:
#   ./generate_round3_test_config.sh <db_host> <db_port> <db_name> <db_user>
#
# Example:
#   ./generate_round3_test_config.sh localhost 5432 aimaheaddev aim_ahead
#
# ---------------------------------------------------------------------------------------------------------------

set -eu

DB_HOST="$1"
DB_PORT="$2"
DB_NAME="$3"
DB_USER="$4"
CASES_PER_USER=10
OUT="round3_test_config.csv"

# Prompt for database password
printf 'Password for user %s: ' "$DB_USER"
stty -echo
read DB_PASS
stty echo
echo
export PGPASSWORD="$DB_PASS"

echo "=========================================="
echo "Round 3 TEST Configuration Generator"
echo "=========================================="
echo "Database: $DB_NAME@$DB_HOST:$DB_PORT"
echo "Cases per user: $CASES_PER_USER"
echo "Test users:"
echo "  - lirjiao@unc.edu"
echo "  - test@unc.edu"
echo "  - sean.sylvia@unc.edu"
echo "  - srfort@live.unc.edu"
echo ""
echo "Configuration:"
echo "  Always shown (100%): Age, Gender"
echo "  Random (50%): Medical History, Family History, BMI, CRC_SCORE"
echo "  Never shown (0%): CRC_RISK ranges"
echo "Output file: $OUT"
echo "=========================================="
echo ""

# Write CSV header
printf 'User,Case No.,Path,Collapse,Highlight,Top\n' > "$OUT"

# Generate configuration for all 4 test users in a single query
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -w \
     -A -F',' -t <<SQL >> "$OUT"
WITH
  -- Define test users
  test_users AS (
    SELECT 'lirjiao@unc.edu' AS email
    UNION ALL SELECT 'test@unc.edu'
    UNION ALL SELECT 'sean.sylvia@unc.edu'
    UNION ALL SELECT 'srfort@live.unc.edu'
  ),
  
  -- Get all valid person_ids from visit_occurrence
  valid_persons AS (
    SELECT DISTINCT person_id
    FROM public.visit_occurrence
  ),
  
  -- Randomly select $CASES_PER_USER cases for each user
  selected_cases AS (
    SELECT
      u.email,
      vp.person_id AS case_id,
      ROW_NUMBER() OVER (PARTITION BY u.email ORDER BY random()) AS rn
    FROM test_users u
    CROSS JOIN valid_persons vp
  ),
  
  -- Limit to $CASES_PER_USER cases per user
  user_cases AS (
    SELECT email, case_id
    FROM selected_cases
    WHERE rn <= $CASES_PER_USER
  ),
  
  -- Age and Gender (ALWAYS SHOWN - 100%)
  always_shown AS (
    SELECT
      uc.email,
      uc.case_id,
      'BACKGROUND.Patient Demographics.Age' AS path
    FROM user_cases uc
    
    UNION ALL
    
    SELECT
      uc.email,
      uc.case_id,
      'BACKGROUND.Patient Demographics.Gender' AS path
    FROM user_cases uc
  ),
  
  -- Family History fields (50% random visibility)
  family_history_random AS (
    SELECT
      uc.email,
      uc.case_id,
      'BACKGROUND.Family History.' || o.value_as_string AS path
    FROM user_cases uc
    JOIN public.observation o ON o.person_id = uc.case_id
    WHERE o.observation_concept_id = 4167217
      AND o.value_as_string IS NOT NULL
      AND random() < 0.5
  ),
  
  -- Medical History fields (50% random visibility)
  medical_history_random AS (
    SELECT
      uc.email,
      uc.case_id,
      'BACKGROUND.Medical History.' || o.value_as_string AS path
    FROM user_cases uc
    JOIN public.observation o ON o.person_id = uc.case_id
    WHERE o.observation_concept_id = 1008364
      AND o.value_as_string IS NOT NULL
      AND random() < 0.5
  ),
  
  -- BMI from measurement table (50% random) - THE KEY FIX
  bmi_random AS (
    SELECT
      uc.email,
      uc.case_id,
      'PHYSICAL EXAMINATION.Body measure.BMI (body mass index) centile' AS path
    FROM user_cases uc
    JOIN public.measurement m ON m.person_id = uc.case_id
    WHERE m.measurement_concept_id = 40490382
      AND m.value_as_number IS NOT NULL
      AND random() < 0.5
  ),
  
  -- CRC_SCORE ONLY (50% random) - EXCLUDE all risk ranges
  crc_score_only AS (
    SELECT
      uc.email,
      uc.case_id,
      'BACKGROUND.CRC risk assessments.' || o.value_as_string AS path
    FROM user_cases uc
    JOIN public.observation o ON o.person_id = uc.case_id
    WHERE o.observation_concept_id = 45614722
      AND o.value_as_string IS NOT NULL
      -- ONLY show Colorectal Cancer Score, NOT the risk ranges
      AND o.value_as_string LIKE 'Colorectal Cancer Score:%'
      -- Explicitly exclude all risk-related observations
      AND o.value_as_string NOT LIKE '%Risk%'
      AND random() < 0.5
  ),
  
  -- Combine all visible fields
  all_visible_fields AS (
    SELECT * FROM always_shown
    UNION ALL
    SELECT * FROM family_history_random
    UNION ALL
    SELECT * FROM medical_history_random
    UNION ALL
    SELECT * FROM bmi_random
    UNION ALL
    SELECT * FROM crc_score_only
  )

-- Final output with standard CSV columns
SELECT
  email AS "User",
  case_id AS "Case No.",
  path AS "Path",
  'FALSE' AS "Collapse",
  'TRUE' AS "Highlight",
  '' AS "Top"
FROM all_visible_fields
ORDER BY email, case_id, path;
SQL

echo ""
echo "=========================================="
echo "Configuration generated successfully!"
echo "Output: $OUT"
echo ""
echo "Next steps:"
echo "1. Review the generated CSV file"
echo "2. Upload via: curl -X POST http://127.0.0.1:5000/admin/config/upload -F \"file=@$OUT\""
echo "=========================================="
