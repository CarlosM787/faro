// Assembles the public website exactly like .github/workflows/pages.yml (website/* + docs/legal/*.pdf -> /legal/)
// for Cloudflare Workers Static Assets. Nothing outside website/ and the legal PDFs is ever published.
//   node scripts/cf-assets.mjs prod     -> .cf-dist     (production: indexable)
//   node scripts/cf-assets.mjs staging  -> .cf-staging  (workers.dev test address: noindex + robots Disallow)
import { cpSync, rmSync, readdirSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
const mode = process.argv[2] === 'staging' ? 'staging' : 'prod';
const OUT = mode === 'staging' ? '.cf-staging' : '.cf-dist';
rmSync(OUT, { recursive: true, force: true });
cpSync('website', OUT, { recursive: true, filter: (src) => path.basename(src) !== 'CNAME' });
mkdirSync(path.join(OUT, 'legal'), { recursive: true });
for (const f of readdirSync('docs/legal')) if (f.endsWith('.pdf')) cpSync(path.join('docs/legal', f), path.join(OUT, 'legal', f));
const hp = path.join(OUT, '_headers');
const base = existsSync('website/_headers') ? readFileSync('website/_headers', 'utf8') : '';
writeFileSync(hp, base + (mode === 'staging' ? '\n/*\n  X-Robots-Tag: noindex, nofollow\n' : ''));
if (mode === 'staging') writeFileSync(path.join(OUT, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
console.log(`cf-assets: ${mode} -> ${OUT}`);
