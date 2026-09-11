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
        mode_en = "student" if mode == "student" else "answer"
        for src, ext in ((jpg, "jpg"), (pdf, "pdf"), (docx, "docx")):
            dst = os.path.join(out_dir, f"{stem}-{fa_mode}.{ext}")
            shutil.copy(src, dst)
            d2 = os.path.join(DL, f"lab-{slug}-{mode_en}.{ext}")
            shutil.copy(src, d2)
            print("  →", os.path.relpath(dst, REPO))

    # ۶) ZIP بستهٔ کامل با ساختار پوشه‌بندی فصل/آزمایش
    ztmp = os.path.join(BUILD, "zipsrc")
    zdir = os.path.join(ztmp, dir_name)
    if os.path.exists(ztmp):
        shutil.rmtree(ztmp)
    os.makedirs(zdir, exist_ok=True)
    for mode_en in ("student", "answer"):
        for ext in ("jpg", "pdf", "docx"):
            shutil.copy(os.path.join(DL, f"lab-{slug}-{mode_en}.{ext}"), zdir)
    fsrc = os.path.join(ROOT, "fonts")
    if os.path.isdir(fsrc):
        shutil.copytree(fsrc, os.path.join(zdir, "fonts"),
                        ignore=shutil.ignore_patterns("*.zip"))
    zpath = os.path.join(DL, f"lab-{slug}-complete.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    subprocess.run(["zip", "-qr", zpath, dir_name], cwd=ztmp, check=True)
    shutil.rmtree(ztmp)
    print("  →", os.path.relpath(zpath, REPO))
    print(f"✅ کاربرگ «{data['subject']}» در ۶ فایل + ZIP آماده شد.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fasl1-azmayesh1")
