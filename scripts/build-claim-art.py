"""Build the four claim props above the four claims on the homepage.

Run from anywhere; writes assets/claims/*.png. Needs the posty repo checked out
beside this one, because every piece is REAL APP ART - the site composes props
out of the product's own objects rather than drawing web illustrations.

Every prop is composed into a canvas of the SAME height and trimmed only on the
sides and bottom, so the transparent headroom that survives is what sets each
object's size relative to the other three. CSS then gives all four one height
and bottom-aligns them; the relative scale is baked here, on purpose, because
it is a drawing decision and not a layout one.
"""
from PIL import Image, ImageDraw, ImageFilter
import os
import tempfile

POSTY = "/Users/pamihood/proj/posty"
WEB   = "/Users/pamihood/proj/buzzybox-web"
OUT   = os.path.join(WEB, "assets/claims")

CANVAS_H = 260          # 3x of the ~87px display box

def op(p): return Image.open(os.path.join(POSTY, p)).convert("RGBA")
def ow(p): return Image.open(os.path.join(WEB, p)).convert("RGBA")

def fit_h(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)

def round_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=r, fill=255)
    return m

def trim(im):
    bb = im.split()[-1].getbbox()
    return im.crop(bb) if bb else im

def trim_sides_and_bottom(im):
    """Keep the transparent headroom (it encodes the object's size); drop the
    rest, so CSS flex-end still stands every prop on one ground line."""
    bb = im.split()[-1].getbbox()
    return im.crop((bb[0], 0, bb[2], bb[3])) if bb else im

def shadow_layer(im, blur, dy, alpha):
    lay = Image.new("RGBA", (im.width, im.height + dy), (58, 42, 24, 255))
    m = Image.new("L", lay.size, 0)
    m.paste(im.split()[-1].point(lambda v: min(alpha, v)), (0, dy))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(blur)))
    return lay

def place(canvas, im, xy, blur=6, dy=4, alpha=95):
    canvas.alpha_composite(shadow_layer(im, blur, dy, alpha), xy)
    canvas.alpha_composite(im, xy)

def canvas(w=900):
    return Image.new("RGBA", (w, CANVAS_H), (0, 0, 0, 0))

# ---------------------------------------------------------------- 1. seaside
def build_stack_pen():
    im = fit_h(trim(op("samples/desks/driftwood_cove/stationery_pen_driftwood_cove.png")), 152)
    C = canvas(im.width + 20)
    place(C, im, (10, CANVAS_H - im.height - 6), blur=6, dy=4, alpha=70)
    return trim_sides_and_bottom(C)

# ---------------------------------------------------------------- 2. japanese
# hinoki_noren mailbox geometry, straight out of its desk_styles config
# (20260807170000_hinoki_mailbox_build_gate.sql): the arch is the opening mail
# sits in, and pileWidthFraction is how wide the app draws that mail.
ARCH = dict(x=0.30, y=0.455, w=0.42, h=0.39, pile_w=0.90)
# Airmail, not one of the Japanese pack's own envelopes. Aizome and asanoha are
# the prettier papers and at this size they are a blue rectangle and a pink one;
# the red-and-blue border is the one envelope that still says MAIL at 20px. It
# is also what the Japanese Garden screenshot happens to show.
ENVELOPE = "samples/envelopes/envelope_airmail_02_front_transparent.png"

def mailbox_with_mail(h):
    box = trim(op("samples/desks/hinoki_noren/mailbox_open_no_nameplate_hinoki_noren.png"))
    W, H = box.size
    ax, ay = ARCH["x"] * W, ARCH["y"] * H
    aw, ah = ARCH["w"] * W, ARCH["h"] * H
    env = op(ENVELOPE)
    env = env.resize((round(aw * ARCH["pile_w"]),
                      round(aw * ARCH["pile_w"] * env.height / env.width)), Image.LANCZOS)
    seated = box.copy()
    ex = round(ax + (aw - env.width) / 2)
    ey = round(ay + ah - env.height - ah * 0.04)      # sits on the arch floor
    # ON TOP of the box: the arch interior is painted, so mail composited
    # behind the asset simply disappears.
    seated.alpha_composite(shadow_layer(env, 7, 5, 90), (ex, ey))
    seated.alpha_composite(env, (ex, ey))
    return fit_h(seated, h)

def paper(path, h, rot, r=13):
    im = fit_h(Image.open(os.path.join(POSTY, path)).convert("RGBA"), h)
    im.putalpha(round_mask(im.size, r))
    pad = Image.new("RGBA", (im.width + 36, im.height + 36), (0, 0, 0, 0))
    pad.alpha_composite(im, (18, 18))
    return pad.rotate(rot, resample=Image.BICUBIC, expand=True)

# How far each piece tucks under the one to its right, in canvas px. The papers
# OVERLAP by a hair rather than sitting apart: two sheets left side by side read
# as a diagram of two papers, and one corner tucked under the other reads as
# paper someone put down. Rotating for expand=True leaves transparent margin, so
# every piece is trimmed to its own ink first and placed off its VISIBLE edge -
# positioning off the padded box is what left a gap here the first time.
PAPER_OVERLAP = 18
BOX_TUCK      = 26

