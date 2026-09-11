// رندر HTML → PNG (چندخیطه ۳۰۰dpi) + PDF — با پارامتر:
//   node render.js <input.html> <out.png> <out.pdf>
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
const path = require('path');

(async () => {
  const htmlPath = process.argv[2];
  const pngOut = process.argv[3];
  const pdfOut = process.argv[4];
  if (!htmlPath || !pngOut || !pdfOut) {
    console.error('usage: node render.js <in.html> <out.png> <out.pdf>'); process.exit(1);
  }
  const browser = await puppeteer.launch({
    executablePath: await chromium.executablePath(),
    args: chromium.args,
    headless: true,
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 3 });
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle0' });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: pngOut, fullPage: true });
  await page.pdf({
    path: pdfOut, format: 'A4', printBackground: true,
    preferCSSPageSize: true, margin: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  await browser.close();
  console.log('rendered:', path.basename(pngOut), '+', path.basename(pdfOut));
})().catch(e => { console.error(e); process.exit(1); });
