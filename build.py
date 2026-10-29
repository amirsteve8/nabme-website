#!/usr/bin/env python3
"""Builds the NABME site into ./site from the content below.

Run:  python3 build.py
Every page shares one header, footer and design system (site/styles.css, site/main.js).
Content follows "NABME.org Website Rebuild, Designer Handoff" (Oct 11, 2026).
Photos: swap files in PHOTOS once Rick's photos arrive; no page edits needed.
"""
import html, json, os, re, time
VER = str(int(time.time()))

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = {
    "a": {"name": "Movement", "logo": "official", "hero": "full", "cls": "v-a"},
    "b": {"name": "Heritage", "logo": "official", "hero": "full", "cls": "v-b"},
    "c": {"name": "Editorial", "logo": "seal", "hero": "split", "cls": "v-c"},
}
VKEY = os.environ.get("NABME_VARIANT", "a")
V = VARIANTS[VKEY]
OUT = os.path.join(HERE, "site" if VKEY == "a" else f"site-{VKEY}")

# ---------------------------------------------------------------- assets
PHOTOS = {  # slot -> (file, alt). NABME's own photos and film stills.
    "hero_poster": ("assets/photos/poster-steps.jpg", "Black male educators gathered on the steps at the inaugural Capital Summit"),
    "steps": ("assets/photos/summit-steps.jpg", "Black male educators in matching black shirts gathered on the steps at Howard University for the inaugural Capital Summit"),
    "summit_group": ("assets/photos/summit-group.jpg", "A group of Black male educators in The Black Man Can shirts at the Capital Summit"),
    "summit_group2": ("assets/photos/summit-group-2.jpg", "Summit attendees posing together in a classroom"),
    "summit_audience": ("assets/photos/summit-audience.jpg", "Educators listening during a Summit session"),
    "summit_audience2": ("assets/photos/summit-audience-2.jpg", "An attendee speaking from the audience at the Summit"),
    "summit_welcome": ("assets/photos/summit-welcome.jpg", "The welcome sign for the Black Male Educators Capitol Summit in a historic hall"),
    "summit_stage": ("assets/photos/summit-stage.jpg", "The Summit stage set with red chairs and portraits"),
    "summit_hall": ("assets/photos/summit-hall.jpg", "The Summit hall set for the opening session"),
    "summit_panel": ("assets/photos/summit-panel.jpg", "A panel conversation at the Summit"),
    "group": ("assets/photos/educators-group.jpg", "A group of Black male educators standing together at a NABME gathering"),
    "group2": ("assets/photos/educators-group-2.jpg", "NABME educators smiling together at a conference"),
    "bmec": ("assets/photos/bmec-philly.jpg", "Athari Fellows with educators at the Black Male Educators Convening in Philadelphia"),
    "stage": ("assets/photos/educators-stage.jpg", "Four Black male educators on a conference stage"),
    "panel": ("assets/photos/panel-stage.jpg", "Educators speaking on a panel in a historic hall"),
    "portrait": ("assets/photos/stage-portrait.jpg", "Educators on stage in a domed hall"),
    "arrival": ("assets/photos/statesmen-arrival.jpg", "Boys arriving at school through a line of Black men cheering them on"),
    "arrival2": ("assets/photos/statesmen-arrival-2.jpg", "A boy with a backpack walks past men welcoming students to school"),
    "athari_table": ("assets/photos/athari-table.jpg", "Athari Fellows talking around the dinner table at the Lake House retreat"),
    "athari_cooking": ("assets/photos/athari-cooking.jpg", "Athari Fellows cooking together during the Lake House cooking challenge"),
    "athari_kitchen": ("assets/photos/athari-kitchen.jpg", "Fellows gathered in the kitchen at the Lake House retreat"),
    "athari_lake": ("assets/photos/athari-lake.jpg", "Athari Fellows outdoors by the lake at the retreat"),
    "athari_lawn": ("assets/photos/athari-lawn.jpg", "Fellows gathered on the lawn during the Athari retreat"),
    "s26_kid": ("assets/photos/s26-84.jpg", "Black male educators in The Black Man Can shirts gathered around a young student at the 2026 Summit"),
    "s26_mentor": ("assets/photos/s26-86.jpg", "An educator welcomes a young man at the 2026 Summit at Howard University"),
    "s26_students": ("assets/photos/s26-22.jpg", "Student volunteers talking together at the 2026 Summit"),
    "s26_group": ("assets/photos/s26-101.jpg", "Seven Black male educators in The Black Man Can shirts standing together"),
    "s26_recruit": ("assets/photos/s26-127.jpg", "A school leader presenting to educators at a recruiting table"),
    "s26_table": ("assets/photos/s26-14.jpg", "Two Black male educators smiling at a round table"),
    "s26_aerial": ("assets/photos/s26-138.jpg", "Hundreds of Black male educators gathered outside Howard University, seen from above"),
    "s26_stage": ("assets/photos/s26-83.jpg", "Black male educators standing together on stage at the 2026 Summit"),
    "s26_class": ("assets/photos/s26-57.jpg", "Three Black male educators in a classroom"),
    "s26_seated": ("assets/photos/s26-10.jpg", "Educators seated together in the Summit auditorium"),
    "s26_crew": ("assets/photos/s26-28.jpg", "A group of educators posing together in a classroom"),
    "s26_speaker": ("assets/photos/s26-144.jpg", "A speaker addressing the 2026 Summit from the podium"),
    "s26_smiles": ("assets/photos/s26-102.jpg", "Three educators smiling together at the 2026 Summit"),
    "p_talk": ("assets/photos/s26-4.jpg", "Black male educators in conversation during a NABME session"),
    "p_trio": ("assets/photos/s26-135.jpg", "Three educators in The Black Man Can shirts smiling together"),
    "p_howard": ("assets/photos/s26-77.jpg", "Educators laughing together outside Howard University's Myrtilla Miner Auditorium"),
    "p_panel": ("assets/photos/s26-91.jpg", "A speaker and students on a panel at the 2026 Summit"),
    "p_audience": ("assets/photos/s26-142.jpg", "Educators in the audience at the 2026 Summit"),
    "p_onstage": ("assets/photos/s26-150.jpg", "Three educators on stage at the 2026 Summit"),
    "p_lineup": ("assets/photos/s26-81.jpg", "Black male educators standing together on the Summit stage"),
    "p_pair": ("assets/photos/s26-87.jpg", "Two educators smiling side by side"),
    "p_session": ("assets/photos/s26-b62.jpg", "Educators at desks during a breakout session"),
    "buggbey": ("assets/buggbey.jpg", "Jeff BuggBey, a NABME Fellow and fifth-grade math teacher"),
}
STRIP = ["s26_kid", "p_trio", "p_howard", "p_panel", "s26_mentor", "p_session", "p_lineup", "s26_smiles", "p_onstage", "s26_class"]
HERO_CLIPS = "assets/video/hero-summit.mp4, assets/video/hero-steps.mp4"
FULL_FILM = "https://drive.google.com/file/d/1vNOAQJWO7ptAhPpQZfE6aEyguL_9hYCb/preview"
REPORTS = {  # full decks, shared from NABME's Drive (viewable and downloadable)
    "nabme": ("NABME Organizational Impact Report", "2016–2026", "https://drive.google.com/file/d/1G_KosuzqYae6YSNjxFdz-NFuxhhUL29Q/view"),
    "athari": ("Athari Fellowship Impact Report", "2021–2026", "https://drive.google.com/file/d/1xdcULqt7dfvDP3TcTIQKLzPzAm3SngVu/view"),
    "summit": ("Black Male Educator Capital Summit Impact Report", "2026", "https://drive.google.com/file/d/1H1-17VrmlwpWDBQtUSE9XdSROzqbAvpx/view"),
}
PAYPAL = "https://www.paypal.com/donate/?hosted_button_id=R6A7JGUC8FP32"
SUMMIT_START = "2027-02-11T08:00:00-05:00"  # countdown target: day one of Summit 2027
SUMMIT_DATES = "February 11–13, 2027"
SUMMIT_DAYS = [  # (weekday, date, event, description); more events will be announced later
    ("Thursday", "Feb 11", "Capitol Hill Fly-In", "Black male educators take their voice to policymakers on Capitol Hill."),
    ("Friday", "Feb 12", "Black Boy Hackathon", "Students and educators build solutions together."),
    ("Saturday", "Feb 13", "Black Male Educator Capital Summit", "A full day of keynotes, breakouts and brotherhood at Howard University."),
]
SUMMIT_REG_OPEN = False  # True turns Summit registration (and its $100 PayPal checkout) back on
CFP_DEADLINE = "Monday, December 14, 2026"
SUMMIT_FEE = "$100"
SUMMIT_PAY_URL = "https://www.paypal.com/ncp/payment/NHRTEGF92R54N"  # PayPal payment link for the $100 registration; when set, registrants continue to it after the form
HOWARD_LOGO = "assets/logos/howard.png"  # shown in the Summit banner when the file exists

SOCIAL = [
    ("Facebook", "https://www.facebook.com/nabmeinc", "facebook-logo"),
    ("Facebook community group", "https://www.facebook.com/groups/751356851659519", "users-three"),
    ("Instagram", "https://www.instagram.com/nabmeinc", "instagram-logo"),
    ("LinkedIn", "https://www.linkedin.com/in/nabme-inc-50474a26a", "linkedin-logo"),
]

NAV = [
    ("Who We Are", "who", [("Mission & Values", "/mission", "Mission, vision and core beliefs"), ("Founders", "/founders", "The people behind the mission"), ("Our Impact", "/impact", "Impact reports, 2016–2026")]),
    ("Programs", "programs", [("Athari Fellowship", "/athari", "Two-year leadership program"), ("Capital Summit", "/summit", "Feb. 11–13, 2027 · Washington, D.C."), ("Call for Proposals", "/summit/proposals", "Present at the 2027 Summit · due Dec. 14")]),
    ("Careers", "careers", [("Talent Portal", "/talent", "One portal, three ways in"), ("Resume Bank", "/resume-bank", "Free educator profile"), ("Employer Access", "/employers", "Search the talent"), ("Job Board", "/jobs", "Open positions")]),
    ("NABME News", "news", [("Blog", "/blog", "NABME Voices"), ("Media", "/media", "Coverage of NABME"), ("Events", "/events", "Upcoming and past"), ("NABME Live", "/live", "The movement, in real time")]),
    ("Partners", "partners", [("Partners & Funders", "/partners", "Who we build alongside and who supports the work")]),
    ("Join Us", "join", [("Join NABME", "/join", "Become part of the movement"), ("Contact Us", "/contact", "Questions and inquiries")]),
]


def e(s):
    return html.escape(s, quote=True)


def ic(name, extra=""):
    return f'<i class="ph ph-{name}{(" " + extra) if extra else ""}" aria-hidden="true"></i>'


ARROW = ic("arrow-up-right")
CHECK = ic("check")
EXT = ' target="_blank" rel="noopener"'


