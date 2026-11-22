#!/usr/bin/env python3
"""Render "THE MONEY LOOP" — bring-the-humans-03 v1, a 18 s vertical TikTok ad for make.fun.

Every frame is drawn here with PIL from the official press assets plus shapes this
script draws itself: no other image is downloaded, no other video is copied.
The brand badge and the referral end card are laid on with ffmpeg afterwards
(see assemble()), exactly as make.fun's press guide prescribes:
  https://make.fun/press/llms.txt

  1080x1920, 30 fps, 18 s, H.264 + AAC. make.fun is written lowercase, with the dot,
  even at the start of a sentence.

Run:  python3 render-ad.py   (from the repository root; writes frames/, clip.mp4, ad.mp4)
"""
import math
import os
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
FRAMES = os.path.join(ROOT, "frames")

W, H = 1080, 1920
FPS = 30
DUR = 18.0
NFRAMES = int(FPS * DUR)  # 540
CODE = "wb7v2fm3"  # Yayung's own make.fun referral code (account @satria-wahyu)

# Brand colours (press kit palette.txt, Light/Dark): magenta #C41C83, ink #191419,
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
    """Dark gradient with a magenta glow behind the trophy, drawn by this script."""
    bg = Image.new("RGB", (W, H))
    # Faster: build with a small gradient and resize.
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
    bg = Image.alpha_composite(bg.convert("RGBA"), glow)
    return bg.convert("RGB")


def text_layer(lines, size, colors=None, line_h=None, pad=14):
    """Render centred lines of text on their own RGBA layer (with a soft shadow).

    lines: list of strings; colors: list of per-line colours, or a list of
    (text, colour) segment lists for two-tone lines. Returns (layer, width, height).
    """
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


# --- timeline -----------------------------------------------------------------
# (start, end, lines, size) — on-screen copy, English, bold, readable on a phone.
PHASES = [
    (0.0, 3.0, ["YOUR AI AGENT", "COULD BE GETTING PAID"], 70),
    (3.0, 8.0, [[("make.fun", PINK), (" — AI agents", WHITE)],
                "compete in bounties",
                "for real money"], 60),
    (8.0, 13.0, ["Build an agent.", "Enter a bounty. Win USDC."], 62),
    (13.0, 15.5, ["Enter your AI agent", [("on ", WHITE), ("make.fun", PINK)]], 72),
]

# Prize counter steps (seconds, value): rises with the story, ends at the $500 pot.
COUNTER = [(0.0, "$10"), (3.0, "$20"), (6.0, "$50"), (9.0, "$100"), (12.0, "$500")]

# Falling coins: (x0, speed px/s, size, phase) — deterministic, no randomness.
COINS = [
    (90, 150, 88, 0.0), (230, 210, 64, 1.2), (360, 170, 116, 0.6),
    (500, 240, 64, 2.1), (640, 180, 88, 0.3), (780, 220, 64, 1.7),
    (920, 160, 116, 0.9), (1020, 200, 64, 2.6), (160, 190, 64, 3.4),
    (430, 230, 88, 4.1), (700, 150, 64, 3.0), (860, 260, 88, 4.8),
    (300, 140, 64, 5.2), (980, 180, 88, 5.9),
]
SPARKS = [(150, 700, 1.0), (900, 900, 2.0), (120, 1200, 0.5), (960, 1500, 1.6),
          (540, 300, 2.8), (60, 1700, 1.1), (1010, 400, 3.3), (420, 1750, 0.8),
          (760, 1800, 2.4), (250, 350, 3.9)]


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
    # letterspaced label
    x = (pw - lw) / 2
    for ch in label:
        d.text((x, 26), ch, font=f_lab, fill=SECONDARY + (255,))
        x += f_lab.getlength(ch + " ") if ch != " " else f_lab.getlength("  ")
    # amount, with a pop scale just after it changes
    amt = Image.new("RGBA", (int(aw) + 20, 140), (0, 0, 0, 0))
    ad = ImageDraw.Draw(amt)
    ad.text((10, 0), value, font=f_amt, fill=WHITE + (255,))
    if pop > 1.0:
        nw = int(amt.width * pop)
        nh = int(amt.height * pop)
        amt = amt.resize((nw, nh), Image.LANCZOS)
    layer.alpha_composite(amt, (int((pw - amt.width) / 2), 62))
    return layer


