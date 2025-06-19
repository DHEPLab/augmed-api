#!/usr/bin/env bash
set -euo pipefail

# === DESCRIPTION ==================
# This script creates accounts for a list of participants in a TSV file.
# The TSV file should have the following columns:
# Occupation/Specialty Email Prolific ID.
# The script will randomly select a specified number of participants and create accounts for them.
# The script uses the Prolific API to create accounts.
# The script requires the following environment variables to be set:
# - API_URL: The URL of the admin API for creating accounts.
# - API_KEY: The API key for admin API for creating accounts.
# The script will create accounts for the specified number of participants and print the number of accounts created.
# The script will also print the number of accounts created.
# ==================================

# === CONFIGURATION ===
API_URL="api_url_here"
API_KEY="api_key_here
INPUT_FILE="participants.tsv"
NUM_SAMPLES=100

# === sanity check ===
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: '$INPUT_FILE' not found. Please save your list as a TSV with columns:" \
       "Occupation/Specialty<TAB>Email<TAB>Prolific ID." >&2
  exit 1
fi

# === helper to produce randomized lines of "email|id" with valid emails only ===
random_stream() {
  awk -F'\t' '
    BEGIN { srand() }
    NR>1 && NF>=3 {
      email = $2
      # trim leading/trailing whitespace
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", email)
      # only keep if looks like user@domain.tld (no spaces)
      if (email ~ /^[^[:space:]]+@[^[:space:]]+\.[^[:space:]]+$/) {
        printf "%f\t%s|%s\n", rand(), email, $3
      }
    }
  ' "$INPUT_FILE" \
    | sort -n
}

# === build the JSON array ===
users_json="["
count=0

while IFS=$'\t' read -r _ pair; do
  IFS='|' read -r email id <<< "$pair"
  users_json+=$(
    printf '{"name":"Prolific ID: %s","email":"%s","position":"Physician Assistant (PA)","employer":"n/a","area_of_clinical_ex":"n/a"},' \
           "$id" "$email"
  )
  count=$((count+1))
  [ "$count" -ge "$NUM_SAMPLES" ] && break
done < <(random_stream)

if [ "$count" -eq 0 ]; then
  echo "Error: no valid emails found in $INPUT_FILE" >&2
  exit 1
fi

# strip trailing comma, close array
users_json="${users_json%,}]"

# === send one bulk request ===
curl --location "$API_URL" \
     --header "X-API-KEY: $API_KEY" \
     --header 'Content-Type: application/json' \
     --data-raw "{\"users\":$users_json}"

echo "✅ Created accounts for $count randomly selected participants."
