import os
import re
import urllib.request
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
CACHE_DIR = Path(__file__).resolve().parent / ".icon_cache"

# Banner configuration
WIDTH = 1600
HEIGHT = 580
BG_COLOR = (15, 23, 42)          # #0F172A (Clean dark slate)
CARD_BG = (30, 41, 59)           # #1E293B (Subtle surface)
CARD_BORDER = (51, 65, 85)       # #334155 (Muted border)
PILL_BG = (15, 23, 42)           # #0F172A (Inner pill background)
TEXT_PRIMARY = (248, 250, 252)   # #F8FAFC
TEXT_SECONDARY = (148, 163, 184) # #94A3B8
ACCENT_COLOR = (56, 189, 248)    # #38BDF8

DEVICON_BASE = "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons"
SIMPLEICONS_BASE = "https://cdn.simpleicons.org"

CATEGORIES = [
    (
        "Languages",
        [
            ("Kotlin", f"{DEVICON_BASE}/kotlin/kotlin-original.svg"),
            ("Java", f"{DEVICON_BASE}/java/java-original.svg"),
            ("PHP", f"{DEVICON_BASE}/php/php-original.svg"),
            ("JavaScript", f"{DEVICON_BASE}/javascript/javascript-original.svg"),
            ("TypeScript", f"{DEVICON_BASE}/typescript/typescript-original.svg"),
            ("Python", f"{DEVICON_BASE}/python/python-original.svg"),
            ("C#", f"{DEVICON_BASE}/csharp/csharp-original.svg"),
        ],
    ),
    (
        "Frontend",
        [
            ("HTML5", f"{DEVICON_BASE}/html5/html5-original.svg"),
            ("CSS3", f"{DEVICON_BASE}/css3/css3-original.svg"),
            ("Tailwind CSS", f"{DEVICON_BASE}/tailwindcss/tailwindcss-original.svg"),
            ("Bootstrap", f"{DEVICON_BASE}/bootstrap/bootstrap-original.svg"),
            ("React", f"{DEVICON_BASE}/react/react-original.svg"),
            ("Next.js", f"{SIMPLEICONS_BASE}/nextdotjs/FFFFFF"),
            ("Alpine.js", f"{DEVICON_BASE}/alpinejs/alpinejs-original.svg"),
            ("Inertia.js", f"{SIMPLEICONS_BASE}/inertia/9553E9"),
            ("Vite", f"{DEVICON_BASE}/vitejs/vitejs-original.svg"),
        ],
    ),
    (
        "Backend & Frameworks",
        [
            ("Laravel", f"{DEVICON_BASE}/laravel/laravel-original.svg"),
            ("Flask", f"{SIMPLEICONS_BASE}/flask/FFFFFF"),
        ],
    ),
    (
        "Databases",
        [
            ("MySQL", f"{DEVICON_BASE}/mysql/mysql-original.svg"),
            ("SQLite", f"{DEVICON_BASE}/sqlite/sqlite-original.svg"),
            ("Supabase", f"{DEVICON_BASE}/supabase/supabase-original.svg"),
        ],
    ),
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_candidates = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
        if bold
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for path in font_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def normalize_svg_for_dark_bg(name: str, svg_text: str) -> str:
    # Remove shadow overlay gradients that have empty/black stop-color
    svg_text = re.sub(r'<path[^>]*fill-opacity="\.2"[^>]*/>', "", svg_text)

    # Resolve linearGradient / radialGradient url(#id) references to solid stop colors
    # so PyMuPDF renders vibrant colors instead of black fallback.
    gradients = {}
    for match in re.finditer(
        r'<(?:linearGradient|radialGradient)[^>]*\bid="([^"]+)"[^>]*>(.*?)</(?:linearGradient|radialGradient)>',
        svg_text,
        re.DOTALL,
    ):
        grad_id, body = match.group(1), match.group(2)
        stops = re.findall(r'stop-color="([^"]+)"', body)
        if stops:
            gradients[grad_id] = stops[-1] if name == "Kotlin" else stops[0]

    for grad_id, color in gradients.items():
        svg_text = svg_text.replace(f"url(#{grad_id})", color)

    # Contrast adjustments for dark pill backgrounds (#0F172A)
    if name == "Alpine.js":
        svg_text = svg_text.replace("#2d3441", "#cbd5e1")
    elif name == "SQLite":
        svg_text = svg_text.replace("#003956", "#38bdf8")
    elif name == "MySQL":
        svg_text = svg_text.replace("#00618A", "#38bdf8")
    elif name == "Java":
        svg_text = svg_text.replace("#0074BD", "#38bdf8")
    elif name == "Laravel":
        svg_text = svg_text.replace('fill="#f0513f"', 'fill="#FF2D20" stroke="#FF2D20" stroke-width="2.5"')
    elif name == "PHP":
        svg_text = re.sub(r'<path d="([^"]+)"', r'<path fill="#ffffff" d="\1"', svg_text)

    return svg_text


def fetch_icon_image(name: str, url: str, size: int = 28, cache_dir: Path = CACHE_DIR) -> Image.Image:
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in name.lower())
    svg_path = cache_dir / f"{safe_name}.svg"

    if not svg_path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            svg_bytes = resp.read()
        svg_path.write_bytes(svg_bytes)
    else:
        svg_bytes = svg_path.read_bytes()

    svg_text = normalize_svg_for_dark_bg(name, svg_bytes.decode("utf-8", errors="ignore"))
    doc = fitz.open(stream=svg_text.encode("utf-8"), filetype="svg")
    page = doc[0]
    rect = page.rect
    scale = (size * 3) / max(rect.width, rect.height, 1)
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=True)
    img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    img.thumbnail((size, size), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset_x = (size - img.width) // 2
    offset_y = (size - img.height) // 2
    canvas.paste(img, (offset_x, offset_y), img)
    return canvas


def build_banner(output_path: Path = ASSETS_DIR / "social_banner.png") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    banner = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(banner)

    # Outer subtle border
    draw.rounded_rectangle(
        [24, 24, WIDTH - 25, HEIGHT - 25],
        radius=20,
        outline=CARD_BORDER,
        width=2,
    )

    title_font = load_font(50, bold=True)
    subtitle_font = load_font(26, bold=False)
    cat_font = load_font(16, bold=True)
    item_font = load_font(17, bold=False)

    # Header area
    margin_x = 64
    header_y = 52
    title_text = "RDevz PH"
    draw.text((margin_x, header_y), title_text, font=title_font, fill=TEXT_PRIMARY)
    title_bbox = draw.textbbox((margin_x, header_y), title_text, font=title_font)

    # Divider bar and Software Solutions subtitle
    sep_x = title_bbox[2] + 22
    draw.line([(sep_x, header_y + 12), (sep_x, header_y + 52)], fill=ACCENT_COLOR, width=3)
    draw.text(
        (sep_x + 22, header_y + 18),
        "Software Solutions",
        font=subtitle_font,
        fill=ACCENT_COLOR,
    )

    # Horizontal divider below header
    divider_y = 132
    draw.line([(margin_x, divider_y), (WIDTH - margin_x, divider_y)], fill=CARD_BORDER, width=1)

    # Layout metrics
    icon_size = 26
    pill_height = 46
    pill_pad_x = 14
    pill_gap_x = 12
    pill_gap_y = 12
    box_height = 114
    row_gap = 18

    def draw_category_box(x0: int, y0: int, x1: int, y1: int, title: str, items: list) -> None:
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=14,
            fill=CARD_BG,
            outline=CARD_BORDER,
            width=1,
        )
        draw.text((x0 + 22, y0 + 16), title.upper(), font=cat_font, fill=TEXT_SECONDARY)

        cur_x = x0 + 22
        cur_y = y0 + 48
        max_x = x1 - 22

        for label, url in items:
            icon_img = fetch_icon_image(label, url, size=icon_size)
            text_bbox = draw.textbbox((0, 0), label, font=item_font)
            text_w = text_bbox[2] - text_bbox[0]
            pill_w = pill_pad_x + icon_size + 10 + text_w + pill_pad_x

            if cur_x + pill_w > max_x and cur_x > x0 + 22:
                cur_x = x0 + 22
                cur_y += pill_height + pill_gap_y

            draw.rounded_rectangle(
                [cur_x, cur_y, cur_x + pill_w, cur_y + pill_height],
                radius=10,
                fill=PILL_BG,
                outline=CARD_BORDER,
                width=1,
            )

            icon_y = cur_y + (pill_height - icon_size) // 2
            banner.paste(icon_img, (cur_x + pill_pad_x, icon_y), icon_img)

            text_x = cur_x + pill_pad_x + icon_size + 10
            text_y = cur_y + (pill_height - (text_bbox[3] - text_bbox[1])) // 2 - 2
            draw.text((text_x, text_y), label, font=item_font, fill=TEXT_PRIMARY)

            cur_x += pill_w + pill_gap_x

    # Row 1: Languages (Full Width)
    row1_top = 156
    row1_bottom = row1_top + box_height
    draw_category_box(margin_x, row1_top, WIDTH - margin_x, row1_bottom, CATEGORIES[0][0], CATEGORIES[0][1])

    # Row 2: Frontend (Full Width)
    row2_top = row1_bottom + row_gap
    row2_bottom = row2_top + box_height
    draw_category_box(margin_x, row2_top, WIDTH - margin_x, row2_bottom, CATEGORIES[1][0], CATEGORIES[1][1])

    # Row 3: Backend & Frameworks (Left) + Databases (Right)
    row3_top = row2_bottom + row_gap
    row3_bottom = row3_top + box_height
    mid_x = WIDTH // 2 - 10
    draw_category_box(margin_x, row3_top, mid_x, row3_bottom, CATEGORIES[2][0], CATEGORIES[2][1])
    draw_category_box(mid_x + 20, row3_top, WIDTH - margin_x, row3_bottom, CATEGORIES[3][0], CATEGORIES[3][1])

    banner.convert("RGB").save(output_path, quality=95)
    print(f"Saved banner to {output_path}")


if __name__ == "__main__":
    build_banner()

