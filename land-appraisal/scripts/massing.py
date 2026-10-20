"""Massing / 3-D feasibility model of the 13-lot site.

Outputs:
  ../model/massing.json      building volumes (metres)
  ../model/site.obj          OBJ mesh (open in any 3-D viewer)
  ../figures/massing-iso.svg aerial axonometric
  ../figures/massing-street.svg  low-angle view
  ../viewer.html             interactive orbit viewer (no dependencies)
"""
import json, math, os
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
D = json.load(open(os.path.join(ROOT, 'data', 'analysis.json')))
os.makedirs(os.path.join(ROOT, 'model'), exist_ok=True)

# ------------------------------------------------------------------ parameters
SETBACK = 1.5
FLOORS = {
    'A': [('res', 3.20), ('res', 3.00), ('res', 3.00)],                    # 3 floors, 9.2 m
    'B': [('com', 4.50), ('off', 3.60), ('res', 3.00), ('res', 3.00)],     # 4 floors, 14.1 m
}
COL = {'res': '#d9b779', 'com': '#7fa8bd', 'off': '#a8bfd0'}
FA = str.maketrans('0123456789.,', '۰۱۲۳۴۵۶۷۸۹٫٬')


def fa(s):
    return str(s).translate(FA)
BAND = {'res': '#8a6b34', 'com': '#3f6d84', 'off': '#6d8798'}

lots = D['lots']
buildings = []
for l in lots:
    p = Polygon(l['poly'])
    fp = p.buffer(-SETBACK, join_style=1)
    if fp.is_empty or fp.area < 0.55 * p.area:
        fp = p.buffer(-1.0, join_style=1)
    if fp.is_empty:
        fp = p.buffer(-0.6, join_style=1)
    if isinstance(fp, MultiPolygon):
        fp = max(fp.geoms, key=lambda g: g.area)
    fp = fp.simplify(0.35)
    z = 0.0
    seq = []
    for use, h in FLOORS[l['block']]:
        seq.append(dict(use=use, z0=round(z, 2), z1=round(z + h, 2), h=h))
        z += h
    buildings.append(dict(id=l['id'], block=l['block'], poly=[[round(x, 2), round(y, 2)] for x, y in fp.exterior.coords],
                          lot_area=l['area_label'], footprint=round(fp.area, 1),
                          coverage=round(fp.area / l['area_label'], 3),
                          height=round(z, 2), floors=seq,
                          gfa=round(fp.area * len(seq), 1),
                          gfa_res=round(fp.area * sum(1 for s in seq if s['use'] in ('res',)), 1),
                          gfa_com=round(fp.area * sum(1 for s in seq if s['use'] == 'com'), 1),
                          gfa_off=round(fp.area * sum(1 for s in seq if s['use'] == 'off'), 1)))

A = [b for b in buildings if b['block'] == 'A']
B = [b for b in buildings if b['block'] == 'B']
vals = dict(
    n=len(buildings),
    lot_area=round(sum(b['lot_area'] for b in buildings), 2),
    footprint=round(sum(b['footprint'] for b in buildings), 1),
    coverage=round(sum(b['footprint'] for b in buildings) / sum(b['lot_area'] for b in buildings), 3),
    gfa=round(sum(b['gfa'] for b in buildings), 1),
    gfa_res=round(sum(b['gfa_res'] for b in buildings), 1),
    gfa_com=round(sum(b['gfa_com'] for b in buildings), 1),
    gfa_off=round(sum(b['gfa_off'] for b in buildings), 1),
    far=round(sum(b['gfa'] for b in buildings) / sum(b['lot_area'] for b in buildings), 2),
)
vals['units'] = int(round(vals['gfa_res'] / 90))
vals['parking'] = vals['units']

# site / street geometry (metres, y down) derived from the lot union, not hand-guessed
SITE_GEOM = unary_union([Polygon(l['poly']) for l in lots])
SITE_RINGS = [list(g.exterior.coords) for g in
              (SITE_GEOM.geoms if SITE_GEOM.geom_type == 'MultiPolygon' else [SITE_GEOM])]
ROAD_RING = SITE_GEOM.buffer(7.5, join_style=2).difference(SITE_GEOM).simplify(0.35)
ROADS = [list(g.exterior.coords) for g in
         (ROAD_RING.geoms if ROAD_RING.geom_type == 'MultiPolygon' else [ROAD_RING])]
