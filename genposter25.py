"""Render the 25 November 2026 news poster with Pillow.

This is the local design generator.  The competition renderer is kept
separate and can reproduce the composition with Python's standard library.
"""
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


W = H = 1024
PAPER = (246, 241, 228)
NAVY = (18, 35, 58)
RED = (183, 48, 43)
GOLD = (210, 150, 54)
PALE = (232, 225, 208)
MUTED = (78, 88, 96)
WHITE = (255, 252, 241)


def font(size, bold=False):
    names = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    return ImageFont.truetype(names, size)


def text_box(draw, xy, text, fnt, fill=NAVY, width=None, leading=4):
    x, y = xy
    lines = []
    if width:
        # Wrap by measured words.  Character-count wrapping can produce
        # one-letter lines when the available width is small.
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split():
                candidate = word if not line else line + " " + word
                if line and draw.textlength(candidate, font=fnt) > width:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
    else:
        lines = text.split("\n")
    for line in lines:
        while width and draw.textlength(line, font=fnt) > width and len(line) > 1:
            line = line[:-1]
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def icon(draw, kind, box):
    x, y, w, h = box
    cx, cy = x + w // 2, y + h // 2
    if kind == "rocket":
        draw.ellipse((cx - 25, y + 9, cx + 25, y + 106), outline=NAVY, width=7)
        draw.polygon([(cx - 25, y + 75), (cx - 47, y + 111), (cx - 22, y + 103)], fill=RED)
        draw.polygon([(cx + 25, y + 75), (cx + 47, y + 111), (cx + 22, y + 103)], fill=RED)
        draw.ellipse((cx - 8, y + 31, cx + 8, y + 47), fill=GOLD)
        draw.polygon([(cx - 16, y + 108), (cx, y + 148), (cx + 16, y + 108)], fill=GOLD)
        draw.line((x + 18, y + 142, x + 82, y + 142), fill=NAVY, width=6)
        draw.line((x + 100, y + 142, x + 170, y + 142), fill=NAVY, width=6)
    elif kind == "wall":
        for row in range(3):
            yy = y + 35 + row * 37
            start = x + (row % 2) * 22
            for col in range(4):
                draw.rectangle((start + col * 53, yy, start + col * 53 + 45, yy + 27), fill=RED)
        draw.line((x + 25, y + 157, x + w - 20, y + 157), fill=NAVY, width=8)
        draw.text((x + 62, y + 5), "$", font=font(52, True), fill=NAVY)
    elif kind == "flame":
        draw.polygon([(cx, y + 5), (cx - 45, y + 75), (cx - 30, y + 145), (cx, y + 170),
                      (cx + 38, y + 138), (cx + 50, y + 77)], fill=RED)
        draw.polygon([(cx, y + 59), (cx - 20, y + 105), (cx - 7, y + 143),
                      (cx + 23, y + 119), (cx + 22, y + 91)], fill=GOLD)
    elif kind == "refinery":
        draw.rectangle((x + 26, y + 83, x + 164, y + 153), outline=NAVY, width=6)
        for xx in (x + 52, x + 89, x + 126):
            draw.rectangle((xx, y + 50, xx + 15, y + 84), fill=NAVY)
        draw.line((x + 59, y + 50, x + 59, y + 18), fill=RED, width=7)
        draw.line((x + 133, y + 50, x + 133, y + 7), fill=RED, width=7)
        draw.ellipse((x + 49, y + 8, x + 69, y + 28), fill=GOLD)
        draw.ellipse((x + 123, y - 3, x + 143, y + 17), fill=GOLD)
    elif kind == "mine":
        draw.polygon([(x + 20, y + 155), (cx, y + 26), (x + w - 20, y + 155)], fill=NAVY)
        draw.polygon([(x + 53, y + 155), (cx, y + 72), (x + w - 53, y + 155)], fill=PAPER)
        draw.ellipse((cx - 18, y + 95, cx + 18, y + 131), fill=GOLD)
        draw.line((x + 30, y + 157, x + w - 30, y + 157), fill=RED, width=8)
    elif kind == "grid":
        for i in range(4):
            draw.line((x + 30 + i * 42, y + 15, x + 30 + i * 42, y + 155), fill=NAVY, width=4)
            draw.line((x + 30, y + 20 + i * 40, x + 156, y + 20 + i * 40), fill=NAVY, width=4)
        draw.line((x + 102, y + 15, x + 80, y + 70, x + 108, y + 70, x + 85, y + 155), fill=RED, width=8)


