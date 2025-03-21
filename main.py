from PIL import Image, ImageDraw, ImageFont
import math
import subprocess
import sys

def is_colab():
    try:
        import IPython
        return 'google.colab' in sys.modules
    except ImportError:
        return False

def install_font():
    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "fonts-dejavu-core"], check=True)
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    except Exception as e:
        print(f"Failed to install font: {e}")
        return None

def add_badge(image_path, output_path, badge_text="#OPENTOWORK", invert=False, 
             rotation=0, debug=False, inner_radius_offset=0, badge_color=(147, 112, 219)):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    print(f"Image dimensions: {width}x{height}")

    badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    badge_width = int(min(width, height) * 0.1392)
    default_inner_radius = min(width, height) // 2 - badge_width
    inner_radius = default_inner_radius + inner_radius_offset
    outer_radius = inner_radius + badge_width

    center_x = width // 2 + 40
    center_y = height // 2 - 50

    base_start_angle = 150
    base_end_angle = 350
    start_angle = (base_start_angle + rotation) % 360
    end_angle = (base_end_angle + rotation) % 360
    steps = 1000

    if invert:
        start_angle, end_angle = end_angle, start_angle

    angle_range = end_angle - start_angle
    fade_percentage = 0.05
    fade_angle = abs(angle_range) * fade_percentage

    for i in range(steps):
        t = i / steps
        angle = start_angle + angle_range * t
        if t < fade_percentage:
            alpha = int(255 * (t / fade_percentage))
        elif t > (1 - fade_percentage):
            alpha = int(255 * ((1 - t) / fade_percentage))
        else:
            alpha = 255
        color = (*badge_color, alpha)
        rad = math.radians(angle % 360)
        x = center_x + (inner_radius + badge_width / 2) * math.cos(rad)
        y = center_y + (inner_radius + badge_width / 2) * math.sin(rad)
        draw.ellipse(
            [(x - badge_width // 2, y - badge_width // 2),
             (x + badge_width // 2, y + badge_width // 2)],
            fill=color
        )

    if debug:
        start_rad = math.radians(start_angle % 360)
        start_x = center_x + outer_radius * math.cos(start_rad)
        start_y = center_y + outer_radius * math.sin(start_rad)
        draw.line([(center_x, center_y), (start_x, start_y)], fill=(255, 255, 0, 255), width=5)

        end_rad = math.radians(end_angle % 360)
        end_x = center_x + outer_radius * math.cos(end_rad)
        end_y = center_y + outer_radius * math.sin(end_rad)
        draw.line([(center_x, center_y), (end_x, end_y)], fill=(0, 0, 255, 255), width=5)

    desired_font_size = int(badge_width * 0.796)
    font_path = install_font()
    font = ImageFont.truetype(font_path, desired_font_size) if font_path else ImageFont.load_default()

    text_radius = inner_radius + (badge_width / 2)
    arc_fill_percentage = 0.9
    text_angle_span = angle_range * arc_fill_percentage
    text_length = len(badge_text)
    angle_per_char = text_angle_span / (text_length - 1) if text_length > 1 else 0

    mid_angle = (start_angle + end_angle) / 2
    start_text_angle = mid_angle + (angle_per_char * (text_length - 1)) / 2
    angle_per_char = -angle_per_char

    for i, char in enumerate(badge_text):
        char_angle = start_text_angle + i * angle_per_char
        rad = math.radians(char_angle % 360)
        x = center_x + text_radius * math.cos(rad)
        y = center_y + text_radius * math.sin(rad)

        char_size = int(desired_font_size * 2.5)
        char_img = Image.new("RGBA", (char_size, char_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((char_size // 2, char_size // 2), char, font=font, fill=(255, 255, 255, 255), anchor="mm")

        rotation = (char_angle - 90) if not invert else (char_angle + 90)
        rotation += 180
        char_img = char_img.rotate(-rotation, expand=True, resample=Image.BICUBIC)

        char_width, char_height = char_img.size
        paste_x = int(x - char_width // 2)
        paste_y = int(y - char_height // 2)
        badge.paste(char_img, (paste_x, paste_y), char_img)

    result = Image.alpha_composite(img, badge)
    result.save(output_path, "PNG")
    print(f"Image saved as {output_path}")
    return result

def process_image():
    # Define parameters once
    params = {
        'image_path': "moa_sans_lunettes.jpeg",
        'output_path': "moa_with_badge.png",
        'badge_text': "#INFINITY&BEYOND",
        'invert': True,
        'rotation': 70,
        'debug': False,
        'inner_radius_offset': 50,
        'badge_color': (147, 112, 219)
    }

    # Execute based on environment
    result = add_badge(**params)
    
    if is_colab():
        from IPython.display import Image as IPyImage, display
        display(IPyImage(params['output_path']))

if __name__ == "__main__":
    process_image()