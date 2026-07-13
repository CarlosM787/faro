// CI guard: every locale must expose the identical key set (risk #4: i18n drift).
// English is the reference; all other language folders under src/locales must
// match it exactly, so the language picker never surfaces a missing string.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../src/locales", import.meta.url));

const flatten = (obj, prefix = "") =>
  Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" && v !== null ? flatten(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  );

const REFERENCE = "en";
const langs = readdirSync(root).filter((d) => statSync(join(root, d)).isDirectory());
if (!langs.includes(REFERENCE)) {
  console.error(`✗ reference locale "${REFERENCE}" not found under src/locales`);
  process.exit(1);
}
const others = langs.filter((l) => l !== REFERENCE);

let failed = false;
const namespaces = readdirSync(join(root, REFERENCE)).filter((f) => f.endsWith(".json"));

for (const ns of namespaces) {
  const ref = new Set(flatten(JSON.parse(readFileSync(join(root, REFERENCE, ns), "utf8"))));
  for (const lang of others) {
    let keys;
    try {
      keys = new Set(flatten(JSON.parse(readFileSync(join(root, lang, ns), "utf8"))));
    } catch {
      failed = true;
      console.error(`✗ ${lang}/${ns}: missing or invalid JSON`);
      continue;
    }
    const missing = [...ref].filter((k) => !keys.has(k));
    const extra = [...keys].filter((k) => !ref.has(k));
    if (missing.length) {
      failed = true;
      console.error(`✗ ${lang}/${ns}: keys in ${REFERENCE} but missing in ${lang}: ${missing.join(", ")}`);
    }
    if (extra.length) {
      failed = true;
      console.error(`✗ ${lang}/${ns}: keys in ${lang} not present in ${REFERENCE}: ${extra.join(", ")}`);
    }
  }
}

if (failed) process.exit(1);
console.log(
  `✓ i18n key parity OK across ${namespaces.length} namespace(s) for ${langs.length} locales (${langs.join(", ")})`,
);