def build_japanese():
    """The mailbox anchors the group and it holds MAIL - an empty box on the
    page that sells receiving letters was the thing missing.

    The two stickers are small and sit ON THE EDGE of a sheet, half off: at
    this size a sticker laid flat on a page just reads as a smudge in the
    middle of the paper, and half-off an edge it still reads as a sticker."""
    C = canvas(940)
    box    = mailbox_with_mail(232)
    moon   = trim(paper("samples/papers/paper_moon_rabbit_01/full.png", 156, 8))
    sakura = trim(paper("samples/papers/paper_sakura_branch_01_landscape/full.png", 124, -6))
    koi    = fit_h(trim(op("samples/stickers/sticker_koi_washi_01.png")), 46)
    oni    = fit_h(trim(op("samples/stickers/sticker_onigiri_washi_01.png")), 44)

    base = CANVAS_H - 10
    # Left margin is not slack: the onigiri hangs off the moon sheet's outer
    # corner, and at x_moon = 4 it fell off the canvas and got trimmed away.
    x_moon   = 56
    x_sakura = x_moon + moon.width - PAPER_OVERLAP
    x_box    = x_sakura + sakura.width - BOX_TUCK

    place(C, moon,   (x_moon,   base - moon.height),   blur=6, dy=4, alpha=70)
    place(C, sakura, (x_sakura, base - sakura.height), blur=6, dy=4, alpha=70)
    place(C, box,    (x_box,    base - box.height),    blur=9, dy=6, alpha=82)
    # Straddling a sheet EDGE, half off - laid flat on the page they read as a
    # smudge at this size, and tucked against an edge they still read as
    # stickers someone put there.
    # They sit at opposite ends and OFF the sakura sheet, which is the prettiest
    # thing in the group and the one surface nothing should cover. The onigiri
    # straddles the moon sheet's outer corner where the whole of it shows; the
    # koi leans on the mailbox plinth, which reads as a sticker someone stuck on
    # the mailbox rather than a fish swimming over a cherry-blossom page.
    place(C, oni, (x_moon - 44, base - oni.height + 2), blur=4, dy=3, alpha=70)
    place(C, koi, (x_box + round(box.width * 0.74), base - koi.height + 4), blur=4, dy=3, alpha=70)
    return trim_sides_and_bottom(C)

# ---------------------------------------------------------------- 3. drawers
# Measured off drawer-row.jpg: the mint front runs y 33..211, each drawer is
# 272 wide on a 280 pitch. Cropping to the paint means no wood rail survives
# above or below the group.
DR_X0, DR_W, DR_PITCH = 4, 272, 280
DR_TOP, DR_BOT, DR_R = 33, 212, 11

def build_drawers():
    """Three drawers overlapped and ROTATED. Rotation is what keeps them
    separate - a straight overlap fuses three rectangles into one long bench,
    the failure the plan charms already recorded."""
    row = ow("assets/drawer-row.jpg")
    cuts = []
    for i in range(3):
        x = DR_X0 + i * DR_PITCH
        d = row.crop((x, DR_TOP, x + DR_W, DR_BOT))
        d.putalpha(round_mask(d.size, DR_R))
        cuts.append(fit_h(trim(d), 122))
    C = canvas(940)
    step = round(cuts[0].width * 0.70)
    base = CANVAS_H - 10
    for i, (c, a) in enumerate(zip(cuts, (-5, 1, 6))):
        pad = Image.new("RGBA", (c.width + 60, c.height + 60), (0, 0, 0, 0))
        pad.alpha_composite(c, (30, 30))
        r = pad.rotate(a, resample=Image.BICUBIC, expand=True)
        place(C, r, (10 + i * step, base - r.height + (6, 16, 0)[i]), blur=6, dy=5, alpha=72)
    return trim_sides_and_bottom(C)

# ---------------------------------------------------------------- 4. bee
def build_bee():
    im = fit_h(trim(op("Buzzybox/Buzzybox/Resources/Assets.xcassets/HomeDesk/"
                       "bee_skep_bed_withbee.imageset/bee_skep_bed_withbee.png")), 176)
    C = canvas(im.width + 20)
    place(C, im, (10, CANVAS_H - im.height - 6), blur=6, dy=4, alpha=60)
    return trim_sides_and_bottom(C)

BUILDERS = {
    "claim-letters.png":     build_stack_pen,
    "claim-imagination.png": build_japanese,
    "claim-approved.png":    build_drawers,
    "claim-putdown.png":     build_bee,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, fn in BUILDERS.items():
        im = fn(); im.save(os.path.join(OUT, name), optimize=True); made.append((name, im))
        print(f"{name:24s} {im.size}")

    # contact sheet, for looking at the set before wiring it in
    CELL, LABEL = 360, 24
    sheet = Image.new("RGB", (CELL * 4, CANVAS_H + 40 + LABEL), (250, 247, 242))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(made):
        p = im.copy(); p.thumbnail((CELL - 30, CANVAS_H))
        sheet.paste(p, (i * CELL + (CELL - p.width) // 2, 20 + (CANVAS_H - p.height)), p)
        d.line([(i*CELL, 20+CANVAS_H), ((i+1)*CELL, 20+CANVAS_H)], fill=(222,213,203))
        d.text((i * CELL + 12, CANVAS_H + 30), f"{name}  {im.size[0]}x{im.size[1]}", fill=(60, 50, 40))
    preview = os.path.join(tempfile.gettempdir(), "claims_preview.png")
    sheet.save(preview)
    print("contact sheet:", preview)
