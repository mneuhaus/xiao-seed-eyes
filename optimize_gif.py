#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import math
from PIL import Image

def create_preview(input_file, preview_file):
    try:
        with Image.open(input_file) as im:
            width, height = im.size
    except Exception as e:
        print(f"Error opening {input_file} for preview: {e}")
        return False

    if width < height:
        # Portrait: resize width to 240 and crop vertically.
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
            "#0",   # select only the first frame
            "-o",
            preview_file
        ]
        print(f"Preview Portrait: resizing width to 240, new height {new_height}, crop_y {crop_y}")
    elif width > height:
        # Landscape: resize height to 240 and crop horizontally.
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
            "#0",   # select only the first frame
            "-o",
            preview_file
        ]
        print(f"Preview Landscape: resizing height to 240, new width {new_width}, crop_x {crop_x}")
    else:
        # Square: simply resize.
        command = [
            "gifsicle",
            "--resize=240x240",
            "--optimize=3",
            "--lossy=80",
            "--colors=128",
            input_file,
            "#0",   # select only the first frame
            "-o",
            preview_file
        ]
        print("Preview Square: resizing to 240x240")
    
    print("Executing preview command:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error processing preview for {input_file}")
        return False
    return True

def convert_mp4_to_gif(input_file, output_file):
    # Use ffmpeg to convert MP4 to GIF with scaling and cropping.
    # The filter chain does the following:
    # • If the input is landscape (width >= height), scale using height=240 (width auto-scaled)
    # • If the input is portrait (width < height), scale using width=240 (height auto-scaled)
    # Then, crop from the center to exactly 240x240.
    filter_str = "scale='if(gte(iw,ih),-1,240)':'if(gte(iw,ih),240,-1)',crop=240:240"
    command = [
        "ffmpeg",
        "-y",                # Overwrite output if it exists
        "-hide_banner",
        "-loglevel", "error",
        "-i", input_file,
        "-vf", filter_str,
        output_file
    ]
    print("Executing mp4→gif conversion command:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error converting {input_file} to gif")
        return False
    return True

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
    parser.add_argument("input_dir", help="Path to the directory containing original GIF files")
    parser.add_argument("output_dir", help="Path to the directory where optimized GIFs and previews will be stored")
    parser.add_argument("--rotate", type=int, default=0, help="If set, rotate the optimized GIF by this many degrees. Produces additional _left+<angle>.gif and _right-<angle>.gif files.")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isdir(input_dir):
        print(f"Error: input directory {input_dir} does not exist or is not a directory.")
        sys.exit(1)

    gif_files = [f for f in os.listdir(input_dir) if ((f.lower().endswith(".gif") and not (f.lower().endswith("_o.gif") or f.lower().endswith("_preview.gif"))) or f.lower().endswith(".mp4"))]
    if not gif_files:
        print("No GIF files found in the input directory.")
        sys.exit(0)

    for filename in gif_files:
        base, ext = os.path.splitext(filename)
        if "_preview" in base.lower():
            continue
            
        input_file = os.path.join(input_dir, filename)
        # Determine working file (to be used for optimization)
        working_file = input_file
        ext = ext.lower()
        if(ext == ".mp4"):
            # For MP4, convert it first to a temporary GIF in the output folder
            base, _ = os.path.splitext(filename)
            converted_filename = base + "_converted.gif"
            working_file = os.path.join(output_dir, converted_filename)
            if not convert_mp4_to_gif(input_file, working_file):
                continue   # Skip this file if conversion fails
            ext = ".gif"  # Set extension as gif for further processing
        else:
            base, ext = os.path.splitext(filename)

        # Drive optimization using working_file
        output_filename = base + "_o" + ext
        output_file = os.path.join(output_dir, output_filename)
        optimize_gif(working_file, output_file)
        
        preview_filename = base + "_preview" + ext
        preview_file = os.path.join(output_dir, preview_filename)
        create_preview(working_file, preview_file)

        if args.rotate != 0:
            rotate_angle = args.rotate
            # Build filenames for left and right outputs using the base name
            left_filename = base + f"_left+{rotate_angle}" + ext
            left_filepath = os.path.join(output_dir, left_filename)
            right_filename = base + f"_right-{rotate_angle}" + ext
            right_filepath = os.path.join(output_dir, right_filename)
            
            # Build commands using ImageMagick's "convert"
            left_command = [
                "convert",
                output_file,
                "-coalesce",
                "-rotate", str(rotate_angle),
                "-layers", "optimize",
                "-loop", "0",
                left_filepath
            ]
            right_command = [
                "convert",
                output_file,
                "-coalesce",
                "-rotate", "-" + str(rotate_angle),
                "-layers", "optimize",
                "-loop", "0",
                right_filepath
            ]
            print("Executing left rotation command:", " ".join(left_command))
            result_left = subprocess.run(left_command)
            if result_left.returncode != 0:
                print(f"Error rotating left for {output_file}")
            else:
                print(f"Left rotated file created: {left_filepath}")
            
            print("Executing right rotation command:", " ".join(right_command))
            result_right = subprocess.run(right_command)
            if result_right.returncode != 0:
                print(f"Error rotating right for {output_file}")
            else:
                print(f"Right rotated file created: {right_filepath}")

if __name__ == "__main__":
    main()
