// Summit registration checkout. A row reaches Airtable only after PayPal confirms the $100 was captured.
// Needs PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in Vercel (PAYPAL_ENV=sandbox for test mode), plus the Airtable variables.
//   GET  -> { ready, clientId } for the PayPal buttons
//   POST _action=create  -> checks the form, opens a $100 PayPal order
//   POST _action=capture -> takes the payment, confirms it, then saves the registration
import { TABLES } from "./_schema.js";
import { saveRecord, hasRecord } from "./_airtable.js";

const TABLE = "Summit Registrations";
const AMOUNT = "100.00", CURRENCY = "USD", MARKER = "nabme-summit-2027";
const REQUIRED = ["name", "email", "city", "org", "level", "role", "years", "attended_2026", "days", "shirt"];
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
const base = () => process.env.PAYPAL_ENV === "sandbox" ? "https://api-m.sandbox.paypal.com" : "https://api-m.paypal.com";
const ready = () => !!(process.env.PAYPAL_CLIENT_ID && process.env.PAYPAL_CLIENT_SECRET && process.env.AIRTABLE_TOKEN && process.env.AIRTABLE_BASE_ID);
const help = "email bmecsummit@nabme.org";

async function accessToken() {
  const auth = Buffer.from(`${process.env.PAYPAL_CLIENT_ID}:${process.env.PAYPAL_CLIENT_SECRET}`).toString("base64");
  const res = await fetch(`${base()}/v1/oauth2/token`, { method: "POST", headers: { Authorization: `Basic ${auth}`, "content-type": "application/x-www-form-urlencoded" }, body: "grant_type=client_credentials" });
  if (!res.ok) throw new Error(`PayPal login failed: ${res.status}`);
  return (await res.json()).access_token;
}

function missingField(form) {
  for (const key of REQUIRED) if (!form.getAll(key).some((v) => v.toString().trim())) return key;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((form.get("email") || "").toString().trim()) ? null : "email";
}

function rowFrom(form, cap, order) {
  const fields = { "Page": (form.get("_page") || "").toString().slice(0, 200), "Submitted at": new Date().toISOString(), "Status": "Paid",
    "PayPal order ID": order.id, "PayPal capture ID": cap.id, "Amount paid": `$${cap.amount.value} ${cap.amount.currency_code}`, "PayPal payer email": order.payer?.email_address || "" };
  for (const [key, column] of TABLES[TABLE].fields) {
    const values = form.getAll(key).map((v) => v.toString().trim()).filter(Boolean);
    if (values.length) fields[column] = values.join(", ").slice(0, 10000);
  }
  return fields;
}

async function createOrder(form) {
  const token = await accessToken();
  const res = await fetch(`${base()}/v2/checkout/orders`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "content-type": "application/json" }, body: JSON.stringify({
    intent: "CAPTURE",
    purchase_units: [{ custom_id: MARKER, description: "Black Male Educator Capital Summit 2027 registration", amount: { currency_code: CURRENCY, value: AMOUNT } }],
    application_context: { brand_name: "NABME", shipping_preference: "NO_SHIPPING", user_action: "PAY_NOW" },
  }) });
  if (!res.ok) { console.error("PayPal create order failed", res.status, await res.text()); return json({ ok: false, error: "We couldn't start the payment." }, 502); }
  return json({ ok: true, id: (await res.json()).id });
}

async function capture(orderId, token) {
  const call = () => fetch(`${base()}/v2/checkout/orders/${orderId}/capture`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "content-type": "application/json", "Prefer": "return=representation", "PayPal-Request-Id": `capture-${orderId}` } });
  try { const res = await call(); if (res.status < 500) return res; } catch (err) { console.error("PayPal capture network error", err); }
  return call();   // same request id, so PayPal can't charge twice
}

async function refund(cap, token) {
  const res = await fetch(`${base()}/v2/payments/captures/${cap.id}/refund`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "content-type": "application/json", "PayPal-Request-Id": `refund-${cap.id}` }, body: "{}" });
  if (!res.ok) console.error("PayPal refund failed", cap.id, res.status, await res.text());
  return res.ok;
}

async function captureAndSave(form) {
  const orderId = (form.get("orderID") || "").toString();
  if (!/^[A-Z0-9]{10,30}$/.test(orderId)) return json({ ok: false, error: "That payment couldn't be found." }, 400);
  const token = await accessToken();
  const res = await capture(orderId, token);
  const order = await res.json().catch(() => ({}));
  if (!res.ok) {
    const issue = order.details?.[0]?.issue;
    console.error("PayPal capture failed", orderId, res.status, issue);
    if (issue === "INSTRUMENT_DECLINED") return json({ ok: false, retry: true, error: "That card was declined. Please try another payment method." }, 402);
    return json({ ok: false, error: "The payment didn't go through, and you were not charged." }, 402);
  }
  const unit = order.purchase_units?.[0], cap = unit?.payments?.captures?.[0];
  if (order.status !== "COMPLETED" || cap?.status !== "COMPLETED") {
    console.error("PayPal payment not complete", orderId, order.status, cap?.status);
    return json({ ok: false, error: `PayPal hasn't finished this payment, so your registration isn't complete yet. Please ${help} with reference ${orderId}.` }, 402);
  }
  if (cap.amount?.value !== AMOUNT || cap.amount?.currency_code !== CURRENCY || (cap.custom_id || unit.custom_id) !== MARKER) {
    console.error("PayPal payment does not match the Summit fee", orderId, cap.amount, cap.custom_id);
    return json({ ok: false, error: `That payment doesn't match the registration fee. Please ${help} with reference ${orderId}.` }, 402);
  }
  if (await hasRecord(TABLE, "PayPal order ID", orderId)) return json({ ok: true });   // a repeat of a payment that's already saved

  const fields = rowFrom(form, cap, order);
  for (let i = 0; i < 3; i++) {
    if ((await saveRecord(TABLE, TABLES[TABLE], fields).catch(() => ({ ok: false }))).ok) return json({ ok: true });
    await new Promise((r) => setTimeout(r, 400 * (i + 1)));
  }
  // Paid but couldn't be recorded: give the money back rather than keep a payment with no registration
  console.error("Paid registration could not be saved", orderId, cap.id);
  const back = await refund(cap, token);
  return json({ ok: false, error: back ? "We couldn't save your registration, so your payment was refunded. Please try again." : `We received your payment but couldn't save your registration. Please ${help} with reference ${cap.id}.` }, 502);
}

export function GET() {
  return json({ ready: ready(), clientId: process.env.PAYPAL_CLIENT_ID || null });
}

export async function POST(request) {
  if (!ready()) return json({ ok: false, error: "Online payment isn't available right now." }, 503);
  let form;
  try { form = await request.formData(); } catch { return json({ ok: false, error: "Could not read the form." }, 400); }
  if ((form.get("company_website") || "").toString().trim()) return json({ ok: false, error: "Could not read the form." }, 400);   // spam trap
  const missing = missingField(form);
  if (missing) return json({ ok: false, error: "Please complete every required field." }, 400);
  try {
    const action = form.get("_action");
    if (action === "create") return await createOrder(form);
    if (action === "capture") return await captureAndSave(form);
    return json({ ok: false, error: "Unknown request." }, 400);
  } catch (err) {
    console.error("Summit checkout error", err);
    return json({ ok: false, error: `Something went wrong with the payment. If you were charged, please ${help}.` }, 502);
  }
}
