#!/usr/bin/env python3
"""Generate 100% original, brand-new graphics and pixel/isometric sprites for AgentForge."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
EMPLOYEE_DIR = ROOT / "assets" / "employees"
FURNITURE_DIR = ROOT / "assets" / "office" / "furniture"
FRONTEND_EMPLOYEE_DIR = ROOT / "frontend" / "public" / "assets" / "employees"
FRONTEND_FURNITURE_DIR = ROOT / "frontend" / "public" / "assets" / "office" / "furniture"

for d in [EMPLOYEE_DIR, FURNITURE_DIR, FRONTEND_EMPLOYEE_DIR, FRONTEND_FURNITURE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def create_avatar(bg_color, hair_color, skin_color, shirt_color, accent_color, accessory="glasses"):
    """Generate a clean, modern, stylized 96x96 agent avatar."""
    img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded background circle
    draw.ellipse([4, 4, 92, 92], fill=bg_color)
    draw.ellipse([5, 5, 91, 91], outline=(255, 255, 255, 40), width=2)

    # Shoulders / Body
    draw.rounded_rectangle([20, 64, 76, 96], radius=14, fill=shirt_color)
    # Collar / tie / accent
    draw.polygon([(48, 64), (42, 82), (48, 92), (54, 82)], fill=accent_color)
    draw.polygon([(48, 64), (44, 72), (48, 76), (52, 72)], fill=(255, 255, 255, 180))

    # Neck
    draw.rectangle([42, 54, 54, 66], fill=skin_color)

    # Head / Face
    draw.ellipse([26, 20, 70, 62], fill=skin_color)

    # Eyes
    draw.ellipse([34, 38, 42, 44], fill=(24, 28, 36))
    draw.ellipse([54, 38, 62, 44], fill=(24, 28, 36))
    # Eye shine
    draw.ellipse([36, 39, 39, 42], fill=(255, 255, 255))
    draw.ellipse([56, 39, 59, 42], fill=(255, 255, 255))

    # Smile
    draw.arc([42, 44, 54, 54], start=10, end=170, fill=(30, 30, 40), width=2)

    # Hair
    if accessory == "beanie":
        draw.rounded_rectangle([23, 12, 73, 34], radius=10, fill=hair_color)
        draw.rounded_rectangle([21, 28, 75, 36], radius=4, fill=accent_color)
    elif accessory == "headset":
        # Hair base
        draw.ellipse([24, 14, 72, 40], fill=hair_color)
        draw.rectangle([24, 24, 32, 44], fill=hair_color)
        draw.rectangle([64, 24, 72, 44], fill=hair_color)
        # Headset band
        draw.arc([22, 12, 74, 50], start=190, end=350, fill=(40, 44, 52), width=4)
        # Headset earpads
        draw.rounded_rectangle([20, 34, 28, 48], radius=3, fill=accent_color)
        draw.rounded_rectangle([68, 34, 76, 48], radius=3, fill=accent_color)
        # Mic
        draw.line([26, 44, 36, 54], fill=(40, 44, 52), width=2)
        draw.ellipse([34, 52, 38, 56], fill=accent_color)
    else:
        # Modern stylish hair
        draw.ellipse([24, 12, 72, 38], fill=hair_color)
        draw.polygon([(24, 26), (36, 14), (60, 14), (72, 26), (68, 36), (48, 22), (28, 36)], fill=hair_color)

    # Glasses / Visor
    if accessory in ("glasses", "beanie"):
        # Frame
        draw.rectangle([31, 35, 45, 47], outline=accent_color, width=2)
        draw.rectangle([51, 35, 65, 47], outline=accent_color, width=2)
        draw.line([45, 40, 51, 40], fill=accent_color, width=2)
        draw.line([26, 39, 31, 39], fill=accent_color, width=2)
        draw.line([65, 39, 70, 39], fill=accent_color, width=2)
        # Lens tint
        draw.rectangle([33, 37, 43, 45], fill=(255, 255, 255, 60))
        draw.rectangle([53, 37, 63, 45], fill=(255, 255, 255, 60))
    elif accessory == "visor":
        draw.rounded_rectangle([30, 36, 66, 46], radius=4, fill=accent_color)
        draw.line([32, 41, 64, 41], fill=(255, 255, 255, 200), width=2)

    return img


def generate_all_avatars():
    configs = {
        "assistant-a.png": ((24, 48, 89), (30, 35, 45), (245, 215, 185), (28, 32, 42), (99, 102, 241), "glasses"),
        "assistant-b.png": ((16, 64, 48), (45, 30, 20), (240, 205, 175), (20, 50, 40), (16, 185, 129), "headset"),
        "assistant-c.png": ((72, 45, 16), (20, 20, 20), (235, 195, 165), (55, 35, 15), (245, 158, 11), "beanie"),
        "assistant-d.png": ((55, 24, 75), (50, 40, 60), (250, 220, 195), (40, 25, 55), (168, 85, 247), "glasses"),
        "assistant-e.png": ((75, 25, 40), (35, 25, 20), (245, 210, 180), (60, 20, 35), (244, 63, 94), "visor"),
        "assistant-g.png": ((18, 55, 65), (25, 35, 30), (240, 205, 175), (20, 45, 50), (6, 182, 212), "headset"),
        "assistant-h.png": ((70, 35, 15), (55, 45, 35), (245, 215, 185), (60, 30, 15), (249, 115, 22), "glasses"),
        "assistant-i.png": ((20, 30, 60), (80, 85, 95), (240, 210, 180), (25, 35, 65), (59, 130, 246), "visor"),
    }
    for filename, params in configs.items():
        avatar = create_avatar(*params)
        avatar.save(EMPLOYEE_DIR / filename, "PNG")
        avatar.save(FRONTEND_EMPLOYEE_DIR / filename, "PNG")
    print(f"Generated {len(configs)} new avatars successfully.")


def generate_office_furniture():
    """Generate high-resolution isometric office furniture assets."""

    # 1. Computer Desk Back (1208 x 664)
    w, h = 1208, 664
    desk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(desk)

    # Isometric desk surface
    # Top diamond coordinates
    top_pts = [(w * 0.5, h * 0.18), (w * 0.92, h * 0.44), (w * 0.5, h * 0.72), (w * 0.08, h * 0.44)]
    # Front-left side
    side_left = [(w * 0.08, h * 0.44), (w * 0.5, h * 0.72), (w * 0.5, h * 0.88), (w * 0.08, h * 0.60)]
    # Front-right side
    side_right = [(w * 0.5, h * 0.72), (w * 0.92, h * 0.44), (w * 0.92, h * 0.60), (w * 0.5, h * 0.88)]

    # Draw legs / frame
    d.rectangle([w * 0.16, h * 0.50, w * 0.20, h * 0.95], fill=(30, 33, 40))
    d.rectangle([w * 0.80, h * 0.50, w * 0.84, h * 0.95], fill=(22, 25, 32))
    d.rectangle([w * 0.48, h * 0.70, w * 0.52, h * 0.98], fill=(26, 29, 36))

    # Desk sides
    d.polygon(side_left, fill=(35, 40, 50))
    d.polygon(side_right, fill=(25, 30, 38))

    # Desk top (Dark brushed carbon texture)
    d.polygon(top_pts, fill=(45, 52, 64))
    d.polygon(top_pts, outline=(70, 80, 98), width=3)

    # LED Neon Edge glow
    d.line([top_pts[3], top_pts[2], top_pts[1]], fill=(99, 102, 241), width=4)

    # Large Desk Mat
    mat_pts = [(w * 0.5, h * 0.32), (w * 0.78, h * 0.50), (w * 0.5, h * 0.65), (w * 0.22, h * 0.50)]
    d.polygon(mat_pts, fill=(20, 22, 28))
    d.polygon(mat_pts, outline=(99, 102, 241, 100), width=2)

    # Dual curved monitors (seen from back/angled)
    # Monitor 1 (Left)
    m1_pts = [(w * 0.30, h * 0.10), (w * 0.50, h * 0.22), (w * 0.50, h * 0.44), (w * 0.30, h * 0.32)]
    d.polygon(m1_pts, fill=(18, 20, 25))
    d.polygon(m1_pts, outline=(60, 65, 80), width=2)
    # Stand
    d.rectangle([w * 0.39, h * 0.36, w * 0.41, h * 0.45], fill=(40, 45, 55))

    # Monitor 2 (Right)
    m2_pts = [(w * 0.50, h * 0.22), (w * 0.70, h * 0.10), (w * 0.70, h * 0.32), (w * 0.50, h * 0.44)]
    d.polygon(m2_pts, fill=(24, 28, 35))
    d.polygon(m2_pts, outline=(70, 78, 95), width=2)
    # Stand
    d.rectangle([w * 0.59, h * 0.36, w * 0.61, h * 0.45], fill=(45, 50, 62))

    # Screen glow from front
    d.line([(w * 0.31, h * 0.34), (w * 0.69, h * 0.34)], fill=(129, 140, 248, 120), width=2)

    # Keyboard & Mouse
    kb_pts = [(w * 0.46, h * 0.50), (w * 0.56, h * 0.56), (w * 0.52, h * 0.59), (w * 0.42, h * 0.53)]
    d.polygon(kb_pts, fill=(15, 16, 20))
    d.polygon(kb_pts, outline=(80, 85, 100), width=1)
    d.ellipse([w * 0.60, h * 0.55, w * 0.63, h * 0.58], fill=(30, 32, 40))

    desk.save(FURNITURE_DIR / "computer-desk-back.png", "PNG")
    desk.save(FRONTEND_FURNITURE_DIR / "computer-desk-back.png", "PNG")

    # 2. Ergonomic Chair Back (416 x 464)
    w, h = 416, 464
    chair_b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(chair_b)
    # Base wheels
    d.ellipse([w * 0.25, h * 0.82, w * 0.75, h * 0.94], fill=(25, 28, 35))
    d.rectangle([w * 0.47, h * 0.68, w * 0.53, h * 0.84], fill=(70, 75, 88))
    # Seat back
    d.rounded_rectangle([w * 0.28, h * 0.56, w * 0.72, h * 0.70], radius=16, fill=(35, 40, 52))
    # Backrest spine & mesh
    d.rounded_rectangle([w * 0.30, h * 0.20, w * 0.70, h * 0.58], radius=24, fill=(28, 32, 42))
    d.rounded_rectangle([w * 0.32, h * 0.22, w * 0.68, h * 0.56], radius=20, fill=(38, 44, 58))
    # Headrest
    d.rounded_rectangle([w * 0.38, h * 0.08, w * 0.62, h * 0.18], radius=12, fill=(28, 32, 42))
    # Spine support
    d.rectangle([w * 0.48, h * 0.18, w * 0.52, h * 0.58], fill=(99, 102, 241))
    chair_b.save(FURNITURE_DIR / "chair-back.png", "PNG")
    chair_b.save(FRONTEND_FURNITURE_DIR / "chair-back.png", "PNG")

    # 3. Ergonomic Chair Front (400 x 504)
    w, h = 400, 504
    chair_f = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(chair_f)
    # Base wheels
    d.ellipse([w * 0.22, h * 0.82, w * 0.78, h * 0.95], fill=(25, 28, 35))
    d.rectangle([w * 0.47, h * 0.68, w * 0.53, h * 0.84], fill=(70, 75, 88))
    # Seat cushion
    d.rounded_rectangle([w * 0.24, h * 0.56, w * 0.76, h * 0.72], radius=20, fill=(48, 56, 72))
    d.rounded_rectangle([w * 0.26, h * 0.58, w * 0.74, h * 0.70], radius=18, fill=(58, 68, 88))
    # Backrest front
    d.rounded_rectangle([w * 0.30, h * 0.18, w * 0.70, h * 0.56], radius=22, fill=(40, 48, 64))
    d.rounded_rectangle([w * 0.33, h * 0.21, w * 0.67, h * 0.53], radius=18, fill=(50, 60, 80))
    # Headrest
    d.rounded_rectangle([w * 0.38, h * 0.06, w * 0.62, h * 0.16], radius=12, fill=(48, 56, 74))
    # Armrests
    d.rounded_rectangle([w * 0.16, h * 0.42, w * 0.24, h * 0.60], radius=8, fill=(30, 35, 45))
    d.rounded_rectangle([w * 0.76, h * 0.42, w * 0.84, h * 0.60], radius=8, fill=(30, 35, 45))
    chair_f.save(FURNITURE_DIR / "chair-front.png", "PNG")
    chair_f.save(FRONTEND_FURNITURE_DIR / "chair-front.png", "PNG")

    # 4. Meeting Table (1064 x 432)
    w, h = 1064, 432
    table = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(table)
    # Legs
    d.rectangle([w * 0.20, h * 0.50, w * 0.24, h * 0.92], fill=(25, 28, 35))
    d.rectangle([w * 0.76, h * 0.50, w * 0.80, h * 0.92], fill=(22, 25, 32))
    # Isometric Table Surface
    t_top = [(w * 0.50, h * 0.10), (w * 0.94, h * 0.44), (w * 0.50, h * 0.78), (w * 0.06, h * 0.44)]
    t_left = [(w * 0.06, h * 0.44), (w * 0.50, h * 0.78), (w * 0.50, h * 0.88), (w * 0.06, h * 0.54)]
    t_right = [(w * 0.50, h * 0.78), (w * 0.94, h * 0.44), (w * 0.94, h * 0.54), (w * 0.50, h * 0.88)]
    d.polygon(t_left, fill=(38, 44, 55))
    d.polygon(t_right, fill=(28, 33, 42))
    d.polygon(t_top, fill=(50, 58, 72))
    d.polygon(t_top, outline=(75, 86, 105), width=3)
    # Center frosted glass inlay
    inlay = [(w * 0.50, h * 0.24), (w * 0.80, h * 0.44), (w * 0.50, h * 0.64), (w * 0.20, h * 0.44)]
    d.polygon(inlay, fill=(25, 35, 50))
    d.polygon(inlay, outline=(99, 102, 241, 160), width=2)
    table.save(FURNITURE_DIR / "meeting-table.png", "PNG")
    table.save(FRONTEND_FURNITURE_DIR / "meeting-table.png", "PNG")

    # 5. Plant (456 x 600)
    w, h = 456, 600
    plant = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(plant)
    # Pot
    pot_pts = [(w * 0.28, h * 0.60), (w * 0.72, h * 0.60), (w * 0.64, h * 0.92), (w * 0.36, h * 0.92)]
    d.polygon(pot_pts, fill=(220, 225, 235))
    d.polygon(pot_pts, outline=(180, 185, 195), width=2)
    # Soil
    d.ellipse([w * 0.28, h * 0.56, w * 0.72, h * 0.64], fill=(60, 45, 35))
    # Monstera Leaves (Lush green)
    leaf_colors = [(16, 185, 129), (5, 150, 105), (4, 120, 87), (52, 211, 153)]
    leaves = [
        ([w * 0.40, h * 0.15, w * 0.60, h * 0.45], leaf_colors[0]),
        ([w * 0.18, h * 0.22, w * 0.42, h * 0.52], leaf_colors[1]),
        ([w * 0.58, h * 0.22, w * 0.82, h * 0.52], leaf_colors[2]),
        ([w * 0.28, h * 0.32, w * 0.52, h * 0.60], leaf_colors[3]),
        ([w * 0.48, h * 0.32, w * 0.72, h * 0.60], leaf_colors[0]),
    ]
    for box, col in leaves:
        d.ellipse(box, fill=col)
        # Leaf stem
        d.line([(box[0] + box[2]) / 2, box[3], w * 0.5, h * 0.58], fill=(30, 90, 60), width=3)
    plant.save(FURNITURE_DIR / "plant.png", "PNG")
    plant.save(FRONTEND_FURNITURE_DIR / "plant.png", "PNG")

    # 6. Sofa (1136 x 496)
    w, h = 1136, 496
    sofa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sofa)
    # Isometric Sofa Back
    s_back = [(w * 0.20, h * 0.12), (w * 0.90, h * 0.40), (w * 0.88, h * 0.55), (w * 0.18, h * 0.27)]
    d.polygon(s_back, fill=(35, 42, 55))
    d.polygon(s_back, outline=(60, 70, 90), width=2)
    # Seat cushions
    s_seat = [(w * 0.18, h * 0.27), (w * 0.88, h * 0.55), (w * 0.72, h * 0.78), (w * 0.04, h * 0.48)]
    d.polygon(s_seat, fill=(45, 55, 72))
    d.polygon(s_seat, outline=(75, 88, 110), width=3)
    # Front base
    s_front = [(w * 0.04, h * 0.48), (w * 0.72, h * 0.78), (w * 0.72, h * 0.88), (w * 0.04, h * 0.58)]
    d.polygon(s_front, fill=(28, 35, 48))
    # Cushions divide lines
    d.line([(w * 0.28, h * 0.38), (w * 0.22, h * 0.58)], fill=(30, 38, 50), width=3)
    d.line([(w * 0.52, h * 0.46), (w * 0.46, h * 0.67)], fill=(30, 38, 50), width=3)
    # Throw Pillow
    pillow = [(w * 0.14, h * 0.34), (w * 0.24, h * 0.30), (w * 0.26, h * 0.42), (w * 0.16, h * 0.46)]
    d.polygon(pillow, fill=(99, 102, 241))
    sofa.save(FURNITURE_DIR / "sofa.png", "PNG")
    sofa.save(FRONTEND_FURNITURE_DIR / "sofa.png", "PNG")

    print("Generated 6 new isometric office furniture assets successfully.")


def generate_logos():
    """Generate modern neon AgentForge logo and brand icons."""
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Outer Hexagon Glow
    cx, cy, r = size // 2, size // 2, 210
    import math
    hex_pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(30, 390, 60)]
    d.polygon(hex_pts, fill=(15, 23, 42))
    d.polygon(hex_pts, outline=(99, 102, 241), width=16)

    # Inner Core
    r2 = 140
    hex_pts2 = [(cx + r2 * math.cos(math.radians(a)), cy + r2 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
    d.polygon(hex_pts2, fill=(30, 27, 75))
    d.polygon(hex_pts2, outline=(16, 185, 129), width=8)

    # Lightning Bolt
    bolt_pts = [
        (cx + 20, cy - 100),
        (cx - 50, cy + 10),
        (cx - 5, cy + 10),
        (cx - 20, cy + 100),
        (cx + 50, cy - 10),
        (cx + 5, cy - 10),
    ]
    d.polygon(bolt_pts, fill=(245, 158, 11))
    d.polygon(bolt_pts, outline=(255, 255, 255), width=4)

    # Save logos
    for target_path in [
        ROOT / "open-factory-logo.png",
        ROOT / "open-factory-header-logo.png",
        ROOT / "workflow-factory-icon.png",
        ROOT / "frontend" / "public" / "open-factory-logo.png",
        ROOT / "frontend" / "public" / "open-factory-header-logo.png",
        ROOT / "frontend" / "public" / "workflow-factory-icon.png",
    ]:
        img.save(target_path, "PNG")

    # Favicon SVG
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <polygon points="32,4 58,19 58,45 32,60 6,45 6,19" fill="#0f172a" stroke="#6366f1" stroke-width="4"/>
  <polygon points="32,16 48,25 48,39 32,48 16,39 16,25" fill="#1e1b4b" stroke="#10b981" stroke-width="2"/>
  <polygon points="34,18 24,33 31,33 28,46 40,31 33,31" fill="#f59e0b"/>
</svg>"""
    for svg_path in [ROOT / "favicon.svg", ROOT / "frontend" / "public" / "favicon.svg"]:
        svg_path.write_text(svg_content, encoding="utf-8")

    print("Generated all brand logos and icons successfully.")


if __name__ == "__main__":
    generate_all_avatars()
    generate_office_furniture()
    generate_logos()
    print("ALL GRAPHICAL ASSETS REBUILT FROM SCRATCH WITH ZERO OLD MATERIAL!")
