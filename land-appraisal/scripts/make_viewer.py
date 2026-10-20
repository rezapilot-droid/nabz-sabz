"""Build viewer.html from scripts/viewer_template.html.

Inlines the massing model (so the file opens offline) and two Vazirmatn woff2
faces (so Persian labels render identically everywhere).
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
FONTS = ('/home/user/tools/fonts/node_modules/vazirmatn/fonts/webfonts/', '')

def font(name):
    for base, _ in (FONTS,):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return base64.b64encode(open(p, 'rb').read()).decode()
    raise SystemExit('font not found: %s' % name)

tpl = open(os.path.join(HERE, 'viewer_template.html'), encoding='utf-8').read()
model = json.load(open(os.path.join(ROOT, 'model', 'massing.json'), encoding='utf-8'))
tpl = tpl.replace('__MODEL_JSON__', json.dumps(model, ensure_ascii=False, separators=(',', ':')))
tpl = tpl.replace('__FONT_REGULAR__', font('Vazirmatn-Regular.woff2'))
tpl = tpl.replace('__FONT_BOLD__', font('Vazirmatn-Bold.woff2'))
out = os.path.join(ROOT, 'viewer.html')
open(out, 'w', encoding='utf-8').write(tpl)
print('wrote %s  %.1f KB' % (out, len(tpl.encode()) / 1024))