def img(slot, cls="", eager=False, pos=None):
    f, alt = PHOTOS[slot]
    style = f' style="object-position:{pos}"' if pos else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="/{f}" alt="{e(alt)}" {load} decoding="async"{style}{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>'


def slide_strip(slots, label, pos="center 30%"):
    # Photo strip that glides sideways; the second copy makes the loop seamless and is hidden from screen readers
    figs = "".join(f'<figure>{img(x, pos=pos)}</figure>' for x in slots)
    return f'<section class="strip strip--slide" aria-label="{e(label)}" data-strip><div class="strip__track"><div class="strip__set">{figs}</div><div class="strip__set" aria-hidden="true">{figs}</div></div></section>'


def eyebrow(t):
    return f'<p class="eyebrow">{t}</p>'


def btn(label, href, kind="red", icon=True, extra=""):
    return f'<a class="btn btn--{kind}" href="{href}"{extra}>{label}{(" " + ARROW) if icon else ""}</a>'


# ---------------------------------------------------------------- chrome
def brand_html(footer=False):
    if V["logo"] == "official":
        return '<a class="brand brand--official" href="/" aria-label="NABME, National Association of Black Male Educators, home"><img src="/assets/nabme-logo-official.png" alt="" width="160" height="89"></a>'
    seal = "seal-white" if footer else "seal"
    return f'<a class="brand" href="/" aria-label="NABME home"><img src="/assets/{seal}.svg" alt="" width="50" height="50"><span>NABME</span></a>'


def header(active):
    items = []
    for label, key, links in NAV:
        sub = "".join(f'<a href="{h}">{e(t)}<small>{e(d)}</small></a>' for t, h, d in links)
        cls = "nav__item is-active" if key == active else "nav__item"
        items.append(f'<li class="{cls}"><button class="nav__top" type="button" aria-expanded="false" aria-haspopup="true">{e(label)} {ic("caret-down")}</button><div class="nav__menu">{sub}</div></li>')
    mob = "".join(
        f'<details><summary>{e(label)} {ic("caret-down")}</summary>' + "".join(f'<a href="{h}">{e(t)}</a>' for t, h, _ in links) + "</details>"
        for label, key, links in NAV
    )
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap utility__inner"><span>Partnership · Protection · Proximity · Practice</span><nav aria-label="Utility"><a href="/donate">Donate</a><a href="/careers">Careers</a><a href="/events">Events</a><a href="/contact">Contact</a></nav></div></div>
<header class="header"><div class="wrap header__inner">
  {brand_html()}
  <nav aria-label="Primary"><ul class="nav" role="list">{"".join(items)}</ul></nav>
  <div class="header__cta"><a class="btn btn--outline btn--sm" href="/join">Join NABME</a><a class="btn btn--red btn--sm" href="/donate">Donate</a><button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mnav"><span></span><span></span></button></div>
</div></header>
<div class="mnav" id="mnav" aria-hidden="true">{mob}<div class="btn-row"><a class="btn btn--red" href="/donate">Donate</a><a class="btn btn--outline" href="/join">Join NABME</a></div></div>'''


def signup_form(dark=False, compact=False, source="footer"):
    role = '<select name="role" aria-label="I am a (optional)"><option value="">I am a… (optional)</option><option>Educator</option><option>School leader</option><option>Employer</option><option>Funder</option></select>'
    return f'''<form class="inline-form" data-inline data-source="{source}"><label class="sr" for="em-{source}">Email address</label><input id="em-{source}" type="email" name="email" placeholder="you@school.org" autocomplete="email" required>{"" if compact else role}<button class="btn btn--red" type="submit">Stay updated</button></form><p class="inline-msg" aria-live="polite"></p>'''


def footer():
    cols = "".join(
        f'<nav aria-label="{e(label)}"><h2>{e(label)}</h2>' + "".join(f'<a href="{h}">{e(t)}</a>' for t, h, _ in links) + "</nav>"
        for label, key, links in NAV[:4]
    )
    socials = "".join(f'<a href="{u}"{EXT} aria-label="{e(n)}">{ic(i)}</a>' for n, u, i in SOCIAL)
    return f'''<footer class="footer on-dark"><div class="wrap">
  <div class="footer__top">
    <div>
      {brand_html(True)}
      <p class="footer__tag">Partnership, Protection, Proximity, and Practice.</p>
      <div class="footer__signup"><label for="em-footer">Get NABME news in your inbox</label>{signup_form(True, source="footer")}</div>
      <div class="socials" aria-label="NABME on social media">{socials}</div>
    </div>
    <div class="footer__cols">{cols}</div>
  </div>
  <div class="footer__bottom"><span>© <span data-year>2026</span> National Association of Black Male Educators</span><span><a href="/partners">Partners</a> · <a href="/join">Join</a> · <a href="/contact">Contact</a> · <a href="/live">NABME Live</a> · <a href="/nominate">Nominate an educator</a></span><button class="motion-toggle" type="button" aria-pressed="false">Pause motion</button></div>
</div></footer>
<dialog id="newsletter-pop" class="pop" aria-labelledby="pop-title"><button class="dialog-close" type="button" data-close aria-label="Close">{ic("x")}</button><p class="eyebrow">Stay updated</p><h2 id="pop-title">The movement, in your inbox.</h2><p>Summit news, Athari updates, new jobs for Black male educators. One email a month.</p>{signup_form(source="pop")}</dialog>'''


def page(path, title, desc, body, active="", dark_head=False):
    slug = path.strip("/") or "index"
    full = f"{title} | NABME" if path != "/" else "NABME | National Association of Black Male Educators"
    html_doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f7f6f2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NABME">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="/assets/photos/s26-138.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/seal.svg" type="image/svg+xml">
<link rel="preload" href="/assets/InterVariable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="/styles.css?v={VER}">
</head>
<body class="{V["cls"]}">
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/main.js?v={VER}" defer></script>
</body>
</html>
'''
    html_doc = re.sub(r"(?<=\d)–(?=\d)", "\u2060–\u2060", html_doc)  # word joiners: date ranges never wrap at the dash
    target = os.path.join(OUT, "index.html" if slug == "index" else f"{slug}.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return target


def closing(title, text, buttons):
    return f'''<section class="band-red closing" aria-label="Next step"><div class="wrap"><div><h2>{title}</h2>{f"<p>{text}</p>" if text else ""}</div><div class="btn-row">{buttons}</div></div></section>'''


def countdown_block(primary=None, buttons=True):
    primary = btn("Get notified", "#notify", "red") if primary is None else primary
    row = f'<div class="btn-row">{primary}{btn("Become a sponsor", "/summit#sponsor", "ghost", False)}</div>' if buttons else ""
    return f'''<div class="countdown-wrap"><div class="countdown" data-countdown="{SUMMIT_START}" role="timer" aria-label="Countdown to Summit 2027, which starts February 11, 2027"><div><b data-d>–</b><span>Days</span></div><div><b data-h>–</b><span>Hours</span></div><div><b data-m>–</b><span>Minutes</span></div><div><b data-s>–</b><span>Seconds</span></div></div>{row}</div>'''


def summit_days(heading_tag="h3"):
    cards = "".join(f'<article class="day{" day--red" if i == 2 else ""}"><p class="day__when">{w} · {d}</p><{heading_tag}>{t}</{heading_tag}><p>{x}</p></article>' for i, (w, d, t, x) in enumerate(SUMMIT_DAYS))
    return f'<div class="days">{cards}</div><p class="days-note">More events will be announced soon.</p>'


def summit_announce():
    return f'''<section class="section band-dark summit-announce" aria-labelledby="sa-h"><div class="wrap">
  <div class="section-head section-head--row"><div><p class="eyebrow">Summit 2027 · Save the dates</p><h2 id="sa-h" class="h2">{SUMMIT_DATES} <span class="red">·</span> Washington, D.C.</h2><p class="lede" style="margin-top:12px">Three days. One movement. The Black Male Educator Capital Summit grows into a full week of action.</p></div>{countdown_block(summit_register_btn("red"))}</div>
  {summit_days()}
</div></section>'''


def howard_mark():
    if os.path.exists(os.path.join(HERE, "site", HOWARD_LOGO)):
        return f'<img class="howard-mark" src="/{HOWARD_LOGO}" alt="Howard University">'
    return '<span class="howard-mark howard-mark--text">Howard University</span>'


def summit_register_btn(kind="light"):
    return btn("Register now", "/summit/register", kind) if SUMMIT_REG_OPEN else btn("Submit a proposal", "/summit/proposals", kind)


def summit_tabs(active):
    tabs = [("overview", "Overview", "/summit"), ("mission", "Mission, Strands & Goals", "/summit/mission"), ("proposals", "Call for Proposals", "/summit/proposals")]
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if k == active else ""}>{t}</a>' for k, t, h in tabs)
    return f'<nav class="subnav" aria-label="Summit sections"><div class="wrap">{links}</div></nav>'


def summit_banner(heading_tag="h2"):
    return f'''<div class="summit-banner summit-banner--soon" id="register"><div><p class="eyebrow">Summit 2027 · {SUMMIT_DATES}</p><{heading_tag}>The Black Male Educator <span>Capital Summit</span> returns.</{heading_tag}><p class="lede" style="margin-top:14px">Thursday: Capitol Hill Fly-In. Friday: Black Boy Hackathon. Saturday: the Summit at Howard University.</p><p class="summit-fee">{f"<b>Registration is open.</b> {SUMMIT_FEE} per educator." if SUMMIT_REG_OPEN else f"<b>Call for proposals is open</b> through {CFP_DEADLINE}. Registration opens soon."}</p><div class="btn-row" style="margin-top:20px">{summit_register_btn("red")}</div></div><div class="summit-side"><div class="howard"><p>See you at</p>{howard_mark()}</div><div class="qr-card"><img src="/assets/qr-register.svg" alt="QR code to register for the Summit" width="120" height="120"><p><b>{"Scan to register" if SUMMIT_REG_OPEN else "Scan for Summit details"}</b>Point your phone's camera at the code.</p></div></div></div>'''


def impact_band():
    return f'''<section class="band-dark impact wedge section" aria-labelledby="impact-h"><div class="wrap">
  <p class="eyebrow">A movement, not a moment</p>
  <h2 id="impact-h">Since 2016, NABME has built the pipeline of Black male educators our children deserve.</h2>
  <div class="stats">
    <div class="stat"><span class="stat__num" data-count="50000" data-suffix="+">50,000+</span><span class="stat__label">Educators reached since 2016</span></div>
    <div class="stat"><span class="stat__num is-accent" data-count="310" data-suffix="+">310+</span><span class="stat__label">Educators registered or waitlisted for the 2026 Summit</span></div>
    <div class="stat"><span class="stat__num" data-count="20" data-suffix="+">20+</span><span class="stat__label">States represented</span></div>
    <div class="stat"><span class="stat__num is-accent" data-count="100" data-suffix="%">100%</span><span class="stat__label">Athari Fellows retained in education (Cohorts 1 and 2)</span></div>
  </div>
  <p style="margin-top:28px"><a class="text-link" href="/impact" style="color:#fff">See our impact reports {ARROW}</a></p>
</div></section>'''


def why_matters():
    return f'''<section class="band-dark wedge wedge--top section" aria-labelledby="why-h"><div class="wrap">
  <p class="eyebrow">Why this work matters</p>
  <h2 id="why-h" class="h2" style="max-width:20ch">Black boys need to see Black men at the front of the class.</h2>
  <div class="stats stats--3">
    <div class="stat"><span class="stat__num is-accent" data-count="1.3" data-dec="1" data-suffix="%">1.3%</span><span class="stat__label">of U.S. public school teachers are Black men.</span><span class="stat__src"><a href="https://usafacts.org/articles/how-many-black-male-teachers-are-there-in-the-us/"{EXT}>NCES via USAFacts, 2020–21</a></span></div>
    <div class="stat"><span class="stat__num" data-count="39" data-suffix="%">39%</span><span class="stat__label">lower dropout risk for very low-income Black boys who had one Black teacher in grades 3–5.</span><span class="stat__src"><a href="https://hub.jhu.edu/2017/04/05/black-teachers-improve-student-graduation-college-access/"{EXT}>Gershenson et al., 2017</a></span></div>
    <div class="stat"><span class="stat__num is-accent" data-count="13" data-suffix="%">13%</span><span class="stat__label">more likely to graduate high school when Black students have a Black teacher in K–3.</span><span class="stat__src"><a href="https://www.nber.org/papers/w25254"{EXT}>NBER w25254, 2018</a></span></div>
  </div>
</div></section>'''


def logo_file(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    for ext in ("svg", "png", "jpg", "webp"):
        if os.path.exists(os.path.join(HERE, "site", "assets", "logos", f"{slug}.{ext}")):
            return f"/assets/logos/{slug}.{ext}"
    return ""


LOGO_DARK = set()  # logos made for dark backgrounds
LOGO_ICON_ONLY = {"Monument Academy PCS"}  # logo files without the name: show the name under the icon


def logo_tile(name, url, note="", lg=False):
    cls = "logo-tile logo-tile--lg" if lg else "logo-tile"
    if name in LOGO_DARK: cls += " logo-tile--dark"
    src = logo_file(name)
    inner = f'<img src="{src}" alt="{e(name)}" loading="lazy">' if src else e(name)
    if src and name in LOGO_ICON_ONLY: inner += f'<b class="logo-tile__name">{e(name)}</b>'
    return f'<a class="{cls}{" logo-tile--img" if src else ""}" href="{url}"{EXT}><span>{inner}{f"<small>{e(note)}</small>" if note else ""}</span></a>'


PARTNERS = [
    ("Education Forward DC", "https://edforwarddc.org"),
    ("Center for Black Educator Development", "https://thecenterblacked.org"),
    ("My Brother's Keeper DC", "https://dc.gov/mayor/my-brothers-keeper-dc"),
    ("Statesmen College Preparatory Academy for Boys", "https://statesmenboys.org"),
    ("CitySchools Collaborative", "https://cityschoolscollab.org"),
    ("City Teaching Alliance", "https://cityteachingalliance.org"),
    ("City Year Washington, DC", "https://www.cityyear.org/dc"),
    ("He Is Me Institute", "https://heisme.org"),
    ("Innovation for Equity", "https://innovationequity.org"),
]
FUNDERS = [
    ("NewSchools Venture Fund", "https://www.newschools.org"),
    ("Education Forward DC", "https://edforwarddc.org"),
    ("The Annie E. Casey Foundation", "https://www.aecf.org"),
    ("Executives' Alliance Fund", "https://schottfoundation.org/our-work/executive-alliance-boys-men-color/"),
]
SUMMIT_FUNDERS = [
    ("Education Forward DC", "https://edforwarddc.org"),
    ("My Brother's Keeper DC", "https://dc.gov/mayor/my-brothers-keeper-dc"),
    ("Legends Charter School", "https://legendsschools.org"),
    ("The Social Justice School", "https://thesocialjusticeschool.org"),
    ("Thurgood Marshall Academy PCS", "https://www.thurgoodmarshallacademy.org"),
    ("Washington Leadership Academy PCS", "https://www.washingtonleadershipacademy.org"),
    ("Friendship Public Charter School", "https://www.friendshipschools.org"),
    ("E.L. Haynes PCS", "https://www.elhaynes.org"),
    ("DC Prep", "https://www.dcprep.org"),
    ("Monument Academy PCS", "https://www.monumentacademy.org"),
    ("Center City PCS", "https://www.centercitypcs.org"),
    ("Howard University Middle School of Mathematics & Science", "https://hu-ms2.org"),
]

QUOTES = [
    ("My leadership evolution has been about learning to balance care with courage. Athari has helped me become more grounded, more reflective and more courageous.", "Cohort 2 Fellow · End-of-year survey", ""),
    ("It is excellent to know that I am not having an isolated experience, and that I can brainstorm with a group of Black men who are accomplished inside of urban education.", "Athari Fellow, Cohort 2 · Program evaluation", "qcard--paper"),
    ("Giving young professionals the rare opportunity to stand shoulder to shoulder with some of the most accomplished people in this space was genuinely life-changing.", "Athari Fellow · April 2026 program evaluation", "qcard--red"),
]


def quote_carousel(label="Fellow voices"):
    slides = "".join(
        f'<div class="qslide" role="group" aria-roledescription="slide" aria-label="Quote {i + 1} of {len(QUOTES)}"><figure class="qcard {cls}"><div class="qmark" aria-hidden="true">“</div><blockquote>{e(q)}</blockquote><figcaption><cite>{e(c)}</cite></figcaption></figure></div>'
        for i, (q, c, cls) in enumerate(QUOTES)
    )
    return f'''<div class="qcarousel" data-carousel aria-roledescription="carousel" aria-label="{e(label)}"><div class="qtrack">{slides}</div><div class="qcontrols"><button class="round-btn" type="button" data-prev aria-label="Previous quote">{ic("arrow-left")}</button><button class="round-btn" type="button" data-next aria-label="Next quote">{ic("arrow-right")}</button><div class="qdots"></div></div></div>'''


ROLES = {
    "Early childhood (PreK)": ["PreK lead teacher", "PreK assistant teacher", "Early childhood aide", "Childcare / Head Start staff"],
    "Classroom (K–12)": ["Elementary teacher", "Middle school teacher", "High school teacher", "Special education teacher", "ESL / ELL teacher", "Arts, music or PE teacher", "CTE / vocational teacher", "Substitute teacher", "Teacher resident / student teacher"],
    "Classroom support": ["Paraprofessional / instructional aide", "Teacher's aide / assistant", "Behavior technician / interventionist", "Tutor", "Interventionist / reading or math specialist"],
    "Student support": ["School counselor", "School social worker", "School psychologist", "Dean of students / culture", "Restorative practices coordinator", "Athletic director / coach", "Mentor / youth development"],
    "School leadership": ["Instructional coach", "Department chair / grade-level lead", "Assistant principal", "Principal / head of school", "Director of operations"],
    "District / central office": ["Superintendent / deputy", "Chief / central office leader", "Curriculum & instruction specialist", "Program director / manager", "HR / talent / recruitment"],
    "Higher education": ["Professor / lecturer", "Adjunct faculty", "College administrator", "Student affairs / advising", "College or graduate student", "Aspiring educator"],
    "Beyond schools": ["Education nonprofit staff", "Policy / advocacy", "Education researcher", "Ed-tech", "Retired educator", "Ally / partner"],
}


def role_field(label="Your role", name="role", required=True):
    req = " required" if required else ""
    groups = "".join(f'<optgroup label="{e(g)}">' + "".join(f"<option>{e(o)}</option>" for o in opts) + "</optgroup>" for g, opts in ROLES.items())
    return (f'<div class="field"><label for="f-{name}">{e(label)}</label><select id="f-{name}" name="{name}" data-other{req}><option value="">Choose your role</option>{groups}<option value="Other">Other (type your role)</option></select><span class="err">This field is required.</span></div>'
            f'<div class="field" data-other-for="f-{name}" hidden><label for="f-{name}-other">Type your role</label><input id="f-{name}-other" name="{name}_other" type="text" placeholder="For example: Family engagement coordinator"><span class="err">Tell us your role.</span></div>')


def field(label, name, typ="text", required=False, hint="", full=False, options=None, placeholder="", auto="", attrs=""):
    req = " required" if required else ""
    star = "" if required else ' <span class="hint">(optional)</span>'
    fid = "f-" + name
    hint_html = f'<span class="hint" id="{fid}-h">{hint}</span>' if hint else ""
    desc = f' aria-describedby="{fid}-h"' if hint else ""
    auto_attr = f' autocomplete="{auto}"' if auto else ""
    if options is not None:
        opts = '<option value="">Choose one</option>' + "".join(f"<option>{e(o)}</option>" for o in options)
        control = f'<select id="{fid}" name="{name}"{req}{desc}>{opts}</select>'
    elif typ == "textarea":
        control = f'<textarea id="{fid}" name="{name}"{req}{desc}{attrs} placeholder="{e(placeholder)}"></textarea>'
    else:
        control = f'<input id="{fid}" name="{name}" type="{typ}"{req}{desc}{auto_attr} placeholder="{e(placeholder)}">'
    err = {"email": "Enter a valid email address.", "url": "Enter a full link starting with https://"}.get(typ, "This field is required.")
    return f'<div class="field{" field--full" if full else ""}"><label for="{fid}">{e(label)}{star}</label>{hint_html}{control}<span class="err">{err}</span></div>'


def checks(legend, name, options, full=True):
    boxes = "".join(f'<label class="check"><input type="checkbox" name="{name}" value="{e(o)}"> {e(o)}</label>' for o in options)
    return f'<fieldset class="field{" field--full" if full else ""}"><legend>{e(legend)} <span class="hint">(choose any)</span></legend><div class="checks">{boxes}</div></fieldset>'


def success(title, text, actions=""):
    return f'<div class="success" aria-live="polite">{ic("check-circle", "big")}<h3>{title}</h3><p>{text}</p>{f"<div class=btn-row>{actions}</div>" if actions else ""}</div>'


# ================================================================ PAGES
NEWS = [
    ("Dear Black Men: We Still Need You to Teach", "Word In Black (Sharif El-Mekki)", "Sep. 30, 2026", "Op-ed", "A decade after his first call, El-Mekki argues schools must prepare and keep Black men, not just recruit them.", "https://wordinblack.com/2026/09/dear-black-men-we-still-need-you-to-teach/"),
    ("Why America's Schools Need More Black Male Educators — Like Me", "The 74", "Feb. 25, 2026", "Op-ed", "A Black male instructional leader makes the case for HBCU pipelines, retention and an end to “disciplinarian” typecasting.", "https://www.the74million.org/article/why-americas-schools-need-more-black-male-educators-like-me/"),
    ("“Power to the Pupil”: Black educators gather in Philly to discuss the future of teaching", "WHYY", "Nov. 25, 2025", "News", "More than 1,000 educators at the Black Men in Education Convening tackle the shortage, burnout and AI.", "https://whyy.org/articles/black-men-in-education-convening-2025/"),
    ("Why so few Black men teach in American classrooms", "PBS NewsHour", "Mar. 26, 2023", "Video", "Call Me MISTER's Mark Joseph on why Black boys disconnect from school and how cohorts keep Black men teaching.", "https://www.pbs.org/newshour/show/why-so-few-black-men-teach-in-american-classrooms"),
    ("Few Black male teachers are in US classrooms. These programs are changing that.", "ABC News / Good Morning America", "", "Article + video", "Three programs, including NABME partner He Is Me Institute, that are growing the number of Black male teachers.", "https://www.goodmorningamerica.com/living/story/black-male-teachers-us-classrooms-programs-changing-96821522"),
]


def news_cards(items, lead=True):
    out = []
    for i, (t, outlet, date, typ, blurb, url) in enumerate(items):
        is_video = "Video" in typ
        tag = f'<span class="tag{" tag--red" if is_video else ""}">{ic("play-circle") + " " if is_video else ""}{e(typ)}</span>'
        meta = f'<div class="story__meta">{tag}<span>{e(outlet)}{(" · " + e(date)) if date else ""}</span></div>'
        verb = "Watch" if is_video else "Read"
        cls = "story story--lead" if (lead and i == 0) else "story"
        out.append(f'<a class="{cls}" href="{url}"{EXT}>{meta}<h3>{e(t)}</h3><p>{e(blurb)}</p><span class="more">{verb} {ARROW}<span class="sr">(opens in a new tab)</span></span></a>')
    return "".join(out)


IG_HOME = ["DcJOCf6joPm", "DbG4At8IH9a", "DVQznJMDdid"]
IG_WALL = ["DcJOCf6joPm", "DbG4At8IH9a", "DVQznJMDdid", "DaIwL-jjvvd", "Da5Qkv4DhGA", "DY0rwAIDEAi", "DVFA6htDvnA", "DVCvKt2jhFh", "DVBXKFADjTO"]


def ig_grid(ids):
    # Post photos only (no likes or comments); each one opens the post on Instagram
    cells = "".join(
        f'<a class="ig" href="https://www.instagram.com/p/{i}/"{EXT} aria-label="Open this post on Instagram">'
        f'<img src="/assets/ig/{i}.jpg" alt="NABME Instagram post" loading="lazy" decoding="async">'
        f'<span class="ig__badge">{ic("instagram-logo")}</span></a>'
        for i in ids
    )
    return f'<div class="ig-grid">{cells}</div>'


def build_home():
    doors = [
        ("Aspiring educators", "Thinking about teaching?", "Explore paths into the classroom and the support that keeps you there.", "Explore careers", "/careers"),
        ("Current educators and leaders", "Grow where you are.", "Join a brotherhood of Black male educators and submit your interest in the Athari Fellowship.", "Join NABME", "/join"),
        ("Schools hiring", "Find your next great hire.", "Search NABME's Resume Bank and post positions where Black male educators look.", "Visit the Talent Portal", "/talent"),
        ("Funders and partners", "Invest in the pipeline.", "Stand with the organizations and funders powering this work.", "Partner with us", "/partners"),
    ]
    door_html = "".join(f'<div class="door"><p class="door__who">{a}</p><h3>{b}</h3><p>{c}</p>{btn(d, h, "outline")}</div>' for a, b, c, d, h in doors)
    partners = "".join(logo_tile(n, u) for n, u in PARTNERS[:6] + FUNDERS[:1] + FUNDERS[2:])
    body = f'''
<section class="vhero{" vhero--split" if V["hero"] == "split" else ""}" aria-labelledby="hero-h">
  <div class="vhero__media">{img("hero_poster", eager=True)}<video muted playsinline preload="metadata" aria-hidden="true" data-clips="{HERO_CLIPS}" poster="/{PHOTOS["hero_poster"][0]}"></video></div>
  <div class="vhero__controls"><span class="vhero__caption">The inaugural Black Male Educator Capital Summit · Washington, D.C.</span><button class="icon-btn" type="button" data-video-toggle aria-label="Pause background video">{ic("pause")}</button></div>
  <div class="vhero__inner">
    <h1 id="hero-h">Answer the call. <span class="red">Change the world.</span></h1>
    <p class="vhero__sub">NABME recruits, develops and supports Black male educators, because our children deserve to see themselves at the front of the class.</p>
    <p class="vhero__quote">“Education is the most powerful weapon which you can use to change the world.” Nelson Mandela</p>
    <div class="btn-row">{btn("Join NABME", "/join")}<button class="btn btn--ghost" type="button" data-film>{ic("play")} Watch the 2026 Summit recap</button></div>
  </div>
</section>

{summit_announce()}

<section class="tiles" aria-label="Get involved">
  <a class="tile" href="/join"><span class="tile__label">Join the movement</span><h2>Become a member {ARROW}</h2><p>Connect with Black male educators across the country.</p></a>
  <a class="tile" href="/donate"><span class="tile__label">Support the work</span><h2>Give to NABME {ARROW}</h2><p>Put more Black men at the front of the classroom.</p></a>
  <div class="tile tile--signup"><span class="tile__label">Stay updated</span><h2>Get NABME news</h2>{signup_form(compact=True, source="tile")}</div>
</section>

{slide_strip(STRIP, "NABME educators, Fellows and Summit moments")}

{impact_band()}

<section class="section"><div class="wrap split">
  <div>{eyebrow("Our mission")}<h2 class="h2">More educators. More possibility.</h2></div>
  <div><p class="statement">Our mission is to dramatically increase the number of marginalized children who succeed by dramatically increasing the number of highly effective Black and Brown male teachers and leaders who positively impact them.</p><p style="margin-top:28px"><a class="text-link text-link--red" href="/mission">Our mission &amp; values {ARROW}</a></p></div>
</div></section>

<section class="section band-stone" aria-labelledby="prog-h"><div class="wrap">
  <div class="section-head">{eyebrow("Our programs")}<h2 id="prog-h" class="h2">Where the pipeline gets built.</h2></div>
  <div class="programs">
    <a class="program" href="/athari">{img("p_talk", pos="center 30%")}<div class="program__body"><span class="program__kicker">Flagship leadership program</span><h3>The Athari Fellowship</h3><p class="program__proof">31 Fellows. 100% retained. 83% in leadership.</p><span class="more">Explore the Fellowship {ARROW}</span></div></a>
    <a class="program" href="/summit">{img("s26_aerial", pos="center 45%")}<div class="program__body"><span class="program__kicker">Summit 2027 · {SUMMIT_DATES}</span><h3>The Black Male Educator Capital Summit</h3><p class="program__proof">See you at Howard University</p><span class="more">Relive the 2026 Summit {ARROW}</span></div></a>
  </div>
</div></section>

<section class="section" aria-labelledby="serve-h"><div class="wrap">
  <div class="section-head">{eyebrow("Who we serve")}<h2 id="serve-h" class="h2">There is a door for you.</h2></div>
  <div class="doors">{door_html}</div>
</div></section>

<section class="section band-stone" aria-labelledby="news-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("News in education")}<h2 id="news-h" class="h2">The national conversation.</h2><p class="lede" style="margin-top:14px">The national conversation about Black men in the classroom, and why it matters for every child.</p></div><a class="text-link" href="/media">NABME in the media {ARROW}</a></div>
  <div class="news-grid">{news_cards(NEWS)}</div>
</div></section>

<section class="section" aria-labelledby="live-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("NABME Live")}<h2 id="live-h" class="h2">The movement, in real time.</h2><p class="lede" style="margin-top:14px">See what our educators, Fellows and partners are sharing. Tag @nabmeinc and use #NABME to join the conversation.</p></div><div class="btn-row">{btn("Follow on Instagram", "https://www.instagram.com/nabmeinc", "outline", True, EXT)}{btn("Follow on Facebook", "https://www.facebook.com/nabmeinc", "outline", True, EXT)}</div></div>
  {ig_grid(IG_HOME)}
  <p style="margin-top:22px"><a class="text-link text-link--red" href="/live">See the full wall {ARROW}</a></p>
</div></section>

<section class="section" style="padding-top:0" aria-label="Capital Summit"><div class="wrap">{summit_banner()}</div></section>

<section class="section band-stone" aria-labelledby="partners-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Partners and funders")}<h2 id="partners-h" class="h2">This work takes all of us.</h2></div><a class="text-link" href="/partners">All partners and funders {ARROW}</a></div>
  <div class="logo-row">{partners}</div>
</div></section>

{closing("Step to the front of the class.", "Join a national network of Black and Brown male educators. Get mentorship, career support and a community that has your back.", btn("Join NABME", "/join", "light"))}

<dialog id="film" aria-label="NABME film: The Black Male Educator Summit"><div class="dialog-bar"><span>The Black Male Educator Summit</span><button class="dialog-close" type="button" data-close aria-label="Close film">{ic("x")}</button></div><div class="film"><iframe title="The Black Male Educator Summit film" data-src="{FULL_FILM}" src="about:blank" allow="autoplay; fullscreen" allowfullscreen></iframe></div></dialog>
'''
    page("/", "Home", "The National Association of Black Male Educators recruits, develops and supports Black male teachers and leaders, so every child can see himself at the front of the class.", body)


def build_mission():
    vision = [
        ("Teachers in place", "An abundance of classically trained Black and Brown men who have secured positions in education."),
        ("Leaders at the helm", "An abundance of highly-effective Black and Brown male leaders leading high performing schools and school districts across the nation."),
        ("The next generation", "An emerging cadre of Black and Brown male high school students entering college with a focus on education and the goal of becoming educators."),
        ("Voices in policy", "An abundance of educated and knowledgeable Black and Brown men directly impacting the shifts in policies within education needed to ensure equity for all children."),
        ("Closing the gap", "An abundance of influential Black and Brown male educational leaders directly contributing to the success and achievement of Black and Brown men in education, closing the equity and achievement gap for marginalized children."),
    ]
    vc = "".join(f'<article class="card card--bar{"-red" if i % 2 == 0 else ""}"><span class="num">{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(vision))
    beliefs = [
        ("Service", "We are dedicated to the service of education as a civil right; not just as a profession."),
        ("Passion", "We are passionate about the work of education and seek to equip educators with the necessary tools to ensure every student receives the quality of education they deserve."),
        ("Excellence", "We are committed to excellence in every sense of the word. We want to develop life-changing educators through academic excellence, professional excellence, and excellence in teaching and learning."),
    ]
    bc = "".join(f'<article class="card card--side{"-red" if i != 1 else ""}"><h3 style="font-size:1.9rem">{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(beliefs))
    body = f'''
<section class="phero phero--split"><div class="wrap">
  <div>{eyebrow("Who we are")}<h1>Mission, Vision and Core <span class="red">Beliefs</span></h1><p class="lede">NABME exists to put more highly effective Black and Brown men in front of the children who need them most.</p></div>
  <div class="phero__photo">{img("p_lineup", eager=True)}</div>
</div></section>

<section class="section"><div class="wrap split">
  <div>{eyebrow("NABME mission")}</div>
  <p class="statement" style="font-size:clamp(1.6rem,3vw,2.5rem)">The mission of the National Association of Black Male Educators is to dramatically increase the number of <span class="red">marginalized children who succeed</span> by dramatically increasing the number of highly effective Black and Brown male teachers and leaders who positively impact them.</p>
</div></section>

<section class="mosaic" aria-label="NABME educators">{"".join(f'<figure>{img(x)}</figure>' for x in ["s26_aerial", "s26_stage", "s26_class", "s26_speaker", "s26_crew"])}</section>

<section class="section band-stone" aria-labelledby="vision-h"><div class="wrap">
  <div class="section-head">{eyebrow("NABME vision")}<h2 id="vision-h" class="h2">By <span class="red">2035</span>, NABME will be widely known for creating:</h2></div>
  <div class="vision-cards">{vc}</div>
</div></section>

<section class="section" aria-labelledby="beliefs-h"><div class="wrap">
  <div class="section-head">{eyebrow("Core beliefs")}<h2 id="beliefs-h" class="h2">Three beliefs. One goal.</h2><p class="lede">The National Association of Black Male Educators believes deeply in the success of Black and Brown men in education to improve the outcomes for all children. We aim to do this through 3 core beliefs:</p></div>
  <div class="grid-3">{bc}</div>
</div></section>

{pillars_section("Our four pillars", "Partnership. Protection. Proximity. Practice.")}

{closing("Stand with the men at the front of the class.", "", btn("Join NABME", "/join", "light") + btn("Meet the Founders", "/founders", "ghost", False))}
'''
    page("/mission", "Mission, Vision and Core Beliefs", "NABME's mission, its 2035 vision and the core beliefs of Service, Passion and Excellence that guide Black and Brown male educators.", body, "who")


def pillars_section(label="The Athari model", title="Four pillars anchor every session, retreat and convening.", band="band-stone"):
    pil = [
        ("I", "Partnership", "Accountable, vulnerable relationships among brothers who share lived experience and a common purpose."),
        ("II", "Protection", "The psychological safety to lower the guard, name what hurts and ask hard questions without performance."),
        ("III", "Proximity", "Physical and relational nearness to leaders who have walked the road, collapsing the distance between aspiration and example."),
        ("IV", "Practice", "Disciplined application of new frameworks to the daily work of leading schools, with feedback and reps."),
    ]
    p = "".join(f'<article class="pillar"><span class="pillar__num" aria-hidden="true">{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in pil)
    return f'''<section class="section {band}" aria-labelledby="pillars-h"><div class="wrap"><div class="section-head">{eyebrow(label)}<h2 id="pillars-h" class="h2">{title}</h2></div><div class="pillars">{p}</div></div></section>'''


FOUNDERS = [
    ("Dr. Rictor L. Craig, Jr.", "Founder & CEO", "Co-Founder and Head of Schools, Statesmen College Preparatory Academy for Boys", "/craig-bio", "/assets/photos/founder-craig.jpg", "info@nabme.org", "RC"),
    ("Joseph Speight", "Co-Founder", "Deputy Chief Academic Officer, Friendship Public Charter School", "/speight-bio", "/assets/photos/founder-speight.jpg", "info@nabme.org", "JS"),
    ("Dr. William L. Blake", "Co-Founder", "Urban education leader; former Director of Redesign XQ, District of Columbia Public Schools", "/blake-bio", "/assets/photos/founder-blake.jpg", "", "WB"),
]


def headshot(src, name, initials):
    return f'<img src="{src}" alt="{e(name)}" loading="lazy" decoding="async" onerror="this.replaceWith(Object.assign(document.createElement(\'span\'),{{className:\'initials\',textContent:\'{initials}\'}}))">'


def build_founders():
    cards = ""
    for name, role, title, bio, photo, email, ini in FOUNDERS:
        mail = f'<div class="socials"><a href="mailto:{email}" aria-label="Email {e(name)}">{ic("envelope-simple")}</a></div>' if email else ""
        cards += f'<article class="person"><figure>{headshot(photo, name, ini)}</figure><p class="eyebrow" style="margin:0">{role}</p><h3>{e(name)}</h3><p>{e(title)} · Washington, DC</p><a class="text-link text-link--red" href="{bio}">View full bio {ARROW}</a>{mail}</article>'
    body = f'''
<section class="phero"><div class="wrap">
  {eyebrow("Who we are · NABME founders")}
  <h1>The people behind the <span class="red">mission</span>.</h1>
  <blockquote class="pull" style="margin:34px 0 0;max-width:62ch">“In order to increase the percentage of African American males in education, and to also close the achievement gap for students of color across the nation, we must develop the capacity of Black male educators to achieve results that will yield dramatic outcomes for marginalized students. The National Association of Black Male Educators commits to this charge.”<cite>NABME Founders</cite></blockquote>
</div></section>
<section class="section"><div class="wrap"><div class="people">{cards}</div></div></section>
{slide_strip(["s26_group", "s26_smiles", "s26_seated", "p_pair", "s26_kid", "p_howard", "p_trio", "p_talk"], "The NABME community", "center 35%")}
{closing("Founded in 2016. Built for the next generation.", "", btn("Our mission &amp; values", "/mission", "light") + btn("Join NABME", "/join", "ghost", False))}
'''
    page("/founders", "NABME Founders", "Meet NABME's founders: Dr. Rictor L. Craig, Jr., Joseph Speight and Dr. William L. Blake.", body, "who")


BIOS = {
    "craig-bio": ("Dr. Rictor L. Craig, Jr.", "Founder & CEO", 0, [
        "For Rictor Craig Jr., going to school was never a drag. He knew early on that both giving and receiving an education would be major passions of his. He knew so much so, that he began taking college courses in the 11th grade in his hometown of Chattanooga, Tennessee.",
        "Rictor began his educational career in 2003 teaching 11th and 12th grade English in the Baltimore City Public School System. In 2005, Rictor joined the Friendship Public Charter School system, where he taught 10th grade English, AP Literature, AP Language, and a Dual Enrollment Literature course. In 2011, Rictor became Principal of Friendship Woodridge Elementary and Middle School and in 2012, he led the school to receiving its Tier 1 status (high performing charter school) and to receiving its International Baccalaureate status in 2015, changing the name to Friendship Woodridge International Elementary and Middle School. Rictor is a Cohort 11 New Leader Alumni and a RELAY GSE Principals Cohort 1 Alumni. He serves on several boards including The Envest Foundation, EmPower Online Magazine, New Leaders National Alumni Advisory Board and CitySchools Collaborative (formerly CityTutor DC) Board of Directors. Rictor is the Founder of the National Association of Black Male Educators (2016) and the Co-Founder/Founding Director of Instruction for Statesmen College Preparatory Academy for Boys (2017).",
        "Rictor holds a B.A. in Professional English from North Carolina A&T State University (2003), a Master of Arts in Teaching from Morgan State University (2005), a Masters of Science in Administration from Trinity Washington University (2011), and received his Doctorate in Educational Leadership (2025) from The University of Maryland Eastern Shore. Rictor attributes his love of learning to his parents, instilling in him the importance of education, even though they did not have the same educational opportunities as he did.",
        "For Rictor, encouraging and overseeing scholars, similarly to how his parents and teachers did for him, is important in guaranteeing quality education and a hope for a better future, especially for Black and Brown boys. His mission as an educator is to provide a Tier 1 education to students of color. It is his goal to ensure that all scholars, no matter their socio-economic background or race, receive an exceptional education to ensure they are prepared to get TO and THROUGH college.",
    ]),
    "speight-bio": ("Joseph E. Speight, Jr.", "Co-Founder", 1, [
        "For more than fifteen years, Joseph E. Speight, Jr., has dedicated his career to transforming the lives of children, empowering educators, and strengthening communities through visionary educational leadership. Recognized as an innovative leader and advocate for educational excellence, he has consistently driven student achievement, developed high-performing teams, and championed equitable opportunities for all learners.",
        "Throughout his career, Mr. Speight has served in a variety of impactful leadership roles, including Teacher, Assistant Principal, Principal, Chief Academic Officer, and currently Deputy Chief Academic Officer for Friendship Public Charter School. Joseph is the Founder of the Black Male Teacher Residency (BMTR) powered by Friendship PCS and Co-Founder of the National Association of Black Male Educators (NABME). Through these initiatives, he has helped create pathways for aspiring educators and inspired countless leaders to advance educational equity and excellence across schools and communities.",
        "Mr. Speight's commitment to lifelong learning mirrors the values he instills in others. He earned a Bachelor of Science degree from Virginia State University, a Master of Science in Organizational Leadership from Nyack College, a Master of Science in Educational Administration from Trinity Washington University, and an Executive Master of Leadership degree from Georgetown University. He is currently pursuing an Education Doctorate (Ed.D.) in Policy and Leadership at American University.",
    ]),
    "blake-bio": ("Dr. William L. Blake", "Co-Founder", 2, [
        "Dr. William L. Blake has spent more than a decade in urban education as a classroom teacher, assistant principal, principal and district leader. He most recently served as Director of Redesign XQ for District of Columbia Public Schools, working with the Cardozo Education Campus community to reimagine the high school experience for students furthest from opportunity.",
        "A product of Prince George's County Public Schools, Dr. Blake returned to lead in the same district. He served as principal of Stephen Decatur Middle School and as an assistant principal at Dr. Henry A. Wise, Jr. High School. He began his career at Gwynn Park High School as a Family and Consumer Sciences teacher, Director of Peer Mediation, senior class advisor and mentor teacher. He has also taught as an adjunct professor at Morgan State University.",
        "Dr. Blake holds a Bachelor of Science in Family and Consumer Sciences from Morgan State University, a Master of Arts in Curriculum and Instruction from Trinity Washington University, and a Doctorate of Education from the University of Maryland Eastern Shore. He is a graduate of the AASA/Howard University Urban Superintendents Academy and a member of Kappa Alpha Psi Fraternity, Inc.",
    ]),
}


def build_bios():
    for slug, (name, role, idx, paras) in BIOS.items():
        f = FOUNDERS[idx]
        body = f'''
<section class="phero"><div class="wrap"><p class="crumbs"><a href="/founders">NABME Founders</a> / {e(name)}</p>{eyebrow(role)}<h1>{e(name)}</h1><p class="lede">{e(f[2])} · Washington, DC</p></div></section>
<section class="section"><div class="wrap bio-layout"><figure><div>{headshot(f[4], name, f[6])}</div><figcaption>{e(name)}, {e(role)} of the National Association of Black Male Educators</figcaption></figure><div class="prose">{"".join(f"<p>{e(p)}</p>" for p in paras)}<p><a class="text-link text-link--red" href="/founders">All founders {ARROW}</a></p></div></div></section>
'''
        page("/" + slug, name, f"{name}, {role} of the National Association of Black Male Educators: biography.", body, "who")


def build_join():
    body = f'''
<section class="phero phero--split"><div class="wrap">
  <div>{eyebrow("Join us")}<h1>Join the <span class="red">movement</span>.</h1><p class="lede">By completing the information form below, you will become a part of a movement of change agents committed to positively affecting the lives of the marginalized children that they serve. Help dramatically shift outcomes in schools across the world. Join Us!</p></div>
  <div class="phero__photo">{img("p_trio", eager=True, pos="center 30%")}</div>
</div></section>
<section class="section"><div class="wrap" style="max-width:860px">
  <div class="form-panel form-wrap" data-steps data-save="join">
    <div class="steps-head"><b data-step-label>About you</b><span data-step-count>Step 1 of 2</span></div>
    <div class="progress" aria-hidden="true"><i></i></div>
    <form class="form" data-form="Members" style="margin-top:26px">
      <div class="step-panel" data-title="About you"><div class="form-grid">
        {field("Your name", "name", required=True, auto="name")}
        {field("Your email", "email", "email", required=True, auto="email")}
        {role_field()}
        {field("School / organization", "org", required=True, auto="organization")}
      </div><div class="step-nav"><span></span><button class="btn btn--red" type="button" data-next>Continue {ic("arrow-right")}</button></div></div>
      <div class="step-panel" data-title="Your work and interests" hidden><div class="form-grid">
        {field("City, State", "city", required=True, auto="address-level2", placeholder="Washington, DC")}
        {field("Years in education", "years", options=["0–3 years", "4–7 years", "8–12 years", "13+ years", "Not yet in education"])}
        {checks("I'm interested in", "interests", ["Athari Fellowship", "Capital Summit", "Careers/Resume Bank", "Mentoring", "Volunteering"])}
      </div><p class="form-note">We'll add you to the NABME newsletter. Unsubscribe anytime.</p><div class="step-nav"><button class="btn btn--outline" type="button" data-back>{ic("arrow-left")} Back</button><button class="btn btn--red" type="submit">Join NABME</button></div></div>
    </form>
    {success("Welcome to the movement.", "Check your inbox for a welcome email. Here are three ways to take your next step:", btn("Submit your resume", "/resume-bank") + btn("Register for the Summit", "/summit", "outline") + btn("Follow NABME", "/live", "outline"))}
  </div>
</div></section>'''
    page("/join", "Join NABME", "Join the National Association of Black Male Educators: a national movement of Black and Brown male educators and allies.", body, "join")


def build_contact():
    socials = "".join(f'<a class="text-link" href="{u}"{EXT}>{ic(i)} {e(n)}</a><br>' for n, u, i in SOCIAL)
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("Join us · Contact")}<h1>Let's <span class="red">talk</span>.</h1><p class="lede">Please feel free to contact us with any questions or business inquiries. We'd love to hear from you!</p></div></section>
<section class="section"><div class="wrap split">
  <div><h2 style="font-size:1.4rem;margin-bottom:10px">Email us</h2><p style="margin-bottom:30px"><a class="text-link text-link--red" href="mailto:info@nabme.org" style="font-size:1.25rem;font-weight:700">{ic("envelope-simple")} info@nabme.org</a><br><span class="source">All inquiries and questions go here.</span></p><h2 style="font-size:1.4rem;margin-bottom:14px">Find NABME online</h2><div style="display:grid;gap:12px">{socials}</div></div>
  <div class="form-panel form-wrap"><form class="form" data-form="Contact Messages"><div class="form-grid">
    {field("Name", "name", required=True, auto="name")}
    {field("Email", "email", "email", required=True, auto="email")}
    {field("Organization", "org", auto="organization")}
    {field("Topic", "topic", required=True, options=["General", "Partnerships and sponsorship", "Media and speaking", "Athari Fellowship", "Capital Summit", "Talent Portal", "Other"])}
    {field("Message", "message", "textarea", required=True, full=True)}
  </div><div><button class="btn btn--red" type="submit">Send message</button></div></form>
  {success("Message sent.", "Thanks for reaching out. The right person on the NABME team will get back to you.")}</div>
</div></section>'''
    page("/contact", "Contact Us", "Contact the National Association of Black Male Educators about partnerships, media, the Athari Fellowship, the Capital Summit or the Talent Portal.", body, "join")


def build_careers():
    paths = [
        ("Teach", "Classroom roles at every grade.", "/jobs", "Job Board"),
        ("Lead", "Deans, assistant principals and principals.", "/athari", "Athari Fellowship"),
        ("Support", "Counselors, coaches, culture and operations roles.", "/jobs", "Job Board"),
        ("Shape policy", "Advocacy and the Capitol Hill Fly-In.", "/summit", "Capital Summit"),
    ]
    pc = "".join(f'<a class="card card-link card--bar{"-red" if i % 2 == 0 else ""}" href="{h}"><h3>{t}</h3><p>{d}</p><span class="more">{l} {ARROW}</span></a>' for i, (t, d, h, l) in enumerate(paths))
    body = f'''
<section class="phero phero--split"><div class="wrap">
  <div>{eyebrow("Careers in education")}<h1>Our children need to see <span class="red">you</span> at the front of the class.</h1>
  <div class="btn-row">{btn("Search open positions", "/jobs")}{btn("Join the Resume Bank", "/resume-bank", "outline")}</div></div>
  <div class="phero__photo">{img("arrival2", eager=True, pos="center 35%")}</div>
</div></section>
<section class="section"><div class="wrap prose" style="max-width:820px">
  <p>Fewer than 2 of every 100 public school teachers in America are Black men. To us, that is not just a statistic. It is a classroom without a mirror. It is a hallway without a mentor. It is a school without the voice that could have changed a boy's direction.</p>
  <p>The research is clear. When Black students have a Black teacher, they are more likely to finish high school and more likely to go to college. For low-income Black boys, one Black teacher in elementary school lowers the risk of dropping out by 39 percent. Black male educators do not only teach content. They model possibility.</p>
  <p>That is why NABME exists: to dramatically increase the number of highly effective Black and Brown male teachers and leaders, and to make sure that every man who answers the call is known, loved, and pushed to be great.</p>
  <p>If you are considering education, we want you in the work. If you are already in the work, we want you to stay, to grow and to lead. There is a place for you here.</p>
  <div class="btn-row" style="margin-top:10px">{btn("Search open positions", "/jobs")}{btn("Join the Resume Bank", "/resume-bank", "outline")}{btn("Submit interest in the Athari Fellowship", "/athari#interest", "outline")}</div>
</div></section>
<section class="mosaic mosaic--kids" aria-label="Black men with the young people they serve">{"".join(f'<figure>{img(x, pos="center 35%")}</figure>' for x in ["s26_kid", "arrival", "s26_mentor", "arrival2", "s26_students"])}</section>
{why_matters()}
<section class="section" aria-labelledby="paths-h"><div class="wrap"><div class="section-head">{eyebrow("Four paths into the work")}<h2 id="paths-h" class="h2">Find where you fit.</h2></div><div class="grid-4">{pc}</div></div></section>
<section class="section band-stone" aria-labelledby="open-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Open positions")}<h2 id="open-h" class="h2">The newest roles for Black male educators.</h2></div>{btn("See all jobs", "/jobs", "outline")}</div>
  <div class="empty">{ic("briefcase")}<h3>New positions are on the way.</h3><p>Schools and organizations post openings through NABME's Job Board. The six newest will appear here.</p><div class="btn-row">{btn("Post a position", "/post-job")}{btn("Get new-job alerts", "/resume-bank", "outline")}</div></div>
</div></section>
{closing("Let schools that want you find you.", "Build your profile once. Get found by schools and organizations that are looking for Black male educators.", btn("Create my profile", "/resume-bank", "light"))}
<section class="section"><div class="wrap" style="max-width:900px"><figure class="qcard qcard--paper"><div class="qmark" aria-hidden="true">“</div><blockquote>The most valuable things about the Athari Fellowship have been the proximity and the protection. The power of these two things have been the key driving forces for both development and healing.</blockquote><figcaption><cite>Athari Fellow, Cohort 2</cite></figcaption></figure></div></section>
'''
    page("/careers", "Careers", "Careers for Black male educators: open positions, the NABME Resume Bank and the Athari Fellowship.", body, "careers")


def build_talent():
    lanes = [
        ("Educators", "free", [("Create profile", "guided, 5 steps", False), ("NABME review", "approve profile", False), ("In Resume Bank", "searchable", False), ("Get invited", "interview, hire", False)]),
        ("Employers", "resume access", [("Request access", "school or network", False), ("Verified account", "NABME approves", False), ("Search and save", "filters, saved lists", False), ("Invite and hire", "interviews", False)]),
        ("Employers", "job posts", [("Post a position", "form and logo", False), ("NABME review", "approve listing", False), ("Live on Job Board", "60 days", False), ("Educators apply", "direct to you", False)]),
    ]
    lane_html = "".join(f'<div class="lane"><div class="lane__who"><b>{w}</b><span>{s}</span></div>' + "".join(f'<div class="step{" step--paid" if p else ""}"><b>{a}</b><span>{b}</span></div>' for a, b, p in steps) + "</div>" for w, s, steps in lanes)
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_group", eager=True, pos="center 30%")}</div><div class="wrap">{eyebrow("The NABME Talent Portal")}<h1>One portal. Three <span class="red">ways in</span>.</h1><p class="lede">A free profile for educators, resume access for employers, and a job board where schools post openings for Black male educators.</p></div></section>
<section class="section"><div class="wrap"><div class="plans">
  <article class="plan plan--dark"><span class="plan__for">For educators · Free</span><h3>Join the Resume Bank</h3><p class="plan__price">Build a profile once. Get found by schools and organizations that want Black male educators.</p>{btn("Create my profile", "/resume-bank")}</article>
  <article class="plan plan--feature"><span class="plan__for">For employers · Free during launch</span><h3>Search the talent</h3><p class="plan__price">Request verified access to search resumes, save candidates and invite them to interview.</p>{btn("Request employer access", "/employers")}</article>
  <article class="plan"><span class="plan__for">For employers · Free during launch</span><h3>Post an open position</h3><p class="plan__price">List teaching and leadership roles where Black male educators are already looking.</p>{btn("Post a job", "/post-job", "outline")}</article>
</div></div></section>
<section class="section band-stone" aria-labelledby="how-h"><div class="wrap">
  <div class="section-head">{eyebrow("How the portal works")}<h2 id="how-h" class="h2">Simple for educators. Simple for schools.</h2></div>
  <div class="flow" role="list">{lane_html}</div>
  <p class="source" style="margin-top:18px">Employer access and job posts are free while NABME grows the Resume Bank.</p>
</div></section>
<section class="section"><div class="wrap split--even split">
  <div>{eyebrow("Find a job")}<h2 class="h2">Looking for your next role?</h2><p class="lede" style="margin-top:14px">Search open positions from schools that want Black male educators, save jobs and apply with your portal profile.</p><div class="btn-row" style="margin-top:24px">{btn("Browse the Job Board", "/jobs")}</div></div>
  <div class="photo" style="aspect-ratio:4/3">{img("p_audience")}</div>
</div></section>'''
    page("/talent", "Talent Portal", "The NABME Talent Portal: a free Resume Bank for Black male educators, resume access for employers and a job board.", body, "careers")


def build_resume_bank():
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("Talent Portal · For educators · Free")}<h1>Join the <span class="red">Resume Bank</span>.</h1><p class="lede">Build your profile once. Get found by schools and organizations that are looking for Black male educators. It saves as you go and works on your phone.</p></div></section>
<section class="section"><div class="wrap" style="max-width:900px">
  <div class="form-panel form-wrap" data-steps data-save="resume">
    <div class="steps-head"><b data-step-label>About you</b><span data-step-count>Step 1 of 5</span></div>
    <div class="progress" aria-hidden="true"><i></i></div>
    <form class="form" data-form="Resume Bank" style="margin-top:26px">
      <div class="step-panel" data-title="About you"><div class="form-grid">
        {field("Full name", "name", required=True, auto="name")}
        {field("Email", "email", "email", required=True, auto="email")}
        {field("Phone", "phone", "tel", auto="tel")}
        {field("City, State", "city", required=True, auto="address-level2")}
        <div class="field"><label for="f-photo">Headshot <span class="hint">(optional)</span></label><input id="f-photo" name="photo" type="file" accept="image/*" data-max-mb="4"></div>
        {field("Willing to relocate?", "relocate", required=True, options=["Yes", "No", "Maybe"])}
      </div><div class="step-nav"><span></span><button class="btn btn--red" type="button" data-next>Continue {ic("arrow-right")}</button></div></div>
      <div class="step-panel" data-title="Your work" hidden><div class="form-grid">
        {role_field("Current role", "current_role")}
        {field("Years in education", "years", required=True, options=["0–3 years", "4–7 years", "8–12 years", "13+ years"])}
        {field("Grade bands", "grades", hint="For example: K–5, 6–8, 9–12")}
        {field("Subjects", "subjects")}
        {field("Certifications / licensure by state", "certs", full=True, hint="For example: DC Secondary English; MD Administrator I")}
      </div><div class="step-nav"><button class="btn btn--outline" type="button" data-back>{ic("arrow-left")} Back</button><button class="btn btn--red" type="button" data-next>Continue {ic("arrow-right")}</button></div></div>
      <div class="step-panel" data-title="What you want next" hidden><div class="form-grid">
        {checks("Target roles", "targets", ["Teacher", "Dean", "AP", "Principal", "Coach", "Central office", "Other"])}
        {field("Schedule", "schedule", required=True, options=["Full-time", "Part-time", "Either"])}
        {field("Available to start", "start", "month")}
        {field("Open to remote?", "remote", options=["Yes", "No"])}
      </div><div class="step-nav"><button class="btn btn--outline" type="button" data-back>{ic("arrow-left")} Back</button><button class="btn btn--red" type="button" data-next>Continue {ic("arrow-right")}</button></div></div>
      <div class="step-panel" data-title="Show yourself" hidden><div class="form-grid">
        <div class="field field--full"><label for="f-resume">Resume (PDF or Word)</label><input id="f-resume" name="resume" type="file" accept=".pdf,.doc,.docx" required data-max-mb="4"><span class="err">Attach your resume (PDF or Word, up to 4 MB) to continue.</span></div>
        {field("Link to a 60-second video intro", "video", "url", full=True, hint="Optional. Upload to YouTube, Google Drive or Vimeo and paste the link.", placeholder="https://")}
        {field("LinkedIn URL", "linkedin", "url", placeholder="https://www.linkedin.com/in/…")}
        {field("Skills", "skills", hint="Separate with commas")}
      </div><div class="step-nav"><button class="btn btn--outline" type="button" data-back>{ic("arrow-left")} Back</button><button class="btn btn--red" type="button" data-next>Continue {ic("arrow-right")}</button></div></div>
      <div class="step-panel" data-title="Privacy and consent" hidden><div class="form-grid">
        <fieldset class="field field--full"><legend>Who can see your profile?</legend><div class="checks" style="grid-template-columns:1fr"><label class="check"><input type="radio" name="visibility" value="verified" checked> Visible to verified employers</label><label class="check"><input type="radio" name="visibility" value="hidden"> Hidden: I'll apply to jobs myself</label></div></fieldset>
        <div class="field field--full"><label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to be contacted by verified employers through the portal and to receive NABME emails.</label><span class="err">Please agree to continue.</span></div>
      </div><p class="form-note">Your contact details stay private until you accept an employer's invitation.</p><div class="step-nav"><button class="btn btn--outline" type="button" data-back>{ic("arrow-left")} Back</button><button class="btn btn--red" type="submit">Submit my profile</button></div></div>
    </form>
    {success("Your profile is in review.", "NABME reviews every profile before it becomes searchable. You'll get an email when it's live, plus a dashboard showing profile strength, employer views, invitations and saved jobs.", btn("Browse the Job Board", "/jobs") + btn("Register for the Summit", "/summit", "outline"))}
  </div>
</div></section>'''
    page("/resume-bank", "Resume Bank", "Join NABME's free Resume Bank and get found by schools looking for Black male educators.", body, "careers")


def build_employers():
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_recruit", eager=True, pos="center 30%")}</div><div class="wrap">{eyebrow("Talent Portal · For employers")}<h1>Your next great hire is <span class="red">already here</span>.</h1><p class="lede">Search NABME's network of Black male educators and invite them to interview. Employer access is free during launch.</p><div class="btn-row">{btn("Request access", "#access")}{btn("Post a job", "/post-job", "ghost", False)}</div></div></section>
<section class="section band-stone"><div class="wrap split">
  <div>{eyebrow("What you get")}<h2 class="h2">Search, save, invite, hire.</h2></div>
  <div class="grid-2">
    <div class="card"><h3>Filters that matter</h3><p>Role, grade band, subject, state, years of experience, certification and openness to relocate.</p></div>
    <div class="card"><h3>Saved lists</h3><p>Build shortlists for each opening and share them with your hiring team.</p></div>
    <div class="card"><h3>Private invitations</h3><p>Invite educators to interview through the portal. Their contact details stay private until they accept.</p></div>
    <div class="card"><h3>“We hired” button</h3><p>Tell NABME when you hire, so placements count toward the impact report.</p></div>
  </div>
</div></section>
<section class="section" id="access"><div class="wrap split">
  <div>{eyebrow("Request access")}<h2 class="h2">Verified employers only.</h2><p class="lede" style="margin-top:14px">NABME approves each employer account before resumes are visible, protecting educators' information. Access is free while we grow the Resume Bank.</p></div>
  <div class="form-panel form-wrap"><form class="form" data-form="Employers"><div class="form-grid">
    {field("Organization", "org", required=True, auto="organization")}
    {field("Your name", "name", required=True, auto="name")}
    {field("Work email", "email", "email", required=True, auto="email")}
    {field("Organization type", "orgtype", required=True, options=["Single school", "Charter network", "School district", "Higher education", "Nonprofit / other"])}
    {field("Number of schools", "schools", "number")}
    {field("Roles you're hiring for", "hiring", hint="For example: 3rd grade teacher, dean of students")}
  </div><div><button class="btn btn--red" type="submit">Request access</button></div></form>
  {success("Request received.", "NABME will verify your organization and email you when your access is ready.")}</div>
</div></section>'''
    page("/employers", "Employer Access", "Search NABME's Resume Bank of Black male educators. Free employer access during launch.", body, "careers")


def build_jobs():
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_table", eager=True, pos="center 30%")}</div><div class="wrap">{eyebrow("Talent Portal · Job Board")}<h1>Find your next role at the <span class="red">front of the class</span>.</h1><p class="lede">Teaching and leadership roles from schools and organizations that want Black male educators.</p><div class="btn-row">{btn("Post a position", "/post-job")}{btn("Join the Resume Bank", "/resume-bank", "ghost", False)}</div></div></section>
<section class="section"><div class="wrap">
  <form class="filters" data-jobsearch role="search" aria-label="Search jobs">
    <div class="field"><label for="j-k">Keywords</label><input id="j-k" type="search" name="q" placeholder="Title, subject or school"></div>
    <div class="field"><label for="j-r">Role</label><select id="j-r"><option>All roles</option><option>Teacher</option><option>Dean</option><option>Assistant principal</option><option>Principal</option><option>Coach</option><option>Central office</option></select></div>
    <div class="field"><label for="j-g">Grade band</label><select id="j-g"><option>All grades</option><option>K–5</option><option>6–8</option><option>9–12</option></select></div>
    <div class="field"><label for="j-s">State</label><select id="j-s"><option>All states</option><option>DC</option><option>Maryland</option><option>Virginia</option><option>Remote</option></select></div>
    <button class="btn btn--red" type="submit">Search jobs</button>
  </form>
  <p class="inline-msg" data-jobs-msg aria-live="polite"></p>
  <div class="empty" style="margin-top:20px">{ic("briefcase")}<h3>No open positions yet.</h3><p>NABME reviews every listing before it goes live. Listings stay up for 60 days, and the newest jobs go out in a weekly email to the Resume Bank.</p><div class="btn-row">{btn("Post the first position", "/post-job")}{btn("Get new-job alerts", "/resume-bank", "outline")}</div></div>
</div></section>'''
    page("/jobs", "Job Board", "Jobs for Black male educators: teaching and leadership roles posted by schools and organizations through NABME.", body, "careers")


def build_post_job():
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("Talent Portal · For employers · Per post")}<h1>Post your opening where <span class="red">Black male educators</span> are already looking.</h1><p class="lede">Posting is free during launch. NABME approves each listing before it goes live; listings run for 60 days with an option to renew.</p></div></section>
<section class="section"><div class="wrap" style="max-width:900px"><div class="form-panel form-wrap"><form class="form" data-form="Job Posts"><div class="form-grid">
  {field("Job title", "title", required=True)}
  {field("Organization", "org", required=True, auto="organization")}
  {field("Location", "location", required=True, placeholder="Washington, DC")}
  {field("Remote option", "remote", options=["On-site", "Hybrid", "Remote"])}
  {field("Job type", "type", required=True, options=["Full Time", "Part Time", "Contract"])}
  {field("Role category", "category", required=True, options=["Teacher", "Dean", "Assistant principal", "Principal", "Coach", "Counselor", "Operations", "Central office", "Other"])}
  {field("Grade band", "grades", options=["K–5", "6–8", "9–12", "K–12", "Adult / higher ed"])}
  {field("Salary range", "salary", hint="Listings with a salary range get more applicants", placeholder="$58,000–$72,000")}
  {field("Description", "desc", "textarea", required=True, full=True)}
  {field("How to apply (email or URL)", "apply", required=True)}
  {field("Application deadline", "deadline", "date")}
  <div class="field"><label for="f-logo">Logo <span class="hint">(optional)</span></label><input id="f-logo" name="logo" type="file" accept="image/*" data-max-mb="4"></div>
</div><p class="form-note">NABME reviews every listing before it goes live and emails you when it's up.</p><div><button class="btn btn--red" type="submit">Submit for review</button></div></form>
{success("Listing submitted.", "NABME will review your listing and email you when it's live on the Job Board.", btn("Back to the Talent Portal", "/talent", "outline"))}</div></div></section>'''
    page("/post-job", "Post a Job", "Post teaching and leadership openings for Black male educators on NABME's Job Board.", body, "careers")


def build_donate():
    body = f'''
<section class="phero phero--split"><div class="wrap">
  <div>{eyebrow("Donate")}<h1>NABME needs <span class="red">your help</span>.</h1><p class="lede">When you invest in NABME, you are investing in changing the lives of millions of marginalized children across the world. NABME aspires to dramatically increase the number of highly effective Black and Brown male educators who positively impact the children that they serve. Your gift will help us get this done.</p></div>
  <div class="form-panel give-card" id="give">
    <p class="eyebrow">Give securely through PayPal</p>
    <h2 class="h2" style="font-size:1.7rem">Every gift puts a Black male educator in the room.</h2>
    <p>Choose your amount, give once or monthly, and pay with a card or your PayPal account, all on NABME's secure PayPal page.</p>
    <ul class="give-steps"><li>Pick any amount, from $25 to whatever moves you</li><li>Check "Make this a monthly donation" to give every month</li><li>Giving in honor of a Black male educator who shaped you? Add his name in the note</li></ul>
    <a class="btn btn--red give-btn" href="{PAYPAL}"{EXT}>Go to PayPal to give {ARROW}</a>
    <p class="form-note">NABME is a 501(c)(3) nonprofit organization. PayPal emails you a receipt for your records.</p>
  </div>
</div></section>
<section class="section band-stone"><div class="wrap split">
  <div>{eyebrow("Proof it works")}<h2 class="h2"><span class="red">100%</span> of our Athari Fellows are still in education, and 83% now lead.</h2><p class="lede" style="margin-top:16px">More than 310 educators answered the call to the first Capital Summit. <a href="/impact">Read our impact reports</a>.</p></div>
  <div><h3 style="font-size:1.3rem;margin-bottom:14px">With your support we can:</h3><ul class="heard"><li style="list-style:none">Establish connections with undergraduate institutions across the country to recruit Black males into the field of education</li><li style="list-style:none">Provide high quality professional development to teachers to increase the quality of instruction in classrooms</li><li style="list-style:none">Increase the interest of Black males in the field of education</li><li style="list-style:none">Provide support to Black male educators in alignment with their professional goals</li><li style="list-style:none">Bring Black male educators together at the annual Black Male Educator Capital Summit</li></ul></div>
</div></section>
{impact_band()}
<section class="section"><div class="wrap"><div class="section-head">{eyebrow("Other ways to give")}<h2 class="h2">Every seat is a statement.</h2></div><div class="grid-3">
  <a class="card card-link card--bar-red" href="/summit#sponsor"><h3>Sponsor the Summit</h3><p>Put your organization behind the 2nd Annual Black Male Educator Capital Summit.</p><span class="more">Sponsorship {ARROW}</span></a>
  <a class="card card-link card--bar" href="/contact"><h3>Corporate and foundation partnerships</h3><p>Build a multi-year partnership with NABME. Choose “Partnerships and sponsorship” on the contact form.</p><span class="more">Contact us {ARROW}</span></a>
  <a class="card card-link card--bar-red" href="#give"><h3>Give in honor</h3><p>Dedicate your gift to a Black male educator who shaped you.</p><span class="more">Give in honor {ARROW}</span></a>
</div><p class="source" style="margin-top:22px">The National Association of Black Male Educators is a 501(c)(3) nonprofit organization.</p></div></section>'''
    page("/donate", "Donate", "Give to NABME: fund the Athari Fellowship, the Black Male Educator Capital Summit and the pipeline of Black male educators.", body)


MEDIA_CARDS = [
    ("Black male educators deserve support. That's where NABME comes in.", "Education Forward DC", "Apr. 10, 2024", "Feature", "Black men are entering education faster than any other group, but they are also leaving. How NABME keeps them in the work.", "https://edforwarddc.org/black-male-educators-deserve-support-thats-where-nabme-comes-in/"),
    ("TheBlackManCan Awards Celebrates 16 Years of Black Excellence in NYC", "Cassius Life", "Apr. 28, 2026", "Article", "Dr. Rictor Craig presents the Classroom King Award.", "https://cassiuslife.com/1398145/the-black-man-can-awards-year-16-celebration/"),
    ("Strong Relationships and Role Models Help Black and Latino Boys Succeed", "Clark Foundation", "Mar. 23, 2024", "Case study", "Statesmen, and Shawn Hardnett and Dr. Rictor Craig's model.", "https://clarkfoundationdc.org/impact/case-studies/strong-relationships-and-role-models-help-black-and-latino-boys-succeed"),
    ("Globetrotting with Students at Statesmen", "DC Public Charter School Board", "Mar. 20, 2023", "Article", "Statesmen students travel to Madrid, Paris and London.", "https://dcpcsb.org/globetrotting-students-statesmen-college-academy-prep-pcs"),
    ("2023 Amplify Keynotes & Presenters", "Kauffman Foundation", "2023", "Speaker listing", "Dr. Craig as NABME founder.", "https://www.kauffman.org/amplify/2023-conference/keynotes-presenters/"),
    ("Stride, Inc. Changing the Face of American Education Through Partnership with National Association of Black Male Educators", "Business Wire", "Apr. 21, 2021", "Press release", "Recruiting and professional development for Black male educators in online and hybrid schools.", "https://www.businesswire.com/news/home/20210421005328/en"),
    ("Black Mentorship Educators Network aims to increase representation of Black male educators at KIPP DC", "KIPP DC", "Jan. 31, 2020", "Article", "NABME named as partner.", "https://www.kippdc.org/black-mentorship-educators-network-aims-to-increase-representation-of-black-male-educators-at-kipp-dc/"),
    ("“I see heaven in the eyes of these boys”: The birth of an all-male charter school in Southeast Washington, D.C.", "Thomas B. Fordham Institute", "Sep. 20, 2019", "Commentary", "Statesmen's founding.", "https://edexcellence.net/national/commentary/i-see-heaven-eyes-these-boys-birth-all-male-charter-school-southeast-washington"),
    ("N.C. A&T Alumnus Co-Founds School for African American Boys in Washington, D.C.", "N.C. A&T Alumni", "Oct. 26, 2018", "Article", "Dr. Craig.", "https://ncatsualumni.org/n-c-at-alumnus-co-founds-school-for-african-american-boys-in-washington-d-c/"),
    ("2016 Healthy School Hero: Rictor Craig", "Action for Healthy Kids", "Oct. 12, 2016", "Award story", "Dr. Craig's school wellness work at Friendship Woodridge.", "https://actionforhealthykids.org/story/2016-healthy-school-hero-rictor-craig/"),
    ("BE Modern Man: “The Progressive Educator,” Rictor Craig", "Black Enterprise", "May 11, 2016", "Profile", "Dr. Craig and NABME's founding.", "https://www.blackenterprise.com/modern-man-progressive-educator-rictor-craig/"),
]
MEDIA_MORE = [  # links still to collect from Rick / the handoff team
    ("Mar. 11, 2026", "Pahara Announces 2026 Pahara Fellowship Cohorts", "Pahara Institute · Shawn Hardnett named to the Leaf Cohort", ""),
    ("Nov. 12, 2025", "Thrive Dispatches S2E5: Love As An Operational Strategy", "Georgetown Thrive Center · Shawn Hardnett · Podcast", ""),
    ("Apr. 10, 2024", "Black male educators deserve support. That's where NABME comes in.", "Education Forward DC · NABME, Dr. Craig, Joseph Speight, Shawn Hardnett", ""),
    ("2023", "A first-class educational experience", "Education Forward DC · Statesmen; Shawn Hardnett quoted", ""),
    ("Sep. 17, 2021", "Building D.C. schools that serve all students and support all educators", "The Washington Post · Op-ed co-written by Dr. Craig", ""),
    ("c. Aug. 2020", "“We've had a social justice summer”", "WUSA9 · Statesmen's KINGS 101 · TV news", ""),
    ("May 4, 2020", "LTL Ep. 4: The Boy Crisis in Our Schools", "Project Forever Free · Shawn Hardnett · Podcast", ""),
    ("c. 2019", "“For black and brown boys”", "WUSA9 · Shawn Hardnett and Dr. Rictor Craig as founders · TV news", ""),
    ("c. Aug. 2018", "80 black men greet boys on first day of school in emotional video", "WUSA9 · Dr. Rictor Craig and Shawn Hardnett", "https://wusa9.com/article/news/local/dc/dc-charter-school-changing-way-students-of-color-are-educated/65-bd2d97c6-6b94-4686-8a8e-ae1a32500b24"),
    ("Sep. 28, 2017", "With New Middle School for DC Boys, Shawn Hardnett Follows His North Star", "Education Forward DC · Profile", ""),
    ("Jan. 20, 2013", "Young students reflect on growing up with Obama as president", "TheGrio · Dr. Craig as principal", ""),
]


def build_media():
    cards = news_cards(MEDIA_CARDS, lead=False)
    more = "".join(f'<li><time>{d}</time><div><b>{e(t)}</b><span>{e(s)}</span></div>{(f"<a href={chr(34)}{u}{chr(34)}{EXT}>Open {ARROW}</a>") if u else "<em>Link coming</em>"}</li>' for d, t, s, u in MEDIA_MORE)
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("NABME News · Media")}<h1>NABME in the <span class="red">conversation</span>.</h1><p class="lede">When children see Black and Brown men leading their classrooms and schools, they see what is possible for themselves. That is why this conversation matters to NABME, and why we keep adding our voice to it. Social posts live on <a href="/live">NABME Live</a>.</p></div></section>
<section class="section"><div class="wrap">
  <div class="grid-2" style="margin-bottom:28px">
    <a class="story story--lead" style="grid-column:auto;grid-row:auto;min-height:300px" href="https://vimeo.com/nabme"{EXT}><div class="story__meta"><span class="tag tag--red">{ic("play-circle")} Video</span><span>Vimeo · Sept. 2021 · 1 hr 21 min</span></div><h3>Dear White Educators: A Conversation with Dr. Rictor Craig</h3><p>A candid conversation on race, teaching and what Black boys need from every educator.</p><span class="more">Watch {ARROW}</span></a>
    <div class="card card--side-red" style="justify-content:center"><p class="kicker red">Leadership in the field</p><h3>Profiles</h3><p>Rictor Craig, NewSchools Venture Fund · Shawn Hardnett, National Charter Collaborative · Shawn Hardnett, MEN Impact Change honoree (2024) · Bowie State Black Male Teacher Initiative Consortium (NABME listed).</p></div>
  </div>
  <div class="news-grid">{cards}</div>
  <h2 class="h2" style="font-size:clamp(1.6rem,2.6vw,2.2rem);margin:clamp(48px,6vw,80px) 0 18px">More coverage</h2>
  <ul class="cov">{more}</ul>
