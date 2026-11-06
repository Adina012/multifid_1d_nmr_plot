"""
NMR Data Reader Module
Handles reading and parsing NMR data files.
"""
import numpy as np
import os
import re


def readNMR(file_path, x_limits=None):
    """
    Reads an NMR data file and extracts x_values (ppm) and y_values (intensity).
    
    Parameters:
    -----------
    file_path : str
        Path to the NMR data file
    x_limits : tuple of (float, float), optional
        If provided, only return data within (x_max, x_min) range
        
    Returns:
    --------
    x_values : ndarray
        Chemical shift values in ppm
    y_values : ndarray
        Intensity values
    """
    left = right = size = None
    data = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                stripped_line = line.strip()
                if stripped_line.startswith("# LEFT"):
                    matches = re.findall(
                        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*ppm",
                        stripped_line,
                    )
                    if len(matches) >= 2:
                        left, right = float(matches[0]), float(matches[1])
                elif stripped_line.startswith("# SIZE"):
                    size_match = re.search(r"=\s*(\d+)", stripped_line)
                    if size_match:
                        size = int(size_match.group(1))
                elif stripped_line and not stripped_line.startswith("#"):
                    data.append(float(stripped_line))

        if left is None or right is None or size is None:
            raise ValueError(f"Failed to extract LEFT, RIGHT, or SIZE from {file_path}.")
        if size < 2:
            raise ValueError("SIZE must be at least 2.")
        if len(data) != size:
            raise ValueError(
                f"Expected {size} intensity values but found {len(data)}."
            )

        x_values = np.linspace(left, right, size)
        y_values = np.asarray(data, dtype=float)
        
        if x_limits is not None:
            high, low = sorted(x_limits, reverse=True)
            mask = (x_values <= high) & (x_values >= low)
            x_values = x_values[mask]
            y_values = y_values[mask]
            if len(x_values) < 2:
                raise ValueError("The selected x-axis limits contain fewer than 2 points.")

        return x_values, y_values
    
    except (OSError, ValueError) as e:
        raise ValueError(f"Error reading {os.path.basename(file_path)}: {e}")
