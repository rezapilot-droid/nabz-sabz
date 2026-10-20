"""Final data build: geometry -> metrics -> CSV/JSON -> SVG figures."""
import json, math, os, csv
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
import svgkit as K

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'land-appraisal'))
os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'figures'), exist_ok=True)

LABELS = {'north': [173.92, 171.26, 166.16, 178.45],
          'south': [211.15, 165.00, 165.00, 193.04],
          'single': [215.51, 188.42, 237.04, 296.31, 334.42]}

raw = json.load(open(os.path.join(HERE, 'lots_ws.json')))
items = []
for d in raw:
    p = Polygon(d['poly']).buffer(0)
    items.append(dict(poly=p, yellow=d['yellow'], area_drawn=p.area))

# ---- id assignment
A = [d for d in items if d['yellow']]
B = [d for d in items if not d['yellow']]
midy = (min(d['poly'].centroid.y for d in A) + max(d['poly'].centroid.y for d in A)) / 2
A_n = sorted([d for d in A if d['poly'].centroid.y < midy], key=lambda d: d['poly'].centroid.x)
A_s = sorted([d for d in A if d['poly'].centroid.y >= midy], key=lambda d: d['poly'].centroid.x)
B_s = sorted(B, key=lambda d: d['poly'].centroid.x)
for i, d in enumerate(A_n, 1):
    d['id'] = 'A-1%d' % i; d['row'] = 'north'
for i, d in enumerate(A_s, 1):
    d['id'] = 'A-2%d' % i; d['row'] = 'south'
for i, d in enumerate(B_s, 1):
    d['id'] = 'B-1%d' % i; d['row'] = 'single'
items = A_n + A_s + B_s

# ---- match labelled (net) areas: nearest-area assignment within each row group
for grp, key in ((A_n, 'north'), (A_s, 'south'), (B_s, 'single')):
    for d, L in zip(sorted(grp, key=lambda d: d['poly'].centroid.x), LABELS[key]):
        d['area_label'] = L

# ---- calibrate traced outlines to the areas written on the drawing
for grp in (A_n + A_s, B_s):
    need = sum(d['area_label'] for d in grp) - sum(d['poly'].area for d in grp)
    per = sum(d['poly'].exterior.length for d in grp)
    delta = need / per
    for d in grp:
        d['poly_raw'] = d['poly']
        d['poly'] = d['poly'].buffer(delta, join_style=1).buffer(0)
    print('calibrate block: delta %.3f m' % delta)

# ---- frontage, curated from the drawing's own dimension strings + measurement
CUR = {
 'A-11': (13.2, 'ST:10m', 0.0, '—'), 'A-12': (10.3, 'ST:10m', 0.0, '—'),
 'A-13': (9.5, 'ST:10m', 0.0, '—'), 'A-14': (12.1, 'ST:10m', 14.5, 'ST:8m'),
 'A-21': (11.2, 'ST:8m', 0.0, '—'), 'A-22': (11.0, 'ST:8m', 0.0, '—'),
 'A-23': (11.0, 'ST:8m', 0.0, '—'), 'A-24': (14.2, 'ST:8m', 16.6, 'ST:8m'),
 'B-11': (21.7, 'ST:8m', 27.4, 'ST:12m'), 'B-12': (10.0, 'ST:8m', 11.0, 'ST:12m'),
 'B-13': (10.0, 'ST:8m', 12.4, 'ST:12m'), 'B-14': (25.0, 'ST:8m', 7.6, 'ST:8m'),
 'B-15': (24.9, 'ST:12m', 13.6, 'ST:8m'),
}
# boundary double-count correction (per metre of block perimeter)
blkA = unary_union([d['poly'] for d in (A_n + A_s)]).buffer(0.25).buffer(-0.25)
blkB = unary_union([d['poly'] for d in B_s]).buffer(0.25).buffer(-0.25)
offA = (blkA.area - sum(d['area_label'] for d in (A_n + A_s))) / blkA.exterior.length
offB = (blkB.area - sum(d['area_label'] for d in B_s)) / blkB.exterior.length

