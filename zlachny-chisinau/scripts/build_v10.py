#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import random
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
VENUE_ASSETS = ASSETS / "venues"
ASSETS.mkdir(exist_ok=True)
VENUE_ASSETS.mkdir(exist_ok=True)

CITY_SOURCES = [
    "https://images.pexels.com/photos/14471525/pexels-photo-14471525.jpeg?auto=compress&cs=tinysrgb&w=2400",
    "https://images.pexels.com/photos/34962360/pexels-photo-34962360.jpeg?auto=compress&cs=tinysrgb&w=2400",
]
PARTY_SOURCES = [
    "https://images.pexels.com/photos/30592890/pexels-photo-30592890.jpeg?auto=compress&cs=tinysrgb&w=2400",
    "https://images.pexels.com/photos/3171837/pexels-photo-3171837.jpeg?auto=compress&cs=tinysrgb&w=2400",
]

def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ZlachnyChisinauBuild/1.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()

def open_remote(urls: list[str]) -> tuple[Image.Image, str]:
    errors: list[str] = []
    for url in urls:
        try:
            return Image.open(io.BytesIO(download(url))).convert("RGB"), url
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("All image sources failed:\n" + "\n".join(errors))

def cover_position(
    image: Image.Image,
    size: tuple[int, int],
    position: tuple[float, float] = (0.5, 0.5),
) -> Image.Image:
    tw, th = size
    w, h = image.size
    scale = max(tw / w, th / h)
    nw, nh = round(w * scale), round(h * scale)
    image = image.resize((nw, nh), Image.Resampling.LANCZOS)
    px = max(0.0, min(1.0, position[0]))
    py = max(0.0, min(1.0, position[1]))
    left = round((nw - tw) * px)
    top = round((nh - th) * py)
    return image.crop((left, top, left + tw, top + th))