_xs = [p[0] for r in SITE_RINGS for p in r]; _ys = [p[1] for r in SITE_RINGS for p in r]
PLATE = [[min(_xs) - 20, min(_ys) - 20], [max(_xs) + 20, min(_ys) - 20],
         [max(_xs) + 20, max(_ys) + 20], [min(_xs) - 20, max(_ys) + 20]]

json.dump(dict(params=dict(setback=SETBACK, floors=FLOORS), buildings=buildings, summary=vals,
               site=SITE_RINGS, roads=ROADS),
          open(os.path.join(ROOT, 'model', 'massing.json'), 'w'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ 3-D helpers
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def norm(a):
    L = math.sqrt(dot(a, a)) or 1
    return (a[0] / L, a[1] / L, a[2] / L)


def camera(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    d = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    right = norm((-math.sin(az), math.cos(az), 0.0))
    up = norm(cross(d, right))
    return d, right, up


LIGHT = norm((-0.35, -0.5, 0.78))


def shade(hexcol, n, base=0.52):
    n = norm(n)
    k = base + (1 - base) * max(0.0, dot(n, LIGHT))
    h = hexcol.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


def faces_of(poly, z0, z1, col_side, col_top):
    faces = []
    ring = poly[:]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    cx = sum(p[0] for p in ring) / len(ring)
    cy = sum(p[1] for p in ring) / len(ring)
    faces.append(dict(pts=[(x, y, z1) for x, y in ring], n=(0, 0, 1), col=col_top))
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        nx, ny = ey, -ex
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if nx * (mx - cx) + ny * (my - cy) < 0:
            nx, ny = -nx, -ny
        faces.append(dict(pts=[(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
                          n=(nx, ny, 0), col=col_side))
    return faces


def cam_ortho(az_deg, el_deg):
    return camera(az_deg, el_deg)


def ring_of(poly):
    return poly[:-1] if poly[0] == poly[-1] else poly


def render(path, az=128, el=34, w=1560, h=1080, scale=0.98, title='', subtitle='',
           legend=True, labels=True, shadow=True, short=False,
           eye=None, target=None, fov=46, pad_top=92, pad_bottom=104, facade=False):
    """Orthographic axonometric (default) or true perspective when eye/target are given."""
    persp = eye is not None
    if persp:
        eye = tuple(float(v) for v in eye)
        target = tuple(float(v) for v in target)
        fwd = norm(sub(target, eye))
        right = norm(cross(fwd, (0.0, 0.0, 1.0)))
        up = norm(cross(right, fwd))
        area = h - pad_top - pad_bottom
        focal = (area / 2.0) / math.tan(math.radians(fov) / 2.0)

        def P(p):
            r = sub(p, eye)
            wz = max(dot(r, fwd), 0.4)
            return (w / 2.0 + focal * dot(r, right) / wz,
                    pad_top + area / 2.0 - focal * dot(r, up) / wz)

        def depth(p):
            return dot(sub(p, eye), fwd)

        def visible(n, pts):
            c = tuple(sum(q[i] for q in pts) / len(pts) for i in range(3))
            return dot(n, sub(eye, c)) > 0.001
    else:
        d, right, up = camera(az, el)
        allpts = [(p[0], p[1], 0.0) for r in SITE_RINGS for p in r]
        for bd in buildings:
            for p in ring_of(bd['poly']):
                allpts.append((p[0], p[1], 0.0))
                allpts.append((p[0], p[1], bd['height']))
        us = [dot(p, right) for p in allpts]
        vs = [dot(p, up) for p in allpts]
        u0, u1 = min(us), max(us)
        v0, v1 = min(vs), max(vs)
        area = h - pad_top - pad_bottom
        s = min((w - 150) / (u1 - u0), area / (v1 - v0)) * scale
        ox = (w - (u1 - u0) * s) / 2.0 - u0 * s
        oy = pad_top + area / 2.0 + (v0 + v1) / 2.0 * s

        def P(p):
            return (ox + dot(p, right) * s, oy - dot(p, up) * s)

        def depth(p):
            return dot(p, d)

        def visible(n, pts):
            return dot(n, d) > 0.001

    out = ['<rect width="%d" height="%d" fill="#fbfcfd"/>' % (w, h)]
    if persp:
        # sky above the horizon line, ground plane below it (camera has no roll)
        dh = (fwd[0], fwd[1], 0.0)
        du_, dv_, dw_ = dot(dh, right), dot(dh, up), max(dot(dh, fwd), 1e-6)
        y_h = max(-10.0, min(h + 10.0, pad_top + area / 2.0 - focal * dv_ / dw_))
        out.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#dfe8ee"/><stop offset="1" stop-color="#f6f9fb"/>'
                   '</linearGradient></defs>')
        out.append('<rect width="%d" height="%.1f" fill="url(#sky)"/>' % (w, max(y_h, 0)))
        out.append('<rect y="%.1f" width="%d" height="%.1f" fill="#edeae3"/>'
                   % (y_h, w, max(h - y_h, 0)))
    # roads (9 m band around the site union)
    for r in ROADS:
        pts = [P((x, y, -0.1)) for x, y in r]
        out.append('<path d="M %s Z" fill="#dfe3e6" stroke="#cdd3d8" stroke-width="0.8"/>'
                   % ' L '.join('%.1f,%.1f' % q for q in pts))
    # site ground
    for r in SITE_RINGS:
        pts = [P((x, y, 0.0)) for x, y in r]
        out.append('<path d="M %s Z" fill="#f3f1ea" stroke="#a99a7a" stroke-width="1.8"/>'
                   % ' L '.join('%.1f,%.1f' % q for q in pts))
    # lot tint + dashed property lines
    for bd in buildings:
        pts = [P((x, y, 0.02)) for x, y in ring_of(bd['poly'])]
        out.append('<path d="M %s Z" fill="#ece5d5" stroke="#bcae90" stroke-width="0.8" '
                   'stroke-dasharray="5 3"/>' % ' L '.join('%.1f,%.1f' % q for q in pts))

    # shadows: swept silhouette (true footprint + offset copy + edge quads)
    if shadow:
        from shapely.geometry import Polygon as SP
        ox_, oy_ = -LIGHT[0] / LIGHT[2], -LIGHT[1] / LIGHT[2]
        for bd in buildings:
            bh = bd['height']
            dx, dy = ox_ * bh, oy_ * bh
            ring = ring_of(bd['poly'])
            fp = SP(ring)
            off = SP([(x + dx, y + dy) for x, y in ring])
            quads = []
            for i in range(len(ring)):
                a2, c2 = ring[i], ring[(i + 1) % len(ring)]
                quads.append(SP([a2, c2, (c2[0] + dx, c2[1] + dy), (a2[0] + dx, a2[1] + dy)]))
            sh = unary_union([fp, off] + quads)
            for g in (sh.geoms if sh.geom_type == 'MultiPolygon' else [sh]):
                pts = [P((x, y, 0.03)) for x, y in g.exterior.coords]
                out.append('<path d="M %s Z" fill="#1b1b1f" opacity="0.075"/>'
                           % ' L '.join('%.1f,%.1f' % q for q in pts))

    # building volumes
    faces = []
    for bd in buildings:
        for i, f in enumerate(bd['floors']):
            col = COL[f['use']]
            top_floor = (i == len(bd['floors']) - 1)
            for fc in faces_of(bd['poly'], f['z0'], f['z1'], None, None):
                if not visible(fc['n'], fc['pts']):
                    continue
                fc['col'] = shade(col, fc['n'], 0.99 if fc['n'] == (0, 0, 1) else 0.74)
                fc['depth'] = sum(depth(q) for q in fc['pts']) / len(fc['pts'])
                fc['lot'] = bd['id']
                fc['z'] = (f['z0'], f['z1'])
                fc['use'] = f['use']
                faces.append(fc)
    faces.sort(key=lambda f: f['depth'])
    for f in faces:
        pts = [P(q) for q in f['pts']]
        out.append('<path d="M %s Z" fill="%s" stroke="#00000026" stroke-width="0.55" '
                   'stroke-linejoin="round"/>'
                   % (' L '.join('%.1f,%.1f' % q for q in pts), f['col']))
        if facade and f['n'][2] == 0:
            # ribbon glazing band + mullions, interpolated on the wall quad
            (ax_, ay_, _), (bx_, by_, _) = f['pts'][0], f['pts'][1]
            z0, z1 = f['z']
            t0 = 0.16 if f['use'] == 'com' else 0.22
            t1 = 0.92 if f['use'] == 'com' else 0.80
            q = [P((ax_, ay_, z0 + (z1 - z0) * t0)), P((bx_, by_, z0 + (z1 - z0) * t0)),
                 P((bx_, by_, z0 + (z1 - z0) * t1)), P((ax_, ay_, z0 + (z1 - z0) * t1))]
            out.append('<path d="M %s Z" fill="#2f4351" fill-opacity="0.34"/>'
                       % ' L '.join('%.1f,%.1f' % pp for pp in q))
            seg_len = math.hypot(bx_ - ax_, by_ - ay_)
            n_mull = max(1, int(seg_len / 2.6))
            for k in range(1, n_mull):
                tt = k / float(n_mull)
                mx_ = ax_ + (bx_ - ax_) * tt
                my_ = ay_ + (by_ - ay_) * tt
                p1 = P((mx_, my_, z0 + (z1 - z0) * t0)); p2 = P((mx_, my_, z0 + (z1 - z0) * t1))
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#f7f7f4" '
                           'stroke-opacity="0.55" stroke-width="0.8"/>' % (p1[0], p1[1], p2[0], p2[1]))

    # labels (perspective: only the front row, so no label lands on a nearer volume)
    if labels:
        if persp:
            dmin = min(sum(depth((x, y, bd['height'])) for x, y in ring_of(bd['poly'])) / len(ring_of(bd['poly']))
                       for bd in buildings)
        else:
            dmin = None

        def hidden_depth(bd):
            if not persp:
                return False
            dd = sum(depth((x, y, bd['height'])) for x, y in ring_of(bd['poly'])) / len(ring_of(bd['poly']))
            return dd > dmin + 26.0

        placed = []
        order = sorted(buildings, key=lambda q: -sum(p[1] for p in q['poly']) / len(q['poly']))
        for bd in order:
            if hidden_depth(bd):
                continue
            ring = ring_of(bd['poly'])
            cx0, cy0 = (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))
            lx, ly = P((cx0, cy0, bd['height']))
            if hidden_depth(bd):
                continue
            if any(abs(lx - q[0]) < (46 if not persp else 30) and abs(ly - q[1]) < 22 for q in placed):
                continue
            placed.append((lx, ly))
            out.append('<text x="%.1f" y="%.1f" font-size="11.5" font-weight="700" fill="#33260f" '
                       'text-anchor="middle" font-family="Vazirmatn">%s</text>' % (lx, ly - 5, bd['id']))
            if not short:
                out.append('<text x="%.1f" y="%.1f" font-size="9.2" fill="#5c4a2e" text-anchor="middle" '
                           'font-family="Vazirmatn">%s طبقه — %s مترمربع</text>'
                           % (lx, ly + 7, fa(str(len(bd['floors']))), fa('%.0f' % bd['footprint'])))

    # title / subtitle
    out.append('<text x="%d" y="40" font-size="21" font-weight="700" fill="#0f4c5c" text-anchor="end" '
               'font-family="Vazirmatn">%s</text>' % (w - 36, title))
    out.append('<text x="%d" y="62" font-size="11.5" fill="#6b7280" text-anchor="end" '
               'font-family="Vazirmatn">%s</text>' % (w - 36, subtitle))

    if not persp:
        bx, by = 46, h - 54
        seg = s * 10.0
        for k in range(4):
            out.append('<rect x="%.1f" y="%d" width="%.1f" height="8" fill="%s" stroke="#333" stroke-width="0.6"/>'
                       % (bx + k * seg, by, seg, '#333' if k % 2 == 0 else '#fff'))
        out.append('<text x="%.1f" y="%d" font-size="10.5" fill="#374151" font-family="Vazirmatn">۰</text>'
                   % (bx - 2, by + 22))
        out.append('<text x="%.1f" y="%d" font-size="10.5" fill="#374151" text-anchor="middle" '
                   'font-family="Vazirmatn">۴۰ متر</text>' % (bx + 4 * seg, by + 22))
    else:
        out.append('<text x="46" y="%d" font-size="10.5" fill="#6b7280" font-family="Vazirmatn">'
                   'نمای پرسپکتیو — مقیاس تقریبی، چشم در ارتفاع ۱٫۷ متر</text>' % (h - 46))

    # north arrow (plan north = -Y)
    ax, ay = w - 82, h - 92
    nu, nv = dot((0, -1, 0), right), dot((0, -1, 0), up)
    L = math.hypot(nu, nv) or 1
    tipx, tipy = ax + nu / L * 20, ay - nv / L * 20
    out.append('<circle cx="%d" cy="%d" r="25" fill="#fff" stroke="#b9c0c7" stroke-width="1"/>' % (ax, ay))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#0f4c5c" stroke-width="2.4"/>'
               % (ax - nu / L * 12, ay + nv / L * 12, tipx, tipy))
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#0f4c5c"/>'
               % (tipx, tipy, tipx - nu / L * 10 - nv / L * 4.5, tipy + nv / L * 10 - nu / L * 4.5,
                  tipx - nu / L * 10 + nv / L * 4.5, tipy + nv / L * 10 + nu / L * 4.5))
    out.append('<text x="%d" y="%d" font-size="9.4" fill="#374151" text-anchor="middle" '
               'font-family="Vazirmatn">شمال نقشه</text>' % (ax, ay + 38))
    out.append('<text x="%d" y="%d" font-size="8.2" fill="#8b949e" text-anchor="middle" '
               'font-family="Vazirmatn">(فرضی — از پلان)</text>' % (ax, ay + 50))

    if legend:
        items = [('res', 'مسکونی'), ('com', 'تجاری (همکف)'), ('off', 'اداری')]
        lx = 44
        for use, name in items:
            out.append('<rect x="%d" y="%d" width="16" height="11" fill="%s" stroke="#00000033"/>'
                       % (lx, h - 88, COL[use]))
            out.append('<text x="%d" y="%d" font-size="9.8" fill="#374151" text-anchor="start" '
                       'font-family="Vazirmatn">%s</text>' % (lx + 22, h - 79, name))
            lx += 22 + len(name) * 7.4 + 20

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" '
           'style="max-width:100%%;height:auto;background:#fbfcfd;font-family:Vazirmatn">%s</svg>'
           % (w, h, ''.join(out)))
    open(path, 'w').write(svg)
    return path


