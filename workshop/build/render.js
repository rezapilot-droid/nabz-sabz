// رندر A4.html → PNG (چندخیطه) و PDF
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
const path = require('path');

(async () => {
  const htmlPath = process.argv[2] || path.join(process.cwd(), 'build', 'A4.html');
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

  await page.screenshot({ path: path.join(process.cwd(), 'build', 'A4.png'), fullPage: true });

  await page.pdf({
    path: path.join(process.cwd(), 'build', 'A4.pdf'),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  await browser.close();
  console.log('rendered: build/A4.png + build/A4.pdf');
})().catch(e => { console.error(e); process.exit(1); });
