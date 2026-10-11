"""
Generate high-resolution PNG logos for CampusInsight using PIL.
Ensures zero SVG parsing issues in Streamlit and crisp rendering across all screens.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).resolve().parent

def get_font(size: int, bold: bool = False):
    """Attempts to load Segoe UI or Arial from Windows Fonts, falling back to default."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_logo(is_dark: bool = False) -> Image.Image:
    # 2x supersampling for ultra crisp anti-aliasing
    scale = 2
    w, h = 540 * scale, 125 * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Palette
    navy = (30, 58, 138, 255) if not is_dark else (96, 165, 250, 255)
    teal = (13, 148, 136, 255) if not is_dark else (45, 212, 191, 255)
    amber = (245, 158, 11, 255)
    blue_bar = (59, 130, 246, 255)
    badge_bg = (248, 250, 252, 255) if not is_dark else (30, 41, 59, 255)
    badge_border = (226, 232, 240, 255) if not is_dark else (51, 65, 85, 255)
    text_primary = (15, 23, 42, 255) if not is_dark else (255, 255, 255, 255)
    text_muted = (100, 116, 139, 255) if not is_dark else (148, 163, 184, 255)

    # 1. Badge Base (x=10, y=12, w=100, h=100)
    bx, by, bw, bh = 12 * scale, 12 * scale, 100 * scale, 100 * scale
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=22 * scale, fill=badge_bg, outline=badge_border, width=2 * scale)

    # 2. Open Book Pages at the base
    cx = bx + bw // 2
    # Left page
    left_page = [
        (cx - 28 * scale, by + 74 * scale),
        (cx - 2 * scale, by + 74 * scale),
        (cx - 2 * scale, by + 56 * scale),
        (cx - 28 * scale, by + 58 * scale)
    ]
    draw.polygon(left_page, fill=navy)
    # Right page
    right_page = [
        (cx + 2 * scale, by + 74 * scale),
        (cx + 28 * scale, by + 74 * scale),
        (cx + 28 * scale, by + 58 * scale),
        (cx + 2 * scale, by + 56 * scale)
    ]
    draw.polygon(right_page, fill=teal)
    # Center spine bookmark
    draw.polygon([
        (cx - 1 * scale, by + 74 * scale),
        (cx + 1 * scale, by + 74 * scale),
        (cx + 1 * scale, by + 81 * scale),
        (cx, by + 78 * scale),
        (cx - 1 * scale, by + 81 * scale)
    ], fill=teal)

    # 3. Analytics Bars rising above book
    # Bar 1
    draw.rounded_rectangle([cx - 18 * scale, by + 46 * scale, cx - 12 * scale, by + 60 * scale], radius=2 * scale, fill=blue_bar)
    # Bar 2
    draw.rounded_rectangle([cx - 8 * scale, by + 40 * scale, cx - 2 * scale, by + 60 * scale], radius=2 * scale, fill=blue_bar)
    # Bar 3
    draw.rounded_rectangle([cx + 2 * scale, by + 34 * scale, cx + 8 * scale, by + 60 * scale], radius=2 * scale, fill=teal)
    # Bar 4
    draw.rounded_rectangle([cx + 12 * scale, by + 28 * scale, cx + 18 * scale, by + 60 * scale], radius=2 * scale, fill=(20, 184, 166, 255))

    # 4. Upward Analytics Arrow
    draw.line([(cx - 20 * scale, by + 54 * scale), (cx + 18 * scale, by + 24 * scale)], fill=amber, width=3 * scale)
    # Arrowhead
    ax, ay = cx + 18 * scale, by + 24 * scale
    draw.polygon([(ax + 5 * scale, ay - 2 * scale), (ax - 4 * scale, ay - 3 * scale), (ax, ay + 4 * scale)], fill=amber)

    # 5. Graduation Cap on top
    # Cap diamond
    cap_top = (cx, by + 12 * scale)
    cap_right = (cx + 22 * scale, by + 20 * scale)
    cap_bottom = (cx, by + 28 * scale)
    cap_left = (cx - 22 * scale, by + 20 * scale)
    draw.polygon([cap_top, cap_right, cap_bottom, cap_left], fill=navy)
    # Cap skull band
    draw.arc([cx - 12 * scale, by + 20 * scale, cx + 12 * scale, by + 28 * scale], 0, 180, fill=navy, width=3 * scale)
    # Tassel
    draw.ellipse([cx - 2 * scale, by + 18 * scale, cx + 2 * scale, by + 22 * scale], fill=amber)
    draw.line([(cx, by + 20 * scale), (cx + 16 * scale, by + 27 * scale)], fill=amber, width=2 * scale)
    draw.ellipse([cx + 14 * scale, by + 27 * scale, cx + 18 * scale, by + 31 * scale], fill=amber)

    # 6. Typography
    font_brand = get_font(38 * scale, bold=True)
    font_sub = get_font(12 * scale, bold=True)

    tx = 130 * scale
    ty = 22 * scale

    # "Campus"
    draw.text((tx, ty), "Campus", font=font_brand, fill=text_primary)
    
    # Calculate width of "Campus"
    bbox_campus = draw.textbbox((tx, ty), "Campus", font=font_brand)
    tx_insight = bbox_campus[2] + 4 * scale
    # "Insight"
    draw.text((tx_insight, ty), "Insight", font=font_brand, fill=teal)

    # Subtitle
    sub_y = ty + 46 * scale
    draw.text((tx + 2 * scale, sub_y), "STUDENT RESULT ANALYSIS & IMPROVEMENT SYSTEM", font=font_sub, fill=text_muted)

    # Accent decorative lines under subtitle
    line_y = sub_y + 22 * scale
    draw.rounded_rectangle([tx + 2 * scale, line_y, tx + 72 * scale, line_y + 3 * scale], radius=2 * scale, fill=teal)
    draw.rounded_rectangle([tx + 78 * scale, line_y, tx + 98 * scale, line_y + 3 * scale], radius=2 * scale, fill=amber)

    # Downsample with Lanczos for smooth anti-aliased finish
    final_img = img.resize((w // scale, h // scale), Image.Resampling.LANCZOS)
    return final_img

if __name__ == "__main__":
    light_logo = draw_logo(is_dark=False)
    light_logo.save(ASSETS_DIR / "campusinsight_logo.png", format="PNG")
    print(f"Saved {ASSETS_DIR / 'campusinsight_logo.png'}")

    dark_logo = draw_logo(is_dark=True)
    dark_logo.save(ASSETS_DIR / "campusinsight_sidebar_logo.png", format="PNG")
    print(f"Saved {ASSETS_DIR / 'campusinsight_sidebar_logo.png'}")
