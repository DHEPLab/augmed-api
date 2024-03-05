#!/usr/bin/env bash

echo "Running tests and checking coverage before pushing changes..."

# Run pytest with coverage (assuming pytest-cov is configured in pyproject.toml)
pytest

# Capture the exit status of pytest command
result=$?

# If the result is not successful (non-zero), then tests failed
if [ $result -ne 0 ]; then
    echo "Tests failed or do not meet coverage threshold, please check and fix your code."
    exit 1
fi


echo "All checks passed. Proceeding with push..."
exit 0
