# NMR Spectra Plotter

This Tkinter application plots 1D NMR spectra and optionally quantifies
lithium from raw spectra.

## Features

- Plot multiple spectra together, separately, or as stacked subplots.
- Exclude the selected liquid reference from plotted spectra.
- Normalize plotted intensity and quantification integrals independently by
  sample mass.
- Quantify complete raw spectra using trapezoidal integration.
- Calculate lithium from a reference concentration entered in **mol Li/kg**.
- Display lithium as mmol, mg, and `Li (ug/mg sample)`.
- Show low-resolution previews in the GUI while retaining 300 DPI export
  settings.

## Requirements

```text
numpy
matplotlib
Pillow
tkinter
```

Install the Python packages with:

```bash
pip install numpy matplotlib Pillow
```

## Run

```bash
python main.py
```

Select one or more files, enter one sample mass in mg for each file, and
choose whether to plot and/or quantify them.

The expected file format is:

```text
# LEFT = 200 ppm, RIGHT = -100 ppm
# SIZE = 1234
intensity_value_1
intensity_value_2
...
```

## Lithium units

The reference mass is converted from mg to kg and multiplied by the entered
`mol Li/kg` concentration. The resulting lithium moles are converted to mmol,
then to mg using lithium's atomic molar mass, 6.941 g/mol. The salt molecular
weight is not applied because the concentration is already expressed as
lithium, not salt, concentration.
