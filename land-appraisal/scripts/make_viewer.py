"""Build viewer.html from scripts/viewer_template.html.

Inlines: the massing model, two Vazirmatn woff2 faces, and a QR code that points
at the running preview URL (so the page can be opened on a phone).

Usage:
  python3 scripts/make_viewer.py [url]
If no url is given it is derived from E2B_SANDBOX_ID + PORT (default 8099).
"""
import base64, json, os
import segno

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
FONT_DIR = os.path.join(HERE, '..', 'assets')

PORT = os.environ.get('VIEWER_PORT', '8099')
SANDBOX = os.environ.get('E2B_SANDBOX_ID', '')
DEFAULT_URL = ('https://%s-%s.e2b.app/viewer.html' % (PORT, SANDBOX)) if SANDBOX else 'viewer.html'


def font(name):
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        raise SystemExit('font not found: %s' % name)
    return base64.b64encode(open(p, 'rb').read()).decode()


def qr_svg(url):
    q = segno.make(url, error='m', micro=False)
    svg = q.svg_inline(scale=1, border=2, dark='#0f4c5c', light='#ffffff')
    return svg


url = (os.sys.argv[1] if len(os.sys.argv) > 1 else DEFAULT_URL)

tpl = open(os.path.join(HERE, 'viewer_template.html'), encoding='utf-8').read()
model = json.load(open(os.path.join(ROOT, 'model', 'massing.json'), encoding='utf-8'))

tpl = tpl.replace('__MODEL_JSON__', json.dumps(model, ensure_ascii=False, separators=(',', ':')))
tpl = tpl.replace('__QR_SVG__', qr_svg(url))
tpl = tpl.replace('__VIEWER_URL__', url)
tpl = tpl.replace('__FONT_REGULAR__', font('Vazirmatn-Regular.woff2'))
tpl = tpl.replace('__FONT_BOLD__', font('Vazirmatn-Bold.woff2'))

out = os.path.join(ROOT, 'viewer.html')
open(out, 'w', encoding='utf-8').write(tpl)
print('wrote %s  %.1f KB  (qr → %s)' % (out, len(tpl.encode()) / 1024, url))