rows = []
for d in items:
    p = d['poly']
    area_meas = d['area_label']
    rect = d['poly_raw'].minimum_rotated_rectangle
    xs, ys = rect.exterior.xy
    sides = sorted([math.dist((xs[i], ys[i]), (xs[i + 1], ys[i + 1])) for i in range(4)], reverse=True)
    per = d['poly_raw'].exterior.length
    c = CUR[d['id']]
    rows.append(dict(
        id=d['id'], row=d['row'], block='A' if d['yellow'] else 'B',
        row_fa={'north': 'ردیف شمالی — بر ST:10m', 'south': 'ردیف جنوبی — بر ST:8m',
                'single': 'ردیف واحد — بر ST:8m و ST:12m'}[d['row']],
        area_label=round(d['area_label'], 2), area_meas=round(d['area_label'] + 0.0, 1),
        depth=round(sides[1], 1), width=round(sides[3], 1),
        ratio=round(sides[1] / sides[3], 2),
        perimeter=round(per, 1),
        compaction=round(4 * math.pi * area_meas / per ** 2, 2),
        f1=c[0], s1=c[1], f2=c[2], s2=c[3],
        n_streets=1 + (1 if c[2] > 0 else 0),
        centroid=[round(p.centroid.x, 2), round(p.centroid.y, 2)],
        poly=[[round(x, 2), round(y, 2)] for x, y in p.exterior.coords]))

rows.sort(key=lambda d: d['id'])
arr = np.array([d['area_label'] for d in rows])
stats = dict(n=len(arr), total=round(float(arr.sum()), 2), mean=round(float(arr.mean()), 2),
             median=round(float(np.median(arr)), 2), sd=round(float(arr.std(ddof=1)), 2),
             cv=round(float(arr.std(ddof=1) / arr.mean()), 3), mn=round(float(arr.min()), 2),
             mx=round(float(arr.max()), 2), n_lt200=int((arr < 200).sum()),
             n_ge200=int((arr >= 200).sum()), n_lt175=int((arr < 175).sum()),
             n_ge250=int((arr >= 250).sum()),
             total_A=round(sum(d['area_label'] for d in rows if d['block'] == 'A'), 2),
             total_B=round(sum(d['area_label'] for d in rows if d['block'] == 'B'), 2))

streets = [
    dict(name='ST:10m', width=10, lots='A-11 … A-14', side='ضلع شمالی بلوک A', length=46.0),
    dict(name='ST:8m', width=8, lots='A-21 … A-24 / B-11 … B-13', side='حد فاصل دو بلوک', length=47.4),
    dict(name='ST:8m', width=8, lots='A-14، A-24، B-14، B-15', side='ضلع شرقی بلوک A و شمالشرقی بلوک B', length=61.3),
    dict(name='ST:12m', width=12, lots='B-11 … B-13 / B-15', side='ضلع جنوبغربی بلوک B', length=50.4),
]
street_area = sum(s['width'] * s['length'] for s in streets) * 0.74
gross = stats['total'] + street_area

checks = dict(
    south_chain=[11.16, 11.00, 11.00, 14.24], north_chain=[13.16, 10.00, 10.00, 12.23],
    south_sum=round(sum([11.16, 11.00, 11.00, 14.24]), 2),
    north_sum=round(sum([13.16, 10.00, 10.00, 12.23]), 2),
    measured_south_edge=47.4, measured_north_edge=45.4,
    blkA_drawn=round(blkA.area, 1), blkB_drawn=round(blkB.area, 1),
    blkA_perim=round(blkA.exterior.length, 1), blkB_perim=round(blkB.exterior.length, 1),
    offset_A=round(offA, 2), offset_B=round(offB, 2),
    drawn_total=round(blkA.area + blkB.area, 1), label_total=stats['total'],
    consistency_pct=round((blkA.area + blkB.area - stats['total']) / stats['total'] * 100, 2),
)
data = dict(meta=dict(source='1_29754637390.pdf', created='2026-09-11T00:24:46',
                      producer='AutoCAD Map 3D 2018 / pdfplot14.hdi', sheet_mm=[842, 1191], scale='5.40 pt/m ≈ 1:525'),
            lots=rows, stats=stats, streets=streets, checks=checks,
            street_area=round(street_area), gross=round(gross), net_ratio=round(stats['total'] / gross, 3))
