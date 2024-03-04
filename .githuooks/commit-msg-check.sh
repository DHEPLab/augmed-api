#!/usr/bin/env bash

# Define color variables for printing messages with color
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

# Define regex patterns for different parts of the commit message
card_name_regex="\[UNCAIM-[0-9]+\]|\[TECH\]"
person_name_regex="[A-Z][a-z]+."
author_name_regex="\[(${person_name_regex})(\s(&|&&)\s${person_name_regex})?\]"
work_type_regex="build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test"
commit_msg_regex="^${card_name_regex}${author_name_regex}\s?${work_type_regex}(\([a-z \-]+\))?\!?:\ .+"

# Function to read the commit message from the provided file
get_commit_message() {
    cat "$1"
}

# Function to check if the commit message matches the given regex pattern
matches_regex() {
    local message=$1
    local regex=$2
    echo "$message" | grep -Eq "$regex"
}

# Function to print a success message
print_success() {
    echo -e "${GREEN}Commit message meets Conventional Commit standards.${RESET}"
}

# Function to print an error message with examples
print_error() {
    echo -e "${RED}Commit message does not meet Conventional Commit standard.${RESET}"
    echo -e "${YELLOW}Example: [UNCAIM-70][Alex Xu] feat: the code changes the world.${RESET}"
    echo -e "${YELLOW}Or for pairs: [UNCAIM-70][Pair DevA & Pair DevB] feat: the code changes the world.${RESET}"
}

# Read the commit message from the provided file path
commit_message=$(get_commit_message "$1")

# Check if the commit message matches the conventional commits regex
if matches_regex "$commit_message" "$commit_msg_regex"; then
    print_success
    exit 0
else
    print_error
    exit 1
fi