</div></section>
{closing("Have a NABME story?", "Media and speaking requests go straight to the team.", btn("Contact us", "/contact", "light"))}'''
    page("/media", "Media", "NABME in the news: coverage of the National Association of Black Male Educators, Dr. Rictor Craig and Shawn Hardnett.", body, "news")


def build_blog():
    upcoming = [("Athari", "The 2025–26 Athari Fellowship Impact Report"), ("Summit", "Summit recap: 310 educators answered the call"), ("Athari", "Welcome, Athari Cohort 4"), ("Voices", "Educator spotlights from Nominate a Black Male Educator")]
    up = "".join(f'<article class="card card--bar{"-red" if i % 2 == 0 else ""}"><span class="tag">{c}</span><h3>{t}</h3><p>Coming soon to NABME Voices.</p></article>' for i, (c, t) in enumerate(upcoming))
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("NABME News · Blog")}<h1>NABME <span class="red">Voices</span>.</h1><p class="lede">From the classroom, for the future. A monthly post from NABME's educators, Fellows and leaders, plus our impact reports.</p></div></section>
<section class="section"><div class="wrap">
  <a class="split--even split card-link" href="/math-with-buggbey" style="text-decoration:none;align-items:center">
    <div class="photo" style="aspect-ratio:4/5;max-height:560px">{img("buggbey", pos="center 20%")}</div>
    <div><div class="story__meta"><span class="tag tag--red">Voices</span><span>NABME · March 7, 2023</span></div><h2 class="h2" style="margin:16px 0">Mathematics with Mr. BuggBey</h2><p class="lede">A NABME Fellow on the joy of helping students gain confidence in math.</p><p style="margin-top:22px"><span class="text-link text-link--red">Read the interview {ARROW}</span></p></div>
  </a>
</div></section>
<section class="section band-stone"><div class="wrap"><div class="section-head">{eyebrow("Next in NABME Voices")}<h2 class="h2">Coming soon.</h2></div><div class="grid-4">{up}</div>
<div class="grid-2" style="margin-top:28px"><a class="card card-link card--side-red" href="/nominate"><p class="kicker red">Nominate a Black male educator</p><h3>Who changed your direction?</h3><p>Tell us about him. Selected nominations are featured on NABME Voices, with permission.</p><span class="more">Nominate {ARROW}</span></a><div class="form-panel"><h3 style="font-size:1.4rem;margin-bottom:12px">Get every new post</h3>{signup_form(source="blog")}</div></div></div></section>'''
    page("/blog", "Blog", "NABME Voices: stories, interviews and impact reports from Black male educators.", body, "news")

    art = f'''
<section class="phero"><div class="wrap"><p class="crumbs"><a href="/blog">NABME Voices</a> / Interview</p>{eyebrow("Voices · March 7, 2023")}<h1>Mathematics with <span class="red">Mr. BuggBey</span></h1><p class="lede">A NABME Fellow on the joy of helping students gain confidence in math.</p></div></section>
<section class="section"><div class="wrap bio-layout"><figure><div>{img("buggbey", eager=True)}</div><figcaption>Jeff BuggBey, fifth-grade math teacher, Statesmen College Prep Academy for Boys</figcaption></figure><div class="prose">
  <h2>Confidence through learning.</h2><p>Jeff BuggBey teaches fifth-grade math at Statesmen College Prep Academy for Boys. In NABME's profile, he describes the satisfaction of watching students understand a problem and gain confidence.</p>
  <h2>A network to grow with.</h2><p>He credits NABME with connecting him to other Black male educators, practical training, conversations about shared challenges, and opportunities to present at conferences. He hopes to develop as a master teacher and take on leadership.</p>
  <div class="form-panel" style="margin-top:34px"><h3 style="font-size:1.3rem;margin-bottom:12px">Get the next NABME Voices post</h3>{signup_form(source="article")}</div>
</div></div></section>'''
    page("/math-with-buggbey", "Mathematics with Mr. BuggBey", "A NABME Fellow and fifth-grade math teacher on helping students gain confidence in math.", art, "news")