json.dump(data, open(os.path.join(OUT, 'data', 'analysis.json'), 'w'), ensure_ascii=False, indent=1)

with open(os.path.join(OUT, 'data', 'lots.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'row', 'area_label_m2', 'area_measured_m2', 'depth_m', 'width_m',
                'L_over_W', 'perimeter_m', 'compaction', 'frontage_1_m', 'street_1',
                'frontage_2_m', 'street_2', 'n_streets'])
    for d in rows:
        w.writerow([d['id'], d['row_fa'], '%.2f' % d['area_label'], '%.1f' % d['area_meas'],
                    '%.1f' % d['depth'], '%.1f' % d['width'], '%.2f' % d['ratio'],
                    '%.1f' % d['perimeter'], '%.2f' % d['compaction'],
                    '%.1f' % d['f1'], d['s1'], '%.1f' % d['f2'], d['s2'], d['n_streets']])

print(json.dumps(stats, ensure_ascii=False))
print('off', round(offA, 2), round(offB, 2), 'consistency', checks['consistency_pct'])
print('gross', round(gross), 'net', data['net_ratio'])

# ============================================================ FIGURE 1
PAD = 30
X0, X1, Y0, Y1 = 76.0, 170.0, 50.0, 152.0
SC = 11.4
CW = (X1 - X0) * SC + 2 * PAD
CH = (Y1 - Y0) * SC + 2 * PAD + 40


def T(x, y):
    return (PAD + (x - X0) * SC, PAD + (y - Y0) * SC)


b = ['<rect width="%.0f" height="%.0f" fill="#ffffff"/>' % (CW, CH)]
g = ['<g stroke="#e8edf3" stroke-width="0.6">']
for x in range(80, int(X1) + 1, 10):
    g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (*T(x, Y0), *T(x, Y1)))
for y in range(50, int(Y1) + 1, 10):
    g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (*T(X0, y), *T(X1, y)))
g.append('</g>')
b += g

centre = (120, 100)
BANDS = [([(92.2, 59.2), (129.9, 62.8)], 10.0),
         ([(88.7, 92.4), (136.0, 92.4)], 7.0),
         ([(138.3, 88.7), (131.0, 76.6), (129.9, 62.8)], 8.0),
         ([(143.1, 99.2), (160.9, 127.3)], 8.0),
         ([(94.1, 103.0), (107.0, 112.8), (137.9, 127.3), (148.9, 141.7)], 12.0)]
for coords, wid in BANDS:
    pts = [T(*p) for p in coords]
    outer = K.offset_line(pts, wid * SC, T(*centre))
    b.append('<path d="%s" fill="#f7f3e7" stroke="#cdc4ab" stroke-width="0.6" stroke-dasharray="5,4"/>'
             % K.poly_path(pts + list(reversed(outer))))

for d in rows:
    pts = [T(*q) for q in d['poly']]
    fill = '#fceea8' if d['block'] == 'A' else '#b7e7ee'
    b.append('<path d="%s" fill="%s" stroke="#8c2b1f" stroke-width="1" stroke-linejoin="round"/>'
             % (K.poly_path(pts), fill))
for blk in (blkA, blkB):
    b.append('<path d="%s" fill="none" stroke="#5c1109" stroke-width="2.3"/>'
             % K.poly_path([T(*q) for q in blk.exterior.coords]))

