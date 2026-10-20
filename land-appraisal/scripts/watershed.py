"""Watertight, smoothed lot geometry: watershed on (fill | parcel-boundary) mask."""
import json
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage
from scipy.ndimage import binary_closing, binary_opening, binary_dilation, distance_transform_edt, label
from skimage.segmentation import watershed
from skimage import measure
from skimage.morphology import disk
from shapely.geometry import Polygon

S = 30.0  # px per metre at 400 dpi
doc = pymupdf.open('/tmp/arena-coding-uploads/1_29754637390.pdf')
pix = doc[0].get_pixmap(dpi=400, colorspace=pymupdf.csRGB, alpha=False)
a = np.array(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
R, G, B = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
YY = (R > 200) & (G > 200) & (B < 120)
CC = (R < 120) & (G > 200) & (B > 200)
DARK = (np.abs(R - 184) < 45) & (G < 70) & (np.abs(B - 46) < 60)   # parcel boundary 0.72,0,0.18
fill = YY | CC

lab, n = label(fill)
sizes = ndimage.sum(fill, lab, range(1, n + 1))
seeds = np.zeros_like(lab)
k = 0
for i in range(n):
    if sizes[i] > 30000:
        k += 1
        seeds[lab == i + 1] = k
print('lots', k)

mask0 = binary_closing(fill | DARK, disk(3))
mask0 = binary_opening(mask0, disk(2))
lab2, n2 = label(mask0)
keep = np.zeros_like(mask0)
for i in range(1, n2 + 1):
    m = lab2 == i
    if (fill & m).sum() > 20000:
        keep |= m
region = keep
dist = distance_transform_edt(region)
ws = watershed(-dist, seeds, mask=region)

out = []
for i in range(1, k + 1):
    m = ws == i
    m = binary_opening(m, disk(4))
    m = binary_closing(m, disk(5))
    m = ndimage.binary_fill_holes(m)
    labm, nm = label(m)
    if nm > 1:  # keep biggest blob
        sz = ndimage.sum(m, labm, range(1, nm + 1))
        m = labm == (int(np.argmax(sz)) + 1)
    cont = max(measure.find_contours(m.astype(float), 0.5), key=len)
    p = Polygon([(c[1], c[0]) for c in cont]).buffer(0)
    p = p.simplify(36.0, preserve_topology=True)         # drop 1.75 m survey-marker zig-zag
    p = p.simplify(1.4, preserve_topology=True)
    p = p.buffer(0)
    cy, cx = ndimage.center_of_mass(m)
    isy = (YY[int(cy) - 45:int(cy) + 45, int(cx) - 45:int(cx) + 45].sum() >
           CC[int(cy) - 45:int(cy) + 45, int(cx) - 45:int(cx) + 45].sum())
    out.append(dict(k=i, yellow=bool(isy),
                    poly=[[round(x / S, 3), round(y / S, 3)] for x, y in p.exterior.coords]))
    print(i, 'Y' if isy else 'C', '%.1f m2' % (p.area / S ** 2), 'n=%d' % len(p.exterior.coords))
json.dump(out, open('lots_ws.json', 'w'))
