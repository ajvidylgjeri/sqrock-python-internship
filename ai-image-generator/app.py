"""
AI Image Generator — Sqrock IT Solutions Python Internship (Phase 1, Task 4)

A Flask web app that turns a text prompt into an image. It works fully OFFLINE:
the default generator uses Pillow to render a unique piece of abstract art that
is deterministically derived from the prompt (same prompt -> same image), with
the prompt caption overlaid.

To use a real text-to-image API instead, set an API key and plug your call into
`live_image()` (a Stability/OpenAI example is sketched there) — the app will use
it automatically when IMAGE_API_KEY is set.

Run:
    pip install -r requirements.txt
    python app.py
    # open http://127.0.0.1:5000

Author: Ajvi Dylgjeri
"""
import os
import io
import base64
import hashlib
import math
import random
from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageFilter

app = Flask(__name__)
IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "").strip()
SIZE = 640


# ---------------------------------------------------------------------------
# Offline generative art (default — no API key needed)
# ---------------------------------------------------------------------------
def _seed_from_prompt(prompt: str) -> int:
    return int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16) % (2 ** 32)


def _palette(rng):
    base_h = rng.random()
    cols = []
    for i in range(3):
        h = (base_h + i * 0.18 + rng.uniform(-0.05, 0.05)) % 1.0
        cols.append(_hsv_to_rgb(h, 0.55 + rng.random() * 0.35, 0.7 + rng.random() * 0.3))
    return cols


def _hsv_to_rgb(h, s, v):
    i = int(h * 6)
    f = h * 6 - i
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i % 6]
    return (int(r * 255), int(g * 255), int(b * 255))


def offline_image(prompt: str) -> Image.Image:
    rng = random.Random(_seed_from_prompt(prompt))
    cols = _palette(rng)

    # vertical gradient background between two palette colours
    top, bot = cols[0], cols[1]
    img = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(SIZE):
        t = y / SIZE
        row = tuple(int(top[c] * (1 - t) + bot[c] * t) for c in range(3))
        draw.line([(0, y), (SIZE, y)], fill=row)

    # floating translucent circles
    for _ in range(rng.randint(8, 16)):
        r = rng.randint(30, 160)
        cx, cy = rng.randint(0, SIZE), rng.randint(0, SIZE)
        col = cols[rng.randint(0, 2)]
        alpha = rng.randint(40, 120)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (alpha,))

    # a sweep of connected triangles for structure
    pts = [(rng.randint(0, SIZE), rng.randint(0, SIZE)) for _ in range(rng.randint(3, 6))]
    draw.polygon(pts, fill=cols[2] + (90,))

    img = img.filter(ImageFilter.GaussianBlur(1))

    # caption with the prompt
    draw = ImageDraw.Draw(img, "RGBA")
    caption = prompt if len(prompt) <= 60 else prompt[:57] + "..."
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except Exception:
        font = ImageFont.load_default()
    tw = draw.textlength(caption, font=font)
    bar_h = 64
    draw.rectangle([0, SIZE - bar_h, SIZE, SIZE], fill=(0, 0, 0, 140))
    draw.text(((SIZE - tw) / 2, SIZE - bar_h + 18), caption, font=font, fill=(255, 255, 255, 255))
    return img


# ---------------------------------------------------------------------------
# Optional live mode (plug in a real text-to-image API here)
# ---------------------------------------------------------------------------
def live_image(prompt: str) -> Image.Image:
    """
    Example integration point. With a real key you would call an image API, e.g.:

        import requests
        r = requests.post("https://api.stability.ai/v2beta/stable-image/generate/core",
                          headers={"authorization": f"Bearer {IMAGE_API_KEY}"},
                          files={"none": ""}, data={"prompt": prompt, "output_format": "png"})
        return Image.open(io.BytesIO(r.content))

    If anything fails we fall back to the offline generator so the app never breaks.
    """
    try:
        raise NotImplementedError  # no key wired in this demo build
    except Exception:
        return offline_image(prompt)


def generate(prompt: str) -> Image.Image:
    return live_image(prompt) if IMAGE_API_KEY else offline_image(prompt)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    mode = "live" if IMAGE_API_KEY else "offline"
    return render_template("index.html", mode=mode)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please enter a prompt."}), 400
    img = generate(prompt)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return jsonify({"image": "data:image/png;base64," + b64, "prompt": prompt})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
