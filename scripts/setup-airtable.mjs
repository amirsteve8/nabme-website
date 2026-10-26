// One-time setup: creates every NABME form table and column in an Airtable base.
// Safe to run again; it only adds what's missing.
// Run from the nabme-v3 folder:
//   AIRTABLE_TOKEN=your_token AIRTABLE_BASE_ID=appXXXXXXXX node scripts/setup-airtable.mjs
// The token needs these scopes: schema.bases:read, schema.bases:write, data.records:write.
import { TABLES } from "../site/api/_schema.js";

const token = process.env.AIRTABLE_TOKEN, base = process.env.AIRTABLE_BASE_ID;
if (!token || !base) { console.error("Set AIRTABLE_TOKEN and AIRTABLE_BASE_ID first."); process.exit(1); }
const meta = `https://api.airtable.com/v0/meta/bases/${base}/tables`;
const headers = { Authorization: `Bearer ${token}`, "content-type": "application/json" };

const TYPES = {
  text: { type: "singleLineText" }, long: { type: "multilineText" }, email: { type: "email" },
  phone: { type: "phoneNumber" }, url: { type: "url" }, file: { type: "multipleAttachments" },
};
function columns(def) {
  const cols = def.fields.map(([, name, type]) => ({ name, ...TYPES[type] }));
  if (def.status) cols.push({ name: "Status", type: "singleSelect", options: { choices: def.status.map((name) => ({ name })) } });
  cols.push({ name: "Page", type: "url" });
  cols.push({ name: "Submitted at", type: "dateTime", options: { dateFormat: { name: "us" }, timeFormat: { name: "12hour" }, timeZone: "America/New_York" } });
  return cols;
}

const existing = await fetch(meta, { headers }).then((r) => r.json());
if (existing.error) { console.error("Airtable said:", existing.error); process.exit(1); }

for (const [name, def] of Object.entries(TABLES)) {
  const want = columns(def);
  const found = existing.tables.find((t) => t.name === name);
  if (!found) {
    const r = await fetch(meta, { method: "POST", headers, body: JSON.stringify({ name, fields: want }) });
    console.log(r.ok ? `Created table: ${name}` : `Could not create ${name}: ${await r.text()}`);
    continue;
  }
  const have = new Set(found.fields.map((f) => f.name));
  for (const col of want.filter((c) => !have.has(c.name))) {
    const r = await fetch(`${meta}/${found.id}/fields`, { method: "POST", headers, body: JSON.stringify(col) });
    console.log(r.ok ? `Added ${name} > ${col.name}` : `Could not add ${name} > ${col.name}: ${await r.text()}`);
  }
  console.log(`Checked table: ${name}`);
}
console.log("Done. Open the base in Airtable to see every table.");
