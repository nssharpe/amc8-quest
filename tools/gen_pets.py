"""Generate 10-stage evolutions for the 7 non-dragon pets as Inkscape-editable SVGs.

Run from the repo root:  python tools/gen_pets.py
Writes assets/pets/<pet>/stage0.svg ... stage9.svg. The dragon line is
NOT touched (those files carry Nate's hand edits and are source of truth).

Conventions from Nate's dragon review:
 - glow eyes (stage 7+) = radial gradient pupil, black core -> colored rim
 - fang = small triangle tilted along the mouth curve; right fang at stage 5+,
   mirrored left fang at stage 7+ (species with cat-like mouths)
 - cracked-egg spots sit ON the shell pieces
"""
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets", "pets")
DARK = "#26324e"
BLUSH = "#ff9c9c"
CROWN = "#ffd21f"
CROWN_D = "#e0a80f"
FLAME_O = "#ff9f2e"
FLAME_Y = "#ffd21f"

def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))

def hx(rgb):
    return "#%02x%02x%02x" % rgb

# ---------------- shared bits ----------------

def outline_def(color, radius=2.5):
    """Nate's white-on-white fix: dilate the union silhouette into a soft outline."""
    return (f'<filter id="outline" x="-15%" y="-15%" width="130%" height="130%">'
            f'<feMorphology in="SourceAlpha" operator="dilate" radius="{radius}" result="dil"/>'
            f'<feFlood flood-color="{color}" result="col"/>'
            f'<feComposite in="col" in2="dil" operator="in" result="out"/>'
            f'<feMerge><feMergeNode in="out"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

def aura_def(inner, outer):
    return (f'<radialGradient id="auraGrad" cx="50%" cy="55%" r="50%">'
            f'<stop offset="0%" stop-color="{inner}" stop-opacity="0.5"/>'
            f'<stop offset="70%" stop-color="{outer}" stop-opacity="0.25"/>'
            f'<stop offset="100%" stop-color="{outer}" stop-opacity="0"/></radialGradient>')

def eye_grad_defs(rim, lx=80, rx=124, cy=86):
    """Nate's glow-eye gradient: black core -> colored rim, y-stretched to the pupil."""
    out = []
    for name, cx in (("eyeGradL", lx), ("eyeGradR", rx)):
        out.append(
            f'<radialGradient id="{name}" cx="{cx}" cy="{cy}" fx="{cx}" fy="{cy}" r="6.5" '
            f'gradientTransform="matrix(1,0,0,1.3076923,0,{cy - cy * 1.3076923:.6f})" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0.22" stop-color="#000000"/><stop offset="1" stop-color="{rim}"/></radialGradient>')
    return "".join(out)

def eyes(glow, lx=78, rx=122, cy=84, s=1.0):
    out = []
    for sx, name, grad in ((lx, "eyeL", "eyeGradL"), (rx, "eyeR", "eyeGradR")):
        pupil = f'url(#{grad})' if glow else DARK
        out.append(f'<g id="{name}"><ellipse cx="{sx}" cy="{cy}" rx="{13*s:.1f}" ry="{15*s:.1f}" fill="#ffffff"/>'
                   f'<ellipse cx="{sx + 2}" cy="{cy + 2}" rx="{6.5*s:.1f}" ry="{8.5*s:.1f}" fill="{pupil}"/>'
                   f'<circle cx="{sx + 4.5}" cy="{cy - 2}" r="{2.6*s:.1f}" fill="#ffffff"/></g>')
    return "".join(out)

def cheeks(y=104, lx=62, rx=138):
    return (f'<ellipse id="cheekL" cx="{lx}" cy="{y}" rx="8" ry="5" fill="{BLUSH}" opacity="0.55"/>'
            f'<ellipse id="cheekR" cx="{rx}" cy="{y}" rx="8" ry="5" fill="{BLUSH}" opacity="0.55"/>')

def fangs(stage, base_y=125):
    """Nate's tilted fangs: right at 5+, left mirrored at 7+."""
    out = []
    if stage >= 5:
        out.append(f'<path id="fangR" d="m 105.37,{base_y} 6.30,4.28 0.14,-7.21 z" fill="#ffffff"/>')
    if stage >= 7:
        out.append(f'<path id="fangL" d="m 94.17,{base_y - 0.5} -6.30,4.28 -0.14,-7.21 z" fill="#ffffff"/>')
    return "".join(out)

def crown(ytop=40):
    return (f'<g id="crown" transform="rotate(-8 100 {ytop})">'
            f'<path d="M78,{ytop+4} L78,{ytop-14} L88,{ytop-4} L100,{ytop-20} L112,{ytop-4} L122,{ytop-14} L122,{ytop+4} Z" fill="{CROWN}"/>'
            f'<rect x="78" y="{ytop+2}" width="44" height="7" rx="3" fill="{CROWN_D}"/>'
            f'<circle cx="78" cy="{ytop-15}" r="4" fill="{CROWN_D}"/><circle cx="100" cy="{ytop-22}" r="4.5" fill="{CROWN_D}"/>'
            f'<circle cx="122" cy="{ytop-15}" r="4" fill="{CROWN_D}"/></g>')

def particle(kind, s=1.0):
    if kind == "flame":
        return (f'<g transform="scale({s})"><path d="M0,8 C-6,2 -5,-6 0,-12 C5,-6 6,2 0,8 Z" fill="{FLAME_O}"/>'
                f'<path d="M0,5 C-3,1 -2,-3 0,-7 C2,-3 3,1 0,5 Z" fill="{FLAME_Y}"/></g>')
    if kind == "star":
        return (f'<path transform="scale({s})" d="M0,-9 L2.4,-2.4 L9,0 L2.4,2.4 L0,9 L-2.4,2.4 L-9,0 L-2.4,-2.4 Z" fill="{FLAME_Y}"/>')
    if kind == "snow":
        p = []
        for k in range(3):
            a = k * 60
            p.append(f'<rect x="-1.2" y="-8" width="2.4" height="16" rx="1.2" transform="rotate({a})" fill="#cfeeff"/>')
        return f'<g transform="scale({s})">{"".join(p)}</g>'
    if kind == "bubble":
        return (f'<g transform="scale({s})"><circle r="7" fill="none" stroke="#9fdcf5" stroke-width="2.4"/>'
                f'<circle cx="-2.4" cy="-2.4" r="1.6" fill="#ffffff"/></g>')
    return ""

def ring(kind):
    out = []
    for i in range(10):
        ang = math.pi * 2 * i / 10 - math.pi / 2
        x = 100 + 90 * math.cos(ang)
        y = 112 + 84 * math.sin(ang)
        out.append(f'<g transform="translate({x:.0f},{y:.0f})">{particle(kind, 1 if i % 2 == 0 else 0.7)}</g>')
    return '<g id="ring">' + "".join(out) + "</g>"

def embers(kind, col=None):
    pts = [(30, 60, 1.0), (44, 132, 0.8), (166, 52, 0.85), (178, 148, 1.0), (24, 168, 0.7), (150, 24, 0.8)]
    out = [f'<g transform="translate({x},{y})">{particle(kind, s * 0.55)}</g>' for x, y, s in pts]
    return '<g id="embers">' + "".join(out) + "</g>"

def aura_circle():
    return '<circle id="aura" cx="100" cy="112" r="88" fill="url(#auraGrad)"/>'

def egg_pair(base, spot, peek_head, ice=None):
    """Returns (stage0_svg, stage1_svg). Spots ride the shell pieces (Nate's rule)."""
    stage0 = (f'<g id="egg">{ice or ""}<path d="M100,34 C138,34 158,80 158,124 C158,166 132,192 100,192 '
              f'C68,192 42,166 42,124 C42,80 62,34 100,34 Z" fill="{base}"/>'
              f'<ellipse cx="82" cy="120" rx="9" ry="7" fill="{spot}"/>'
              f'<ellipse cx="122" cy="98" rx="7" ry="9" fill="{spot}"/>'
              f'<ellipse cx="104" cy="152" rx="8" ry="6" fill="{spot}"/>'
              f'<ellipse cx="76" cy="86" rx="5" ry="6" fill="{spot}"/>'
              f'<path d="M100,34 C76,34 60,62 54,96 C66,58 82,42 100,40 Z" fill="#ffffff" opacity="0.6"/></g>')
    cap = (f'<g id="shellCap" transform="rotate(-14 100 52)"><path d="M70,64 C70,42 84,30 100,30 C116,30 130,42 130,64 '
           f'L118,56 L110,66 L100,54 L90,66 L82,56 Z" fill="{base}"/>'
           f'<ellipse cx="112" cy="44" rx="6" ry="5" fill="{spot}"/><ellipse cx="86" cy="48" rx="4" ry="3.5" fill="{spot}"/></g>')
    shell = (f'<path id="shellBottom" d="M46,128 C46,168 68,192 100,192 C132,192 154,168 154,128 '
             f'L142,138 L132,124 L120,140 L110,126 L100,142 L90,126 L80,140 L68,124 L58,138 Z" fill="{base}"/>'
             f'<ellipse cx="80" cy="164" rx="8" ry="6" fill="{spot}"/>'
             f'<ellipse cx="118" cy="158" rx="7" ry="6" fill="{spot}"/>'
             f'<ellipse cx="100" cy="178" rx="6" ry="5" fill="{spot}"/>')
    stage1 = f'<g id="hatchling">{ice or ""}{peek_head}{cap}{shell}</g>'
    return stage0, stage1

def peek_face(body, muzzle, extras=""):
    """Generic peeking baby head used inside the cracked egg."""
    return (f'<circle cx="100" cy="96" r="40" fill="{body}"/>{extras}'
            f'<g><ellipse cx="84" cy="92" rx="10" ry="12" fill="#ffffff"/><ellipse cx="85.5" cy="94" rx="5" ry="6.6" fill="{DARK}"/>'
            f'<circle cx="87.5" cy="90" r="2" fill="#ffffff"/></g>'
            f'<g><ellipse cx="116" cy="92" rx="10" ry="12" fill="#ffffff"/><ellipse cx="117.5" cy="94" rx="5" ry="6.6" fill="{DARK}"/>'
            f'<circle cx="119.5" cy="90" r="2" fill="#ffffff"/></g>'
            f'{muzzle}'
            f'<ellipse cx="72" cy="106" rx="6" ry="4" fill="{BLUSH}" opacity="0.55"/>'
            f'<ellipse cx="128" cy="106" rx="6" ry="4" fill="{BLUSH}" opacity="0.55"/>')

def wrap(inner, title, scale=None):
    if scale:
        inner = f'<g id="pet" transform="translate(100,196) scale({scale}) translate(-100,-196)">{inner}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n'
            f'  <title>{title}</title>\n  {inner}\n</svg>\n')

