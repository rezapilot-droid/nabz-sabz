# -*- coding: utf-8 -*-
"""
ساخت کامل کاربرگ «گزارش آزمایشگاه علوم هشتم» برای یک آزمایش:
  ورودی: experiments/<slug>.json
  خروجی: ۶ فایل (دانش‌آموزی + پاسخنامهٔ دبیر) × (JPG + PDF + DOCX)
         → worksheets/<dir_name>/ با نام فارسی + download/ با نام لاتین
اجرا:  python3 build/build_lab.py <slug>
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # workshop/
BUILD = os.path.join(ROOT, "build")
REPO = os.path.dirname(ROOT)
DL = os.path.join(REPO, "download")

def main(slug):
    with open(os.path.join(ROOT, "experiments", slug + ".json"), encoding="utf-8") as f:
        data = json.load(f)
    dir_name = data.get("dir_name", slug)
    stem = data.get("file_stem", slug)
    out_dir = os.path.join(REPO, "worksheets", dir_name)
    os.makedirs(out_dir, exist_ok=True)

    # ۱) HTML
    sys.path.insert(0, BUILD)
    import lab_report, lab_report_docx
    lab_report.build_both(data, os.path.join(BUILD, slug))

    # ۲) رندر PNG + PDF
    env = dict(os.environ)
    env.setdefault("LD_LIBRARY_PATH", "/tmp/al2023/lib")
    for mode, fa_mode in (("student", "دانش‌آموزی"), ("answer", "پاسخنامه-دبیر")):
        html = os.path.join(BUILD, f"{slug}-{mode}.html")
        png  = os.path.join(BUILD, f"{slug}-{mode}.png")
        pdf  = os.path.join(BUILD, f"{slug}-{mode}.pdf")
        subprocess.run(["node", os.path.join(BUILD, "render.js"), html, png, pdf],
                       check=True, env=env, cwd=ROOT)

        # ۳) JPG چاپی ۳۰۰dpi
        from PIL import Image
        im = Image.open(png).convert("RGB")
        im = im.resize((2480, 3508), Image.LANCZOS)
        jpg = os.path.join(BUILD, f"{slug}-{mode}.jpg")
        im.save(jpg, quality=92, dpi=(300, 300))

        # ۴) DOCX
        docx = os.path.join(BUILD, f"{slug}-{mode}.docx")
        lab_report_docx.build_docx(data, mode, docx)

        # ۵) خروجی‌های نهایی (فارسی) + نسخهٔ دانلود (لاتین)
        for src, ext in ((jpg, "jpg"), (pdf, "pdf"), (docx, "docx")):
            dst = os.path.join(out_dir, f"{stem}-{fa_mode}.{ext}")
            shutil.copy(src, dst)
            d2 = os.path.join(DL, f"lab-{slug}-{'student' if mode=='student' else 'answer'}.{ext}")
            shutil.copy(src, d2)
            print("  →", os.path.relpath(dst, REPO))

    print(f"✅ کاربرگ «{data['subject']}» در ۶ فایل آماده شد.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fasl1-azmayesh1")
