const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
const path = require('path');
(async () => {
  const browser = await puppeteer.launch({executablePath: await chromium.executablePath(), args: chromium.args, headless: true});
  const page = await browser.newPage();
  await page.setViewport({width: 794, height: 1123});
  await page.goto('file://' + path.resolve(process.argv[2]), {waitUntil: 'networkidle0'});
  await page.evaluate(() => document.fonts.ready);
  const m = await page.evaluate(() => {
    const out = [];
    const sheet = document.querySelector('.sheet');
    const sh = sheet.getBoundingClientRect();
    out.push(['SHEET', Math.round(sh.height)]);
    document.querySelectorAll('.hdr, .subject, .idrow').forEach(el =>
      out.push([el.className, Math.round(el.getBoundingClientRect().height)]));
    document.querySelectorAll('.sec').forEach((el,i) =>
      out.push(['sec'+(i+1), Math.round(el.getBoundingClientRect().height)]));
    // آخرین المانِ در جریان صفحه
    const kids = [...sheet.children].filter(el => getComputedStyle(el).position !== 'absolute');
    const last = kids[kids.length-1].getBoundingClientRect();
    const free = sh.bottom - parseFloat(getComputedStyle(sheet).paddingBottom) - last.bottom;
    out.push(['FREE-SPACE-BEFORE-BOTTOM-PAD', Math.round(free)]);
    out.push(['OVERFLOW', free < 0 ? 'YES !' : 'no']);
    return out;
  });
  m.forEach(([k,v]) => console.log(k.padEnd(28), v));
  await browser.close();
})().catch(e => {console.error(e); process.exit(1);});
