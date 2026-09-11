# -*- coding: utf-8 -*-
"""سرور دانلود + آپلود عکس آموزگار — با ذخیرهٔ خودکار روی گیت‌هاب"""
import os, re, subprocess, sys, html
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))          # nabz-sabz/download
REPO = os.path.dirname(BASE)                               # nabz-sabz/
RECEIVE_DIR = os.path.join(REPO, "uploads-received")
os.makedirs(RECEIVE_DIR, exist_ok=True)
BRANCH = "arena/01a0904f-nabz-sabz"

UPLOAD_FORM = """<!doctype html><html dir="rtl" lang="fa"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>آپلود عکس آموزگار</title><style>
@font-face{font-family:'Vazirmatn';src:url('/fonts/Vazirmatn-Regular.ttf') format('truetype');font-weight:400}
@font-face{font-family:'Vazirmatn';src:url('/fonts/Vazirmatn-Bold.ttf') format('truetype');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;font-family:'Vazirmatn',sans-serif;color:#5b4a5e;display:flex;align-items:center;justify-content:center;padding:20px;
 background:linear-gradient(160deg,#ffeef8 0%,#f3e8ff 55%,#e8f6fd 100%)}
.card{width:100%;max-width:520px;background:#fffdfa;border:3px solid #f5b8d0;border-radius:24px;padding:30px 26px;text-align:center;
 box-shadow:0 10px 40px rgba(216,132,181,.25)}
h1{font-size:19px;color:#c2447c;margin-bottom:8px}
p{font-size:13px;font-weight:600;color:#8a7596;line-height:2;margin-bottom:18px}
input[type=file]{width:100%;border:2px dashed #e9a9d6;background:#fdf4fa;border-radius:14px;padding:18px;font-family:inherit;font-size:13px;
 font-weight:700;color:#b23e78;margin-bottom:14px}
button{width:100%;border:0;font-family:inherit;font-size:15px;font-weight:700;color:#fff;cursor:pointer;
 background:linear-gradient(90deg,#ef6fae,#a86bd8);border-radius:99px;padding:12px;box-shadow:0 3px 0 #e8b7d6}
.msg{margin-top:14px;font-size:12.5px;font-weight:700;color:#1f8a63;line-height:2}
</style></head><body><div class="card">
<h1>📤 آپلود فایل برای پروژهٔ کاربرگ</h1>
<p>این صفحه برای رساندن فایل‌ها به سفارش‌دهندهٔ کاربرگ است:<br>
📸 عکس دبیر آزمایشگاه &nbsp;|&nbsp; 📕 فایل PDF کتاب علوم هشتم<br>
فایل به‌صورت خودکار در مخزن گیت‌هاب ذخیره می‌شود.</p>
<form method="POST" action="/upload" enctype="multipart/form-data">
<input type="file" name="file" accept="image/*" required>
<button type="submit">آپلود کن 🌸</button>
</form>
<div class="msg">{MSG}</div>
</div></body></html>"""

def parse_multipart(body, content_type):
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not m: return []
    boundary = (m.group(1) or m.group(2)).encode()
    parts = body.split(b'--' + boundary)
    files = []
    for part in parts[1:-1]:
        seg = part.lstrip(b'\r\n')
        head, _, data = seg.partition(b'\r\n\r\n')
        data = data.rsplit(b'\r\n', 1)[0]
        mh = re.search(rb'filename="([^"]*)"', head)
        if mh and data:
            files.append((mh.group(1).decode('utf-8', 'replace'), data))
    return files

def git_backup(path_rel):
    log = []
    try:
        for cmd in [
            ["git", "-C", REPO, "add", path_rel],
            ["git", "-C", REPO, "commit", "-m",
             "دریافت عکس آموزگار از صفحهٔ آپلود — " + datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["git", "-C", REPO, "push", "origin", BRANCH],
        ]:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            log.append((r.stdout + r.stderr).strip()[-200:])
            if r.returncode != 0:
                break
    except Exception as e:
        log.append(str(e))
    return log

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASE, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % args))

    def do_GET(self):
        if self.path in ("/upload", "/upload/"):
            body = UPLOAD_FORM.replace("{MSG}", "")
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def do_POST(self):
        if self.path not in ("/upload", "/upload/"):
            self.send_error(404); return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            files = parse_multipart(body, self.headers.get("Content-Type", ""))
            if not files:
                raise ValueError("فایلی دریافت نشد")
            fname, data = files[0]
            ext = os.path.splitext(fname)[1].lower()
            known = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic", ".pdf")
            if ext not in known:
                ext = ext or ".jpg"
            # حفظ نام اصلی فایل (پاک‌سازی شده) تا کتاب و عکس با هم تداخل نکنند
            stem = re.sub(r'[^\w\.\-]', '-', os.path.splitext(fname)[0])[:40] or "file"
            safe = stem + ext
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic") and stem.startswith("test"):
                safe = "test-" + stem + ext
            dest = os.path.join(RECEIVE_DIR, safe)
            with open(dest, "wb") as f:
                f.write(data)
            size_kb = len(data) // 1024
            if not fname.startswith("test_"):
                git_backup("uploads-received/" + safe)
                msg = "✅ عکس با موفقیت دریافت شد (%d کیلوبایت) و در گیت‌هاب ذخیره شد.<br>حالا در چت بنویسید: «گذاشتم»" % size_kb
            else:
                msg = "(حالت تست — فایل ذخیره شد اما کامیت نشد)"
            out = UPLOAD_FORM.replace("{MSG}", msg).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)
        except Exception as e:
            out = UPLOAD_FORM.replace("{MSG}", "❌ خطا: " + html.escape(str(e))).encode()
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

if __name__ == "__main__":
    srv = HTTPServer(("0.0.0.0", 8080), Handler)
    print("server up on 8080 (download + upload)")
    srv.serve_forever()
