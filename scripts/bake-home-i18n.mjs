// Bakes the bilingual homepage into two static pages so crawlers and no-JS readers get the text.
//   node scripts/bake-home-i18n.mjs
//
// Source:  website-src/home.template.html  (markup with data-i18n keys + the `const T = {...}` dictionary)
// Output:  website/index.html    (English, canonical https://faroquant.com/)
//          website/es/index.html (Spanish, canonical https://faroquant.com/es/)
//
// The template is parsed and filled by Chromium's own DOM (Playwright, scripts disabled), so the
// output is exactly what the old in-browser setLang() produced, without the runtime switch. Each
// page links to the other with hreflang; the EN/ES control becomes two links, like /methodology/.
// Playwright comes from C:/dev/agent-workstation/web-tools on this PC (a dev-time tool only; the
// generated HTML is committed and GitHub Pages serves it as-is).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'C:/dev/agent-workstation/web-tools/node_modules/playwright');

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TEMPLATE = path.join(ROOT, 'website-src', 'home.template.html');
const SITE = 'https://faroquant.com';
const html = readFileSync(TEMPLATE, 'utf8');

const m = html.match(/const T = (\{[\s\S]*?\n\});\s*\nfunction setLang/);
if (!m) throw new Error('dictionary `const T = {...}` not found in the template');
const T = vm.runInNewContext(`(${m[1]})`);
for (const k of Object.keys(T.en)) if (!(k in T.es)) throw new Error(`missing Spanish string: ${k}`);

// Head text the dictionary doesn't carry.
const META = {
  en: null, // keep the template's English head as written
  es: {
    title: 'Faro — Copiloto de portafolio con IA',
    description: 'Análisis de portafolio bilingüe y de código abierto. Un motor cuantitativo desde primeros principios y un copiloto de IA que muestra su trabajo: las cifras sin respaldo se detectan y se marcan. English y español.',
    ogTitle: 'Faro — Copiloto de portafolio con IA',
    ogDescription: 'Métricas de riesgo desde primeros principios, explicadas por una IA cuyas cifras se comparan con las del motor. Código abierto, bilingüe, corre gratis en tu computadora.',
  },
};
const OUT = { en: path.join(ROOT, 'website', 'index.html'), es: path.join(ROOT, 'website', 'es', 'index.html') };
const URL_OF = { en: `${SITE}/`, es: `${SITE}/es/` };

const browser = await chromium.launch();
const ctx = await browser.newContext({ javaScriptEnabled: false });
for (const L of ['en', 'es']) {
  const page = await ctx.newPage();
  await page.route('**/*', (r) => r.abort());
  await page.setContent(html, { waitUntil: 'domcontentloaded' });
  const out = await page.evaluate(({ T, L, META, URL_OF }) => {
    const d = T[L];
    document.documentElement.lang = L;
    document.querySelectorAll('[data-i18n]').forEach((el) => { const v = d[el.dataset.i18n]; if (v !== undefined) el.textContent = v; });
    document.querySelectorAll('[data-i18n-html]').forEach((el) => { const v = d[el.dataset.i18nHtml]; if (v !== undefined) el.innerHTML = v; });
    document.querySelectorAll('[data-i18n-alt]').forEach((el) => { const v = d[el.dataset.i18nAlt]; if (v !== undefined) el.alt = v; });
    document.getElementById('hero-h1').innerHTML = d['hero.h1'];
    // The runtime dictionary + switch are no longer needed.
    [...document.scripts].filter((s) => s.textContent.includes('const T = {')).forEach((s) => s.remove());
    // EN/ES become links between the two URLs.
    const sw = document.querySelector('span.lang');
    sw.innerHTML = `<a id="btn-en" href="/" hreflang="en" lang="en"${L === 'en' ? ' class="on" aria-current="page"' : ''}>EN</a>` +
      `<a id="btn-es" href="/es/" hreflang="es" lang="es"${L === 'es' ? ' class="on" aria-current="page"' : ''}>ES</a>`;
    // Root-relative asset and link URLs, so /es/ resolves them too.
    document.querySelectorAll('[src],[href]').forEach((el) => {
      for (const a of ['src', 'href']) {
        const v = el.getAttribute(a);
        if (v && !/^(https?:|mailto:|tel:|data:|#|\/)/.test(v)) el.setAttribute(a, '/' + v);
      }
    });
    // Head: canonical, og:url, hreflang pair, and Spanish head text.
    const head = document.head;
    head.querySelector('link[rel="canonical"]').setAttribute('href', URL_OF[L]);
    head.querySelector('meta[property="og:url"]').setAttribute('content', URL_OF[L]);
    head.querySelectorAll('link[rel="alternate"][hreflang]').forEach((n) => n.remove());
    const canon = head.querySelector('link[rel="canonical"]');
    [['en', URL_OF.en], ['es', URL_OF.es], ['x-default', URL_OF.en]].reverse().forEach(([hl, href]) => {
      const l = document.createElement('link'); l.rel = 'alternate'; l.hreflang = hl; l.href = href; canon.after(l);
    });
    const meta = META[L];
    if (meta) {
      document.title = meta.title;
      head.querySelector('meta[name="description"]').setAttribute('content', meta.description);
      head.querySelector('meta[property="og:title"]').setAttribute('content', meta.ogTitle);
      head.querySelector('meta[property="og:description"]').setAttribute('content', meta.ogDescription);
    }
    head.prepend(document.createComment(' GENERATED by scripts/bake-home-i18n.mjs from website-src/home.template.html. Edit the template, then re-run. '));
    return '<!DOCTYPE html>\n' + document.documentElement.outerHTML + '\n';
  }, { T, L, META, URL_OF });
  mkdirSync(path.dirname(OUT[L]), { recursive: true });
  writeFileSync(OUT[L], out);
  await page.close();
  console.log(`baked ${L} → ${path.relative(ROOT, OUT[L])} (${out.length} bytes)`);
}
await browser.close();
