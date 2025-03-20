from PIL import Image, ImageDraw, ImageFont
import math
import subprocess

# Install a scalable font in Colab
def install_font():
    try:
        # Install the fonts-dejavu-core package, which includes DejaVuSans.ttf
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "fonts-dejavu-core"], check=True)
        # The font is typically installed at /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    except Exception as e:
        print(f"Failed to install font: {e}")
        return None

def add_badge(image_path, output_path, badge_type="opentowork", invert=False):
    """
    Add either an #OPENTOWORK or #DONTWANTOWORK badge to a profile picture.
    
    Parameters:
    - image_path: Path to the input image
    - output_path: Path to save the modified image
    - badge_type: "opentowork" (green) or "dontwantowork" (red)
    - invert: Whether to mirror the badge horizontally
    """
    # Open the image
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    print(f"Image dimensions: {width}x{height}")

    # Create a transparent overlay for the badge
    badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    # Set color based on badge type
    if badge_type.lower() == "opentowork":
        color_base = (70, 112, 49)  # #467031 - LinkedIn green
        text = "#OPENTOWORK"
    else:  # dontwantowork
        color_base = (199, 49, 49)  # #C73131 - Red
        text = "#DONTWANTOWORK"

    # Calculate the badge thickness and position
    badge_width = int(min(width, height) * 0.1392)  # ~167 pixels for 1200x1600 image
    outer_radius = min(width, height) // 2
    inner_radius = outer_radius - badge_width
    print(f"Badge width: {badge_width}, Outer radius: {outer_radius}, Inner radius: {inner_radius}")

    # Shift the circle downward
    center_x = width // 2
    center_y = height // 2 + 70  # Move 70 pixels down

    # Draw an incomplete circle with fading effect
    start_angle = 310  # -50°
    end_angle = 150   # +150°
    steps = 1000      # Number of steps for smooth gradient

    # Adjust angles for proper drawing direction
    if start_angle > end_angle:
        start_angle -= 360  # Normalize to draw from 310° to 150°
    angle_range = end_angle - start_angle  # 200°

    # Fading portion: 5% on each end of the 200° arc
    fade_percentage = 0.05  # 5% fading on each end (10° total, 5° per side)
    fade_angle = angle_range * fade_percentage  # 5% of 200° = 10°

    for i in range(steps):
        # Calculate the angle and fading
        t = i / steps
        angle = start_angle + angle_range * t
        # Create a fading effect at the edges
        if t < fade_percentage:  # Fade in (first 5%)
            alpha = int(255 * (t / fade_percentage))
        elif t > (1 - fade_percentage):  # Fade out (last 5%)
            alpha = int(255 * ((1 - t) / fade_percentage))
        else:
            alpha = 255
        color = (*color_base, alpha)  # RGB with fading alpha
        rad = math.radians(angle)
        # Mirror the x-coordinate based on invert
        x_mirror = -1 if invert else 1
        x0 = center_x + x_mirror * (outer_radius - badge_width // 2) * math.cos(rad)
        y0 = center_y + (outer_radius - badge_width // 2) * math.sin(rad)
        draw.ellipse(
            [(x0 - badge_width // 2, y0 - badge_width // 2),
             (x0 + badge_width // 2, y0 + badge_width // 2)],
            fill=color
        )

    # Desired font size (in pixels) to achieve a rendered size of 100 pixels
    desired_font_size = int(badge_width * 0.796)  # Adjusted to get rendered size of ~100 pixels
    print(f"Desired font size: {desired_font_size}")

    # Try to install and use a scalable font
    font_path = install_font()
    if font_path:
        try:
            font = ImageFont.truetype(font_path, desired_font_size)
            print(f"Using font: {font_path}, Font size: {desired_font_size}")
        except Exception as e:
            print(f"Failed to load font {font_path}: {e}")
            font = ImageFont.load_default()
            print("Falling back to default font")
    else:
        font = ImageFont.load_default()
        print("Font installation failed, using default font")

    # Verify the actual rendered size of the text
    test_img = Image.new("RGBA", (desired_font_size * 2, desired_font_size * 2), (0, 0, 0, 0))
    test_draw = ImageDraw.Draw(test_img)
    test_draw.text((desired_font_size, desired_font_size), "O", font=font, fill=(255, 255, 255, 255), anchor="mm")
    bbox = test_img.getbbox()
    if bbox:
        rendered_width = bbox[2] - bbox[0]
        rendered_height = bbox[3] - bbox[1]
        print(f"Rendered text size (for 'O'): {rendered_width}x{rendered_height} pixels")
    else:
        print("Could not determine rendered text size")
        rendered_height = 8  # Fallback assumption for default font

    # If the rendered size is too small (e.g., default font), render at a smaller size and scale up
    if rendered_height < desired_font_size * 0.5:  # If rendered size is less than 50% of desired
        print("Rendered text size is too small, rendering at a smaller size and scaling up")
        # Render at a smaller size (e.g., the default font's natural size)
        render_font_size = 12  # Default font renders at ~6-8 pixels, so use a slightly larger size
        font = ImageFont.load_default()
        # Calculate scaling factor to achieve desired rendered size of 100 pixels
        desired_rendered_size = 100
        scaling_factor = desired_rendered_size / rendered_height
        print(f"Scaling factor: {scaling_factor}")
    else:
        render_font_size = desired_font_size
        scaling_factor = 1.0

    # Calculate arc length and text placement
    arc_length = (end_angle - start_angle) * math.pi * inner_radius / 180
    print(f"Arc length: {arc_length} pixels")
    
    # Calculate text spread to fill most of the arc
    arc_fill_percentage = 0.9  # 90% of the arc
    text_arc_length = arc_length * arc_fill_percentage
    
    # Calculate radius for text placement - vertically center within the badge width
    text_radius = inner_radius + (badge_width * 0.5)  # Place text at 50% of badge thickness from inner edge
    
    # Calculate text properties for better placement
    text_length = len(text)
    text_angle_span = (end_angle - start_angle) * arc_fill_percentage
    angle_per_char = text_angle_span / (text_length - 1) if text_length > 1 else 0
    
    # Calculate start angle to center text in arc
    mid_angle = (start_angle + end_angle) / 2
    start_text_angle = mid_angle - (angle_per_char * (text_length - 1)) / 2
    
    print(f"Text angle span: {text_angle_span}, Angle per char: {angle_per_char}")
    print(f"Text starting angle: {start_text_angle}, Text radius: {text_radius}")

    # Place and rotate each character
    for i in enumerate(text):
        char_index = i[0]
        char = i[1]

        # Adjust the angle direction based on invert
        if invert:
            # Read clockwise: from (start_text_angle + text_angle_span) to start_text_angle
            char_angle = (start_text_angle + text_angle_span) - char_index * angle_per_char
        else:
            # Read counterclockwise: from start_text_angle to (start_text_angle + text_angle_span)
            char_angle = start_text_angle + char_index * angle_per_char
        
        rad = math.radians(char_angle)
        
        # Mirror the x-coordinate based on invert
        x_mirror = -1 if invert else 1
        x = center_x + x_mirror * text_radius * math.cos(rad)
        y = center_y + text_radius * math.sin(rad)
        
        # Create a temporary image for this character
        char_size = int(render_font_size * 2.5)
        char_img = Image.new("RGBA", (char_size, char_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        
        # Draw the character centered in its image
        char_draw.text((char_size//2, char_size//2), char, font=font, fill=(255, 255, 255, 255), anchor="mm")
        
        # Scale the character image to the desired size
        if scaling_factor != 1.0:
            new_size = (int(char_img.width * scaling_factor), int(char_img.height * scaling_factor))
            char_img = char_img.resize(new_size, resample=Image.BICUBIC)
        
        # Calculate rotation angle based on character position
        # Align with the tangent of the circle and adjust for readability
        if invert:
            rotation = char_angle + 90  # Align for clockwise reading
        else:
            rotation = char_angle - 90  # Align for counterclockwise reading
        # Since the text is inside the circle, rotate it 180 degrees to make it readable
        rotation += 180
        
        # Rotate the character
        char_img = char_img.rotate(-rotation, expand=True, resample=Image.BICUBIC)
        
        # Paste the character onto the badge
        char_width, char_height = char_img.size
        paste_x = int(x - char_width // 2)
        paste_y = int(y - char_height // 2)
        badge.paste(char_img, (paste_x, paste_y), char_img)

    # Combine the original image with the badge overlay
    result = Image.alpha_composite(img, badge)

    # Save the output
    result.save(output_path, "PNG")
    print(f"Image saved as {output_path}")

# Usage in Colab
input_image = "moa_sans_lunettes_bw.jpeg"
output_image = "moa_with_badge.png"
add_badge(input_image, output_image, badge_type="dontwantowork", invert=False)  # Red badge, inverted

# Optional: Display the result in Colab
from IPython.display import Image as IPyImage
display(IPyImage(output_image))