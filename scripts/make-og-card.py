#!/usr/bin/env python3
"""Build assets/og-card.jpg — the 1200x630 image a link to Postmello unfurls as.

Shoots scripts/og-card.html in headless Chrome at 2x and downsamples, rather
than composing the card in PIL. PIL would need font FILES; the site's three
faces come from the Google Fonts CDN, so the only way to guarantee the card is
set in the same Rubik / Nunito / DM Mono as the page it points at is to let a
browser render it. It also means the card is authored in the site's own tokens.

Rerun after any change to the H1, the hero shot, or the type system.
Needs network on first run (the CDN); Chrome caches the fonts afterwards.
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "og-card.html"
OUT = ROOT / "assets" / "og-card.jpg"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if not pathlib.Path(CHROME).exists():
    sys.exit(f"Chrome not found at {CHROME}")

with tempfile.TemporaryDirectory() as tmp:
    shot = pathlib.Path(tmp) / "card@2x.png"
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        # 2x, then downsampled: text rendered at 1200px wide and saved straight
        # to JPEG picks up visible edge artefacts on the thin strokes.
        "--force-device-scale-factor=2",
        "--window-size=1200,630",
        # The fonts are a network fetch; without a budget Chrome can shoot the
        # page before they land and the card silently ships in the fallback face.
        "--virtual-time-budget=15000",
        f"--screenshot={shot}",
        SRC.as_uri(),
    ], check=True, capture_output=True)

    card = Image.open(shot).convert("RGB")
    if card.size != (2400, 1260):
        print(f"  (warning: shot came back {card.size}, expected 2400x1260)")
    card = card.resize((1200, 630), Image.LANCZOS)
    card.save(OUT, quality=88, optimize=True, progressive=True)

print(f"wrote {OUT.relative_to(ROOT)}  1200x630  {OUT.stat().st_size // 1024} KB")