print(json.dumps(vals, ensure_ascii=False))
render(os.path.join(ROOT, 'figures', 'massing-iso.svg'), az=128, el=34, w=1560, h=900,
       scale=1.0, pad_bottom=96, title='نمای ایزومتریک طرح پیشنهادی — ۱۳ قطعه',
       subtitle='بلوک A مسکونی ۳ طبقه · بلوک B تجاری–اداری–مسکونی ۴ طبقه · سطح اشغال %.0f٪ · تراکم %.2f'
       % (vals['coverage'] * 100, vals['far']))
render(os.path.join(ROOT, 'figures', 'massing-plan.svg'), az=90, el=89, w=1180, h=1120,
       scale=1.0, title='نقشه بام و سطح اشغال — ۱۳ قطعه پس از عقب‌نشینی ۱٫۵ متر',
       subtitle='خط‌چین: مرز قطعه · خط پُر: مرز پروژه · سطح اشغال ۶۱٪ · تراکم ۲٫۱۴',
       short=False, shadow=False)
render(os.path.join(ROOT, 'figures', 'massing-street.svg'), w=1560, h=640, pad_top=66, pad_bottom=40,
       title='نمای چشم‌سطح از معبر جنوبی — بلوک B (تجاری–اداری–مسکونی)',
       subtitle='ارتفاع ۱۴٫۱ متر · همکف تجاری ۴٫۵ متر · چشم ناظر ۱٫۷ متر · پرسپکتیو ۵۲ درجه',
       legend=True, short=False, eye=(121.0, 170.0, 1.70), target=(127.0, 120.0, 5.6), fov=40,
       facade=True)

# ------------------------------------------------------------------ OBJ
obj = ['# nabz-sabz massing — metres, Z up', 'o site']
vidx = 0
for b in buildings:
    obj.append('g %s' % b['id'])
    ring = b['poly'][:-1] if b['poly'][0] == b['poly'][-1] else b['poly']
    n = len(ring)
    base = vidx
    for x, y in ring:
        obj.append('v %.3f %.3f 0.000' % (x, y))
    for x, y in ring:
        obj.append('v %.3f %.3f %.3f' % (x, y, b['height']))
    vidx += 2 * n
    for i in range(n):
        j = (i + 1) % n
        obj.append('f %d %d %d %d' % (base + i + 1, base + j + 1, base + n + j + 1, base + n + i + 1))
    obj.append('f ' + ' '.join(str(base + n + i + 1) for i in range(n)))
    obj.append('f ' + ' '.join(str(base + n + i + 1) for i in reversed(range(n))))
open(os.path.join(ROOT, 'model', 'site.obj'), 'w').write('\n'.join(obj) + '\n')
print('obj written')
