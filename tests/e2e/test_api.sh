#!/bin/bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

pass() {
  echo -e "${GREEN}[PASS]${NC} $1"
  PASSED=$((PASSED + 1))
}

fail() {
  echo -e "${RED}[FAIL]${NC} $1"
  FAILED=$((FAILED + 1))
}

assert_status() {
  local step="$1"
  local expected="$2"
  local actual="$3"
  if [ "$actual" -eq "$expected" ]; then
    pass "$step (HTTP $actual)"
  else
    fail "$step — expected HTTP $expected, got HTTP $actual"
  fi
}

# Prerequisite checks
if ! command -v jq &> /dev/null; then
  echo -e "${RED}Error: jq is not installed. Install it with: brew install jq${NC}"
  exit 1
fi

if [ -z "${BASE_URL:-}" ]; then
  echo -e "${RED}Error: BASE_URL environment variable is not set.${NC}"
  echo "Usage: BASE_URL=http://127.0.0.1:3000 bash $0"
  exit 1
fi

echo "================================================"
echo "E2E Test: Task Management API"
echo "BASE_URL: ${BASE_URL}"
echo "================================================"
echo ""

# Step 1: POST /tasks — Create a task
echo "--- Step 1: Create task ---"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "E2E test task"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "POST /tasks" 201 "$HTTP_CODE"

if [ "$HTTP_CODE" -ne 201 ]; then
  echo -e "${RED}Cannot continue without a created task. Aborting.${NC}"
  exit 1
fi

echo "$BODY" | jq .

# Step 2: Extract task_id
TASK_ID=$(echo "$BODY" | jq -r '.task_id')
echo ""
echo "Extracted task_id: ${TASK_ID}"
echo ""

# Step 3: GET /tasks — List tasks
echo "--- Step 3: List tasks ---"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/tasks")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "GET /tasks" 200 "$HTTP_CODE"

FOUND=$(echo "$BODY" | jq --arg id "$TASK_ID" '.tasks[] | select(.task_id == $id) | .task_id' | wc -l | tr -d ' ')
if [ "$FOUND" -ge 1 ]; then
  pass "Task $TASK_ID found in list"
else
  fail "Task $TASK_ID not found in list"
fi
echo ""

# Step 4: PUT /tasks/{task_id} — Update done=true
echo "--- Step 4: Update task (done=true) ---"
RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${BASE_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{"done": true}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "PUT /tasks/${TASK_ID}" 200 "$HTTP_CODE"
echo "$BODY" | jq .
echo ""

# Step 5: GET /tasks/{task_id} — Verify update
echo "--- Step 5: Verify update ---"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/tasks/${TASK_ID}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "GET /tasks/${TASK_ID}" 200 "$HTTP_CODE"

DONE=$(echo "$BODY" | jq -r '.done')
if [ "$DONE" = "true" ]; then
  pass "Task done=true confirmed"
else
  fail "Task done expected true, got $DONE"
fi
echo ""

# Step 6: DELETE /tasks/{task_id} — Delete task
echo "--- Step 6: Delete task ---"
RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/tasks/${TASK_ID}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "DELETE /tasks/${TASK_ID}" 200 "$HTTP_CODE"
echo "$BODY" | jq .
echo ""

# Step 7: GET /tasks/{task_id} — Verify deletion (expect 404)
echo "--- Step 7: Verify deletion ---"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/tasks/${TASK_ID}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
assert_status "GET /tasks/${TASK_ID} (expect 404)" 404 "$HTTP_CODE"
echo ""

# Summary
echo "================================================"
TOTAL=$((PASSED + FAILED))
echo -e "Results: ${GREEN}${PASSED} passed${NC}, ${RED}${FAILED} failed${NC}, ${TOTAL} total"
echo "================================================"

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
