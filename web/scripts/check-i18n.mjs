// CI guard: en/es locale files must have identical key sets (risk #4: i18n drift).
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../src/locales", import.meta.url));

const flatten = (obj, prefix = "") =>
  Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" && v !== null ? flatten(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  );

const langs = ["en", "es"];
let failed = false;

const namespaces = readdirSync(join(root, "en")).filter((f) => f.endsWith(".json"));
for (const ns of namespaces) {
  const keys = {};
  for (const lang of langs) {
    const file = join(root, lang, ns);
    keys[lang] = new Set(flatten(JSON.parse(readFileSync(file, "utf8"))));
  }
  for (const [a, b] of [["en", "es"], ["es", "en"]]) {
    const missing = [...keys[a]].filter((k) => !keys[b].has(k));
    if (missing.length) {
      failed = true;
      console.error(`✗ ${ns}: keys in ${a} but missing in ${b}: ${missing.join(", ")}`);
    }
  }
}

if (failed) process.exit(1);
console.log(`✓ i18n key parity OK across ${namespaces.length} namespace(s) (en ⇄ es)`);
