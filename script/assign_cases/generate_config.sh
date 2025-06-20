#!/usr/bin/env bash

# ---------------------------------------------------------------------------------------------------------------
# generate_config.sh
#
# A Shell script to generate a configuration file for assigning cases to users in a database.
# This script connects to a PostgreSQL database and retrieves a specified number of users and cases,
# then generates a CSV file with the assigned cases and features for each user.
#
# This script requires the following parameters:
# 1. Database host
# 2. Database port (default is 5432)
# 3. Database name
# 4. Database user
# 5. Number of users to select
# 6. Number of cases per user
# 7. Number of AI cases per user
# 8. Output CSV file path (default is "config.csv", which is in the same directory as this script)
#
# It will create a CSV file for N users sampled from your public.user table, assigns each 24 random person-cases,
# randomly flags 12 of them for AI (“RISK ASSESSMENT.CRC risk assessments”), and writes out one row per
# (User, Case No., Path) in exactly the lab’s OMOP format.
# You can then use this CSV file to configure the assignment of cases to users in your application. Specifically,
# use it with Postman and the `https://augmed1.dhep.org/admin/config/upload` endpoint to upload the configuration
# CSV for case assignments. The backend will then use this configuration to assign cases to users.
#
# To run:
# 1. Change directory to the script's location: cd script/assign_cases
# 2. Run: chmod +x generate_config.sh
# 3. Run the script: (Remember to remove the # symbols at the beginning of each line)
#   ./generate_config.sh \
#     <db_host> \
#     <db_port> \
#     <db_name> \
#     <db_user> \
#     <number_of_users> \
#     <cases_per_user> \
#     <ai_per_user> \
#     <output_file.csv>
#
# Example:
#   ./generate_config.sh \
#     localhost \
#     5433 \
#     aimaheaddev \
#     aim_ahead \
#     6 \
#     20 10 \
#     config.csv
#
# (Enter your database password when prompted)
#
# ---------------------------------------------------------------------------------------------------------------

set -eu

DB_HOST="$1"
DB_PORT="$2"
DB_NAME="$3"
DB_USER="$4"
NUM_USERS="$5"
CASES_PER_USER="$6"
RISK_CASES_PER_USER="$7"
OUT="$8"

# Prompt for database password once, export to PGPASSWORD for all subsequent psql invocations
printf 'Password for user %s: ' "$DB_USER"
stty -echo
read DB_PASS
stty echo
echo
export PGPASSWORD="$DB_PASS"

# 1) Print a single header line.  (The CSV parser expects exactly these columns.)
printf 'User,Case No.,Path,Collapse,Highlight,Top\n' > "$OUT"

# 2) Loop over each of N random users, generate their cases, and append to CSV with progress logging
count=0
while IFS= read -r user; do
  count=$((count + 1))
  echo "[${count}/${NUM_USERS}] Processing user: $user"

  psql -h "$DB_HOST" \
       -p "$DB_PORT" \
       -U "$DB_USER" \
       -d "$DB_NAME" \
       -w \
       -A -F',' -t <<SQL >> "$OUT"
