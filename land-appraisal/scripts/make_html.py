"""Generate a self-contained RTL HTML report (inline SVG figures + tables)."""
import json, math, os, csv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..'))
D = json.load(open(os.path.join(OUT, 'data', 'analysis.json')))
lots, S, C = D['lots'], D['stats'], D['checks']

def svg(name):
    s = open(os.path.join(OUT, 'figures', name)).read()
    # make it responsive
    s = s.replace('width="100%"', 'width="100%"').replace('<svg ', '<svg class="fig" ', 1)
    return s

lat0, lon0 = 35.542902, 51.487268
def geo(lat, lon):
    R = 6371008.8
    p1, p2 = math.radians(lat0), math.radians(lat)
    dl = math.radians(lon - lon0)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    d = 2 * R * math.asin(math.sqrt(a))
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return d, (math.degrees(math.atan2(x, y)) + 360) % 360

CTX = [('راه امامزاده شعیب (نزدیک‌ترین راه نام‌دار)', 35.5432847, 51.4886756, 'شمال', 'دسترسی محلی — بدون برچسب عرض'),
       ('نقطه مرجع روستای فیروزآباد', 35.5448629, 51.4839269, 'شمال‌غرب', 'بافت مسکونی و خدمات روستایی'),
       ('بخش قلعه‌نو (مرکز تقریبی بخش)', 35.5119433, 51.5155876, 'جنوب‌شرق', 'مرجع صدور مجوز و خدمات اداری'),
       ('روستای چاله‌طرخان', 35.4985838, 51.4778690, 'جنوب', 'دهستان محل وقوع ملک'),
       ('شهر ری', 35.5964, 51.4266, 'شمال‌غرب', 'مرکز شهرستان'),
       ('تهران — میدان آزادی', 35.6997, 51.3561, 'شمال‌غرب', 'کریدور اصلی اشتغال و خدمات')]

def fmt(n, d=2):
    return ('{:,.%df}' % d).format(n).replace(',', '٬').replace('.', '٫')

rows = ''.join(
    f"<tr><td class='id'>{l['id']}</td><td>{l['block']}</td><td class='num'>{fmt(l['area_label'])}</td>"
    f"<td class='num'>{fmt(l['f1'],1)}</td><td>{l['s1']}</td>"
    f"<td class='num'>{fmt(l['f2'],1) if l['f2'] else '—'}</td>"
    f"<td class='num'>{fmt(l['depth'],1)}</td><td class='num'>{fmt(l['width'],1)}</td>"
    f"<td class='num'>{fmt(l['ratio'])}</td><td class='num'>{fmt(l['perimeter'],1)}</td>"
    f"<td class='num'>{fmt(l['compaction'])}</td></tr>"
    for l in lots)

ctx_rows = ''
for name, la, lo, dirn, note in CTX:
    d, brg = geo(la, lo)
    dist = ('%.0f m' % d) if d < 1000 else ('%.1f km' % (d / 1000))
    ctx_rows += (f"<tr><td>{name}</td><td class='num'>{dist}</td><td>{dirn}</td>"
                 f"<td class='num'>{brg:.0f}°</td><td>{note}</td></tr>")

checks = [
    ('زنجیره ابعاد ضلع جنوبی بلوک A', '۱۱٫۱۶ + ۱۱٫۰۰ + ۱۱٫۰۰ + ۱۴٫۲۴ = ۴۷٫۴۰ m',
     'اندازه‌گیری: ۴۷٫۳۳ m', '۰٫۱۵٪'),
    ('زنجیره ابعاد ضلع شمالی بلوک A', '۱۳٫۱۶ + ۱۰٫۰۰ + ۱۰٫۰۰ + ۹٫۲۳ = ۴۲٫۳۹ m',
     'اندازه‌گیری: ۴۲٫۵ m', '≈۰٫۳٪'),
    ('قطعه A-22 و A-23 (کنترل مستطیل کامل)', '۱۱٫۰۰ × ۱۵٫۰۰ = ۱۶۵٫۰۰ m²',
     'درج‌شده: ۱۶۵٫۰۰ m²', '۰٫۰۰٪'),
    ('قطعه B-14 (ذوزنقه)', '(۸٫۸۲ + ۲۰٫۸۰) ÷ ۲ × ۲۰٫۰۰ = ۲۹۶٫۲۰ m²',
     'درج‌شده: ۲۹۶٫۳۱ m²', '۰٫۰۴٪'),
    ('قطعه A-11 (ناسازگاری)', '۱۷٫۱۶ × ۱۳٫۱۶ = ۲۰۸٫۶۷ m²',
     'درج‌شده: ۱۷۳٫۹۲ m² — پخ غربی', '۱۶٫۷٪ ✗'),
    ('جمع ۱۳ قطعه', 'جمع ارقام S= : ۲٬۶۹۵٫۶۸ m²',
     'مساحت ترسیم‌شده: ۲٬۶۶۰ m²', '۱٫۳٪'),
]
check_rows = ''.join(f"<tr><td>{a}</td><td class='mono'>{b}</td><td class='mono'>{c}</td><td class='num'>{d}</td></tr>"
                     for a, b, c, d in checks)

