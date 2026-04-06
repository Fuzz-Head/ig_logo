from PIL import Image, ImageDraw


def make_circle(image):
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
    padding_percent=5,
    shape="Square",
    offset_x=0,
    offset_y=0
):

    base = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    reference = min(base.width, base.height)

    new_width = int(reference * (scale_percent / 100))
    ratio = new_width / logo.width
    new_height = int(logo.height * ratio)

    logo = logo.resize((new_width, new_height))

    if shape == "Circle":
        logo = make_circle(logo)

    padding = int(reference * (padding_percent / 100))

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
    else:
        x = (base.width - new_width) // 2
        y = (base.height - new_height) // 2

    x += offset_x
    y += offset_y

    base.paste(logo, (x, y), logo)

    return base


def save_image(image, output_path):
    image.convert("RGB").save(output_path, "JPEG", quality=95)