def card(im, draw, x, y, w, h, label, headline, body, kind):
    draw.rectangle((x, y, x + w, y + h), fill=WHITE, outline=PALE, width=2)
    draw.rectangle((x, y, x + 7, y + h), fill=RED)
    draw.text((x + 20, y + 13), label, font=font(14, True), fill=RED)
    # The title has a full card width.  Its short, all caps form stays on one line.
    draw.text((x + 20, y + 36), headline, font=font(18, True), fill=NAVY)
    # Render the existing pictogram into a compact top-zone layer.  Several
    # icons use coordinates beyond their nominal box, so resizing the layer
    # gives every card the same hard boundary before the body copy begins.
    icon_layer = Image.new("RGBA", (170, 166), (0, 0, 0, 0))
    icon(ImageDraw.Draw(icon_layer), kind, (0, 0, 170, 166))
    icon_layer = icon_layer.resize((170, 104), Image.Resampling.LANCZOS)
    im.paste(icon_layer, (x + 28, y + 62), icon_layer)
    text_box(draw, (x + 20, y + 181), body, font(14), width=w - 40, leading=2)


def main():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 13), fill=RED)
    d.text((48, 30), "THE WORLD / IN ONE DAY", font=font(20, True), fill=RED)
    d.text((48, 54), "THE DAILY SIGNAL", font=font(66, True), fill=NAVY)
    d.text((50, 126), "WEDNESDAY 25 NOVEMBER 2026", font=font(22, True), fill=NAVY)
    d.text((565, 130), "EVERY STORY FIRST REPORTED 25 NOV 2026", font=font(15, True), fill=RED)
    d.line((48, 166, 976, 166), fill=NAVY, width=5)

    cards = [
        ("CHINA / SPACE", "FOREIGN FIRST", "Shenzhou-24 docked with Tiangong carrying the first foreign astronaut to ride a Chinese spacecraft: a Pakistani astronaut.", "rocket"),
        ("US / TRADE", "TARIFF WALL", "The US proposed surprise new tariffs of up to 20% on imports from 14 economies over subsidized industrial overcapacity.", "wall"),
        ("EGYPT / DISASTER", "CAIRO FIRE", "A fuel tanker overturned and caught fire, killing at least 30 people.", "flame"),
        ("YEMEN / SAUDI", "REFINERY ATTACKED", "Yemen's Houthis attacked Saudi Arabia's largest oil refinery, setting it ablaze, and hit a tower in Riyadh; 11 wounded.", "refinery"),
        ("INDONESIA / DISASTER", "MINE FLOODS", "A flooded West Java gold mine left 9 dead, with 17 miners still trapped.", "mine"),
        ("UKRAINE / RUSSIA", "GRID GOES DARK", "Russia struck Ukraine's grid; Odesa battles blackouts. Leaked Russian data indicate about 490,000 soldiers killed.", "grid"),
    ]
    xs = [48, 290, 532]
    for i, item in enumerate(cards):
        card(im, d, xs[i % 3], 186 + (i // 3) * 294, 225, 276, *item)

    rx, ry, rw = 780, 186, 196
    d.rectangle((rx, ry, rx + rw, 756), fill=NAVY)
    d.text((rx + 16, ry + 17), "ALSO ON", font=font(24, True), fill=WHITE)
    d.text((rx + 16, ry + 47), "25 NOV", font=font(34, True), fill=GOLD)
    d.line((rx + 16, ry + 91, rx + rw - 16, ry + 91), fill=RED, width=4)
    rail = [
        ("MARKETS", "AI doubts sink Asian chip stocks; Kospi falls 6.2%. Dow closes higher after erasing 1,100 points."),
        ("UK / COST-OF-LIVING", "Energy price cap to rise 26% to £2,166 in January."),
        ("VATICAN", "Pope Leo calls COP31's failure ‘troubling’ and urges action."),
        ("US", "Macy's parade postponed by storms; judge blocks birthright order again."),
        ("MIDEAST", "Israeli strike in Gaza City kills a Hamas security chief and his family."),
    ]
    yy = ry + 108
    for label, body in rail:
        d.text((rx + 16, yy), label, font=font(14, True), fill=GOLD)
        yy = text_box(d, (rx + 16, yy + 21), body, font(14), WHITE, rw - 32, 1) + 7

    d.rectangle((48, 794, 976, 806), fill=RED)
    d.text((48, 818), "BY THE NUMBERS", font=font(23, True), fill=RED)
    nums = [("20%", "tariff proposal"), ("30+", "Egypt deaths"), ("9 / 17", "dead / trapped"), ("6.2%", "Kospi fall"), ("£2,166", "January cap"), ("490k", "reported killed")]
    xx = 270
    for value, caption in nums:
        d.text((xx, 812), value, font=font(28, True), fill=NAVY)
        d.text((xx, 846), caption, font=font(14), fill=MUTED)
        xx += 115 if value != "£2,166" else 125
    d.line((48, 875, 976, 875), fill=PALE, width=2)
    d.text((48, 889), "Solomon Islands sign security pact with Australia  •  North Korea orders Swiss office in Pyongyang closed", font=font(16, True), fill=NAVY)
    d.rectangle((48, 930, 976, 974), fill=RED)
    d.text((65, 943), "ALL FACTS FIRST REPORTED 25 NOVEMBER 2026 · DETERMINISTIC RENDER", font=font(16, True), fill=WHITE)
    im.save(Path(__file__).resolve().parent / "entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
