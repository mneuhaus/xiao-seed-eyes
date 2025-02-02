#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from PIL import Image

def optimize_gif(input_file, output_file):
    try:
        with Image.open(input_file) as im:
            width, height = im.size
    except Exception as e:
        print(f"Error opening {input_file}: {e}")
        return False

    if width < 240 or height < 240:
        print(f"Error: {input_file} is smaller than 240x240, skipping.")
        return False

    x_off = (width - 240) // 2
    y_off = (height - 240) // 2
    crop_spec = f"240x240+{x_off}+{y_off}"

    command = ["gifsicle", f"--crop={crop_spec}", "--optimize=3", input_file, "-o", output_file]
    print(f"Processing: {input_file} -> {output_file} ({crop_spec})")
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
