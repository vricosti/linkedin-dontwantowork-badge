from PIL import Image, ImageDraw, ImageFont
import math
import subprocess
import sys

# Check if running in Colab
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

def add_badge(image_path, output_path, badge_type="opentowork", invert=False, rotation=0, debug=False, inner_radius_offset=0):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    print(f"Image dimensions: {width}x{height}")

    badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    if badge_type.lower() == "opentowork":
        color_base = (70, 112, 49)  # #467031 - LinkedIn green
        text = "#OPENTOWORK"
    else:  # dontwantowork
        color_base = (199, 49, 49)  # #C73131 - Red
        text = "#DONTWANTOWORK"

    badge_width = int(min(width, height) * 0.1392)  # Fixed thickness
    default_inner_radius = min(width, height) // 2 - badge_width  # Default inner radius
    inner_radius = default_inner_radius + inner_radius_offset  # Adjustable distance from center
    outer_radius = inner_radius + badge_width  # Outer edge moves with inner_radius
    print(f"Badge width: {badge_width}, Outer radius: {outer_radius}, Inner radius: {inner_radius}")

    center_x = width // 2 + 50
    center_y = height // 2 + 80

    # Define arc in counterclockwise degrees from 0° (positive x-axis)
    base_start_angle = 150
    base_end_angle = 350
    
    # Apply rotation
    start_angle = (base_start_angle + rotation) % 360
    end_angle = (base_end_angle + rotation) % 360
    steps = 1000

    # Adjust direction based on invert
    if invert:
        start_angle, end_angle = end_angle, start_angle  # Reverse to clockwise

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
        color = (*color_base, alpha)
        rad = math.radians(angle % 360)
        x = center_x + (inner_radius + badge_width / 2) * math.cos(rad)  # Midpoint of badge
        y = center_y + (inner_radius + badge_width / 2) * math.sin(rad)
        draw.ellipse(
            [(x - badge_width // 2, y - badge_width // 2),
             (x + badge_width // 2, y + badge_width // 2)],
            fill=color
        )

    # Draw angle indicator lines if debug is True (swapped colors)
    if debug:
        # Yellow line for start_angle (text ends here)
        start_rad = math.radians(start_angle % 360)
        start_x = center_x + outer_radius * math.cos(start_rad)
        start_y = center_y + outer_radius * math.sin(start_rad)
        draw.line([(center_x, center_y), (start_x, start_y)], fill=(255, 255, 0, 255), width=5)

        # Blue line for end_angle (text starts here)
        end_rad = math.radians(end_angle % 360)
        end_x = center_x + outer_radius * math.cos(end_rad)
        end_y = center_y + outer_radius * math.sin(end_rad)
        draw.line([(center_x, center_y), (end_x, end_y)], fill=(0, 0, 255, 255), width=5)

    desired_font_size = int(badge_width * 0.796)
    font_path = install_font()
    font = ImageFont.truetype(font_path, desired_font_size) if font_path else ImageFont.load_default()

    test_img = Image.new("RGBA", (desired_font_size * 2, desired_font_size * 2), (0, 0, 0, 0))
    test_draw = ImageDraw.Draw(test_img)
    test_draw.text((desired_font_size, desired_font_size), "O", font=font, fill=(255, 255, 255, 255), anchor="mm")
    bbox = test_img.getbbox()
    rendered_height = (bbox[3] - bbox[1]) if bbox else 8

    if rendered_height < desired_font_size * 0.5:
        render_font_size = 12
        font = ImageFont.load_default()
        scaling_factor = 100 / rendered_height
    else:
        render_font_size = desired_font_size
        scaling_factor = 1.0

    text_radius = inner_radius + (badge_width / 2)  # Center text within badge
    arc_fill_percentage = 0.9
    text_angle_span = angle_range * arc_fill_percentage
    text_length = len(text)
    angle_per_char = text_angle_span / (text_length - 1) if text_length > 1 else 0
    
    # Text direction: from end_angle (blue) to start_angle (yellow)
    mid_angle = (start_angle + end_angle) / 2
    start_text_angle = mid_angle + (angle_per_char * (text_length - 1)) / 2  # Start at end_angle side
    angle_per_char = -angle_per_char  # Move toward start_angle

    for i, char in enumerate(text):
        char_angle = start_text_angle + i * angle_per_char
        rad = math.radians(char_angle % 360)
        x = center_x + text_radius * math.cos(rad)
        y = center_y + text_radius * math.sin(rad)

        char_size = int(render_font_size * 2.5)
        char_img = Image.new("RGBA", (char_size, char_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((char_size // 2, char_size // 2), char, font=font, fill=(255, 255, 255, 255), anchor="mm")

        if scaling_factor != 1.0:
            new_size = (int(char_img.width * scaling_factor), int(char_img.height * scaling_factor))
            char_img = char_img.resize(new_size, resample=Image.BICUBIC)

        rotation = (char_angle - 90) if not invert else (char_angle + 90)  # Flip orientation
        rotation += 180  # Inside circle adjustment
        char_img = char_img.rotate(-rotation, expand=True, resample=Image.BICUBIC)

        char_width, char_height = char_img.size
        paste_x = int(x - char_width // 2)
        paste_y = int(y - char_height // 2)
        badge.paste(char_img, (paste_x, paste_y), char_img)

    result = Image.alpha_composite(img, badge)
    result.save(output_path, "PNG")
    print(f"Image saved as {output_path}")

def main():
    input_image = "moa_sans_lunettes_bw_centered.jpeg"
    output_image = "moa_with_badge.png"
    add_badge(input_image, output_image, badge_type="dontwantowork", invert=True, rotation=70, debug=False, inner_radius_offset=50)

if is_colab():
    from IPython.display import Image as IPyImage, display
    input_image = "moa_sans_lunettes_bw_centered.jpeg"
    output_image = "moa_with_badge.png"
    add_badge(input_image, output_image, badge_type="dontwantowork", invert=True, rotation=70, debug=False, inner_radius_offset=50)
    display(IPyImage(output_image))
else:
    if __name__ == "__main__":
        main()