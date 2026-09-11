# -*- coding: utf-8 -*-
"""
قالب «گزارش آزمایشگاه علوم هشتم» — فرمت استاندارد گزارش‌دهی (نمونهٔ خوارزمی)
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

# ---------- آیکون‌های کوچک داخل عنوان بخش‌ها (SVG سفید)
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

def dotted(n=1, cls=""):
    return f'<div class="dline {cls}"></div>' * n

# ---------------------------------------------------------------- صفحه
def build_page(data, mode):
    """mode: 'student' یا 'answer'"""
    is_ans = (mode == "answer")

    # --- کارت‌های مواد
    mat_cards = "".join(
        f'''<div class="mat-card">
             <div class="mat-imgwrap"><img src="{b64('assets/' + m['img'])}" alt=""></div>
             <div class="mat-name">{m['name']}</div>
             <div class="mat-amount">{m['amount']}</div>
           </div>'''
        for m in data["materials"])

    # --- مراحل روش کار
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

    # --- فرضیه
    if is_ans:
        hyp = f'<div class="fill ans">پاسخ پیشنهادی: {data["hypothesis"]["answer"]}</div>'
    else:
        hyp = f'<div class="hint">{data["hypothesis"]["hint"]}</div>' + dotted(2)

    # --- نتیجه‌گیری
    concl = (f'<div class="fill ans">{data["conclusion"]["answer"]}</div>' if is_ans
             else dotted(2))

    # --- فکر کنید و پاسخ دهید
    if is_ans:
        think_boxes = "".join(
            f'''<div class="think-box">
                  <div class="tq">{fa(i+1)}. {t["q"]}</div>
                  <div class="ta ans">پاسخ: {t["answer"]}</div>
                </div>'''
            for i, t in enumerate(data["think"]))
    else:
        think_boxes = "".join(
            f'''<div class="think-box">
                  <div class="tq">{fa(i+1)}. {t["q"]}</div>
                  {dotted(2)}
                </div>'''
            for i, t in enumerate(data["think"]))

    sheet_cls = "sheet ans" if is_ans else "sheet"
    badge = ('<div class="vbadge ans-badge">پاسخنامه — ویژهٔ دبیر</div>' if is_ans
             else '<div class="vbadge stu-badge">برگهٔ دانش‌آموز</div>')
    avatar_mode = "_ans" if is_ans else ""

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
  background:linear-gradient(160deg,#ffeef8 0%,#f3e8ff 55%,#e8f6fd 100%);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}}
.page {{ width:210mm; height:297mm; padding:5.5mm 6.5mm; }}
.sheet {{
  width:100%; height:100%; background:#fffdfa;
  border:1.2mm solid #f5b8d0; border-radius:6mm; padding:4mm 5.5mm 13.5mm;
  box-shadow:0 0 0 0.8mm #ffe1ee inset; position:relative; overflow:hidden;
}}

/* ---------- هدر ---------- */
.hdr {{ display:flex; align-items:center; gap:2.5mm; }}
.banner {{
  flex:1; text-align:center; color:#fff;
  background:linear-gradient(90deg,#ef6fae,#a86bd8);
  border-radius:5mm; padding:1.4mm 4mm 1.8mm; box-shadow:0 1mm 0 #e8b7d6;
}}
.banner .t {{ font-family:'Lalezar'; font-size:16pt; line-height:1.3; }}
.teacher {{
  flex:0 0 46mm; display:flex; align-items:center; gap:1.8mm;
  background:linear-gradient(135deg,#fde7f3,#f3e8ff); border:0.5mm solid #f2c4dd;
  border-radius:3.5mm; padding:1.2mm 2mm;
}}
.teacher img {{ width:11.5mm; height:11.5mm; }}
.teacher .l1 {{ font-size:7.8pt; font-weight:600; color:#a06ab8; line-height:1.5; }}
.teacher .l2 {{ font-size:10.5pt; font-weight:800; color:#7c3f96; line-height:1.5; white-space:nowrap; }}
.vbadge {{
  flex:0 0 21mm; text-align:center; font-size:8.4pt; font-weight:800; color:#fff;
  border-radius:3.5mm; padding:2.2mm 1mm; line-height:1.7;
}}
.ans-badge {{ background:linear-gradient(135deg,#34b487,#1f8a63); box-shadow:0 0.8mm 0 #b7e3cf; }}
.stu-badge {{ background:linear-gradient(135deg,#7ec9ee,#4d9fd6); box-shadow:0 0.8mm 0 #c4e6f6; }}
.subject {{ text-align:center; margin-top:1.2mm; }}
.subject .s1 {{ font-family:'Lalezar'; font-size:12.5pt; color:#d4547e; line-height:1.3; }}
.subject .s2 {{ font-size:8.2pt; font-weight:600; color:#a98cb8; margin-top:0.4mm; }}

/* ---------- ردیف مشخصات ---------- */
.idrow {{ display:flex; gap:2.5mm; margin-top:1.6mm; }}
.idbox {{
  flex:1; display:flex; align-items:baseline; gap:1.5mm;
  background:#fdf4fa; border:0.5mm dashed #e9b9d6; border-radius:3mm;
  padding:1mm 3mm 1.3mm; font-size:9pt; font-weight:700; color:#8a5a9e;
}}
.idbox .fill2 {{ flex:1; border-bottom:0.5mm dotted #cfa9df; min-height:4.5mm; }}

/* ---------- بخش‌ها ---------- */
.sec {{ margin-top:1.6mm; }}
.sec-head {{ display:flex; align-items:center; gap:2.5mm; margin-bottom:1.1mm; }}
.sec-head .line {{ flex:1; border-top:0.5mm dotted #e5a9c9; }}
.pill {{
  display:flex; align-items:center; gap:2mm; color:#fff; white-space:nowrap;
  background:linear-gradient(90deg,#ef6fae,#a86bd8); border-radius:99px;
  padding:0.7mm 4mm 1mm; font-size:10pt; font-weight:800;
  box-shadow:0 0.6mm 0 #e8b7d6;
}}
.pill .n {{
  width:5.6mm; height:5.6mm; display:flex; align-items:center; justify-content:center;
  background:#ffffff; color:#c2447c; border-radius:50%; font-size:8.8pt; font-weight:800;
}}
.pill svg {{ width:4.4mm; height:4.4mm; }}
.card {{
  background:linear-gradient(180deg,#fff6fb,#fdeff7); border:0.55mm solid #f6c6dd;
  border-radius:4mm; padding:1.3mm 3.2mm 1.5mm;
}}
.card.mint {{ background:linear-gradient(180deg,#f4fbf8,#ebf7f1); border-color:#bfe6d2; }}

/* هدف و فرضیه: متن در یک خط با عنوان */
.inline-card {{ display:flex; align-items:center; gap:3mm; }}
.inline-card .txt {{ flex:1; font-size:9.4pt; font-weight:600; line-height:1.65; color:#54455c; }}
.hint {{ font-size:8.6pt; font-weight:600; color:#a05a92; line-height:1.65; margin-bottom:0.6mm; }}
.fill {{ font-size:9.6pt; font-weight:600; line-height:1.8; color:#54455c; }}
.fill.ans {{ color:#0f7a55; font-weight:700; }}
.dline {{ border-bottom:0.55mm dotted #bb8fd4; height:3.6mm; }}

/* مواد و وسایل */
.grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:2.4mm; }}
.mat-card {{
  background:#fff; border:0.55mm solid #f6c6dd; border-radius:3.5mm;
  padding:1mm 1mm 1.2mm; text-align:center;
}}
.mat-imgwrap {{ height:11mm; display:flex; align-items:center; justify-content:center; }}
.mat-imgwrap img {{ max-width:11mm; max-height:11.5mm; }}
.mat-name {{ font-size:9.2pt; font-weight:800; color:#b23e78; margin-top:0.5mm; }}
.mat-amount {{
  display:inline-block; margin-top:0.9mm; font-size:7.6pt; font-weight:700; color:#3d7fa8;
  background:#e3f4fd; border:0.4mm solid #bfe3f7; border-radius:99px; padding:0.1mm 2mm 0.4mm;
}}

/* روش کار */
.steps {{ list-style:none; display:grid; grid-template-columns:1fr 1fr; gap:0.5mm 4.5mm; }}
.steps li {{ display:flex; align-items:flex-start; gap:2mm; padding:0.25mm 0; }}
.stepnum {{
  flex:0 0 auto; width:5.8mm; height:5.8mm; margin-top:0.4mm;
  display:flex; align-items:center; justify-content:center;
  font-size:8.8pt; font-weight:800; color:#fff;
  background:linear-gradient(135deg,#f27bb2,#a86bd8); border-radius:50%;
  box-shadow:0 0.5mm 0 #e3aed2;
}}
.steptxt {{ font-size:9.2pt; font-weight:600; line-height:1.6; color:#54455c; }}

/* جدول مشاهدات */
table.obs {{ width:100%; border-collapse:collapse; background:#fff; border-radius:3mm; overflow:hidden; }}
table.obs th {{
  background:linear-gradient(90deg,#ef6fae,#a86bd8); color:#fff;
  font-size:9.6pt; font-weight:800; padding:1.6mm 2mm;
  border:0.4mm solid #f0c6de;
}}
table.obs td {{
  border:0.4mm solid #f0c6de; padding:0.9mm 2.4mm; font-size:9pt; font-weight:600;
  color:#54455c; height:7mm; vertical-align:middle;
}}
table.obs td.lbl {{ font-weight:800; color:#a8377c; background:#fdf0f8; width:34%; }}
table.obs td.ans {{ color:#0f7a55; font-weight:700; }}

/* فکر کنید */
.think-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:2.6mm; }}
.think-box {{
  background:#fdf6fc; border:0.55mm solid #ecc2e2; border-radius:4mm; padding:1.2mm 3mm 1.3mm;
}}
.tq {{ font-size:9.2pt; font-weight:800; color:#8e44ad; line-height:1.6; margin-bottom:0.2mm; }}
.ta.ans {{ font-size:9pt; font-weight:700; color:#0f7a55; line-height:1.75; }}

/* فشرده‌سازی مخصوص حالت پاسخنامه */
.sheet.ans .sec {{ margin-top:1.3mm; }}
.sheet.ans .sec-head {{ margin-bottom:0.9mm; }}
.sheet.ans .card {{ padding:1.1mm 3.2mm 1.3mm; }}
.sheet.ans .fill.ans {{ line-height:1.7; font-size:9.4pt; }}
.sheet.ans .ta.ans {{ line-height:1.6; font-size:8.8pt; }}
.sheet.ans table.obs td {{ height:8.4mm; padding:0.7mm 2.4mm; }}
.sheet.ans .think-box {{ padding:1mm 3mm 1.1mm; }}
.sheet.ans .steps li {{ padding:0.15mm 0; }}
.sheet.ans .mat-imgwrap {{ height:10.5mm; }}
.sheet.ans .mat-imgwrap img {{ max-height:11mm; }}
.sheet.ans .idrow {{ margin-top:1.2mm; }}
.sheet.ans .subject {{ margin-top:0.9mm; }}

/* پاصفحه */
.safety {{
  display:flex; align-items:center; gap:2.5mm;
  background:#fff8e8; border:0.55mm solid #f5d98d; border-radius:99px; padding:0.8mm 4mm;
}}
.safety .ic {{ width:5.4mm; height:5.4mm; flex:0 0 auto; }}
.safety .tx {{ font-size:8.2pt; font-weight:700; color:#9a6b12; line-height:1.45; }}
.footer {{
  position:absolute; bottom:3mm; right:5.5mm; left:5.5mm;
  display:flex; align-items:center; gap:3mm;
  background:#fff; border:0.5mm solid #f3d0e4; border-radius:99px; padding:0.8mm 4mm;
}}
.footer .strip {{ display:flex; align-items:center; gap:1.3mm; flex:1; justify-content:center; }}
.footer .strip img {{ height:8.2mm; width:auto; }}
.footer .ftext {{ font-size:7.6pt; font-weight:700; color:#b06aa0; white-space:nowrap; }}
</style></head>
<body><div class="page"><div class="{sheet_cls}">

  <div class="hdr">
    <div class="teacher">
      <img src="{b64('assets/teacher-avatar.png')}" alt="">
      <div><div class="l1">دبیر آزمایشگاه:</div><div class="l2">{TEACHER_NAME}</div></div>
    </div>
    <div class="banner"><div class="t">{HEADER_TITLE}</div></div>
    {badge}
  </div>

  <div class="subject">
    <div class="s1">موضوع آزمایش: {data['subject']}</div>
    <div class="s2">{data['source']}</div>
  </div>

  <div class="idrow">
    <div class="idbox">نام و نام خانوادگی: <span class="fill2"></span></div>
    <div class="idbox" style="flex:0 0 34mm;">شماره کلاس: <span class="fill2"></span></div>
    <div class="idbox" style="flex:0 0 46mm;">تاریخ: ....... / ....... / .......</div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(1)}</span>{icon('target')} هدف آزمایش</span><span class="line"></span></div>
    <div class="card inline-card"><div class="txt">{data['objective']}</div></div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(2)}</span>{icon('bulb')} فرضیه</span><span class="line"></span></div>
    <div class="card">{hyp}</div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(3)}</span>{icon('flask')} مواد و وسایل</span><span class="line"></span></div>
    <div class="grid">{mat_cards}</div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(4)}</span>{icon('list')} روش کار</span><span class="line"></span></div>
    <div class="card mint"><ol class="steps">{steps}</ol></div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(5)}</span>{icon('table')} جدول ثبت مشاهدات</span><span class="line"></span></div>
    <table class="obs"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(6)}</span>{icon('check','#1f8a63')} نتیجه‌گیری</span><span class="line"></span></div>
    <div class="card">{concl}</div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="pill"><span class="n">{fa(7)}</span>{icon('think')} فکر کنید و پاسخ دهید</span><span class="line"></span></div>
    <div class="think-grid">{think_boxes}</div>
  </div>

  <div style="height:1.4mm"></div>
  <div class="safety">
    <svg class="ic" viewBox="0 0 24 24"><path fill="#f5b921" d="M12 2L1 21h22L12 2z"/><rect x="11" y="9" width="2" height="6" rx="1" fill="#7a5a00"/><circle cx="12" cy="17.6" r="1.2" fill="#7a5a00"/></svg>
    <div class="tx">نکتهٔ ایمنی: {data['safety']}</div>
  </div>

  <div class="footer">
    <div class="ftext">{HEADER_TITLE} | {TEACHER_NAME}</div>
    <div class="strip">{''.join(f'<img src="{b64(f"assets/icons/strip-{i}.png")}" alt="">' for i in range(7))}</div>
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
