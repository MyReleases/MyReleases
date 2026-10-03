"""Builds the profile card: typed text on the left, the dot drawing on the right.

    python scripts/build_readme.py           # drawing at full height, running off the right edge
    python scripts/build_readme.py --inset   # smaller drawing with margins around it

The card is one picture cut into slices so that the e-mail and the X handle can be real
links (a link inside a single image would not be clickable on GitHub). ROWS lists the
slices row by row; each becomes assets/readme-<name>.svg.

README.md is rewritten to stitch the slices back together. assets/readme.svg is the whole
card in one file, for previews. The drawing comes from assets/dots-source.txt (braille dot
art). Edit LINES to change the text.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
W, H = 1280, 824
INK, PAPER, SOFT = "#1f1b2e", "#f5f2ea", "#4a4560"
MONO = "'Cascadia Mono', 'Cascadia Code', Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', 'Yu Gothic', Meiryo, 'Hiragino Sans', 'Noto Sans CJK JP', monospace"
BLEED = "--inset" not in sys.argv  # drawing enlarged to the full height of the card and running off its right edge
X, TITLE, ROLE, BODY, LINK = 72, 76, 28, 21, 21   # left edge of the text, then font sizes
YS = [190, 270, 326, 408, 442, 476, 510, 544, 584]  # baselines, top to bottom
RULE_Y = 346
ART = (566, 0, 8.24, 3.1) if BLEED else (620, 112, 6, 2.3)  # x, y, dot spacing, dot radius
ART_ROWS, ROW_TIME = 100, 0.025  # the inset drawing prints row by row, top to bottom
RISE_TIME = 1.3                  # the full-height drawing floats up into place
ART_START = 0.4
# the text starts typing once the drawing is there
TEXT_START = ART_START + (RISE_TIME if BLEED else ART_ROWS * ROW_TIME) + 0.4
RIGHT = X + 40 * BODY * 0.6  # right edge of the text column (end of the longest line)
SIGN_RIGHT = True  # signature flush right instead of flush left
EMAIL, X_URL = "visory.wave@gmail.com", "https://x.com/VisoryDaily"

# text, x, baseline y, font size, weight, colour, seconds per character, pause after, underlined
LINES = [
    ("Hello,", X, YS[0], TITLE, 800, INK, .09, .35, False),
    ("I'm Visory", X, YS[1], TITLE, 800, INK, .09, .45, False),
    ("Indie product producer", X, YS[2], ROLE, 700, INK, .05, .5, False),
    ("Leading teams that build apps and games.", X, YS[3], BODY, 400, SOFT, .03, .3, False),
    ("Turning rough ideas into clear plans,", X, YS[4], BODY, 400, SOFT, .03, .08, False),
    ("and plans into shipped products.", X, YS[5], BODY, 400, SOFT, .03, .3, False),
    ("Concept, scope, roadmap, release.", X, YS[6], BODY, 400, SOFT, .03, .3, False),
    ("Games people finish, apps people keep.", X, YS[7], BODY, 400, SOFT, .03, .5, False),
    ("— ヴィゾリー", None if SIGN_RIGHT else X, YS[8], BODY, 700, INK, .09, .6, False),  # x=None: flush right
    (EMAIL, X, 704, LINK, 700, INK, .04, .25, True),
    ("@VisoryDaily on X", X, 738, LINK, 700, INK, .04, 0, True),
]
RULE_AFTER = 2  # index of the line the short rule appears under

# The card row by row: (top, bottom, [(name, left, right, link, alt), ...])
LINK_W = 352
ROWS = [
    (0, 600, [("top", 0, W, None, None)]),
    (600, 712, [("mail", 0, LINK_W, f"mailto:{EMAIL}", EMAIL), ("mail-rest", LINK_W, W, None, "")]),
    (712, H, [("x", 0, LINK_W, X_URL, "@VisoryDaily on X"), ("x-rest", LINK_W, W, None, "")]),
]
# Every row must stay taller than one line of README text (24px) even on a phone,
# or the browser pads the row and a dark seam shows: 112 of 1280 units is 24px at 274px wide.
SLICES = {name: (left, top, right - left, bottom - top)
          for top, bottom, cells in ROWS for name, left, right, _, _ in cells}

# braille bit -> (column, row) inside one 2x4 cell
BITS = {0x01: (0, 0), 0x02: (0, 1), 0x04: (0, 2), 0x40: (0, 3), 0x08: (1, 0), 0x10: (1, 1), 0x20: (1, 2), 0x80: (1, 3)}


def drawing(ox, oy, step=6, mirror=True):
    """Dot centres of the drawing, as (x, y) pairs."""
    rows = (ASSETS / "dots-source.txt").read_text(encoding="utf-8").splitlines()
    cols = max(len(r) for r in rows)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            v = ord(ch) - 0x2800
            if not 0 < v < 256:
                continue
            for bit, (dx, dy) in BITS.items():
                if v & bit:
                    gx = i * 2 + dx
                    if mirror:
                        gx = cols * 2 - 1 - gx
                    yield ox + gx * step + step / 2, oy + (j * 4 + dy) * step + step / 2


def advances(text, size):
    """Running width after each character: kana and other wide glyphs take a full em, the rest 0.6."""
    stops = [0.0]
    for ch in text:
        stops.append(stops[-1] + size * (1.0 if ord(ch) > 0x2E80 else 0.6))
    return stops


def typed():
    t, clips, texts, cursors, rule_at = TEXT_START, [], [], [], 0
    for k, (text, x, y, size, weight, color, per, pause, underline) in enumerate(LINES):
        stops = advances(text, size)
        n, total = len(text), stops[-1]
        if x is None:
            x = RIGHT - total
        dur = n * per
        widths = ";".join(f"{w:.1f}" for w in stops)
        xs = ";".join(f"{x + w + 2:.1f}" for w in stops)
        clips.append(f'<clipPath id="l{k}"><rect x="{x}" y="{y - size}" width="0" height="{size * 1.5:.0f}">'
                     f'<animate attributeName="width" calcMode="discrete" values="{widths}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        line = (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
                f'textLength="{total:.1f}" lengthAdjust="spacing">{text}</text>')
        if underline:
            line += f'<rect x="{x}" y="{y + 6}" width="{total:.1f}" height="1.5" fill="{color}"/>'
        texts.append(f'<g clip-path="url(#l{k})">{line}</g>')
        last = k == len(LINES) - 1
        hold = "indefinite" if last else f"{dur + pause:.2f}s"
        blink = 'class="blink" ' if last else ""
        cursors.append(f'<rect {blink}x="{x}" y="{y - size * .82:.0f}" width="{max(3, size * .09):.0f}" height="{size:.0f}" fill="{INK}" opacity="0">'
                       f'<set attributeName="opacity" to="1" begin="{t:.2f}s" dur="{hold}"/>'
                       f'<animate attributeName="x" calcMode="discrete" values="{xs}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect>')
        t += dur + pause
        if k == RULE_AFTER:
            rule_at = t - pause / 2
    rule = (f'<rect x="{X}" y="{RULE_Y}" width="0" height="5" rx="2.5" fill="{INK}">'
            f'<animate attributeName="width" from="0" to="72" begin="{rule_at:.2f}s" dur=".3s" fill="freeze"/></rect>')
    return "".join(clips), "".join(texts) + rule + "".join(cursors), t


def card(box=(0, 0, W, H)):
    bx, by, bw, bh = box
    ox, oy, step, r = ART
    reach = 44  # dots just outside a slice are kept: the drawing moves while it floats up
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>' for x, y in drawing(ox, oy, step)
                   if bx - 4 <= x <= bx + bw + 4 and by - reach <= y <= by + bh + reach)
    if BLEED:
        # the whole drawing fades in while sliding up
        reveal = ""
        art = (f'<g fill="{INK}" clip-path="url(#card)"><g opacity="0">'
               f'<animate attributeName="opacity" values="0;1" begin="{ART_START}s" dur="{RISE_TIME}s" fill="freeze"/>'
               f'<animateTransform attributeName="transform" type="translate" values="0 36;0 0" begin="{ART_START}s" dur="{RISE_TIME}s" '
               f'calcMode="spline" keySplines="0.1 0.7 0.2 1" keyTimes="0;1" fill="freeze"/>{dots}</g></g>')
    else:
        # printed like a photo: one finished row of dots at a time
        heights = ";".join(f"{i * step:.1f}" for i in range(ART_ROWS + 1))
        reveal = (f'<clipPath id="print"><rect x="{ox}" y="{oy}" width="{ART_ROWS * step}" height="0">'
                  f'<animate attributeName="height" calcMode="discrete" values="{heights}" begin="{ART_START}s" dur="{ART_ROWS * ROW_TIME}s" fill="freeze"/></rect></clipPath>')
        art = f'<g fill="{INK}" clip-path="url(#print)">{dots}</g>'
    clips, text, _ = typed()
    label = " ".join(line[0] for line in LINES)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx} {by} {bw} {bh}" width="{bw}" height="{bh}" preserveAspectRatio="none" font-family="{MONO}" role="img" aria-label="{label}">
  <style>.blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ visibility: hidden }} }}</style>
  <defs>
    <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="920" cy="412" r="740"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="20"/></clipPath>
    {reveal}
    {clips}
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="{PAPER}"/>
  <rect width="{W}" height="{H}" rx="20" fill="url(#glow)"/>
  {art}
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.25" fill="none" stroke="#e2dccd" stroke-width="1.5"/>
  {text}
</svg>'''


def pct(width):
    return f"{width / W * 100:.5f}".rstrip("0").rstrip(".") + "%"


def readme_html(src):
    """The stitched card. `src(name)` gives the image address for a slice."""
    about = " ".join(line[0] for line in LINES if not line[8])
    out = []
    for _, _, cells in ROWS:
        for name, left, right, link, alt in cells:
            tag = f'<img src="{src(name)}" width="{pct(right - left)}" align="top" alt="{about if alt is None else alt}" />'
            out.append(f'<a href="{link}">{tag}</a>' if link else tag)
    # no whitespace between the tags: any gap would show up as a seam in the card
    return "<p>" + "".join(out) + "</p>"


if __name__ == "__main__":
    (ASSETS / "readme.svg").write_text(card(), encoding="utf-8")
    for stale in ASSETS.glob("readme-*.svg"):
        stale.unlink()
    for name, box in SLICES.items():
        (ASSETS / f"readme-{name}.svg").write_text(card(box), encoding="utf-8")
    (ROOT / "README.md").write_text(readme_html(lambda name: f"assets/readme-{name}.svg") + "\n", encoding="utf-8")
    sizes = ", ".join(f"{p.name} {p.stat().st_size // 1024} KB" for p in sorted(ASSETS.glob("readme*.svg")))
    print(sizes)
