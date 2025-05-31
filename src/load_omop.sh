#!/usr/bin/env bash
# ------------------------------------------------------------------------------------------------------------
# load_omop.sh
#
# This script force-reloads the OMOP vocabulary and clinical data into a local PostgreSQL database.
# It assumes the database is running locally and the user has appropriate permissions.
# Change the DB_URL, VOCAB, and CLINICAL variables as needed.
# NOTE: Make sure that you have downloaded the OMOP vocabulary from https://athena.ohdsi.org/vocabulary/list
# and the clinical data is in the expected format in the specified directories before running this script.
#
# Usage: ./load_omop.sh
#
# ------------------------------------------------------------------------------------------------------------

set -euo pipefail

DB_URL="postgresql://localuser:localpass@localhost:5432/localdb"
VOCAB="$HOME/vocab"
CLINICAL="$HOME/data"

echo "=== A) Prep: widen name columns & truncate everything ==="
psql "$DB_URL" <<'EOF'
-- 1) Widen all length-constrained name fields to TEXT
ALTER TABLE concept             ALTER COLUMN concept_name             TYPE TEXT;
ALTER TABLE vocabulary          ALTER COLUMN vocabulary_name         TYPE TEXT;
ALTER TABLE domain              ALTER COLUMN domain_name             TYPE TEXT;
ALTER TABLE concept_class       ALTER COLUMN concept_class_name      TYPE TEXT;
ALTER TABLE concept_synonym     ALTER COLUMN concept_synonym_name    TYPE TEXT;
ALTER TABLE relationship        ALTER COLUMN relationship_name        TYPE TEXT;
ALTER TABLE concept_relationship ALTER COLUMN concept_relationship_name TYPE TEXT;
ALTER TABLE concept_ancestor    ALTER COLUMN ancestor_desc             TYPE TEXT;
ALTER TABLE drug_strength       ALTER COLUMN description             TYPE TEXT;

-- 2) Truncate all vocab & clinical tables
TRUNCATE concept_synonym,
         concept_ancestor,
         concept_relationship,
         relationship,
         concept_class,
         domain,
         vocabulary,
         drug_strength,
         concept
  RESTART IDENTITY CASCADE;

TRUNCATE person,
         visit_occurrence,
         observation,
         measurement,
         display_config
  RESTART IDENTITY CASCADE;
EOF

echo "=== B) Disable triggers (to skip FK checks) ==="
psql "$DB_URL" <<'EOF'
-- disable triggers on vocab tables
ALTER TABLE concept          DISABLE TRIGGER ALL;
ALTER TABLE vocabulary       DISABLE TRIGGER ALL;
ALTER TABLE domain           DISABLE TRIGGER ALL;
ALTER TABLE concept_class    DISABLE TRIGGER ALL;
ALTER TABLE concept_synonym  DISABLE TRIGGER ALL;
ALTER TABLE relationship     DISABLE TRIGGER ALL;
ALTER TABLE concept_relationship DISABLE TRIGGER ALL;
ALTER TABLE concept_ancestor DISABLE TRIGGER ALL;
ALTER TABLE drug_strength    DISABLE TRIGGER ALL;
EOF

echo "=== C) Bulk-load vocab (tabs) ==="
psql "$DB_URL" <<EOF
\COPY concept               FROM '$VOCAB/CONCEPT.csv'               WITH DELIMITER E'\t' CSV HEADER;
\COPY vocabulary            FROM '$VOCAB/VOCABULARY.csv'            WITH DELIMITER E'\t' CSV HEADER;
\COPY domain                FROM '$VOCAB/DOMAIN.csv'                WITH DELIMITER E'\t' CSV HEADER;
\COPY concept_class         FROM '$VOCAB/CONCEPT_CLASS.csv'         WITH DELIMITER E'\t' CSV HEADER;
\COPY concept_synonym       FROM '$VOCAB/CONCEPT_SYNONYM.csv'       WITH DELIMITER E'\t' CSV HEADER;
\COPY relationship          FROM '$VOCAB/RELATIONSHIP.csv'          WITH DELIMITER E'\t' CSV HEADER;
\COPY concept_relationship  FROM '$VOCAB/CONCEPT_RELATIONSHIP.csv'  WITH DELIMITER E'\t' CSV HEADER;
\COPY concept_ancestor      FROM '$VOCAB/CONCEPT_ANCESTOR.csv'      WITH DELIMITER E'\t' CSV HEADER;
\COPY drug_strength         FROM '$VOCAB/DRUG_STRENGTH.csv'         WITH DELIMITER E'\t' CSV HEADER;
EOF

echo "=== D) Re-enable triggers (restore FK enforcement) ==="
psql "$DB_URL" <<'EOF'
ALTER TABLE concept          ENABLE TRIGGER ALL;
ALTER TABLE vocabulary       ENABLE TRIGGER ALL;
ALTER TABLE domain           ENABLE TRIGGER ALL;
ALTER TABLE concept_class    ENABLE TRIGGER ALL;
ALTER TABLE concept_synonym  ENABLE TRIGGER ALL;
ALTER TABLE relationship     ENABLE TRIGGER ALL;
ALTER TABLE concept_relationship ENABLE TRIGGER ALL;
ALTER TABLE concept_ancestor ENABLE TRIGGER ALL;
ALTER TABLE drug_strength    ENABLE TRIGGER ALL;
EOF

echo "=== E) Load clinical OMOP data (commas) & assign cases ==="
psql "$DB_URL" <<EOF
\COPY person           FROM '$CLINICAL/person.csv'           WITH (FORMAT csv, HEADER true);
\COPY visit_occurrence FROM '$CLINICAL/visit_occurrence.csv' WITH (FORMAT csv, HEADER true);
\COPY observation      FROM '$CLINICAL/observation.csv'      WITH (FORMAT csv, HEADER true);
\COPY measurement      FROM '$CLINICAL/measurement.csv'      WITH (FORMAT csv, HEADER true);

INSERT INTO display_config (user_email, case_id, path_config)
  SELECT 'test@unc.edu', visit_occurrence_id, '{}'::jsonb
    FROM visit_occurrence;
EOF

echo "✅ All vocabulary and clinical data have been force-reloaded!"
