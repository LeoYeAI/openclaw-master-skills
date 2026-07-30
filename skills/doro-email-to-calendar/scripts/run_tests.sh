#!/bin/bash
# Run all tests using Python's built-in unittest
# Usage: ./run_tests.sh [test_module] [test_class] [test_method]
#
# Examples:
#   ./run_tests.sh                          # Run all tests
#   ./run_tests.sh test_common              # Run tests in test_common.py
#   ./run_tests.sh test_common TestGetDayOfWeek  # Run specific test class

cd "$(dirname "$0")"

if [ $# -eq 0 ]; then
    python3 -m unittest discover -s tests -v
elif [ $# -eq 1 ]; then
    python3 -m unittest "tests.$1" -v
elif [ $# -eq 2 ]; then
    python3 -m unittest "tests.$1.$2" -v
else
    python3 -m unittest "tests.$1.$2.$3" -v
fi
