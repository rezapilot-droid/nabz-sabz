"""Small SVG drawing helpers (metres in, SVG out)."""
import math
import json
from shapely.geometry import Polygon, LineString, Point

FONT = "font-family:'Vazirmatn','IRANSans','Tahoma','Segoe UI',sans-serif"


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def poly_path(coords, close=True):
    d = 'M ' + ' L '.join('%.2f,%.2f' % (x, y) for x, y in coords)
    return d + (' Z' if close else '')


def text(x, y, s, size=9, fill='#111', anchor='middle', weight='400', extra='', rot=None):
    tr = ' transform="rotate(%s %.2f %.2f)"' % (rot, x, y) if rot else ''
    return ('<text x="%.2f" y="%.2f" font-size="%.1f" fill="%s" text-anchor="%s" '
            'font-weight="%s" style="%s"%s%s>%s</text>') % (x, y, size, fill, anchor, weight, FONT, extra, tr, esc(s))


def offset_line(coords, dist, away_from):
    """Offset a polyline by dist (metres) to the side away from `away_from` point."""
    pts = list(coords)
    out = []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == len(pts) - 1:
            dx, dy = x - pts[-2][0], y - pts[-2][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        cand1 = (x + nx * dist, y + ny * dist)
        cand2 = (x - nx * dist, y - ny * dist)
        d1 = math.dist(cand1, away_from)
        d2 = math.dist(cand2, away_from)
        out.append(cand1 if d1 < d2 else cand2)
    return out


def band(coords, width, away_from, fill='#f4f1e8', stroke='#b9b2a0', dash='5,4'):
    """Right-of-way band between a frontage line and its outer offset."""
    outer = offset_line(coords, width, away_from)
    ring = list(coords) + list(reversed(outer))
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="0.5" stroke-dasharray="%s" fill-opacity="0.85"/>'
            % (poly_path(ring), fill, stroke, dash))


def arrow_dim(x1, y1, x2, y2, label, size=7.4, side=1, color='#8a1c1c', off=0.0):
    """Dimension line with ticks and a label."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    x1o, y1o = x1 + nx * off, y1 + ny * off
    x2o, y2o = x2 + nx * off, y2 + ny * off
    mx, my = (x1o + x2o) / 2 + nx * side * 1.2, (y1o + y2o) / 2 + ny * side * 1.2
    tick = 0.7
    s = ['<g stroke="%s" stroke-width="0.45" fill="none">' % color,
         '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (x1o, y1o, x2o, y2o)]
    for (px, py) in ((x1o, y1o), (x2o, y2o)):
        s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke-width="0.9"/>'
                 % (px - (nx + dx / L) * tick, py - (ny + dy / L) * tick,
                    px + (nx + dx / L) * tick, py + (ny + dy / L) * tick))
    s.append('</g>')
    s.append(text(mx, my + 2.2, label, size=size, fill=color))
    return ''.join(s)


def svg_doc(w, h, body, extra_defs=''):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" '
            'role="img" style="max-width:100%%;height:auto;background:#fff">'
            '<defs>%s</defs>%s</svg>') % (w, h, extra_defs, body)
