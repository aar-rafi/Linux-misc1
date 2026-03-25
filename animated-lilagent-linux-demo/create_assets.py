#!/usr/bin/env python3
"""
create_assets.py — Generate demo walk-cycle PNG frames for Lil Agent (Linux)

Outputs FRAME_COUNT RGBA PNG files (walk_00.png … walk_07.png) into the
assets/ sub-directory next to this script.

Requirements:
    pip install Pillow
    # or on Arch Linux:
    sudo pacman -S python-pillow
"""

import math
import os

from PIL import Image, ImageDraw

# ── Configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

FRAME_COUNT = 8   # number of frames in one walk cycle
W, H = 80, 130    # frame size in pixels (width × height)

# Palette
_SKIN  = (255, 200, 150, 255)
_SHIRT = ( 65, 105, 225, 255)   # royal blue
_PANTS = ( 30,  30, 100, 255)   # dark navy
_SHOE  = ( 50,  30,  10, 255)   # dark brown
_EYES  = ( 30,  30,  30, 255)


# ── Drawing ────────────────────────────────────────────────────────────────────

def _rounded_rect(draw: ImageDraw.ImageDraw,
                  bbox: tuple[int, int, int, int],
                  radius: int,
                  fill: tuple) -> None:
    """Draw a filled rounded rectangle (works with Pillow < 8.2 too)."""
    x0, y0, x1, y1 = bbox
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    for cx, cy in [(x0 + r, y0 + r), (x1 - r, y0 + r),
                   (x0 + r, y1 - r), (x1 - r, y1 - r)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def draw_walk_frame(frame_idx: int, total: int) -> Image.Image:
    """Return a single RGBA walk-cycle frame."""
    t = frame_idx / total
    phase = t * 2 * math.pi

    # Vertical body-bob: rises slightly at mid-stance
    bob = int(-abs(math.sin(phase * 2)) * 3)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2   # horizontal centre

    # ── Head ──────────────────────────────────────────────────────────────────
    HR = 13       # head radius
    hx, hy = cx, 8 + bob
    d.ellipse([hx - HR, hy, hx + HR, hy + HR * 2], fill=_SKIN)
    # Eyes
    for ex in (hx - 7, hx + 4):
        d.ellipse([ex, hy + 9, ex + 4, hy + 13], fill=_EYES)
    # Smile
    d.arc([hx - 5, hy + 13, hx + 5, hy + 19], start=0, end=180,
          fill=(150, 80, 60, 255), width=2)

    # ── Torso ─────────────────────────────────────────────────────────────────
    tx0, ty0 = cx - 14, hy + HR * 2 + 3
    tx1, ty1 = cx + 14, ty0 + 34
    _rounded_rect(d, (tx0, ty0, tx1, ty1), radius=6, fill=_SHIRT)

    # ── Arms ──────────────────────────────────────────────────────────────────
    ARM_LEN = 28
    arm_angle = math.sin(phase) * 0.5   # ±0.5 rad swing

    for sgn in (-1, 1):                  # -1 = left arm, +1 = right arm
        sx = cx + sgn * 14
        sy = ty0 + 6
        # Left arm swings forward with right leg (opposite sign)
        swing = arm_angle * sgn
        ex = int(sx + sgn * 4 + ARM_LEN * math.sin(swing))
        ey = int(sy + ARM_LEN * math.cos(swing))
        d.line([(sx, sy), (ex, ey)], fill=_SHIRT, width=9)
        # Hand
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=_SKIN)

    # ── Legs ──────────────────────────────────────────────────────────────────
    THIGH = 26
    SHIN  = 24
    hip_y = ty1
    leg_angle = math.sin(phase) * 0.55   # ±0.55 rad thigh swing

    for sgn in (-1, 1):                  # -1 = left leg, +1 = right leg
        hx_leg = cx + sgn * 7
        thigh_ang = leg_angle * sgn      # legs swing opposite to each other

        kx = int(hx_leg + THIGH * math.sin(thigh_ang))
        ky = int(hip_y  + THIGH * math.cos(thigh_ang))
        d.line([(hx_leg, hip_y), (kx, ky)], fill=_PANTS, width=12)

        # Shin — slight passive knee bend follows thigh
        shin_ang = thigh_ang * 0.4
        fx = int(kx + SHIN * math.sin(shin_ang))
        fy = int(ky + SHIN * math.cos(shin_ang))
        d.line([(kx, ky), (fx, fy)], fill=_PANTS, width=10)

        # Shoe
        _rounded_rect(d, (fx - 10, fy - 5, fx + 10, fy + 8), radius=4, fill=_SHOE)

    return img


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    print(f"Generating {FRAME_COUNT} walk-cycle frames → {ASSETS_DIR}/")
    for i in range(FRAME_COUNT):
        frame = draw_walk_frame(i, FRAME_COUNT)
        path = os.path.join(ASSETS_DIR, f"walk_{i:02d}.png")
        frame.save(path, "PNG")
        print(f"  ✓  walk_{i:02d}.png")
    print("\nDone!  Run   python lil_agent.py   to start the animation.")


if __name__ == "__main__":
    main()
