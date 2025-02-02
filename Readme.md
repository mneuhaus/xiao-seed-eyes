# TFT_eSPI_GifPlayer

## Description
TFT_eSPI_GifPlayer is an Arduino project that plays animated GIFs on a 240×240 TFT display. It reads GIF files from an SD card and provides a built-in web API over WiFi to control playback, manage files (upload, delete), and change settings such as display rotation. A Python tool (optimize_gif.py) is included to optimize and convert GIFs (and even MP4 videos) for best performance on the device.

## Features
• Plays animated GIFs on a 240×240 TFT display using the TFT_eSPI library.
• Utilizes an SD card for file storage and management of GIF assets.
• Offers a web interface/API for browsing, uploading, deleting, and controlling GIF playback.
• Supports interactive display commands (open, close, blink, colorful) for visual effects.
• Provides a Python-based GIF optimization/conversion tool (optimize_gif.py) that leverages gifsicle, ffmpeg, and ImageMagick.
• Persists display rotation settings using the Preferences library.

## Files

- TFT_eSPI_GifPlayer.ino: Main Arduino sketch.
- .gitignore: Git ignore rules.
- CONVENTIONS.md: Coding conventions.
- Readme.md: This file.

## Usage

Open the Arduino project in the Arduino IDE and upload it to your board. Once running, you can access the web interface by connecting to the device's IP address. Use the included optimize_gif.py tool to prepare your GIF files for optimal playback on the device.

## Installation & Flashing

1. Install the Arduino IDE (or PlatformIO) and configure it for your ESP32 board.
2. Install the required libraries (e.g., TFT_eSPI, AnimatedGIF, Preferences).
3. Connect your board via USB and select the proper COM port and board type in the IDE.
4. Open TFT_eSPI_GifPlayer.ino, compile, and flash the firmware.
5. On startup, the device initializes the SD card and WiFi. Monitor Serial output to confirm successful connection.
6. Once running, access the web interface by navigating to the device's IP address in your browser.

## GIF Optimization Tool

The provided optimize_gif.py script optimizes GIF files (or converts MP4s) for the device.

### Requirements
• Python 3 with the Pillow package (install via 'pip3 install Pillow')
• gifsicle, ffmpeg, and ImageMagick must be installed and available in your system PATH.

### Installation for the CLI Tool
For instance, on Ubuntu/Debian you can install the dependencies with:
  sudo apt-get install gifsicle ffmpeg imagemagick
Then install Pillow:
  pip3 install Pillow

### Usage Examples
• Basic GIF Optimization:
  python3 optimize_gif.py path/to/input_gifs path/to/output_gifs
• Optimize with additional rotation (e.g., 90°):
  python3 optimize_gif.py path/to/input_gifs path/to/output_gifs --rotate 90
• Advanced example (converting MP4s, optimizing, and rotating 180°):
  python3 optimize_gif.py ./originals ./optimized --rotate 180

The script processes files with .gif and .mp4 extensions in the specified input directory, generating:
  • Files with the '_o' suffix: optimized for playback.
  • Files with the '_preview' suffix: a preview image from the first GIF frame.
  • If rotation is specified, additional rotated files ('_left+<angle>' and '_right-<angle>') are also created.
