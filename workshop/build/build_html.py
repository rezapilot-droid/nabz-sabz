# -*- coding: utf-8 -*-
"""
ساخت کاربرگ آزمایش علوم هشتم — فصل اول
خروجی: A4.html → A4.png → A4.pdf → JPG نهایی + DOCX قابل ویرایش
"""
import base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # workshop/
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(os.path.dirname(ROOT), "worksheets")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- محتوا
TEACHER   = "نام آموزگار: خانم قاسم‌تبار"
CHAPTER   = "فصل اول: مخلوط و جداسازی مواد"
EXPERIMENT= "آزمایش ۱: مخلوط‌های همگن و ناهمگن"
SUBTITLE  = "برگرفته از فعالیت صفحهٔ ۳ کتاب علوم تجربی پایهٔ هشتم"
BISM      = "بسمه تعالی"

MATERIALS = [
    ("beaker-water", "بشر شماره‌دار", "۲ عدد"),
    ("water-jug",    "آب",            "۱۰۰ میلی‌لیتر در هر بشر"),
    ("measuring-spoon", "قاشقک",      "۱ عدد"),
    ("salt-pinches", "نمک خوراکی",    "۱ قاشقک سرپُر"),
    ("soil-spoon",   "خاک باغچه",     "۱ قاشقک سرپُر"),
    ("rod-stir",     "همزن شیشه‌ای",  "۱ عدد"),
]
MATERIAL_IMAGES = {
    "beaker-water":    "assets/beaker-water.png",
    "water-jug":       "assets/water-jug.png",
    "measuring-spoon": "assets/measuring-spoon.png",
    "salt-pinches":    "assets/salt-pinches.png",
    "soil-spoon":      "assets/soil-spoon.png",
    "rod-stir":        "assets/rod-stir.png",
}

STEPS = [
    "دو بشر را انتخاب کنید و با چسب کاغذی برای آن‌ها شمارهٔ ۱ و ۲ بگذارید.",
    "در هر دو بشر به مقدار یکسان (۱۰۰ میلی‌لیتر) آب بریزید.",
    "در بشر شمارهٔ ۱ یک قاشقک خاک باغچه و در بشر شمارهٔ ۲ یک قاشقک نمک خوراکی بریزید.",
    "محتویات هر دو بشر را با همزن شیشه‌ای به‌آرامی و کاملاً به هم بزنید.",
    "چند لحظه صبر کنید و سپس رنگ و شفافیت محتویات دو بشر را با هم مقایسه کنید.",
    "مشاهدات خود را در کادرهای بخش «مشاهدات و نتیجه‌گیری» یادداشت کنید.",
]

OBS1_TITLE = "بشر شمارهٔ ۱ — مخلوط آب و خاک"
OBS2_TITLE = "بشر شمارهٔ ۲ — مخلوط آب و نمک"
OBS_Q = "پس از هم زدن، مخلوط چگونه به نظر می‌رسد؟ (شفاف یا کدر؟)"

CONCLUSION = ("نتیجه‌گیری: با توجه به مشاهدات، مخلوط شماره ..... همگن (محلول) و "
              "مخلوط شماره ..... ناهمگن است؛ زیرا ...................")
SAFETY = ("نکتهٔ ایمنی: مواد آزمایشگاهی را نچشید و با چشمان خود به آن‌ها نزدیک نکنید؛ "
          "پس از پایان آزمایش، دست‌های خود را با آب و صابون بشویید.")
FOOTER_TEXT = "کاربرگ علوم تجربی — پایهٔ هشتم | با آرزوی موفقیت برای دانش‌مندان کوچک"

