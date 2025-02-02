# GIF Optimization

Before uploading GIFs to the device, optimize them using the provided script:

```bash
python3 optimize_gif.py input.gif output.gif
```

This will:
1. Center-crop the GIF to 240x240 pixels
2. Optimize the GIF using gifsicle

Requirements:
- Python 3 with Pillow package installed
- gifsicle in your system PATH