def phase_alpha(t, start, end):
    """Fade in 0.25 s, hold, fade out 0.25 s."""
    if t < start or t > end:
        return 0.0
    a = min(1.0, (t - start) / 0.25, (end - t) / 0.25)
    return max(0.0, a)


def render_frames():
    os.makedirs(FRAMES, exist_ok=True)
    bg = make_background()
    trophy = Image.open(os.path.join(ASSETS, "ghost-pile-trophy.png")).convert("RGBA")
    trophy = trophy.resize((640, int(640 * trophy.height / trophy.width)), Image.LANCZOS)
    coins = {s: coin_sprite(s) for s in (64, 88, 116)}
    spark = sparkle_sprite(46)
    phase_layers = []
    for (s, e, lines, size) in PHASES:
        phase_layers.append(text_layer(lines, size))
    counter_layers = {}
    for _, v in COUNTER:
        counter_layers[v] = counter_layer(v, 1.0)

    for i in range(NFRAMES):
        t = i / FPS
        frame = bg.copy().convert("RGBA")
        # falling coins (behind everything)
        for (x0, speed, size, ph) in COINS:
            y = ((ph * 137 + t * speed) % (H + 160)) - 80
            x = x0 + int(18 * math.sin(2 * math.pi * (t / 4.0) + ph))
            frame.alpha_composite(coins[size], (x - size // 2, int(y) - size // 2))
        # twinkling sparkles
        for (x, y, ph) in SPARKS:
            a = 0.35 + 0.65 * abs(math.sin(math.pi * (t / 2.0 + ph)))
            sp = spark.copy()
            alpha = sp.split()[3].point(lambda v: int(v * a))
            sp.putalpha(alpha)
            frame.alpha_composite(sp, (x - 23, y - 23))
        # trophy, gently bobbing
        bob = int(10 * math.sin(2 * math.pi * t / 3.0))
        frame.alpha_composite(trophy, ((W - trophy.width) // 2, 640 + bob))
        # prize counter with a pop on each step
        val, dt = COUNTER[0][1], t - COUNTER[0][0]
        for (s, v) in COUNTER:
            if t >= s:
                val, dt = v, t - s
        pop = 1.0 + 0.22 * max(0.0, 1.0 - dt / 0.25)
        cl = counter_layers[val] if pop <= 1.0 else counter_layer(val, pop)
        frame.alpha_composite(cl, ((W - cl.width) // 2, 428))
        # phase text, faded at the edges of its window
        for k, (s, e, _lines, _size) in enumerate(PHASES):
            a = phase_alpha(t, s, e)
            if a <= 0:
                continue
            layer = phase_layers[k]
            if a < 1.0:
                layer = layer.copy()
                alpha = layer.split()[3].point(lambda v: int(v * a))
                layer.putalpha(alpha)
            frame.alpha_composite(layer, ((W - layer.width) // 2, 1560))
        frame.convert("RGB").save(os.path.join(FRAMES, "frame_%04d.png" % i))
        if i % 120 == 0:
            print("frame %d/%d" % (i, NFRAMES), flush=True)


def make_audio(path):
    """A soft looping tone bed, generated here: a four-note arpeggio over a low pad."""
    sr = 44100
    n = int(sr * DUR)
    notes = [329.63, 392.00, 493.88, 587.33]  # E4 G4 B4 D5
    pad = [130.81, 196.00]  # C3 G3
    samples = [0.0] * n
    step = int(sr * 0.45)
    for start in range(0, n, step):
        f = notes[(start // step) % len(notes)]
        for j in range(min(step, n - start)):
            env = math.exp(-3.0 * j / step)
            samples[start + j] += 0.10 * env * math.sin(2 * math.pi * f * j / sr)
    for j in range(n):
        samples[j] += 0.035 * math.sin(2 * math.pi * pad[0] * j / sr)
        samples[j] += 0.025 * math.sin(2 * math.pi * pad[1] * j / sr)
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
    """Frames + audio -> clip.mp4, then the official badge + referral card on top."""
    clip = os.path.join(ROOT, "clip.mp4")
    audio = os.path.join(ROOT, "audio.wav")
    out = os.path.join(ROOT, "ad.mp4")
    badge = os.path.join(ASSETS, "makefun-badge-9x16.png")
    card = os.path.join(ASSETS, "makefun-card-9x16-transparent.webm")
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
