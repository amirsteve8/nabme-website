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
echo

case "$AIRTABLE_BASE_ID" in app*) ;; *) echo "That base ID doesn't start with 'app'. Check the base's web address and try again."; exit 1;; esac
if [ -z "$AIRTABLE_TOKEN" ]; then echo "No token entered."; exit 1; fi

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
