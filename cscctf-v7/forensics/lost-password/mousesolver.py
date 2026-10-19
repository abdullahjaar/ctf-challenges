import struct
from PIL import Image, ImageDraw

img = Image.new("RGB", (8000, 8000), "white")
draw = ImageDraw.Draw(img)
x, y = 4000, 4000

with open("mouse_hid.txt") as f:
    for line in f:
        line = line.strip().replace(":", "")
        if len(line) < 12: continue
        b = bytes.fromhex(line)
        buttons = b[0]
        dx = struct.unpack("<h", b[2:4])[0]
        dy = struct.unpack("<h", b[4:6])[0]
        x += dx; y += dy
        if buttons & 1:
            draw.ellipse((x-4, y-4, x+4, y+4), fill="black")

img.crop(img.getbbox()).save("drawing.png")
