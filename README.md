# NMR Multi-Figure 1D Plot

A Python utility for plotting multiple NMR (Nuclear Magnetic Resonance) spectral data files in a single figure with multiple subplots.

## Features

- Load and plot multiple NMR data files (.txt format)
- Interactive file selection via GUI dialog
- Automatic x-axis range extraction from file headers
- Proper NMR spectral display with reversed x-axis (ppm scale)
- Scientific notation formatting for intensity values
- Error handling for malformed files
- Optimized for large datasets

## Requirements

- Python 3.x
- NumPy
- Matplotlib
- tkinter (usually included with Python)

## Installation

```bash
pip install numpy matplotlib
```

## Usage

```bash
python main.py
```

1. A file dialog will open
2. Select one or more `.txt` NMR data files
3. Plots will display in a stacked subplot layout

## File Format

Expected NMR data file format:

```
# LEFT = X.XX ppm, RIGHT = Y.YY ppm
# SIZE = 1234 (points)
intensity_value_1
intensity_value_2
...
```

## Output

The script generates a matplotlib figure with:
- One subplot per selected file
- Intensity values in scientific notation
- Properly formatted NMR spectral display

## License

MIT
