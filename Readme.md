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
