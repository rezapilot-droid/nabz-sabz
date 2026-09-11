# -*- coding: utf-8 -*-
"""
قالب «گزارش آزمایشگاه علوم هشتم» — سبک فانتزی دفترچهٔ دخترانه
(واشی‌تِيپ، استیکر، کارت‌های آب‌نباتی، عکس بزرگ دبیر)
ساخت HTML نسخهٔ دانش‌آموزی و پاسخنامهٔ دبیر از روی فایل دادهٔ آزمایش
"""
import base64, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # workshop/
TEACHER_NAME = "خانم قاسم‌تبار"
HEADER_TITLE = "گزارش آزمایشگاه علوم هشتم"

FA_NUM = "۰۱۲۳۴۵۶۷۸۹"
def fa(n): return "".join(FA_NUM[int(d)] for d in str(n))

def b64(rel):
    opt = rel.replace("assets/", "assets/opt/", 1)
    opt_path = os.path.join(ROOT, opt)
    path = opt_path if os.path.exists(opt_path) else os.path.join(ROOT, rel)
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

# ---------- آیکون‌های سفید عنوان بخش‌ها
ICONS = {
    "target": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="#fff" stroke-width="2.2"/><circle cx="12" cy="12" r="3.2" fill="#fff"/></svg>',
    "bulb":   '<svg viewBox="0 0 24 24"><path fill="#fff" d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2V18h6v-1.3c0-.8.4-1.5 1-2A7 7 0 0 0 12 2z"/><rect x="9.6" y="19" width="4.8" height="1.7" rx=".8" fill="#fff"/><rect x="10.4" y="21.2" width="3.2" height="1.5" rx=".7" fill="#fff"/></svg>',
    "flask":  '<svg viewBox="0 0 24 24"><path fill="#fff" d="M9 2h6v2h-1v5.2l5.3 9.2A2 2 0 0 1 17.6 21H6.4a2 2 0 0 1-1.7-2.6L10 9.2V4H9V2z"/></svg>',
    "list":   '<svg viewBox="0 0 24 24"><circle cx="5" cy="6" r="2" fill="#fff"/><circle cx="5" cy="12" r="2" fill="#fff"/><circle cx="5" cy="18" r="2" fill="#fff"/><rect x="9.5" y="4.8" width="11" height="2.4" rx="1.2" fill="#fff"/><rect x="9.5" y="10.8" width="11" height="2.4" rx="1.2" fill="#fff"/><rect x="9.5" y="16.8" width="11" height="2.4" rx="1.2" fill="#fff"/></svg>',
    "table":  '<svg viewBox="0 0 24 24"><path fill="#fff" d="M3 4h18v16H3V4zm2 2v3h6V6H5zm8 0v3h6V6h-6zM5 11v3h6v-3H5zm8 0v3h6v-3h-6zM5 16v2h6v-2H5zm8 0v2h6v-2h-6z"/></svg>',
    "check":  '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#fff"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="{p}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "think":  '<svg viewBox="0 0 24 24"><path fill="#fff" d="M12 2a7 7 0 0 0-7 7c0 2.6 1.4 4.4 2.9 5.6.6.5 1.1 1.2 1.1 2V18h6v-1.4c0-.8.5-1.5 1.1-2C17.6 13.4 19 11.6 19 9a7 7 0 0 0-7-7zm-3 7a3 3 0 0 1 6 0c0 1.2-.7 1.9-1.5 2.5-.4.3-.8.7-1 1.2h-1c-.2-.5-.6-.9-1-1.2C9.7 10.9 9 10.2 9 9z"/><rect x="9.6" y="19" width="4.8" height="1.7" rx=".8" fill="#fff"/><rect x="10.4" y="21.2" width="3.2" height="1.5" rx=".7" fill="#fff"/></svg>',
}
def icon(name, pill_color="#a86bd8"):
    return ICONS[name].replace("{p}", pill_color)