WITH
  -- STEP A: Single user context
  users AS (
    SELECT '$user' AS email
  ),

  -- STEP B: All person_ids that actually have at least one visit (so get_case_by_user won't blow up)
  valid_persons AS (
    SELECT DISTINCT person_id
    FROM public.visit_occurrence
  ),

  -- STEP C: Cross‐join to pick M random cases/user + K random “risk cases”/user
  picks AS (
    SELECT
      u.email,
      vp.person_id           AS case_no,
      ROW_NUMBER() OVER (PARTITION BY u.email ORDER BY random()) AS rn_case,
      ROW_NUMBER() OVER (PARTITION BY u.email ORDER BY random()) AS rn_risk
    FROM users u
    CROSS JOIN valid_persons vp
  ),

  sample_cases AS (
    SELECT email, case_no
    FROM picks
    WHERE rn_case <= $CASES_PER_USER
  ),

  risk_cases AS (
    SELECT email, case_no
    FROM picks
    WHERE rn_risk <= $RISK_CASES_PER_USER
  ),

  -- STEP D: Gather *all* leaf‐level observation rows for each (user,case_id)
  all_leaves AS (
    -- BACKGROUND.Family History (4167217)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Family History.' || o.value_as_string AS path
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4167217
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- BACKGROUND.Social History.Smoke (4041306)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Social History.Smoke.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4041306
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- BACKGROUND.Social History.Alcohol (4238768)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Social History.Alcohol.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4238768
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- BACKGROUND.Social History.Drug use (4038710)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Social History.Drug use.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4038710
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- BACKGROUND.Social History.Sexual behavior (4283657, 4314454)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Social History.Sexual behavior.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id IN (4283657, 4314454)
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- BACKGROUND.Medical History (1008364)
    SELECT
      s.email,
      s.case_no,
      'BACKGROUND.Medical History.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 1008364
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PATIENT COMPLAINT.Chief Complaint (38000282)
    SELECT
      s.email,
      s.case_no,
      'PATIENT COMPLAINT.Chief Complaint.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 38000282
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PATIENT COMPLAINT.Current Symptoms (38000280, 38000281, 44814721, 38000276)
    SELECT
      s.email,
      s.case_no,
      'PATIENT COMPLAINT.Current Symptoms.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id IN (38000280, 38000281, 44814721, 38000276)
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Abdomen (4152368)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Abdomen.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4152368
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Respiratory (4090320)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Respiratory.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4090320
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Vital Signs (4263222)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Vital Signs.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4263222
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Neurological (4154954)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Neurological.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4154954
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Ophthalmology (4080843)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Ophthalmology.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4080843
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Cardiovascular (36717771)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Cardiovascular.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 36717771
     AND o.value_as_string IS NOT NULL

    UNION ALL
    -- PHYSICAL EXAMINATION.Physical Characteristics (4086988)
    SELECT
      s.email,
      s.case_no,
      'PHYSICAL EXAMINATION.Physical Characteristics.' || o.value_as_string
    FROM sample_cases s
    JOIN public.observation o
      ON o.person_id = s.case_no
     AND o.observation_concept_id = 4086988
     AND o.value_as_string IS NOT NULL
  ),

  -- STEP E: From all_leaves, randomly pick ~50% to “show” (WHERE random()<0.5)
  shown_leaves AS (
    SELECT email, case_no, path
    FROM all_leaves
    WHERE random() < 0.5
  ),

  -- STEP F: Emit exactly one CSV‐row for each chosen leaf, with Collapse=FALSE,Highlight=TRUE
  leaf_rows AS (
    SELECT
      sl.email    AS "User",
      sl.case_no  AS "Case No.",
      sl.path     AS Path,
      'FALSE'     AS Collapse,
      'TRUE'      AS Highlight,
      ''          AS Top
    FROM shown_leaves sl
  ),

  -- STEP G: Emit one “CRC risk assessments” row for each (user,case_no) in risk_cases
  risk_rows AS (
    SELECT
      rc.email   AS "User",
      rc.case_no AS "Case No.",
      'RISK ASSESSMENT.CRC risk assessments' AS Path,
      'FALSE'    AS Collapse,
      'TRUE'     AS Highlight,
      ''         AS Top
    FROM risk_cases rc
  )

-- UNION together leaf_rows + risk_rows and randomize order for this user
SELECT * FROM (
  SELECT * FROM leaf_rows
  UNION ALL
  SELECT * FROM risk_rows
) AS all_rows
ORDER BY random();
SQL

done < <(psql -h "$DB_HOST" \
           -p "$DB_PORT" \
           -U "$DB_USER" \
           -d "$DB_NAME" \
           -w \
           -A -t <<SQL
SELECT email
FROM public."user"
ORDER BY random()
LIMIT $NUM_USERS;
SQL
)

echo "Done – wrote $OUT"