# scale per growth stage (index 2..9)
SCALES = {2: 0.62, 3: 0.70, 4: 0.78, 5: 0.84, 6: 0.90, 7: 0.93, 8: 0.95, 9: 0.97}
def tone(i):  # 0..1 color deepening across growth stages
    return {2: 0.0, 3: 0.1, 4: 0.25, 5: 0.4, 6: 0.55, 7: 0.7, 8: 0.85, 9: 1.0}[i]

# ================= species builders (stage index i in 2..9) =================

def unicorn(i):
    body = "#fdfaf3"
    hoof = "#d8c8ea"
    mane = hx(lerp((255, 156, 224), (178, 139, 255), tone(i)))
    parts = []
    # tail
    if i >= 3:
        parts.append(f'<path id="tail" d="M140,160 C166,156 176,138 172,118 C186,132 184,158 168,170 C158,177 146,177 140,172 Z" fill="{mane}"/>')
    # legs
    parts.append(f'<ellipse id="footL" cx="76" cy="186" rx="15" ry="11" fill="{hoof}"/>')
    parts.append(f'<ellipse id="footR" cx="124" cy="186" rx="15" ry="11" fill="{hoof}"/>')
    parts.append(f'<ellipse id="body" cx="100" cy="150" rx="45" ry="39" fill="{body}"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="158" rx="28" ry="26" fill="#f6ecdd"/>')
    # ears
    parts.append(f'<path id="earL" d="M62,56 C58,40 64,30 74,26 C80,36 80,48 74,58 Z" fill="{body}"/>'
                 f'<path d="M66,52 C64,42 68,35 73,32 C76,39 76,47 72,53 Z" fill="{BLUSH}" opacity="0.6"/>')
    parts.append(f'<path id="earR" d="M138,56 C142,40 136,30 126,26 C120,36 120,48 126,58 Z" fill="{body}"/>'
                 f'<path d="M134,52 C136,42 132,35 127,32 C124,39 124,47 128,53 Z" fill="{BLUSH}" opacity="0.6"/>')
    parts.append(f'<circle id="head" cx="100" cy="92" r="52" fill="{body}"/>')
    # mane: scallops over the top-left of the head, grows with stage
    if i >= 2:
        n = min(3 + (i - 2), 6)
        if i >= 8:  # rainbow
            cols = ["#ff5f7a", "#ff9f2e", "#ffd21f", "#3ddc97", "#4cc9f0", "#b28bff"]
        else:
            cols = [mane] * 6
        sc = []
        for k in range(n):
            a = math.pi * (0.95 - 0.13 * k)
            x = 100 + 54 * math.cos(a)
            y = 92 - 54 * math.sin(a)
            sc.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{13 + (2 if k % 2 else 0)}" fill="{cols[k % len(cols)]}"/>')
        parts.append('<g id="mane">' + "".join(sc) + "</g>")
    # horn — base sits below the mane scallops; LEGENDARY tip clears the crown
    if i >= 3:
        hl = {3: 26, 4: 34, 5: 40, 6: 46, 7: 50, 8: 54, 9: 60}[i]
        hcol = CROWN if i >= 7 else "#f2e3b8"
        parts.append(f'<path id="horn" d="M93,62 L100,{62 - hl} L107,62 Z" fill="{hcol}"/>'
                     f'<path d="M95,{62 - hl * 0.3:.0f} L105,{62 - hl * 0.5:.0f}" stroke="{CROWN_D}" stroke-width="2"/>'
                     f'<path d="M94,{62 - hl * 0.55:.0f} L104,{62 - hl * 0.75:.0f}" stroke="{CROWN_D}" stroke-width="2"/>')
    if i >= 8:
        parts.append(f'<g id="marks" fill="{mane}" opacity="0.7"><path d="M58,140 l2.5,5 5,0.7 -3.6,3.6 0.9,5 -4.8,-2.5 -4.8,2.5 0.9,-5 -3.6,-3.6 5,-0.7 Z"/>'
                     f'<path d="M142,138 l2.5,5 5,0.7 -3.6,3.6 0.9,5 -4.8,-2.5 -4.8,2.5 0.9,-5 -3.6,-3.6 5,-0.7 Z"/></g>')
    # face
    parts.append(f'<ellipse id="muzzle" cx="100" cy="116" rx="24" ry="16" fill="#f9e9f2"/>')
    parts.append(f'<ellipse cx="93" cy="112" rx="2.2" ry="3" fill="{DARK}"/><ellipse cx="107" cy="112" rx="2.2" ry="3" fill="{DARK}"/>')
    parts.append(f'<path id="mouth" d="M90,123 Q100,130 110,123" fill="none" stroke="{DARK}" stroke-width="3.2" stroke-linecap="round"/>')
    parts.append(eyes(i >= 7))
    parts.append(cheeks())
    if i >= 9:
        parts.append(crown(34))
    return "".join(parts)