# ---------------------------------------------------------------- ابزار
def b64(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def icon(name):
    return b64(f"assets/icons/{name}")

# تزئین‌های کوچک SVG (قلب، ستارهٔ چهارپر، گل)
HEART = '<svg class="deco" viewBox="0 0 24 24"><path fill="{c}" d="M12 21s-7.5-4.7-10-9C.4 8.6 2.2 4.5 6 4.5c2.2 0 3.6 1.2 4.4 2.5h1.2c.8-1.3 2.2-2.5 4.4-2.5 3.8 0 5.6 4.1 4 7.5-2.5 4.3-10 9-10 9z" opacity=".9"/></svg>'
SPARK = '<svg class="deco" viewBox="0 0 24 24"><path fill="{c}" d="M12 1l2.4 8.6L23 12l-8.6 2.4L12 23l-2.4-8.6L1 12l8.6-2.4z" opacity=".9"/></svg>'
FLOWER= ('<svg class="deco" viewBox="0 0 24 24"><g fill="{c}" opacity=".9">'
         '<circle cx="12" cy="5" r="3.4"/><circle cx="12" cy="19" r="3.4"/>'
         '<circle cx="5" cy="12" r="3.4"/><circle cx="19" cy="12" r="3.4"/>'
         '<circle cx="12" cy="12" r="3" fill="#fff"/></g></svg>')

def deco(shape, c, size="4mm", static=False):
    pos = "position:static;" if static else ""
    return shape.replace("{c}", c).replace('class="deco"', f'class="deco" style="{pos}width:{size};height:{size}"')

# ---------------------------------------------------------------- HTML
def build_html():
    icons_footer = "".join(
        f'<img src="{icon(f"strip-{i}.png")}" alt="">' for i in range(7)
    )

    mat_cards = ""
    for key, name, amount in MATERIALS:
        mat_cards += f"""
        <div class="mat-card">
          <div class="mat-imgwrap"><img src="{b64(MATERIAL_IMAGES[key])}" alt=""></div>
          <div class="mat-name">{name}</div>
          <div class="mat-amount">{amount}</div>
        </div>"""

    steps_html = "".join(
        f'<li><span class="stepnum">{i+1}</span><span class="steptxt">{s}</span></li>'
        for i, s in enumerate(STEPS)
    )

    dotted = '<div class="dline"></div>'
    html = f"""<!doctype html>
<html dir="rtl" lang="fa"><head><meta charset="utf-8">
<title>{EXPERIMENT}</title>
<style>
@font-face{{font-family:'Vazirmatn';src:url('../fonts/Vazirmatn-Regular.ttf') format('truetype');font-weight:400}}
@font-face{{font-family:'Vazirmatn';src:url('../fonts/Vazirmatn-Medium.ttf') format('truetype');font-weight:500}}
@font-face{{font-family:'Vazirmatn';src:url('../fonts/Vazirmatn-SemiBold.ttf') format('truetype');font-weight:600}}
@font-face{{font-family:'Vazirmatn';src:url('../fonts/Vazirmatn-Bold.ttf') format('truetype');font-weight:700}}
@font-face{{font-family:'Vazirmatn';src:url('../fonts/Vazirmatn-ExtraBold.ttf') format('truetype');font-weight:800}}
@font-face{{font-family:'Lalezar';src:url('../fonts/Lalezar-Regular.ttf') format('truetype')}}

@page {{ size: A4; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:210mm; height:297mm; }}
body {{
  font-family:'Vazirmatn'; color:#5b4a5e;
  background: linear-gradient(160deg,#ffeef8 0%,#f3e8ff 55%,#e8f6fd 100%);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}}
.page {{ position:relative; width:210mm; height:297mm; padding:6mm 7mm; }}

/* قاب کاربرگ */
.sheet {{
  position:relative; width:100%; height:100%;
  background:#fffdfa; border:1.2mm solid #f5b8d0; border-radius:6mm;
  padding:4.5mm 6mm 12mm; overflow:hidden;
  box-shadow: 0 0 0 0.8mm #ffe1ee inset;
}}
.deco {{ position:absolute; }}

/* --- هدر --- */
.bism {{
  width:46mm; margin:0 auto; text-align:center; font-size:11.5pt; font-weight:700; color:#8a5a9e;
  background:#f6ecfc; border:0.5mm solid #e3c7f2; border-radius:99px; padding:0.8mm 0 1mm;
}}
.hdr {{ display:flex; align-items:center; gap:2.5mm; margin-top:1.8mm; }}
.hdr .side {{
  flex:0 0 47mm; font-size:9.2pt; font-weight:700; line-height:1.9;
  border-radius:3mm; padding:1.6mm 3mm; text-align:center;
}}
.hdr .side.teacher {{
  color:#7c4a93; background:linear-gradient(135deg,#fde7f3,#f3e8ff); border:0.5mm solid #f2c4dd;
}}
.hdr .side.meta {{
  color:#6d5a86; background:#fdf4fa; border:0.5mm dashed #e9b9d6; font-weight:600; font-size:8.8pt;
}}
.hdr .side.meta b {{ color:#c2447c; }}
.titles {{ flex:1; text-align:center; padding:0 1mm; }}
.chapter {{ font-family:'Lalezar'; font-size:19pt; line-height:1.3;
  background:linear-gradient(90deg,#e0559b,#9b59d0); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.exp {{ font-family:'Lalezar'; font-size:14.5pt; color:#d4547e; margin-top:0.4mm; }}
.subtitle {{ font-size:8.2pt; font-weight:500; color:#a98cb8; margin-top:0.8mm; }}

/* --- عنوان بخش‌ها --- */
.sec-head {{ display:flex; align-items:center; gap:2.5mm; margin:2.4mm 0 2mm; }}
.sec-head .line {{ flex:1; height:0; border-top:0.5mm dotted #e5a9c9; }}
.sec-title {{
  display:flex; align-items:center; gap:2mm;
  font-size:12pt; font-weight:800; color:#fff; white-space:nowrap;
  background:linear-gradient(90deg,#ef6fae,#a86bd8); border-radius:99px; padding:1.2mm 5mm 1.6mm;
  box-shadow:0 0.6mm 0 #e8b7d6;
}}

/* --- کارت‌های مواد --- */
.grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:3mm; }}
.mat-card {{
  background:linear-gradient(180deg,#fff6fb,#fdeff7); border:0.55mm solid #f6c6dd; border-radius:4mm;
  padding:1.7mm 1.5mm 1.9mm; text-align:center;
}}
.mat-imgwrap {{ height:21mm; display:flex; align-items:center; justify-content:center; }}
.mat-imgwrap img {{ max-width:20mm; max-height:20.5mm; }}
.mat-name {{ font-size:9.8pt; font-weight:800; color:#b23e78; margin-top:0.8mm; }}
.mat-amount {{
  display:inline-block; margin-top:1.2mm; font-size:7.8pt; font-weight:700; color:#3d7fa8;
  background:#e3f4fd; border:0.4mm solid #bfe3f7; border-radius:99px; padding:0.3mm 2.4mm 0.6mm;
}}

/* --- مراحل --- */
.steps {{ list-style:none; margin-top:0.6mm; }}
.steps li {{ display:flex; align-items:flex-start; gap:2.8mm; padding:1.05mm 0; }}
.stepnum {{
  flex:0 0 auto; width:6.8mm; height:6.8mm; margin-top:0.2mm;
  display:flex; align-items:center; justify-content:center;
  font-size:9.8pt; font-weight:800; color:#fff;
  background:linear-gradient(135deg,#f27bb2,#a86bd8); border-radius:50%;
  box-shadow:0 0.5mm 0 #e3aed2;
}}
.steptxt {{ font-size:10.6pt; font-weight:600; line-height:1.85; color:#54455c; padding-top:0.7mm; }}

/* --- مشاهدات --- */
.obs-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:3.5mm; }}
.obs-box {{
  background:#fdf6fc; border:0.55mm solid #ecc2e2; border-radius:4mm; padding:2.2mm 3mm 2.6mm;
}}
.obs-box.mint {{ background:#f4fbf8; border-color:#bfe6d2; }}
.obs-title {{ font-size:10pt; font-weight:800; color:#a8377c; text-align:center; margin-bottom:0.6mm; }}
.obs-box.mint .obs-title {{ color:#1f8a63; }}
.obs-q {{ font-size:8.6pt; font-weight:600; color:#8a7596; text-align:center; margin-bottom:1.2mm; }}
.obs-box.mint .obs-q {{ color:#57907a; }}
.dline {{ border-bottom:0.55mm dotted #bb8fd4; height:6.3mm; }}
.obs-box.mint .dline {{ border-color:#8cc9a8; }}

.conclusion {{
  margin-top:2.2mm; display:flex; align-items:center; gap:3mm;
  background:linear-gradient(135deg,#fff2f9,#f5efff);
  border:0.55mm solid #e5b8ec; border-radius:4mm; padding:1.5mm 3.5mm 1.9mm;
}}
.conclusion .cta {{ flex:1; font-size:10pt; font-weight:800; color:#8e44ad; line-height:2; }}
.conclusion .dline {{ border-color:#d5a8e0; }}
.conclusion img {{ flex:0 0 auto; width:18mm; height:18mm; }}

/* --- ایمنی --- */
.safety {{
  margin-top:2.2mm; display:flex; align-items:center; gap:2.8mm;
  background:#fff8e8; border:0.55mm solid #f5d98d; border-radius:99px; padding:1.8mm 4.5mm;
}}
.safety .ic {{ flex:0 0 auto; width:6mm; height:6mm; }}
.safety .tx {{ font-size:9.3pt; font-weight:700; color:#9a6b12; line-height:1.6; }}

/* --- پاصفحه --- */
.footer {{
  position:absolute; bottom:3.4mm; right:6mm; left:6mm;
  display:flex; align-items:center; gap:3mm;
  background:#ffffff; border:0.5mm solid #f3d0e4; border-radius:99px; padding:1mm 4mm;
}}
.footer .strip {{ display:flex; align-items:center; gap:1.4mm; flex:1; justify-content:center; }}
.footer .strip img {{ height:9mm; width:auto; }}
.footer .ftext {{ font-size:7.8pt; font-weight:700; color:#b06aa0; white-space:nowrap; }}
</style></head>
<body><div class="page"><div class="sheet">

  {deco(SPARK,'#f7b8d9','5mm')}
  <div class="deco" style="top:6mm;right:9mm;">{deco(FLOWER,'#e9a9d6','4.4mm').replace('class="deco" ','')}</div>
  <div class="deco" style="top:7mm;left:10mm;">{deco(SPARK,'#c9a7ec','4.6mm').replace('class="deco" ','')}</div>
  <div class="deco" style="bottom:15mm;right:8mm;">{deco(HEART,'#f5b9cf','4.2mm').replace('class="deco" ','')}</div>

  <div class="bism">{BISM}</div>

  <div class="hdr">
    <div class="side meta">
      نام و نام خانوادگی: ...........................<br>
      کلاس: هشتم ....... &nbsp;|&nbsp; تاریخ: ....... / ....... / .......
    </div>
    <div class="titles">
      <div class="chapter">{CHAPTER}</div>
      <div class="exp">{EXPERIMENT}</div>
      <div class="subtitle">{SUBTITLE}</div>
    </div>
    <div class="side teacher">{TEACHER}</div>
  </div>

  <div class="sec-head"><span class="sec-title">{deco(FLOWER,'#ffffff','4.2mm',True)} لوازم و مواد لازم برای آزمایش</span><span class="line"></span></div>
  <div class="grid">{mat_cards}</div>

  <div class="sec-head"><span class="sec-title">{deco(SPARK,'#ffffff','4mm',True)} روش اجرای آزمایش</span><span class="line"></span></div>
  <ol class="steps">{steps_html}</ol>

  <div class="sec-head"><span class="sec-title">{deco(HEART,'#ffffff','4.2mm',True)} مشاهدات و نتیجه‌گیری</span><span class="line"></span></div>
  <div class="obs-grid">
    <div class="obs-box">
      <div class="obs-title">{OBS1_TITLE}</div>
      <div class="obs-q">{OBS_Q}</div>
      {dotted}{dotted}{dotted}
    </div>
    <div class="obs-box mint">
      <div class="obs-title">{OBS2_TITLE}</div>
      <div class="obs-q">{OBS_Q}</div>
      {dotted}{dotted}{dotted}
    </div>
  </div>
  <div class="conclusion">
    <div class="cta">{CONCLUSION}</div>
    <img src="{b64('assets/beakers-two.png')}" alt="">
  </div>

  <div class="safety">
    <svg class="ic" viewBox="0 0 24 24"><path fill="#f5b921" d="M12 2L1 21h22L12 2z"/><rect x="11" y="9" width="2" height="6" rx="1" fill="#7a5a00"/><circle cx="12" cy="17.6" r="1.2" fill="#7a5a00"/></svg>
    <div class="tx">{SAFETY}</div>
  </div>

  <div class="footer">
    <div class="ftext">{FOOTER_TEXT}</div>
    <div class="strip">{icons_footer}</div>
  </div>

</div></div></body></html>"""

    with open(os.path.join(BUILD, "A4.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML built:", os.path.join(BUILD, "A4.html"))

if __name__ == "__main__":
    build_html()
