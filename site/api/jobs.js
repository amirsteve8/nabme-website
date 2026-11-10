// Public job board feed: listings set to Approved in Airtable's Job Posts table, within 60 days of being submitted and not past their deadline.
// New submissions wait as Pending review. Rows whose title or organization starts with TEST never show.
const TABLE = "Job Posts", DAYS_LIVE = 60;
const json = (body, status = 200, cache = "public, s-maxage=60, stale-while-revalidate=300") => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": cache } });

function listing(r) {
  const f = r.fields;
  const logo = f["Logo"]?.[0]?.thumbnails?.large?.url || f["Logo"]?.[0]?.url || null;
  return { id: r.id, title: f["Job title"], org: f["Organization"], location: f["Location"] || "", remote: f["Remote option"] || "", type: f["Job type"] || "", category: f["Role category"] || "",
    grades: f["Grade band"] || "", salary: f["Salary range"] || "", desc: f["Description"] || "", apply: f["How to apply"] || "", deadline: f["Application deadline"] || "", posted: f["Submitted at"] || r.createdTime, logo };
}

export async function GET() {
  const token = process.env.AIRTABLE_TOKEN, base = process.env.AIRTABLE_BASE_ID;
  if (!token || !base) return json({ ok: false, jobs: [] }, 503, "no-store");
  const rows = [];
  try {
    let offset;
    do {
      const q = new URLSearchParams({ filterByFormula: "{Status}='Approved'", pageSize: "100" });
      if (offset) q.set("offset", offset);
      const res = await fetch(`https://api.airtable.com/v0/${base}/${encodeURIComponent(TABLE)}?${q}`, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) { console.error("Job board read failed", res.status, await res.text()); return json({ ok: false, jobs: [] }, 502, "no-store"); }
      const page = await res.json();
      rows.push(...(page.records || []));
      offset = page.offset;
    } while (offset && rows.length < 1000);
  } catch (err) { console.error("Job board read failed", err); return json({ ok: false, jobs: [] }, 502, "no-store"); }

  const today = new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });
  const cutoff = Date.now() - DAYS_LIVE * 86400000;
  const jobs = rows.map(listing)
    .filter((j) => j.title && j.org && !/^TEST\b/.test(j.title) && !/^TEST\b/.test(j.org) && Date.parse(j.posted) >= cutoff && (!j.deadline || j.deadline >= today))
    .sort((a, b) => Date.parse(b.posted) - Date.parse(a.posted));
  return json({ ok: true, jobs });
}