def build_events():
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("NABME News · Events")}<h1>Where the <span class="red">brotherhood</span> gathers.</h1></div></section>
<section class="section"><div class="wrap">
  <h2 class="h2" style="font-size:clamp(1.6rem,2.6vw,2.2rem);margin-bottom:18px">Upcoming</h2>
  <div style="margin:0 0 56px">{summit_banner("h3")}</div>
  <h2 class="h2" style="font-size:clamp(1.6rem,2.6vw,2.2rem);margin-bottom:18px">Past</h2>
  <div class="photo" style="aspect-ratio:3/1;margin-bottom:16px">{img("p_lineup", pos="center 40%")}</div>
  <article class="event event--past"><div class="event__date"><b>12</b><span>Aug 2026</span></div><div><h3>Healing While Leading</h3><p>A Vineyard conversation on Black male educator mental health with Shawn Hardnett, William Collins, Sharif El-Mekki and moderator Dr. David Johns. Old Whaling Church, Edgartown, MA.</p></div><div class="btn-row"><a class="btn btn--outline btn--sm" href="/assets/photos/flyer-healing-while-leading.jpg"{EXT}>View flyer</a></div></article>
  <article class="event event--past"><div class="event__date"><b>28</b><span>Feb 2026</span></div><div><h3>The inaugural Black Male Educator Capital Summit</h3><p>Washington, D.C. 190+ registered, 310+ registered or waitlisted, from 20+ states.</p></div><div class="btn-row">{btn("Recap and numbers", "/summit#numbers", "outline")}</div></article>