# ---------- رنگ‌بندی «آب‌نباتی» هر بخش
SECS = [
    dict(num=1, key="target", title="هدف آزمایش",           g1="#f470aa", g2="#e14e93", tint="#fff5fa", border="#f7c0da"),
    dict(num=2, key="bulb",   title="فرضیه",                 g1="#a86bd8", g2="#8f4fd0", tint="#f9f4ff", border="#dcc6f4"),
    dict(num=3, key="flask",  title="مواد و وسایل",          g1="#ff9d6f", g2="#fb7e55", tint="#fff7f2", border="#ffd2ba"),
    dict(num=4, key="list",   title="روش کار",               g1="#3fbf9f", g2="#23a67e", tint="#f2fbf7", border="#bfe6d6"),
    dict(num=5, key="table",  title="جدول ثبت مشاهدات",      g1="#5ab6e8", g2="#3a99d6", tint="#f2f9ff", border="#c0e2f6"),
    dict(num=6, key="check",  title="نتیجه‌گیری",            g1="#f25d8e", g2="#e63f78", tint="#fff3f7", border="#f9bfd3"),
    dict(num=7, key="think",  title="فکر کنید و پاسخ دهید",  g1="#c86bd8", g2="#ad4ec6", tint="#faf3ff", border="#e0c2f2"),
]

def dotted(n=1):
    return '<div class="dline"></div>' * n

def sec_head(s):
    rot = "l" if s["num"] % 2 else "r"
    return (f'<div class="sec-head"><span class="pill {rot}" '
            f'style="background:linear-gradient(90deg,{s["g1"]},{s["g2"]});'
            f'box-shadow:0 0.7mm 0 {s["border"]}">'
            f'<span class="n" style="color:{s["g2"]}">{fa(s["num"])}</span>'
            f'{icon(s["key"], s["g2"])} {s["title"]}</span>'
            f'<span class="line" style="border-color:{s["border"]}"></span></div>')

def sec_card(s, inner, extra=""):
    return (f'<div class="card {extra}" '
            f'style="background:{s["tint"]};border:0.6mm dashed {s["border"]}">{inner}</div>')

