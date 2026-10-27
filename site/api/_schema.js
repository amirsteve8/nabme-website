// Where each website form saves in Airtable: one table per form.
// field: [form input name, Airtable column, column type]. Shared by api/submit.js and scripts/setup-airtable.mjs.
// Types: text, long, email, phone, url, select, file. Every table also gets "Page" and "Submitted at".

export const TABLES = {
  "Members": {
    fields: [
      ["name", "Name", "text"], ["email", "Email", "email"], ["role", "Role", "text"], ["role_other", "Role (other)", "text"],
      ["org", "School or organization", "text"], ["city", "City, State", "text"], ["years", "Years in education", "text"],
      ["interests", "Interests", "long"],
    ],
  },
  "Resume Bank": {
    status: ["New", "Approved", "Hidden"],
    fields: [
      ["name", "Name", "text"], ["email", "Email", "email"], ["phone", "Phone", "phone"], ["city", "City, State", "text"],
      ["relocate", "Willing to relocate", "text"], ["current_role", "Current role", "text"], ["current_role_other", "Current role (other)", "text"],
      ["years", "Years in education", "text"], ["grades", "Grade bands", "text"], ["subjects", "Subjects", "text"],
      ["certs", "Certifications", "long"], ["targets", "Target roles", "long"], ["schedule", "Schedule", "text"],
      ["start", "Available to start", "text"], ["remote", "Open to remote", "text"], ["video", "Video intro link", "url"],
      ["linkedin", "LinkedIn", "url"], ["skills", "Skills", "long"], ["visibility", "Profile visibility", "text"],
      ["consent", "Consent to contact", "text"], ["photo", "Headshot", "file"], ["resume", "Resume", "file"],
    ],
  },
  "Employers": {
    status: ["New", "Verified", "Declined"],
    fields: [
      ["org", "Organization", "text"], ["name", "Contact name", "text"], ["email", "Work email", "email"],
      ["orgtype", "Organization type", "text"], ["schools", "Number of schools", "text"], ["hiring", "Roles hiring for", "long"],
    ],
  },
  "Job Posts": {
    status: ["Pending review", "Approved", "Expired"],
    fields: [
      ["title", "Job title", "text"], ["org", "Organization", "text"], ["location", "Location", "text"], ["remote", "Remote option", "text"],
      ["type", "Job type", "text"], ["category", "Role category", "text"], ["grades", "Grade band", "text"], ["salary", "Salary range", "text"],
      ["desc", "Description", "long"], ["apply", "How to apply", "text"], ["deadline", "Application deadline", "text"], ["logo", "Logo", "file"],
    ],
  },
  "Summit Registrations": {
    status: ["Pending payment", "Paid", "Waitlist", "Cancelled"],
    fields: [
      ["name", "Name", "text"], ["email", "Email", "email"], ["phone", "Phone", "phone"],
      ["org", "School or organization", "text"], ["role", "Role", "text"], ["role_other", "Role (other)", "text"],
      ["city", "City, State", "text"], ["years", "Years in education", "text"],
      ["days", "Days attending", "long"], ["attended_2026", "Attended the 2026 Summit", "text"],
      ["shirt", "T-shirt size", "text"], ["dietary", "Dietary needs", "text"], ["access", "Accessibility needs", "text"],
      ["heard", "How they heard", "text"], ["photo_consent", "Photo consent", "text"],
    ],
  },
  "Athari Interest": {
    fields: [["name", "Name", "text"], ["email", "Email", "email"], ["school", "School", "text"], ["role", "Role", "text"], ["years", "Years in education", "text"]],
  },
  "Nominations": {
    fields: [
      ["nominee", "Nominee", "text"], ["school", "School", "text"], ["city", "City", "text"], ["why", "Why they matter", "long"],
      ["name", "Nominated by", "text"], ["email", "Nominator email", "email"],
    ],
  },
  "Contact Messages": {
    fields: [["name", "Name", "text"], ["email", "Email", "email"], ["org", "Organization", "text"], ["topic", "Topic", "text"], ["message", "Message", "long"]],
  },
  "Donations": {
    fields: [["freq", "Frequency", "text"], ["amount", "Amount", "text"], ["other", "Other amount", "text"], ["designation", "Designation", "text"], ["honor", "In honor of", "text"]],
  },
  "Newsletter": {
    fields: [["email", "Email", "email"], ["role", "I am a", "text"], ["source", "Signed up from", "text"]],
  },
  "Summit Interest": {
    fields: [["email", "Email", "email"], ["source", "Signed up from", "text"]],
  },
};

export const MAX_FILE_BYTES = 4 * 1024 * 1024; // keeps a whole submission under Vercel's 4.5 MB request limit

// Airtable column definitions for a table: used by the setup script and to create a missing table on first use
const TYPES = {
  text: { type: "singleLineText" }, long: { type: "multilineText" }, email: { type: "email" },
  phone: { type: "phoneNumber" }, url: { type: "url" }, file: { type: "multipleAttachments" },
};
export function columns(def) {
  const cols = def.fields.map(([, name, type]) => ({ name, ...TYPES[type] }));
  if (def.status) cols.push({ name: "Status", type: "singleSelect", options: { choices: def.status.map((name) => ({ name })) } });
  cols.push({ name: "Page", type: "url" });
  cols.push({ name: "Submitted at", type: "dateTime", options: { dateFormat: { name: "us" }, timeFormat: { name: "12hour" }, timeZone: "America/New_York" } });
  return cols;
}
