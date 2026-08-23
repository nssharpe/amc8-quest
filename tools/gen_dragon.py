"""Generate the 10-stage dragon evolution as standalone, Inkscape-editable SVGs.

Run from the repo root:  python tools/gen_dragon.py
Outputs assets/pets/dragon/stage0.svg ... stage9.svg (200x200 viewBox,
transparent background, flat cartoon style, no strokes on fills).
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "pets", "dragon")

# ---------------- palette ----------------
def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))

def hx(rgb):
    return "#%02x%02x%02x" % rgb

GREEN_Light = (108, 212, 134)   # young body
GREEN_Deep = (52, 158, 92)      # elder body
BELLY = "#f6ecc3"
MUZZLE_L = (152, 228, 168)
MUZZLE_D = (96, 190, 122)
HORN = "#f2e3b8"
HORN_GOLD = "#ffd21f"
DARK = "#26324e"
BLUSH = "#ff9c9c"
WING_MEMBRANE = "#8fe0c8"
WING_MEMBRANE_MYTHIC = "#c9aaff"
FLAME_O = "#ff9f2e"
FLAME_Y = "#ffd21f"
EGG = "#f2f7e9"
EGG_SPOT = "#a5d9a0"
CROWN = "#ffd21f"
CROWN_D = "#e0a80f"

# ---------------- shared parts (all drawn around a 200x200 canvas, feet at y=196) ----

def defs(stage):
    d = """
  <radialGradient id="auraGrad" cx="50%" cy="55%" r="50%">
    <stop offset="0%" stop-color="#ffd21f" stop-opacity="0.55"/>
    <stop offset="70%" stop-color="#ff9f2e" stop-opacity="0.28"/>
    <stop offset="100%" stop-color="#ff9f2e" stop-opacity="0"/>
  </radialGradient>"""
    return f"<defs>{d}\n  </defs>"

def aura(kind):
    if kind == "glow":
        return '<circle id="aura" cx="100" cy="112" r="88" fill="url(#auraGrad)"/>'
    if kind == "ring":
        flames = []
        import math
        for i in range(10):
            ang = math.pi * 2 * i / 10 - math.pi / 2
            x = 100 + 90 * math.cos(ang)
            y = 112 + 84 * math.sin(ang)
            s = 1 if i % 2 == 0 else 0.7
            flames.append(
                f'<g transform="translate({x:.0f},{y:.0f}) scale({s})">'
                f'<path d="M0,8 C-6,2 -5,-6 0,-12 C5,-6 6,2 0,8 Z" fill="{FLAME_O}"/>'
                f'<path d="M0,5 C-3,1 -2,-3 0,-7 C2,-3 3,1 0,5 Z" fill="{FLAME_Y}"/></g>')
        return ('<circle id="aura" cx="100" cy="112" r="88" fill="url(#auraGrad)"/>'
                '<g id="flameRing">' + "".join(flames) + "</g>")
    return ""

def wing(side, size, membrane):
    """side: -1 left, 1 right. size: 0 none, 1 nub, 2 small, 3 large."""
    if size == 0:
        return ""
    if size == 1:
        return (f'<g id="wing{"L" if side<0 else "R"}" transform="translate(100,0) scale({side},1) translate(-100,0)">'
                f'<path d="M138,118 C156,108 162,116 156,130 C150,140 140,140 136,132 Z" fill="{hx(GREEN_Deep)}"/></g>')
    if size == 2:
        arm = 'M136,112 C168,86 186,92 184,104 C176,100 168,102 164,108 C174,108 178,116 174,124 C166,120 160,122 156,128 C162,132 162,140 156,144 C144,146 134,132 134,120 Z'
        mem = 'M140,116 C160,102 174,104 172,112 C164,112 158,116 154,122 C158,126 157,133 152,136 C144,136 138,128 138,120 Z'
    else:
        arm = 'M134,106 C168,64 196,70 194,86 C184,80 174,82 168,90 C182,90 188,102 182,112 C172,106 164,108 158,116 C168,120 170,132 162,140 C146,146 132,126 132,112 Z'
        mem = 'M140,108 C164,80 184,84 182,94 C172,92 164,96 158,104 C164,108 164,118 158,124 C148,126 138,118 138,110 Z'
    g = f'<g id="wing{"L" if side<0 else "R"}" transform="translate(100,0) scale({side},1) translate(-100,0)">'
    return g + f'<path d="{arm}" fill="{hx(GREEN_Deep)}"/><path d="{mem}" fill="{membrane}"/></g>'

def tail(body, fin, flame):
    t = f'<path id="tail" d="M118,168 C150,172 168,160 172,136 C174,124 170,116 162,112 C166,124 160,140 146,148 C136,154 124,156 116,154 Z" fill="{body}"/>'
    if fin:
        t += f'<path id="tailFin" d="M162,112 C158,100 162,90 172,84 C170,94 174,98 182,98 C174,104 170,110 170,118 Z" fill="{hx(GREEN_Deep)}"/>'
    if flame:
        s = {1: 0.7, 2: 1.0, 3: 1.3}[flame]
        t += (f'<g id="tailFlame" transform="translate(170,100) scale({s})">'
              f'<path d="M0,14 C-10,4 -8,-10 0,-20 C8,-10 10,4 0,14 Z" fill="{FLAME_O}"/>'
              f'<path d="M0,9 C-5,3 -4,-5 0,-11 C4,-5 5,3 0,9 Z" fill="{FLAME_Y}"/></g>')
    return t

def spikes(body_dark, n):
    if not n:
        return ""
    xs = [76, 100, 124][:n] if n <= 3 else [64, 82, 100, 118, 136]
    out = []
    for i, x in enumerate(xs):
        h = 16 if x == 100 else 12
        out.append(f'<path d="M{x-9},46 C{x-4},{40-h} {x+4},{40-h} {x+9},46 L{x+6},54 L{x-6},54 Z" fill="{body_dark}"/>')
    return '<g id="spikes">' + "".join(out) + "</g>"

def creature(p):
    """The dragon itself, feet on y=196, centered on x=100."""
    body = hx(lerp(GREEN_Light, GREEN_Deep, p["tone"]))
    body_dark = hx(lerp(GREEN_Deep, (34, 120, 70), p["tone"]))
    muzzle = hx(lerp(MUZZLE_L, MUZZLE_D, p["tone"] * 0.6))
    parts = []
    parts.append(wing(-1, p["wings"], p["membrane"]))
    parts.append(wing(1, p["wings"], p["membrane"]))
    parts.append(tail(body, p["tailfin"], p["tailflame"]))
    # legs
    parts.append(f'<ellipse id="footL" cx="74" cy="186" rx="16" ry="11" fill="{body_dark}"/>')
    parts.append(f'<ellipse id="footR" cx="126" cy="186" rx="16" ry="11" fill="{body_dark}"/>')
    # body + belly
    parts.append(f'<ellipse id="body" cx="100" cy="150" rx="46" ry="40" fill="{body}"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="158" rx="30" ry="28" fill="{BELLY}"/>')
    # arms
    parts.append(f'<ellipse id="armL" cx="62" cy="146" rx="10" ry="15" transform="rotate(18 62 146)" fill="{body_dark}"/>')
    parts.append(f'<ellipse id="armR" cx="138" cy="146" rx="10" ry="15" transform="rotate(-18 138 146)" fill="{body_dark}"/>')
    # horns (behind head)
    if p["horns"]:
        hs = {1: 0.6, 2: 1.0}[p["horns"]]
        hcol = HORN_GOLD if p.get("goldhorns") else HORN
        parts.append(f'<g id="horns" transform="translate(100,60) scale({hs}) translate(-100,-60)">'
                     f'<path d="M66,58 C58,44 58,30 68,20 C74,32 76,44 74,56 Z" fill="{hcol}"/>'
                     f'<path d="M134,58 C142,44 142,30 132,20 C126,32 124,44 126,56 Z" fill="{hcol}"/></g>')
    # head
    parts.append(f'<circle id="head" cx="100" cy="92" r="52" fill="{body}"/>')
    if p.get("marks"):
        parts.append(f'<g id="marks" fill="{BELLY}" opacity="0.85">'
                     '<path d="M100,50 l3.5,7 7,1 -5,5 1.2,7 -6.7,-3.5 -6.7,3.5 1.2,-7 -5,-5 7,-1 Z"/>'
                     '<circle cx="64" cy="72" r="3"/><circle cx="136" cy="72" r="3"/></g>')
    # muzzle + face
    parts.append(f'<ellipse id="muzzle" cx="100" cy="114" rx="27" ry="18" fill="{muzzle}"/>')
    parts.append(f'<ellipse id="nostrilL" cx="92" cy="109" rx="2.6" ry="3.4" fill="{DARK}"/>')
    parts.append(f'<ellipse id="nostrilR" cx="108" cy="109" rx="2.6" ry="3.4" fill="{DARK}"/>')
    smile = 'M88,122 Q100,130 112,122'
    parts.append(f'<path id="mouth" d="{smile}" fill="none" stroke="{DARK}" stroke-width="3.5" stroke-linecap="round"/>')
    if p.get("fang"):
        parts.append(f'<path id="fang" d="M108,124 l3,7 4,-6 Z" fill="#ffffff"/>')
    pupil = HORN_GOLD if p.get("gloweyes") else DARK
    for sx, name in ((78, "eyeL"), (122, "eyeR")):
        parts.append(f'<g id="{name}"><ellipse cx="{sx}" cy="84" rx="13" ry="15" fill="#ffffff"/>'
                     f'<ellipse cx="{sx + 2}" cy="86" rx="6.5" ry="8.5" fill="{pupil}"/>'
                     f'<circle cx="{sx + 4.5}" cy="82" r="2.6" fill="#ffffff"/></g>')
    parts.append(f'<ellipse id="cheekL" cx="62" cy="104" rx="8" ry="5" fill="{BLUSH}" opacity="0.55"/>')
    parts.append(f'<ellipse id="cheekR" cx="138" cy="104" rx="8" ry="5" fill="{BLUSH}" opacity="0.55"/>')
    parts.append(spikes(body_dark, p["spikes"]))
    if p.get("crown"):
        parts.append(f'<g id="crown" transform="rotate(-8 100 40)">'
                     f'<path d="M78,44 L78,26 L88,36 L100,20 L112,36 L122,26 L122,44 Z" fill="{CROWN}"/>'
                     f'<rect x="78" y="42" width="44" height="7" rx="3" fill="{CROWN_D}"/>'
                     f'<circle cx="78" cy="25" r="4" fill="{CROWN_D}"/><circle cx="100" cy="18" r="4.5" fill="{CROWN_D}"/>'
                     f'<circle cx="122" cy="25" r="4" fill="{CROWN_D}"/></g>')
    return "".join("    " + x + "\n" for x in parts if x)

def embers():
    pts = [(30, 60, 3), (44, 132, 2.4), (166, 52, 2.6), (178, 148, 3), (24, 168, 2.2), (150, 24, 2.4)]
    out = [f'<circle cx="{x}" cy="{y}" r="{r}" fill="{FLAME_Y}" opacity="0.9"/>' for x, y, r in pts]
    return '<g id="embers">' + "".join(out) + "</g>"

def egg_svg(cracked):
    spots = ('<ellipse cx="82" cy="120" rx="9" ry="7" fill="{s}"/>'
             '<ellipse cx="122" cy="98" rx="7" ry="9" fill="{s}"/>'
             '<ellipse cx="104" cy="152" rx="8" ry="6" fill="{s}"/>'
             '<ellipse cx="76" cy="86" rx="5" ry="6" fill="{s}"/>').format(s=EGG_SPOT)
    if not cracked:
        return (f'<g id="egg"><path d="M100,34 C138,34 158,80 158,124 C158,166 132,192 100,192 '
                f'C68,192 42,166 42,124 C42,80 62,34 100,34 Z" fill="{EGG}"/>{spots}'
                f'<path d="M100,34 C76,34 60,62 54,96 C66,58 82,42 100,40 Z" fill="#ffffff" opacity="0.6"/></g>')
    # hatchling: bottom shell + peeking head + shell cap
    head = (f'<circle cx="100" cy="96" r="40" fill="{hx(GREEN_Light)}"/>'
            f'<g><ellipse cx="84" cy="92" rx="10" ry="12" fill="#ffffff"/><ellipse cx="85.5" cy="94" rx="5" ry="6.6" fill="{DARK}"/>'
            f'<circle cx="87.5" cy="90" r="2" fill="#ffffff"/></g>'
            f'<g><ellipse cx="116" cy="92" rx="10" ry="12" fill="#ffffff"/><ellipse cx="117.5" cy="94" rx="5" ry="6.6" fill="{DARK}"/>'
            f'<circle cx="119.5" cy="90" r="2" fill="#ffffff"/></g>'
            f'<ellipse cx="100" cy="112" rx="16" ry="10" fill="{hx(MUZZLE_L)}"/>'
            f'<ellipse cx="95" cy="109" rx="1.8" ry="2.4" fill="{DARK}"/><ellipse cx="105" cy="109" rx="1.8" ry="2.4" fill="{DARK}"/>'
            f'<path d="M92,117 Q100,123 108,117" fill="none" stroke="{DARK}" stroke-width="2.8" stroke-linecap="round"/>'
            f'<ellipse cx="72" cy="106" rx="6" ry="4" fill="{BLUSH}" opacity="0.55"/>'
            f'<ellipse cx="128" cy="106" rx="6" ry="4" fill="{BLUSH}" opacity="0.55"/>')
    cap = (f'<g id="shellCap" transform="rotate(-14 100 52)"><path d="M70,64 C70,42 84,30 100,30 C116,30 130,42 130,64 '
           f'L118,56 L110,66 L100,54 L90,66 L82,56 Z" fill="{EGG}"/>'
           f'<ellipse cx="112" cy="42" rx="6" ry="5" fill="{EGG_SPOT}"/></g>')
    shell = (f'<path id="shellBottom" d="M46,128 C46,168 68,192 100,192 C132,192 154,168 154,128 '
             f'L142,138 L132,124 L120,140 L110,126 L100,142 L90,126 L80,140 L68,124 L58,138 Z" fill="{EGG}"/>{spots}')
    return f'<g id="hatchling">{head}{cap}{shell}</g>'

STAGES = [
    dict(name="Egg",       kind="egg"),
    dict(name="Hatchling", kind="crack"),
    dict(name="Kid",       s=0.62, tone=0.0,  wings=0, horns=1, spikes=0, tailfin=0, tailflame=0, membrane=WING_MEMBRANE),
    dict(name="Scrapper",  s=0.70, tone=0.1,  wings=1, horns=1, spikes=0, tailfin=0, tailflame=0, membrane=WING_MEMBRANE),
    dict(name="Champion",  s=0.78, tone=0.25, wings=2, horns=1, spikes=2, tailfin=1, tailflame=0, membrane=WING_MEMBRANE),
    dict(name="Hero",      s=0.84, tone=0.4,  wings=2, horns=2, spikes=3, tailfin=1, tailflame=1, membrane=WING_MEMBRANE, fang=1),
    dict(name="Mega",      s=0.90, tone=0.55, wings=3, horns=2, spikes=3, tailfin=1, tailflame=2, membrane=WING_MEMBRANE, fang=1),
    dict(name="Ultra",     s=0.93, tone=0.7,  wings=3, horns=2, spikes=3, tailfin=1, tailflame=2, membrane=WING_MEMBRANE, fang=1,
         gloweyes=1, aura="glow"),
    dict(name="Mythic",    s=0.95, tone=0.85, wings=3, horns=2, spikes=3, tailfin=1, tailflame=3, membrane=WING_MEMBRANE_MYTHIC,
         fang=1, gloweyes=1, aura="glow", marks=1, ember=1),
    dict(name="LEGENDARY", s=0.97, tone=1.0,  wings=3, horns=2, spikes=3, tailfin=1, tailflame=3, membrane=WING_MEMBRANE_MYTHIC,
         fang=1, gloweyes=1, aura="ring", marks=1, ember=1, crown=1, goldhorns=1),
]

def build(i, st):
    inner = []
    if st.get("aura"):
        inner.append(aura(st["aura"]))
    if st["kind" ] if "kind" in st else None:
        pass
    if st.get("kind") == "egg":
        inner.append(egg_svg(False))
    elif st.get("kind") == "crack":
        inner.append(egg_svg(True))
    else:
        s = st["s"]
        inner.append(f'<g id="dragon" transform="translate(100,196) scale({s}) translate(-100,-196)">\n{creature(st)}  </g>')
    if st.get("ember"):
        inner.append(embers())
    body = "\n  ".join(inner)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>Dragon — stage {i}: {st["name"]}</title>
  {defs(st)}
  {body}
</svg>
'''

os.makedirs(OUT, exist_ok=True)
for i, st in enumerate(STAGES):
    path = os.path.join(OUT, f"stage{i}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build(i, st))
    print("wrote", os.path.normpath(path))