# ---------------------------------------------------------------- صفحه
def build_page(data, mode):
    is_ans = (mode == "answer")
    sec = {s["num"]: s for s in SECS}

    # --- مواد (پولارویدها)
    mat_cards = "".join(
        f'''<div class="mat-card">
             <div class="mat-imgwrap"><img src="{b64('assets/' + m['img'])}" alt=""></div>
             <div class="mat-name">{m['name']}</div>
             <div class="mat-amount">{m['amount']}</div>
           </div>'''
        for m in data["materials"])

    # --- روش کار
    steps = "".join(
        f'<li><span class="stepnum">{fa(i+1)}</span><span class="steptxt">{s}</span></li>'
        for i, s in enumerate(data["procedure"]))

    # --- جدول مشاهدات
    obs = data["observation"]
    thead = "".join(f"<th>{c}</th>" for c in obs["columns"])
    tbody = ""
    for r in obs["rows"]:
        if is_ans:
            cells = "".join(f'<td class="ans">{a}</td>' for a in r["answer"])
            tbody += f'<tr><td class="lbl">{r["label"]}</td>{cells}</tr>'
        else:
            tbody += (f'<tr><td class="lbl">{r["label"]}</td>'
                      + '<td></td>' * (len(obs["columns"]) - 1) + '</tr>')

    # --- هدف و روش کار: در نسخهٔ دانش‌آموزی خالی (برای نوشتن دانش‌آموز)
    if is_ans:
        obj_inner = f'<div class="inline-card"><div class="txt">🎯 {data["objective"]}</div></div>'
        steps_inner = f'<ol class="steps">{steps}</ol>'
    else:
        obj_inner = '<div class="blank-big">' + dotted(2) + '</div>'
        steps_inner = ('<div class="blank-grid">' + '<div class="dline"></div>' * 6 + '</div>'
                       + '<div class="write-hint">✎ هدف آزمایش و مراحل کار را خودت بنویس…</div>')

    # --- فرضیه
    s2 = sec[2]
    if is_ans:
        hyp = f'<div class="fill ans">💡 پاسخ پیشنهادی: {data["hypothesis"]["answer"]}</div>'
    else:
        hyp = f'<div class="hint">💭 {data["hypothesis"]["hint"]}</div>' + dotted(2)

    # --- نتیجه‌گیری
    s6 = sec[6]
    concl_inner = (f'<div class="concl-wrap"><img class="medal" src="{b64("assets/icons/strip-4.png")}" alt="">'
                   f'<div class="concl-txt">' +
                   (f'<div class="fill ans">{data["conclusion"]["answer"]}</div>' if is_ans else dotted(2))
                   + '</div></div>')
    concl = sec_card(s6, concl_inner)

    # --- فکر کنید
    s7 = sec[7]
    if is_ans:
        think_boxes = "".join(
            f'''<div class="think-box" style="background:{s7['tint']};border:0.6mm dashed {s7['border']}">
                  <div class="qmark" style="background:linear-gradient(135deg,{s7['g1']},{s7['g2']})">؟</div>
                  <div class="tq">{t["q"]}</div>
                  <div class="ta ans">✿ پاسخ: {t["answer"]}</div>
                </div>'''
            for t in data["think"])
    else:
        think_boxes = "".join(
            f'''<div class="think-box" style="background:{s7['tint']};border:0.6mm dashed {s7['border']}">
                  <div class="qmark" style="background:linear-gradient(135deg,{s7['g1']},{s7['g2']})">؟</div>
                  <div class="tq">{t["q"]}</div>
                  {dotted(1)}
                </div>'''
            for t in data["think"])

    badge = ('<div class="vbadge ans">پاسخنامه<br>دبیر 💚</div>' if is_ans else '')
    sheet_cls = "sheet ans" if is_ans else "sheet"

    html = f"""<!doctype html>
<html dir="rtl" lang="fa"><head><meta charset="utf-8">
<title>{data['subject']}</title>
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
  font-family:'Vazirmatn'; color:#54455c;
  background-color:#ffeff7;
  background-image:
    radial-gradient(#fbd3e7 1.1mm, transparent 1.2mm),
    radial-gradient(#ead9fb 0.9mm, transparent 1mm),
    linear-gradient(160deg,#fff1f8 0%,#fdf0fb 50%,#edf8ff 100%);
  background-size: 9mm 9mm, 13mm 13mm, 100% 100%;
  background-position: 0 0, 4.5mm 4.5mm, 0 0;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}}
.page {{ width:210mm; height:297mm; padding:5.5mm 6.5mm; position:relative; }}
.sheet {{
  width:100%; height:100%; background:#fffdfa;
  border:1.4mm solid #f3a7cf; border-radius:7mm;
  box-shadow:0 0 0 1mm #ffe4f1 inset;
  position:relative; overflow:hidden;
  padding:5mm 5.5mm 12.5mm;
}}
/* واشی‌تِیپ گوشه‌ها */
.tape {{
  position:absolute; width:34mm; height:8mm; opacity:.9; z-index:5;
  background:repeating-linear-gradient(45deg,#ffd9ec 0 3mm,#ffc3e0 3mm 6mm);
  border-radius:1mm; box-shadow:0 0.4mm 0.8mm rgba(200,120,170,.25);
}}
.tape.tl {{ top:-3mm; right:14mm; transform:rotate(-6deg); }}
.tape.tr {{ top:-3mm; left:14mm; transform:rotate(5deg);
  background:repeating-linear-gradient(45deg,#e3d2ff 0 3mm,#d3baf9 3mm 6mm); }}
/* شناورهای تزئینی */
.float {{ position:absolute; z-index:1; }}
.f1 {{ top:33mm; left:3.2mm; width:6mm; transform:rotate(-12deg); }}
.f2 {{ top:86mm; right:2.6mm; width:5mm; transform:rotate(14deg); }}
.f3 {{ top:150mm; left:2.8mm; width:5.4mm; transform:rotate(8deg); }}
.f4 {{ top:214mm; right:3mm; width:6mm; transform:rotate(-10deg); }}

/* ---------- هدر ---------- */
.hdr {{ display:flex; align-items:center; gap:3mm; position:relative; z-index:2; }}
.teacher {{
  flex:0 0 50mm; display:flex; align-items:center; gap:2.2mm;
  background:#fff; border:0.7mm solid #f2bcd8; border-radius:5mm;
  padding:1.8mm 2mm; transform:rotate(-1.6deg);
  box-shadow:0.6mm 0.8mm 0 #f9d7e8;
}}
.teacher img {{ width:20mm; height:20mm; flex:0 0 auto; }}
.teacher .l1 {{ font-size:7.6pt; font-weight:700; color:#b478c8; }}
.teacher .l2 {{ font-size:11.5pt; font-weight:800; color:#8e3f9e; white-space:nowrap; line-height:1.4; }}
.teacher .hearts {{ font-size:7pt; color:#f27bb2; letter-spacing:0.4mm; }}
.banner {{
  flex:1; text-align:center; color:#fff; position:relative;
  background:linear-gradient(90deg,#f472b4,#a86bd8,#7ec9ee);
  border-radius:8mm 8mm 8mm 8mm / 10mm 10mm 10mm 10mm;
  padding:2mm 4mm 2.4mm; box-shadow:0 1.1mm 0 #eab6d8;
}}
.banner .t {{ font-family:'Lalezar'; font-size:16.5pt; line-height:1.25; text-shadow:0 0.6mm 0 rgba(160,60,130,.35); }}
.vbadge {{
  flex:0 0 19mm; text-align:center; font-size:8.4pt; font-weight:800; color:#fff;
  border-radius:5mm; padding:3.2mm 1mm; line-height:1.8; transform:rotate(2.5deg);
}}
.vbadge.stu {{ background:linear-gradient(135deg,#7ec9ee,#4d9fd6); box-shadow:0.5mm 0.8mm 0 #c4e6f6; }}
.vbadge.ans {{ background:linear-gradient(135deg,#4fd0a0,#23a67e); box-shadow:0.5mm 0.8mm 0 #bfe9d6; }}

.subject {{ text-align:center; margin-top:1.4mm; }}
.subject .s1 {{ font-family:'Lalezar'; font-size:12pt; color:#d94380; line-height:1.25; }}
.subject .s2 {{ font-size:8pt; font-weight:600; color:#b293c4; margin-top:0.3mm; }}
.candyline {{ width:64mm; height:1.2mm; margin:0.7mm auto 0; border-radius:99px;
  background:repeating-linear-gradient(90deg,#f470aa 0 3mm,#a86bd8 3mm 6mm,#7ec9ee 6mm 9mm); }}

/* ---------- مشخصات ---------- */
.idrow {{ display:flex; gap:2.5mm; margin-top:1.3mm; }}
.idbox {{
  flex:1; display:flex; align-items:baseline; gap:1.5mm;
  background:#fff; border:0.55mm solid #eec3dd; border-radius:99px;
  padding:1mm 3.5mm 1.3mm; font-size:9pt; font-weight:700; color:#8a5a9e;
  box-shadow:0 0.5mm 0 #fbe3f0;
}}
.idbox .fill2 {{ flex:1; border-bottom:0.5mm dotted #cf9fdf; min-height:4.2mm; }}

/* ---------- بخش‌ها ---------- */
.sec {{ margin-top:1.5mm; }}
.sec-head {{ display:flex; align-items:center; gap:3mm; margin-bottom:1mm; }}
.sec-head .line {{ flex:1; border-top:0.55mm dotted; opacity:.8; }}
.pill {{
  display:flex; align-items:center; gap:2mm; color:#fff; white-space:nowrap;
  border-radius:99px; padding:0.7mm 4mm 1mm;
  font-size:10pt; font-weight:800;
}}
.pill.l {{ transform:rotate(-1.3deg); }}
.pill.r {{ transform:rotate(1.3deg); }}
.pill .n {{
  width:6mm; height:6mm; display:flex; align-items:center; justify-content:center;
  background:#fff; border-radius:50%; font-size:9pt; font-weight:800;
}}
.pill svg {{ width:4.6mm; height:4.6mm; }}
.card {{ border-radius:5.5mm; padding:1mm 3.5mm 1.2mm; }}

.inline-card {{ display:flex; align-items:center; gap:3mm; }}
.inline-card .txt {{ flex:1; font-size:9.5pt; font-weight:600; line-height:1.7; color:#54455c; }}
.hint {{ font-size:8.6pt; font-weight:600; color:#9c5490; line-height:1.6; margin-bottom:0.4mm; }}
.fill {{ font-size:9.5pt; font-weight:600; line-height:1.8; color:#54455c; }}
.fill.ans {{ color:#0f7a55; font-weight:700; }}
.dline {{ border-bottom:0.55mm dotted #c39ad8; height:3mm; }}

/* ---------- مواد: پولاروید ---------- */
.grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:3mm; }}
.mat-card {{
  position:relative; background:#fff; border:0.55mm solid #f4c9de; border-radius:4mm;
  padding:2mm 1mm 1.3mm; text-align:center; box-shadow:0 0.5mm 0 #fce6f1;
}}
.mat-card::before {{
  content:''; position:absolute; top:-1.8mm; right:50%; margin-right:-6mm;
  width:12mm; height:3.6mm; border-radius:1mm; opacity:.95;
  background:repeating-linear-gradient(45deg,#ffe1ef 0 2mm,#ffc9e2 2mm 4mm);
  transform:rotate(-3deg);
}}
.mat-imgwrap {{ height:10.5mm; display:flex; align-items:center; justify-content:center; }}
.mat-imgwrap img {{ max-width:12mm; max-height:12.5mm; }}
.mat-name {{ font-size:9.2pt; font-weight:800; color:#c2447c; margin-top:0.4mm; }}
.mat-amount {{
  display:inline-block; margin-top:0.8mm; font-size:7.6pt; font-weight:700; color:#2f7ba6;
  background:#e8f5fd; border:0.4mm solid #c4e5f8; border-radius:99px; padding:0.1mm 2mm 0.4mm;
}}

/* ---------- روش کار ---------- */
.steps {{ list-style:none; display:grid; grid-template-columns:1fr 1fr; gap:0.4mm 5mm; }}
.steps li {{ display:flex; align-items:flex-start; gap:2.2mm; padding:0.45mm 0; }}
.stepnum {{
  flex:0 0 auto; width:6mm; height:6mm; margin-top:0.3mm;
  display:flex; align-items:center; justify-content:center;
  font-size:9pt; font-weight:800; color:#fff;
  background:linear-gradient(135deg,#3fbf9f,#23a67e); border-radius:60% 40% 55% 45%;
  box-shadow:0 0.5mm 0 #bfe6d6;
}}
.steps li:nth-child(2n) .stepnum {{ background:linear-gradient(135deg,#f470aa,#e14e93); border-radius:40% 60% 45% 55%; box-shadow:0 0.5mm 0 #f7c0da; }}
.steptxt {{ font-size:9pt; font-weight:600; line-height:1.42; color:#54455c; }}

/* ---------- جدول ---------- */
table.obs {{ width:100%; border-collapse:separate; border-spacing:0; background:#fff;
  border-radius:4mm; overflow:hidden; border:0.55mm solid #c0e2f6; }}
table.obs th {{
  color:#fff; font-size:9.6pt; font-weight:800; padding:1.2mm 2mm;
  background:linear-gradient(90deg,#5ab6e8,#3a99d6);
  border-left:0.4mm solid #ffffff55;
}}
table.obs td {{
  border-top:0.45mm dotted #a9d6f0; padding:0.9mm 2.6mm; font-size:9.2pt; font-weight:600;
  color:#54455c; height:4.5mm; vertical-align:middle;
}}
table.obs td.lbl {{ font-weight:800; color:#2377b3; background:#f2f9ff; width:34%; }}
table.obs td.ans {{ color:#0f7a55; font-weight:700; }}

/* ---------- نتیجه‌گیری ---------- */
.concl-wrap {{ display:flex; align-items:center; gap:3mm; }}
.concl-wrap .medal {{ flex:0 0 auto; width:12.5mm; height:12.5mm; }}
.concl-txt {{ flex:1; }}

/* ---------- فکر کنید ---------- */
.think-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:3mm; }}
.think-box {{ border-radius:5mm; padding:1.2mm 3mm 1.2mm; position:relative; }}
.qmark {{
  position:absolute; top:-2.6mm; right:3mm; width:7mm; height:7mm;
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-size:11pt; font-weight:800; border-radius:50%;
  box-shadow:0 0.5mm 0 rgba(0,0,0,.08); transform:rotate(8deg);
}}
.tq {{ font-size:9pt; font-weight:800; color:#8e44ad; line-height:1.55; margin:0.3mm 9mm 0.3mm 0; }}
.ta.ans {{ font-size:8.8pt; font-weight:700; color:#0f7a55; line-height:1.6; }}

/* فشرده‌سازی مخصوص پاسخنامه */
.sheet.ans .mat-imgwrap {{ height:9.6mm; }}
.sheet.ans .mat-imgwrap img {{ max-height:10mm; }}
.sheet.ans .mat-card {{ padding:1.6mm 1mm 1.1mm; }}
.sheet.ans .tq {{ font-size:8.8pt; margin:0.2mm 9mm 0.2mm 0; }}
.sheet.ans .concl-wrap .medal {{ width:11mm; height:11mm; }}

/* ---------- کادرهای خالی دانش‌آموز ---------- */
.blank-big .dline {{ height:5.5mm; }}
.blank-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:3mm 7mm; }}
.blank-grid .dline {{ height:5mm; }}
.write-hint {{ text-align:center; font-size:8pt; font-weight:700; color:#c99ab8; margin-top:0.8mm; }}
.sheet.ans .blank-big, .sheet.ans .blank-grid, .sheet.ans .write-hint {{ display:none; }}
.sheet:not(.ans) .sec {{ margin-top:1.35mm; }}
.sheet:not(.ans) .card {{ padding:0.9mm 3.5mm 1.1mm; }}

/* ---------- فوتر «با عشق» ---------- */
.love {{
  position:absolute; bottom:3.2mm; right:0; left:0; margin:0 12mm;
  display:flex; align-items:center; justify-content:center; gap:2mm;
  background:linear-gradient(90deg,#ffeef8,#f6edff 55%,#eaf7ff);
  border:0.55mm solid #f2bcd8; border-radius:99px;
  box-shadow:0 0.6mm 0 #fbe0ef, 0 0 0 0.6mm #ffffff inset;
  padding:1.4mm 6mm 1.7mm;
}}
.love .lv1, .love .lv2 {{ font-size:9.6pt; font-weight:800; color:#c2447c; white-space:nowrap; }}
.love .lv2 {{ color:#8e44ad; }}
.love .lvh {{ width:4.6mm; height:4.6mm; margin:0 0.4mm; }}
.love .lv3 {{ font-size:9pt; margin-right:1mm; }}

/* ---------- فشرده‌سازی حالت پاسخنامه ---------- */
.sheet.ans .sec {{ margin-top:1.1mm; }}
.sheet.ans .card {{ padding:1.1mm 3.5mm 1.3mm; }}
.sheet.ans .fill.ans {{ line-height:1.5; font-size:9pt; }}
.sheet.ans .ta.ans {{ line-height:1.42; font-size:8.6pt; }}
.sheet.ans table.obs td {{ height:6.2mm; padding:0.4mm 2.6mm; }}
.sheet.ans .think-box {{ padding:1.6mm 3mm 1.7mm; }}
.sheet.ans .steps li {{ padding:0.05mm 0; }}
.sheet.ans .idrow {{ margin-top:2mm; }}
.sheet.ans .subject {{ margin-top:1mm; }}
</style></head>
<body><div class="page"><div class="{sheet_cls}">
  <div class="tape tl"></div><div class="tape tr"></div>

  <img class="float f1" src="{b64('assets/icons/strip-4.png')}" alt="">
  <img class="float f2" src="{b64('assets/icons/strip-0.png')}" alt="">
  <img class="float f3" src="{b64('assets/icons/strip-5.png')}" alt="">
  <img class="float f4" src="{b64('assets/icons/strip-1.png')}" alt="">

  <div class="hdr">
    <div class="teacher">
      <img src="{b64('assets/teacher-avatar.png')}" alt="">
      <div>
        <div class="l1">دبیر آزمایشگاه:</div>
        <div class="l2">{TEACHER_NAME}</div>
        <div class="hearts">♥ ♥ ♥</div>
      </div>
    </div>
    <div class="banner">
      <div class="t">{HEADER_TITLE}</div>
      
    </div>
    {badge}
  </div>

  <div class="subject">
    <div class="s1">موضوع آزمایش: {data['subject']}</div>
    <div class="candyline"></div>
  </div>

  <div class="idrow">
    <div class="idbox">نام و نام خانوادگی: <span class="fill2"></span></div>
    <div class="idbox" style="flex:0 0 34mm;">شماره کلاس: <span class="fill2"></span></div>
    <div class="idbox" style="flex:0 0 46mm;">تاریخ: ....... / ....... / .......</div>
  </div>

  <div class="sec">
    {sec_head(sec[1])}
    {sec_card(sec[1], obj_inner)}
  </div>

  <div class="sec">
    {sec_head(sec[2])}
    {sec_card(sec[2], hyp)}
  </div>

  <div class="sec">
    {sec_head(sec[3])}
    <div class="grid">{mat_cards}</div>
  </div>

  <div class="sec">
    {sec_head(sec[4])}
    {sec_card(sec[4], steps_inner)}
  </div>

  <div class="sec">
    {sec_head(sec[5])}
    <table class="obs"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>
  </div>

  <div class="sec">
    {sec_head(sec[6])}
    {concl}
  </div>

  <div class="sec">
    {sec_head(sec[7])}
    <div class="think-grid">{think_boxes}</div>
  </div>

  <div class="love">
    <span class="lv1">طراحی شده با</span>
    <svg class="lvh" viewBox="0 0 24 24"><path fill="#ef5f9a" d="M12 21s-7.5-4.7-10-9C.4 8.6 2.2 4.5 6 4.5c2.2 0 3.6 1.2 4.4 2.5h1.2c.8-1.3 2.2-2.5 4.4-2.5 3.8 0 5.6 4.1 4 7.5-2.5 4.3-10 9-10 9z"/></svg>
    <span class="lv2">عشق، برای دانش‌آموزان دبیرستان هوردخت</span>
    <span class="lv3">🌸</span>
  </div>

</div></div></body></html>"""
    return html


def build_both(data, out_prefix):
    for mode in ("student", "answer"):
        html = build_page(data, mode)
        with open(f"{out_prefix}-{mode}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"built: {out_prefix}-{mode}.html")


if __name__ == "__main__":
    import sys
    slug = sys.argv[1] if len(sys.argv) > 1 else "fasl1-azmayesh1"
    with open(os.path.join(ROOT, "experiments", slug + ".json"), encoding="utf-8") as f:
        data = json.load(f)
    build_both(data, os.path.join(ROOT, "build", slug))