def robot(i):
    metal = hx(lerp((176, 188, 210), (124, 136, 160), tone(i)))
    metal_d = hx(lerp((124, 136, 160), (88, 100, 124), tone(i)))
    trim = CROWN if i >= 8 else metal_d
    parts = []
    if i >= 7:  # jet flames under the treads
        for x in (74, 126):
            parts.append(f'<g id="jet{x}" transform="translate({x},193)">{particle("flame", 0.8)}</g>')
    # treads
    parts.append(f'<rect id="footL" x="58" y="176" width="34" height="18" rx="9" fill="{metal_d}"/>')
    parts.append(f'<rect id="footR" x="108" y="176" width="34" height="18" rx="9" fill="{metal_d}"/>')
    # arms
    if i >= 3:
        parts.append(f'<rect id="armL" x="44" y="126" width="16" height="34" rx="8" transform="rotate(14 52 143)" fill="{metal_d}"/>')
        parts.append(f'<rect id="armR" x="140" y="126" width="16" height="34" rx="8" transform="rotate(-14 148 143)" fill="{metal_d}"/>')
    # torso
    parts.append(f'<rect id="torso" x="70" y="118" width="60" height="62" rx="16" fill="{metal}"/>')
    if i >= 4:
        parts.append(f'<rect id="chest" x="84" y="132" width="32" height="24" rx="6" fill="{DARK}"/>'
                     f'<path d="M100,151 C96,147 92,143 92,140 C92,136 96,135 100,139 C104,135 108,136 108,140 C108,143 104,147 100,151 Z" fill="#3ddc97"/>')
    if i >= 5:
        parts.append(f'<rect id="shoulderL" x="60" y="116" width="18" height="12" rx="6" fill="{trim}"/>'
                     f'<rect id="shoulderR" x="122" y="116" width="18" height="12" rx="6" fill="{trim}"/>')
    # head
    parts.append(f'<rect id="head" x="60" y="48" width="80" height="70" rx="20" fill="{metal}"/>')
    parts.append(f'<rect id="facePlate" x="68" y="60" width="64" height="48" rx="14" fill="#e8edf5"/>')
    # ear bolts
    parts.append(f'<circle id="boltL" cx="58" cy="84" r="7" fill="{trim}"/><circle id="boltR" cx="142" cy="84" r="7" fill="{trim}"/>')
    # antenna
    ab = CROWN if i >= 7 else BLUSH
    parts.append(f'<rect id="antennaStem" x="97.5" y="30" width="5" height="20" rx="2.5" fill="{metal_d}"/>'
                 f'<circle id="antennaBall" cx="100" cy="26" r="7" fill="{ab}"/>')
    if i >= 6:
        parts.append(f'<path id="finL" d="M60,58 L46,50 L48,66 L60,68 Z" fill="{trim}"/>'
                     f'<path id="finR" d="M140,58 L154,50 L152,66 L140,68 Z" fill="{trim}"/>')
    # face
    parts.append(eyes(i >= 7, lx=82, rx=118, cy=82, s=0.9))
    parts.append(f'<path id="mouth" d="M88,98 Q100,105 112,98" fill="none" stroke="{DARK}" stroke-width="3.2" stroke-linecap="round"/>')
    parts.append(cheeks(y=96, lx=72, rx=128))
    if i >= 9:
        parts.append(crown(30))
    return "".join(parts)

