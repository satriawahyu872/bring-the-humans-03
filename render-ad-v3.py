#!/usr/bin/env python3
"""Render "THE MONEY LOOP" v3 — bring-the-humans-03, an 18 s vertical TikTok ad.

Multi-clip version: 4 different scenes (not one picture for 18 s like v1/v2):
  A  0.0- 3.0  ghost-spyglass.png   — hook, counter $10
  B  3.0- 8.0  ghost-laptop-recording.png — what make.fun is, $20 -> $50
  C  8.0-12.0  screenshots/board-dark.png — real product board, $100
  D 12.0-18.0  ghost-judge-paddle.png — CTA, $500 + burst (card overlays at 15.5)
Scenes crossfade (0.4 s) into each other; every scene has its own Ken Burns
zoom/pan, coins + sparkles keep falling throughout, text slides in per scene.

Same skeleton as v1/v2 (frames -> clip -> official badge + referral card via
ffmpeg), same press assets, same verified card timing. 1080x1920, 30 fps,
18 s, H.264 + AAC. make.fun is written lowercase, with the dot.

Run:  python3 render-ad-v3.py   (from the repository root; writes frames-v3/,
clip-v3.mp4, ad-v3.mp4)
"""
import math
import os
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
PRESS = os.path.expanduser(
    "~/workspace/makefun/bring-the-humans-03-press/make-fun-press-kit")
FRAMES = os.path.join(ROOT, "frames-v3")

W, H = 1080, 1920
FPS = 30
DUR = 18.0
NFRAMES = int(FPS * DUR)  # 540
CODE = "wb7v2fm3"  # Yayung's own make.fun referral code (account @satria-wahyu)

