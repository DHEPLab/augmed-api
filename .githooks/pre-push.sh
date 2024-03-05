#!/usr/bin/env bash

# Define color variables for printing messages with color
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo -e "${YELLOW}Running tests and checking coverage before pushing changes...${RESET}"

# Run pytest with coverage
pytest

# Capture the exit status of pytest command
result=$?

if [ $result -ne 0 ]; then
    echo -e "${RED}Tests failed or do not meet coverage threshold, please check and fix your code.${RESET}"
    exit 1
fi

echo -e "${GREEN}All checks passed. Proceeding with push...${RESET}"
exit 0