</div></section>'''
    page("/events", "Events", "NABME events: Summit 2027 info coming soon, plus past convenings.", body, "news")


def build_live():
    accounts = [
        ("Facebook page", "facebook.com/<wbr>nabmeinc", "https://www.facebook.com/nabmeinc"),
        ("Facebook group", "Join our community", "https://www.facebook.com/groups/751356851659519"),
        ("Instagram", "@nabmeinc", "https://www.instagram.com/nabmeinc"),
        ("LinkedIn", "NABME Inc", "https://www.linkedin.com/in/nabme-inc-50474a26a"),
    ]
    acc = "".join(f'<a class="card card-link account-card" href="{u}"{EXT}><p class="kicker red">{n}</p><h3>{h}</h3><span class="more">Follow {ARROW}</span></a>' for n, h, u in accounts)
    filters = "".join(f'<span class="chip" style="border-color:var(--rule)">{f}</span>' for f in ["All", "NABME", "Community", "Summit", "Athari"])
    tiles = ig_grid(IG_WALL)
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("NABME Live")}<h1>The movement, in <span class="red">real time</span>.</h1><p class="lede">See what our educators, Fellows and partners are sharing. Tag @nabmeinc and use #NABME to join the conversation.</p><div class="btn-row">{btn("Follow on Instagram", "https://www.instagram.com/nabmeinc", "red", True, EXT)}{btn("Follow on Facebook", "https://www.facebook.com/nabmeinc", "outline", True, EXT)}</div></div></section>
<section class="section"><div class="wrap">
  <div class="chips" style="margin:0 0 20px" aria-label="Filters">{filters}</div>
  {tiles}
  <p class="source" style="margin-top:16px">Recent posts from @nabmeinc and collaborators. Once a social-wall service is connected, the wall shows NABME's own posts automatically. Posts from others appear after NABME approves them. Images of students are never auto-published.</p>
</div></section>
<section class="section band-stone"><div class="wrap"><div class="section-head">{eyebrow("Follow NABME")}<h2 class="h2">Find us everywhere the movement is.</h2><p class="lede">Hashtags: #NABME · #nabmeinc · #BMECapitalSummit · #AthariFellowship · #BlackMaleEducators</p></div><div class="grid-4">{acc}</div></div></section>'''
    page("/live", "NABME Live", "NABME Live: posts from NABME's educators, Fellows and partners. Tag @nabmeinc and use #NABME.", body, "news")