def cat(i):
    body = hx(lerp((245, 172, 106), (224, 123, 40), tone(i)))
    stripe = hx(lerp((201, 116, 46), (168, 88, 26), tone(i)))
    parts = []
    # tail
    parts.append(f'<path id="tail" d="M136,168 C164,168 176,150 172,128 C182,144 182,168 164,178 C154,183 142,182 136,177 Z" fill="{body}"/>')
    if i >= 4:
        parts.append(f'<path d="M168,136 C172,143 173,150 171,156 L163,151 C166,147 168,141 168,136 Z" fill="{stripe}"/>')
    parts.append(f'<ellipse id="footL" cx="76" cy="187" rx="15" ry="10" fill="{body}"/>')
    parts.append(f'<ellipse id="footR" cx="124" cy="187" rx="15" ry="10" fill="{body}"/>')
    parts.append(f'<ellipse id="body" cx="100" cy="150" rx="44" ry="38" fill="{body}"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="158" rx="27" ry="25" fill="#f6ecc3"/>')
    parts.append(f'<ellipse id="armL" cx="63" cy="146" rx="10" ry="15" transform="rotate(18 63 146)" fill="{stripe}"/>')
    parts.append(f'<ellipse id="armR" cx="137" cy="146" rx="10" ry="15" transform="rotate(-18 137 146)" fill="{stripe}"/>')
    # lion mane behind head at 8+
    if i >= 8:
        spikes_ = []
        for k in range(12):
            a = math.pi * 2 * k / 12
            x1, y1 = 100 + 46 * math.cos(a), 90 + 46 * math.sin(a)
            x2, y2 = 100 + 68 * math.cos(a + 0.26), 90 + 68 * math.sin(a + 0.26)
            x3, y3 = 100 + 46 * math.cos(a + 0.52), 90 + 46 * math.sin(a + 0.52)
            spikes_.append(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f} L{x3:.0f},{y3:.0f} Z" fill="{stripe}"/>')
        parts.append('<g id="mane">' + "".join(spikes_) + "</g>")
    # ears
    parts.append(f'<path id="earL" d="M60,64 L54,28 L88,46 Z" fill="{body}"/><path d="M64,58 L60,38 L79,48 Z" fill="{BLUSH}" opacity="0.7"/>')
    parts.append(f'<path id="earR" d="M140,64 L146,28 L112,46 Z" fill="{body}"/><path d="M136,58 L140,38 L121,48 Z" fill="{BLUSH}" opacity="0.7"/>')
    parts.append(f'<circle id="head" cx="100" cy="92" r="52" fill="{body}"/>')
    # head stripes
    if i >= 4:
        parts.append(f'<g id="stripes" fill="{stripe}"><path d="M92,42 C94,50 94,56 92,62 L98,62 C99,55 99,48 98,42 Z"/>'
                     f'<path d="M104,41 C106,49 106,55 104,61 L110,61 C111,54 111,47 110,41 Z" transform="rotate(8 107 51)"/>'
                     f'<path d="M80,44 C82,50 82,55 80,60 L86,60 C87,54 87,49 86,44 Z" transform="rotate(-8 83 52)"/></g>')
    # muzzle
    parts.append(f'<ellipse id="muzzle" cx="100" cy="116" rx="24" ry="16" fill="#fdf6e4"/>')
    parts.append(f'<path id="nose" d="M95,108 L105,108 L100,115 Z" fill="{BLUSH}"/>')
    parts.append(f'<path id="philtrum" d="M100,115 L100,119" fill="none" stroke="{DARK}" stroke-width="2.6" stroke-linecap="round"/>')
    parts.append(f'<path id="mouth" d="M89,119 Q100,128 111,119" fill="none" stroke="{DARK}" stroke-width="3" stroke-linecap="round"/>')
    parts.append(fangs(i, base_y=124.5))
    # whiskers
    if i >= 3:
        parts.append(f'<g id="whiskers" stroke="{DARK}" stroke-width="2" stroke-linecap="round" opacity="0.75">'
                     f'<path d="M60,108 L40,104" fill="none"/><path d="M60,114 L40,116" fill="none"/>'
                     f'<path d="M140,108 L160,104" fill="none"/><path d="M140,114 L160,116" fill="none"/></g>')
    parts.append(eyes(i >= 7))
    parts.append(cheeks())
    if i >= 9:
        parts.append(crown(34))
    return "".join(parts)

