# NMR Spectra Plotter

A user-friendly GUI application for plotting 1D NMR spectra with customizable visualization options.

## Features

- 📊 Plot single or multiple NMR spectra
- 🎨 Purple-themed modern GUI
- 🔧 Customizable x-axis limits
- 📈 Publication quality (300 DPI) or preview mode (100 DPI)
- 📁 Easy file selection and management
- 🔄 Plot multiple spectra on same figure or separately

## Project Structure

```
multifig_1d_nmr_plot/
├── main.py          # Main application launcher
├── nmr_gui.py       # GUI interface module
├── nmr_plotter.py   # Plotting functionality
├── nmr_reader.py    # NMR data file reader
└── README.md        # This file
```

## Module Descriptions

### `main.py`
Entry point for the application. Simply run this file to launch the GUI.

### `nmr_gui.py`
Contains the `NMRPlotterGUI` class which handles:
- User interface creation with purple theme
- File selection and management
- User input validation
- Coordinating between modules

### `nmr_plotter.py`
Handles all plotting operations:
- Setting plot quality (publication/preview)
- Creating single or multiple spectrum plots
- Applying formatting and styles
- Managing matplotlib parameters

### `nmr_reader.py`
Parses NMR data files:
- Extracts LEFT, RIGHT, and SIZE parameters
- Generates x-axis values (ppm)
- Reads intensity data
- Error handling for malformed files

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Use the GUI to:
   - Select one or more NMR data files (.txt)
   - Choose plot mode (single/multiple)
   - Select quality (publication/preview)
   - Optionally set custom x-axis limits
   - Click "Plot Spectra" to generate plots

## Requirements

- Python 3.x
- numpy
- matplotlib
- tkinter (usually included with Python)

## Data File Format

Expected NMR data file format:
```
# LEFT = 15.0 ppm ... RIGHT = -5.0 ppm
# SIZE = 32768 (SI = 65536)
<intensity values, one per line>
```

## Benefits of Modular Structure

✅ **Clarity**: Each module has a single, clear purpose  
✅ **Maintainability**: Easy to find and fix issues  
✅ **Reusability**: Functions can be imported and used elsewhere  
✅ **Testing**: Each module can be tested independently  
✅ **Collaboration**: Multiple people can work on different modules
