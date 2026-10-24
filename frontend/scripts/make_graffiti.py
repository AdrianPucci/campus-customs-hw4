"""Draws an original graffiti-style wall (SVG) for the Home page strip.

Everything is generated from shapes with a fixed random seed, so it's new artwork, not a copy:
a sprayed concrete wall, big angular "wildstyle" shards in coral and olive with navy outlines,
teal bubbles, white highlights, paint drips and splatter.

Run from the frontend folder:  python scripts/make_graffiti.py
Writes public/graffiti-wall.svg
"""
import math
import random
from pathlib import Path

W, H = 1500, 500
CORAL, TEAL, OLIVE, NAVY = "#f0705e", "#22a9b6", "#8f8c3c", "#1d2b4f"
CREAM, DARK = "#f4ead2", "#121a30"
rng = random.Random(1701)  # Yale's founding year; change it for a different wall


def poly(points, fill, stroke=None, width=0, extra=""):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    s = f' stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"' if stroke else ""
    return f'<polygon points="{pts}" fill="{fill}"{s} {extra}/>'


def shard(cx, cy, length, angle, thickness):
    """A long pointed blade, the basic wildstyle stroke."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    tip = (cx + dx * length, cy + dy * length)
    back = (cx - dx * length * 0.35, cy - dy * length * 0.35)
    bend = rng.uniform(-0.25, 0.25) * length
    mid1 = (cx + nx * thickness + dx * bend * 0.2, cy + ny * thickness + dy * bend * 0.2)
    mid2 = (cx - nx * thickness * 0.6 + dx * bend * 0.3, cy - ny * thickness * 0.6 + dy * bend * 0.3)
    return [back, mid1, tip, mid2]


def drip(x, y, color, length):
    w = rng.uniform(3, 6)
    return (f'<path d="M{x - w:.1f},{y:.1f} L{x - w * 0.6:.1f},{y + length:.1f} '
            f'a{w * 0.6:.1f},{w * 0.6:.1f} 0 0 0 {w * 1.2:.1f},0 L{x + w:.1f},{y:.1f} Z" fill="{color}"/>')


parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         """<defs>
  <filter id="wall" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.10  0 0 0 0 0.14  0 0 0 0 0.24  0 0 0 0.55 0"/>
  </filter>
  <filter id="spray" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="3" result="g"/>
    <feDisplacementMap in="SourceGraphic" in2="g" scale="5"/>
  </filter>
  <filter id="soft"><feGaussianBlur stdDeviation="14"/></filter>
</defs>""",
         f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']

# Soft sprayed color clouds behind everything
for _ in range(9):
    c = rng.choice([TEAL, CORAL, OLIVE])
    parts.append(f'<ellipse cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(0, H):.0f}" rx="{rng.uniform(120, 260):.0f}" '
                 f'ry="{rng.uniform(60, 140):.0f}" fill="{c}" opacity="0.18" filter="url(#soft)"/>')

# Concrete texture and faint horizontal block seams
parts.append(f'<rect width="{W}" height="{H}" filter="url(#wall)"/>')
for y in range(100, H, 100):
    parts.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{DARK}" stroke-opacity="0.35" stroke-width="2"/>')

# The piece: overlapping shards, outlined in navy, with cream highlights
art = ['<g filter="url(#spray)">']
centers = [(x, H * 0.5 + rng.uniform(-60, 60)) for x in range(90, W, 120)]
for cx, cy in centers:
    for _ in range(3):
        color = rng.choice([CORAL, CORAL, OLIVE, OLIVE, TEAL])
        pts = shard(cx + rng.uniform(-30, 30), cy + rng.uniform(-40, 40),
                    rng.uniform(110, 230), rng.uniform(0, 360), rng.uniform(22, 48))
        art.append(poly(pts, color, DARK, 9))
        # highlight sliver along one edge
        hx = [(pts[0][0] * 0.7 + pts[1][0] * 0.3, pts[0][1] * 0.7 + pts[1][1] * 0.3), pts[1],
              (pts[1][0] * 0.6 + pts[2][0] * 0.4, pts[1][1] * 0.6 + pts[2][1] * 0.4)]
        art.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in hx)}" fill="none" '
                   f'stroke="{CREAM}" stroke-width="3" stroke-linecap="round" opacity="0.85"/>')

# Teal bubbles with navy rims and white glints
for _ in range(26):
    x, y, r = rng.uniform(40, W - 40), rng.uniform(70, H - 70), rng.uniform(9, 22)
    art.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{TEAL}" stroke="{DARK}" stroke-width="5"/>')
    art.append(f'<circle cx="{x - r * 0.35:.0f}" cy="{y - r * 0.35:.0f}" r="{r * 0.22:.1f}" fill="#ffffff" opacity="0.9"/>')

# Flowing teal line weaving through the piece
pts = [(0, H * 0.55)]
for x in range(150, W + 150, 150):
    pts.append((x, H * 0.5 + rng.uniform(-110, 110)))
d = f"M{pts[0][0]},{pts[0][1]:.0f} " + " ".join(f"S{x - 75},{y:.0f} {x},{y:.0f}" for x, y in pts[1:])
art.append(f'<path d="{d}" fill="none" stroke="{DARK}" stroke-width="16" stroke-linecap="round"/>')
art.append(f'<path d="{d}" fill="none" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/>')
art.append("</g>")
parts += art

# Drips under the piece
for _ in range(22):
    parts.append(drip(rng.uniform(30, W - 30), rng.uniform(H * 0.62, H * 0.75),
                      rng.choice([CORAL, OLIVE, TEAL]), rng.uniform(25, 95)))

# Spray splatter
for _ in range(240):
    parts.append(f'<circle cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(0, H):.0f}" r="{rng.uniform(0.8, 3.2):.1f}" '
                 f'fill="{rng.choice([CORAL, TEAL, OLIVE, CREAM])}" opacity="{rng.uniform(0.4, 0.9):.2f}"/>')

parts.append("</svg>")
out = Path(__file__).resolve().parent.parent / "public" / "graffiti-wall.svg"
out.write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