def fox(i):
    body = hx(lerp((255, 154, 77), (229, 112, 31), tone(i)))
    dark = hx(lerp((229, 112, 31), (190, 84, 18), tone(i)))
    parts = []
    # extra kitsune tails at 8+
    tailflame = i >= 6
    def one_tail(dx, rot, idn):
        tf = (f'<path d="M{168+dx},98 C{162+dx},90 {164+dx},80 {172+dx},74 C{180+dx},80 {182+dx},90 {176+dx},98 Z" fill="#b28bff"/>' if tailflame else "")
        return (f'<g id="{idn}" transform="rotate({rot} 140 170)">'
                f'<path d="M136,170 C160,168 174,148 172,120 C172,110 176,104 172,98 C186,118 188,152 168,172 C156,183 142,182 136,177 Z" fill="{body}"/>'
                f'<path d="M172,98 C178,108 180,118 178,128 C170,122 168,112 168,104 Z" fill="#ffffff"/>{tf}</g>')
    if i >= 8:
        parts.append(one_tail(0, 17, "tail3"))
        parts.append(one_tail(0, -18, "tail2"))
    parts.append(one_tail(0, 4, "tail"))
    parts.append(f'<ellipse id="footL" cx="76" cy="187" rx="15" ry="10" fill="{dark}"/>')
    parts.append(f'<ellipse id="footR" cx="124" cy="187" rx="15" ry="10" fill="{dark}"/>')
    parts.append(f'<ellipse id="body" cx="100" cy="150" rx="44" ry="38" fill="{body}"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="158" rx="27" ry="25" fill="#fff4e4"/>')
    parts.append(f'<ellipse id="armL" cx="63" cy="146" rx="10" ry="15" transform="rotate(18 63 146)" fill="{dark}"/>')
    parts.append(f'<ellipse id="armR" cx="137" cy="146" rx="10" ry="15" transform="rotate(-18 137 146)" fill="{dark}"/>')
    # big pointy ears w/ dark tips
    tip = CROWN if i >= 9 else dark
    parts.append(f'<path id="earL" d="M58,70 L48,20 L92,44 Z" fill="{body}"/><path d="M55,52 L48,20 L68,31 Z" fill="{tip}"/>')
    parts.append(f'<path id="earR" d="M142,70 L152,20 L108,44 Z" fill="{body}"/><path d="M145,52 L152,20 L132,31 Z" fill="{tip}"/>')
    parts.append(f'<circle id="head" cx="100" cy="94" r="50" fill="{body}"/>')
    # cheek fluff
    if i >= 4:
        parts.append(f'<path id="fluffL" d="M52,96 L34,90 L50,106 L36,108 L54,116 Z" fill="{body}"/>')
        parts.append(f'<path id="fluffR" d="M148,96 L166,90 L150,106 L164,108 L146,116 Z" fill="{body}"/>')
    # white muzzle patch
    parts.append(f'<path id="muzzle" d="M74,110 C74,96 88,92 100,92 C112,92 126,96 126,110 C126,126 112,134 100,134 C88,134 74,126 74,110 Z" fill="#fff4e4"/>')
    parts.append(f'<path id="nose" d="M95,108 L105,108 L100,115 Z" fill="{DARK}"/>')
    parts.append(f'<path id="philtrum" d="M100,115 L100,119" fill="none" stroke="{DARK}" stroke-width="2.6" stroke-linecap="round"/>')
    parts.append(f'<path id="mouth" d="M89,119 Q100,128 111,119" fill="none" stroke="{DARK}" stroke-width="3" stroke-linecap="round"/>')
    parts.append(fangs(i, base_y=124.5))
    parts.append(eyes(i >= 7))
    parts.append(cheeks(y=106, lx=64, rx=136))
    if i >= 9:
        parts.append(crown(30))
    return "".join(parts)

def shark(i):
    body = hx(lerp((127, 168, 200), (74, 122, 158), tone(i)))
    dark = hx(lerp((94, 136, 168), (54, 96, 128), tone(i)))
    parts = []
    # floats on bubbles
    parts.append(f'<ellipse id="water" cx="100" cy="188" rx="52" ry="8" fill="#4cc9f0" opacity="0.35"/>')
    parts.append(f'<g id="floatBubbles">'
                 f'<circle cx="72" cy="182" r="6" fill="none" stroke="#9fdcf5" stroke-width="2"/>'
                 f'<circle cx="104" cy="186" r="4.5" fill="none" stroke="#9fdcf5" stroke-width="2"/>'
                 f'<circle cx="130" cy="181" r="5.5" fill="none" stroke="#9fdcf5" stroke-width="2"/></g>')
    # tail fin (right)
    if i >= 4:
        parts.append(f'<path id="tailFin" d="M146,130 C162,118 166,102 160,88 C170,94 178,108 174,124 C186,120 192,126 192,134 C184,134 176,138 172,144 C160,152 148,146 146,138 Z" fill="{dark}"/>')
    # dorsal fin
    if i >= 3:
        ds = {3: 0.7, 4: 0.85, 5: 1.0, 6: 1.1, 7: 1.15, 8: 1.2, 9: 1.25}[i]
        tipcol = CROWN if i >= 9 else dark
        parts.append(f'<g id="dorsal" transform="translate(100,84) scale({ds}) translate(-100,-84)">'
                     f'<path d="M82,84 C80,50 90,30 106,20 C102,38 108,54 120,66 L114,84 Z" fill="{tipcol}"/></g>')
    # body (one big blob, face on body)
    parts.append(f'<path id="body" d="M42,124 C42,90 68,64 100,64 C132,64 158,90 158,124 C158,152 132,172 100,172 C68,172 42,152 42,124 Z" fill="{body}"/>')
    parts.append(f'<path id="belly" d="M54,138 C64,156 82,166 100,166 C118,166 136,156 146,138 C132,148 116,153 100,153 C84,153 68,148 54,138 Z" fill="#eaf6fb"/>')
    # side fins
    if i >= 4:
        parts.append(f'<path id="finL" d="M48,132 C34,138 26,148 26,158 C38,156 48,150 56,142 Z" fill="{dark}"/>')
        parts.append(f'<path id="finR" d="M152,132 C166,138 174,148 174,158 C162,156 152,150 144,142 Z" fill="{dark}"/>')
    # gills
    if i >= 5:
        g = []
        for k, x in enumerate((58, 66, 74)):
            g.append(f'<path d="M{x},108 C{x - 2},114 {x - 2},120 {x},126" fill="none" stroke="{dark}" stroke-width="2.6" stroke-linecap="round"/>')
        parts.append('<g id="gillsL">' + "".join(g) + "</g>")
    # mouth: wide arc with teeth
    parts.append(f'<path id="mouth" d="M76,132 Q100,146 124,132" fill="none" stroke="{DARK}" stroke-width="3.5" stroke-linecap="round"/>')
    if i >= 5:
        teeth = []
        for x, y, r in ((84, 135.5, -16), (95, 139.5, -6), (106, 139.2, 8), (117, 134.5, 17)):
            teeth.append(f'<path transform="rotate({r} {x} {y})" d="M{x - 4},{y} L{x + 4},{y} L{x},{y + 7} Z" fill="#ffffff"/>')
        parts.append('<g id="teeth">' + "".join(teeth) + "</g>")
    parts.append(f'<ellipse cx="90" cy="120" rx="2.2" ry="3" fill="{DARK}"/><ellipse cx="110" cy="120" rx="2.2" ry="3" fill="{DARK}"/>')
    if i >= 8:
        parts.append(f'<g id="marks" fill="#eaf6fb" opacity="0.9"><path d="M64,84 l2.2,4.4 4.4,0.6 -3.2,3.2 0.8,4.4 -4.2,-2.2 -4.2,2.2 0.8,-4.4 -3.2,-3.2 4.4,-0.6 Z"/>'
                     f'<path d="M134,82 l2.2,4.4 4.4,0.6 -3.2,3.2 0.8,4.4 -4.2,-2.2 -4.2,2.2 0.8,-4.4 -3.2,-3.2 4.4,-0.6 Z"/></g>')
    parts.append(eyes(i >= 7, lx=80, rx=120, cy=102))
    parts.append(cheeks(y=118, lx=66, rx=134))
    if i >= 9:
        parts.append(crown(36))
    return "".join(parts)

