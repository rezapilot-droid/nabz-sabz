const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
(async () => {
  const browser = await puppeteer.launch({executablePath: await chromium.executablePath(), args: chromium.args, headless: true});
  const page = await browser.newPage();
  await page.setViewport({width: 700, height: 200, deviceScaleFactor: 2});
  await page.goto('file://' + process.cwd() + '/build/test.html', {waitUntil: 'networkidle0'});
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({path: 'build/test.png'});
  await browser.close();
  console.log('done');
})().catch(e => {console.error(e); process.exit(1);});
