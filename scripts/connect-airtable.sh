#!/bin/bash
# Connects the NABME website to Airtable in one go:
#   1. asks for the base ID and access token (the token is hidden as you paste it)
#   2. creates every form table and column in the base
#   3. saves both values to the nabme-movement Vercel project for production
# Run from the nabme-v3 folder:  bash scripts/connect-airtable.sh
set -e
cd "$(dirname "$0")/.."

echo "NABME website: connect Airtable"
echo
read -r -p "Base ID (starts with app): " AIRTABLE_BASE_ID
read -r -s -p "Access token (hidden as you paste, then press Enter): " AIRTABLE_TOKEN
echo
AIRTABLE_BASE_ID="$(printf %s "$AIRTABLE_BASE_ID" | tr -d '[:space:]')"
AIRTABLE_TOKEN="$(printf %s "$AIRTABLE_TOKEN" | tr -d '[:space:]')"
echo "Token received: ${AIRTABLE_TOKEN:0:3}... (${#AIRTABLE_TOKEN} characters)"
echo

case "$AIRTABLE_BASE_ID" in app*) ;; *) echo "That base ID doesn't start with 'app'. Check the base's web address and try again."; exit 1;; esac
if [ -z "$AIRTABLE_TOKEN" ]; then echo "No token entered. The paste may not have gone in; try again."; exit 1; fi
case "$AIRTABLE_TOKEN" in pat*) ;; *) echo "Airtable tokens start with 'pat'. Copy the token again and retry."; exit 1;; esac

if ! curl -sf -o /dev/null -H "Authorization: Bearer $AIRTABLE_TOKEN" "https://api.airtable.com/v0/meta/bases/$AIRTABLE_BASE_ID/tables"; then
  echo "Airtable didn't accept this token for that base. Check that:"
  echo "  - it's the newest token (after Regenerate, the old one stops working)"
  echo "  - it has the schema.bases:read and schema.bases:write scopes"
  echo "  - its Access includes the NABME Website base, then click Save changes"
  exit 1
fi
echo "Token works."

echo "Creating tables in Airtable..."
AIRTABLE_TOKEN="$AIRTABLE_TOKEN" AIRTABLE_BASE_ID="$AIRTABLE_BASE_ID" node scripts/setup-airtable.mjs
echo

echo "Saving the connection to Vercel (production)..."
cd site
vercel env rm AIRTABLE_TOKEN production --yes >/dev/null 2>&1 || true
vercel env rm AIRTABLE_BASE_ID production --yes >/dev/null 2>&1 || true
printf %s "$AIRTABLE_TOKEN" | vercel env add AIRTABLE_TOKEN production >/dev/null
printf %s "$AIRTABLE_BASE_ID" | vercel env add AIRTABLE_BASE_ID production >/dev/null
unset AIRTABLE_TOKEN
echo "Saved."
echo
echo "All set. Tell Claude it's done, and it will redeploy the site and test each form."