def dino(i):
    """Triceratops — blue-slate, neck frill, brow + nose horns (distinct from dragon)."""
    body = hx(lerp((138, 168, 216), (85, 120, 184), tone(i)))
    dark = hx(lerp((104, 134, 186), (60, 92, 150), tone(i)))
    frill = hx(lerp((96, 122, 176), (52, 80, 136), tone(i)))
    scallop = FLAME_Y if i >= 8 else FLAME_O
    horncol = CROWN if i >= 9 else "#f2e3b8"
    parts = []
    parts.append(f'<path id="tail" d="M118,166 C148,170 168,158 174,136 C176,124 170,114 162,112 C166,126 158,142 144,150 C134,156 124,158 116,156 Z" fill="{body}"/>')
    parts.append(f'<ellipse id="footL" cx="74" cy="186" rx="17" ry="11" fill="{dark}"/>')
    parts.append(f'<ellipse id="footR" cx="126" cy="186" rx="17" ry="11" fill="{dark}"/>')
    # neck frill: ring of overlapping petals (scalloped edge), spikes at the
    # junctions, dots ON the frill face — per Nate's reference art
    if i >= 3:
        fs = {3: 0.72, 4: 0.82, 5: 0.9, 6: 1.0, 7: 1.05, 8: 1.08, 9: 1.1}[i]
        petals, spikes_, dots = [], [], []
        for k in range(7):
            th = math.radians(195 - k * 35)
            px_, py_ = 100 + 52 * math.cos(th), 90 - 52 * math.sin(th)
            petals.append(f'<circle cx="{px_:.0f}" cy="{py_:.0f}" r="19" fill="{frill}"/>')
            if k < 6:
                tj = math.radians(195 - k * 35 - 17.5)
                sx_, sy_ = 100 + 63 * math.cos(tj), 90 - 63 * math.sin(tj)
                rot = 90 - math.degrees(tj)
                spikes_.append(f'<g transform="translate({sx_:.0f},{sy_:.0f}) rotate({rot:.0f})">'
                               f'<path d="M-6,2 L0,-13 L6,2 Z" fill="{frill}"/></g>')
                dx_, dy_ = 100 + 58 * math.cos(tj), 90 - 58 * math.sin(tj)
                dots.append(f'<circle cx="{dx_:.0f}" cy="{dy_:.0f}" r="4" fill="{scallop}"/>')
        parts.append(f'<g id="frill" transform="translate(100,90) scale({fs}) translate(-100,-90)">'
                     + "".join(spikes_) + "".join(petals) + "".join(dots) + '</g>')
    parts.append(f'<ellipse id="body" cx="100" cy="150" rx="46" ry="40" fill="{body}"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="158" rx="29" ry="27" fill="#f2ecc8"/>')
    parts.append(f'<circle cx="63" cy="144" r="4.5" fill="{dark}" id="bodyDotL"/>'
                 f'<circle cx="137" cy="144" r="4.5" fill="{dark}" id="bodyDotR"/>')
    if i >= 9:  # lava cracks
        parts.append(f'<g id="lava" stroke="{FLAME_O}" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.9">'
                     f'<path d="M62,142 L70,148 L66,156"/><path d="M138,140 L131,148 L136,156"/></g>')
    parts.append(f'<ellipse id="armL" cx="64" cy="146" rx="9" ry="13" transform="rotate(22 64 146)" fill="{dark}"/>')
    parts.append(f'<ellipse id="armR" cx="136" cy="146" rx="9" ry="13" transform="rotate(-22 136 146)" fill="{dark}"/>')
    parts.append(f'<circle id="head" cx="100" cy="92" r="50" fill="{body}"/>')
    # brow horns — Nate's stage-9 design (rooted at the outer brow, sweeping
    # up-and-outward to sharp tips), scaled for earlier stages about the roots
    if i >= 4:
        hs = {4: 0.7, 5: 0.85, 6: 1.0, 7: 1.1, 8: 1.15, 9: 1.2}[i] / 1.2
        parts.append(f'<g id="hornL" transform="translate(73,62) scale({hs:.4f}) translate(-73,-62)">'
                     f'<path d="M67.0,66.0 C63.8,66.8 56.7,39.1 59.9,24.5 C65.6,35.8 83.5,59.5 78.2,61.7 Z" fill="{horncol}"/></g>')
        parts.append(f'<g id="hornR" transform="translate(127,62) scale({hs:.4f}) translate(-127,-62)">'
                     f'<path d="M133.0,66.0 C136.2,66.8 143.3,39.1 140.1,24.5 C134.4,35.8 116.5,59.5 121.8,61.7 Z" fill="{horncol}"/></g>')
    # snout + nose horn
    parts.append(f'<ellipse id="muzzle" cx="100" cy="116" rx="28" ry="18" fill="{hx(lerp((176, 200, 236), (124, 154, 208), tone(i) * 0.6))}"/>')
    if i >= 5:
        parts.append(f'<path id="noseHorn" d="M92,106 C92,96 96,90 100,90 C104,90 108,96 108,106 C104,109 96,109 92,106 Z" fill="{horncol}"/>')
    parts.append(f'<ellipse cx="90" cy="112" rx="2.6" ry="3.4" fill="{DARK}"/><ellipse cx="110" cy="112" rx="2.6" ry="3.4" fill="{DARK}"/>')
    parts.append(f'<path id="mouth" d="M86,124 Q100,132 114,124" fill="none" stroke="{DARK}" stroke-width="3.5" stroke-linecap="round"/>')
    parts.append(eyes(i >= 7))
    parts.append(cheeks())
    if i >= 9:
        parts.append(crown(22))
    return "".join(parts)