def build_partners():
    seen, combined = set(), []
    for n, u in PARTNERS + FUNDERS:  # one list; an organization that is both appears once
        if n not in seen:
            seen.add(n); combined.append((n, u))
    allw = "".join(logo_tile(n, u) for n, u in combined)
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("Partners and funders")}<h1>This work takes <span class="red">all of us</span>.</h1><p class="lede">Dramatically increasing the number of highly effective Black and Brown male teachers and leaders who positively affect marginalized children is a complex problem. It requires a comprehensive response, and everyone must participate in the solution. We are proud to stand with these partners and grateful to the funders who make the work possible.</p></div></section>
<section class="section" id="funders" aria-labelledby="p-h"><div class="wrap"><div class="section-head">{eyebrow("Funders + partners")}<h2 id="p-h" class="h2">The organizations we build alongside and the investors who directly support NABME.</h2></div><div class="logo-row">{allw}</div><p style="margin-top:24px"><a class="text-link text-link--red" href="/summit#funders">See the funders of the Capital Summit {ARROW}</a></p></div></section>
{closing("Partner with NABME.", "", btn("Become a partner", "/contact", "light") + btn("Support the work", "/donate", "ghost", False))}'''
    page("/partners", "Partners and Funders", "NABME's partners and funders, from Education Forward DC to The Annie E. Casey Foundation.", body, "partners")


def dumbbell_svg():
    rows = [("Storytelling & Branding", 1.40, 3.14, 124), ("Challenging the Status Quo", 1.29, 2.86, 122), ("Fostering Inclusivity", 1.43, 3.14, 120), ("Embracing Uncertainty", 1.33, 2.86, 114), ("Impact Measurement", 1.43, 2.86, 100), ("Diagnosing Adaptive Challenges", 1.71, 3.14, 83), ("Emotional Intelligence", 1.67, 3.00, 80)]
    W, left, right, top, rowh = 860, 240, 800, 20, 50
    x = lambda v: left + (v - 1) / 3 * (right - left)
    H = top + rowh * len(rows) + 40
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="db-t db-d"><title id="db-t">Fellows grew 80% to 124% in every leadership competency</title><desc id="db-d">Self-rating before and after the Fellowship on a 1 to 4 scale, six Cohort 2 Fellows. ' + "; ".join(f"{n}: {b:.2f} to {a:.2f}, plus {p}%" for n, b, a, p in rows) + ".</desc>"]
    for v in range(1, 5):
        parts.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top - 6}" y2="{top + rowh * len(rows)}" stroke="#e2e1da" stroke-dasharray="3 4"/><text x="{x(v):.1f}" y="{top + rowh * len(rows) + 22}" text-anchor="middle" font-size="12" fill="#585a56" font-family="Inter">{v}</text>')
    for i, (n, b, a, p) in enumerate(rows):
        y = top + rowh * i + rowh / 2
        parts.append(f'<text x="{left - 18}" y="{y + 4:.1f}" text-anchor="end" font-size="14" font-weight="600" fill="#1b1c1b" font-family="Inter">{e(n)}</text>')
        parts.append(f'<line x1="{x(b):.1f}" x2="{x(a):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e8a3ad" stroke-width="3"/>')
        parts.append(f'<circle cx="{x(b):.1f}" cy="{y:.1f}" r="7" fill="#b9bab3"/><circle cx="{x(a):.1f}" cy="{y:.1f}" r="9" fill="#c51f36"/>')
        parts.append(f'<text x="{x(a) + 16:.1f}" y="{y + 5:.1f}" font-size="15" font-weight="800" fill="#c51f36" font-family="Inter">+{p}%</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_athari():
    timeline = [
        ("SY 2021–2024 · Three-year pilot", "Cohort 1", "8 Fellows · all 8 completed · 100% still in education · all 8 now in leadership roles", "is-first"),
        ("SY 2024–2026 · Complete", "Cohort 2", "10 Fellows · all 10 completed · 100% still in education · 7 promoted for SY 2026–27", "is-done"),
        ("SY 2025–2027 · Year 2", "Cohort 3", "3 Fellows continuing · Marquis Duncan promoted mid-program", "is-done"),
        ("SY 2026–2028 · Year 1", "Cohort 4", "8 new Fellows launched September 2026", "is-now"),
    ]
    tl = "".join(f'<div class="tl {c}"><p class="tl__when">{w}</p><h3>{t}</h3><p>{d}</p></div>' for w, t, d, c in timeline)
    year = [
        ("Summer", "Summer Retreat", "Shared housing to launch the cohort and build trust from day one.", True, "athari_lawn"),
        ("Monthly", "Leadership Classes", "Co-facilitated by seasoned school leaders Shawn Hardnett and Dr. Rictor Craig.", False, "p_session"),
        ("On campus", "Shadow Days", "A day alongside sitting leaders at Statesmen Academy for Boys.", True, "arrival"),
        ("Winter", "The Capital Summit", "The field-wide convening of Black male educators that anchors the year.", False, "s26_aerial"),
        ("On the road", "BMEC-Philly", "A travel cohort to the national Black Male Educators Convening.", True, "bmec"),
        ("Spring", "The Lake House Retreat", "Fireside dialogue and a cooking challenge, away from city, screens and school.", False, "athari_lake"),
    ]
    yc = "".join(f'<article class="card {"card--bar-red" if r else "card--bar"}"><figure>{img(ph, pos="center 30%")}</figure><div><p class="kicker{" red" if r else ""}">{k}</p><h3>{t}</h3><p>{d}</p></div></article>' for k, t, d, r, ph in year)
    cohort1 = [
        ("Jefferson BuggBey", "Statesmen Academy for Boys", "Math Instructor → Director of Instruction (Principal)"),
        ("Charles Williams", "E.L. Haynes PCS", "ELA Instructor → Dean of Instruction"),
        ("Javan Carter", "Frederick Douglass HS (Baltimore)", "ELA Specialist → Assistant Principal"),
        ("Melvin Smith", "Statesmen Academy for Boys", "Behavior Tech → Behavior Support Coordinator"),
        ("Michael Carswell", "Washington Leadership Academy PCS", "ELA Instructor → Grade Level Lead"),
        ("Garry Cameron", "Friendship Public Charter Schools", "Math Instructor → Academy Director (AP)"),
        ("Cameron Hollis", "Friendship Public Charter Schools", "Ed Tech Coach → IB PYP Coordinator"),
        ("Darryl Groves", "District of Columbia Public Schools", "Physical Health Instructor → Dean of Schools"),
    ]
    fw1 = "".join(f'<li><time style="color:var(--ink);font-weight:700">{e(n)}</time><div><b>{e(r)}</b><span>{e(s)}</span></div><span></span></li>' for n, s, r in cohort1)
    fellows = [
        ("Anthony Whaley", "Ingenuity Prep PCS", "Director of Literacy (SY 26–27; formerly Vice Principal, KIPP DC)"),
        ("Tyrell Dale", "Statesmen College Prep", "English Teacher → Dean of Instruction (SY 26–27)"),
        ("Christian Rowe", "Friendship Public Charter School", "Dean of Students (SY 26–27; formerly STEM Teacher, Statesmen)"),
        ("Zyshonne Small", "Statesmen Academy for Boys", "Lead Kings 101 Teacher → Dean of Instruction (SY 26–27)"),
        ("Emmanuel Antwi", "Statesmen College Prep", "Lead Kings Instructor → Dean of School Culture (SY 26–27)"),
        ("LaBront Makle", "KIPP DC", "Associate Director of Compliance (promoted mid-program)"),
        ("Tarrence Hughes", "KIPP Legacy College Prep", "Dean of Culture"),
        ("Rashad Wilkerson", "Bishop McNamara High School", "Director of Admissions, Enrollment, & Communications"),
        ("Jarrell Pittman", "KIPP DC", "PBIS Coordinator / Restorative Practices Teacher"),
        ("Jacquez Jefferson", "Statesmen College Prep", "Kings 6 Instructor → Dean of School Community and Culture (SY 26–27)"),
    ]
    fw = "".join(f'<li><time style="color:var(--ink);font-weight:700">{e(n)}</time><div><b>{e(r)}</b><span>{e(s)}</span></div><span></span></li>' for n, s, r in fellows)
    more_quotes = [
        ("Having meaningful and motivating conversations with Mr. Craig and Mr. Hardnett gave way to such invigorating feelings about the potential impact we can make in education. Them speaking life into us brought forth so much affirmation and confidence about our journey.", "Cohort 3 Fellow"),
        ("I overall enjoyed and was heavily impacted by the experience. I believe that the innovative and fine-tailored development of Black men done as part of this fellowship is one of a kind.", "Jarrell Pittman, Cohort 2"),
    ]
    mq = "".join(f'<blockquote class="voice"><p>“{e(q)}”</p><cite>{e(c)}</cite></blockquote>' for q, c in more_quotes)
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("p_talk", eager=True, pos="center 30%")}</div><div class="wrap">
  {eyebrow("NABME · Flagship leadership program")}
  <h1>The Athari <span class="red">Fellowship</span></h1>
  <p class="phero__meta"><strong>Athari</strong> <em>(Swahili)</em>: <span class="red">impact.</span></p>
  <p class="lede">A brotherhood, a leadership lab and a healing space for Black male educators across the DMV.</p>
  <div class="btn-row">{btn("Join the interest list", "#interest")}{btn("Read the impact report", "/impact#athari", "ghost", False)}</div>
  <p class="source" style="margin-top:28px;letter-spacing:.14em;font-weight:700;text-transform:uppercase;font-size:.75rem;color:#fff">Partnership · Protection · Proximity · Practice</p>
</div></section>

<section class="section"><div class="wrap split">
  <div>{eyebrow("What Athari is")}<h2 class="h2">Two years. One brotherhood.</h2></div>
  <div class="prose"><p>The Athari Fellowship is NABME's flagship leadership development program for Black male educators across the DMV region. It is a brotherhood, a leadership lab, and a healing space, built on four pillars that anchor every session, retreat, and convening.</p><p>Athari is a two-year program. Fellows meet monthly with seasoned school leaders, travel together, retreat together, and practice new leadership moves in their own buildings, with feedback from the men beside them and the supervisors above them.</p><p>The Fellowship is co-facilitated by Shawn Hardnett and Dr. Rictor Craig.</p></div>
</div></section>

{pillars_section()}

<section class="section" aria-labelledby="tl-h"><div class="wrap"><div class="section-head">{eyebrow("The Athari Fellowship over the years")}<h2 id="tl-h" class="h2">Each cohort builds on the last.</h2></div><div class="timeline">{tl}</div></div></section>

<section class="section band-stone" aria-labelledby="num-h"><div class="wrap">
  <div class="section-head">{eyebrow("2021–2026 · Five years in numbers")}<h2 id="num-h" class="h2">31 Fellows. Four cohorts. Every completer still in education.</h2><p class="lede">Across five years and four cohorts, the Athari Fellowship has served thirty-one Black male educators through class sessions, residential retreats, the Black Male Educator Capital Summit at Howard University, and the BMEC-Philly convening.</p></div>
  <div class="metrics">
    <div class="metric metric--dark"><span class="metric__num" data-count="31">31</span><span class="metric__label">Fellows served across four cohorts</span></div>
    <div class="metric metric--dark"><span class="metric__num" data-count="100" data-suffix="%">100%</span><span class="metric__label">Cohort 1 and 2 Fellows still in education (18 of 18)</span></div>
    <div class="metric metric--dark"><span class="metric__num" data-count="83" data-suffix="%">83%</span><span class="metric__label">Cohort 1 and 2 Fellows in leadership roles (15 of 18)</span></div>
    <div class="metric"><span class="metric__num num-red" data-count="104" data-prefix="+" data-suffix="%">+104%</span><span class="metric__label">Avg. growth in adaptive leadership</span></div>
    <div class="metric"><span class="metric__num" data-count="6">6</span><span class="metric__label">Fellows promoted mid-program · Cohorts 1, 2 and 3</span></div>
    <div class="metric"><span class="metric__num" data-count="19">19</span><span class="metric__label">Class sessions · 87% attendance</span></div>
    <div class="metric"><span class="metric__num"><span data-count="4.10" data-dec="2">4.10</span><small>/5</small></span><span class="metric__label">Supervisor 360 leadership rating</span></div>
    <div class="metric"><span class="metric__num num-red"><span data-count="9.9" data-dec="1">9.9</span><small>/10</small></span><span class="metric__label">Capital Summit likelihood to recommend</span></div>
    <div class="metric"><span class="metric__num"><span data-count="4.83" data-dec="2">4.83</span><small>/5</small></span><span class="metric__label">Networking with Black male educators</span></div>
  </div>
  <p style="margin-top:24px">{btn("Read the Athari impact report", "/impact#athari", "outline")}</p>
</div></section>

<section class="section band-dark wedge" aria-labelledby="ret-h"><div class="wrap split--even split">
  <div>{eyebrow("Cohorts 1 and 2 · The headline")}<h2 id="ret-h" class="big-claim">100% retained. <span>83% in leadership.</span></h2><p class="lede" style="margin-top:22px">Across Cohorts 1 and 2, all 18 Fellows are still in education, and 15 of 18 hold formal leadership positions. Six Fellows across Cohorts 1, 2 and 3 were promoted mid-program.</p></div>
  <div class="promo"><h3>Where they lead today</h3><ul><li><b>1</b> Principal</li><li><b>7</b> Deans</li><li><b>2</b> Assistant Principals</li><li><b>2</b> Directors</li><li><b>2</b> Coordinators</li><li><b>1</b> Grade Level Lead</li></ul><p>Mid-program promotions: 4 Cohort 1 Fellows during the pilot's first year · LaBront Makle (Cohort 2) → Associate Director of Compliance, KIPP DC · Marquis Duncan (Cohort 3) → Instructional Leadership Coach</p></div>
</div></section>

<section class="section" aria-labelledby="lead-h"><div class="wrap">
  <div class="section-head">{eyebrow("Where our Fellows lead")}<h2 id="lead-h" class="h2">Our Fellows, in their roles today.</h2></div>
  <h3 style="font-size:1.2rem;margin-bottom:6px">Cohort 1 · SY 2021–2024</h3>
  <ul class="cov">{fw1}</ul>
  <h3 style="font-size:1.2rem;margin:36px 0 6px">Cohort 2 · SY 2024–2026</h3>
  <ul class="cov">{fw}</ul>
</div></section>

<section class="section band-stone" aria-labelledby="grow-h"><div class="wrap">
  <div class="section-head">{eyebrow("Pillar IV · Practice")}<h2 id="grow-h" class="h2">Fellows grew 80% to 124% in every leadership competency.</h2><p class="lede">Athari measures leadership growth from three angles: Fellows' own self-assessment, 360 reviews completed by their direct supervisors, and before/after capability ratings. Across all three views, the evidence points the same direction.</p></div>
  <div class="chart-card">{dumbbell_svg()}<div class="chart-legend"><span>Before</span><span class="after">After</span></div><p class="source" style="margin-top:8px">Self-rating before vs. after the Fellowship · 1 = basic awareness, 4 = advanced (could teach it) · six Cohort 2 Fellows, end-of-year survey</p></div>
  <div class="metrics" style="margin-top:12px">
    <div class="metric"><span class="metric__num">3.94<small>/5</small></span><span class="metric__label">Fellow self-assessment across 20 leadership items</span></div>
    <div class="metric"><span class="metric__num">4.10<small>/5</small></span><span class="metric__label">Mid-year supervisor 360 across 24 dimensions · 83% Agree or Strongly Agree</span></div>
    <div class="metric metric--red"><span class="metric__num">+104%</span><span class="metric__label">Average growth in adaptive leadership capability</span></div>
  </div>
  <blockquote class="pull" style="margin:40px 0 0;max-width:66ch">“He advocates effectively for both his students and the teaching team he leads. When he identifies a school system in need of refinement, he does not wait for others to find a solution; instead, he takes the initiative to spearhead the work and present a viable option to the team.”<cite>Direct Supervisor of a Cohort 2 Fellow</cite></blockquote>
</div></section>

<section class="section" aria-labelledby="year-h"><div class="wrap"><div class="section-head">{eyebrow("Inside an Athari year")}<h2 id="year-h" class="h2">Leadership is built in the room, on the road and at the table.</h2></div><div class="year">{yc}</div></div></section>

<section class="section band-stone" aria-labelledby="voices-h"><div class="wrap">
  <div class="section-head">{eyebrow("Fellow voices")}<h2 id="voices-h" class="h2">In their own words.</h2></div>
  {quote_carousel()}
  <div class="voices" style="margin-top:28px">{mq}</div>
</div></section>

<section class="section"><div class="wrap split">
  <div>{eyebrow("Looking ahead · SY 2026–2027")}<h2 class="h2">We listen to our Fellows.</h2></div>
  <p class="statement" style="font-size:clamp(1.25rem,2vw,1.6rem)">This year we are adding a published scope and sequence with anchoring texts, a Fellow-facing digital library of frameworks and tools, quarterly peer coaching triads, expanded shadow days and one-on-one coaching, and an Athari Alumni network.</p>
</div></section>

<section class="section band-stone" id="interest"><div class="wrap split">
  <div>{eyebrow("For educators")}<h2 class="h2">Join the interest list for the next cohort.</h2><p class="lede" style="margin-top:14px">Be first to hear when applications open for Cohort 5.</p>
    <div class="grid-2" style="margin-top:28px"><a class="card card-link card--bar-red" href="/nominate"><h3>School leaders</h3><p>Nominate a Fellow from your team.</p><span class="more">Nominate a Fellow {ARROW}</span></a><a class="card card-link card--bar" href="/donate"><h3>Funders</h3><p>Sponsor a Fellow's two-year journey.</p><span class="more">Sponsor a Fellow {ARROW}</span></a></div>
    <p id="report" class="note" style="margin-top:22px">Read the <a href="/impact#athari">Athari Fellowship Impact Report, 2021–2026</a>, or <a href="{REPORTS["athari"][2]}"{EXT}>open the full report deck</a>.</p>
  </div>
  <div class="form-panel form-wrap"><form class="form" data-form="Athari Interest"><div class="form-grid">
    {field("Name", "name", required=True, auto="name")}
    {field("Email", "email", "email", required=True, auto="email")}
    {field("School", "school", required=True, auto="organization")}
    {field("Role", "role", required=True)}
    {field("Years in education", "years", required=True, options=["0–3 years", "4–7 years", "8–12 years", "13+ years"])}
  </div><div><button class="btn btn--red" type="submit">Join the interest list</button></div></form>
  {success("You're on the list.", "We'll email you when applications open for the next Athari cohort.")}</div>
</div></section>

{closing("To the Black men of Athari, who showed up and told us the truth: thank you.", "", btn("Join the interest list", "#interest", "light") + btn("Give to the Summit", "/donate", "ghost", False))}'''
    page("/athari", "The Athari Fellowship", "The Athari Fellowship, Swahili for impact, is NABME's two-year leadership program for Black male educators.", body, "programs")


def report_card(key, nums):
    name, years, deck = REPORTS[key]
    stats = "".join(f'<li><b>{n}</b><span>{l}</span></li>' for n, l in nums)
    return f'<article class="report"><p class="report__years">{years}</p><h3>{name}</h3><ul class="report__stats">{stats}</ul><div class="btn-row"><a class="btn btn--red btn--sm" href="#{key}">Read the highlights {ARROW}</a><a class="btn btn--outline btn--sm" href="{deck}"{EXT}>Open the full report</a></div></article>'


def build_impact():
    cards = (report_card("nabme", [("50,000+", "educators reached"), ("20+", "states"), ("2016", "founded")])
             + report_card("athari", [("31", "Fellows served"), ("100%", "retained"), ("83%", "in leadership")])
             + report_card("summit", [("310+", "registered or waitlisted"), ("97", "Net Promoter Score"), ("4.97/5", "satisfaction")]))
    m = lambda num, label, cls="": f'<div class="metric {cls}"><span class="metric__num">{num}</span><span class="metric__label">{label}</span></div>'
    programs = [("Athari Fellowship", "Two-year leadership development fellowship for Black male educators in the DMV region.", "/athari"),
                ("Capital Summit", "Annual national convening at Howard University for professional development and collective strategy.", "/summit"),
                ("Martha's Vineyard Series", "An August residential program combining professional development with wellness and strategic planning.", "/events"),
                ("Educator Fair", "A recruitment event connecting Black and Brown male educators with schools and districts.", "/careers"),
                ("Digital Platform", "A resume portal, job board and resource library at nabme.org.", "/talent")]
    pc = "".join(f'<a class="card card-link card--bar{"-red" if i % 2 == 0 else ""}" href="{h}"><h3>{t}</h3><p>{d}</p><span class="more">Learn more {ARROW}</span></a>' for i, (t, d, h) in enumerate(programs))
    cohorts = [("Cohort 1 (pilot)", "SY 2021–2024", "8", "Completed · all 8 in leadership roles"), ("Cohort 2", "SY 2024–2026", "10", "Completed · 7 promoted for SY 2026–27"),
               ("Cohort 3", "SY 2025–2027", "3 continuing", "Active, Year 2"), ("Cohort 4", "SY 2026–2028", "8 new", "Active, Year 1")]
    ct = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in cohorts)
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("p_lineup", eager=True, pos="center 35%")}</div><div class="wrap">
  {eyebrow("Who we are · Our impact")}
  <h1>Ten years of <span class="red">impact</span>.</h1>
  <p class="lede">Since 2016, NABME has reached more than 50,000 educators, built a fellowship where every completer is still in education, and launched a national Summit that drew 310+ educators from 20+ states.</p>
</div></section>

<section class="section" aria-labelledby="reports-h"><div class="wrap">
  <div class="section-head">{eyebrow("Impact reports")}<h2 id="reports-h" class="h2">Three reports. One movement.</h2></div>
  <div class="reports">{cards}</div>
</div></section>

<section class="section band-stone" id="nabme" aria-labelledby="nabme-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("NABME Organizational Impact Report · 2016–2026")}<h2 id="nabme-h" class="h2">From grassroots PD to a national movement.</h2></div><a class="btn btn--outline" href="{REPORTS["nabme"][2]}"{EXT}>Open the full report {ARROW}</a></div>
  <div class="split" style="margin-bottom:36px"><p class="lede">Founded in 2016 and self-funded for five years by its founder, Dr. Rictor Craig, NABME reached over 10,000 educators through free instructional professional development across D.C.</p><p class="lede">In 2021, NewSchools Venture Fund became NABME's first major investor, catalyzing the Athari Fellowship, the Capital Summit, and a national movement spanning 20+ states.</p></div>
  <div class="metrics">
    {m("50,000+", "Educators reached, 2016–2026", "metric--red")}
    {m("5 years", "Self-funded, grassroots operations")}
    {m("31", "Athari Fellows served")}
    {m("100%", "Athari retention, Cohorts 1 and 2", "metric--dark")}
    {m("83%", "Athari leadership ascension", "metric--dark")}
    {m("+104%", "Avg. leadership growth")}
    {m("310+", "Summit registrants and waitlist")}
    {m("97", "Summit Net Promoter Score")}
    {m("20+", "States represented")}
  </div>
  <h3 style="font-size:1.3rem;margin:48px 0 16px">Our programs</h3>
  <div class="grid-3">{pc}</div>
</div></section>

<section class="section" id="athari" aria-labelledby="athari-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Athari Fellowship Impact Report · 2021–2026")}<h2 id="athari-h" class="h2">100% retained. 83% in leadership.</h2></div><a class="btn btn--outline" href="{REPORTS["athari"][2]}"{EXT}>Open the full report {ARROW}</a></div>
  <p class="lede" style="margin-bottom:32px;max-width:70ch">Across five years and four cohorts, the Athari Fellowship has served 31 Black male educators. All 18 Fellows in Cohorts 1 and 2 are still in education, and 15 of 18 hold formal leadership positions.</p>
  <div class="metrics">
    {m("31", "Fellows served across four cohorts", "metric--dark")}
    {m("18 / 18", "Cohort 1 and 2 Fellows still in education", "metric--dark")}
    {m("15 / 18", "In leadership positions", "metric--red")}
    {m("6", "Fellows promoted mid-program")}
    {m("+104%", "Avg. growth in adaptive leadership (range +80% to +124%)")}
    {m("87%", "Attendance across 19 class sessions")}
    {m("3.94/5", "Fellow self-assessment, 20 leadership items")}
    {m("4.10/5", "Supervisor 360 rating · 83% Agree or Strongly Agree")}
    {m("4.83/5", "Networking with other Black male educators")}
  </div>
  <div style="overflow-x:auto;margin-top:36px"><table class="data-table"><caption class="sr">Athari cohorts</caption><thead><tr><th scope="col">Cohort</th><th scope="col">School years</th><th scope="col">Fellows</th><th scope="col">Status</th></tr></thead><tbody>{ct}</tbody></table></div>
  <p style="margin-top:24px"><a class="text-link text-link--red" href="/athari">Explore the Athari Fellowship {ARROW}</a></p>
