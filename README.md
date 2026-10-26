# NABME website

The new website for the National Association of Black Male Educators (NABME). Preview: https://nabme-movement.vercel.app

## How it's built

- `build.py` generates every page into `site/`. Page content, navigation, photos and numbers all live in this file.
- `site/styles.css` and `site/main.js` hold the design system and interactions. `site/assets/` holds photos, video, logos and the Summit QR code.
- `site/api/submit.js` is a Vercel function that saves every form to Airtable. The tables and columns are defined in `site/api/_schema.js`.
- `scripts/setup-airtable.mjs` creates those tables in a new Airtable base (one-time setup).
- `DESIGN.md` documents colors, type, motion, pages, and what's connected and what isn't.

## Make a change

```bash
NABME_VARIANT=a python3 build.py
```

This rebuilds `site/`. Preview it with any static server, then deploy:

```bash
cd site && vercel deploy --prod --name nabme-movement
```

## Environment variables (Vercel)

| Variable | Purpose |
| --- | --- |
| `AIRTABLE_TOKEN` | Airtable access token (scopes: data.records:write, schema.bases:read, schema.bases:write) |
| `AIRTABLE_BASE_ID` | The base ID, starting with `app` |
| `RESEND_API_KEY`, `NOTIFY_FROM`, `NOTIFY_TO` | Optional email alerts for new form entries |

Never commit these values.

## Notes

- The printed Summit QR code points to `https://nabme-movement.vercel.app/register`, a redirect set in `build.py` (`SUMMIT_REGISTER`). Keep that path working after launch.
- Versions B (Heritage) and C (Editorial) build into `site-b/` and `site-c/` with `NABME_VARIANT=b` or `c`. They're kept out of the repo because the client chose version A.
