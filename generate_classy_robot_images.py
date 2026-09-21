#!/usr/bin/env python3
"""
Generate classy cute robot mascot state images and boot splash for Sentinel S3-Box-3 firmware.
Features:
- Cute robot chassis with expressive LED visor face
- Official Tez Solutions chest badge logo
- Pure dark background / transparent alpha for seamless dark UI integration
- State-specific accents (cyan listening waves, purple thought bubbles, speaking waves, red error X_X)
- 160x130 RGBA format for status page mascot
- 320x240 RGBA format for boot splash (loading.png)
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

IMG_DIR = "/home/tez-admin/box3-sentinel/images"
ESPHOME_IMG_DIR = "/home/tez-admin/Esp-Box-VoiceAssistant/images"

# Load source robot assets
im_idle = Image.open(f"{ESPHOME_IMG_DIR}/tez_idle.png").convert("RGBA")
im_err = Image.open(f"{ESPHOME_IMG_DIR}/tez_error.png").convert("RGBA")
im_mont = Image.open(f"{ESPHOME_IMG_DIR}/tez_robot_montage.jpg")

im_listen = Image.open(f"{ESPHOME_IMG_DIR}/tez_listening.png").convert("RGB")
arr_l = np.array(im_listen, dtype=float)

im_think = Image.open(f"{ESPHOME_IMG_DIR}/tez_thinking.png").convert("RGB")
arr_t = np.array(im_think, dtype=float)

im_reply = Image.open(f"{ESPHOME_IMG_DIR}/tez_replying.png").convert("RGB")
arr_r = np.array(im_reply, dtype=float)

def transfer_face(src_arr, base_img):
    out = base_img.copy()
    out_arr = np.array(out, dtype=float)
    visor_bg = np.array([22.0, 26.0, 35.0, 255.0])
    
    # 1. Clear base face features inside the oval visor
    for y in range(72, 130):
        for x in range(115, 205):
            dx = (x - 160) / 42.0
            dy = (y - 100) / 25.0
            if dx*dx + dy*dy <= 1.0:
                p = out_arr[y, x]
                if p[0] > 40 or p[1] > 45 or p[2] > 55:
                    out_arr[y, x] = visor_bg
                    
    # 2. Transfer new face features from src_arr
    for y in range(72, 130):
        for x in range(115, 205):
            dx = (x - 160) / 42.0
            dy = (y - 100) / 25.0
            if dx*dx + dy*dy <= 1.0:
                p = src_arr[y, x]
                diff = np.maximum(p - [22, 26, 35], 0)
                if diff.max() > 20:
                    out_arr[y, x, :3] = p[:3]
                    out_arr[y, x, 3] = 255.0
                    
    return Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))

def add_soundwaves(base_img, src_white_arr, color_rgb=(0, 210, 255)):
    out_arr = np.array(base_img, dtype=float)
    for y in range(240):
        for x in range(320):
            if x < 85 or x > 235:
                diff = 255.0 - src_white_arr[y, x, 0]
                if diff > 8.0:
                    alpha = (diff / 255.0) ** 1.15
                    for c in range(3):
                        out_arr[y, x, c] = np.maximum(out_arr[y, x, c], alpha * color_rgb[c])
                    out_arr[y, x, 3] = 255.0
    return Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))

def add_thought_bubbles(base_img, src_white_arr, color_rgb=(175, 90, 250)):
    out_arr = np.array(base_img, dtype=float)
    for y in range(90):
        for x in range(180, 320):
            diff = 255.0 - src_white_arr[y, x, 1]
            if diff > 10.0:
                alpha = (diff / 230.0) ** 1.1
                for c in range(3):
                    out_arr[y, x, c] = np.maximum(out_arr[y, x, c], alpha * color_rgb[c])
                out_arr[y, x, 3] = 255.0
    return Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))

# Generate the 6 full-size 320x240 dark states
full_idle = im_idle
full_listen = add_soundwaves(transfer_face(arr_l, im_idle), arr_l, color_rgb=(0, 210, 255))
full_think = add_thought_bubbles(transfer_face(arr_t, im_idle), arr_t, color_rgb=(175, 90, 250))
full_reply = add_soundwaves(transfer_face(arr_r, im_idle), arr_r, color_rgb=(56, 189, 248))
full_error = im_err
full_notready = im_mont.crop((0, 240, 320, 480)).convert("RGBA")

# Crop and scale into optimal UI dimensions for status page: 160 x 130
# Center of the robot is at (160, 125)
# Let's crop tightly around the robot: (44, 20, 276, 225) -> width 232, height 205
# Scaling 232x205 down to 160x130 (Lanczos) fits with crisp details!
CROP_BOX = (44, 20, 276, 225)
TARGET_SIZE = (160, 130)

def process_for_ui(full_img):
    cropped = full_img.crop(CROP_BOX)
    resized = cropped.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    return resized

os.makedirs(IMG_DIR, exist_ok=True)

ui_idle = process_for_ui(full_idle)
ui_listen = process_for_ui(full_listen)
ui_think = process_for_ui(full_think)
ui_reply = process_for_ui(full_reply)
ui_error = process_for_ui(full_error)
ui_notready = process_for_ui(full_notready)

ui_idle.save(f"{IMG_DIR}/idle.png")
ui_listen.save(f"{IMG_DIR}/listening.png")
ui_think.save(f"{IMG_DIR}/thinking.png")
ui_reply.save(f"{IMG_DIR}/replying.png")
ui_error.save(f"{IMG_DIR}/error.png")
ui_notready.save(f"{IMG_DIR}/notready.png")

print("Saved 6 state images (160x130) to images/")

# Now create classy 320x240 boot splash: loading.png
splash = Image.new("RGBA", (320, 240), (10, 14, 20, 255))
draw = ImageDraw.Draw(splash)

# Add subtle dark radial background glow in center
for r in range(120, 0, -4):
    alpha = int(28 * (1.0 - r / 120.0))
    glow_col = (20, 45, 80, alpha)
    draw.ellipse((160 - r, 120 - r, 160 + r, 120 + r), fill=glow_col)

# Paste centered robot mascot (scaled slightly compact: 130x106)
robot_splash = full_idle.crop(CROP_BOX).resize((130, 115), Image.Resampling.LANCZOS)
splash.paste(robot_splash, (160 - 65, 55), robot_splash)

# Typography
font_path_b = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
font_path_m = "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf"
font_path_r = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"

f_title = ImageFont.truetype(font_path_b, 20)
f_sub = ImageFont.truetype(font_path_r, 11)
f_status = ImageFont.truetype(font_path_m, 10)

# "S E N T I N E L" spaced header
draw.text((160, 24), "S E N T I N E L", font=f_title, fill=(56, 189, 248, 255), anchor="mm")
draw.text((160, 40), "AI VOICE SATELLITE  |  TEZSOLUTIONS", font=f_sub, fill=(148, 163, 184, 255), anchor="mm")

# Sleek loading pill at bottom
bar_w, bar_h = 140, 6
bx, by = 160 - bar_w // 2, 192
# Track background
draw.rounded_rectangle((bx, by, bx + bar_w, by + bar_h), radius=3, fill=(28, 38, 54, 255))
# Active gradient progress
prog_w = 95
draw.rounded_rectangle((bx, by, bx + prog_w, by + bar_h), radius=3, fill=(56, 189, 248, 255))
# Glowing tip
draw.ellipse((bx + prog_w - 4, by - 1, bx + prog_w + 4, by + bar_h + 1), fill=(186, 230, 253, 255))

draw.text((160, 214), "INITIALIZING SYSTEM...", font=f_status, fill=(203, 213, 225, 255), anchor="mm")

splash.save(f"{IMG_DIR}/loading.png")
print("Saved classy loading.png (320x240) to images/")

# Create a montage of all 7 images for visual inspection
preview = Image.new("RGB", (160 * 4, 130 * 2), (15, 20, 28))
preview.paste(ui_idle, (0, 0))
preview.paste(ui_listen, (160, 0))
preview.paste(ui_think, (320, 0))
preview.paste(ui_reply, (480, 0))
preview.paste(ui_error, (0, 130))
preview.paste(ui_notready, (160, 130))
preview.paste(splash.resize((160, 120)), (320, 135))

preview.save("/home/tez-admin/box3-sentinel/classy_robot_montage.jpg")
print("Saved classy_robot_montage.jpg")