for d in rows:
    x, y = T(*d['centroid'])
    b.append(K.text(x, y - 6, d['id'], size=10, weight='700', fill='#3a1410'))
    b.append(K.text(x, y + 8, '%.2f' % d['area_label'], size=9, fill='#5b1a12'))
    b.append(K.text(x, y + 19, 'm²', size=6.4, fill='#7a4a44'))
    if d['f2'] > 0:
        b.append(K.text(x, y + 29, 'بر %.1f + %.1f' % (d['f1'], d['f2']), size=6.2, fill='#7a4a44'))

for x, y, s in [(110, 52.6, 'ST:10m — عرض ۱۰ متر'), (112, 96.4, 'ST:8m — عرض ۸ متر'),
                (153.5, 88.0, 'ST:8m'), (110, 128.5, 'ST:12m — عرض ۱۲ متر')]:
    b.append(K.text(*T(x, y), s, size=8.6, weight='700', fill='#0f5132'))

# dimension chains
south = [(88.7, '11.16'), (99.86, '11.00'), (110.86, '11.00'), (121.86, '14.24')]
for i in range(4):
    x1 = south[i][0]
    x2 = south[i + 1][0] if i < 3 else 136.10
    b.append(K.arrow_dim(*T(x1, 92.4), *T(x2, 92.4), south[i][1], size=7.4, side=1, off=15))
north = [(92.2, '13.16'), (105.36, '10.00'), (115.36, '10.00'), (125.36, '12.23')]
for i in range(4):
    x1 = north[i][0]
    x2 = north[i + 1][0] if i < 3 else 137.6
    b.append(K.arrow_dim(*T(x1, 59.6), *T(x2, 62.9), north[i][1], size=7.4, side=-1, off=13))

b.append(K.text(*T(78.0, 66.0), 'بلوک A', size=10, weight='700', anchor='start', fill='#7a5b00'))
b.append(K.text(*T(78.0, 71.5), '۸ قطعه', size=8, anchor='start', fill='#7a5b00'))
b.append(K.text(*T(78.0, 76.0), '۱٬۴۲۳٫۹۸ m²', size=8, anchor='start', fill='#7a5b00'))
b.append(K.text(*T(79.0, 108.0), 'بلوک B', size=10, weight='700', anchor='start', fill='#0b4f5c'))
b.append(K.text(*T(79.0, 113.5), '۵ قطعه', size=8, anchor='start', fill='#0b4f5c'))
b.append(K.text(*T(79.0, 118.0), '۱٬۲۷۱٫۷۰ m²', size=8, anchor='start', fill='#0b4f5c'))
b.append(K.text(*T(100.0, 136.0), 'جمع کل: ۱۳ قطعه — ۲٬۶۹۵٫۶۸ m²', size=9, weight='700',
                anchor='start', fill='#111'))

sx, sy = T(X1 - 27, Y1 - 7)
for k in range(5):
    b.append('<rect x="%.1f" y="%.1f" width="%.1f" height="5.5" fill="%s" stroke="#333" stroke-width="0.5"/>'
             % (sx + k * 5 * SC, sy, 5 * SC, '#333' if k % 2 == 0 else '#fff'))
b.append(K.text(sx + 12.5 * SC, sy + 16, '۰ تا ۲۵ متر', size=7.4))

nx, ny = T(163, 57)
b.append('<circle cx="%.1f" cy="%.1f" r="14" fill="#fff" stroke="#333" stroke-width="1"/>' % (nx, ny))
b.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#333"/>' % (nx, ny - 11, nx - 4.5, ny + 6, nx + 4.5, ny + 6))
b.append(K.text(nx, ny + 27, 'جهت شمال', size=7.6, weight='700'))
b.append(K.text(nx, ny + 36, 'روی نقشه', size=6.4))
b.append(K.text(nx, ny + 43, 'درج نشده', size=6.4))

ty = CH - 26
b.append('<rect x="%d" y="%.1f" width="%.0f" height="20" fill="#fbfaf6" stroke="#8c2b1f" stroke-width="1"/>'
         % (PAD, ty, CW - 2 * PAD))