def penguin(i):
    if i == 2:  # fluffy gray chick
        body = "#9aa4b8"
    else:
        body = hx(lerp((70, 80, 104), (38, 50, 78), tone(i)))
    orange = "#ff9f2e" if i < 9 else CROWN
    parts = []
    # ice puddle
    parts.append(f'<ellipse id="ice" cx="100" cy="190" rx="54" ry="7" fill="#bfe6ff" opacity="0.6"/>')
    # feet
    parts.append(f'<ellipse id="footL" cx="80" cy="190" rx="14" ry="7" fill="{orange}"/>')
    parts.append(f'<ellipse id="footR" cx="120" cy="190" rx="14" ry="7" fill="{orange}"/>')
    # one-blob body
    parts.append(f'<path id="body" d="M100,28 C140,28 158,70 158,124 C158,164 134,190 100,190 C66,190 42,164 42,124 C42,70 60,28 100,28 Z" fill="{body}"/>')
    # flippers
    if i >= 4:
        parts.append(f'<path id="flipperL" d="M46,110 C30,124 26,146 34,164 C44,156 50,140 52,124 Z" fill="{body}"/>')
        parts.append(f'<path id="flipperR" d="M154,110 C170,124 174,146 166,164 C156,156 150,140 148,124 Z" fill="{body}"/>')
    # face + belly patch
    parts.append(f'<path id="facePatch" d="M100,44 C126,44 140,66 140,92 C140,104 132,112 100,112 C68,112 60,104 60,92 C60,66 74,44 100,44 Z" fill="#f2f7fb"/>')
    parts.append(f'<ellipse id="belly" cx="100" cy="150" rx="34" ry="36" fill="#f2f7fb"/>')
    # beak: rounded upper + smaller lower lobe with a smiling seam (per Nate's reference)
    parts.append(f'<g id="beak"><path d="M86,96 C90,87 110,87 114,96 C112,102 104,105 100,105 C96,105 88,102 86,96 Z" fill="{orange}"/>'
                 f'<path d="M91,102 C95,108 105,108 109,102 C106,110 94,110 91,102 Z" fill="{orange}"/>'
                 f'<path d="M87,97 Q100,104 113,97" fill="none" stroke="#c97a14" stroke-width="2" stroke-linecap="round"/></g>')
    if i >= 8:
        parts.append(f'<g id="marks" fill="#cfeeff"><circle cx="70" cy="130" r="3"/><circle cx="130" cy="130" r="3"/></g>')
    parts.append(eyes(i >= 7, lx=82, rx=118, cy=78, s=0.9))
    parts.append(cheeks(y=94, lx=70, rx=130))
    if i >= 9:
        parts.append(crown(26))
    return "".join(parts)

# ================= species configs =================

