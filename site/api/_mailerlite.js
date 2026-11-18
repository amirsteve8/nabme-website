// Adds people who sign up on the website to NABME's MailerLite audience, in a group per form.
// Needs MAILERLITE_API_KEY in Vercel. Without it, or if MailerLite is down, forms still save to Airtable as usual.
const API = "https://connect.mailerlite.com/api";

// Only forms where people asked to hear from NABME. Contact, employer, job and nomination forms are left out.
export const GROUPS = {
  "Newsletter": "Newsletter",
  "Summit Interest": "Summit updates",
  "Members": "NABME members",
  "Summit Registrations": "Summit 2027 registrants",
  "Call for Proposals": "Summit 2027 proposal submitters",
  "Athari Interest": "Athari Fellowship interest",
};

const ids = new Map();   // group name -> id, kept while the function stays warm
const call = (path, opts = {}) => fetch(API + path, { ...opts, signal: AbortSignal.timeout(5000), headers: { Authorization: `Bearer ${process.env.MAILERLITE_API_KEY}`, "content-type": "application/json", accept: "application/json" } });

async function groupId(name) {
  if (ids.has(name)) return ids.get(name);
  const found = await call(`/groups?filter[name]=${encodeURIComponent(name)}&limit=100`).then((r) => r.json());
  let g = (found.data || []).find((x) => x.name === name);
  if (!g) g = (await call("/groups", { method: "POST", body: JSON.stringify({ name }) }).then((r) => r.json())).data;
  if (!g?.id) throw new Error(`MailerLite group unavailable: ${name}`);
  ids.set(name, g.id);
  return g.id;
}

export async function subscribe(tableName, form) {
  const group = GROUPS[tableName];
  const email = (form.get("email") || "").toString().trim().toLowerCase();
  if (!process.env.MAILERLITE_API_KEY || !group || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return false;
  try {
    const [first, ...rest] = (form.get("name") || "").toString().trim().split(/\s+/);
    const fields = {};
    if (first) fields.name = first;
    if (rest.length) fields.last_name = rest.join(" ");
    const org = (form.get("org") || form.get("school") || "").toString().trim();
    if (org) fields.company = org;
    const city = (form.get("city") || "").toString().trim();
    if (city) fields.city = city;
    const res = await call("/subscribers", { method: "POST", body: JSON.stringify({ email, fields, groups: [await groupId(group)] }) });
    if (!res.ok) { console.error("MailerLite add failed", tableName, res.status, await res.text()); return false; }
    return true;
  } catch (err) { console.error("MailerLite add failed", tableName, err); return false; }
}