rules = [
    ('مساحت کمتر از ۱۷۵ m²', '۵ قطعه', '۳۸٪', 'زیر حدنصاب رایج تفکیک روستایی (۱۵۰ تا ۲۰۰)'),
    ('مساحت ۱۷۵ تا ۲۰۰ m²', '۳ قطعه', '۲۳٪', 'مرزی — نیازمند استعلام محلی'),
    ('مساحت ۲۰۰ تا ۲۵۰ m²', '۳ قطعه', '۲۳٪', 'منطبق با حدنصاب رایج شهری (۲۰۰)'),
    ('مساحت بیش از ۲۵۰ m²', '۲ قطعه', '۱۵٪', 'مناسب برای قطعات دو واحدی'),
    ('حداقل بر قطعه', '۹٫۵ متر (A-13)', '—', 'کمتر از حد رایج ۱۰ متر — ریسک عدم صدور پروانه'),
    ('حداکثر نسبت طول به عرض', '۲٫۵۸ (B-13)', '—', 'از حد ۳ به ۱ عبور نکرده است'),
    ('نسبت سطح خالص به ناخالص', '≈ ۰٫۶۵', '—', 'متعارف برای تفکیک با سه معبر'),
]
rule_rows = ''.join(f"<tr><td>{a}</td><td class='num'>{b}</td><td class='num'>{c}</td><td>{d}</td></tr>"
                    for a, b, c, d in rules)

streets = [
    ('ST:10m', '۱۰ متر', 'ضلع شمالی بلوک A', 'A-11 تا A-14', '۴۶٫۰ m'),
    ('ST:8m', '۸ متر', 'حد فاصل دو بلوک', 'A-21 تا A-24 و B-11 تا B-13', '۴۷٫۴ m'),
    ('ST:8m', '۸ متر', 'ضلع شرقی / شمال‌شرقی', 'A-14، A-24، B-14 و B-15', '۶۱٫۳ m'),
    ('ST:12m', '۱۲ متر', 'ضلع جنوب‌غربی بلوک B', 'B-11 تا B-13 و B-15', '۵۰٫۴ m'),
]
street_rows = ''.join(f"<tr><td class='id'>{a}</td><td class='num'>{b}</td><td>{c}</td><td>{d}</td><td class='num'>{e}</td></tr>"
                      for a, b, c, d, e in streets)

scen = [
    ('وضع موجود', 13, 207.36, 165.00, 334.42, 'وضع موجود نقشه'),
    ('بازتوزیع متوازن', 13, 207.36, 195, 220, 'حذف ناهمگونی ۱۶۵ تا ۳۳۴ متری'),
    ('تفکیک ۱۲ قطعه‌ای', 12, 224.64, 210, 240, 'همه قطعات بالای ۲۰۰ مترمربع'),
    ('تفکیک ۱۱ قطعه‌ای', 11, 245.06, 230, 260, 'مناسب حدنصاب‌های سخت‌گیرانه‌تر'),
    ('تفکیک ۱۰ قطعه‌ای', 10, 269.57, 260, 280, 'سطح اشغال و پارکینگ راحت‌تر'),
]
scen_rows = ''.join(
    f"<tr><td>{a}</td><td class='num'>{b}</td><td class='num'>{fmt(c)}</td><td class='num'>{fmt(d,0)}</td>"
    f"<td class='num'>{fmt(e,0)}</td><td>{f}</td></tr>" for a, b, c, d, e, f in scen)

