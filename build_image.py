#!/usr/bin/env python3.13
"""Compose the one-image front page for Wednesday, 19 November 2026.

This is the build-time renderer behind ``entry.png``.  It reads the day's
editorial choices from ``news.json``, lays them out on a 1024x1024 canvas
around the AI-generated collage stored in ``front-page.png``, and saves
the finished page back to ``entry.png``.

Layout, top to bottom:

1. a masthead band carrying the title and the dateline,
2. a wide band showing the collage artwork,
3. a stack of story cards -- the lead story first, then the rest --
   each card showing a section kicker, a headline and a short summary,
4. a thin footer strip crediting the sources.

Only Pillow is needed, and only while building.  The submitted entry
itself ships the rendered PNG, so the runner never has to execute this
module; it exists so the image can be regenerated or restyled.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

DATA_FILE = HERE / "news.json"
COLLAGE_FILE = HERE / "front-page.png"
OUTPUT_FILE = HERE / "entry.png"

# Canvas geometry, in pixels.
PAGE_W = 1024
PAGE_H = 1024
PAGE_MARGIN = 36
CONTENT_W = PAGE_W - 2 * PAGE_MARGIN

# Vertical budget for each band of the page.
MASTHEAD_H = 108
COLLAGE_H = 300
FOOTER_H = 34
CARD_GAP = 10

# Palette: warm paper, near-black ink, and a single red accent.
PAPER = (247, 243, 234)
INK = (24, 24, 28)
MUTED = (96, 92, 84)
ACCENT = (178, 34, 44)
CARD_BG = (255, 253, 248)
RULE = (196, 188, 172)

TITLE_TEXT = "THE WORLD IN ONE IMAGE"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a scalable font, preferring DejaVu and degrading gracefully."""
    stem = "DejaVuSans-Bold" if bold else "DejaVuSans"
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/{stem}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def read_editorial() -> dict:
    """Parse ``news.json`` and return the whole editorial record."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def all_stories(data: dict) -> list[dict]:
    """Flatten the editorial file into one ordered list of story dicts."""
    lead = data.get("lead")
    rest = list(data.get("stories", []))
    return ([lead] if lead else []) + rest


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Word-wrap ``text`` so every returned line fits within ``max_width``."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def ellipsise(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """Trim ``text`` with an ellipsis until it fits on a single line."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    trimmed = text
    while trimmed and draw.textlength(trimmed + "...", font=font) > max_width:
        trimmed = trimmed.rsplit(" ", 1)[0]
    return trimmed + "..."


# ---------------------------------------------------------------------------
# Band painters -- each draws one horizontal slice of the page
# ---------------------------------------------------------------------------

def paint_masthead(draw: ImageDraw.ImageDraw, dateline: str, y: int) -> int:
    """Draw the title block at ``y`` and return the height it consumed."""
    title_font = load_font(44, bold=True)
    date_font = load_font(19)
    draw.text((PAGE_MARGIN, y), TITLE_TEXT, font=title_font, fill=INK)
    draw.text((PAGE_MARGIN, y + 58), dateline, font=date_font, fill=MUTED)
    rule_y = y + MASTHEAD_H - 8
    draw.line([(PAGE_MARGIN, rule_y), (PAGE_W - PAGE_MARGIN, rule_y)],
              fill=ACCENT, width=3)
    return MASTHEAD_H


def paint_collage(page: Image.Image, y: int) -> int:
    """Paste the AI collage, centre-cropped to the content width, at ``y``."""
    if not COLLAGE_FILE.is_file():
        return 0
    collage = Image.open(COLLAGE_FILE).convert("RGB")
    scale = max(CONTENT_W / collage.width, COLLAGE_H / collage.height)
    resized = collage.resize(
        (round(collage.width * scale), round(collage.height * scale)),
        Image.LANCZOS,
    )
    left = (resized.width - CONTENT_W) // 2
    top = (resized.height - COLLAGE_H) // 2
    cropped = resized.crop((left, top, left + CONTENT_W, top + COLLAGE_H))
    page.paste(cropped, (PAGE_MARGIN, y))
    return COLLAGE_H


def paint_card(
    draw: ImageDraw.ImageDraw,
    story: dict,
    y: int,
    height: int,
) -> None:
    """Draw one story card: accent tab, kicker, headline, then summary."""
    x0, x1 = PAGE_MARGIN, PAGE_W - PAGE_MARGIN
    draw.rounded_rectangle([x0, y, x1, y + height], radius=8, fill=CARD_BG,
                           outline=RULE, width=1)
    draw.rectangle([x0, y, x0 + 6, y + height], fill=ACCENT)

    kicker_font = load_font(13, bold=True)
    headline_font = load_font(20, bold=True)
    body_font = load_font(14)

    inner_x = x0 + 18
    inner_w = CONTENT_W - 30
    cursor = y + 8
    kicker = (story.get("section") or story.get("tag") or "").upper()
    if kicker:
        draw.text((inner_x, cursor), kicker, font=kicker_font, fill=ACCENT)
        cursor += 19

    for line in wrap(draw, story.get("headline", ""), headline_font, inner_w)[:2]:
        draw.text((inner_x, cursor), line, font=headline_font, fill=INK)
        cursor += 24

    for line in wrap(draw, story.get("summary", ""), body_font, inner_w)[:2]:
        draw.text((inner_x, cursor), line, font=body_font, fill=MUTED)
        cursor += 18


def paint_footer(draw: ImageDraw.ImageDraw, sources: Iterable[str], y: int) -> None:
    """Draw the closing strip naming where the day's reporting came from."""
    footer_font = load_font(12)
    draw.line([(PAGE_MARGIN, y), (PAGE_W - PAGE_MARGIN, y)], fill=RULE, width=1)
    credit = "Sources: " + "; ".join(sources)
    draw.text(
        (PAGE_MARGIN, y + 8),
        ellipsise(draw, credit, footer_font, CONTENT_W),
        font=footer_font,
        fill=MUTED,
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def collect_sources(stories: Sequence[dict]) -> list[str]:
    """Pull a short, de-duplicated source list out of the story records."""
    seen: list[str] = []
    for story in stories:
        for source in story.get("sources", []):
            short = source.split(" - ")[0].strip()
            if short and short not in seen:
                seen.append(short)
    return seen[:4]


def card_height_for(story_count: int, available: int) -> int:
    """Split ``available`` vertical pixels evenly across the story cards.

    Guards against a degenerate editorial file: with no stories at all
    there is nothing to lay out, so the height is simply zero.
    """
    if story_count <= 0:
        return 0
    gaps = CARD_GAP * (story_count - 1)
    return (available - gaps) // story_count


def compose() -> Image.Image:
    """Build the complete front page and return it as an image."""
    data = read_editorial()
    stories = all_stories(data)

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    cursor = 18
    cursor += paint_masthead(draw, data.get("dateline", ""), cursor)
    cursor += 10
    cursor += paint_collage(page, cursor)
    cursor += 12

    # Whatever vertical space remains is shared evenly between the cards.
    remaining = PAGE_H - FOOTER_H - cursor - 12
    card_h = card_height_for(len(stories), remaining)
    for story in stories:
        paint_card(draw, story, cursor, card_h)
        cursor += card_h + CARD_GAP

    paint_footer(draw, collect_sources(stories), PAGE_H - FOOTER_H)
    return page


def build() -> Path:
    """Render the page and write it to ``entry.png``; return that path."""
    page = compose()
    page.save(OUTPUT_FILE, format="PNG")
    return OUTPUT_FILE


if __name__ == "__main__":
    written = build()
    print(f"wrote {written.name}: {written.stat().st_size} bytes")
