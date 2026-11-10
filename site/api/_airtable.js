// Saves one row to Airtable. Creates a missing table or missing columns once, then saves again.
import { columns } from "./_schema.js";

export async function saveRecord(tableName, table, fields) {
  const token = process.env.AIRTABLE_TOKEN, base = process.env.AIRTABLE_BASE_ID;
  const api = `https://api.airtable.com/v0/${base}/${encodeURIComponent(tableName)}`;
  const headers = { Authorization: `Bearer ${token}`, "content-type": "application/json" };
  const save = () => fetch(api, { method: "POST", headers, body: JSON.stringify({ records: [{ fields }], typecast: true }) });
  let res = await save();
  if (res.status === 404 || res.status === 403) {
    // A form added after setup: create its table once, then save again
    const made = await fetch(`https://api.airtable.com/v0/meta/bases/${base}/tables`, { method: "POST", headers, body: JSON.stringify({ name: tableName, fields: columns(table) }) });
    if (made.ok) res = await save();
    else console.error("Could not create table", tableName, made.status, await made.text());
  } else if (res.status === 422) {
    // A question added to an existing form: create the missing columns once, then save again
    const meta = `https://api.airtable.com/v0/meta/bases/${base}/tables`;
    const tables = await fetch(meta, { headers }).then((r) => r.json()).catch(() => ({}));
    const found = tables.tables?.find((t) => t.name === tableName);
    if (found) {
      const have = new Set(found.fields.map((f) => f.name));
      for (const col of columns(table).filter((c) => !have.has(c.name))) {
        const r = await fetch(`${meta}/${found.id}/fields`, { method: "POST", headers, body: JSON.stringify(col) });
        if (!r.ok) console.error("Could not add column", tableName, col.name, r.status, await r.text());
      }
      res = await save();
    }
  }
  if (!res.ok) { console.error("Airtable save failed", res.status, await res.text()); return { ok: false }; }
  return { ok: true, id: (await res.json()).records?.[0]?.id };
}

// True when a row already has this value. A column that doesn't exist yet counts as no match.
export async function hasRecord(tableName, column, value) {
  const token = process.env.AIRTABLE_TOKEN, base = process.env.AIRTABLE_BASE_ID;
  const q = new URLSearchParams({ filterByFormula: `{${column}}='${value}'`, maxRecords: "1" });
  const res = await fetch(`https://api.airtable.com/v0/${base}/${encodeURIComponent(tableName)}?${q}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) return false;
  return ((await res.json()).records || []).length > 0;
}
