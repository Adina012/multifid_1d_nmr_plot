"""
NMR Data Reader Module
Handles reading and parsing NMR data files.
"""
import numpy as np
import re
import os


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
    left, right, size = None, None, None
    data = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('# LEFT'):
                    # Use regex to capture numbers including negative values
                    matches = re.findall(r'([-+]?\d+\.?\d*)\s*ppm', line)
                    if len(matches) >= 2:
                        left, right = float(matches[0]), float(matches[1])
                elif line.startswith('# SIZE'):
                    size = int(re.search(r'=\s*(\d+)', line).group(1))
                elif not line.startswith('#') and line.strip():
                    data.append(float(line.strip()))

        if left is None or right is None or size is None:
            raise ValueError(f"Failed to extract LEFT, RIGHT, or SIZE from {file_path}.")

        # Generate full x-axis
        x_values = np.linspace(left, right, size)
        y_values = np.array(data[:size])
        
        # Filter data if x_limits are provided
        if x_limits is not None:
            x_max, x_min = x_limits
            # NMR convention: x-axis decreases, so max is on left, min is on right
            # Create mask for values within range
            mask = (x_values <= x_max) & (x_values >= x_min)
            x_values = x_values[mask]
            y_values = y_values[mask]

        return x_values, y_values
    
    except (IOError, ValueError) as e:
        raise ValueError(f"Error reading {os.path.basename(file_path)}: {e}")
