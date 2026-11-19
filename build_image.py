#!/usr/bin/env python3
"""Compose entry.png, the one-image summary of Wednesday 19 November 2026.

This is a build-time helper (Pillow needed here only; the grader never
imports it). It reads the day's stories from news.json, takes the
seven-panel editorial collage in front-page.png, and renders a newspaper
front page around it: a masthead naming the day, the collage as the
artwork band, then one headline card per story in big bold type that
stays readable at thumbnail size.

The page is written to entry.png next to this file, always 1024x1024
and never over 1 MiB. PNG is preferred; if the PNG does not fit, the
same pixels go out as JPEG bytes under the entry.png name (the rules
tell the two apart by magic bytes and accept either).

Usage: python3 build_image.py
"""

import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
COLLAGE_FILE = ROOT / "front-page.png"
STORIES_FILE = ROOT / "news.json"
TARGET_FILE = ROOT / "entry.png"

PAGE = 1024            # the page is square
LIMIT = 1024 * 1024    # entry size cap in bytes
PAGE_BG = (247, 241, 227)
BAND = (18, 41, 62)
PAPER = (255, 255, 255)
TEXT = (16, 24, 32)
ACCENT = (140, 43, 27)
HIGHLIGHT = (232, 199, 102)
CARD_EDGE = (201, 184, 148)

FONT_PATHS = [
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
]


def load_font(name, size):
    """Find a Liberation font, falling back to the DejaVu twin."""
    for directory in FONT_PATHS:
        candidate = directory / name
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
        dejavu = directory / name.replace("Liberation", "DejaVu")
        if dejavu.exists():
            return ImageFont.truetype(str(dejavu), size)
    raise SystemExit(f"font not found: {name}")


def load_stories():
    """Return (dateline, [(tag, headline), ...]) from news.json."""
    data = json.loads(STORIES_FILE.read_text(encoding="utf-8"))
    cards = [(data["lead"]["tag"], data["lead"]["headline"])]
    cards += [(item["tag"], item["headline"]) for item in data["stories"]]
    return data["dateline"], cards


def split_lines(draw, text, font, width):
    """Wrap a headline by measuring candidate lines with the font."""
    done, pending = [], ""
    for word in text.split():
        trial = f"{pending} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            pending = trial
        else:
            done.append(pending)
            pending = word
    if pending:
        done.append(pending)
    return done


def paint_header(draw, dateline):
    """Navy masthead: paper title on top, the day's date in gold."""
    draw.rectangle((0, 0, PAGE, 126), fill=BAND)
    title = load_font("LiberationSerif-Bold.ttf", 46)
    day = load_font("LiberationSans-Bold.ttf", 33)
    draw.text((PAGE / 2, 10), "THE WORLD IN ONE IMAGE", font=title,
              fill=PAGE_BG, anchor="ma")
    draw.text((PAGE / 2, 68), dateline, font=day, fill=HIGHLIGHT,
              anchor="ma")
    draw.rectangle((0, 126, PAGE, 132), fill=ACCENT)


def paint_art(page):
    """Paste the collage, cover-cropped, as the band under the masthead."""
    art = Image.open(COLLAGE_FILE).convert("RGB")
    band = ImageOps.fit(art, (PAGE - 48, 396), Image.LANCZOS)
    page.paste(band, (24, 144))
    frame = ImageDraw.Draw(page)
    frame.rectangle((24, 144, PAGE - 24, 540), outline=BAND, width=4)


def paint_cards(draw, cards):
    """One white card per story: colour tab, tag chip, headline text."""
    headline_font = load_font("LiberationSans-Bold.ttf", 28)
    chip_font = load_font("LiberationSans-Bold.ttf", 19)
    top = 556
    for index, (tag, headline) in enumerate(cards):
        colour = ACCENT if index == 0 else BAND
        wrapped = split_lines(draw, headline, headline_font, 788)
        height = 34 * len(wrapped) + 16
        draw.rectangle((24, top, PAGE - 24, top + height), fill=PAPER,
                       outline=CARD_EDGE, width=2)
        draw.rectangle((24, top, 36, top + height), fill=colour)
        chip_right = 48 + draw.textlength(tag, font=chip_font) + 30
        draw.rectangle((48, top + 10, chip_right, top + height - 10),
                       fill=colour)
        draw.text((48 + (chip_right - 48) / 2, top + height / 2), tag,
                  font=chip_font, fill=PAPER, anchor="mm")
        line_y = top + 8
        for line in wrapped:
            draw.text((chip_right + 14, line_y), line, font=headline_font,
                      fill=TEXT)
            line_y += 34
        top += height + 8
    if top > PAGE - 52:
        raise SystemExit(f"headline cards overflow the page: end {top}")


def paint_footer(draw, dateline):
    """Closing strip repeats the date so any crop keeps the day."""
    note = load_font("LiberationSans-Bold.ttf", 23)
    draw.rectangle((0, PAGE - 44, PAGE, PAGE), fill=BAND)
    draw.text((PAGE / 2, PAGE - 38),
              f"The whole day in one picture - {dateline.split(', ', 1)[1]}",
              font=note, fill=HIGHLIGHT, anchor="ma")


def encode_under_limit(page):
    """Serialise as PNG, else as the best JPEG that fits the cap."""
    buffer = io.BytesIO()
    page.save(buffer, format="PNG", optimize=True)
    payload = buffer.getvalue()
    if len(payload) <= LIMIT:
        return payload, "PNG"
    quality = 88
    while quality >= 60:
        buffer = io.BytesIO()
        page.save(buffer, format="JPEG", quality=quality, optimize=True,
                  progressive=False, subsampling=1)
        payload = buffer.getvalue()
        if len(payload) <= LIMIT:
            return payload, "JPEG"
        quality -= 4
    raise SystemExit("the page cannot be encoded within 1 MiB")


def main():
    dateline, cards = load_stories()
    page = Image.new("RGB", (PAGE, PAGE), PAGE_BG)
    draw = ImageDraw.Draw(page)
    paint_header(draw, dateline)
    paint_art(page)
    paint_cards(draw, cards)
    paint_footer(draw, dateline)
    payload, kind = encode_under_limit(page)
    TARGET_FILE.write_bytes(payload)
    print(f"Wrote {TARGET_FILE}")
    print(f"format={kind} bytes={len(payload)} dimensions={PAGE}x{PAGE}")


if __name__ == "__main__":
    main()
