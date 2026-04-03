from PIL import Image, ImageDraw


def make_circle(image):
    """Convert logo into circular shape"""
    size = (min(image.size),) * 2
    mask = Image.new("L", size, 0)

    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)

    mask = mask.resize(image.size)

    image.putalpha(mask)
    return image


def process_image(
    image_path,
    logo_path,
    position="Top-Left",
    scale_percent=20,
    padding=10,
    shape="Square"   # 👈 NEW
):
    base = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Scale based on smaller dimension
    reference = min(base.width, base.height)

    new_width = int(reference * (scale_percent / 100))
    ratio = new_width / logo.width
    new_height = int(logo.height * ratio)

    logo = logo.resize((new_width, new_height))

    # 🔥 Apply shape
    if shape == "Circle":
        logo = make_circle(logo)

    # Position logic
    if position == "Top-Left":
        x, y = padding, padding

    elif position == "Top-Right":
        x = base.width - new_width - padding
        y = padding

    elif position == "Bottom-Left":
        x = padding
        y = base.height - new_height - padding

    elif position == "Bottom-Right":
        x = base.width - new_width - padding
        y = base.height - new_height - padding

    else:  # Center
        x = (base.width - new_width) // 2
        y = (base.height - new_height) // 2

    base.paste(logo, (x, y), logo)

    return base


def save_image(image, output_path):
    image.convert("RGB").save(output_path, "JPEG", quality=95)