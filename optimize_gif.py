#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import math
from PIL import Image

def optimize_gif(input_file, output_file):
    try:
        with Image.open(input_file) as im:
            width, height = im.size
    except Exception as e:
        print(f"Error opening {input_file}: {e}")
        return False

    # Compute scaling factor so that the resized image covers a 240x240 area.
    # This ensures that the resized image is at least 240 in both dimensions.
    factor = max(240 / width, 240 / height)
    new_width = int(math.ceil(width * factor))
    new_height = int(math.ceil(height * factor))
    # Compute crop offsets (center the crop)
    crop_x = (new_width - 240) // 2
    crop_y = (new_height - 240) // 2

    resize_spec = f"{new_width}x{new_height}"
    crop_spec = f"240x240+{crop_x}+{crop_y}"

    # Build the gifsicle command with resizing then cropping and optimizing
    command = [
        "gifsicle",
        f"--resize={resize_spec}",
        f"--crop={crop_spec}",
        "--optimize=3",
        input_file,
        "-o",
        output_file
    ]
    print(f"Processing: {input_file} -> {output_file} (resize: {resize_spec}, crop: {crop_spec})")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error processing {input_file}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Optimize all GIF files in an input directory for the TFT device: center-crop to 240x240 and optimize with gifsicle"
    )
    parser.add_argument("input_dir", help="Path to the input directory containing GIF files")
    parser.add_argument("output_dir", help="Path to the output directory for optimized GIF files")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(input_dir):
        print(f"Error: input directory {input_dir} does not exist or is not a directory.")
        sys.exit(1)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gif_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".gif")]
    if not gif_files:
        print("No GIF files found in the input directory.")
        sys.exit(0)

    for filename in gif_files:
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)
        optimize_gif(input_file, output_file)

if __name__ == "__main__":
    main()
