#!/usr/bin/env bash


echo " Running tests before pushing changes "

# Run pytest with coverage
coverage run -m pytest

# Check if tests were successful
if [ $? -ne 0 ]; then
    echo " Tests failed, please check and fix your code. "
    exit 1
fi

# Check coverage
coverage report

# Check if coverage threshold is met
if [ $? -ne 0 ]; then
    echo "Coverage threshold not met, please improve test coverage.    "
    exit 1
fi

echo "All checks passed. Proceeding with push..."
exit 0
