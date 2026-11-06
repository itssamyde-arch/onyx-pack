"""Erzeugt das ONYX Resource-Pack (Portal-Textur + Logo fuer das Regel-Fenster)."""
import json, math, os, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(BASE, "pack")
OUT_ZIP = os.path.join(BASE, "ONYX-Pack.zip")


def save(img, rel):
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def write(rel, text):
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---- 1. Portal-Textur: animierter Onyx-Wirbel (ersetzt das Nether-Portal-Muster) ----
FRAMES = 32
S = 16
strip = Image.new("RGBA", (S, S * FRAMES))
for f in range(FRAMES):
    ph = 2 * math.pi * f / FRAMES
    for y in range(S):
        for x in range(S):
            u = 2 * math.pi * x / S
            v = 2 * math.pi * y / S
            # nahtlos kachelbar in x/y und periodisch in der Zeit
            n = (math.sin(u * 2 + ph) + math.sin(v * 2 - ph) + math.sin((u + v) + ph * 2) + math.sin((u - v) * 1 - ph)) / 4
            n = (n + 1) / 2  # 0..1
            # Palette: schwarz -> dunkellila -> magenta -> helles Lila
            if n < 0.5:
                t = n / 0.5
                c = (int(10 + 70 * t), int(0 + 10 * t), int(25 + 110 * t))
            else:
                t = (n - 0.5) / 0.5
                c = (int(80 + 150 * t), int(10 + 70 * t), int(135 + 100 * t))
            strip.putpixel((x, f * S + y), (c[0], c[1], c[2], 215))
save(strip, "assets/minecraft/textures/block/nether_portal.png")
write("assets/minecraft/textures/block/nether_portal.png.mcmeta",
      json.dumps({"animation": {"frametime": 2, "interpolate": True}}))

# ---- 2. Logo-Glyph (wird im Regel-Fenster ueber die Schrift onyx:default angezeigt) ----
W, H = 96, 16
big = 8
img = Image.new("RGBA", (W * big, H * big), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
font = None
for cand in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arial.ttf"]:
    if os.path.exists(cand):
        font = ImageFont.truetype(cand, 12 * big)
        break
if font is None:
    font = ImageFont.load_default()
text = "ONYX SMP"
bbox = d.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
pos = ((W * big - tw) // 2 - bbox[0], (H * big - th) // 2 - bbox[1])
glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.text(pos, text, font=font, fill=(190, 60, 255, 255))
glow = glow.filter(ImageFilter.GaussianBlur(big * 1.2))
img = Image.alpha_composite(img, glow)
d = ImageDraw.Draw(img)
d.text((pos[0] + big, pos[1] + big), text, font=font, fill=(25, 0, 40, 255))
d.text(pos, text, font=font, fill=(215, 120, 255, 255))
logo = img.resize((W, H), Image.LANCZOS)
save(logo, "assets/onyx/textures/font/logo.png")
write("assets/onyx/font/default.json", json.dumps({
    "providers": [
        {"type": "bitmap", "file": "onyx:font/logo.png", "ascent": 12, "height": 16, "chars": ["\ue000"]}
    ]
}, ensure_ascii=True))

# ---- 3. pack.mcmeta ----
write("pack.mcmeta", json.dumps({
    "pack": {
        "pack_format": 75,
        "supported_formats": {"min_inclusive": 46, "max_inclusive": 99},
        "description": "\u00a75ONYX SMP \u00a77Texturen"
    }
}, ensure_ascii=True))

write("ONYX-LIESMICH.txt", "ONYX SMP Resource-Pack: Portal-Textur und Logo fuer das Regel-Fenster.\n")

# Pack-Icon
icon = Image.new("RGBA", (64, 64), (15, 0, 25, 255))
ImageDraw.Draw(icon).ellipse((10, 10, 54, 54), outline=(190, 60, 255, 255), width=4)
save(icon, "pack.png")

# ---- ZIP + SHA1 ----
if os.path.exists(OUT_ZIP):
    os.remove(OUT_ZIP)
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(PACK):
        for fn in files:
            full = os.path.join(root, fn)
            z.write(full, os.path.relpath(full, PACK).replace("\\", "/"))
sha1 = hashlib.sha1(open(OUT_ZIP, "rb").read()).hexdigest()
print("ZIP:", OUT_ZIP)
print("SHA1:", sha1)
write("../pack.sha1", sha1)
