#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
    printf 'Usage: %s TEST_DIRECTORY [TEST_PATTERN]\n' "$0" >&2
    exit 2
fi

exec python3 -B -m unittest discover -v -s "$1" -p "${2:-test_*.py}"
