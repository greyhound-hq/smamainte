const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const axeSource = require('axe-core').source;

const PAGES = ['/', '/inspect', '/equipments', '/admin'];
const BASE = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const results = {};
  for (const p of PAGES) {
    const url = new URL(p, BASE).toString();
    const page = await browser.newPage();
    console.log('Checking', url);
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      // inject axe
      await page.evaluate(axeSource);
      const res = await page.evaluate(async () => {
        // run axe with recommended checks; limit to violations
        return await axe.run(document, { runOnly: { type: 'rule', values: ['color-contrast','image-alt','label','aria-valid-attr'] } });
      });
      results[p] = res;
      console.log(`Violations on ${p}:`, res.violations.length);
    } catch (e) {
      console.error('Error scanning', url, e.message || e);
      results[p] = { error: e.message };
    } finally {
      await page.close();
    }
  }
  await browser.close();
  const outPath = path.join(process.cwd(), 'frontend', 'a11y-results.json');
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
  console.log('Saved results to', outPath);
  // print summary
  for (const [p, r] of Object.entries(results)) {
    if (r && r.violations) console.log(p, 'violations:', r.violations.length);
  }
  process.exit(0);
})();