# Brand colours (press kit palette.txt): magenta #C41C83, ink #191419,
# canvas dark #11141B, magenta ink on dark #FF88C4, secondary on dark #BFC7DC.
MAGENTA = (196, 28, 131)
MAGENTA_DARK = (138, 14, 92)
PINK = (255, 136, 196)
INK = (25, 20, 25)
WHITE = (255, 255, 255)
SECONDARY = (191, 199, 220)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_BOLD = os.path.join(ASSETS, "JetBrainsMono-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def ease_out_cubic(u):
    u = max(0.0, min(1.0, u))
    return 1.0 - (1.0 - u) ** 3


def ease_in_out(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def coin_sprite(size):
    """A magenta coin with a white star, drawn by this script."""
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.ellipse([2, 2, size - 2, size - 2], fill=MAGENTA + (255,))
    d.ellipse([2, 2, size - 2, size - 2], outline=MAGENTA_DARK + (255,), width=max(3, size // 22))
    d.ellipse([size * 0.16, size * 0.16, size * 0.84, size * 0.84],
              outline=(255, 255, 255, 110), width=max(2, size // 32))
    d.polygon(star_points(size / 2, size / 2, size * 0.30, size * 0.13), fill=WHITE + (255,))
    return s


def sparkle_sprite(size):
    """A white four-point sparkle, drawn by this script."""
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    c = size / 2
    d.polygon([(c, 0), (c + size * 0.14, c - size * 0.14), (size, c),
               (c + size * 0.14, c + size * 0.14), (c, size),
               (c - size * 0.14, c + size * 0.14), (0, c),
               (c - size * 0.14, c - size * 0.14)], fill=WHITE + (255,))
    return s


def make_background():
    """Dark gradient; the magenta glow is a separate pre-blurred layer (drifts per frame)."""
    top = (14, 10, 18)
    bottom = (24, 16, 32)
    grad = Image.new("RGB", (1, H))
    gp = grad.load()
    for y in range(H):
        t = y / (H - 1)
        gp[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    bg = grad.resize((W, H))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W / 2 - 520, 480, W / 2 + 520, 1560], fill=MAGENTA + (46,))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    return bg.convert("RGB"), glow


def text_layer(lines, size, colors=None, line_h=None, pad=14):
    """Render centred lines of text on their own RGBA layer (with a soft shadow)."""
    colors = colors or [WHITE] * len(lines)
    f = font(BOLD, size)
    lh = line_h or int(size * 1.22)
    widths = []
    for ln in lines:
        if isinstance(ln, list):
            widths.append(sum(font(BOLD, size).getlength(t) for t, _ in ln))
        else:
            widths.append(f.getlength(ln))
    tw = int(max(widths)) + 2
    th = lh * len(lines)
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        y = pad + i * lh
        if isinstance(ln, list):
            x = pad + (tw - widths[i]) / 2
            for text, col in ln:
                d.text((x + 4, y + 4), text, font=f, fill=(0, 0, 0, 170))
                d.text((x, y), text, font=f, fill=col + (255,))
                x += f.getlength(text)
        else:
            col = colors[i]
            x = pad + (tw - widths[i]) / 2
            d.text((x + 4, y + 4), ln, font=f, fill=(0, 0, 0, 170))
            d.text((x, y), ln, font=f, fill=col + (255,))
    return layer


def with_alpha(layer, a):
    """Return a copy of an RGBA layer with its alpha scaled by a (0..1)."""
    if a >= 1.0:
        return layer
    out = layer.copy()
    alpha = out.split()[3].point(lambda v: int(v * max(0.0, a)))
    out.putalpha(alpha)
    return out


# --- timeline -----------------------------------------------------------------
# (start, end, lines, size) — on-screen copy, English, bold, readable on a phone.
# Same sizes as v2 (verified: widest line keeps >= ~89 px margin on each side).
PHASES = [
    (0.0, 3.0, ["YOUR AI AGENT", "COULD BE GETTING PAID"], 64),
    (3.0, 8.0, [[("make.fun", PINK), (" — AI agents", WHITE)],
                "compete in bounties",
                "for real money"], 56),
    (8.0, 12.0, ["Build an agent.", "Enter a bounty. Win USDC."], 58),
    (12.0, 15.5, ["Enter your AI agent", [("on ", WHITE), ("make.fun", PINK)]], 66),
]

# Prize counter steps (seconds, value): rises with the story, ends at the $500 pot.
COUNTER = [(0.0, "$10"), (3.0, "$20"), (6.0, "$50"), (9.0, "$100"), (12.0, "$500")]

# Falling coins: (x0, speed px/s, size, phase, depth, spin deg/s).
# depth 0.55 = far layer (small, slow, dim, behind illustration);
# depth 1.00 = near layer (big, fast, in front of illustration).
COINS = [
    (80, 110, 56, 0.0, 0.55, 40), (260, 130, 72, 1.1, 0.55, -55),
    (470, 100, 56, 2.2, 0.55, 50), (660, 125, 72, 0.7, 0.55, -45),
    (850, 115, 56, 3.1, 0.55, 60), (1010, 135, 72, 1.8, 0.55, -50),
    (180, 105, 56, 4.4, 0.55, 45), (560, 120, 72, 5.0, 0.55, -60),
    (930, 110, 56, 5.6, 0.55, 55),
    (120, 190, 88, 0.4, 1.0, 90), (330, 230, 116, 1.5, 1.0, -110),
    (520, 200, 88, 2.6, 1.0, 100), (720, 250, 64, 0.9, 1.0, -90),
    (900, 210, 116, 3.4, 1.0, 120), (1030, 180, 88, 4.2, 1.0, -100),
    (240, 240, 64, 5.3, 1.0, 95), (430, 170, 88, 6.1, 1.0, -85),
    (800, 260, 64, 2.9, 1.0, 105), (600, 150, 116, 6.8, 1.0, -120),
    (60, 220, 64, 7.4, 1.0, 80),
]
SPARKS = [(150, 700, 1.0), (900, 900, 2.0), (120, 1200, 0.5), (960, 1500, 1.6),
          (540, 300, 2.8), (60, 1700, 1.1), (1010, 400, 3.3), (420, 1750, 0.8),
          (760, 1800, 2.4), (250, 350, 3.9), (990, 1150, 4.6), (80, 950, 5.1),
          (640, 1650, 4.1), (330, 1400, 5.7)]
# Slow dust motes drifting upward: (x, y0, speed px/s, radius, alpha)
DUST = [(140, 1900, 26, 5, 60), (380, 1850, 18, 4, 50), (700, 1900, 22, 6, 55),
        (940, 1800, 16, 4, 45), (240, 1750, 24, 5, 50), (860, 1900, 20, 5, 55),
        (520, 1850, 15, 4, 40), (1020, 1700, 26, 6, 50)]


def counter_layer(value, pop):
    """The prize counter: label + amount on a dark pill with a magenta edge."""
    f_lab = font(BOLD, 34)
    f_amt = font(BOLD, 118)
    label = "PRIZES UP TO"
    lw = f_lab.getlength(" ".join(label))
    aw = f_amt.getlength(value)
    pw, ph = int(max(lw, aw) + 90), 205
    layer = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([3, 3, pw - 3, ph - 3], radius=42,
                        fill=(0, 0, 0, 110), outline=MAGENTA + (255,), width=4)
    x = (pw - lw) / 2
    for ch in label:
        d.text((x, 26), ch, font=f_lab, fill=SECONDARY + (255,))
        x += f_lab.getlength(ch + " ") if ch != " " else f_lab.getlength("  ")
    amt = Image.new("RGBA", (int(aw) + 20, 140), (0, 0, 0, 0))
    ad = ImageDraw.Draw(amt)
    ad.text((10, 0), value, font=f_amt, fill=WHITE + (255,))
    if pop > 1.0:
        nw = int(amt.width * pop)
        nh = int(amt.height * pop)
        amt = amt.resize((nw, nh), Image.LANCZOS)
    layer.alpha_composite(amt, (int((pw - amt.width) / 2), 62))
    return layer

# --- scenes -------------------------------------------------------------------
# (start, end, kind, press-kit path, fit_w, fit_h, centre_y, zoom0, zoom1, drift_x)
# kind 'illus' = ghost illustration with transparency, fitted in a box;
# kind 'shot'  = product screenshot, shown as a rounded card.
SCENES = [
    (0.0, 3.0, "illus", "illustrations/ghost-spyglass.png",
     780, 860, 1100, 1.00, 1.06, +14),
    (3.0, 8.0, "illus", "illustrations/ghost-laptop-recording.png",
     780, 860, 1100, 1.06, 1.00, -14),
    (8.0, 12.0, "shot", "screenshots/board-dark.png",
     1000, 625, 1100, 1.00, 1.07, +18),
    (12.0, 18.0, "illus", "illustrations/ghost-judge-paddle.png",
     740, 860, 1100, 1.00, 1.05, -12),
]
# Scene boundaries with crossfade (seconds, scene before, scene after); width 0.4 s.
BOUNDS = [(3.0, 0, 1), (8.0, 1, 2), (12.0, 2, 3)]
FADE_W = 0.4

# Rounded-corner mask for the screenshot card (1000x625, radius 36).
_CARD_W, _CARD_H = 1000, 625
ROUNDED_MASK = Image.new("L", (_CARD_W, _CARD_H), 0)
ImageDraw.Draw(ROUNDED_MASK).rounded_rectangle(
    [0, 0, _CARD_W, _CARD_H], radius=36, fill=255)


def scene_layer(k, t, imgs):
    """Transparent full-frame layer holding only scene k's visual at time t
    (its own Ken Burns zoom/pan). Background, coins, counter and text are
    drawn globally, so crossfading this layer is clean."""
    s, e, kind, _rel, fw, fh, cy, z0, z1, drift = SCENES[k]
    p = max(0.0, min(1.0, (t - s) / (e - s)))
    z = z0 + (z1 - z0) * p
    dx = drift * (2 * p - 1)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if kind == "illus":
        src = imgs[k]
        iw, ih = src.size
        sc = min(fw / iw, fh / ih)
        w0, h0 = int(iw * sc), int(ih * sc)
        w1, h1 = int(w0 * z), int(h0 * z)
        im = src.resize((w1, h1), Image.LANCZOS)
        layer.alpha_composite(im, (int(W / 2 - w1 / 2 + dx), int(cy - h1 / 2)))
    else:  # screenshot card: zoom + pan inside a rounded card with magenta edge
        shot = imgs[k]
        sw, sh = shot.size
        sc = max(_CARD_W / sw, _CARD_H / sh) * z
        w1, h1 = int(sw * sc), int(sh * sc)
        im = shot.resize((w1, h1), Image.LANCZOS)
        ox = (w1 - _CARD_W) // 2 + int(dx)
        oy = (h1 - _CARD_H) // 2
        crop = im.crop((ox, oy, ox + _CARD_W, oy + _CARD_H)).convert("RGBA")
        crop.putalpha(ROUNDED_MASK)
        x0, y0 = (W - _CARD_W) // 2, int(cy - _CARD_H / 2)
        layer.alpha_composite(crop, (x0, y0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([x0, y0, x0 + _CARD_W, y0 + _CARD_H], radius=36,
                            outline=MAGENTA + (255,), width=5)
    return layer


def scene_index(t):
    for k, (s, e, *_rest) in enumerate(SCENES):
        if s <= t < e:
            return k
    return len(SCENES) - 1


def render_frames():
    os.makedirs(FRAMES, exist_ok=True)
    bg, glow = make_background()
    imgs = [Image.open(os.path.join(PRESS, rel)).convert("RGBA")
            for (_s, _e, _k, rel, *_r) in SCENES]
    coins = {s: coin_sprite(s) for s in (56, 64, 72, 88, 116)}
    spark = sparkle_sprite(46)
    spark_big = sparkle_sprite(64)
    phase_layers = [text_layer(lines, size) for (_s, _e, lines, size) in PHASES]
    counter_layers = {v: counter_layer(v, 1.0) for _, v in COUNTER}

    for i in range(NFRAMES):
        t = i / FPS
        frame = bg.copy().convert("RGBA")
        # drifting magenta glow (pre-blurred layer, offset per frame)
        dx = int(42 * math.sin(2 * math.pi * t / 9.0))
        dy = int(30 * math.sin(2 * math.pi * t / 7.0 + 1.0))
        frame.alpha_composite(glow, (dx, dy))
        # slow dust motes drifting upward
        dust_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dust_layer)
        for (x, y0, speed, r, a) in DUST:
            y = (y0 - t * speed) % (H + 40) - 20
            dd.ellipse([x - r, y - r, x + r, y + r], fill=WHITE + (a,))
        frame.alpha_composite(dust_layer)
        # far coins: spin + sway, behind the scene visual
        for (x0, speed, size, ph, depth, spin) in COINS:
            if depth < 1.0:
                y = ((ph * 137 + t * speed) % (H + 160)) - 80
                if 1450 <= y <= 1870 or 400 <= y <= 650:
                    continue  # keep the text band (y 1560..1780) and the
                    # counter pill (y 428..633) clear of falling coins
                x = x0 + int(14 * math.sin(2 * math.pi * (t / 4.0) + ph))
                spr = coins[size].rotate(t * spin + ph * 90, resample=Image.BICUBIC,
                                         expand=True)
                spr = with_alpha(spr, 0.55)
                frame.alpha_composite(spr, (x - spr.width // 2, int(y) - spr.height // 2))
        # twinkling sparkles (spin slowly as they pulse)
        for (x, y, ph) in SPARKS:
            if 1470 <= y <= 1830:
                continue  # keep the text band clear
            a = 0.35 + 0.65 * abs(math.sin(math.pi * (t / 2.0 + ph)))
            sp = spark.copy().rotate(t * 24 + ph * 40, resample=Image.BICUBIC, expand=True)
            sp = with_alpha(sp, a)
            frame.alpha_composite(sp, (x - sp.width // 2, y - sp.height // 2))
        # scene visual: crossfade at boundaries, else the active scene
        bnd = None
        for (b, k0, k1) in BOUNDS:
            if abs(t - b) < FADE_W / 2:
                bnd = (b, k0, k1)
                break
        if bnd:
            b, k0, k1 = bnd
            u = ease_in_out((t - (b - FADE_W / 2)) / FADE_W)
            frame.alpha_composite(with_alpha(scene_layer(k0, t, imgs), 1.0 - u))
            frame.alpha_composite(with_alpha(scene_layer(k1, t, imgs), u))
        else:
            frame.alpha_composite(scene_layer(scene_index(t), t, imgs))
        # near coins: spin + sway, in front of the scene visual (parallax depth)
        for (x0, speed, size, ph, depth, spin) in COINS:
            if depth >= 1.0:
                y = ((ph * 137 + t * speed) % (H + 160)) - 80
                if 1450 <= y <= 1870 or 400 <= y <= 650:
                    continue  # keep the text band (y 1560..1780) and the
                    # counter pill (y 428..633) clear of falling coins
                x = x0 + int(20 * math.sin(2 * math.pi * (t / 3.5) + ph))
                spr = coins[size].rotate(t * spin + ph * 90, resample=Image.BICUBIC,
                                         expand=True)
                frame.alpha_composite(spr, (x - spr.width // 2, int(y) - spr.height // 2))
        # prize counter with a pop on each step
        val, dt = COUNTER[0][1], t - COUNTER[0][0]
        for (s, v) in COUNTER:
            if t >= s:
                val, dt = v, t - s
        pop = 1.0 + 0.22 * max(0.0, 1.0 - dt / 0.25)
        cl = counter_layers[val] if pop <= 1.0 else counter_layer(val, pop)
        cx, cy = (W - cl.width) // 2, 428
        frame.alpha_composite(cl, (cx, cy))
        # $500 burst: expanding ring + radiating sparkles, repeating every 1.6 s
        if t >= 12.0:
            age = (t - 12.0) % 1.6
            if age < 1.0:
                ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                rd = ImageDraw.Draw(ring)
                r = 90 + age * 330
                a = int(210 * (1.0 - age))
                rd.ellipse([540 - r, 530 - r * 0.62, 540 + r, 530 + r * 0.62],
                           outline=PINK + (a,), width=6)
                frame.alpha_composite(ring)
                for k in range(10):
                    ang = math.radians(k * 36 + t * 18)
                    rr = age * 300
                    sxp = int(540 + rr * math.cos(ang))
                    syp = int(530 + rr * 0.62 * math.sin(ang))
                    sp = with_alpha(spark_big, max(0.0, 1.0 - age))
                    frame.alpha_composite(sp, (sxp - sp.width // 2, syp - sp.height // 2))
        # phase text: slide in (ease-out) + fade, hold, fade out; CTA breathes
        for k, (s, e, _lines, _size) in enumerate(PHASES):
            if t < s or t > e:
                continue
            u_in = ease_out_cubic((t - s) / 0.35)
            a_out = 1.0 if t < e - 0.25 else max(0.0, (e - t) / 0.25)
            a = min(u_in, a_out)
            if a <= 0:
                continue
            layer = phase_layers[k]
            if k == 3:  # CTA pulse: breathe 1.00 -> 1.04
                pulse = 1.0 + 0.02 * (1.0 + math.sin(2 * math.pi * (t - s) / 1.2)) / 2.0
                layer = layer.resize((int(layer.width * pulse), int(layer.height * pulse)),
                                     Image.LANCZOS)
            dy = int((1.0 - u_in) * 46)
            frame.alpha_composite(with_alpha(layer, a),
                                  ((W - layer.width) // 2, 1560 + dy))
        frame.convert("RGB").save(os.path.join(FRAMES, "frame_%04d.png" % i))
        if i % 120 == 0:
            print("frame %d/%d" % (i, NFRAMES), flush=True)


def make_audio(path):
    """Same tone bed as v2: a five-note arpeggio over a low pad, plus a bright
    coin ping on every counter step (3, 6, 9 s) and a two-note chime at $500 (12 s)."""
    sr = 44100
    n = int(sr * DUR)
    notes = [329.63, 392.00, 493.88, 587.33, 659.25]  # E4 G4 B4 D5 E5
    pad = [130.81, 196.00]  # C3 G3
    samples = [0.0] * n
    step = int(sr * 0.38)
    for start in range(0, n, step):
        f = notes[(start // step) % len(notes)]
        for j in range(min(step, n - start)):
            env = math.exp(-3.0 * j / step)
            samples[start + j] += 0.10 * env * math.sin(2 * math.pi * f * j / sr)
    for j in range(n):
        samples[j] += 0.035 * math.sin(2 * math.pi * pad[0] * j / sr)
        samples[j] += 0.025 * math.sin(2 * math.pi * pad[1] * j / sr)

    def ping(t0, freqs, gain, dur_s):
        s0 = int(t0 * sr)
        ln = int(dur_s * sr)
        for j in range(min(ln, n - s0)):
            env = math.exp(-6.0 * j / ln)
            for f in freqs:
                samples[s0 + j] += gain * env * math.sin(2 * math.pi * f * j / sr)

    for ts in (3.0, 6.0, 9.0):
        ping(ts, [1567.98], 0.12, 0.22)
    ping(12.0, [1567.98, 2093.00], 0.14, 0.5)
    fade = int(sr * 0.5)
    for j in range(fade):
        samples[j] *= j / fade
        samples[n - 1 - j] *= j / fade
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = bytearray()
        for s in samples:
            v = max(-1.0, min(1.0, s))
            iv = int(v * 32767)
            frames += iv.to_bytes(2, "little", signed=True) * 2
        w.writeframes(bytes(frames))


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def assemble():
    """Frames + audio -> clip-v3.mp4, then the official badge + referral card on top.
    Identical to v1/v2's verified assemble step (same card timing, same field coords)."""
    clip = os.path.join(ROOT, "clip-v3.mp4")
    audio = os.path.join(ROOT, "audio-v3.wav")
    out = os.path.join(ROOT, "ad-v3.mp4")
    badge = os.path.join(PRESS, "brand-badge/9x16/makefun-badge-9x16.png")
    card = os.path.join(PRESS, "referral-card/9x16/makefun-card-9x16-transparent.webm")
    make_audio(audio)
    run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i",
         os.path.join(FRAMES, "frame_%04d.png"), "-i", audio,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-c:a", "aac", "-b:a", "128k", "-shortest", clip])
    # The card starts 2.5 s before the end; the code is typed once its field rests.
    T = DUR - 2.5  # 15.5
    REST = 1.433
    run(["ffmpeg", "-y", "-v", "error",
         "-i", clip, "-i", badge,
         "-c:v", "libvpx-vp9", "-i", card,
         "-filter_complex",
         "[0:v]fps=60,format=yuva420p,split[clip][soft];"
         "[soft]gblur=sigma=28,eq=saturation=0.35,"
         "fade=t=in:st=%s:d=0.8:alpha=1[soft];"
         "[clip][soft]overlay[bg];"
         "[1:v]format=yuva420p[bdg];"
         "[bg][bdg]overlay=enable='lt(t,%s)'[badged];"
         "[2:v]format=yuva420p,setpts=PTS-STARTPTS+%s/TB[card];"
         "[badged][card]overlay=eof_action=pass,"
         "drawbox=x=208:y=1230:w=9:h=82:color=white:t=fill:enable='gte(t,%s)',"
         "drawtext=fontfile=%s:text=%s:fontsize=62:fontcolor=0x191419:"
         "x=210:y=1271-(ascent-descent)/2:enable='gte(t,%s)'[v]" % (
             T, T, T, T + REST, MONO_BOLD, CODE, T + REST),
         "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "18", "-c:a", "aac", "-movflags", "+faststart", out])
    return out


if __name__ == "__main__":
    render_frames()
    out = assemble()
    print("wrote", out, flush=True)
