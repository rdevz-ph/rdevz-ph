import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

# Render at 3x resolution for crisp anti-aliasing, then downsample to 800x800
FINAL_SIZE = 800
SCALE = 3
SIZE = FINAL_SIZE * SCALE

BG_COLOR = (15, 23, 42)          # #0F172A (Dark slate background)
BADGE_BG = (30, 41, 59)          # #1E293B (Inner surface)
BORDER_COLOR = (51, 65, 85)      # #334155 (Subtle border)
TEXT_PRIMARY = (248, 250, 252)   # #F8FAFC (Crisp white)
TEXT_SECONDARY = (148, 163, 184) # #94A3B8 (Muted slate)
ACCENT_COLOR = (56, 189, 248)    # #38BDF8 (Sky blue accent)


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        candidates = [
            "C:/Windows/Fonts/CascadiaCode.ttf",
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
        ]
    elif bold:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_chevron(draw: ImageDraw.ImageDraw, cx: int, cy: int, w: int, h: int, thickness: int, direction: int, color: tuple) -> None:
    """Draw a clean geometric '<' (direction=-1) or '>' (direction=1) code bracket."""
    half_h = h // 2
    x_tip = cx + direction * (w // 2)
    x_base = cx - direction * (w // 2)

    draw.line([(x_base, cy - half_h), (x_tip, cy)], fill=color, width=thickness, joint="curve")
    draw.line([(x_tip, cy), (x_base, cy + half_h)], fill=color, width=thickness, joint="curve")

    r = thickness // 2
    for px, py in [(x_base, cy - half_h), (x_tip, cy), (x_base, cy + half_h)]:
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color)


def build_logo(output_path: Path = ASSETS_DIR / "logo.png") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    center = SIZE // 2

    # Outer circular badge (safe for both square and circular social profile crops)
    outer_r = int(340 * SCALE)
    draw.ellipse(
        [center - outer_r, center - outer_r, center + outer_r, center + outer_r],
        fill=BADGE_BG,
        outline=BORDER_COLOR,
        width=3 * SCALE,
    )

    # Subtle inner ring
    inner_r = int(316 * SCALE)
    draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        outline=(38, 52, 74),
        width=1 * SCALE,
    )

    # Central Emblem: Geometric '< R / >' mark
    emblem_cy = int(315 * SCALE)
    bracket_w = int(68 * SCALE)
    bracket_h = int(156 * SCALE)
    stroke_w = int(22 * SCALE)

    # Left bracket '<' in accent blue
    draw_chevron(
        draw,
        cx=center - int(184 * SCALE),
        cy=emblem_cy,
        w=bracket_w,
        h=bracket_h,
        thickness=stroke_w,
        direction=-1,
        color=ACCENT_COLOR,
    )

    # Right bracket '>' in accent blue
    draw_chevron(
        draw,
        cx=center + int(184 * SCALE),
        cy=emblem_cy,
        w=bracket_w,
        h=bracket_h,
        thickness=stroke_w,
        direction=1,
        color=ACCENT_COLOR,
    )

    # Center bold 'R' monogram
    r_font = load_font(int(205 * SCALE), bold=True)
    r_text = "R"
    r_bbox = draw.textbbox((0, 0), r_text, font=r_font)
    r_w = r_bbox[2] - r_bbox[0]
    r_h = r_bbox[3] - r_bbox[1]
    r_x = center - r_w // 2 - r_bbox[0] - int(34 * SCALE)
    r_y = emblem_cy - r_h // 2 - r_bbox[1]
    draw.text((r_x, r_y), r_text, font=r_font, fill=TEXT_PRIMARY)

    # Forward slash '/' next to R
    slash_top_x = center + int(102 * SCALE)
    slash_top_y = emblem_cy - int(74 * SCALE)
    slash_bot_x = center + int(62 * SCALE)
    slash_bot_y = emblem_cy + int(74 * SCALE)
    draw.line(
        [(slash_top_x, slash_top_y), (slash_bot_x, slash_bot_y)],
        fill=ACCENT_COLOR,
        width=int(18 * SCALE),
    )
    sr = int(9 * SCALE)
    draw.ellipse([slash_top_x - sr, slash_top_y - sr, slash_top_x + sr, slash_top_y + sr], fill=ACCENT_COLOR)
    draw.ellipse([slash_bot_x - sr, slash_bot_y - sr, slash_bot_x + sr, slash_bot_y + sr], fill=ACCENT_COLOR)

    # Horizontal subtle divider line
    div_y = int(465 * SCALE)
    div_half_w = int(150 * SCALE)
    draw.line([(center - div_half_w, div_y), (center + div_half_w, div_y)], fill=BORDER_COLOR, width=2 * SCALE)

    # Brand Wordmark: "RDevz" (white) + "PH" (accent blue)
    brand_font = load_font(int(68 * SCALE), bold=True)
    part1 = "RDevz "
    part2 = "PH"
    b1 = draw.textbbox((0, 0), part1, font=brand_font)
    b2 = draw.textbbox((0, 0), part2, font=brand_font)
    w1 = b1[2] - b1[0]
    w2 = b2[2] - b2[0]
    total_w = w1 + w2

    text_start_x = center - total_w // 2
    text_y = int(492 * SCALE)
    draw.text((text_start_x, text_y), part1, font=brand_font, fill=TEXT_PRIMARY)
    draw.text((text_start_x + w1, text_y), part2, font=brand_font, fill=ACCENT_COLOR)

    # Subtitle: SOFTWARE SOLUTIONS
    sub_font = load_font(int(21 * SCALE), bold=True)
    sub_text = "SOFTWARE SOLUTIONS"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text((center - sub_w // 2, int(588 * SCALE)), sub_text, font=sub_font, fill=TEXT_SECONDARY)

    # Downsample with Lanczos filter and keep RGBA transparency outside the circle
    final_img = canvas.resize((FINAL_SIZE, FINAL_SIZE), Image.Resampling.LANCZOS)
    final_img.save(output_path)
    print(f"Saved logo to {output_path}")


if __name__ == "__main__":
    build_logo()

