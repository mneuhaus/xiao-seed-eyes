# GIF Optimization

Before uploading GIFs to the device, optimize them using the provided script:

```bash
python3 optimize_gif.py input_directory output_directory
```

This will:
1. Process all GIF files in the input directory
2. Center-crop each GIF to 240x240 pixels
3. Optimize each GIF using gifsicle
4. Save the results to the output directory

Requirements:
- Python 3 with Pillow package installed
- gifsicle in your system PATH

Example:
```bash
python3 optimize_gif.py path/to/input_gifs path/to/output_gifs
```
