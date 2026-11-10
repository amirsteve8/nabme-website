#!/bin/bash
# Connects verified Summit checkout: asks for NABME's PayPal Live Client ID and Secret (the secret is hidden as you paste it),
# checks them with PayPal, saves them to the nabme-movement Vercel project, and deploys the site.
# Run from the nabme-v3 folder:  bash scripts/connect-paypal.sh
set -e
cd "$(dirname "$0")/.."
echo "NABME website: connect PayPal"
echo
read -r -p "Live Client ID: " PAYPAL_CLIENT_ID
read -r -s -p "Live Secret (hidden as you paste, then press Enter): " PAYPAL_CLIENT_SECRET
echo
PAYPAL_CLIENT_ID="$(printf %s "$PAYPAL_CLIENT_ID" | tr -d '[:space:]')"
PAYPAL_CLIENT_SECRET="$(printf %s "$PAYPAL_CLIENT_SECRET" | tr -d '[:space:]')"
if [ -z "$PAYPAL_CLIENT_ID" ] || [ -z "$PAYPAL_CLIENT_SECRET" ]; then echo "One of those was empty. Run this again."; exit 1; fi
CODE="$(printf 'user = "%s:%s"\n' "$PAYPAL_CLIENT_ID" "$PAYPAL_CLIENT_SECRET" | curl -s -o /dev/null -w '%{http_code}' -K - -d grant_type=client_credentials https://api-m.paypal.com/v1/oauth2/token)"
if [ "$CODE" != "200" ]; then
  echo "PayPal didn't accept those (status $CODE). Make sure they're from the Live tab, not Sandbox, and copied fully."
  exit 1
fi
echo "PayPal accepted them."
cd site
vercel env rm PAYPAL_CLIENT_ID production --yes >/dev/null 2>&1 || true
vercel env rm PAYPAL_CLIENT_SECRET production --yes >/dev/null 2>&1 || true
printf %s "$PAYPAL_CLIENT_ID" | vercel env add PAYPAL_CLIENT_ID production >/dev/null
printf %s "$PAYPAL_CLIENT_SECRET" | vercel env add PAYPAL_CLIENT_SECRET production >/dev/null
unset PAYPAL_CLIENT_SECRET
echo "Saved to Vercel. Deploying..."
vercel deploy --prod --yes --name nabme-movement 2>&1 | tail -2
echo
echo "All set. Tell Claude it's done, and it will check the live checkout."