</div></section>

<section class="section band-stone" id="summit" aria-labelledby="summit-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Black Male Educator Capital Summit Impact Report · 2026")}<h2 id="summit-h" class="h2">310+ educators demanded entry.</h2></div><a class="btn btn--outline" href="{REPORTS["summit"][2]}"{EXT}>Open the full report {ARROW}</a></div>
  <p class="lede" style="margin-bottom:32px;max-width:70ch">On February 28, 2026, the inaugural Summit brought together 190+ registered Black male educators, leaders and allies in Washington, D.C. A waitlist of 120+ more signaled demand that exceeded capacity by more than 60%.</p>
  <div class="metrics">
    {m("310+", "Registered or waitlisted", "metric--red")}
    {m("97", "Net Promoter Score", "metric--dark")}
    {m("100%", "Would recommend", "metric--dark")}
    {m("190+", "Confirmed registrants")}
    {m("120+", "Waitlisted educators")}
    {m("20+", "States represented")}
    {m("4.97/5", "Overall satisfaction")}
    {m("4.92/5", "Brotherhood and community")}
    {m("4.88/5", "Session relevance")}
  </div>
  <p class="source" style="margin-top:18px">95% of respondents would pay to attend a larger future Summit. 94% said session pacing was \"just right.\" 47% of attendees have 13+ years in education.</p>
  <p style="margin-top:24px"><a class="text-link text-link--red" href="/summit">Relive the 2026 Summit {ARROW}</a></p>
</div></section>

{closing("Help us write the next ten years.", "", btn("Support NABME", "/donate", "light") + btn("Partner with us", "/partners", "ghost", False))}'''
    page("/impact", "Our Impact", "NABME's impact reports: the organization since 2016, the Athari Fellowship since 2021, and the 2026 Black Male Educator Capital Summit.", body, "who")


def build_summit():
    whocame = {
        "Years in education": [("13+ years", 47), ("8–12 years", 27), ("4–7 years", 17), ("0–3 years", 9)],
        "Professional focus": [("School / system leadership", 43), ("Instructional leadership", 17), ("Student culture", 15), ("Classroom practice", 13), ("Aspiring leader", 12)],
        "Why they came": [("Community & connection", 78), ("Professional growth", 69), ("Leadership development", 59), ("Instructional practices", 16)],
    }
    bars = "".join(f'<div><h3>{g}</h3>' + "".join(f'<div class="bar{" is-top" if i == 0 else ""}"><div class="bar__top"><span>{e(l)}</span><b>{v}%</b></div><div class="bar__track"><i style="--w:{v}%"></i></div></div>' for i, (l, v) in enumerate(items)) + "</div>" for g, items in whocame.items())
    challenges = [
        ("Isolation and underrepresentation", "Being the only, or one of very few, Black male educators in a building, district or leadership team."),
        ("Burnout and disproportionate labor", "Expected to serve as teacher, mentor, disciplinarian, counselor, cultural translator and role model at once."),
        ("Navigating white spaces", "Tone-policed, expertise questioned, reduced to behavior-management roles."),
        ("Lack of mentorship and pipeline", "No structured pathways for Black male leadership development and succession."),
        ("A chilling climate", "A political environment that discourages equity-centered leadership and programming."),
    ]
    brings = ["Authentic relationship-building and trust", "Culturally responsive, equity-centered leadership", "Systems-level strategic thinking and innovation", "Deep content expertise and instructional knowledge", "Empathy, emotional intelligence and servant leadership", "Resilience and the ability to thrive under pressure", "Community building and mentorship"]
    sessions = [("Subversive Leadership", "An AI tool, “Zmara,” for reflective leadership."), ("Affinity + Accountability", "“Affinity is not cheerleading — it's a mirror.”"), ("History Echoes", "Deep dialogue on schooling and Black boys."), ("Instructional Rigor", "The “rigor slingshot” framework."), ("Mentorship Matters", "Dr. Kunjufu's blueprint for mentoring.")]
    voices = [("Just being in a room full of other Black and Brown male educators was amazing.", "Brian Byrd · Life Skills Coach"), ("Every breakout session and every plenary speaker were superb.", "Jermall Wright · Superintendent, Little Rock SD"), ("E V E R Y T H I N G. The whole summit was powerful and very uplifting!", "Abu Sillah · ELA Teacher, Howard Univ. MS"), ("I am motivated to finish my doctorate degree that focused on Black male educators.", "Anthony Peña · Deputy COO, Boston Public Schools")]
    sw = "".join(logo_tile(n, u) for n, u in SUMMIT_FUNDERS)
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_aerial", eager=True, pos="center 40%")}</div><div class="wrap">
  {eyebrow("Summit 2027 · " + SUMMIT_DATES + " · Washington, D.C.")}
  <h1>The Black Male Educator <span class="red">Capital Summit</span></h1>
  <p class="lede" style="margin-top:16px">Three days in Washington, D.C.: the Capitol Hill Fly-In, the Black Boy Hackathon and the Summit at Howard University. {"Registration is open: " + SUMMIT_FEE + " per educator." if SUMMIT_REG_OPEN else "The call for proposals is open through " + CFP_DEADLINE + "."}</p>
  <div class="btn-row" style="margin-top:26px">{summit_register_btn("red")}<button class="btn btn--ghost" type="button" data-film>{ic("play")} Watch the 2026 Summit recap</button></div>
</div></section>
{summit_tabs("overview")}

<section class="section band-dark" aria-labelledby="days-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Save the dates")}<h2 id="days-h" class="h2">{SUMMIT_DATES}</h2></div>{countdown_block(buttons=False)}</div>
  {summit_days()}
</div></section>

<section class="section" style="padding-top:0;padding-bottom:0" id="notify-form"><div class="wrap">{summit_banner()}</div></section>

<section class="section" id="funders" aria-labelledby="sf-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Summit funders")}<h2 id="sf-h" class="h2">Thank you to the funders of the Capital Summit.</h2><p class="lede" style="margin-top:12px">These organizations fund the Black Male Educator Capital Summit itself. Summit funders are recognized here.</p></div><p id="sponsor">{btn("Fund the Summit", "/contact", "outline")}</p></div>
  <div class="logo-row">{sw}</div>
</div></section>

<section class="section"><div class="wrap split">
  <div>{eyebrow("About the Summit")}<h2 class="h2">A movement, not a moment.</h2></div>
  <div class="prose"><p>On February 28, 2026, the inaugural Summit convened in Washington, D.C., bringing together more than 190 registered Black male educators, leaders, and allies for a historic day of professional development, fellowship, and collective strategy.</p><p>The response was extraordinary: over 310 educators registered or joined the waitlist, representing more than 20 states and spanning every level of the education system.</p><p>The Summit was not simply a professional development event. It was a declaration that Black male educators are not ancillary to the American education project, but essential to it. A movement, not a moment.</p></div>
</div></section>

{slide_strip(["s26_stage", "p_howard", "s26_kid", "p_audience", "s26_speaker", "p_panel", "p_onstage", "s26_smiles"], "Moments from the 2026 Summit", "center 40%")}

<section class="section band-stone" id="numbers" aria-labelledby="n-h"><div class="wrap">
  <div class="section-head section-head--row"><div>{eyebrow("Inaugural Summit · February 28, 2026")}<h2 id="n-h" class="h2">Demand outran the room by more than 60%.</h2></div>{btn("Read the 2026 impact report", "/impact#summit", "outline")}</div>
  <div class="metrics">
    <div class="metric metric--red metric--tall"><span class="metric__num" data-count="310" data-suffix="+">310+</span><span class="metric__label">Educators registered or waitlisted</span><span class="metric__note">190+ confirmed registrants and 120+ more on the waitlist, from 20+ states.</span></div>
    <div class="metric metric--dark"><span class="metric__num" data-count="97">97</span><span class="metric__label">Net Promoter Score</span></div>
    <div class="metric metric--dark"><span class="metric__num" data-count="100" data-suffix="%">100%</span><span class="metric__label">Would recommend</span></div>
    <div class="metric"><span class="metric__num"><span data-count="4.97" data-dec="2">4.97</span><small>/5</small></span><span class="metric__label">Overall satisfaction</span></div>
    <div class="metric"><span class="metric__num" data-count="15" data-suffix="+">15+</span><span class="metric__label">Breakout sessions</span></div>
  </div>
</div></section>

<section class="section" aria-labelledby="who-h"><div class="wrap">
  <div class="section-head">{eyebrow("Who came to the 2026 Summit")}<h2 id="who-h" class="h2">Seasoned leaders, and the brotherhood they came for.</h2></div>
  <div class="bars">{bars}</div>
  <p class="source" style="margin-top:20px">Share of survey respondents. “Why they came”: participants could pick up to two reasons, so shares add to more than 100%.</p>
  <blockquote class="pull" style="margin:40px 0 0;max-width:60ch">“Finding spaces for Black male educators to connect and convene.”<cite>Casey Ambrose, Physics Teacher, Washington Leadership Academy</cite></blockquote>
</div></section>

<section class="section band-stone" aria-labelledby="heard-h"><div class="wrap">
  <div class="section-head">{eyebrow("What we heard")}<h2 id="heard-h" class="h2">The weight they carry. The gifts they bring.</h2></div>
  <div class="heard">
    <div><h3>The challenges they carry</h3><ul>{"".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in challenges)}</ul></div>
    <div><h3>What they bring</h3><ul class="plain">{"".join(f"<li>{x}</li>" for x in brings)}</ul><blockquote class="pull" style="margin:28px 0 0">“I bring a justice-centered, relationship-driven leadership approach rooted in integrity, cultural humility, and an unwavering commitment to protecting the dignity and potential of young people.”<cite>Jamial Black, Executive Director</cite></blockquote></div>
  </div>
</div></section>

<section class="section" aria-labelledby="sess-h"><div class="wrap">
  <div class="section-head">{eyebrow("2026 session highlights")}<h2 id="sess-h" class="h2">Sessions rated 4.88 / 5.</h2></div>
  <div class="grid-4 sessions-grid">{"".join(f'<article class="card card--bar{"-red" if i % 2 == 0 else ""}"><h3>{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(sessions))}</div>
  <p class="source" style="margin-top:16px">Average session ratings of 4.88 / 5 for relevance and for practical application.</p>
</div></section>

<section class="section band-stone" aria-labelledby="v-h"><div class="wrap">
  <div class="section-head">{eyebrow("In their voices · 2026")}<h2 id="v-h" class="h2">“Can't put a price tag on excellence.”</h2><p class="lede">Le Quan Graham, 2nd Grade Teacher</p></div>
  <div class="voices">{"".join(f'<blockquote class="voice"><p>“{e(q)}”</p><cite>{e(c)}</cite></blockquote>' for q, c in voices)}</div>
</div></section>

<section class="section" style="padding-top:0" aria-labelledby="give-h"><div class="wrap"><div class="summit-banner">
  <div>{eyebrow("Give to the movement")}<h2 id="give-h">Every seat is a <span>statement</span>.</h2><p class="lede" style="margin-top:14px">Your gift puts a Black male educator in the room, keeps the Summit open to every educator, and fuels NABME's work all year long.</p><div class="btn-row" style="margin-top:22px">{btn("Give to the Summit", "/donate#give")}{btn("Support NABME", "/donate", "ghost", False)}</div><p style="margin-top:14px"><a href="/donate#give" style="color:#fff">Give in honor of a Black male educator who shaped you</a></p></div>
  <div class="metric metric--dark" style="background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.16)"><span class="metric__num" data-count="120" data-suffix="+">120+</span><span class="metric__label">Educators were waitlisted for the inaugural Summit. Help us make room.</span></div>
</div></div></section>

{closing("See you at Howard.", SUMMIT_DATES + " · Washington, D.C.", summit_register_btn("light") + btn("Become a sponsor", "#sponsor", "ghost", False))}
<dialog id="film" aria-label="The 2026 Black Male Educator Summit recap"><div class="dialog-bar"><span>The 2026 Black Male Educator Summit</span><button class="dialog-close" type="button" data-close aria-label="Close film">{ic("x")}</button></div><div class="film"><iframe title="The 2026 Black Male Educator Summit recap" data-src="{FULL_FILM}" src="about:blank" allow="autoplay; fullscreen" allowfullscreen></iframe></div></dialog>'''
    page("/summit", "The Black Male Educator Capital Summit", "The Black Male Educator Capital Summit: relive 2026 and get notified when Summit 2027 details are released.", body, "programs")


def build_summit_register():
    days = [f"{w}, {d}: {t}" for w, d, t, _ in SUMMIT_DAYS]
    day_boxes = "".join(f'<label class="check"><input type="checkbox" name="days" value="{e(x)}" checked> {e(x)}</label>' for x in days)
    pay = SUMMIT_PAY_URL
    note = ("After you submit, you'll continue to PayPal to pay the " + SUMMIT_FEE + " registration fee with a card or your PayPal account.") if pay else ("After you submit, NABME will email you a secure link to pay the " + SUMMIT_FEE + " registration fee.")
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_aerial", eager=True, pos="center 40%")}</div><div class="wrap">
  <p class="crumbs"><a href="/summit" style="color:#fff">The Capital Summit</a> / Register</p>
  {eyebrow("Summit 2027 · " + SUMMIT_DATES + " · Washington, D.C.")}
  <h1>Register for the <span class="red">Capital Summit</span></h1>
  <p class="lede">Three days of advocacy, innovation and brotherhood. Registration is {SUMMIT_FEE} per educator.</p>
</div></section>

<section class="section"><div class="wrap reg-layout">
  <aside class="reg-aside">
    <div class="reg-fee"><span>Registration</span><b>{SUMMIT_FEE}</b><small>per educator</small></div>
    <h2 class="h2" style="font-size:1.4rem;margin:26px 0 14px">What's happening</h2>
    <ul class="reg-days">{"".join(f'<li><span>{w} · {d}</span><b>{t}</b><p>{x}</p></li>' for w, d, t, x in SUMMIT_DAYS)}</ul>
    <p class="source" style="margin-top:14px">More events will be announced soon. Saturday's Summit is at Howard University.</p>
    <p class="group-note"><b>Registering a group?</b> If you are interested in a group registration purchase, email <a href="mailto:bmecsummit@nabme.org">bmecsummit@nabme.org</a>.</p>
    <p class="source" style="margin-top:14px">Questions? Email info@nabme.org.</p>
  </aside>
  <div class="form-panel form-wrap"><form class="form" data-form="Summit Registrations"{f' data-redirect="{pay}"' if pay else ""}><div class="form-grid">
    <h2 class="field--full" style="font-size:1.25rem">About you</h2>
    {field("Full name", "name", required=True, auto="name")}
    {field("Email", "email", "email", required=True, auto="email")}
    {field("Phone", "phone", "tel", auto="tel")}
    {field("City, State", "city", required=True, auto="address-level2", placeholder="Washington, DC")}
    {field("School or organization", "org", required=True, auto="organization")}
    {field("Do you work at the K–12 or collegiate level?", "level", required=True, options=["K–12", "Collegiate (college or university)"])}
    {role_field()}
    {field("Years in education", "years", required=True, options=["0–3 years", "4–7 years", "8–12 years", "13+ years", "Not yet in education"])}
    {field("Did you attend the 2026 Summit?", "attended_2026", required=True, options=["Yes", "No"])}
    <h2 class="field--full" style="font-size:1.25rem;margin-top:10px">Your Summit</h2>
    <fieldset class="field field--full" data-required-group><legend>Which days will you attend?</legend><div class="checks" style="grid-template-columns:1fr">{day_boxes}</div><span class="err">Choose at least one day.</span></fieldset>
    {field("T-shirt size", "shirt", required=True, options=["S", "M", "L", "XL", "2XL", "3XL", "4XL"])}
    {field("How did you hear about the Summit?", "heard", options=["NABME email", "Instagram", "Facebook", "LinkedIn", "A colleague", "My school or district", "Attended in 2026", "Other"])}
    {field("Dietary needs", "dietary", placeholder="Vegetarian, allergies, etc.")}
    {field("Accessibility needs", "access", placeholder="Anything that helps you take part fully")}
    <div class="field field--full"><label class="check"><input type="checkbox" name="photo_consent" value="yes"> NABME may use photos and video of me from the Summit.</label></div>
  </div><p class="form-note">{note}</p><div><button class="btn btn--red" type="submit">{"Continue to payment" if pay else "Register"} {ARROW}</button></div></form>
  {success("You're registered.", ("Your spot is saved. Complete your " + SUMMIT_FEE + " payment on PayPal to confirm it.") if pay else ("Your spot is saved. Watch your inbox: NABME will email your " + SUMMIT_FEE + " payment link and Summit details."), btn("Back to the Summit", "/summit", "outline"))}</div>
</div></section>'''
    if not SUMMIT_REG_OPEN:
        body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("s26_aerial", eager=True, pos="center 40%")}</div><div class="wrap">
  <p class="crumbs"><a href="/summit" style="color:#fff">The Capital Summit</a> / Registration</p>
  {eyebrow("Summit 2027 · " + SUMMIT_DATES + " · Washington, D.C.")}
  <h1>Registration <span class="red">opens soon</span></h1>
  <p class="lede">Be the first to know when registration opens. Want to present? The call for proposals is open through {CFP_DEADLINE}.</p>
  <div class="btn-row">{btn("Submit a proposal", "/summit/proposals", "red")}{btn("See the Summit", "/summit", "ghost", False)}</div>
</div></section>
{summit_tabs("")}
<section class="section"><div class="wrap" style="max-width:720px">
  <h2 class="h2" style="font-size:1.6rem;margin-bottom:12px">Get notified when registration opens</h2>
  <form class="inline-form" data-inline data-table="Summit Interest" data-source="registration-closed" data-done="You're on the list" data-thanks="We'll email you the moment Summit registration opens."><label class="sr" for="em-reg">Email address</label><input id="em-reg" type="email" name="email" placeholder="you@school.org" autocomplete="email" required><button class="btn btn--red" type="submit">Notify me</button></form><p class="inline-msg" aria-live="polite"></p>
  <p class="group-note" style="margin-top:28px"><b>Registering a group?</b> If you are interested in a group registration purchase, email <a href="mailto:bmecsummit@nabme.org">bmecsummit@nabme.org</a>.</p>
</div></section>'''
    page("/summit/register", "Register for the Capital Summit", "Register for the 2027 Black Male Educator Capital Summit, February 11–13 in Washington, D.C. Registration is " + SUMMIT_FEE + ".", body, "programs")


CFP_STRANDS = [
    ("AI, Technology & Instruction", "How are Black male educators leading, adapting, and innovating in the classroom and in the age of artificial intelligence? Sessions in this strand should address high quality instructional practice and how technology is reshaping teaching, learning, and leadership, and how Black male educators can lead that transformation rather than be displaced by it. Topics may include culturally responsive pedagogy, rigorous and engaging instructional strategies, AI-powered instructional tools, digital literacy, the ethics of technology in education, or innovative classroom and school-level applications."),
    ("Civic Education", "How are Black male educators deepening their own civic knowledge and preparing the next generation for informed participation in democracy? This strand moves beyond civic engagement to civic education: equipping educators with the content knowledge, historical grounding, and pedagogical tools to teach civics with clarity and conviction. Topics may include policy literacy, the role of Black men in shaping education policy, teaching government and democracy in K–12 settings, or building civic identity among students."),
    ("Health & Wellness", "How are Black male educators sustaining themselves, physically, mentally, and financially, while sustaining the communities they serve? Sessions in this strand should address the full spectrum of wellbeing: chronic illness prevention, mental health, economic mobility, financial literacy, work-life balance, and the unique health challenges facing Black men in education. This strand is about the whole man, not just the professional."),
]


