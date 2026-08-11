#!/usr/bin/env bash
set -euo pipefail

python -m pip install --disable-pip-version-check --quiet 'pytest==9.1.1'
python -m compileall -q src tests scripts mastermind_sidecar.py
python -m pytest -q tests
python scripts/operate.py
python scripts/verify_public_surface.py

binary="$(mktemp)"
trap 'rm -f "$binary"' EXIT
c++ -std=c++17 -Wall -Wextra -Werror src/lambert_solver.cpp -o "$binary"
output="$($binary)"
printf '%s\n' "$output"
grep -Fq 'LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY' <<<"$output"
grep -Fq 'Hohmann transfer departure speed estimate:' <<<"$output"
