#!/usr/bin/env python3
"""Draw out/explosion.svg from out/explosion.json (no matplotlib needed).

    python3 out/plot_explosion.py
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
runs = json.load(open(os.path.join(HERE, "explosion.json")))["runs"]
runs = sorted({r["support"]: r for r in runs}.values(), key=lambda r: -r["support"])

W, H, L, R, T, B = 640, 380, 70, 150, 30, 50
xs = [r["support"] for r in runs]
lo_x, hi_x = math.log2(min(xs)), math.log2(max(xs))
lo_y, hi_y = 2, 6  # 10^2 .. 10^6


def px(s):  # support decreases left to right
    return L + (hi_x - math.log2(s)) / (hi_x - lo_x) * (W - L - R)


def py(v):
    return T + (hi_y - math.log10(v)) / (hi_y - lo_y) * (H - T - B)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="sans-serif" font-size="12">',
       f'<rect width="{W}" height="{H}" fill="white"/>']
for e in range(lo_y, hi_y + 1):
    y = py(10 ** e)
    out.append(f'<line x1="{L}" x2="{W - R}" y1="{y}" y2="{y}" stroke="#ddd"/>')
    out.append(f'<text x="{L - 8}" y="{y + 4}" text-anchor="end">1e{e}</text>')
for s in xs:
    x = px(s)
    out.append(f'<line x1="{x}" x2="{x}" y1="{T}" y2="{H - B}" stroke="#eee"/>')
    out.append(f'<text x="{x}" y="{H - B + 18}" text-anchor="middle">{s}</text>')
out.append(f'<text x="{(L + W - R) / 2}" y="{H - 10}" text-anchor="middle">'
           'support threshold (log2, halving to the right)</text>')

for key, color, label in [("peak_counters", "#c0392b", "peak pair counters"),
                          ("frequent_pairs", "#2471a3", "frequent pairs found")]:
    pts = " ".join(f"{px(r['support']):.1f},{py(r[key]):.1f}" for r in runs)
    out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>')
    for r in runs:
        out.append(f'<circle cx="{px(r["support"]):.1f}" cy="{py(r[key]):.1f}" r="3" fill="{color}"/>')
    last, dy = runs[-1], (4 if key == "peak_counters" else 18)
    out.append(f'<text x="{W - R + 8}" y="{py(last[key]) + dy:.1f}" fill="{color}">{label}</text>')
out.append("</svg>")
open(os.path.join(HERE, "explosion.svg"), "w").write("\n".join(out))
print("  -> out/explosion.svg")