def build_summit_mission():
    strands = [
        ("Strand 1", "AI, Technology & Instruction", "Leveraging emerging tools and high quality instructional practice to strengthen teaching, learning, and leadership.",
         "Equip Black male educators with the knowledge and tools to leverage artificial intelligence, emerging technology, and high quality instructional practice to strengthen their teaching, streamline their leadership, and prepare their students for a future that is already here.",
         [("1.1", "Ensure that every attendee who engages with the AI, Technology & Instruction strand leaves with at least one AI tool or instructional strategy they can implement in their classroom or school within 30 days of the Summit."),
          ("1.2", "Demystify AI for educators who have had no formal exposure, moving them from apprehension to informed agency, with a focus on how AI can reduce their workload rather than replace their expertise."),
          ("1.3", "Showcase how AI-driven platforms can deliver personalized professional development and leadership content to Black male educators at scale, modeling the kind of innovation NABME is building through the AI-enhanced Athari Fellowship concept."),
          ("1.4", "Address the equity dimensions of AI in education: who is building it, whose data trains it, whose students benefit, and how Black male educators can be active shapers of technology rather than passive consumers.")]),
        ("Strand 2", "Civic Education (Fighting Misinformation)", "Deepening civic knowledge and equipping Black male educators to teach, lead, and advocate with clarity and conviction.",
         "Educate Black male educators on the civic structures, media ecosystems, and information landscapes that shape their communities, so they can recognize misinformation, understand the systems it exploits, and bring that knowledge back to their students and schools.",
         [("2.1", "Develop educators' media literacy and critical analysis skills so they can identify misinformation targeting their communities, and teach those skills to their students."),
          ("2.2", "Connect the Summit to the Capitol Hill Fly-In advocacy day, ensuring that civic education is not theoretical but grounded in direct experience. Educators who attend the Thursday fly-in bring firsthand knowledge of the legislative process into Saturday's sessions."),
          ("2.3", "Build a network of Black male educators who are informed, knowledgeable, and connected to one another as civic voices, so that when misinformation campaigns emerge, the response is not individual but collective.")]),
        ("Strand 3", "Health & Wellness", "General wellbeing, chronic illness prevention, and economic mobility, embedded within wellness as a dimension of whole-person health.",
         "Address the full spectrum of what it means for a Black man in education to be well, physically, mentally, and financially, because the same system that depletes Black male educators professionally also undermines their health and their wealth, and you cannot solve one without solving the others. This strand explicitly treats physical health, mental health, and financial health as interdependent.",
         [("3.1", "Mental health and general wellbeing: create space for Black male educators to name the emotional and psychological toll of the work without judgment, and provide evidence-based strategies for managing stress, burnout, and the unique mental health challenges of being a Black man in a system not designed for him."),
          ("3.2", "Chronic illness and physical health: address the chronic illnesses that disproportionately impact Black men (hypertension, diabetes, heart disease, and stress-related conditions) with practical health literacy, screening awareness, and prevention strategies that educators can act on immediately."),
          ("3.3", "Economic mobility: reframe financial health as a dimension of overall wellness, with concrete wealth-building strategies (homeownership pathways, investment fundamentals, retirement planning, side income development, and debt elimination), because a career of service should not require a lifetime of economic sacrifice."),
          ("3.4", "Wellness experience: deliver an on-site wellness experience (massage, mindfulness, decompression space) that gives educators an immediate, tangible encounter with what it feels like to prioritize their own wellbeing inside a professional setting.")]),
    ]
    overview = "".join(f'<article class="card card--bar{"-red" if i != 1 else ""}"><p class="kicker{" red" if i != 1 else ""}">{n}</p><h3>{t}</h3><p>{d}</p></article>' for i, (n, t, d, _, _) in enumerate(strands))
    detail = "".join(f'''<article class="strand" id="strand-{i + 1}"><div class="strand__head"><p class="eyebrow">{n}</p><h3>{t}</h3><p class="strand__purpose"><b>Purpose:</b> {p}</p></div><ol class="goals">{"".join(f"<li><span>{g}</span><p>{x}</p></li>" for g, x in goals)}</ol></article>''' for i, (n, t, _, p, goals) in enumerate(strands))
    overarching = [
        "Convene 500 attendees, including current Black male educators, aspiring educators (high school and college students), college and university professors, and education leaders, for professional development, brotherhood, and collective strategy, establishing the Summit as the premier national professional development experience for Black male educators and those who support them.",
        "Deliver programming shaped entirely by attendee feedback, survey data, and post-Summit research, ensuring that every session addresses a need the educators themselves identified, while maintaining or exceeding the Year 1 benchmarks of a 97 Net Promoter Score and 100% satisfaction rate at double the scale.",
        "Ensure that every attendee leaves with at least one AI tool or instructional strategy they can implement immediately, at least one strategy for protecting their health or building wealth, at least one framework for civic education in their school or community, and at least one meaningful professional relationship that extends beyond the weekend.",
    ]
    og = "".join(f"<li><span>{i + 1:02d}</span><p>{x}</p></li>" for i, x in enumerate(overarching))
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("p_lineup", eager=True, pos="center 35%")}</div><div class="wrap">
  <p class="crumbs"><a href="/summit" style="color:#fff">The Capital Summit</a> / Mission, Strands &amp; Goals</p>
  {eyebrow("Summit 2027 · Mission, strands and goals")}
  <h1>The ecosystem of a <span class="red">balanced man</span>.</h1>
  <p class="lede">A man's professional craft, civic voice, and total wellbeing are not separate topics. Together they make the ecosystem of a balanced man, and a balanced man is the most powerful force in education.</p>
</div></section>
{summit_tabs("mission")}

<section class="section"><div class="wrap split">
  <div>{eyebrow("Summit mission")}<h2 class="h2">Why the Summit exists.</h2></div>
  <p class="statement" style="font-size:clamp(1.25rem,2.1vw,1.7rem)">The Black Male Educator Capital Summit convenes Black male educators nationally to address the forces that determine whether these men stay in education, lead effectively, and live well. Organized around three strands (AI, Technology &amp; Instruction; Civic Education; and Health &amp; Wellness), the Summit treats a man's professional craft, civic voice, and total wellbeing not as separate topics but as the ecosystem of a balanced man.</p>
</div></section>

<section class="section band-stone" aria-labelledby="how-h"><div class="wrap split">
  <div>{eyebrow("How we got here")}<h2 id="how-h" class="h2">Chosen by the educators themselves.</h2></div>
  <div class="prose"><p>The three strands for the 2027 Summit were not selected by leadership alone. They were determined by the Summit Committee based on feedback from the inaugural Summit attendees, research and data collected from surveys and interviews conducted throughout the year, and the committee's analysis of the most urgent needs facing Black male educators nationally. Every strand reflects what the educators themselves told us matters most.</p><p>Economic mobility is intentionally embedded within Health &amp; Wellness rather than standing as a separate strand. Financial precarity is a health issue: a man who is economically insecure cannot be fully well, and the stress of financial instability compounds every other health risk Black men face.</p></div>
</div></section>

<section class="section" aria-labelledby="strands-h"><div class="wrap">
  <div class="section-head">{eyebrow("The three strands")}<h2 id="strands-h" class="h2">Three strands. One balanced man.</h2></div>
  <div class="grid-3">{overview}</div>
</div></section>

<section class="section band-dark" aria-labelledby="goals-h"><div class="wrap">
  <div class="section-head">{eyebrow("Summit goals · across all strands")}<h2 id="goals-h" class="h2">What every attendee leaves with.</h2></div>
  <ol class="goals goals--dark">{og}</ol>
</div></section>

<section class="section" aria-labelledby="sg-h"><div class="wrap">
  <div class="section-head">{eyebrow("Goals by strand")}<h2 id="sg-h" class="h2">How each strand serves the whole man.</h2></div>
  <div class="strands">{detail}</div>
</div></section>

{closing("Have a session that serves the whole man?", "The call for proposals is open through " + CFP_DEADLINE + ".", btn("Submit a proposal", "/summit/proposals", "light") + btn("Back to the Summit", "/summit", "ghost", False))}'''
    page("/summit/mission", "Summit Mission, Strands and Goals", "The mission, three strands and goals of the 2027 Black Male Educator Capital Summit: AI, Technology & Instruction; Civic Education; and Health & Wellness.", body, "programs")


def radios(legend, name, options, required=True):
    boxes = "".join(f'<label class="check"><input type="radio" name="{name}" value="{e(o)}"> {e(o)}</label>' for o in options)
    return f'<fieldset class="field field--full"{" data-required-group" if required else ""}><legend>{e(legend)}</legend><div class="checks">{boxes}</div><span class="err">Choose one.</span></fieldset>'


def build_summit_proposals():
    facts = [("Submission deadline", CFP_DEADLINE), ("Anticipated attendance", "500 educators, school leaders, and allies"), ("Summit experience", "Three-day national convening (Thursday–Saturday)"),
             ("Presentation length", "60 minutes, presented twice for two participant groups"), ("Location", "Howard University School of Education &amp; Howard University Middle School")]
    fc = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in facts)
    sc = "".join(f'<article class="card card--bar{"-red" if i != 1 else ""}"><p class="kicker{" red" if i != 1 else ""}">Strand {i + 1}</p><h3>{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(CFP_STRANDS))
    audiences = ["Classroom Teachers / Lead Teachers", "Instructional Assistants / Paraprofessionals", "School Leaders (Principals, Assistant Principals, Deans)", "District / Headquarters Staff", "Aspiring Educators", "Allies & Advocates"]
    grades = ["Pre-K–Elementary (PK–5)", "Middle School (6–8)", "High School (9–12)", "Postsecondary / Higher Education", "All Grade Levels / General Audience"]
    av = ["Projector", "HDMI / Display Adaptor", "Laptop (presenter does not have one)", "Microphone / Speaker System", "Whiteboard / Easel Pad", "Markers / Pens / Pencils", "Chart Paper / Poster Paper", "Printed Handouts (please attach file)", "Internet / Wi-Fi Access", "Other"]
    group = lambda legend, name, opts, req=False: f'<fieldset class="field field--full"{" data-required-group" if req else ""}><legend>{e(legend)}</legend><div class="checks">{"".join(f"<label class=check><input type=checkbox name={chr(34)}{name}{chr(34)} value={chr(34)}{e(o)}{chr(34)}> {e(o)}</label>" for o in opts)}</div><span class="err">Choose at least one.</span></fieldset>'
    body = f'''
<section class="phero phero--dark phero--photo wedge"><div class="phero__bg">{img("p_panel", eager=True, pos="center 35%")}</div><div class="wrap">
  <p class="crumbs"><a href="/summit" style="color:#fff">The Capital Summit</a> / Call for Proposals</p>
  {eyebrow("Request for proposals · " + SUMMIT_DATES + " · Howard University")}
  <h1>Present at the <span class="red">2027 Summit</span>.</h1>
  <p class="lede">Black Brilliance. Black Scholarship. Black Possibility. Proposals are due {CFP_DEADLINE}.</p>
  <div class="btn-row">{btn("Start your proposal", "#proposal-form", "red")}{btn("Read the strands", "#cfp-strands", "ghost", False)}</div>
</div></section>
{summit_tabs("proposals")}

<section class="section"><div class="wrap split">
  <div>{eyebrow("Call for proposals")}<h2 class="h2">Engaging. Interactive. Action-oriented.</h2></div>
  <div class="prose"><p>Thank you for your interest in presenting at the 2027 Black Male Educator Capital Summit. We invite engaging, interactive, and action-oriented presentations that elevate Black male educators and align with this year's theme: Black Brilliance, Black Scholarship, Black Possibility.</p><p>All proposals must address one of the three 2027 Summit strands and include a clear plan for how participants will apply the learning in their roles.</p>
  <dl class="facts-list">{fc}</dl></div>
</div></section>

<section class="section band-stone" id="cfp-strands" aria-labelledby="cfps-h"><div class="wrap">
  <div class="section-head">{eyebrow("2027 Summit strands")}<h2 id="cfps-h" class="h2">Every session aligns with one strand.</h2><p class="lede">These strands reflect the issues and opportunities most central to the lives and leadership of Black male educators today. <a href="/summit/mission">See the full mission, strands and goals</a>.</p></div>
  <div class="grid-3">{sc}</div>
</div></section>

<section class="section" id="proposal-form"><div class="wrap" style="max-width:920px">
  <div class="form-panel form-wrap"><form class="form" data-form="Call for Proposals"><div class="form-grid">
    <h2 class="field--full form-section">Section 1 · Presenter contact information</h2>
    {field("Full name", "name", required=True, auto="name")}
    {field("Professional/academic title", "prof_title", required=True, placeholder="Dr., Mr., Professor…")}
    {field("Organization name", "org", required=True, auto="organization")}
    {field("Title/role", "role", required=True, auto="organization-title")}
    {field("Email address", "email", "email", required=True, auto="email")}
    {field("Phone number", "phone", "tel", required=True, auto="tel")}
    {field("Brief bio (150 words)", "bio", "textarea", required=True, full=True, hint="Highlight your experience, leadership roles, and work serving Black male educators and students.", attrs=' data-max-words="150"')}
    {field("How does your experience connect to Black male educators and/or the Summit theme of Black Brilliance, Black Scholarship, Black Possibility?", "connection", "textarea", required=True, full=True)}

    <h2 class="field--full form-section">Section 2 · Session alignment and strand</h2>
    {radios("Which 2027 Summit strand does your session address? (select one)", "strand", [t for t, _ in CFP_STRANDS])}
    {field("Session title", "session_title", required=True, full=True)}
    {field("Session description (200–300 words)", "description", "textarea", required=True, full=True, hint="Address: What will participants learn? How does your session connect to your selected strand? How will the presentation accelerate teacher and leader practice upon returning to work? How does your session embody Black Brilliance, Black Scholarship, and Black Possibility for Black male educators and their allies?", attrs=' data-max-words="300" data-min-words="200"')}

    <h2 class="field--full form-section">Section 3 · Session design and facilitation</h2>
    {field("Session agenda (60 minutes)", "agenda", "textarea", required=True, full=True, hint="Outline the flow of your session (time-stamped or bulleted), highlighting where participants will interact, discuss, or practice.")}
    {field("What are the primary objectives/learning outcomes for this session?", "objectives", "textarea", required=True, full=True, placeholder="By the end of the session, participants will be able to…")}
    {field("How will you ensure this presentation is interactive (not a lecture)?", "interactive", "textarea", required=True, full=True, hint="Describe specific activities (e.g., protocols, small-group work, case studies, role-plays, reflection prompts).")}

    <h2 class="field--full form-section">Section 4 · Audience and logistics</h2>
    {group("Intended audience (check all that apply)", "audience", audiences, True)}
    {group("What grade band does your session primarily address? (select all that apply)", "grades", grades, True)}
    {radios("Will you be able to present this session twice during the convening (for two different groups of participants)?", "present_twice", ["Yes", "No"])}
    {group("Please indicate any AV or presentation needs (check all that apply)", "av", av)}
    {field("Other AV needs (please specify)", "av_other", full=True)}
    <div class="field field--full"><label for="f-handouts">Printed handouts file <span class="hint">(optional, PDF or Word, up to 4 MB)</span></label><input id="f-handouts" name="handouts" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" data-max-mb="4"></div>
    {radios("Are you open to having your session recorded and/or materials shared with attendees after the Summit?", "recording", ["Yes", "No"])}
  </div><p class="form-note">Deadline: {CFP_DEADLINE}. Questions: bmecsummit@nabme.org</p><div><button class="btn btn--red" type="submit">Submit my proposal {ARROW}</button></div></form>
  {success("Proposal received.", "Thank you for submitting a proposal for the 2027 Black Male Educator Capital Summit. The Summit Committee will review every proposal after the December 14 deadline and follow up by email.", btn("Back to the Summit", "/summit", "outline"))}</div>
</div></section>'''
    page("/summit/proposals", "Call for Proposals", "Submit a proposal to present at the 2027 Black Male Educator Capital Summit, February 11–13 at Howard University. Due " + CFP_DEADLINE + ".", body, "programs")


def build_nominate():
    body = f'''
<section class="phero"><div class="wrap">{eyebrow("Nominate a Black male educator")}<h1>Who changed your <span class="red">direction</span>?</h1><p class="lede">Tell us about a Black male educator who matters. Selected nominations are featured on NABME Voices, social media and NABME Live, with permission.</p></div></section>
<section class="section"><div class="wrap" style="max-width:900px"><div class="form-panel form-wrap"><form class="form" data-form="Nominations"><div class="form-grid">
  {field("Nominee's name", "nominee", required=True)}
  {field("School", "school", required=True)}
  {field("City, State", "city", required=True)}
  {field("Why he matters", "why", "textarea", required=True, full=True)}
  {field("Your name", "name", required=True, auto="name")}
  {field("Your email", "email", "email", required=True, auto="email")}
</div><div><button class="btn btn--red" type="submit">Send nomination</button></div></form>
{success("Nomination received.", "Thank you for lifting him up. We may reach out to you both before featuring the story.", btn("Share NABME", "/live", "outline"))}</div></div></section>'''
    page("/nominate", "Nominate a Black Male Educator", "Nominate a Black male educator who shaped you. NABME features selected nominations.", body)


def write_support_files():
    seal = open(os.path.join(OUT, "assets/seal.svg"), encoding="utf-8").read()
    seal = seal.replace("#bd2538", "#c51f36").replace("Urbanist, Arial", "Inter, Arial")
    open(os.path.join(OUT, "assets/seal.svg"), "w", encoding="utf-8").write(seal)
    open(os.path.join(OUT, "assets/seal-white.svg"), "w", encoding="utf-8").write(seal.replace('color="#1b1c1b"', 'color="#ffffff"').replace("#c51f36", "#f36070"))
    redirects = [
        ("/sponsors", "/partners"), ("/join-nabme-2", "/join"), ("/mission-and-values", "/mission"), ("/board-members", "/founders"),
        ("/nabme-fellowship-program", "/athari"), ("/resumes", "/resume-bank"), ("/give", "/donate"), ("/contact-us", "/contact"),
        ("/nabme-careersw", "/careers"), ("/talent-portal", "/talent"),
    ]
    vercel = {
        "cleanUrls": True,
        "trailingSlash": False,
        # /register is the printed QR code's target: a temporary redirect, so it can point at the live registration page later
        "redirects": [{"source": s, "destination": d, "permanent": True} for s, d in redirects]
                     + [{"source": "/register", "destination": "/summit/register", "permanent": False}],
        "headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}],
    }
    open(os.path.join(OUT, "vercel.json"), "w").write(json.dumps(vercel, indent=2))
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")


if __name__ == "__main__":
    if VKEY != "a":  # versions share version A's static files (styles, script, media)
        import shutil
        base = os.path.join(HERE, "site")
        os.makedirs(OUT, exist_ok=True)
        shutil.copytree(os.path.join(base, "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
        for f in ("styles.css", "main.js"):
            shutil.copy2(os.path.join(base, f), os.path.join(OUT, f))
    build_home(); build_mission(); build_founders(); build_bios(); build_join(); build_contact()
    build_careers(); build_talent(); build_resume_bank(); build_employers(); build_jobs(); build_post_job()
    build_donate(); build_media(); build_blog(); build_events(); build_live(); build_partners()
    build_athari(); build_summit(); build_nominate(); build_impact(); build_summit_register(); build_summit_mission(); build_summit_proposals()
    write_support_files()
    print("built", len([f for f in os.listdir(OUT) if f.endswith(".html")]), "pages into", OUT)
