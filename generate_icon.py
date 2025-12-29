# -*- coding: utf-8 -*-
"""
Generate a robot icon for the AI Chat application
"""

from PIL import Image, ImageDraw
import random
import os

def generate_robot_icon(size=256, output_path="robot_icon.ico"):
    """Generate a random robot icon"""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Random colors
    primary_colors = [
        (42, 157, 143),   # Teal
        (58, 124, 165),   # Blue
        (138, 43, 226),   # Purple
        (255, 107, 107),  # Coral
        (46, 204, 113),   # Green
        (241, 196, 15),   # Yellow
        (52, 152, 219),   # Sky blue
    ]
    
    accent_colors = [
        (80, 250, 123),   # Bright green
        (255, 121, 198),  # Pink
        (139, 233, 253),  # Cyan
        (255, 184, 108),  # Orange
        (189, 147, 249),  # Light purple
    ]
    
    body_color = random.choice(primary_colors)
    eye_color = random.choice(accent_colors)
    antenna_color = random.choice(accent_colors)
    
    # Darker shade for depth
    dark_body = tuple(max(0, c - 40) for c in body_color)
    
    margin = size // 8
    
    # Antenna
    antenna_x = size // 2
    antenna_top = margin
    antenna_bottom = margin + size // 6
    draw.line([(antenna_x, antenna_top + size//12), (antenna_x, antenna_bottom)], 
              fill=antenna_color, width=size//20)
    # Antenna ball
    ball_radius = size // 16
    draw.ellipse([antenna_x - ball_radius, antenna_top, 
                  antenna_x + ball_radius, antenna_top + ball_radius * 2],
                 fill=antenna_color)
    
    # Head (rounded rectangle)
    head_top = antenna_bottom
    head_bottom = head_top + size // 3
    head_left = margin + size // 8
    head_right = size - margin - size // 8
    
    # Draw head with rounded corners
    corner_radius = size // 10
    draw.rounded_rectangle([head_left, head_top, head_right, head_bottom],
                          radius=corner_radius, fill=body_color, outline=dark_body, width=2)
    
    # Eyes
    eye_size = size // 10
    eye_y = head_top + (head_bottom - head_top) // 3
    left_eye_x = head_left + (head_right - head_left) // 3
    right_eye_x = head_right - (head_right - head_left) // 3
    
    # Eye backgrounds (white)
    draw.ellipse([left_eye_x - eye_size, eye_y - eye_size,
                  left_eye_x + eye_size, eye_y + eye_size],
                 fill=(255, 255, 255))
    draw.ellipse([right_eye_x - eye_size, eye_y - eye_size,
                  right_eye_x + eye_size, eye_y + eye_size],
                 fill=(255, 255, 255))
    
    # Eye pupils
    pupil_size = eye_size // 2
    draw.ellipse([left_eye_x - pupil_size, eye_y - pupil_size,
                  left_eye_x + pupil_size, eye_y + pupil_size],
                 fill=eye_color)
    draw.ellipse([right_eye_x - pupil_size, eye_y - pupil_size,
                  right_eye_x + pupil_size, eye_y + pupil_size],
                 fill=eye_color)
    
    # Mouth (smile)
    mouth_y = head_top + (head_bottom - head_top) * 2 // 3
    mouth_width = size // 6
    draw.arc([size//2 - mouth_width, mouth_y - mouth_width//2,
              size//2 + mouth_width, mouth_y + mouth_width//2],
             start=0, end=180, fill=(255, 255, 255), width=size//25)
    
    # Body
    body_top = head_bottom + size // 20
    body_bottom = size - margin
    body_left = margin + size // 6
    body_right = size - margin - size // 6
    
    draw.rounded_rectangle([body_left, body_top, body_right, body_bottom],
                          radius=corner_radius, fill=body_color, outline=dark_body, width=2)
    
    # Body details - buttons/lights
    button_y = body_top + (body_bottom - body_top) // 3
    button_size = size // 20
    for i, offset in enumerate([-size//8, 0, size//8]):
        btn_color = random.choice(accent_colors)
        draw.ellipse([size//2 + offset - button_size, button_y - button_size,
                      size//2 + offset + button_size, button_y + button_size],
                     fill=btn_color)
    
    # Arms
    arm_width = size // 12
    arm_length = size // 5
    arm_y = body_top + size // 10
    
    # Left arm
    draw.rounded_rectangle([body_left - arm_length, arm_y,
                           body_left, arm_y + arm_width * 2],
                          radius=arm_width//2, fill=body_color, outline=dark_body, width=2)
    
    # Right arm
    draw.rounded_rectangle([body_right, arm_y,
                           body_right + arm_length, arm_y + arm_width * 2],
                          radius=arm_width//2, fill=body_color, outline=dark_body, width=2)
    
    # Save as ICO with multiple sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, format='ICO', sizes=icon_sizes)
    
    # Also save as PNG for preview
    png_path = output_path.replace('.ico', '.png')
    img.save(png_path, format='PNG')
    
    print(f"✓ Generated robot icon: {output_path}")
    print(f"✓ Preview saved: {png_path}")
    
    return output_path


if __name__ == "__main__":
    generate_robot_icon()
