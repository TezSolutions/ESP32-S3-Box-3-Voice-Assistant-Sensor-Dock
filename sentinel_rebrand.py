#!/usr/bin/env python3
"""Rebrand box3-sentinel images into the Sentinel (TezSentinel) theme.

Palette from the TezSentinel robot brand:
  brand blue   #1C5FA8   cyan/sky accent #38BDF8
  purple       #A855F7   red             #EF4444
  green        #22C55E   grey (idle)     #6B7A8D (sentinel steel grey)
"""
from PIL import Image, ImageDraw, ImageFont
import os

SRC = os.path.expanduser('~/box3-sentinel/images')
OUT = os.path.expanduser('~/box3-sentinel/images')
os.makedirs(OUT, exist_ok=True)

CYAN = (0x38, 0xBD, 0xF8)
BLUE = (0x1C, 0x5F, 0xA8)
PURPLE = (0xA8, 0x55, 0xF7)
RED = (0xEF, 0x44, 0x44)
STEEL = (0x6B, 0x7A, 0x8D)

def is_cyanish(px):
    r, g, b = px[0], px[1], px[2]
    return b > 120 and g > 100 and r < 0.75 * b  # ESPHome cyan family

def recolor(path, target, out=None):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if is_cyanish(p):
                px[x, y] = (target[0], target[1], target[2], p[3])
    im.save(out or path)

# ---- state icons ----------------------------------------------------------
# error: orange frown -> red ; keep alpha
recolor(os.path.join(SRC, 'error.png'), RED)
# idle/notready: grey -> steel blue-grey (Sentinel idle)
recolor(os.path.join(SRC, 'idle.png'), STEEL)
recolor(os.path.join(SRC, 'notready.png'), STEEL)
# listening/replying: cyan -> Sentinel sky cyan
recolor(os.path.join(SRC, 'listening.png'), CYAN)
recolor(os.path.join(SRC, 'replying.png'), CYAN)
# thinking: cyan -> Sentinel purple (thinking accent)
recolor(os.path.join(SRC, 'thinking.png'), PURPLE)

# ---- loading splash: rebuild header + recolor ------------------------------
load_path = os.path.join(SRC, 'loading.png')
im = Image.open(load_path).convert('RGBA')
W, H = im.size

# 1) recolor the house body / cyan elements to brand blue
px = im.load()
for y in range(H):
    for x in range(W):
        p = px[x, y]
        if is_cyanish(p):
            px[x, y] = (BLUE[0], BLUE[1], BLUE[2], p[3])

BG = (30, 30, 30, 255)
draw = ImageDraw.Draw(im)

# 2) blank old text areas (ESPHome / S3 Box 3 / Loading .....) — all were
#    drawn over the flat #1E1E1E background, so repaint that solid color.
for box in [(98, 38, 158, 80), (60, 112, 262, 158), (95, 185, 220, 215)]:
    x0, y0, x1, y1 = box
    for y in range(y0, min(y1, H)):
        for x in range(x0, min(x1, W)):
            px[x, y] = BG

# 3) replace the 'E' emblem with a white 'S' inside the house (house bbox
#    [19,29]-[77,85] @320x240; emblem ~[36,47]-[59,80])
try:
    f_s = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf', 26)
    f_head = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf', 34)
    f_mid = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf', 30)
    f_load = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf', 20)
except OSError:
    f_s = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    f_head = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
    f_mid = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    f_load = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)

draw.text((48, 60), 'S', font=f_s, fill=(255, 255, 255, 255), anchor='mm')
# 4) draw Sentinel header + device text
draw.text((101, 59), 'Sentinel', font=f_head, fill=CYAN, anchor='lm')
draw.text((160, 135), 'S3 Box 3', font=f_mid, fill=CYAN, anchor='mm')
draw.text((160, 200), 'Loading .....', font=f_load, fill=(255, 255, 255, 255), anchor='mm')

im.save(load_path)
print('done')