SPECIES = {
    "unicorn": dict(builder=unicorn, egg=("#fdfaf3", "#ffc4ec"), peek_body="#fdfaf3",
                    peek_muzzle=f'<ellipse cx="100" cy="112" rx="14" ry="9" fill="#f9e9f2"/>'
                                f'<ellipse cx="95" cy="109" rx="1.6" ry="2.2" fill="{DARK}"/><ellipse cx="105" cy="109" rx="1.6" ry="2.2" fill="{DARK}"/>'
                                f'<path d="M92,117 Q100,123 108,117" fill="none" stroke="{DARK}" stroke-width="2.8" stroke-linecap="round"/>',
                    peek_extra=f'<path d="M95,60 L100,42 L105,60 Z" fill="#f2e3b8"/>',
                    aura=("#ffd7f5", "#b28bff"), ember="star", ring="star", eye_rim="#b28bff", outline="#b28bff"),
    "robot": dict(builder=robot, egg="box", peek_body="#b0bcd2",
                  peek_muzzle=f'<path d="M92,112 Q100,118 108,112" fill="none" stroke="{DARK}" stroke-width="2.8" stroke-linecap="round"/>',
                  peek_extra=f'<rect x="97" y="40" width="4" height="16" rx="2" fill="#7c88a0"/><circle cx="99" cy="36" r="5" fill="{BLUSH}"/>',
                  aura=("#ffd21f", "#ff9f2e"), ember="star", ring="flame", pupils=(84, 120, 84), eye_rim="#3ddc97"),
    "cat": dict(builder=cat, egg=("#fdf6e4", "#f5c98a"), peek_body="#f5ac6a",
                peek_muzzle=f'<ellipse cx="100" cy="113" rx="13" ry="8" fill="#fdf6e4"/>'
                            f'<path d="M96,106 L104,106 L100,111 Z" fill="{BLUSH}"/>'
                            f'<path d="M100,111 Q100,116 95,117 M100,111 Q100,116 105,117" fill="none" stroke="{DARK}" stroke-width="2.4" stroke-linecap="round"/>',
                peek_extra=f'<path d="M74,68 L70,46 L92,58 Z" fill="#f5ac6a"/><path d="M126,68 L130,46 L108,58 Z" fill="#f5ac6a"/>',
                aura=("#ffd21f", "#ff9f2e"), ember="star", ring="star", eye_rim="#ffbf1f"),
    "fox": dict(builder=fox, egg=("#fff4e4", "#ffbe8c"), peek_body="#ff9a4d",
                peek_muzzle=f'<ellipse cx="100" cy="113" rx="14" ry="9" fill="#fff4e4"/>'
                            f'<path d="M96,106 L104,106 L100,112 Z" fill="{DARK}"/>',
                peek_extra=f'<path d="M72,66 L64,38 L92,54 Z" fill="#ff9a4d"/><path d="M128,66 L136,38 L108,54 Z" fill="#ff9a4d"/>',
                aura=("#ffd21f", "#ff9f2e"), ember="flame", ring="flame", eye_rim="#ffbf1f"),
    "shark": dict(builder=shark, egg=("#dff2fb", "#8fd6f2"), peek_body="#7fa8c8",
                  peek_muzzle=f'<ellipse cx="93" cy="108" rx="2" ry="2.6" fill="{DARK}"/><ellipse cx="107" cy="108" rx="2" ry="2.6" fill="{DARK}"/>'
                              f'<path d="M90,116 Q100,123 110,116" fill="none" stroke="{DARK}" stroke-width="2.8" stroke-linecap="round"/>',
                  peek_extra=f'<path d="M92,58 C92,46 96,38 102,34 C101,42 103,50 108,56 Z" fill="#5e88a8"/>',
                  aura=("#9fdcf5", "#4cc9f0"), ember="bubble", ring="bubble", pupils=(82, 122, 104), eye_rim="#4cc9f0"),
    "dino": dict(builder=dino, egg=("#eaf0fa", "#9ab4dc"), peek_body="#8aa8d8",
                 peek_muzzle='<ellipse cx="100" cy="112" rx="16" ry="10" fill="#b0c8ec"/>'
                             '<ellipse cx="94" cy="108" rx="1.8" ry="2.4" fill="' + DARK + '"/><ellipse cx="106" cy="108" rx="1.8" ry="2.4" fill="' + DARK + '"/>'
                             '<path d="M92,117 Q100,123 108,117" fill="none" stroke="' + DARK + '" stroke-width="2.8" stroke-linecap="round"/>',
                 peek_extra='<path d="M96,62 C97,53 103,53 104,62 Z" fill="#f2e3b8"/>',
                 aura=("#ffd21f", "#ff9f2e"), ember="flame", ring="flame", eye_rim="#ffbf1f"),
    "penguin": dict(builder=penguin, egg=("#f4fafe", "#bfe1f5"), peek_body="#9aa4b8",
                    peek_muzzle=f'<path d="M93,104 L107,104 L100,114 Z" fill="#ff9f2e"/>',
                    peek_extra="",
                    egg_ice=f'<ellipse cx="100" cy="190" rx="56" ry="7" fill="#bfe6ff" opacity="0.6"/>',
                    aura=("#cfeeff", "#7fd0ff"), ember="snow", ring="snow", pupils=(84, 120, 80), eye_rim="#4cc9f0"),
}

def box_egg():
    card = "#d8b078"
    card_d = "#c09858"
    tape = "#f0e6c8"
    s0 = (f'<g id="box"><rect x="46" y="70" width="108" height="108" rx="8" fill="{card}"/>'
          f'<rect x="46" y="70" width="108" height="22" rx="8" fill="{card_d}"/>'
          f'<rect x="92" y="70" width="16" height="108" fill="{tape}"/>'
          f'<rect x="46" y="118" width="108" height="14" fill="{tape}" opacity="0.7"/>'
          f'<text x="100" y="160" font-family="Arial" font-size="26" font-weight="bold" fill="{card_d}" text-anchor="middle">?</text></g>')
    head = peek_face(SPECIES["robot"]["peek_body"], SPECIES["robot"]["peek_muzzle"], SPECIES["robot"]["peek_extra"])
    s1 = (f'<g id="boxOpen"><path d="M46,96 L20,74 L58,66 Z" fill="{card_d}"/>'
          f'<path d="M154,96 L180,74 L142,66 Z" fill="{card_d}"/>'
          f'{head}'
          f'<rect x="46" y="118" width="108" height="60" rx="8" fill="{card}"/>'
          f'<rect x="92" y="118" width="16" height="60" fill="{tape}"/></g>')
    return s0, s1

for pet, cfg in SPECIES.items():
    outdir = os.path.join(ROOT, pet)
    os.makedirs(outdir, exist_ok=True)
    if cfg["egg"] == "box":
        s0, s1 = box_egg()
    else:
        base, spot = cfg["egg"]
        head = peek_face(cfg["peek_body"], cfg["peek_muzzle"], cfg["peek_extra"])
        s0, s1 = egg_pair(base, spot, head, ice=cfg.get("egg_ice"))
    names = ["Egg", "Hatchling", "Kid", "Scrapper", "Champion", "Hero", "Mega", "Ultra", "Mythic", "LEGENDARY"]
    for i in range(10):
        title = f"{pet.capitalize()} — stage {i}: {names[i]}"
        oc = cfg.get("outline")
        if i == 0:
            inner0 = f'<defs>{outline_def(oc)}</defs><g filter="url(#outline)">{s0}</g>' if oc else s0
            svg = wrap(inner0, title)
        elif i == 1:
            inner1 = f'<defs>{outline_def(oc)}</defs><g filter="url(#outline)">{s1}</g>' if oc else s1
            svg = wrap(inner1, title)
        else:
            inner = []
            defs = ""
            if oc:
                defs += outline_def(oc)
            if i >= 7:
                defs += aura_def(*cfg["aura"]) + eye_grad_defs(cfg["eye_rim"], *cfg.get("pupils", (80, 124, 86)))
                inner.append(aura_circle())
            if defs:
                inner.insert(0, f"<defs>{defs}</defs>")
            if i == 9:
                inner.append(ring(cfg["ring"]))
            body = cfg["builder"](i)
            filt = ' filter="url(#outline)"' if oc else ""
            inner.append(f'<g id="pet"{filt} transform="translate(100,196) scale({SCALES[i]}) translate(-100,-196)">{body}</g>')
            if i >= 8:
                inner.append(embers(cfg["ember"]))
            svg = wrap("\n  ".join(inner), title)
        with open(os.path.join(outdir, f"stage{i}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    print("wrote", pet)
print("done")
