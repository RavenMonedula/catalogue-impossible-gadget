#!/usr/bin/env python3
"""The Forever Kettle — a studio catalogue photo of an impossible gadget.

An electric kettle plugged into ITSELF: its power cord loops from the
base back into a socket on its own front, and its red "on" light glows.
One accessory only: a single teacup with a wisp of steam.

Drawn with PIL only. Deterministic (no randomness, no time, no network).
Writes /output/entry.png (1024x1024 PNG).
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
GROUND = 830  # floor line the kettle and cup stand on

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- base
img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
d = ImageDraw.Draw(img)

# clean light-grey-to-white vertical gradient backdrop
top_col, bot_col = (226, 228, 231), (255, 255, 255)
for y in range(H):
    d.line([(0, y), (W, y)], fill=lerp(top_col, bot_col, y / (H - 1)) + (255,))

# ---------------------------------------------------------------- kettle layer (for reflection)
K = Image.new("RGBA", (W, H), (0, 0, 0, 0))
kd = ImageDraw.Draw(K)

# --- steel body: mask + gradient -------------------------------------
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.polygon([(360, 440), (610, 440), (640, GROUND), (330, GROUND)], fill=255)
md.ellipse([330, 798, 640, 842], fill=255)   # rounded base
md.ellipse([358, 424, 612, 456], fill=255)   # rounded shoulder

# brushed-steel gradient: horizontal bands + soft vertical highlight
steel = Image.new("RGB", (W, H), (0, 0, 0))
sd = ImageDraw.Draw(steel)
for y in range(400, 860):
    band = int(10 * math.sin(y / 6.0) + 6 * math.sin(y / 2.3))
    base = 208 + band
    sd.line([(0, y), (W, y)], fill=(base, base + 3, base + 7))
# vertical highlight band (bright on the left third, fading right)
hl = Image.new("L", (W, H), 0)
hd = ImageDraw.Draw(hl)
for x in range(300, 660):
    t = (x - 300) / 360.0
    v = int(150 * math.exp(-((t - 0.32) ** 2) / 0.045))
    hd.line([(x, 400), (x, 860)], fill=v)
hl = hl.filter(ImageFilter.GaussianBlur(18))
white = Image.new("RGB", (W, H), (255, 255, 255))
steel = Image.composite(white, steel, hl)
# darker shading at the far edges
edge = Image.new("L", (W, H), 0)
ed = ImageDraw.Draw(edge)
for x in range(300, 660):
    t = (x - 300) / 360.0
    v = int(70 * (max(0.0, 0.10 - t) / 0.10 + max(0.0, t - 0.90) / 0.10))
    ed.line([(x, 400), (x, 860)], fill=min(90, v))
edge = edge.filter(ImageFilter.GaussianBlur(10))
dark = Image.new("RGB", (W, H), (90, 94, 100))
steel = Image.composite(dark, steel, edge)

body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
body.paste(Image.merge("RGBA", (*steel.split(), mask)), (0, 0))
K.alpha_composite(body)

# body outline (thin, dark) for a crisp product edge
kd.line([(360, 440), (330, GROUND)], fill=(60, 62, 66, 255), width=2)
kd.line([(610, 440), (640, GROUND)], fill=(60, 62, 66, 255), width=2)

# --- lid + knob -------------------------------------------------------
kd.ellipse([352, 406, 618, 452], fill=(52, 54, 60, 255))
kd.ellipse([368, 412, 602, 440], fill=(88, 90, 96, 255))
kd.ellipse([470, 388, 500, 414], fill=(30, 30, 34, 255))
kd.ellipse([476, 391, 488, 403], fill=(150, 152, 158, 255))

# --- spout (left, pointing up) ----------------------------------------
kd.polygon([(352, 590), (238, 468), (222, 490), (298, 622), (356, 672)],
           fill=(196, 199, 204, 255))
kd.line([(352, 590), (238, 468)], fill=(110, 112, 118, 255), width=2)
kd.line([(238, 468), (222, 490)], fill=(70, 72, 78, 255), width=3)
kd.ellipse([224, 472, 240, 488], fill=(40, 40, 44, 255))

# --- handle (right, dark C) -------------------------------------------
kd.arc([556, 458, 712, 722], start=-72, end=72, fill=(38, 38, 42, 255), width=18)
kd.rectangle([608, 462, 632, 486], fill=(38, 38, 42, 255))
kd.rectangle([608, 688, 632, 712], fill=(38, 38, 42, 255))

# --- base ring ---------------------------------------------------------
kd.ellipse([334, 812, 636, 840], outline=(70, 72, 78, 255), width=3)

img.alpha_composite(K)

# ---------------------------------------------------------------- reflection
flip = K.transpose(Image.FLIP_TOP_BOTTOM)
refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
refl.paste(flip, (0, GROUND - (H - 1 - GROUND)))
# fade with depth + overall faintness
fade = Image.new("L", (W, H), 0)
fd = ImageDraw.Draw(fade)
for y in range(GROUND, H):
    fd.line([(0, y), (W, y)], fill=int(255 * (1 - (y - GROUND) / (H - GROUND))))
a = refl.split()[3]
a = ImageChops.multiply(a, fade).point(lambda v: int(v * 0.38))
refl.putalpha(a)
refl = refl.filter(ImageFilter.GaussianBlur(3))
img.alpha_composite(refl)

# ---------------------------------------------------------------- drop shadow
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd = ImageDraw.Draw(sh)
shd.ellipse([300, 812, 700, 862], fill=(0, 0, 0, 110))
shd.ellipse([770, 822, 950, 852], fill=(0, 0, 0, 70))
sh = sh.filter(ImageFilter.GaussianBlur(16))
img.alpha_composite(sh)

# ---------------------------------------------------------------- power light (glow)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, al in ((30, 40), (20, 80), (13, 140)):
    gd.ellipse([452 - r, 640 - r, 452 + r, 640 + r], fill=(255, 60, 45, al))
glow = glow.filter(ImageFilter.GaussianBlur(6))
img.alpha_composite(glow)
d = ImageDraw.Draw(img)
d.ellipse([444, 632, 460, 648], fill=(255, 55, 40, 255))
d.ellipse([447, 635, 453, 641], fill=(255, 220, 210, 255))

# ---------------------------------------------------------------- brand mark (product text only)
brand = "PERPETUA"
bf = font(15)
# letterspaced, centred on the body front
widths = [d.textlength(ch, font=bf) for ch in brand]
total = sum(widths) + 3 * (len(brand) - 1)
x = 485 - total / 2
for ch, wch in zip(brand, widths):
    d.text((x, 552), ch, font=bf, fill=(74, 76, 82, 255))
    x += wch + 3

# ---------------------------------------------------------------- socket + plug (the joke)
# socket panel on the kettle's own front
d.rounded_rectangle([530, 690, 566, 732], radius=5, fill=(44, 44, 48, 255))
d.rectangle([540, 702, 546, 714], fill=(12, 12, 14, 255))
d.rectangle([550, 702, 556, 714], fill=(12, 12, 14, 255))
# plug, inserted from the right
d.rounded_rectangle([566, 698, 606, 724], radius=5, fill=(28, 28, 32, 255))
d.rectangle([556, 705, 568, 711], fill=(150, 150, 155, 255))
d.rectangle([556, 716, 568, 722], fill=(150, 150, 155, 255))

# ---------------------------------------------------------------- cord (loops out and back in)
# smooth Catmull-Rom spline through control points so the cord reads
# as a real cable, not a polygon
def catmull_rom(pts, samples=24):
    out = []
    ext = [pts[0]] + pts + [pts[-1]]
    for i in range(len(ext) - 3):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for k in range(samples):
            t = k / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


cord = catmull_rom([(560, 828), (592, 862), (662, 878), (722, 862),
                    (744, 812), (732, 758), (682, 726), (612, 716)])
d.line(cord, fill=(25, 25, 28, 255), width=11, joint="curve")
# strain relief where the cord leaves the base
d.rounded_rectangle([550, 818, 572, 840], radius=4, fill=(25, 25, 28, 255))

# ---------------------------------------------------------------- teacup + steam
# saucer
d.ellipse([798, 812, 932, 842], fill=(246, 246, 246, 255),
          outline=(190, 190, 190, 255), width=2)
# cup body (slightly tapered)
d.polygon([(818, 748), (912, 748), (900, 818), (830, 818)],
          fill=(250, 250, 250, 255))
d.line([(818, 748), (830, 818)], fill=(200, 200, 200, 255), width=2)
d.line([(912, 748), (900, 818)], fill=(185, 185, 185, 255), width=2)
# cup handle
d.arc([896, 752, 942, 802], start=-80, end=80, fill=(190, 190, 190, 255), width=9)
d.arc([896, 752, 942, 802], start=-80, end=80, fill=(250, 250, 250, 255), width=6)
# rim + tea
d.ellipse([818, 740, 912, 760], fill=(252, 252, 252, 255),
          outline=(200, 200, 200, 255), width=2)
d.ellipse([826, 744, 904, 757], fill=(122, 72, 32, 255))
# steam: two faint wavy wisps
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
std = ImageDraw.Draw(steam)
for cx, top in ((848, 636), (886, 648)):
    pts = [(cx + 9 * math.sin((735 - y) / 26.0), y) for y in range(top, 736, 4)]
    std.line(pts, fill=(170, 170, 170, 130), width=4, joint="curve")
steam = steam.filter(ImageFilter.GaussianBlur(2))
img.alpha_composite(steam)

# ---------------------------------------------------------------- save
img = img.convert("RGB")
os.makedirs("/output", exist_ok=True)
img.save("/output/entry.png", "PNG")
print("saved /output/entry.png", img.size,
      os.path.getsize("/output/entry.png"), "bytes")
