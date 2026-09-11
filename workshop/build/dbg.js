const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
(async () => {
  const browser = await puppeteer.launch({executablePath: await chromium.executablePath(), args: chromium.args, headless: true});
  const page = await browser.newPage();
  await page.setViewport({width: 794, height: 1123});
  await page.goto('file://' + process.cwd() + '/build/fasl1-azmayesh1-student.html', {waitUntil: 'networkidle0'});
  await page.evaluate(() => document.fonts.ready);
  const rows = await page.evaluate(() => {
    const sheet = document.querySelector('.sheet');
    const s = sheet.getBoundingClientRect();
    return [...sheet.children].map(el => {
      const r = el.getBoundingClientRect();
      return `${(el.className||el.tagName).toString().slice(0,20).padEnd(20)} pos=${getComputedStyle(el).position} top=${Math.round(r.top-s.top)} bottom=${Math.round(r.bottom-s.top)}`;
    });
  });
  console.log(rows.join('\n'));
  await browser.close();
})();