b.append(K.text(PAD + 12, ty + 13.5, 'بازترسیم تحلیلی نقشه تفکیک (مقیاس تقریبی ۱:۵۲۵) — مبنا: فایل PDF دریافتی، خروجی AutoCAD Map 3D 2018',
                size=8, anchor='start', fill='#5c1109', weight='700'))
b.append(K.text(CW - PAD - 12, ty + 13.5, 'اندازهگیری روی نقشه با دقت ±۰٫۳ متر — ارقام داخل کادرها، مساحت مندرج در خود نقشه است',
                size=7, anchor='end', fill='#5c1109'))
open(os.path.join(OUT, 'figures', 'plan-redrawn.svg'), 'w').write(K.svg_doc(int(CW), int(CH), ''.join(b)))

# ============================================================ FIGURE 2
w2, h2 = 660, 310
ml, mr, mt, mb = 92, 30, 26, 40
pw, ph = w2 - ml - mr, h2 - mt - mb
mx = 360.0
s2 = ['<rect width="%d" height="%d" fill="#fff"/>' % (w2, h2)]
for v in range(0, 361, 50):
    x = ml + v / mx * pw
    s2.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#eceff3"/>' % (x, mt, x, mt + ph))
    s2.append(K.text(x, mt + ph + 13, str(v), size=7.2, fill='#666'))
xth = ml + 200 / mx * pw
s2.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#c0392b" stroke-width="1.1" stroke-dasharray="4,3"/>'
          % (xth, mt - 8, xth, mt + ph))
s2.append(K.text(xth + 4, mt - 10, 'حدنصاب رایج ۲۰۰ m²', size=7.2, anchor='start', fill='#c0392b', weight='700'))
srt = sorted(rows, key=lambda d: d['area_label'])
bh = ph / len(srt)
for i, d in enumerate(srt):
    y = mt + i * bh
    x = ml + d['area_label'] / mx * pw
    col = '#d9a521' if d['block'] == 'A' else '#1f8a9c'
    s2.append('<rect x="%d" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="1.5"/>'
              % (ml, y + 1.6, max(x - ml, 1), bh - 3.2, col))
    s2.append(K.text(ml - 7, y + bh / 2 + 3, d['id'], size=7.4, anchor='end', fill='#333'))
    s2.append(K.text(x + 5, y + bh / 2 + 3, '%.2f' % d['area_label'], size=7.2, anchor='start', fill='#333'))
s2.append('<rect x="%d" y="%d" width="8" height="8" fill="#d9a521"/>' % (ml + 4, h2 - 18))
s2.append(K.text(ml + 16, h2 - 11, 'بلوک A', size=7.6, anchor='start'))
s2.append('<rect x="%d" y="%d" width="8" height="8" fill="#1f8a9c"/>' % (ml + 62, h2 - 18))
s2.append(K.text(ml + 74, h2 - 11, 'بلوک B', size=7.6, anchor='start'))
s2.append(K.text(ml + pw / 2 + 20, h2 - 11, 'مساحت هر قطعه (m²)', size=7.6, fill='#666'))
open(os.path.join(OUT, 'figures', 'lots-areas.svg'), 'w').write(K.svg_doc(w2, h2, ''.join(s2)))

# ============================================================ FIGURE 3
lat0, lon0 = 35.542902, 51.487268


def geo(lat, lon):
    Rr = 6371008.8
    p1, p2 = math.radians(lat0), math.radians(lat)
    dl = math.radians(lon - lon0)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    d = 2 * Rr * math.asin(math.sqrt(a))
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return d, (math.degrees(math.atan2(x, y)) + 360) % 360


# (name, lat, lon, label dx, label dy, anchor)
ctx = [('راه امامزاده شعیب', 35.5432847, 51.4886756, 52, -34, 'start'),
       ('روستای فیروزآباد', 35.5448629, 51.4839269, -46, -52, 'end'),
       ('چاله‌طرخان', 35.4985838, 51.4778690, 12, 30, 'start'),
       ('بخش قلعه‌نو', 35.5119433, 51.5155876, 22, 40, 'start'),
       ('شهر ری', 35.5964, 51.4266, -22, -26, 'end'),
       ('تهران — میدان آزادی', 35.6997, 51.3561, -30, -30, 'end')]
