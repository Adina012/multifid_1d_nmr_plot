import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import matplotlib.ticker as ticker
import os
import re

# Set publication-quality matplotlib parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8
plt.rcParams['xtick.minor.width'] = 0.5
plt.rcParams['ytick.minor.width'] = 0.5

def get_file_paths():
    """Opens a file dialog to select one or more NMR data files."""
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select NMR Data Files",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    root.destroy()  # Properly destroy window instead of quit()
    return file_paths

def readNMR(file_path):
    """Reads an NMR data file and extracts x_values (ppm) and y_values (intensity)."""
    left, right, size = None, None, None
    data = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('# LEFT'):
                    # Use regex for cleaner parsing
                    matches = re.findall(r'([\d.]+)\s*ppm', line)
                    if len(matches) >= 2:
                        left, right = float(matches[0]), float(matches[1])
                elif line.startswith('# SIZE'):
                    size = int(re.search(r'=\s*(\d+)', line).group(1))
                elif not line.startswith('#') and line.strip():
                    data.append(float(line.strip()))

        if left is None or right is None or size is None:
            raise ValueError(f"Failed to extract LEFT, RIGHT, or SIZE from {file_path}.")

        x_values = np.linspace(left, right, size)
        y_values = np.array(data[:size])  # Use size directly instead of len(x_values)

        return x_values, y_values
    
    except (IOError, ValueError) as e:
        raise ValueError(f"Error reading {os.path.basename(file_path)}: {e}")

# Main execution
file_paths = get_file_paths()

if not file_paths:
    print("No files selected. Exiting.")
    exit()

num_files = len(file_paths)

# Create single figure instead of subplots
fig, ax = plt.subplots(figsize=(10, 6))

# Generate color gradient
colors = plt.cm.viridis(np.linspace(0, 1, num_files))

# Set up formatter once instead of per plot
formatter = ticker.ScalarFormatter(useMathText=True)

for idx, (color, file_path) in enumerate(zip(colors, file_paths)):
    try:
        x_values, y_values = readNMR(file_path)

        # Reverse if needed to ensure decreasing order (NMR standard)
        if x_values[0] < x_values[-1]:
            x_values = x_values[::-1]
            y_values = y_values[::-1]

        filename = os.path.basename(file_path)
        ax.plot(x_values, y_values, linewidth=0.8, label=filename, color=color)
    
    except ValueError as e:
        print(f"Warning: {e}")

ax.set_xlabel("ppm", fontsize=10)
ax.set_ylabel("Intensity", fontsize=10)
ax.legend(fontsize=9, frameon=False, loc='upper right')
ax.invert_xaxis()  # Invert for display
ax.yaxis.set_major_formatter(formatter)
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax.tick_params(axis='both', which='major', labelsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.suptitle("NMR Spectra", fontsize=12, y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.show()
