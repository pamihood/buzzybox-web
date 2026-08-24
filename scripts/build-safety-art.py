#!/usr/bin/env python3
"""Build the three objects above the three Safety points on the homepage.

Same principle as build-claim-art.py: the site composes its props out of the
PRODUCT'S OWN ART rather than drawing web illustrations, so the posty repo has
to be checked out beside this one.

Every point on that row is a real object now (2026-08-23). Two of them are
built here; the third, assets/safety-key.png, predates this script and is the
app's own key (samples/ui/homedesk/key_transparent) trimmed to its bounding
box — it is already right, so nothing here touches it.

Unlike the claim props, these are trimmed TIGHT and carry no transparent
headroom. The claim row bakes headroom on purpose, because there the leftover
space encodes each object's size relative to its neighbours. Here the CSS
balances the three by hand (.safety-art--key / --wide), and headroom inside
the PNG just makes an object render smaller than its box for no stated reason
— which is exactly what made the drawers read as the lightest thing in the row.
"""
from PIL import Image, ImageFilter
import os

POSTY = "/Users/pamihood/proj/posty"
WEB   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H     = 244          # ~3x the 5.5rem stage, before the shadow bed is added


def trim(im):
    bb = im.split()[-1].getbbox()
    return im.crop(bb) if bb else im

def load(path, root=POSTY):
    return trim(Image.open(os.path.join(root, path)).convert("RGBA"))

def fit_h(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)

def shadow(im, blur, dy, alpha):
    lay = Image.new("RGBA", (im.width, im.height + dy), (58, 42, 24, 255))
    m = Image.new("L", lay.size, 0)
    m.paste(im.split()[-1].point(lambda v: min(alpha, v)), (0, dy))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(blur)))
    return lay

def bed(im, blur=7, dy=5, alpha=80, pad=14):
    """Stand the object on its own soft shadow, then trim to the result."""
    c = Image.new("RGBA", (im.width + pad * 2, im.height + dy + pad), (0, 0, 0, 0))
    c.alpha_composite(shadow(im, blur, dy, alpha), (pad, 0))
    c.alpha_composite(im, (pad, 0))
    return trim(c)


def build_closed_box():
    """"No public discovery" — a shut box with a brass clasp.

    It went through three candidates. A closed MAILBOX is the most literal
    answer to "no open inboxes", but every one in the app is the red send box:
    its wordmark plate is an unreadable smudge at this size, and a saturated
    red object on a section about safety reads as an alert — the same reason
    the icons here went sage rather than terracotta. A closed DRAWER FRONT is
    flat by construction and rendered as a lavender rectangle, a colour swatch
    rather than a drawer. The box has real dimensional form, says SHUT without
    a caption, and its brass clasp rhymes with the brass key two columns over.
    """
    return bed(fit_h(load("samples/desks/snug_hollow/"
                          "desk_customize_box_closed_snug_hollow.png"), H))


def build_drawers():
    """"Approved contacts only" — the named drawers, retrimmed.

    Composed by build-claim-art.py, which leaves transparent headroom above
    every prop. On this row that headroom is dead weight: the drawers were
    scaled to the stage INCLUDING it, so the art itself came out a third
    smaller than the objects beside it. Same picture, trimmed to its ink.
    """
    return load("assets/claims/claim-approved.png", root=WEB)


if __name__ == "__main__":
    for name, fn in (("safety-closed-box.png", build_closed_box),
                     ("safety-drawers.png",    build_drawers)):
        im = fn()
        im.save(os.path.join(WEB, "assets", name), optimize=True)
        print(f"{name:26s} {im.size}")
