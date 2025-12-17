"""
NMR Data Reader Module
Handles reading and parsing NMR data files.
"""
import numpy as np
import re
import os


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
