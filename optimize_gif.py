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

    # Use proportional scaling: set the smaller side to 240, then crop the longer side.
    if width < height:
        # Portrait: resize width to 240, calculate new height preserving aspect ratio.
        factor = 240 / float(width)
        new_height = int(math.ceil(height * factor))
        crop_y = (new_height - 240) // 2
        command = [
            "gifsicle",
            "--resize-width", "240",
            f"--crop=0,{crop_y}+240x240",
            "--optimize=3",
            "--lossy=80",
            "--colors=128",
            input_file,
            "-o",
            output_file
        ]
        print(f"Portrait: resizing width to 240, new height {new_height}, crop_y {crop_y}")
    elif width > height:
        # Landscape: resize height to 240, calculate new width proportionally.
        factor = 240 / float(height)
        new_width = int(math.ceil(width * factor))
        crop_x = (new_width - 240) // 2
        command = [
            "gifsicle",
            "--resize-height", "240",
            f"--crop={crop_x},0+240x240",
            "--optimize=3",
            "--lossy=80",
            "--colors=128",
            input_file,
            "-o",
            output_file
        ]
        print(f"Landscape: resizing height to 240, new width {new_width}, crop_x {crop_x}")
    else:
        # Square image: a simple resize will yield a 240x240 output.
        command = [
            "gifsicle",
            "--resize=240x240",
            "--optimize=3",
            "--lossy=80",
            "--colors=128",
            input_file,
            "-o",
            output_file
        ]
        print("Square image: resizing to 240x240")
    
    print("Executing command:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error processing {input_file}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Optimize all GIF files in an input directory for the TFT device: center-crop to 240x240 and optimize with gifsicle"
    )
    parser.add_argument("input_dir", help="Path to the directory containing GIF files (optimized files will get an _o suffix)")
    args = parser.parse_args()

    input_dir = args.input_dir

    if not os.path.isdir(input_dir):
        print(f"Error: input directory {input_dir} does not exist or is not a directory.")
        sys.exit(1)

    gif_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".gif") and not f.lower().endswith("_o.gif")]
    if not gif_files:
        print("No GIF files found in the input directory.")
        sys.exit(0)

    for filename in gif_files:
        input_file = os.path.join(input_dir, filename)
        base, ext = os.path.splitext(filename)
        output_filename = base + "_o" + ext
        output_file = os.path.join(input_dir, output_filename)
        optimize_gif(input_file, output_file)

if __name__ == "__main__":
    main()
