# NMR Spectra Plotter

A user-friendly GUI application for plotting 1D NMR spectra with customizable visualization options.

## Features

- 📊 Plot single or multiple NMR spectra
- 🎨 Purple-themed modern GUI
- 🔧 Customizable x-axis limits
- 🏷️ Customizable x- and y-axis labels
- 📈 Publication quality plotting at 300 DPI
- 🌈 Teal-to-indigo-to-purple-to-pink gradient color scheme
- ∫ Integrated intensity for plotted data or complete raw spectra
- 📋 Separate integral table with selectable relative-integral reference
- 🧪 Estimate lithium amount in samples from a liquid salt reference concentration (mol Li/kg) and mass
- ⚖️ Report lithium loading as Li (ug/mg sample) using the sample masses entered for each tube
- ∫ Optionally normalize integral values by sample mass independently of plot normalization
- ⚖️ Enter one sample mass per selected file before choosing plot or integral normalization
- 🚫 The selected reference spectrum is excluded from plotted figures but remains in quantification
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
- Applying publication-quality plot settings at 300 DPI
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

### Lithium calculation units

The reference concentration must be entered as **mol Li/kg**. The selected
reference mass is entered in **mg** with the other sample masses. The
calculation is:

```text
reference Li (mmol) = concentration (mol Li/kg)
                     × reference mass (mg) / 1,000,000 (kg/mg)
                     × 1,000 (mmol/mol)
Li (mg) = Li (mmol) × 6.941 g/mol
Li (ug/mg sample) = Li (mg) × 1,000 / sample mass (mg)
```

Because the concentration is already expressed as **mol Li/kg**, the selected
salt name is descriptive only. The molecular weight of LiCl, LiFSI, or another
salt is not applied; only the atomic molar mass of lithium is used to convert
Li moles to Li mass.

1. Run the application:
   ```bash
   python main.py
   ```

2. Use the GUI to:
   - Select one or more NMR data files (.txt)
   - Choose plot mode (single/multiple)
   - Plots are always generated at publication quality (300 DPI)
   - Optionally set custom x-axis limits
   - Optionally enter custom x-axis and y-axis labels
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
