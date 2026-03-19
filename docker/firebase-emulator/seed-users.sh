#!/bin/bash
# Seed test users into Firebase Auth Emulator via REST API.
# Waits for the emulator to be ready, then creates users.

EMULATOR_URL="http://localhost:9099"
PROJECT_ID="${FIREBASE_PROJECT_ID:-fbi-dev-484410}"

# Wait for emulator to be ready (up to 60s)
echo "Waiting for Firebase Auth Emulator to be ready..."
for i in $(seq 1 60); do
  if curl -sf "${EMULATOR_URL}/" > /dev/null 2>&1; then
    echo "  Emulator ready after ${i}s"
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "  ERROR: Emulator not ready after 60s"
    exit 1
  fi
  sleep 1
done

create_user() {
  local email="$1"
  local password="$2"
  local display_name="$3"

  echo "Creating user: ${email}"
  local response
  response=$(curl -s -w "\n%{http_code}" -X POST \
    "${EMULATOR_URL}/identitytoolkit.googleapis.com/v1/accounts:signUp?key=fake-api-key" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"${email}\",
      \"password\": \"${password}\",
      \"displayName\": \"${display_name}\",
      \"returnSecureToken\": true
    }")
  local http_code
  http_code=$(echo "$response" | tail -1)
  if [ "$http_code" = "200" ]; then
    echo "  OK"
  elif echo "$response" | grep -q "EMAIL_EXISTS"; then
    echo "  Already exists (OK)"
  else
    echo "  ERROR (HTTP ${http_code}): $(echo "$response" | head -1)"
  fi
}

# Default test users
create_user "admin@local.dev"  "password123" "Local Admin"
create_user "leader@local.dev" "password123" "Local Leader"
create_user "member@local.dev" "password123" "Local Member"

echo "Firebase Auth seed complete."