def radial_glow(
    canvas: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    for step in range(14, 0, -1):
        ratio = step / 14
        r = int(radius * ratio)
        alpha = int(color[3] * (1 - ratio) ** 1.7)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color[:3], alpha))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(3, radius // 18))))

def add_disco_ball(canvas: Image.Image, center: tuple[int, int], radius: int) -> None:
    cx, cy = center
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(
        (cx - radius * 1.35, cy - radius * 1.35, cx + radius * 1.35, cy + radius * 1.35),
        fill=(255, 45, 166, 90),
    )
    gd.ellipse(
        (cx - radius * 1.15, cy - radius * 1.15, cx + radius * 1.15, cy + radius * 1.15),
        fill=(70, 215, 255, 68),
    )
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius // 2)))

    ball_size = radius * 2 + 4
    ball = Image.new("RGBA", (ball_size, ball_size), (0, 0, 0, 0))
    mask = Image.new("L", ball.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((2, 2, ball_size - 3, ball_size - 3), fill=255)

    bd = ImageDraw.Draw(ball)
    for y in range(ball_size):
        yy = (y - radius) / max(1, radius)
        for x in range(ball_size):
            xx = (x - radius) / max(1, radius)
            d = math.sqrt(xx * xx + yy * yy)
            if d > 1:
                continue
            light = max(0, 1 - d)
            highlight = max(0, 1 - math.sqrt((xx + 0.28) ** 2 + (yy + 0.35) ** 2) * 2.2)
            r = int(34 + 95 * light + 125 * highlight)
            g = int(26 + 38 * light + 110 * highlight)
            b = int(62 + 110 * light + 105 * highlight)
            bd.point((x, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    tile_colors = [(255, 235, 255, 210), (255, 69, 172, 210), (73, 218, 255, 195), (170, 100, 255, 180)]
    spacing = max(8, radius // 8)
    for gx in range(0, ball_size, spacing):
        bd.line((gx, 0, gx, ball_size), fill=tile_colors[(gx // spacing) % len(tile_colors)], width=2)
    for gy in range(0, ball_size, spacing):
        bd.line((0, gy, ball_size, gy), fill=tile_colors[(gy // spacing + 1) % len(tile_colors)], width=2)
    bd.line((radius - 15, 8, radius + 30, ball_size - 10), fill=(255, 255, 255, 200), width=5)
    bd.ellipse((radius - 42, radius - 58, radius - 12, radius - 28), fill=(255, 255, 255, 225))
    ball.putalpha(ImageChops.multiply(ball.getchannel("A"), mask))

    canvas.alpha_composite(ball, (cx - radius - 2, cy - radius - 2))
    draw = ImageDraw.Draw(canvas)
    draw.line((cx, 0, cx, cy - radius), fill=(180, 185, 215, 180), width=max(2, radius // 35))

def add_neon_architecture(canvas: Image.Image, size: tuple[int, int]) -> None:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    pink = (255, 46, 157, 230)
    cyan = (65, 219, 255, 190)
    x0, x1 = int(w * 0.77), int(w * 0.99)
    y0, y1 = int(h * 0.08), int(h * 0.72)
    for offset in (0, 8, 16):
        draw.line((x0 + offset, y0, x0 + offset, y1), fill=pink, width=4)
        draw.line((x0, y0 + offset, x1, y0 + offset), fill=pink, width=4)
    draw.line((x0 + 12, int(h * 0.28), x1, int(h * 0.28)), fill=cyan, width=3)
    draw.line((x0 + 12, int(h * 0.58), x1, int(h * 0.58)), fill=(151, 69, 255, 190), width=4)
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12)))
    canvas.alpha_composite(layer)

def add_rooftop_lights(canvas: Image.Image, size: tuple[int, int]) -> None:
    w, h = size
    random.seed(17)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    y = int(h * 0.67)
    draw.line((0, y, w, y - 22), fill=(255, 180, 95, 135), width=2)
    for x in range(int(w * 0.04), int(w * 0.98), max(50, w // 22)):
        yy = y - round((x / w) * 22) + random.randint(-3, 3)
        r = max(3, h // 160)
        draw.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 200, 120, 245))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(4, h // 100))))
    canvas.alpha_composite(layer)

def party_mask(size: tuple[int, int], mobile: bool) -> Image.Image:
    w, h = size
    mask = Image.new("L", size, 0)
    pixels = mask.load()
    for y in range(h):
        y_start = 0.34 if mobile else 0.42
        y_alpha = max(0.0, min(1.0, (y / h - y_start) / (1 - y_start)))
        for x in range(w):
            x_start = 0.08 if mobile else 0.20
            x_alpha = max(0.0, min(1.0, (x / w - x_start) / max(0.01, 1 - x_start)))
            alpha = int(255 * min(1.0, y_alpha * 1.55) * (0.42 + 0.58 * x_alpha))
            pixels[x, y] = alpha
    return mask.filter(ImageFilter.GaussianBlur(max(8, w // 90)))

def compose_hero(
    city: Image.Image,
    party: Image.Image,
    size: tuple[int, int],
    *,
    mobile: bool = False,
) -> Image.Image:
    w, h = size
    city_pos = (0.56, 0.50) if not mobile else (0.62, 0.52)
    party_pos = (0.63, 0.60) if not mobile else (0.60, 0.57)

    city_layer = cover_position(city, size, city_pos)
    city_layer = ImageEnhance.Color(city_layer).enhance(1.24)
    city_layer = ImageEnhance.Contrast(city_layer).enhance(1.12)
    city_layer = ImageEnhance.Brightness(city_layer).enhance(0.72)

    party_layer = cover_position(party, size, party_pos)
    party_layer = ImageEnhance.Color(party_layer).enhance(1.35)
    party_layer = ImageEnhance.Contrast(party_layer).enhance(1.10)
    party_layer = ImageEnhance.Brightness(party_layer).enhance(0.84)

    result = city_layer.convert("RGBA")
    result.alpha_composite(Image.new("RGBA", size, (7, 8, 22, 55)))
    result.alpha_composite(Image.composite(party_layer.convert("RGBA"), Image.new("RGBA", size), party_mask(size, mobile)))

    radial_glow(result, (int(w * 0.73), int(h * 0.52)), int(w * 0.32), (255, 42, 158, 90))
    radial_glow(result, (int(w * 0.45), int(h * 0.58)), int(w * 0.30), (52, 199, 255, 58))
    radial_glow(result, (int(w * 0.53), int(h * 0.48)), int(w * 0.26), (255, 151, 53, 44))

    add_neon_architecture(result, size)
    add_rooftop_lights(result, size)
    ball_center = (int(w * (0.82 if not mobile else 0.74)), int(h * (0.15 if not mobile else 0.13)))
    add_disco_ball(result, ball_center, int(h * (0.105 if not mobile else 0.085)))

    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(w):
        ratio = x / max(1, w - 1)
        alpha = int(170 * max(0, 1 - ratio / (0.72 if not mobile else 0.88)))
        sd.line((x, 0, x, h), fill=(2, 3, 9, alpha))
    result.alpha_composite(shade)

    border = Image.new("RGBA", size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.rounded_rectangle(
        (4, 4, w - 5, h - 5),
        radius=max(18, h // 25),
        outline=(255, 49, 165, 185),
        width=max(2, h // 240),
    )
    bd.line((int(w * 0.49), h - 7, w - 45, h - 7), fill=(65, 220, 255, 140), width=2)
    result.alpha_composite(border.filter(ImageFilter.GaussianBlur(5)))
    result.alpha_composite(border)

    result = ImageEnhance.Sharpness(result.convert("RGB")).enhance(1.12)
    return result

def save_webp(image: Image.Image, path: Path, quality: int = 91) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "WEBP", quality=quality, method=6)
    blob = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
    }

city, city_source = open_remote(CITY_SOURCES)
party, party_source = open_remote(PARTY_SOURCES)
manifest = {
    "generatedAt": "2026-08-01",
    "heroSource": {
        "city": city_source,
        "party": party_source,
        "composition": "night skyline + rooftop party + generated neon architecture and disco ball",
    },
    "assets": {},
}
manifest["assets"]["heroDesktop"] = save_webp(
    compose_hero(city, party, (2000, 1000), mobile=False),
    ASSETS / "hero-desktop.webp",
    92,
)
manifest["assets"]["heroMobile"] = save_webp(
    compose_hero(city, party, (900, 1200), mobile=True),
    ASSETS / "hero-mobile.webp",
    91,
)

source_json = ROOT / "venues-v9.json"
if not source_json.exists():
    source_json = ROOT / "venues.json"
data = json.loads(source_json.read_text(encoding="utf-8"))
for venue in data.get("items", []):
    url = venue.get("image") or venue.get("imageSource")
    if not url or not re.match(r"https?://", url):
        continue
    try:
        image, _ = open_remote([url])
        target = VENUE_ASSETS / f"{venue['id']}.webp"
        local = cover_position(image, (960, 720))
        local = ImageEnhance.Contrast(local).enhance(1.03)
        local = ImageEnhance.Color(local).enhance(1.04)
        info = save_webp(local, target, 82)
        manifest["assets"][venue["id"]] = {**info, "source": url, "status": "illustrative"}
        venue["image"] = info["path"]
        venue["imageStatus"] = "local-illustrative"
    except Exception as exc:
        venue["imageStatus"] = "external-fallback"
        venue["imageError"] = str(exc)

data["schemaVersion"] = 4
data["updatedAt"] = "2026-08-01"
(ROOT / "venues-v10.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
(ASSETS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
extra = ROOT / "v9.css"
if extra.exists():
    css += "\n" + extra.read_text(encoding="utf-8")
css = re.sub(
    r"\.hero-bg\{position:absolute;inset:0;background:[^}]+\}",
    ".hero-bg{position:absolute;inset:0;background:url('assets/hero-desktop.webp') center/cover no-repeat;filter:saturate(1.04) contrast(1.02)}",
    css,
    count=1,
)
css = css.replace(
    ".hero-bg{background-position:67% center}",
    ".hero-bg{background-image:url('assets/hero-mobile.webp');background-position:center 42%}",
)
css = css.replace("font-family:Inter,system-ui,sans-serif", 'font-family:Arial,"DejaVu Sans",system-ui,sans-serif')
css = css.replace("font-family:Oswald,Impact,sans-serif", 'font-family:"DejaVu Sans Condensed",Arial,sans-serif')
(ROOT / "v10.css").write_text(css, encoding="utf-8")

js_source = ROOT / "v9.js"
if not js_source.exists():
    js_source = ROOT / "app.js"
js = js_source.read_text(encoding="utf-8")
js = js.replace("fetch('venues-v9.json?v=9'", "fetch('venues-v10.json?v=10'")
js = js.replace("fetch('venues.json?v=9'", "fetch('venues-v10.json?v=10'")
js = js.replace(
    "function localNow(){return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}",
    "function localNow(){if(new URLSearchParams(location.search).has('qa'))return new Date('2026-08-01T21:00:00');return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}",
)
(ROOT / "v10.js").write_text(js, encoding="utf-8")

html = (ROOT / "index.html").read_text(encoding="utf-8")
html = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">', "", html)
html = re.sub(r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>', "", html)
html = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]+>', "", html)
html = re.sub(
    r'<link rel="stylesheet" href="styles\.css\?v=\d+">(?:<link rel="stylesheet" href="v9\.css\?v=\d+">)?',
    '<link rel="stylesheet" href="v10.css?v=10">',
    html,
)
html = re.sub(r'<script src="(?:app|v9)\.js\?v=\d+"></script>', '<script src="v10.js?v=10"></script>', html)
html = html.replace("<body>", '<body data-build="v10">', 1)
html = html.replace('<body data-build="v9">', '<body data-build="v10">')
(ROOT / "index.html").write_text(html, encoding="utf-8")

(ASSETS / "README.md").write_text(
    """# Local generated assets

These files are generated by `scripts/build_v10.py` and committed by GitHub Actions. The published site serves them from this repository, not from third-party image CDNs. The hero is a project-specific composite recreating the approved nightlife reference: city skyline, active rooftop crowd, neon architecture and a disco ball. Venue images remain illustrative and are labelled as such in the UI. See `manifest.json` for source URLs and SHA-256 hashes.
""",
    encoding="utf-8",
)
print(
    json.dumps(
        {
            "hero": manifest["heroSource"],
            "venueCount": len(data.get("items", [])),
            "assetCount": len(manifest["assets"]),
        },
        indent=2,
    )
)
