#!/bin/bash
# Connects the website to NABME's MailerLite: asks for an API token (hidden as you paste it), checks it,
# saves it to the nabme-movement Vercel project, and deploys. After this, every signup lands in MailerLite.
# Run from the nabme-v3 folder:  bash scripts/connect-mailerlite.sh
set -e
cd "$(dirname "$0")/.."
echo "NABME website: connect MailerLite"
echo
read -r -s -p "MailerLite API token (hidden as you paste, then press Enter): " MAILERLITE_API_KEY
echo
MAILERLITE_API_KEY="$(printf %s "$MAILERLITE_API_KEY" | tr -d '[:space:]')"
if [ -z "$MAILERLITE_API_KEY" ]; then echo "Nothing was pasted. Run this again."; exit 1; fi
CODE="$(printf 'header = "Authorization: Bearer %s"\n' "$MAILERLITE_API_KEY" | curl -s -o /dev/null -w '%{http_code}' -K - -H 'Accept: application/json' 'https://connect.mailerlite.com/api/groups?limit=1')"
if [ "$CODE" != "200" ]; then
  echo "MailerLite didn't accept that token (status $CODE). Create a new one under Integrations > MailerLite API and copy it fully."
  exit 1
fi
echo "MailerLite accepted it."
cd site
vercel env rm MAILERLITE_API_KEY production --yes >/dev/null 2>&1 || true
printf %s "$MAILERLITE_API_KEY" | vercel env add MAILERLITE_API_KEY production >/dev/null
unset MAILERLITE_API_KEY
echo "Saved to Vercel. Deploying..."
vercel deploy --prod --yes --name nabme-movement 2>&1 | tail -2
echo
echo "All set. Tell Claude it's done, and it will send a test signup through."
