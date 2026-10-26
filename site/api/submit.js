// Receives every website form and saves it to NABME's Airtable base.
// Needs two environment variables in Vercel: AIRTABLE_TOKEN and AIRTABLE_BASE_ID.
// Optional email alerts: RESEND_API_KEY, NOTIFY_FROM (a verified sender) and NOTIFY_TO (defaults to info@nabme.org).
import { TABLES, MAX_FILE_BYTES } from "./_schema.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export async function POST(request) {
  const token = process.env.AIRTABLE_TOKEN, base = process.env.AIRTABLE_BASE_ID;
  if (!token || !base) return json({ ok: false, configured: false }, 503);

  let form;
  try { form = await request.formData(); } catch { return json({ ok: false, error: "Could not read the form." }, 400); }
  if ((form.get("company_website") || "").toString().trim()) return json({ ok: true }); // spam trap filled in: pretend success

  const tableName = (form.get("_table") || "").toString();
  const table = TABLES[tableName];
  if (!table) return json({ ok: false, error: "Unknown form." }, 400);

  const fields = { "Page": (form.get("_page") || "").toString().slice(0, 200), "Submitted at": new Date().toISOString() };
  if (table.status) fields["Status"] = table.status[0];
  const files = [];
  for (const [key, column, type] of table.fields) {
    if (type === "file") {
      const f = form.get(key);
      if (f && typeof f === "object" && f.size > 0) {
        if (f.size > MAX_FILE_BYTES) return json({ ok: false, error: `${column} is larger than 4 MB. Please upload a smaller file.` }, 413);
        files.push([column, f]);
      }
      continue;
    }
    const values = form.getAll(key).map((v) => v.toString().trim()).filter(Boolean);
    if (values.length) fields[column] = values.join(", ").slice(0, 10000);
  }

  const api = `https://api.airtable.com/v0/${base}/${encodeURIComponent(tableName)}`;
  const res = await fetch(api, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "content-type": "application/json" },
    body: JSON.stringify({ records: [{ fields }], typecast: true }),
  });
  if (!res.ok) {
    console.error("Airtable save failed", res.status, await res.text());
    return json({ ok: false, error: "We couldn't save this right now." }, 502);
  }
  const recordId = (await res.json()).records?.[0]?.id;

  // Files (resume, headshot, logo) go straight into the record's attachment column
  for (const [column, f] of files) {
    const buf = Buffer.from(await f.arrayBuffer());
    const up = await fetch(`https://content.airtable.com/v0/${base}/${recordId}/${encodeURIComponent(column)}/uploadAttachment`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "content-type": "application/json" },
      body: JSON.stringify({ contentType: f.type || "application/octet-stream", filename: f.name || column, file: buf.toString("base64") }),
    });
    if (!up.ok) console.error("Attachment upload failed", column, up.status, await up.text());
  }

  // Optional: email the team about the new entry
  const resendKey = process.env.RESEND_API_KEY, from = process.env.NOTIFY_FROM;
  if (resendKey && from && !["Newsletter", "Summit Interest"].includes(tableName)) {
    const lines = Object.entries(fields).map(([k, v]) => `${k}: ${v}`).join("\n");
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${resendKey}`, "content-type": "application/json" },
      body: JSON.stringify({ from, to: process.env.NOTIFY_TO || "info@nabme.org", subject: `New website entry: ${tableName}`, text: lines + (files.length ? `\n\nFiles: ${files.map(([c]) => c).join(", ")} (in Airtable)` : "") }),
    }).catch((err) => console.error("Alert email failed", err));
  }

  return json({ ok: true });
}