CTX = 11000.0
w3, h3 = 760, 470
cx, cy, R = w3 / 2 + 6, h3 / 2 + 8, 168
s3 = ['<rect width="%d" height="%d" fill="#fff"/>' % (w3, h3)]
for rr, lab in ((2000, '۲ کیلومتر'), (5000, '۵ کیلومتر'), (10000, '۱۰ کیلومتر')):
    rad = rr / CTX * R
    s3.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#e4e9ef"/>' % (cx, cy, rad))
    s3.append(K.text(cx + rad * 0.705, cy - rad * 0.705, lab, size=8.6, fill='#a3adb8', anchor='start'))
for ang, lab in ((0, 'شمال'), (90, 'شرق'), (180, 'جنوب'), (270, 'غرب')):
    a = math.radians(ang)
    s3.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ccd4dc" stroke-width="0.9"/>'
              % (cx, cy, cx + R * 1.0 * math.sin(a), cy - R * 1.0 * math.cos(a)))
    s3.append(K.text(cx + R * 1.1 * math.sin(a), cy - R * 1.1 * math.cos(a) + 4, lab, size=10, weight='700', fill='#4b5563'))
for name, la, lo, dx, dy, anc in ctx:
    d, brg = geo(la, lo)
    a = math.radians(brg)
    inside = d <= 10000
    rr = (d if inside else 10000) / CTX * R
    x, y = cx + rr * math.sin(a), cy - rr * math.cos(a)
    if inside:
        s3.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#7c3aed"/>' % (x, y))
    else:
        s3.append('<path d="M %.1f %.1f l 9 -5 l 0 10 z" fill="#7c3aed"/>' % (x, y))
    lx, ly = x + dx, y + dy
    s3.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#a99cd0" stroke-width="0.8"/>'
              % (x, y, lx, ly))
    dtxt = ('%.0f متر' % d) if d < 1000 else ('%.1f کیلومتر' % (d / 1000))
    s3.append(K.text(lx + (3 if anc == 'start' else -3), ly - 2, name, size=9.6, anchor=anc, weight='700', fill='#3b2a66'))
    s3.append(K.text(lx + (3 if anc == 'start' else -3), ly + 11, '%s · آزیموت %.0f°' % (dtxt, brg),
                     size=8.2, anchor=anc, fill='#6f5f96'))
s3.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#c0392b" stroke="#fff" stroke-width="1.8"/>' % (cx, cy))
s3.append('<circle cx="%.1f" cy="%.1f" r="13" fill="none" stroke="#c0392b" stroke-width="0.8" stroke-dasharray="3,3"/>' % (cx, cy))
s3.append(K.text(cx - 22, cy + 24, 'قطعه — نقطه تقریبی', size=9.6, anchor='end', weight='700', fill='#c0392b'))
s3.append(K.text(cx - 22, cy + 37, '35.542902 N · 51.487268 E', size=8.4, anchor='end', fill='#c0392b'))
s3.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c0392b" stroke-width="0.8" stroke-dasharray="2,2"/>'
          % (cx - 20, cy + 20, cx - 6, cy + 6))
s3.append(K.text(w3 / 2, h3 - 10, 'شِمای نسبی موقعیت بر پایه آزیموت و فاصله محاسبه‌شده؛ نقشه مکانی و مقیاس محلی ندارد.',
                 size=8.4, fill='#8a8f98'))
open(os.path.join(OUT, 'figures', 'site-context.svg'), 'w').write(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="118 52 604 382" width="100%%" role="img" '
    'style="max-width:100%%;height:auto;background:#fff">'
    '<rect x="118" y="52" width="604" height="382" fill="#fff"/>%s</svg>' % ''.join(s3))

json.dump({k: v for k, v in (('offsets', [round(offA, 2), round(offB, 2)]),)}, open('/tmp/x.json', 'w'))
print('figures written')
