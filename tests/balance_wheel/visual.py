import math
import tempfile

from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def generate_wheel(data: dict):
    if not data:
        raise ValueError("Нет данных для колеса")

    labels = list(data.keys())
    values = [max(1, min(5, int(v))) for v in data.values()]
    count = len(labels)

    if count == 0:
        raise ValueError("Нет данных для колеса")

    size = 1400
    cx = size // 2
    cy = size // 2
    max_radius = 420

    bg_color = (248, 248, 248)
    grid_color = (210, 210, 210)
    axis_color = (190, 190, 190)
    fill_color = (234, 197, 92, 70)
    line_color = (234, 197, 92)
    point_fill = (255, 255, 255)
    text_color = (40, 40, 40)
    label_color = (120, 120, 120)

    img = Image.new("RGBA", (size, size), bg_color)
    draw = ImageDraw.Draw(img, "RGBA")

    font_label = _get_font(24)
    font_value = _get_font(28)
    font_center_big = _get_font(72)
    font_center_small = _get_font(26)

    for level in range(1, 6):
        r = max_radius * level / 5
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            outline=grid_color,
            width=2,
        )

    points = []
    label_points = []

    for i in range(count):
        angle = -math.pi / 2 + (2 * math.pi * i / count)

        x_outer = cx + max_radius * math.cos(angle)
        y_outer = cy + max_radius * math.sin(angle)
        draw.line((cx, cy, x_outer, y_outer), fill=axis_color, width=2)

        value_r = max_radius * values[i] / 5
        px = cx + value_r * math.cos(angle)
        py = cy + value_r * math.sin(angle)
        points.append((px, py))

        label_r = max_radius + 110
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        label_points.append((lx, ly))

    if len(points) > 2:
        draw.polygon(points, fill=fill_color)
        draw.line(points + [points[0]], fill=line_color, width=6)

    point_radius = 22
    for i, (px, py) in enumerate(points):
        draw.ellipse(
            (
                px - point_radius,
                py - point_radius,
                px + point_radius,
                py + point_radius,
            ),
            fill=point_fill,
            outline=line_color,
            width=5,
        )

        value_text = str(values[i])
        bbox = draw.textbbox((0, 0), value_text, font=font_value)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (px - tw / 2, py - th / 2 - 2),
            value_text,
            fill=text_color,
            font=font_value,
        )

    for label, (lx, ly) in zip(labels, label_points):
        bbox = draw.textbbox((0, 0), label, font=font_label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (lx - tw / 2, ly - th / 2),
            label,
            fill=label_color,
            font=font_label,
        )

    avg = round(sum(values) / len(values), 1)
    center_r = 120
    draw.ellipse(
        (cx - center_r, cy - center_r, cx + center_r, cy + center_r),
        fill=(255, 255, 255),
        outline=(225, 225, 225),
        width=3,
    )

    avg_text = str(avg)
    bbox = draw.textbbox((0, 0), avg_text, font=font_center_big)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (cx - tw / 2, cy - th / 2 - 30),
        avg_text,
        fill=text_color,
        font=font_center_big,
    )

    center_text = "Колесо\nбаланса"
    bbox = draw.multiline_textbbox(
        (0, 0),
        center_text,
        font=font_center_small,
        spacing=4,
        align="center",
    )
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.multiline_text(
        (cx - tw / 2, cy + 18),
        center_text,
        fill=text_color,
        font=font_center_small,
        spacing=4,
        align="center",
    )

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_path = temp_file.name
    temp_file.close()

    img = img.convert("RGB")
    img.save(temp_path, format="PNG")

    return temp_path