checklist = [
    ('۱', 'سند مالکیت و پلاک ثبتی', 'تطبیق شماره پلاک، مساحت سند و حدود اربعه با نقشه'),
    ('۲', 'استعلام طرح هادی روستا', 'تأیید قرارگیری در محدوده بافت، حدنصاب تفکیک و بر حداقل'),
    ('۳', 'استعلام جهاد کشاورزی', 'عدم قرارگیری در اراضی زراعی/باغی مشمول قانون جلوگیری از خرد شدن'),
    ('۴', 'استعلام مسیل و حریم', 'تأیید نبودن در حریم مسیل، حریم راه و حریم گسل'),
    ('۵', 'نقشه‌برداری رسمی (UTM)', 'برداشت گوشه‌ها با GPS و تولید نقشه مختصات‌دار برای سند و پروانه'),
    ('۶', 'بازدید میدانی', 'کنترل دسترسی، دیوارکشی موجود، تصرفات و وضعیت معابر'),
]
check_list_rows = ''.join(f"<tr><td class='num'>{a}</td><td class='id'>{b}</td><td>{c}</td></tr>"
                          for a, b, c in checklist)

html = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>گزارش کارشناسی نقشه تفکیک — ۱۳ قطعه</title>
<style>
  :root {{
    --ink:#1b1b1f; --mut:#6b7280; --acc:#0f4c5c; --acc2:#8c2b1f; --gold:#b8860b;
    --line:#d8dde4; --bg:#f6f7f9;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--bg); color:var(--ink);
    font-family:'Vazirmatn','IRANSans','Segoe UI',Tahoma,sans-serif;
    font-size:15px; line-height:1.9;
  }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:0 18px 64px; }}
  header.top {{
    background:linear-gradient(135deg,#0f4c5c,#123a44); color:#fff;
    padding:38px 0 30px; margin-bottom:26px; border-bottom:5px solid #b8860b;
  }}
  header.top .wrap {{ padding-bottom:0; }}
  .kicker {{ font-size:12.5px; opacity:.85; letter-spacing:.4px; }}
  h1 {{ font-size:29px; margin:8px 0 6px; line-height:1.5; font-weight:800; }}
  .sub {{ font-size:14.5px; opacity:.92; max-width:760px; }}
  .meta {{ display:flex; flex-wrap:wrap; gap:10px 22px; margin-top:16px; font-size:12.5px; opacity:.9; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; margin:22px 0 30px; }}
  .kpi {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px 18px; position:relative; overflow:hidden; }}
  .kpi:after {{ content:''; position:absolute; inset-inline-start:0; top:12px; bottom:12px; width:4px; background:var(--acc); border-radius:3px; }}
  .kpi.gold:after {{ background:var(--gold); }}
  .kpi.red:after {{ background:var(--acc2); }}
  .kpi b {{ display:block; font-size:25px; letter-spacing:.3px; }}
  .kpi span {{ font-size:12.5px; color:var(--mut); }}
  section {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:24px 26px; margin-bottom:20px; }}
  h2 {{ font-size:19px; margin:0 0 4px; color:var(--acc); display:flex; align-items:center; gap:9px; }}
  h2 .n {{ background:var(--acc); color:#fff; font-size:12.5px; border-radius:7px; padding:2px 9px; font-weight:700; }}
  .note {{ color:var(--mut); font-size:13.5px; margin:6px 0 16px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13.5px; margin-top:10px; }}
  th {{ background:#eef3f5; color:var(--acc); font-weight:700; padding:9px 8px; text-align:right; white-space:nowrap; font-size:12.8px; }}
  td {{ padding:8px; border-bottom:1px solid #eef1f4; }}
  tbody tr:nth-child(even) {{ background:#fafbfc; }}
  td.num, th.num {{ text-align:center; font-variant-numeric:tabular-nums; white-space:nowrap; }}
  td.id {{ font-weight:700; color:var(--acc2); }}
  td.mono {{ font-size:12.8px; }}
  tfoot td {{ font-weight:700; background:#f2f5f7; }}
  .fig {{ width:100%; height:auto; display:block; margin:6px 0; border:1px solid var(--line); border-radius:10px; background:#fff; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  @media (max-width:760px) {{ .grid2 {{ grid-template-columns:1fr; }} h1 {{ font-size:23px; }} section {{ padding:18px; }} }}
  .callout {{ border-radius:10px; padding:14px 16px; font-size:13.8px; margin-top:14px; }}
  .warn {{ background:#fdf6e8; border:1px solid #e8d4a4; }}
  .danger {{ background:#fdf0ee; border:1px solid #f0cfc9; }}
  .ok {{ background:#eef7f2; border:1px solid #c7e3d6; }}
  ul {{ padding-inline-start:20px; margin:10px 0; }}
  li {{ margin:6px 0; }}
  .pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }}
  .pill {{ background:#f2f5f7; border:1px solid var(--line); border-radius:999px; padding:4px 12px; font-size:12.5px; color:#374151; }}
  footer {{ text-align:center; color:var(--mut); font-size:12.5px; padding:22px 0 0; }}
  @media print {{
    body {{ background:#fff; font-size:12px; }}
    header.top {{ color:#111; background:#fff; border-bottom:3px solid #0f4c5c; }}
    section {{ break-inside:avoid; border-color:#ccc; }}
    .kpi {{ break-inside:avoid; }}
  }}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="kicker">nabz-sabz · بررسی فنی و کارشناسی املاک</div>
    <h1>گزارش کارشناسی نقشه تفکیک اراضی — ۱۳ قطعه</h1>
    <div class="sub">بررسی فنی، بازسازی هندسی و ارزیابی انطباق نقشه تفکیک زمین مسکونی، و بررسی موقعیت زمین نسبت به بافت منطقه بر پایه مختصات اعلامی.</div>
    <div class="meta">
      <span>سند مبنا: <b>1_29754637390.pdf</b></span>
      <span>خروجی AutoCAD Map 3D 2018</span>
      <span>مختصات: ۳۵٫۵۴۲۹۰۲ N — ۵۱٫۴۸۷۲۶۸ E</span>
      <span>نسخه ۱٫۰</span>
    </div>
  </div>
</header>

<div class="wrap">
  <div class="kpis">
    <div class="kpi gold"><b>۱۳ قطعه</b><span>در دو بلوک A و B</span></div>
    <div class="kpi"><b>{fmt(S['total'])} m²</b><span>جمع مساحت خالص قطعات</span></div>
    <div class="kpi"><b>{fmt(S['mean'])} m²</b><span>میانگین مساحت قطعه</span></div>
    <div class="kpi red"><b>۹٫۵ m</b><span>کمترین بر قطعه — A-13</span></div>
  </div>

  <section>
    <h2><span class="n">۱</span> خلاصه یافته‌ها</h2>
    <ul>
      <li>نقشه یک زمین مسکونی را در قالب <b>۱۳ قطعه</b> و <b>دو بلوک</b> نشان می‌دهد: بلوک A با ۸ قطعه ({fmt(S['total_A'])} m²) و بلوک B با ۵ قطعه ({fmt(S['total_B'])} m²).</li>
      <li>سه معبر با عرض‌های <b>۱۰، ۸ و ۱۲ متر</b> به‌ترتیب در ضلع شمالی، حد فاصل دو بلوک/ضلع شرقی و ضلع جنوب‌غربی.</li>
      <li>جمع مساحت مندرج روی نقشه <b>{fmt(S['total'])} m²</b> است؛ اندازه‌گیری مستقل هندسه ترسیم‌شده {fmt(C['drawn_total'],1)} m² شد → اختلاف <b>{fmt(abs(C['consistency_pct']),2)}٪</b> و سازگاری درونی خوب.</li>
      <li>مقیاس با سه روش مستقل کنترل شد: <b>۵٫۴۰ pt بر متر ≈ ۱:۵۲۵ روی A3</b>؛ یعنی ۱ سانتی‌متر نقشه = ۰٫۵۴ متر. همه اعداد متری و همه مساحت‌ها <b>خالص</b> (بعد از کسر معابر).</li>
      <li><b>۸ قطعه زیر ۲۰۰ m²</b> و <b>۵ قطعه زیر ۱۷۵ m²</b>؛ حداقل بر ۹٫۵ متر (A-13) → ریسک انطباق با حدنصاب محلی.</li>
      <li>موقعیت: روستای فیروزآباد، دهستان چاله‌طرخان، بخش قلعه‌نو، شهرستان ری، تهران — ارتفاع ≈۱٬۰۱۵ متر، شیب کمتر از ۱٪.</li>
    </ul>
    <div class="callout warn">
      <b>نتیجه یک‌خطی:</b> نقشه از نظر هندسی و متری منسجم و برای مذاکره و امکان‌سنجی قابل استفاده است، اما به‌تنهایی «سند تفکیک» نیست:
      نه مهر و امضای مهندس و مراجع محلی دارد، نه شماره پلاک ثبتی، نه جهت شمال و نه مختصات گوشه‌ها.
    </div>
  </section>

  <section>
    <h2><span class="n">۲</span> بازترسیم تحلیلی نقشه</h2>
    <div class="note">۱۳ قطعه با شناسه، مساحت مندرج در نقشه، بر معابر و زنجیره ابعاد. نوارهای کرم = معابر با عرض مندرج. شمالِ اصلی در نقشه درج نشده است.</div>
    {svg('plan-redrawn.svg')}
  </section>

  <section>
    <h2><span class="n">۳</span> جدول مشخصات ۱۳ قطعه</h2>
    <div class="note">مساحت‌ها دقیقاً همان ارقام مندرج در نقشه (S=) هستند؛ «عمق» و «عرض» از مستطیل محیطی کمینه محاسبه شده‌اند و شاخص فشردگی = ۴πA ⁄ P².</div>
    <table>
      <thead><tr>
        <th>شناسه</th><th>بلوک</th><th class="num">مساحت (m²)</th><th class="num">بر اصلی (m)</th><th>معبر اصلی</th>
        <th class="num">بر دوم (m)</th><th class="num">عمق (m)</th><th class="num">عرض (m)</th>
        <th class="num">L/W</th><th class="num">محیط (m)</th><th class="num">فشردگی</th>
      </tr></thead>
      <tbody>{rows}</tbody>
      <tfoot><tr>
        <td>جمع</td><td>—</td><td class="num">{fmt(S['total'])}</td><td class="num">—</td><td>—</td>
        <td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td>
      </tr></tfoot>
    </table>
    <div class="pills">
      <span class="pill">میانه: {fmt(S['median'])} m²</span>
      <span class="pill">انحراف معیار: {fmt(S['sd'])} m²</span>
      <span class="pill">ضریب تغییرات: {fmt(S['cv'],3)}</span>
      <span class="pill">دامنه: {fmt(S['mn'])} تا {fmt(S['mx'])} m²</span>
      <span class="pill">نسبت خالص/ناخالص: {fmt(D['net_ratio'],3)}</span>
    </div>
  </section>

  <section>
    <h2><span class="n">۴</span> توزیع مساحت و انطباق با ضوابط</h2>
    <div class="grid2">
      <div>{svg('lots-areas.svg')}</div>
      <div>
        <table>
          <thead><tr><th>ملاک</th><th class="num">نتیجه</th><th class="num">سهم</th><th>ارزیابی</th></tr></thead>
          <tbody>{rule_rows}</tbody>
        </table>
      </div>
    </div>
    <div class="callout danger">
      <b>ریسک اصلی:</b> اگر حدنصاب محلی ۲۰۰ مترمربع یا حداقل بر ۱۰ متر باشد، بخشی از قطعات (به‌ویژه A-13 با بر ۹٫۵ متر و قطعات زیر ۱۷۵ مترمربع)
      قابل تفکیک رسمی و پروانه‌پذیر نخواهد بود. این موضوع باید پیش از هر معامله با استعلام طرح هادی روشن شود.
    </div>
  </section>

  <section>
    <h2><span class="n">۵</span> کنترل صحت و مقیاس</h2>
    <table>
      <thead><tr><th>مورد کنترل</th><th>مبنای نقشه</th><th>نتیجه اندازه‌گیری</th><th class="num">اختلاف</th></tr></thead>
      <tbody>{check_rows}</tbody>
    </table>
    <div class="callout ok">
      <b>عدم قطعیت:</b> ±۰٫۵٪ در طول‌ها و ±۱٫۵٪ در مساحت‌ها (ناشی از ضخامت خطوط، نشانه‌های برداشت و ساده‌سازی مرزها).
      ارقام برای مذاکره و امکان‌سنجی معتبرند، ولی جایگزین برداشت رسمی نیستند.
    </div>
  </section>

  <section>
    <h2><span class="n">۶</span> معابر و سناریوهای بازتوزیع</h2>
    <table>
      <thead><tr><th>معبر</th><th class="num">عرض</th><th>موقعیت</th><th>قطعات برخوردار</th><th class="num">طول تقریبی</th></tr></thead>
      <tbody>{street_rows}</tbody>
    </table>
    <div class="note" style="margin-top:18px">سناریوهای بازتوزیع با سطح خالص ثابت {fmt(S['total'])} m² و معابر بدون تغییر:</div>
    <table>
      <thead><tr><th>سناریو</th><th class="num">تعداد قطعه</th><th class="num">میانگین (m²)</th>
      <th class="num">کمینه تقریبی</th><th class="num">بیشینه تقریبی</th><th>ملاحظه</th></tr></thead>
      <tbody>{scen_rows}</tbody>
    </table>
    <div class="note">ارقام «کمینه/بیشینه» برآورد کارشناسی برای بازچینش خطوط تقسیم است، نه ترسیم دقیق.</div>
  </section>

  <section>
    <h2><span class="n">۷</span> موقعیت زمین و بافت پیرامون</h2>
    <table>
      <thead><tr><th>کمیت</th><th>مقدار</th></tr></thead>
      <tbody>
        <tr><td>مختصات مرکز (اعلامی)</td><td class="mono">۳۵٫۵۴۲۹۰۲ شمالی — ۵۱٫۴۸۷۲۶۸ شرقی</td></tr>
        <tr><td>درجه-دقیقه-ثانیه</td><td class="mono">۳۵°۳۲′۳۴٫۵″ N — ۵۱°۲۹′۱۴٫۲″ E</td></tr>
        <tr><td>UTM زون ۳۹N (WGS84)</td><td class="mono">E ۵۴۴٬۱۶۸ — N ۳٬۹۳۳٬۳۶۱</td></tr>
        <tr><td>نشانی / آبادی</td><td>روستای فیروزآباد، دهستان چاله‌طرخان، بخش قلعه‌نو، شهرستان ری، استان تهران</td></tr>
        <tr><td>ارتفاع و شیب</td><td>۱٬۰۱۴ تا ۱٬۰۱۹ متر — شیب کلی کمتر از ۱٪</td></tr>
        <tr><td>کد پلاس‌کد</td><td class="mono">GFVP+5W6</td></tr>
        <tr><td>ابعاد کلی مجموعه (با معابر)</td><td>حدود ۸۵ × ۶۵ متر → ناخالص ≈{fmt(D['gross'],0)} m²</td></tr>
      </tbody>
    </table>
    <div class="grid2" style="margin-top:18px">
      <div>{svg('site-context.svg')}</div>
      <div>
        <table>
          <thead><tr><th>عوارض</th><th class="num">فاصله</th><th>جهت</th><th class="num">آزیموت</th><th>توضیح</th></tr></thead>
          <tbody>{ctx_rows}</tbody>
        </table>
      </div>
    </div>
    <div class="callout warn">
      <b>نکته دسترسی:</b> تنها راه شناسایی‌شده در پایگاه‌های نقشه جهانی، معبر محلی «امامزاده شعیب» در فاصله حدود ۳۷ متر از نقطه اعلامی است؛
      تطابق دقیق آن با معابر نقشه (ST:8m/10m/12m) قابل تأیید نیست و باید با بازدید میدانی و GPS کنترل شود.
    </div>
  </section>

  <section>
    <h2><span class="n">۸</span> چک‌لیست اجرایی پیش از معامله</h2>
    <table>
      <thead><tr><th class="num">#</th><th>اقدام</th><th>هدف</th></tr></thead>
      <tbody>{check_list_rows}</tbody>
    </table>
    <div class="callout" style="background:#f4f7f9;border:1px solid var(--line)">
      <b>محدودیت‌های این گزارش:</b> ارقام بر پایه فایل PDF و مختصات اعلامی است؛ هیچ بازدید میدانی، برداشت GPS یا استعلام رسمی انجام نشده است.
      این سند ارزش کارشناسی دارد ولی سند مالکیت، پروانه ساخت یا گواهی تفکیک نیست.
    </div>
  </section>

  <footer>
    گزارش کارشناسی نقشه تفکیک — تولیدشده توسط nabz-sabz · نسخه ۱٫۰ · برای چاپ: Ctrl/Cmd + P
  </footer>
</div>
</body>
</html>
"""

open(os.path.join(OUT, 'index.html'), 'w').write(html)
open(os.path.join(OUT, 'report.html'), 'w').write(html)
print('written', len(html))
