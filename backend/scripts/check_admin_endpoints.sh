#!/usr/bin/env bash
# Simple script to verify admin-protected endpoints locally.
# Usage:
#   1) Ensure backend is running (see instructions below).
#   2) Set TEST_TOKEN and ADMIN_UIDS as described below.
#   3) Run this script from repo root: bash backend/scripts/check_admin_endpoints.sh

set -euo pipefail

# Defaults - override by exporting variables before running
: "${BASE_URL:=http://localhost:8000}"
: "${TEST_TOKEN:=faketoken1234}"

# Dev fallback uid: dev-<first8 of token>
DEV_UID="dev-${TEST_TOKEN:0:8}"

echo "Base URL: ${BASE_URL}"
echo "Using test token: ${TEST_TOKEN}" 
echo "Expected dev uid: ${DEV_UID}"

echo
echo "==== Pre-check: make sure ADMIN_UIDS contains '${DEV_UID}' ===="
echo "If not, export ADMIN_UIDS=${DEV_UID} before starting the backend."
echo

echo "1) Try POST /equipments with Authorization (should succeed)"
curl -sS -o /dev/stderr -w "\nHTTP: %{http_code}\n" -X POST "${BASE_URL}/equipments" \
  -H "Authorization: Bearer ${TEST_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Pump","model":"T-1","location":"Lab"}' || true

echo
echo "2) Try POST /equipments without Authorization (should be 403)"
curl -sS -o /dev/stderr -w "\nHTTP: %{http_code}\n" -X POST "${BASE_URL}/equipments" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Pump","model":"T-1","location":"Lab"}' || true

echo
echo "3) Try POST /upload-url with Authorization (should succeed)"
curl -sS -o /dev/stderr -w "\nHTTP: %{http_code}\n" -X POST "${BASE_URL}/upload-url" \
  -H "Authorization: Bearer ${TEST_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg"}' || true

echo
echo "4) Try POST /upload-url without Authorization (should be 403)"
curl -sS -o /dev/stderr -w "\nHTTP: %{http_code}\n" -X POST "${BASE_URL}/upload-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg"}' || true

echo
echo "Done. If the first and third calls returned 200 and the second/fourth returned 403, admin protection works."
