# NABME.org rebuild (v3)

Built from **"NABME.org Website Rebuild, Designer Handoff"** (Oct 11, 2026). Edit content in `build.py`, then run `python3 build.py` to regenerate `site/`. Deploy the `site/` folder.

Mode: **Persuade.** Every page gives one clear next step in its first screen.
Inspiration: thecenterblacked.org (video first, faces before paragraphs, act right away).

## Color (from the handoff, plus gray)
| Token | Hex | Use |
|---|---|---|
| Signature Red | `#C51F36` | Buttons, the highlight word in each H1, labels, closing bands |
| Deep Red | `#9E1C2D` | Hover / pressed |
| Coral | `#F36070` | Accents on dark only |
| Ink | `#1B1C1B` | Text, footer |
| Paper | `#F7F6F2` | Page |
| Muted | `#585A56` | Captions; rules `#D7D7D0` |
| Stone (gray) | `#ECEBE5` | Light gray bands |
| Graphite (gray) | `#232523` | Dark gray bands: hero, impact, Summit, utility bar |

Red stays the accent, never a whole page.

## Signature moves
- **Thin red slash**, carried over from the old site's angled dividers: one per hero and dark band. Red wedges sit in dark bands.
- **One red word** in every H1.
- **Red eyebrow labels** above section titles. The handoff asks for them; impeccable would normally ban them, and the client brief wins.
- **Red closing band** before the footer, with one call to action.

## Type
Inter only. Display headings use 800 weight at `opsz 32`, tracking −0.035em, max 5.75rem. Georgia only for big quote marks.

## Motion (performance-first)
- Muted hero video that alternates clips, with a pause button; it pauses offscreen and with reduced motion.
- Count-up numbers run once when seen. The Summit countdown updates every second (paused in hidden tabs). The quote carousel autoplays every 7s and pauses on hover, focus, offscreen and reduced motion.
- No smooth-scroll library, no scroll-jacking. The **Pause motion** toggle in the footer stops all of it.
- One newsletter pop-up, desktop only, after 30s or on exit intent, at most once every 14 days.

## Pages
`/`, `/mission`, `/founders` (+ `/craig-bio`, `/speight-bio`, `/blake-bio`), `/athari`, `/summit`, `/careers`, `/talent`, `/resume-bank`, `/employers`, `/jobs`, `/post-job`, `/blog` (+ `/math-with-buggbey`), `/media`, `/events`, `/live`, `/partners`, `/join`, `/contact`, `/donate`, `/nominate`.

Redirects (`vercel.json`) cover the short links and old WordPress URLs: `/give`, `/sponsors`, `/join-nabme-2`, `/mission-and-values`, `/board-members`, `/nabme-fellowship-program`, `/resumes`, `/contact-us`, `/nabme-careersw`.

## Not connected yet (front end only)
- **Forms:** Join, Contact, Resume Bank, Employer access, Post a job, Nominate, Athari interest list, newsletter. Each shows full validation and success states but doesn't send yet. Connect them to NABME's email tool or CRM.
- **Payments:** Donate (Givebutter, Donorbox or similar; the PayPal link already works), employer plans and job posts (Stripe or WP Job Manager paid add-ons).
- **NABME Live:** real @nabmeinc Instagram posts, embedded by hand (`IG_HOME` and `IG_WALL` in `build.py`: 3 on home, 9 on /live). To make the feed update itself, choose a social-wall service (Curator, Juicer, Walls.io…) and swap in its embed code.

## Versions
**Chosen (Oct 20, 2026): A · Movement.** The client picked nabme-movement.vercel.app; build and refine that one. B and C are kept for reference only.

Build each version with `NABME_VARIANT=a|b|c python3 build.py`. Version A outputs to `site/`; B and C output to `site-b/` and `site-c/` and share A's styles, script and media.
| Version | Link | Look |
|---|---|---|
| A · Movement | nabme-movement.vercel.app | Full-bleed video hero, seal in header, warm paper with gray bands |
| B · Heritage | nabme-heritage.vercel.app | Official NABME logo, black header with a deep-red utility bar, black-and-white photography that turns to color on hover, bigger type |
| C · Editorial | nabme-editorial.vercel.app | Light and airy: split hero with the film framed beside the headline, white bands, more space |

## Media (from Rick's Drive, Oct 12, 2026)
- Hero loops: `hero-summit.mp4`, the film's black-and-white opening (0:00–0:14, 1280×720, 4 MB); `hero-steps.mp4`, the aerial shot of the men on the steps (IMG_0686, 5 s, 2 MB). Both are muted. The full film opens from Drive in a dialog.
- Photos are in `site/assets/photos/`: Summit (steps, welcome, stage, hall, plus film stills), Athari Lake House retreat, BMEC-Philly, Statesmen arrival, panels, and founder headshots (self-hosted from nabme.org).
- The originals are in `../media-source/` (not deployed).

## Assets still to come
- Confirm who is in the two Drive founder photos (IMG_1451, IMG_6314) before using them.
- Partner and funder logo files (tiles currently show names).
- Impact report PDF (Athari) and the Summit sponsorship prospectus.

## Client round 2 (Oct 20, 2026)
- Summit 2027 details are hidden until release: no dates, countdown or calendar file. The banner reads "Summit 2027 · Info coming soon" with "See you at Howard University". Put Howard's logo at `site/assets/logos/howard.png` and it replaces the text automatically.
- Summit registration: paste the payment or registration link into `SUMMIT_REGISTER` in `build.py`, and "Register for the Summit" buttons appear in the Summit hero, banner and closing band.
- Employer payments are off for now: employer access and job posts are free during launch, with no plans, prices or checkout fields.
- Partner and funder logos: put a file named after the organization (for example `site/assets/logos/education-forward-dc.png`) and its tile shows the logo instead of the name.
- Role picker: `ROLES` in `build.py`, PreK through university plus "Other" with a text box. Used on Join and the Resume Bank.
- All inquiries go to info@nabme.org.
- New photos are from the client's Dropbox (2026 Summit), saved as `site/assets/photos/s26-*.jpg`; the originals are in `../media-source/dropbox-2026-10-20/`.

## Form storage (Oct 26, 2026)
- Every form posts to `site/api/submit.js` (a Vercel function), which saves it to Airtable, one table per form. Tables and columns are defined in `site/api/_schema.js`. Resumes, headshots and logos (up to 4 MB) upload straight into Airtable attachment columns.
- To connect: create the base, run `node scripts/setup-airtable.mjs` with `AIRTABLE_TOKEN` and `AIRTABLE_BASE_ID` set, then add those two variables to the Vercel project's environment and redeploy.
- Until those variables exist, the function answers 503 "not configured" and the forms show their success messages as before.
- Optional email alerts: set `RESEND_API_KEY`, `NOTIFY_FROM` and `NOTIFY_TO`.
- Every form includes a hidden spam-trap field. The Resume Bank video intro is a link field, not an upload.

## Launch (Oct 29, 2026)
- **Live at https://nabme.org.** The www address and the preview address forward there, and printed QR codes keep working through /register.
- **DNS moved from GoDaddy to Vercel** (nameservers ns1/ns2.vercel-dns.com), because GoDaddy's firewall locked the main record. Every email and Microsoft 365 record was copied over and checked. Manage DNS in Vercel from now on. The undo list is in `../launch/nabme-org-dns-before-launch.md`.
- **The domain itself stays registered at GoDaddy** (renews Oct 2027), along with NABME's Microsoft 365 email.
- **`LIVE = True` in build.py:** search indexing, sitemap.xml and Vercel Analytics are on.
